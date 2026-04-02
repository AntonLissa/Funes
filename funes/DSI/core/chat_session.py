"""
Questa classe rappresenta una sessione di chat tra un utente e un agente o un agente e un agente. Tiene traccia della cronologia di conversazione. 
"""

class ChatSession:
    def __init__(self, chat_id, agent):
        self.chat_id = chat_id
        self.agent = agent
        self.history = []

    def add_user_message(self, message):
        self.history.append({"role": "user", "text": message})
        self.agent.add_user_message(message)

    def get_response(self, data):
        reply = self.agent.speak(data)
        self.history.append({"role": "robot", "text": reply})
        return reply

    def export_history(self):
        # salva su file o DB
        return f"/path/to/export/{self.chat_id}.json"
