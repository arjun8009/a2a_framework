

class AgentCard():
    def __init__(self, agent_name:str, agent_description:str, capabilities:list, input_modes:list, output_modes:list):
        
        '''Default class description to define the definition of an agent. This is like the visiting card that an agent can use to communicate with other agents'''
        
        # A proper sensible agent name

        self.agent_name = agent_name
        
        # A brief description of what the agent does
        self.agent_description = agent_description

        # A list of capabilities, inluding information about state transitions
        self.capabilities = capabilities

        # A list of input modes 
        self.input_modes = input_modes

        # A list of output modes
        self.output_modes = output_modes