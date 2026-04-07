import uuid

from flask import Blueprint, request, session, jsonify, render_template

from funes.AIM.config.config_loader import ConfigLoader
from funes.AIM.core.agent_factory import AgentFactory
from funes.AIM.llm.provider.groq_provider import GroqProvider
from funes.DSI.core.session_manager import SessionManager
from funes.DSI.services.chat_service import ChatService
import funes.AIM.core.register_agents 
from funes.AIM.core.agent_registry import registry
from funes.Storage import StorageManager

chat_bp = Blueprint("chat", __name__, template_folder="templates")

config_loader = ConfigLoader()
provider = GroqProvider(config_loader.load_api_key())

factory = AgentFactory(registry=registry, config_loader=config_loader, provider=provider)

session_manager = SessionManager()
storage_manager = StorageManager()
chat_service = ChatService(session_manager, factory, storage_manager)


@chat_bp.route("/")
def index():
    return render_template("chat.html")

@chat_bp.route("/chat/start")
def chat_start():
    chat_id = str(uuid.uuid4())

    chat_service.start_chat(chat_id)
    session["chat_id"] = chat_id
    return jsonify({"chat_id": chat_id, "robot": "Bentornato! Come posso esserti utile?"})

@chat_bp.route("/chat/send_message", methods=["POST"])
def chat_send_message():
    chat_id = session.get("chat_id")
    data = request.get_json()
    user_msg = data.get("message")
    robot_msg = chat_service.send_message(chat_id, user_msg)
    return jsonify({"child": user_msg, "robot": robot_msg})
