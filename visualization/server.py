from flask import Flask,request
from flask_socketio import SocketIO
from flask_cors import CORS
import sys, os
import json
import joblib
import geopandas as gpd
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.card_templates import *
from utils.initialize_os_agents import OSAgentsInitializer
from utils.tools import human_send_message
from utils.keys import set_api_keys
import threading
set_api_keys()

_human_event = threading.Event()
_human_reply = None

_pause_config = {"buildings":"call_os_ngd", "coding_agent":"code_executor"}
_pause_event = threading.Event()
_pause_reply = None

PATH_VISUALIZATION = r"C:\Users\ab1574\OneDrive - University of Exeter\Desktop\Ordnance_Survey\visualization"
DEFAULT_PATH_VISUALIZATION = r"C:\Users\ab1574\OneDrive - University of Exeter\Desktop\Ordnance_Survey"
PATH_ARTIFACTS = r"C:\Users\ab1574\OneDrive - University of Exeter\Desktop\Ordnance_Survey\artifacts"

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Predefined agents

@app.route("/Health", methods=['GET'])
def health_check():
    return {"status":"success"},200


@app.route("/human_send", methods=['POST'])
def send_human_query():
    global _human_reply, _human_event
    _human_event.clear()
    _human_reply = None
    
    data = request.get_json()
    query = data["query"]

    socketio.emit("human_input_required", {"query": query})
    
    got_reply = _human_event.wait(timeout=300)
    if not got_reply:
        return "Timeout — no human response received.", None

    return _human_reply

@app.route("/human-reply", methods=["POST"])
def human_reply():
    global _human_reply, _human_event

    data = request.get_json()
    if not data or "content" not in data:
        return {"error": "Missing content"}, 400

    _human_reply = data["content"]
    _human_event.set()  # unblocks human_send_message above

    return {"status": "ok"}, 200

@app.route("/pause_execution", methods=['POST'])
def pause_execution():
    data = request.get_json()
    if data["code"]:
        reply = tool_breakpoint(data["agent_name"],data["tool_name"],data["database_name"],data["tool_args"],data["table"])
    else:
        reply = tool_breakpoint(data["agent_name"], data["tool_name"],data["tool_name"],data["tool_args"],None)
    return {"status": "ok", "reply": reply},200
    
def format_arguments(agent_name, database_name, tool_args, code_table):

    if code_table is None:
        table = {"columns":list(tool_args.keys()), "conditions":list([str(i) for i in tool_args.values()])}
    else:
        table = code_table
    
    print("tool args received", tool_args)
    return {"agent_name":agent_name,"database_name":database_name, "table":table, "tool_args":tool_args}



def tool_breakpoint(agent_name:str, tool_name:str, database_name:str, tool_args:object, code_table:dict):
    global _pause_reply, _pause_event
    
    tools_to_pause = _pause_config.get(agent_name,[])
    arguments = format_arguments(agent_name,database_name,tool_args,code_table)
    
    if tool_name not in tools_to_pause:
        arguments["pause"] = False
        send_code_data(arguments)
        return None

    arguments["pause"] = True
    send_code_data(arguments)
    
    _pause_event.clear()
    _pause_reply = None

    got_reply = _pause_event.wait(timeout=300)
    if not got_reply:
        return None

    return _pause_reply

@app.route("/resume-execution", methods=["POST"])
def resume_execution():
    """
    Body: {"suggestion": "..."} or {"suggestion": null} to proceed unchanged
    """
    global _pause_reply, _pause_event

    data = request.get_json()
    _pause_reply = data.get("suggestion")  # None = proceed as-is
    _pause_event.set()
    return {"status": "ok"}, 200





@app.route("/config-choice",methods=['POST'])
def initialise_config():
    global agents
    global agent_archiecture
    choice = request.get_json()
    print("Choice",choice)
    choice = choice["choice"]
    config = None
    with open(f"C:/Users/ab1574/OneDrive - University of Exeter/Desktop/Ordnance_Survey/agent_frameworks/{choice}.json","rb") as file:
        config = json.load(file)
    agent_archiecture = OSAgentsInitializer(config).initialize_all_agents()
    agents = [agent_archiecture[i].agent_identity.model_dump() for i in agent_archiecture.keys()]
    socketio.emit("agents_init", agents)
    return {"status":"connected"},200
    

def send_code_data(code_data):
    """
    code_data = {
        "agent_name": "A1",
        "database_name": "D1",
        "table": {
            "columns": ["col1", "col2"],
            "conditions": ["col1 = $1", "col2 > 0"]
        }
    }
    """
    print("Code data sent", code_data)
    socketio.emit("new_code_data", code_data)

@app.route("/receive-code-data", methods=["POST"])
def receive_code_data():
    data = request.get_json()
    if not data:
        return {"error": "No JSON payload"}, 400
    send_code_data(data)
    return {"status": "ok"}, 200



def send_interaction(interaction):
    """
    interaction = {
        "source": "agent_a",
        "target": "agent_b",
        "msg": "Please execute task",
        "response": "Done!"
    }
    """
    print("Interaction sent",interaction)
    socketio.emit("new_interaction", interaction)

@app.route("/interact", methods=["POST"])
def interact():
    data = request.get_json()
    if not data:
        return {"error": "No JSON payload"}, 400
    send_interaction(data)
    return {"status": "ok"}, 200


def load_html(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    return content


@app.route("/receive-data",methods=["POST"])
def receive_data():
    query = request.get_json()["updated_message"]["content"]
    if "human" in agent_archiecture.keys():
        response = human_send_message(query,[agent_archiecture["host_agent"]])
    else:
        response = agent_archiecture["host_agent"].run_agent([{"role":"user","content":query}])
    
    print("\n \n RESPONSE FINAL \n \n",response)
    if (isinstance(response,list) or isinstance(response,set) or isinstance(response,tuple)) and len(response)>1:

        if response[1] is None:
            return [{"role":"assistant","content":response[0]}]
        elif isinstance(response[1][0].data,str):
            path = os.path.join(PATH_VISUALIZATION,response[1][0].data) if os.path.exists(os.path.join(PATH_VISUALIZATION,response[1][0].data)) else os.path.join(DEFAULT_PATH_VISUALIZATION,response[1][0].data)
            data = load_html(path)
            return [{"role":"assistant","content":response[0]},{"role":"assistant","content":data}]
        else:
            return [{"role":"assistant","content":response[0]}]

    else:
        return [{"role":"assistant","content":response}]

@app.route("/get-artifacts",methods=["POST"])
def extract_artifacts():
    if len(os.listdir(PATH_ARTIFACTS)) == 0:
        return []
    else:
        artifacts = [joblib.load(os.path.join(PATH_ARTIFACTS,i)) for i in os.listdir(PATH_ARTIFACTS)]
        artifacts_filtered = [i for i in artifacts if isinstance(i.data,gpd.GeoDataFrame)]
        artifacts_json = [{"name":i.name, "artifact":json.loads(i.data.drop(columns="geometry").copy().applymap(lambda x: x.isoformat() if hasattr(x, "isoformat") else x).to_json(orient="records"))} for i in artifacts_filtered]
        return artifacts_json


    





if __name__ == "__main__":
    # Optional background thread for testing
    #threading.Thread(target=simulate_interactions).start()
    socketio.run(app, host="0.0.0.0", port=5000)
