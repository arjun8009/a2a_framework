import warnings
warnings.filterwarnings("ignore")
from utils.tool_definitions import send_message_definitions
from utils.tool_definitions import *
from a2a.Agent import Agent
from a2a.Human import Human
from utils.card_templates import *
from a2a.Artifact import Artifact
from utils.tools import *
from utils.prompt_templates import *

''' This is the registry the singular mapping of all the classes and variables in the Repo. It
    is used to initialise the agents.'''

registry = {
    
    "code_executor":code_executor,
    "generate_metadata_for_artifacts":generate_metadata_for_artifacts,
    "coding_agent_details":coding_agent_details,
    "additional_args":{"parallel_tool_calls":False},
    "plotting_agent_card":plotting_agent_card,
    "generic_coding_agent_template":generic_coding_agent_template,
    "plotting_agent_template":plotting_agent_template,
    "send_message":send_message,
    "call_osm":call_osm,
    "places_prompt" : places_prompt,
    "buildings_prompt":buildings_prompt,
    "named_area_prompt":named_area_prompt,
    "address_agent_card":address_agent_card,
    "building_agent_card":building_agent_card,
    "named_area_agent_card":named_area_agent_card,
    "water_network_prompt":water_network_prompt,
    "water_network_agent_card":water_network_agent_card,
    "land_features_agent_card":land_features_agent_card,
    "land_use_features_agent_card":land_use_features_agent_card,
    "land_features_prompt":land_features_prompt,
    "land_use_features_prompt":land_use_features_prompt,
    "planning_agent_card":planning_agent_card,
    "planning_agent_prompt":planning_agent_prompt,
    "generate_metadata_for_all_artifacts":generate_metadata_for_all_artifacts,
    "host_prompt_template_for_osm":host_prompt_template_for_osm,
    "human_confirmation_addition":human_confirmation_addition,
    "query_updation_for_host":query_updation_for_host,
    "host_agent_card":host_agent_card,
    "send_message_definitions":send_message_definitions,
    "osm_tool_description":osm_tool_description,
    "code_executor_definition":code_executor_definition,
    "code_metadata_generator_definition":code_metadata_generator_definition,
    "metadata_all_artifacts":metadata_all_artifacts,
    "human_agent_card":human_agent_card,
    "Agent":Agent,
    "Human":Human,
    "AgentCard":AgentCard,
    "Artifact":Artifact
}