''' Here include all the tool definitions which will be provided to llms. Currently only openai tools are supported but will include opensource llms laters'''

send_message_definitions = {
        "type":"function",
        "name":"send_message",
        "description":"Tool that sends messages to another agent to perform a task and provides the agent output",
        "parameters":{
            "type":"object",
            "properties":{
                "target":{
                    "type":"string",
                    "description":"Name of the agent the task needs to be delegated to"
                },
                "task_description":{
                    "type":"string",
                    "description":"The description of the task the agent has to perform"
                }
            }
        }
    }


code_executor_definition = {
        "type":"function",
        "name":"code_executor",
        "description":"Tool that executes code written by an agent using provided artifact names as data inputs.",
        "parameters":{
            "type":"object",
            "properties":{
                "code":{
                    "type":"string",
                    "description":"A string containing python code to be executed"
                },
                "artifact_names":{
                    "type":"array",
                    "items":{
                        "type":"string"
                    },
                    "description":"A list of artifact names which the code will be executed on"
                }
            }
        }
    }

code_metadata_generator_definition = {
        "type":"function",
        "name":"generate_metadata_for_artifacts",
        "description":"Tool that generates metadata for a list of artifact names provided to it",
        "parameters":{
            "type":"object",
            "properties":{
                "artifact_names":{
                    "type":"array",
                    "items":{
                        "type":"string"
                    },
                    "description":"A list of artifact names to generate metadata for"
                }
            }
        }
    }

metadata_all_artifacts = {
        "type":"function",
        "name":"generate_metadata_for_all_artifacts",
        "description":"Tool that generates metadata for all artifacts so you can tell the agents what artifacts to use correctly",
    }



os_ngd_tool_description = {
        "type":"function",
        "name":"call_os_ngd",
        "description":"Tool that search os ngd and returns close results based on query but is not fully accurate",
        "parameters":{
            "type":"object",
            "properties":{
                "filters":{
                    "type":["array","null"],
                    "items":{
                        "type":"string"
                    },
                    "description":"A list of predefined filters provided"
                },
                "bbox":{
                    "type":["string","null"],
                    "description":"bbox tells the tool to search within an artifact polygon. So an artifact of an area maybe stored and you can give the name of the artifact to search within"
                },
                "polygon_or_point":{
                    "type":["boolean","null"],
                    "description":"A boolean to indicate if the user wants to search named area point data or polygon data. True for polygon data and False for point data"
                },
                "street_address":{
                    "type":["boolean","null"],
                    "description":"A boolean to indicate if the user wants to search streets or roads. True for street address data and False for address data"
                },
                "filename":{
                    "type":"string",
                    "description":"The name of the file to save the artifact as"
                }
            },
        }
    }
