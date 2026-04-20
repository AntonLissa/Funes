from funes.AIM.core.agent_registry import register
from funes.AIM.llm.agents.planning_llm import PlanningLLM
from funes.AIM.llm.agents.knowledge_base_llm import KBLLM
from funes.AIM.llm.agents.query_rewrite_llm import QueryRewriteLLM
from funes.AIM.llm.agents.dispatcher_llm import DispatcherLLM
from funes.AIM.llm.agents.master_llm import MasterLLM

register("planning", PlanningLLM)
register("kb", KBLLM)
register("query", QueryRewriteLLM)
register("dispatcher", DispatcherLLM)
register("master", MasterLLM)