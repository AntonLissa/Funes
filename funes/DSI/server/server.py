from pathlib import Path
from flask import Flask, render_template, jsonify, request, session
import uuid
from datetime import datetime
import os
import sys
# Inserisci i percorsi dei moduli

sys.path.insert(0, str(str(Path(__file__).resolve().parent.parent.parent)))  # insert all'inizio del path


# Import PlanningLLM e XMLPlanningCleaner (Windows)
from Scripts.AIM.llm.LLM.planning_LLM import PlanningLLM
from Storage.StorageManager import StorageManager
from utils.utils import print_json
from Scripts.AIM.config.config_loader import ConfigLoader

app = Flask(__name__)
app.secret_key = "super_secret_key_change_me"

# dizionario globale per chat attive
active_chats = {}

# Inizializza PlanningLLM con dati di esempio
storage_manager = StorageManager()
my_data = {
    "planning_data": storage_manager.get_planning_data(),
    "datetime": datetime.now().strftime('%Y-%m-%d_%H:%M:%S'),
    "satellite_passages": storage_manager.get_orbit_from_json(),  # Aggiungi dati di passage se disponibili
    "soe": ""  # Aggiungi dati di sequence of events se disponibili
}

print_json(my_data['planning_data'])
print_json(my_data['satellite_passages'])

# --- ROTTE FLASK --- #

@app.route("/")
def index():
    return render_template("chat.html")


def get_planner_response(chat_id, user_message=None):
    planner = active_chats.get(chat_id)
    if not planner:
        raise ValueError(f"No planner loaded for chat_id {chat_id}")

    if user_message:
        planner.add_user_response(user_message)

    chatbot_response = planner.speak()
    return chatbot_response


@app.route("/chat/start")
def chat_start():
    # crea chat session
    if "chat_id" not in session:
        session["chat_id"] = str(uuid.uuid4())

    chat_id = session["chat_id"]

    # crea e carica dati nel PlanningLLM
    provider = GroqProvider(api_key=os.getenv("GROQ_API_KEY"))
    planner = PlanningLLM(model_name=provider.model_small_name, prompts={}) #)
    planner.load_data(my_data)
    active_chats[chat_id] = planner

    return jsonify({"robot": "Come posso aiutarti?", "chat_id": chat_id})


@app.route("/chat/send_message", methods=["POST"])
def chat_send_message():
    chat_id = session.get("chat_id")
    if not chat_id:
        return jsonify({"error": "No chat session"}), 400

    data = request.get_json()
    user_message = data.get("message", "")

    robot_message = get_planner_response(chat_id, user_message)
    return jsonify({"child": user_message, "robot": robot_message})


@app.route("/chat/exit", methods=["POST"])
def chat_exit():
    chat_id = session.get("chat_id")
    planner = active_chats.pop(chat_id, None)
    session.clear()
    if planner:
        file_path = planner.export_conversation()
        return jsonify({"link": file_path})
    return jsonify({"link": None})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
