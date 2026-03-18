# First the imports and the keys
import warnings
warnings.filterwarnings("ignore")
from utils.registry import registry
import logging

class OSAgentsInitializer():
    def __init__(self, config, logging_filename = "log", diff_dir = None):
        '''
        This class accepts a dictionary of agent configurations and initializes OS agents accordingly.
        args:
            1. config : A dictionary where keys are agent names and values are dictionaries containing agent configurations such as:
                - llm_name : Name of the LLM to be used by the agent
                - tools : A dictionary of tool functions available to the agent
                - tool_definitions : A list of tool definitions for the agent
                - schema : A pydantic BaseModel schema for structured outputs
                - additional_args : Additional arguments for agent configuration
                - system_instruction : System-level instructions for the agent
        '''
        self.agent_dict = config
        self.logging_filename = logging_filename
        if diff_dir is not None:
            self.logger = logging.getLogger(f"evaluation/{diff_dir}/{self.logging_filename}")
            self.logger.setLevel(logging.INFO)
            self.logger.handlers.clear()
            filehandler = logging.FileHandler(f"evaluation/{diff_dir}/{self.logging_filename}.log",mode="w")
            filehandler.setLevel(logging.INFO)
            formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
            filehandler.setFormatter(formatter)
            self.logger.addHandler(filehandler)
        else:
            self.logger = logging.getLogger(f"evaluation/evaluation_logs/{self.logging_filename}")
            self.logger.setLevel(logging.INFO)
            self.logger.handlers.clear()
            filehandler = logging.FileHandler(f"evaluation/evaluation_logs/{self.logging_filename}.log",mode="w")
            filehandler.setLevel(logging.INFO)
            formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
            filehandler.setFormatter(formatter)
            self.logger.addHandler(filehandler)
            
        
        # Prevent propagation to root logger
        self.logger.propagate = False

        
    
    def initialize_agent(self,agentconfig:dict):

        '''Add everything as params using the registry. Except system instruction and available agent dependencies for now.
        args:
            1. agentconfig : A dictionary containing the configuration for a single agent
        '''

        if agentconfig["agent_name"].lower() == "human":
            return registry["Human"](
                human_details = registry[agentconfig["agent_details"]]
            )
        else:
            return registry["Agent"](
                agent_details=registry[agentconfig["agent_details"]],
                llm_name=agentconfig["llm_name"],
                port = None if agentconfig.get("port",None) is None else agentconfig.get("port"),
                tools={tool_name:registry[tool_name] for tool_name in agentconfig.get("tools",[])},
                tool_definitions=[registry[tool_def] for tool_def in agentconfig.get("tool_definitions",[])],
                schema=registry[agentconfig.get("schema",None)] if agentconfig.get("schema",None) is not None else None,
                additional_args=agentconfig.get("additional_args",None),
                system_instruction=registry[agentconfig.get("system_instruction",None)] +  "\n" + (registry[agentconfig["additional_prompts"]] if agentconfig.get("additional_prompts") else "") ,
                available_agents=None,
                logger = self.logger
            )
    
    def add_agent_dependencies(self,initialized_agents:dict):
        '''Add system instructions and available agent dependencies to initialized agents.
        args:
            1. initialized_agents : A dictionary where keys are agent names and values are initialized agent instances
        '''
        # This is what is happening here.
            # For each agent in the agent config, check if it has available agents.
            # If it does, then used the preinitialized agents to get that instance of the agent and set its system instruction to include the available agents.
            # Available agents can be received from the agent config and we are using the preinitialized agents to get the instance of the agent and its details.
        for agents in self.agent_dict:
            if agents.get("available_agents",None):
                initialized_agents[agents["agent_name"]].system_instruction = registry[agents.get("system_instruction")] + \
                "\n" + (registry[agents["additional_prompts"]] if agents.get("additional_prompts") else "") + \
                f"""\n <AVAILABLE AGENTS> {[initialized_agents[i].agent_identity for i in agents["available_agents"]]} <AVAILABLE AGENTS>""" 

        for agents in self.agent_dict:
            if agents.get("available_agents",None):
                initialized_agents[agents["agent_name"]].available_agents = [initialized_agents[i] for i in agents["available_agents"]]

            
    
    def initialize_all_agents(self):
        initialized_agents = {}
        for agent_config in self.agent_dict:
            initialized_agents[agent_config["agent_name"]] = self.initialize_agent(agent_config)
            self.logger.info(f"""Agent {agent_config["agent_name"]} Initialised""")
        self.add_agent_dependencies(initialized_agents)
        return initialized_agents
    
    

