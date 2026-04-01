

from funes.AIM.llm.LLM.base_llm import BaseLLM


class PlanningLLM(BaseLLM):

    def __init__(self, model_name, prompts, provider):
        super().__init__(
            model_name=model_name,
            system_prompt=prompts["system_prompts"]["planning"],
            user_prompt=prompts["user_prompt_templates"]["planning"],
            provider=provider
        )

        self.user_prompt = prompts["user_prompt_templates"]["planning"]

    def build_prompt(self, data):

        return self.user_prompt.format(
            planning_data=data['planning_data'],
            datetime=data['datetime'],
            satellite_passages=data['satellite_passages'],
            sequence_of_events=data['soe'],
            conversation_history=self.session_history
        )
