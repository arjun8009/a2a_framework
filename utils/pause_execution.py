import requests
from utils.code_explainer import explain_code
import traceback

URL = "http://localhost:5000/pause_execution"

def convert_code_to_args(code,artifact_names):

    columns,conditions,plotting = explain_code(code)
    
    if all(isinstance(i, list) for i in columns) and all(isinstance(i, list) for i in conditions):
        
        columns_flat = []
        conditions_flat = []
        database_flat = []
        
        for idx, (c,cd) in enumerate(zip(columns,conditions)):
            columns_flat.extend(c)
            conditions_flat.extend(cd)
            database_flat.extend(artifact_names[idx]*len(c))
        return {"columns":columns_flat,"conditions":conditions_flat}, {columns_flat[i]:conditions_flat[i] for i in range(len(conditions_flat))},plotting
    else:
        return {"columns":columns,"conditions":conditions},{columns[i]:conditions[i] for i in range(len(conditions_flat))},plotting
    
def make_request(url, payload):

    try:
        suggestion = requests.post(url,json=payload)
        suggestion = suggestion.json()
        if suggestion["reply"] is not None:
            return suggestion["reply"]
        else:
            return None
    except Exception as e:
        return None


def pause_tool_execution(agent_name, tool_name, tool_args, code_true):

    '''For coding agent tool_args = {"code":<str>, "artifact_names":[list]}'''
    try:
        if not code_true:
            suggestion = make_request(URL,{"agent_name":agent_name, "tool_name":tool_name, "tool_args":tool_args,"code":code_true})
            return suggestion
        else:
            table, tool_args_code, plotting = convert_code_to_args(tool_args["code"], tool_args["artifact_names"])
            code_json_send = {"agent_name":agent_name if plotting != True else "plotting_agent", "tool_name":tool_name,"database_name":"and".join(tool_args["artifact_names"]),
                              "table":table,"tool_args":tool_args_code,"code":code_true}

            suggestion = make_request(URL,code_json_send)
            return suggestion

    except Exception as e:
        print(traceback.format_exc)
        return None
        
