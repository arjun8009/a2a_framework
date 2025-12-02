from flask import Flask,request
from flask_socketio import SocketIO
from flask_cors import CORS
import sys, os
import json
import joblib
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.card_templates import *
from utils.initialize_os_agents import OSAgentsInitializer
from utils.tools import human_send_message
from utils.keys import set_api_keys
set_api_keys()

PATH_VISUALIZATION = r"C:\Users\ab1574\OneDrive - University of Exeter\Desktop\Ordnance_Survey\visualization"

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Predefined agents


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
            path = os.path.join(PATH_VISUALIZATION,response[1][0].data)
            data = load_html(path)
            return [{"role":"assistant","content":response[0]},{"role":"assistant","content":data}]
        else:
            return [{"role":"assistant","content":response[0]}]

    else:
        return [{"role":"assistant","content":response[0]}]






if __name__ == "__main__":
    # Optional background thread for testing
    #threading.Thread(target=simulate_interactions).start()
    socketio.run(app, host="0.0.0.0", port=5000)
