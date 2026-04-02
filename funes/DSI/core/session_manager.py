"""
Questa classe gestisce le sessioni di chat attive che possono essere tra user e master llm o master llm e agenti
"""

from funes.DSI.core.chat_session import ChatSession


class SessionManager:
    def __init__(self):
        self.active_chats = {}
    
    def create_chat(self, chat_id, agent):
        session = ChatSession(chat_id, agent)
        self.add_chat(session)
        return session

    def add_chat(self, chat_session):
        self.active_chats[chat_session.chat_id] = chat_session

    def get_chat(self, chat_id):
        if chat_id not in self.active_chats:
            raise ValueError(f"Chat session {chat_id} non trovata")
        return self.active_chats[chat_id]

    def remove_chat(self, chat_id):
        return self.active_chats.pop(chat_id, None)
    
    def list_chats(self):
        return list(self.active_chats.keys())
