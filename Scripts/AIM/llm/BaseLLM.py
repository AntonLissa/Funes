from abc import ABC, abstractmethod

class BaseLLM(ABC):

    def __init__(self, model_name, system_prompt, user_prompt):
        self.model_name = model_name
        self.system_prompt = system_prompt
        self.user_prompt = user_prompt
        self.session_history = []

    def add_user_message(self, message):
        self.session_history.append(("user", message))

    def add_assistant_message(self, message):
        self.session_history.append(("assistant", message))

    @abstractmethod
    def build_prompt(self, data):
        pass

    def speak(self, data):

        prompt = self.build_prompt(data)

        response = call_llm_api(
            model_name=self.model_name,
            system_prompt_template=self.system_prompt,
            user_prompt_template=prompt,
            temperature=0
        )

        self.add_assistant_message(response)

        return response
