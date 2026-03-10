import pandas as pd
import json
from utils.initialize_os_agents import OSAgentsInitializer
from utils.keys import set_api_keys
from utils.tools import human_send_message
set_api_keys()
import shutil
import joblib
import os


config = None
with open(r"agent_frameworks\agent_config_with_human_all_opensource.json","rb") as file:
    config = json.load(file)

# Now that things are initialised
agent_archiecture = OSAgentsInitializer(config,"Question_21",diff_dir=None).initialize_all_agents()

human_send_message(message="Find all tall buildings in Exeter that are over 18m tall or 7 floors high",target_agent=[agent_archiecture["host_agent"]])
shutil.rmtree("message_store")
shutil.rmtree("artifacts")
os.makedirs("message_store",exist_ok=True)
os.makedirs("artifacts",exist_ok=True)