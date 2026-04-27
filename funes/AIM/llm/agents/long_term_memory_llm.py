

from funes.AIM.llm.agents.base_llm import BaseLLM

class LTMemoryLLM(BaseLLM):
    agent_type="long_term_memory"

    def __init__(self, model_name, prompts, provider):
        super().__init__(
            model_name=model_name,
            system_prompt=prompts["system_prompt"],
            user_prompt=prompts["user_prompt"],
            provider=provider
        )

    def build_prompt(self, data):

        return self.user_prompt.format(
            conversation_history=data['conversation_history'],  
        )
