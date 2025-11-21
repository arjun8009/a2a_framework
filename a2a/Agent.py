from utils.llms import *
from a2a.AgentCard import AgentCard
from a2a.Artifact import Artifact
from pydantic import BaseModel
import requests

class Agent():

    def __init__(self, agent_details:AgentCard, llm_name:str, schema:BaseModel=None, 
                 tools:dict=None, tool_definitions:list=None, additional_args:dict=None, 
                 available_agents=None, artifacts_req:Artifact = None, system_instruction:str=None):
        
        ''' Default agent is defined here. It contains an identity of the agent and assigns an llm to control the agent
        args:
            1. agent_identity : An identification of the agent of type AgentCard
            2. llm_name : name of the llm agent will use
            3. schema : A pydantic BaseModel type schema
            4. tools : A dictionary of functions {"add_numbers":add_numbers, "substract_numbers":substract_numbers}
            5. tool_definitions : A list of tool defintions
            6. additional_args : A dictionary of additional args to disable parallel tool calls 
            7. available_agents : A list of available agents for send_messages 
            8. artifacts_req : A list of data artifacts required
        outputs : 
            1. llm output can be schema, string or tool evalutation results of type string

            
        We are still working on returning raw data. Will be implemented using Artifacts'''

        self.agent_identity = agent_details
        self.llm_name = llm_name
        self.tools = tools
        self.tool_definitions = tool_definitions
        self.schema = schema
        self.additional_args = additional_args
        self.available_agents = available_agents
        self.artifacts_req = artifacts_req
        self.system_instruction = system_instruction
    
    def run_agent(self,messages):

        '''This actually runs the agent and gives all the outputs including the tools
        
        args:
            1. messages : A list of messages openai style. We dont have the messages in the init bec we want to blank initialise an agent and run it whenever we want
        outputs:
            1. output : ouptut of the llm can be string, schema and in a later stage data artifacts'''
        
        if self.system_instruction:
            messages.insert(0,{"role":"system","content":self.system_instruction})

        if self.artifacts_req:
            messages[-1]["content"] = messages[-1]["content"] + f"\n The data artifacts provided to you are : {[i.name for i in self.artifacts_req]} with descriptions {[i.description for i in self.artifacts_req]}"

        output = run_llm(self.llm_name,messages,self.schema, self.tool_definitions)
        artifacts = None
        attempts = 0
        if hasattr(output,"output"):
            while(output.output[-1].type=="function_call" and attempts < 50):
                fn_calls = [i for i in output.output if i.type=="function_call"]

                # running of tools without multithreading
                messages,artifacts = self.run_tools(messages,fn_calls)
                attempts = attempts + 1
                output = run_llm(self.llm_name,messages,self.schema, self.tool_definitions)

        if hasattr(output,"output_text"):
            return output.output_text,artifacts
        else:
            return output,None
    
    def run_tools(self,messages,fn_calls):

        '''run tools will actually run the llm tool calls. However this functionality is limited to openai tool calling. Will later implement open source tool calling here and
        in run_llms
        
        args:
            1. messages : A list of messages to update
            2. fn_calls : A list of function_call outputs
        
        output:
            updated_messages : A list of updated messages with stringified outputs'''
        
        artifacts = []
        interaction = {}
        interaction_sent = False
        for call in fn_calls:
            messages.append(call)
            args = json.loads(call.arguments)
            tool_names = self.tools.keys()

            # In case we need to provide available agents
            if call.name in tool_names:
                print(f"Calling tool {call.name} with args : {args}")
                
                if call.name == "call_os_ngd":
                    args["ngd_name"] = self.agent_identity.agent_name

                if call.name == "send_message":
                    args["agents"] = self.available_agents
                    args["source"] = self.agent_identity.agent_name
                    # visualisation only
                    interaction = {"source":args["source"], "target":args["target"], "msg":args["task_description"]}
                    #requests.post("http://localhost:5000/interact",json=interaction)

                
                # If we need to provide raw data to the llm to code
                if self.artifacts_req is not None:
                    args["data"] = [i for i in self.artifacts_req]

                result = self.tools[call.name](**args)
                #print(f"Tool {call.name} returned result : {result}")



                # Assuming that the results of the agent will be a list consisting of output and the data. Output will be a description of what it has found. Aritfact can be an object or a list of objects
                if (isinstance(result,set) or isinstance(result,list)) and len(result)==2 and (isinstance(result[1],Artifact) or (isinstance(result[1],list) and all([isinstance(i,Artifact) for i in result[1]]))):
                    
                    if isinstance(result[1],list):
                        message_content = str(result[0]) + "\n" + f" Additionally some data artifacts have been generated with names : {[i.name for i in result[1]]} and descriptions : {[i.description for i in result[1]]} "
                        artifacts = [i for i in result[1]]
                    else:
                        message_content = str(result[0]) + "\n" + f" An artifact has been generated with name : {result[1].name} and description : {result[1].description} "
                        artifacts.append(result[1])
                    messages.append({"type":"function_call_output", "call_id":call.call_id,"output":message_content})
                    
                else:
                    messages.append({"type":"function_call_output", "call_id":call.call_id,"output":str(result)})
        
                
        
        if len(artifacts) > 0:
            return messages,artifacts
        else:
            return messages,None
        
        