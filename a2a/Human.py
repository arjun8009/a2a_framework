from a2a.AgentCard import AgentCard


class Human():
    def __init__(self, human_details:AgentCard):
        ''' Default human is defined here. It contains an identity of the human
        args:
            1. human_identity : An identification of the human of type AgentCard
        outputs : 
            1. llm output can be schema, string or tool evalutation results of type string'''

        self.agent_identity = human_details
    
    def run_agent(self,messages):
        '''This actually runs the human and gives all the outputs including the tools
        
        args:
            1. messages : A list of messages openai style. We dont have the messages in the init bec we want to blank initialise an human and run it whenever we want
        outputs:
            1. output : ouptut of the human can be string, schema and in a later stage data artifacts'''
        
        print("Messages for human to process:", messages[-1]["content"])
        #output = input("Please provide your response:")
        return f"<HUMAN AGENT>The agent wants help for the following query : \n query : {messages[-1]["content"]}",None
    