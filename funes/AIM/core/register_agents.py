from funes.AIM.core.agent_registry import register
from funes.AIM.llm.agents.planning_llm import PlanningLLM

register("planning", PlanningLLM)
