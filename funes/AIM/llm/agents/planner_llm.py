

from funes.AIM.config import config_loader
from funes.AIM.core.agent_factory import AgentFactory
from funes.AIM.llm.agents.base_llm import BaseLLM

import re 
import json

class PlannerLLM(BaseLLM):
    agent_type="planner_llm"

    def __init__(self, model_name, prompts, provider):
            super().__init__(
                model_name=model_name,
                system_prompt=prompts["system_prompt"],
                user_prompt=prompts["user_prompt"],
                provider=provider
            )

    def get_reasoning_and_tools(self, data):
        try:
            llm_answer = self.speak(data)
            if llm_answer.startswith("```"):
                llm_answer = llm_answer[3:]

            if llm_answer.endswith("```"):
                llm_answer = llm_answer[:-3]
            data = json.loads(llm_answer)
            
   
            return {
                "goal": data.get("goal", ""),
                "plan_reasoning": data.get("plan_reasoning", ""),
                "execution_plan": data.get("execution_plan", []),
            }
        except Exception as e:
            print(f"Errore durante l'analisi della risposta del planner: {str(e)}")
            return {
                'analysis': "Non sono riuscito ad analizzare la query.",
                'tools': []
            }


    def build_prompt(self, data):
            return self.user_prompt.format(user_query = data['user_query'], conversation_history = data['conversation_history'], critic_feedback = data['critic_feedback'], called_tools = data['called_tools'])


if __name__ == '__main__':
    from funes.AIM.config.config_loader import ConfigLoader
    from funes.AIM.llm.provider.groq_provider import GroqProvider
    import funes.AIM.core.register_agents 
    from funes.AIM.core.agent_registry import registry

    config_loader = ConfigLoader()
    provider = GroqProvider(config_loader.load_api_key())
    factory = AgentFactory(registry, config_loader, provider)
    agent = factory.create_agent("planner_llm")
    queries = [
    # --- SEMPLICI ---
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
    for i in range(0, 1):
        print("_"*30)
        q = "Is the anomaly reported in ticket OPS-231 related to the FDS maneuver?"
        print(f"- Question: {q}")
        answer = agent.get_reasoning_and_tools(data={'user_query': q, 'conversation_history': [], 'critic_feedback': '', 'called_tools': []})
        for elem in answer:
            print(f"    - {elem}: {answer[elem]}")
        
