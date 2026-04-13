from abc import ABC, abstractmethod

from funes.AIM.llm.provider.base_provider import BaseProvider

class BaseLLM(ABC):

    def __init__(self, model_name: str, system_prompt: str, user_prompt: str, provider: BaseProvider):
        
        self.model_name = model_name
        self.system_prompt = system_prompt
        self.user_prompt = user_prompt
        self.session_history = []
        self.provider = provider

    def add_user_message(self, message):
        self.session_history.append(("user", message))

    def add_assistant_message(self, message):
        self.session_history.append(("assistant", message))

    @abstractmethod
    def build_prompt(self, data):
        pass

    def get_last_user_message(self):
        for role, msg in reversed(self.session_history):
            if role == "user":
                return msg
        return ""

    def get_recent_history(self, n=2):
        return self.session_history[-n:]

    def speak(self, data):

        prompt = self.build_prompt(data)

        response = self.provider.call(
            model_name=self.model_name,
            system_prompt=self.system_prompt,
            user_prompt=prompt,
            temperature=0
        )

        self.add_assistant_message(response)

        return response
