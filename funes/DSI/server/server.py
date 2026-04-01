from pathlib import Path
from flask import Flask, render_template, jsonify, request, session
import uuid
from datetime import datetime
import os
import sys



# Import PlanningLLM e XMLPlanningCleaner (Windows)
from funes.AIM.llm.LLM.planning_llm import PlanningLLM
from funes.Storage.StorageManager import StorageManager
from funes.utils.utils import print_json
from funes.AIM.config.config_loader import ConfigLoader
from funes.AIM.llm.provider.groq_provider import GroqProvider

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

# inizializzazione config loader
config_loader = ConfigLoader()


# --- ROTTE FLASK --- #

@app.route("/")
def index():
    return render_template("chat.html")


def get_planner_response(chat_id, user_message=None):
    planner_llm = active_chats.get(chat_id)
    if not planner_llm:
        raise ValueError(f"No planner loaded for chat_id {chat_id}")

    if user_message:
        planner_llm.add_user_message(user_message)

    chatbot_response = planner_llm.speak(my_data)
    return chatbot_response


@app.route("/chat/start")
def chat_start():
    # crea chat session
    if "chat_id" not in session:
        session["chat_id"] = str(uuid.uuid4())

    chat_id = session["chat_id"]

    # crea e carica dati nel PlanningLLM
    planning_llm_prompts = config_loader.load_yaml("llm_config.yaml")

    provider = GroqProvider(api_key=os.environ.get("GROQ_API_KEY"))
    planner_llm = PlanningLLM(model_name=provider.model_small_name, prompts=planning_llm_prompts, provider=provider)
    active_chats[chat_id] = planner_llm

    return jsonify({"robot": "Benvenuto! Come posso aiutarti?", "chat_id": chat_id})


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
    planner_llm = active_chats.pop(chat_id, None)
    session.clear()
    if planner_llm:
        file_path = planner_llm.export_conversation()
        return jsonify({"link": file_path})
    return jsonify({"link": None})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
