import uuid

from flask import Blueprint, request, session, jsonify, render_template

from funes.AIM.config.config_loader import ConfigLoader
from funes.AIM.core.agent_factory import AgentFactory
from funes.AIM.llm.provider.groq_provider import GroqProvider
from funes.DSI.core.session_manager import SessionManager
from funes.DSI.services.chat_service import ChatService
import funes.AIM.core.register_agents 
from funes.AIM.core.agent_registry import registry
from funes.Storage.storage_manager import StorageManager

chat_bp = Blueprint("chat", __name__, template_folder="templates")

config_loader = ConfigLoader()
provider = GroqProvider(config_loader.load_api_key())

factory =   AgentFactory(registry=registry, config_loader=config_loader, provider=provider)

query_llm = factory.create_agent('query')
session_manager = SessionManager()
storage_manager = StorageManager(light_mode=False)
chat_service = ChatService(session_manager, factory, storage_manager)



user_id = 'user_1' # SOLO PER TEST


def check_chat_started():
    chat_id = session.get("chat_id")

    if not chat_id:

        chat_id = str(uuid.uuid4())
        session["chat_id"] = chat_id

        storage_manager.create_chat(
            chat_id=chat_id,
            user_id=user_id,
            agent="kb"
        )

        chat_service.start_chat(chat_id, agent_type="kb")

    return chat_id



@chat_bp.route("/")
def index():

    session.pop("chat_id", None)

    return render_template("chat.html")


@chat_bp.route("/chat/new")
def chat_start():
    return jsonify({"chat_id": '000', "robot": "Welcome back! How can I help you?"})

@chat_bp.route("/chat/send_message", methods=["POST"])
def chat_send_message():
    chat_id = check_chat_started()
    data = request.get_json()
    user_msg = data.get("message")

    if query_llm:
        enhanced_query = query_llm.speak(conversation = chat_service.get_chat_conversation(chat_id=chat_id), query=user_msg)
        print(f"chat routes: ENHANCED QUERY: {enhanced_query}")
    else:
        enhanced_query = user_msg
    data = storage_manager.get_kb_results(enhanced_query)
    robot_msg = chat_service.send_message(chat_id, user_msg, data=data)
    
    storage_manager.save_message(chat_id=chat_id, user_id=user_id, role="user", content=user_msg)
    storage_manager.save_message(chat_id=chat_id, user_id=user_id, role="assistant", content=robot_msg)
    return jsonify({"child": user_msg, "robot": robot_msg})


@chat_bp.route("/chat/load_latest")
def chat_retrieve():
    print("---REtrieving chats")
    chats = storage_manager.list_user_chats(user_id=user_id)
    print(f"retrieved: {chats}")
    return jsonify({
        "chats": chats
    })

@chat_bp.route("/load_chat/<chat_id>")
def get_chat(chat_id):

    messages = storage_manager.get_chat_messages(chat_id)
    session["chat_id"] = chat_id

    chat_service.start_chat(chat_id, agent_type="kb")


    formatted = []

    for m in messages:
        formatted.append({
            "role": m["role"],
            "text": m["content"],
            "datetime": str(m.get("created_at"))
        })

    chat_service.load_data_from_db(chat_id, formatted)

    return jsonify({"messages": formatted})
