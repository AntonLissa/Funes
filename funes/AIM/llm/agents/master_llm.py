from datetime import datetime

from funes.AIM.llm.agents.base_llm import BaseLLM


class MasterLLM(BaseLLM):
    agent_type="master"

    def __init__(self, model_name, prompts, provider):
        super().__init__(
            model_name=model_name,
            system_prompt=prompts["system_prompt"],
            user_prompt=prompts["user_prompt"],
            provider=provider
        )

    def build_prompt(self, data):

        tool_results = data.get("tool_results", {})


        return self.user_prompt.format(
            datetime=datetime.now(),

            user_query=data.get("query", ""),

            conversation_history=self.get_recent_history(5),
            
            tool_results = tool_results
        )
