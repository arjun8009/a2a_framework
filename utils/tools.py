import geopandas as gpd
import pandas as pd
import numpy as np
from a2a.Task import Task
from a2a.SendMessage import SendMessage
from a2a.Artifact import Artifact
from a2a.Messages import Messages
from utils.os_utils_data_raw import *
from a2a.Human import Human
from utils.card_templates import human_agent_card
import uuid
import warnings
import joblib
import os
import inspect
import requests
import traceback

''' Default place for adding tool. From OS NGD to other useful tools'''

ARTIFACT_PATH = r"C:\Users\ab1574\OneDrive - University of Exeter\Desktop\Ordnance_Survey\artifacts"



# New function with raw data
def call_os_ngd(**kwargs):
    '''This is a single tool for calling os ngd data base. It checks which agent is calling it and calls that particular ngd
    args:
        1. Different args based on different ngd features
        2. ngd_name : mandatory name of the ngd to call

        output:
        The data fetched from the os ngd database in the form of a geopandas dataframe as an artifact and a summary of the data fetched'''
    
    ngd_util_mapping = {"address":query_address,
                       "buildings":query_buildings,
                       "named_area":apply_extent_named_area,
                       "water_features":query_water_features,
                       "water_network":query_water_network,
                       "land_features":query_land_features,
                       "land_use_features":query_land_use,
                       "structures_agent":query_structure}
    
    args = inspect.signature(ngd_util_mapping[kwargs["ngd_name"]]).parameters.keys()
    logger = kwargs["logger"]
    
    try:
        result = ngd_util_mapping[kwargs["ngd_name"]](**{k:v for k,v in kwargs.items() if(k!="ngd_name" and k in args and k!="logger") })
    except Exception as e:
        logger.exception("Exception in call os ngd",e)
        return "There was an error while calling NGD. Most probable cause is wrong artifact name for bbox parameter. Try a few times with the correct artifact names."

    if not isinstance(result,list):
        logger.info("NGD query result %s",result)
    else:
        logger.info("NGD query result %s",result)

    if result is not None:

        if isinstance(result,list):
            artifacts = [
                Artifact(name=f"""{df.attrs["name"]}""", description=df.attrs["description"],
                         data=df) for i,df in enumerate(result)
            ]
            [joblib.dump(artifacts[i], os.path.join(ARTIFACT_PATH,f"{artifacts[i].name}.pkl")) for i in range(len(artifacts))]

            return_msg = f"""Multiple search results have been found in multiple datasets. A summary of each is provided.
            Artifacts generated are : {[i.name for i in artifacts]},
            Descriptions are : {[i.description for i in artifacts]},
            counts of records fetched are : {[i.attrs["count"] for i in result]}.
            """
            return [return_msg, artifacts]
        else:
            artifact = Artifact(name=f"""{result.attrs["name"]}""", description=result.attrs["description"],
                                data=result)
            joblib.dump(artifact, os.path.join(ARTIFACT_PATH,f"{artifact.name}.pkl"))
            return_msg = f"""Search results have been found. 
            Artifact generated is : {artifact.name},
            Description is : {artifact.description},
            count of records fetched : {result.attrs["count"]}.
            """
            return [return_msg, artifact]

    else:
        return "No results found for your search terms "

    


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
    logger = kwargs["logger"]

    agent_names = [i.agent_identity.agent_name for i in agents]
    
    # Need to handle human agent separately because human needs host agent and host agent needs human
    if target == "human_agent":

        agent = Human(human_details=human_agent_card)
    else:
        agent = agents[agent_names.index(target)]
    
    # Make a set of messages and then create a task object
    messages_list = [{"role":"user","content":task_description}]
    
    task_id = source + "^" + target + "^" + str(uuid.uuid4())

    # save the messages to the message store or update existing messages and then save
    message_obj = Messages(messages=messages_list,task_id=task_id)
    message_obj.add_or_update_messages()

    messages_list = message_obj.get_messages()

    # Filter messages to last 10 only to avoid token overload
    if len(messages_list) > 10:
        messages_list = messages_list[-10:]

    logger.info(f"Messages sent to agent {target} : {messages_list}")
    task = Task(messages=messages_list,task_id=task_id)

    output = SendMessage(task,agent,logger).send_messages()
    # Return the output of the agent to visualise
    try:
        interaction = {"source":target, "target":source, "msg":output.task_output}
        requests.post("http://localhost:5000/interact",json=interaction)
        logger.info(f"Output from agent {target} : {output.task_output}")
    except Exception as e:
        logger.warning("OFFLINE MODE")
        logger.info(f"Output from agent {target} : {output.task_output}")

    if output.task_status == "success":
        
        # Storing the updated messages again in the message store with output from the agent
        if output.task_artifact is not None:
            output_msg = output.task_output + f"Addtionally some data artifacts have been generated with names  {[i.name for i in output.task_artifact]} and \n descriptions {[i.description for i in output.task_artifact]}" 
            message_obj.add_messages([{"role":"assistant","content":output_msg}])
            return [output_msg , output.task_artifact]

        else:
            message_obj.add_messages([{"role":"assistant","content":str(output.task_output)}])
            return output.task_output
        

    else:
        warnings.warn(f"Error encountered in sending message from {source} to {target} : ")
        message_obj.add_messages([{"role":"assistant","content":str(output.task_output)}])
        return output.task_output



