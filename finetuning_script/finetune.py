from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, TrainingArguments
import torch
from huggingface_hub import login
import os
from utils.keys import set_api_keys
from peft import LoraConfig, get_peft_model
import pandas as pd
from trl import SFTTrainer
import gc

set_api_keys()
DATA_PATH = r"C:\Users\ab1574\OneDrive - University of Exeter\Desktop\Ordnance_Survey\test_data_for_ambiguity\dataset_mapeval_approved_ambiguities_updated.csv"
hf_token = os.environ.get("HF_TOKEN")
login(hf_token)

# This is quantization we can aim for 16 bit quantization. not currently using it
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=False,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
)

# We load the model and use FP16 for training settings
model_dir = "Qwen/Qwen3-32B"
tokenizer = AutoTokenizer.from_pretrained(model_dir, use_fast=True)
model = AutoModelForCausalLM.from_pretrained(
    model_dir,
    device_map="auto",  
    torch_dtype=torch.bfloat16,
    trust_remote_code=True             
)

model.config.use_cache = False
model.config.pretraining_tp = 1

system_prompt = """You are an agent for ambiguity detection in map or geospatial queries.
for each of the questions there can be a few types of ambiguity
1. ambiguity of point of interest : Where is the mentioned entity located (like name of a resort but where is the resort located). More context here, any place or street mentioned can have multiple occurences so if the location (city, town or country) is not mentioned then it is ambiguous
2. ambiguity of distance : nearby or close does not give specific distance
3. other ambiguity : which can be descriptions like best place or good food without description
For each of the queries explain what type of ambiguity and the reason for the ambiguity.
"""

# We need to preprocess the data to set it into format for training
def preprocess_data_with_eos(eos_token,examples):

    def preprocess_examples(examples):
        queries = examples["queries"].tolist()
        answers = examples["answers"].tolist()
        chats = []
        for q,a in zip(queries,answers):
            a += eos_token
            chat = [
                {"role":"user", "content":q},
                {"role":"assistant","content":a}
            ]
            chats.append(chat)
        
        return {"messages":chats}
    
    dataset = examples.map(preprocess_examples,batched=True)
    dataset["messages"].insert(0,{"role":"system","content":system_prompt})
    return dataset


# Now we load and format the data
dataset = pd.read_csv(DATA_PATH)

dataset = preprocess_data_with_eos(tokenizer.eos_token,dataset)

# Add the chat template below the abstraction
def formatting_function(examples):
     return tokenizer.apply_chat_template(examples["messages"], tokenize=False, add_generation_prompt=False)


# setting up the model

peft_config = LoraConfig(
    lora_alpha=16,                           # Scaling factor for LoRA
    lora_dropout=0.05,                       
    r=64,                                    # Rank of the LoRA update matrices
    bias="none",                             
    task_type="CAUSAL_LM",                   # Task type: Causal Language Modeling
    target_modules=[
        "q_proj",
        "k_proj",
        "v_proj",
        "o_proj",
        "gate_proj",
        "up_proj",
        "down_proj",
    ],  # Target modules for LoRA
)
# We have set up lora and now we can use simple things like SFTTrainer to finetune the model
model = get_peft_model(model, peft_config)


# These are sourced from tutorials. Boilerplate things
arguments = TrainingArguments(
    output_dir="output",
    per_device_train_batch_size=1,
    per_device_eval_batch_size=1,
    gradient_accumulation_steps=2,
    optim="paged_adamw_32bit",
    num_train_epochs=1,
    logging_steps=0.2,
    warmup_steps=10,
    logging_strategy="steps",
    learning_rate=2e-4,
    fp16=False,
    bf16=False,
    group_by_length=True,
    report_to="none"
)

trainer = SFTTrainer(
    model=model,
    args=arguments,
    train_dataset=dataset,
    peft_config=peft_config,
    formatting_func=formatting_function
)

gc.collect()
torch.cuda.empty_cache()
model.config.use_cache = False
trainer.train()


