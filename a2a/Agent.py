from utils.llms import *
from a2a.AgentCard import AgentCard
from pydantic import BaseModel

class Agent():

    def __init__(self, agent_details:AgentCard, llm_name:str, schema:BaseModel=None, tools:dict=None, tool_definitions:list=None, additional_args:dict=None, available_agents=None):
        ''' Default agent is defined here. It contains an identity of the agent and assigns an llm to control the agent
        args:
            1. agent_identity : An identification of the agent of type AgentCard
            2. llm_name : name of the llm agent will use
            3. schema : A pydantic BaseModel type schema
            4. tools : A dictionary of functions {"add_numbers":add_numbers, "substract_numbers":substract_numbers}
            5. tool_definitions : A list of tool defintions
            6. Addtional_args : A dictionary of additional args to disable parallel tool calls 
            7. Avaialable agents : A list of available agents for send_messages 
        
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
    
    def run_agent(self,messages):

        '''This actually runs the agent and gives all the outputs including the tools
        
        args:
            1. messages : A list of messages openai style. We dont have the messages in the init bec we want to blank initialise an agent and run it whenever we want
        outputs:
            1. output : ouptut of the llm can be string, schema and in a later stage data artifacts'''

        output = run_llm(self.llm_name,messages,self.schema, self.tool_definitions)
        
        attempts = 0
        if hasattr(output,"output"):
            while(output.output[-1].type=="function_call" and attempts < 4):
                fn_calls = [i for i in output.output if i.type=="function_call"]

                # running of tools without multithreading
                messages = self.run_tools(messages,fn_calls)
                attempts = attempts + 1
                output = run_llm(self.llm_name,messages,self.schema, self.tool_definitions)

        if hasattr(output,"output_text"):
            return output.output_text
        else:
            return output
    
    def run_tools(self,messages,fn_calls):

        '''run tools will actually run the llm tool calls. However this functionality is limited to openai tool calling. Will later implement open source tool calling here and
        in run_llms
        
        args:
            1. messages : A list of messages to update
            2. fn_calls : A list of function_call outputs
        
        output:
            updated_messages : A list of updated messages with stringified outputs'''
        
        for call in fn_calls:
            messages.append(call)
            args = json.loads(call.arguments)
            tool_names = self.tools.keys()

            # In case we need to provide available agents
            if call.name in tool_names:
                print(f"Calling tool {call.name} with args : {args}")
                if call.name == "send_message":
                    args["agents"] = self.available_agents
                    args["source"] = self.agent_identity.agent_name

                result = self.tools[call.name](**args)
                messages.append({"type":"function_call_output", "call_id":call.call_id,"output":str(result)})
        return messages
        
        