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
        "description":"Tool that executes code written by an agent",
        "parameters":{
            "type":"object",
            "properties":{
                "code":{
                    "type":"string",
                    "description":"Name of the agent the task needs to be delegated to"
                }
            }
        }
    }

