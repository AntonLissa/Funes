

from funes.AIM.config import config_loader
from funes.AIM.core.agent_factory import AgentFactory
from funes.AIM.llm.agents.base_llm import BaseLLM
import re 
import json

class DispatcherLLM(BaseLLM):
    agent_type="dispatcher"

    def __init__(self, model_name, prompts, provider):
            super().__init__(
                model_name=model_name,
                system_prompt=prompts["system_prompt"],
                user_prompt=prompts["user_prompt"],
                provider=provider
            )

    def get_reasoning_and_tools(self, query, tools_used=None):
        try:
            # Otteniamo la risposta testuale dall'LLM
            data = {'user_query': query}
            llm_answer = self.speak(data)
            data = json.loads(llm_answer)
            
   
            return {
                'analysis': data['analysis'],
                'tools': data['tools']
            }
        except Exception as e:
            print(f"Errore durante l'analisi della risposta del dispatcher: {str(e)}")
            return {
                'analysis': "Non sono riuscito ad analizzare la query.",
                'tools': []
            }


    def build_prompt(self, query):
            return self.user_prompt.format(user_query = query)


if __name__ == '__main__':
    from funes.AIM.config.config_loader import ConfigLoader
    from funes.AIM.llm.provider.groq_provider import GroqProvider
    import funes.AIM.core.register_agents 
    from funes.AIM.core.agent_registry import registry

    config_loader = ConfigLoader()
    provider = GroqProvider(config_loader.load_api_key())
    factory = AgentFactory(registry, config_loader, provider)
    agent = factory.create_agent("dispatcher")
    queries = [
    # --- SEMPLICI ---
    "What is the current spacecraft health status?",
    "Check network connectivity of all ground stations",
    "Show latest telemetry anomalies",
    "What are the upcoming planned passes for today?",
    "When is the next orbital maneuver scheduled for satellite IME01?",
    "Explain what a downlink pass is",

    # --- MEDIE ---
    "Why is there packet loss in the downlink stream?",
    "Are there any open incidents affecting ground stations?",
    "What is the visibility window for the spacecraft over Europe today?",
    "Summarize recent telemetry anomalies in the last 24 hours",
    "Check if today's planned operations conflict with current orbit constraints",
    "What does ticket OPS-231 report?",

    # --- DIFFICILI / REALI (quelle che ti fregano il dispatcher) ---
    "Why did the downlink performance degrade yesterday during pass 14?",
    "Is the anomaly reported in ticket OPS-231 related to the FDS maneuver?",
    "Which subsystem is responsible for the current power anomaly?",
    "Analyze the GS status",
    "Could the recent scheduling conflict have caused missed telemetry data?",
    "Correlate recent ground station outages with observed telemetry gaps",
    "Was the maneuver yesterday responsible for increased anomaly reports?",
    "Identify possible root cause of intermittent communication loss during last orbit"
    ]


    correct_tools = [
    # --- SEMPLICI ---
    ["telemetry_tool"],
    ["network_monitor"],
    ["telemetry_tool"],
    ["planning_tool"],
    ["fds_tool"],
    ["knowledge_base_tool"],

    # --- MEDIE ---
    ["network_monitor", "telemetry_tool"],
    ["ticketing_llm_tool", "network_monitor"],
    ["fds_tool", "planning_tool"],
    ["telemetry_tool", "ticketing_llm_tool"],
    ["planning_tool", "fds_tool"],
    ["ticketing_llm_tool"],

    # --- DIFFICILI ---
    ["network_monitor", "telemetry_tool", "ticketing_llm_tool", "planning_tool"],
    ["ticketing_llm_tool", "fds_tool"],
    ["telemetry_tool", "ticketing_llm_tool"],
    ["network_monitor", "ticketing_llm_tool", "planning_tool"],
    ["planning_tool", "fds_tool", "telemetry_tool"],
    ["network_monitor", "telemetry_tool", "ticketing_llm_tool"],
    ["fds_tool", "ticketing_llm_tool", "telemetry_tool"],
    ["telemetry_tool", "network_monitor", "fds_tool", "ticketing_llm_tool"]
    ]

    cont = 0
    for i in range(0, len(queries)):
        print("_"*30)
        q = queries[i]
        print(f"- Question: {q}")
        answer = agent.get_reasoning_and_tools(query = q)
        for elem in answer:
            print(f"    - {elem}: {answer[elem]}")
        
        for tool in correct_tools[i]:
                if tool not in answer['tools']:
                    print(f"    - Risposta mancante/errata per {elem}: {tool} non in {answer['tools']}")
                    cont += 1
    print(f"- Sono state sbagliate {cont}/{len(queries)}")