

from funes.AIM.core.agent_factory import AgentFactory
from funes.AIM.llm.agents.base_llm import BaseLLM

class CriticLLM(BaseLLM):
    agent_type="critic"

    def __init__(self, model_name, prompts, provider):
        super().__init__(
            model_name=model_name,
            system_prompt=prompts["system_prompt"],
            user_prompt=prompts["user_prompt"],
            provider=provider
        )

    def build_prompt(self, data):

        return self.user_prompt.format(
            user_query=data['user_query'],
            tools_called=data['tools_called'],
            final_answer=data['final_answer']

        )

