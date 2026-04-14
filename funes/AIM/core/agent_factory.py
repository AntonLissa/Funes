from matplotlib.units import registry


class AgentFactory:

    def __init__(self, registry, config_loader, provider):
        self.registry = registry
        self.llm_config = config_loader.load_yaml()
        self.provider = provider
        self.models = {'small': 'llama-3.1-8b-instant', 'large': 'llama-3.3-70b-versatile'}

    def create_agent(self, agent_type):

        if agent_type not in self.registry:
            raise ValueError(f"Agente '{agent_type}' non registrato")

        agent_class = self.registry[agent_type]

        prompts = {
            "system_prompt": self.llm_config[agent_type]["system_prompt"],
            "user_prompt": self.llm_config[agent_type]["user_prompt"]
        }

        return agent_class(
            model_name=self.models[self.llm_config[agent_type]['model_size']],
            prompts=prompts,
            provider=self.provider
        )


if __name__ == "__main__":
    from funes.AIM.config.config_loader import ConfigLoader
    from funes.AIM.llm.provider.groq_provider import GroqProvider
    import funes.AIM.core.register_agents 
    from funes.AIM.core.agent_registry import registry

    config_loader = ConfigLoader()
    provider = GroqProvider(config_loader.load_api_key())
    factory = AgentFactory(registry, config_loader, provider)
    agent = factory.create_agent("planning")
    print(agent.speak(data={'planning_data': 'Esempio di dati di pianificazione', 'datetime': '2024-06-01T12:00:00Z', 'satellite_passages': 'Esempio di passaggi satellitari', 'soe': 'Esempio di sequenza di eventi'}))