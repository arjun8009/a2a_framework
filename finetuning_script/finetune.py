import torch
from huggingface_hub import login
import os
import json
from peft import LoraConfig, get_peft_model
import pandas as pd
from trl import SFTTrainer, SFTConfig
import gc
from pathlib import Path
from datasets import Dataset
from transformers import BitsAndBytesConfig
from transformers.utils import get_json_schema


DATA_PATH = "/home/ab1574/Ordnance_Survey/DPO_dumps/DPO_trajectories"
MODEL_DIR = "/home/ab1574/models/qwen3.5-35a3b"

send_message_definitions = {
        "type":"function",
        "function":{
        "name":"send_message",
        "description":"Tool that sends messages to another agent to perform a task and provides the agent output",
        "parameters":{
            "type":"object",
            "properties":{
                "target":{
                    "type":"string",
                    "description":"Name of the agent the task needs to be delegated to"
                },
                "task_description":{
                    "type":"string",
                    "description":"The description of the task the agent has to perform"
                }
            }
        }
        }
    }

metadata_all_artifacts = {
        "type":"function",
        "function":{
        "name":"generate_metadata_for_all_artifacts",
        "description":"Tool that generates metadata for all artifacts so you can tell the agents what artifacts to use correctly",
        }
    }



hf_token = "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"
login(hf_token)


def prepare_dataset():
    dataset = []

    for file in os.listdir(DATA_PATH):
        
        if os.path.isdir(DATA_PATH + "/" + file):
            continue
        json_trajectories = None        
        
        with open(DATA_PATH + "/" + file, "r") as f:
            
            json_trajectories = json.load(f)["messages"]

            for msg in json_trajectories:
                if "content" not in msg:
                    msg["content"] = ""
                
            dataset.append({"messages":json_trajectories, "tools":[metadata_all_artifacts,send_message_definitions]})
        
    
    dataset_final = Dataset.from_list(dataset, on_mixed_types="use_json")
    return dataset_final



def make_trainer(dataset:Dataset):

    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_use_double_quant=True,
    )

    lora_config = LoraConfig(
        r=16,
        lora_alpha=16,
        lora_dropout=0,
        bias='none',
        task_type='CAUSAL_LM',
        target_modules=[
            'q_proj','k_proj','v_proj','o_proj',
            'gate_proj','up_proj','down_proj'
        ]
    )

    training_args = SFTConfig(
        output_dir="/home/ab1574/models/finetuned_qwen3.5-35a3b",
        per_device_train_batch_size=1,
        gradient_accumulation_steps=16,
        learning_rate=2e-4,
        num_train_epochs=1,
        logging_steps=1,
        bf16=True,
        gradient_checkpointing=True,
        packing=False,
        model_init_kwargs={"quantization_config": bnb_config, "trust_remote_code": True}
    )

    trainer = SFTTrainer(model=MODEL_DIR,
                        peft_config = lora_config,
                         args=training_args,
                        train_dataset=dataset
                         )
    return trainer

dataset = prepare_dataset()
trainer = make_trainer(dataset)
trainer.train()



        
        

    
    
