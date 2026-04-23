from pydantic import BaseModel


class DpoDataRaw(BaseModel):
    '''This is the data class for the DPO. It contains all the data that the DPO needs to make a decision. It is used to pass the data to the DPO and also to store the data in a structured way.'''
    agent_name: str
    agent_system_instruction : str
    agent_tool_definitions : list[object]
    agent_message_data : list[object]




class DpoDataFull(BaseModel):
    '''This is the final data class for the DPO. This data can be used to tune the model'''
    agent_name: str
    agent_message_data_preffered : DpoDataRaw
    agent_message_data_unpreffered : DpoDataRaw
