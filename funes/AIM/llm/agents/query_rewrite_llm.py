

from funes.AIM.llm.agents.base_llm import BaseLLM

class QueryRewriteLLM(BaseLLM):
    agent_type="planning"

    def __init__(self, model_name, prompts, provider):
        super().__init__(
            model_name=model_name,
            system_prompt=prompts["system_prompt"],
            user_prompt=prompts["user_prompt"],
            provider=provider
        )

    def build_prompt(self, conversation, user_query):

        return self.user_prompt.format(
            conversation_history=conversation,
            user_query = user_query
        )
