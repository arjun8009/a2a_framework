from openai import OpenAI
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage,SystemMessage
import json
import warnings


# We can create hybrid architectures with both openai and whitebox models. 
# Without GPU availability let us limit to 3b-8b models only. 
# In such cases we do not use these models for data analysis or tool usage but as supervisors to coding agents


# This is a utility function to try and parse json response from the llm and validate it using our schema. Should work normally but edge cases will be there
def parse_and_validate(output:str,schema:object):
    '''
    Parse through the llm output and convert it to structured. Used in cases where reasoning models do not support structured output
    args:
    output : str = output of the model
    schema : orginal pydantic schema

    output: parsed schema
    '''
    output = output.replace("`","").replace("json","")
    return schema.model_validate_json(output)

#Function that tries to convert pydantic schema to a json schema automatically and this can be added to the prompt
def convert_pydantic_schema_to_json(schema):
    '''
    Convert pydantic schema to json schema
    args:
    schema: pydantic schema for structured output
    output:
    json schema to be added to the prompt'''
    schema_dumped = {k: v.default for k, v in schema.model_fields.items()}
    return json.dumps(schema_dumped,indent=2)


# Function that  creates compatible prompt formats given an llm instance. messages should be made in default openai api style
def create_compatible_prompt_template(llm_instance,messages:list,isthinking:bool):
    '''Make the messages compatible accross various llm platforms.
    Args:
    llm_instance: The instantiated LLM model
    messages: list of messages in openai style
    
    outputs:
    messages : Now compatible with llm instance'''
    
    # if it is openai instance then return them
    if not isinstance(llm_instance,ChatOllama):
        if isthinking:
            for i,j in enumerate(messages):
                if j["role"] == "system":
                    messages[i]["role"] = "user"
        return messages
    else:
        messages_changed = []
        for i in messages:
            if i["role"]=="system":
                messages_changed.append(SystemMessage(content = i["content"]))
            else:
                messages_changed.append(HumanMessage(content=i["content"]))
        return messages_changed
    

# Function to run an llm instance can be a langchain instance or an openai instance. Will return output in different formats : structured, messages and tools.
# Note tools can only be used for openai llms

def run_llm(model_name:str, messages: list, schema:object, tools:object, additional_args={"temperature":0,"max_tokens":2048, "parallel_tool_calls":True}):
    ''' Run the LLM instance with the given prompt.
    Args:
        model name : Name of a model from a choice of approved models current llama3.2, gpt-4 variants and thinking models o1-o3 models
        messages (list): A list of messages to send to the LLM
        schema : A pydantic object
        tools : Tool descriptions will only be applied to openai llms
        args : more args containing temperature and max tokens
    Returns:
        The response from the LLM.
        can be an object in case of structured output
        can be a list of messages in case of tools
        can be a simple response'''
    
    # use default args and add keys of additional args
    default_args = {"temperature":0,"max_tokens":2048, "parallel_tool_calls":True}
    args = {**default_args, **additional_args}

    
    # Check if openai model else checks for ollama models
    # also checks if it is a reasoning model or not. As thinking models do not accept temperature and max_tokens
    
    isthinking = False
    if model_name.startswith("gpt") or model_name.startswith("o"):
        llm_instance = OpenAI()
        isthinking = True if model_name.startswith("o") or model_name=="gpt-5" else False
    
    elif model_name.startswith("llama"):
        llm_instance = ChatOllama(model=model_name,max_tokens=args["max_tokens"],temperature=args["temperature"])
    else:
        return "LLM model is not supported"
    
    # if Ollama make the messages compatible and then call it while checking for schema. Does not support tools
    messages = create_compatible_prompt_template(llm_instance,messages,isthinking)
    if isinstance(llm_instance, ChatOllama):
        if tools is not None:
            return "We are not supporting tools with open source llms at the moment"
        if schema is not None:
            return llm_instance.with_structured_output(schema).invoke(messages)
        else:
            return llm_instance.invoke(messages).content
    else:
        # if openai check for thinking, schema and tools. May need to refactor this later to make it efficient
        openai_llm_instance = llm_instance
        
        if schema is not None:
            if not isthinking:
                response = openai_llm_instance.beta.chat.completions.parse(model=model_name,temperature=args["temperature"],messages=messages,response_format= schema)
                return response.choices[0].message.parsed
            else:
                warnings.warn("NOTE : Openai reasoning models do not support structured output so will  provide the structure in prompt and try. Susceptible to failure",UserWarning)
                
                # convert the pydantic schema to json
                json_schema = convert_pydantic_schema_to_json(schema)
                # make a custom instruction to respond in a particular format
                response_format_ins = "Respond using the following schema so that json.loads works on the ouptut you provide \n json schema : " + json_schema
                messages[-1]["content"] = messages[-1]["content"] + "\n" + response_format_ins
                response = openai_llm_instance.chat.completions.create(model=model_name,messages=messages)
                try:
                    return parse_and_validate(response.choices[0].message.content,schema)
                except Exception as e:
                    return "Parsing Failed for json output."
        else:
            if tools:
                if not isthinking:
                    return openai_llm_instance.responses.create(model = model_name,temperature=args["temperature"],parallel_tool_calls=args["parallel_tool_calls"],input=messages, tools=tools)
                else:
                    return openai_llm_instance.responses.create(model = model_name,input=messages,parallel_tool_calls=args["parallel_tool_calls"], tools=tools)
            else:
                if not isthinking:
                    return openai_llm_instance.chat.completions.create(model = model_name,max_tokens=args["max_tokens"],temperature=args["temperature"],messages=messages).choices[0].message.content
                    
                else:
                    return openai_llm_instance.chat.completions.create(model = model_name,messages=messages).choices[0].message.content

    