def generate_metadata_for_artifacts(**kwargs):

    '''Function to generate metadata for artifacts passed to it
    args:
        1. artifact_names : A list of artifact names to generate metadata for
    output:
        1. columns : A list of columns for each artifact
        2. first_five_rows : A list of dataframes containing first five rows of each artifac
        3. filenames : filename of each artifact'''
    

    artifacts = [joblib.load(os.path.join(ARTIFACT_PATH,f"{name}.pkl")) for name in kwargs["artifact_names"] if name+".pkl" in os.listdir(ARTIFACT_PATH)]
    logger = kwargs["logger"]
    logger.info(f"artifacts loaded for metadata generation : {[i.name for i in artifacts]}")
    columns = [list(df.data.columns) for df in artifacts]
    first_five_rows = [df.data.head() for df in artifacts]
    filenames = [df.name for df in artifacts]  
    return columns,first_five_rows,filenames

def generate_metadata_for_all_artifacts(**kwargs):

    '''Function to generate metadata for artifacts passed to it
    args:
        1. artifact_names : A list of artifact names to generate metadata for
    output:
        1. columns : A list of columns for each artifact
        2. first_five_rows : A list of dataframes containing first five rows of each artifac
        3. filenames : filename of each artifact'''
    
    logger = kwargs["logger"]
    artifacts = [joblib.load(os.path.join(ARTIFACT_PATH,f"{name}")) for name in os.listdir(ARTIFACT_PATH)]
    metadata = {i.name:i.description for i in artifacts}
    return metadata



def code_executor(**kwargs):

    '''function to execute code generated by the llm
     args:
        1. code : The code to execute
        2. artifact_names : The names of the artifacts to provide as input
        3. data : A list of artifacts available to the agent if the agent is not provided with raw data then it will search the aritfacts folder
        output:
        The output of the code execution'''
    
    code = kwargs["code"]
    artifact_names = kwargs["artifact_names"]
    data = kwargs.get("data",None)
    data = [i.data for i in data if i.name in artifact_names] if data is not None else [joblib.load(os.path.join(ARTIFACT_PATH,f"{name}.pkl")).data for name in artifact_names if name+".pkl" in os.listdir(ARTIFACT_PATH)]
    logger = kwargs["logger"]
    try:
        namespace = {}
        code = "import matplotlib\nmatplotlib.use('Agg')\n" + code
        logger.info(f"Executing code {code}")
        exec(code,namespace)
        function_name = [name for name in namespace if callable(namespace[name])][-1]
        logger.info(f"function name {function_name}")
        output = namespace[function_name](data=data)
        logger.info("Output completed")
        # We are assuming that the output of the coding agent will be  a list of 4 things [summary of output, artifact name, artifact description, artifact data ], None if no artifact
        if isinstance(output,list):

            # if a valid artifact is returned we will save it to the artifacts folder so that it can be used later
            if output[1] is not None and output[2] is not None and output[3] is not None:
                artifact = Artifact(name=output[1],description=output[2],data=output[3])
                if isinstance(output[3], (gpd.GeoDataFrame, gpd.GeoSeries)):
                    if not output[3].empty:
                        joblib.dump(artifact, os.path.join(ARTIFACT_PATH,f"{artifact.name}.pkl"))
                        return [output[0], Artifact(name=output[1],description=output[2],data=output[3])]
                    return "The search return no results and no artifacts are generated"
                else:
                    joblib.dump(artifact, os.path.join(ARTIFACT_PATH,f"{artifact.name}.pkl"))
                    return [output[0], Artifact(name=output[1],description=output[2],data=output[3])]
            else:
                return output[0]
        else:
            return output
    except Exception as e:
        logger.exception("ERROR EXECUTING CODE %s",e)
        return traceback.format_exc()

def human_send_message(message:str, target_agent:list):
    '''This function will be a stopgap for human to send messages to other agents, currently only host agent
    args:
        1. message : The message the human is sending to the agent
        2. target_agent : The agent object the human is sending the message to
    output:
        The updated task
    '''
    logger = target_agent[0].logger
    try:
        logger.info(f"sending message from human to host {message}")
        interaction = {"source":"human_agent", "target":"host_agent", "msg":message}
        requests.post("http://localhost:5000/interact",json=interaction)
    except Exception as e:
        logger.info("OFFLINE MODE")
        
    output = send_message(source="human_agent",
                    target="host_agent",
                    task_description=message,
                    agents=target_agent,
                    logger=logger)
    return output