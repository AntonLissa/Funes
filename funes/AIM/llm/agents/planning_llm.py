

from funes.AIM.llm.agents.base_llm import BaseLLM

class PlanningLLM(BaseLLM):
    agent_type="planning"

    def __init__(self, model_name, prompts, provider):
        super().__init__(
            model_name=model_name,
            system_prompt=prompts["system_prompt"],
            user_prompt=prompts["user_prompt"],
            provider=provider
        )

    def build_prompt(self, data):

        return self.user_prompt.format(
            remaining_iterations=data['remaining_iterations'],
            conversation_history=data['conversation_history'],
            critic_feedback=data['critic_feedback'],
            called_tools=data['called_tools'],
            user_query=data['user_query'],
        )
