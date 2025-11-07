import geopandas as gpd
import pandas as pd
import numpy as np
from a2a.Task import Task
from a2a.SendMessage import SendMessage
from a2a.Artifact import Artifact
from a2a.Messages import Messages
from utils.os_utils import *
import uuid
import warnings
import joblib
import os

''' Default place for adding tool. From OS NGD to other useful tools'''

def call_os_ngd(**kwargs):
    '''This is a single tool for calling os ngd data base. It checks which agent is calling it and calls that particular ngd
    args:
        1. Different args based on different ngd features
        2. ngd_name : mandatory name of the ngd to call

        output:
        The data fetched from the os ngd database in the form of a geopandas dataframe as an artifact and a summary of the data fetched'''
    
    
    
    if kwargs["ngd_name"] == "address" or kwargs["ngd_name"] =="buildings":
        
        # Make the params dynamically, We are only searching addresses with terms so filters will be None and terms will be not None
        if kwargs["terms"] is not None:
            address_or_buildings = True
            search_terms = kwargs["terms"]
        else:
            address_or_buildings = False
            search_terms = kwargs["terms"]

        result =  query_address_and_buildings(address_or_building=address_or_buildings,name_or_theme=search_terms,bbox=kwargs["bbox"])
    
    if kwargs["ngd_name"] == "named_area":
        search_terms = kwargs["terms"]
        result =  query_named_area(search_areas=search_terms)
    
    if result is not None and len(result) > 0:
        artifact = Artifact(name=f"""{kwargs["ngd_name"]}_search_results""", description="A concatenated geopandas dataframe containing multiple results per search found within the bbox if requested so assume all points are in the bbox. Filter it if required",
                         data=result)
        joblib.dump(artifact, f"./artifacts/{artifact.name}.pkl")
        print("Multiple search results have been found for each of your search terms. Please filter them as you seem fit. Also if you had asked for bbox then the bbox has been applied. You can skip bbox join")
        return ["Multiple search results have been found for each of your search terms. Please filter them as you seem fit. Also if you had asked for bbox then the search results have been found within the bbox so further filter will not require the bbox",
                artifact]
    
    if result is not None and len(result) == 0:
        print("No results found")
        return "No results found for your search terms "
    else:
        print("some error occured in os ngd")
        return "some error occured. Make sure that you cannot use a point as bbox and search within a point"

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

    print(f"Messages sent to agent {target}", messages_list)
    task = Task(messages=messages_list,task_id=task_id)

    output = SendMessage(task,agent).send_messages()


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
    

    artifacts = [joblib.load(f"./artifacts/{name}.pkl") for name in kwargs["artifact_names"] if name+".pkl" in os.listdir("./artifacts/")]
    print("artifacts loaded for metadata generation", [i.name for i in artifacts])
    columns = [list(df.data.columns) for df in artifacts]
    first_five_rows = [df.data.head() for df in artifacts]
    filenames = [df.name for df in artifacts]  
    return columns,first_five_rows,filenames

def generate_metadata_for_all_artifacts():

    '''Function to generate metadata for artifacts passed to it
    args:
        1. artifact_names : A list of artifact names to generate metadata for
    output:
        1. columns : A list of columns for each artifact
        2. first_five_rows : A list of dataframes containing first five rows of each artifac
        3. filenames : filename of each artifact'''
    

    artifacts = [joblib.load(f"./artifacts/{name}") for name in os.listdir("./artifacts/")]
    print("artifacts loaded for metadata generation", [i.name for i in artifacts])
    names = [i.name for i in artifacts]
    description = [i.description for i in artifacts]
    return names,description



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
    data = [i.data for i in data if i.name in artifact_names] if data is not None else [joblib.load(f"./artifacts/{name}.pkl").data for name in artifact_names if name+".pkl" in os.listdir("./artifacts/")]

    try:
        namespace = {}
        code = "import matplotlib\nmatplotlib.use('Agg')\n" + code
        exec(code,namespace)
        function_name = [name for name in namespace if callable(namespace[name])][-1]
        print("function name",function_name)
        output = namespace[function_name](data=data)
        # We are assuming that the output of the coding agent will be  a list of 4 things [summary of output, artifact name, artifact description, artifact data ], None if no artifact
        if isinstance(output,list):

            # if a valid artifact is returned we will save it to the artifacts folder so that it can be used later
            if output[1] is not None and output[2] is not None and output[3] is not None:
                artifact = Artifact(name=output[1],description=output[2],data=output[3])
                joblib.dump(artifact, f"./artifacts/{artifact.name}.pkl")
                return [output[0], Artifact(name=output[1],description=output[2],data=output[3])]
            else:
                return output[0]
        else:
            return output
    except Exception as e:
        print(e)
        return e
