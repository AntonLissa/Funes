from funes.AIM.core.agent_registry import register
from funes.AIM.llm.agents.planning_llm import PlanningLLM
from funes.AIM.llm.agents.knowledge_base_llm import KBLLM
register("planning", PlanningLLM)
register("kb", KBLLM)
