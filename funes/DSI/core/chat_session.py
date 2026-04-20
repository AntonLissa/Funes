"""
Questa classe rappresenta una sessione di chat tra un utente e un agente o un agente e un agente. Tiene traccia della cronologia di conversazione. 
"""

from datetime import datetime


class ChatSession:
    def __init__(self, chat_id, agent):
        self.chat_id = chat_id
        self.agent = agent
        self.history = []

    def add_user_message(self, message):
        self.history.append({"role": "user", "text": message, "datetime": datetime.now().isoformat()})
        self.agent.add_user_message(message)

    def get_response(self, data):
        reply = self.agent.speak(data)
        self.history.append({"role": "assistant", "text": reply})
        return reply

    def set_history(self, history):
        self.history = history
        self.agent.session_history = history

    def get_conversation(self):
        return self.history
    
    def export_history(self):
        # salva su file o DB
        return f"/path/to/export/{self.chat_id}.json"
