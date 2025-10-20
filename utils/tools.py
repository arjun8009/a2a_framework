import geopandas as gpd
import pandas as pd
import numpy as np
from a2a.Task import Task
from a2a.SendMessage import SendMessage
import uuid
import warnings

''' Default place for adding tool. From OS NGD to other useful tools'''

def call_os_ngd():
    return None

def send_message(**kwargs):
    
    '''This function will be a tool agents will have to communicate with each other. The messages they give will be converted to tasks
    args:
        1. target : The agent messages are targetted to
        2. task_description : What is required of the agent

        The rest of the inputs can be provided manually by the code
    output:
        The updated task
    '''
    
    target = kwargs["target"]
    task_description = kwargs["task_description"]
    agents = kwargs["agents"]
    source = kwargs["source"]

    agent_names = [i.agent_identity.agent_name for i in agents]
    agent = agents[agent_names.index(target)]



    messages_list = [{"role":"user","content":task_description}]
    task = Task(messages=messages_list,task_id=uuid.uuid4())

    output = SendMessage(task,agent).send_messages()

    if output.task_status == "success":
        return output.task_output
    else:
        warnings.warn(f"Error encountered in sending message from {source} to {target} : ")
        return output.task_output






