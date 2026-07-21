

import json

from funes.AIM.core.agent_factory import AgentFactory
from funes.AIM.llm.agents.base_llm import BaseLLM
from funes.Storage.storage_manager import StorageManager

class TicketLLM(BaseLLM):
    agent_type="ticket"

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
            tickets = data.get("tickets", [])

        )

if __name__ == '__main__':
    from funes.AIM.config.config_loader import ConfigLoader
    from funes.AIM.llm.provider.groq_provider import GroqProvider
    import funes.AIM.core.register_agents 
    from funes.AIM.core.agent_registry import registry

    config_loader = ConfigLoader()
    provider = GroqProvider(config_loader.load_api_key())
    factory = AgentFactory(registry, config_loader, provider)
    agent = factory.create_agent("ticket_llm")
    sm = StorageManager(light_mode=True)
    data = {"user_query": "Are there any open tickets related to network problems?", "tickets" : sm.get_tickets()}
    print(agent.speak(data=data))
    print(json.loads(agent.speak(data=data)).get("tickets", []))