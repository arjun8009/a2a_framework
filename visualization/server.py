from flask import Flask,request
from flask_socketio import SocketIO
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.card_templates import *


app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Predefined agents
agents = [host_agent_card.model_dump(),planning_agent_card.model_dump(),address_agent_card.model_dump(), named_area_agent_card.model_dump(),building_agent_card.model_dump(),plotting_agent_card.model_dump(),coding_agent_details.model_dump()]

@app.route("/agents")
def get_agents():
    return {"agents": agents}

@socketio.on("connect")
def handle_connect():
    print("Client connected")
    socketio.emit("agents_init", agents)

# ✅ Exposed function: call this to push new interactions dynamically
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

if __name__ == "__main__":
    # Optional background thread for testing
    #threading.Thread(target=simulate_interactions).start()
    socketio.run(app, host="0.0.0.0", port=5000)
