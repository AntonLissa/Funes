from abc import ABC, abstractmethod

from funes.AIM.llm.provider.base_provider import BaseProvider

class BaseLLM(ABC):

    def __init__(self, model_name: str, system_prompt: str, user_prompt: str, provider: BaseProvider):
        
        self.model_name = model_name
        self.system_prompt = system_prompt
        self.user_prompt = user_prompt
        self.provider = provider


    @abstractmethod
    def build_prompt(self, data):
        pass


    def speak(self, data):
        prompt = self.build_prompt(data)

        response = self.provider.call(
            model_name=self.model_name,
            system_prompt=self.system_prompt,
            user_prompt=prompt,
            temperature=0
        )

        return response
