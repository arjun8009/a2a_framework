from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, TrainingArguments
import torch
from huggingface_hub import login
from peft import PeftModel


hf_token = "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"
login(hf_token)
ADAPTOR_PATH = "output/checkpoint-13"


bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=False,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
)

# We load the model and use FP16 for testing settings
model_dir = "Qwen/Qwen3-30B-A3B"
tokenizer = AutoTokenizer.from_pretrained(model_dir, use_fast=True)
model = AutoModelForCausalLM.from_pretrained(
    model_dir,
    device_map="auto",  
    torch_dtype=torch.bfloat16,
    trust_remote_code=True,
    quantization_config = bnb_config            
)

model_peft = PeftModel.from_pretrained(model,ADAPTOR_PATH,device_map="auto",trust_remote_code=True)
model_peft.eval()


# Inference
system_prompt = """You are an agent for ambiguity detection in map or geospatial queries.
for each of the questions there can be a few types of ambiguity
1. ambiguity of point of interest : Where is the mentioned entity located (like name of a resort but where is the resort located). More context here, any place or street mentioned can have multiple occurences so if the location (city, town or country) is not mentioned then it is ambiguous. Names of cities, towns, counties, countries do not count as ambiguities
2. ambiguity of distance : nearby or close does not give specific distance
3. other ambiguity : which can be descriptions like best place or good food without description
For each of the queries explain what type of ambiguity and the reason for the ambiguity.
"""

def formatting_function(examples):
     return tokenizer.apply_chat_template(examples["messages"], tokenize=False, add_generation_prompt=False)


question = "Find places to eat near st Davids station in Exeter"

# Set it in a way accepted by the formatting function
text_example = {"messages":[{"role":"system","content":system_prompt + tokenizer.eos_token},
                {"role":"user","content":question + tokenizer.eos_token}]}

# Now apply the chat template
formatted_text_example = formatting_function(text_example)

inputs = tokenizer(
    formatted_text_example,
    return_tensors="pt"
).to("cuda")

with torch.no_grad():
    outputs = model_peft.generate(
        input_ids=inputs.input_ids,
        attention_mask=inputs.attention_mask,
        max_new_tokens=2048,
        eos_token_id=tokenizer.eos_token_id,
        use_cache=True,
    )

response = tokenizer.batch_decode(outputs, skip_special_tokens=True)

print(response)