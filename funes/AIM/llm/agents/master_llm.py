from funes.AIM.llm.agents.base_llm import BaseLLM


class MasterLLM(BaseLLM):
    def __init__(self, model_name, prompts, provider):
        super().__init__(
            agent_type="master",
            model_name=model_name,
            system_prompt=prompts["system_prompt"],
            user_prompt=prompts["user_prompt_template"],
            provider=provider
        )
        self.prompts_config = prompts  # Salviamo i prompt per i sotto-agenti
        self.provider = provider
        self.agents = {} # Cache degli agenti creati

    def delegate_task(self, agent_type: str, model_name: str):
        """Crea un agente worker tramite la factory se non esiste già."""
        if agent_type not in self.agents:
            self.agents[agent_type] = AgentFactory.get_agent(
                agent_type=agent_type,
                model_name=model_name,
                prompts=self.prompts_config,
                provider=self.provider
            )
        return self.agents[agent_type]

