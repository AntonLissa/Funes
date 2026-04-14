

'''
Questa classe gestisce le sessioni di chat, creando agenti e mantenendo lo stato delle conversazioni.
'''

from funes.DSI.core.chat_session import ChatSession


class ChatService:
    def __init__(self, session_manager, factory, storage):
        self.session_manager = session_manager
        self.factory = factory
        self.storage = storage


    def start_chat(self, chat_id, agent_type="planning"):
        agent = self.factory.create_agent(agent_type)
        session = self.session_manager.create_chat(chat_id, agent)
        return session

    def send_message(self, chat_id, message, data={"planning_data": None, "datetime": None, "satellite_passages": None, "soe": None}):
        session = self.session_manager.get_chat(chat_id)
        if not session:
            raise ValueError("Chat not found")
        session.add_user_message(message)
        return session.get_response(data)

    def get_chat_conversation(self, chat_id):
        chat_session =  self.session_manager.get_chat(chat_id)
        return chat_session.get_conversation()