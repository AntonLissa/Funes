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
from funes.langgraph.graph.graph_engine import GraphEngine
from langchain_core.messages import HumanMessage, AIMessage

chat_bp = Blueprint("chat", __name__, template_folder="templates")

config_loader = ConfigLoader()
provider = GroqProvider(config_loader.load_api_key())

factory =   AgentFactory(registry=registry, config_loader=config_loader, provider=provider)

session_manager = SessionManager()
storage_manager = StorageManager(light_mode=False)
chat_service = ChatService(session_manager, factory, storage_manager)

engine = GraphEngine(factory, storage_manager)

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

    if not user_msg:
        return jsonify({"error": "No message provided"}), 400

    try:
        # 2. DELEGA AL GRAFO: Fa tutto lui (Dispatcher -> Tools -> Master)
        # Nota: se vuoi passare la storia della conversazione, potresti dover 
        # passare il chat_id al GraphEngine per recuperare i messaggi precedenti.
        robot_msg = engine.run(user_msg, chat_id=chat_id)

        
    except Exception as e:
        print(f"Errore nel GraphEngine: {e}")
        robot_msg = f"Mi dispiace, si è verificato un errore tecnico nell'elaborazione della richiesta: {e}"
    
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
    graph_messages = []

    for m in messages:
        formatted.append({
            "role": m["role"],
            "text": m["content"],
            "datetime": str(m.get("created_at"))
        })
        if m["role"] == "user":
            graph_messages.append(HumanMessage(content=m["content"]))
        else:
            graph_messages.append(AIMessage(content=m["content"]))
   
    engine.app.update_state(
    config={"configurable": {"thread_id": chat_id}},
    values={"messages": graph_messages}
    )

    chat_service.load_data_from_db(chat_id, formatted)

    return jsonify({"messages": formatted})
