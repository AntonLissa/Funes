from funes.AIM.core.agent_registry import register
from funes.AIM.llm.agents.critic_llm import CriticLLM
from funes.AIM.llm.agents.planning_llm import PlanningLLM
from funes.AIM.llm.agents.knowledge_base_llm import KBLLM
from funes.AIM.llm.agents.query_rewrite_llm import QueryRewriteLLM
from funes.AIM.llm.agents.planner_llm import PlannerLLM
from funes.AIM.llm.agents.master_llm import MasterLLM
from funes.AIM.llm.agents.long_term_memory_llm import LTMemoryLLM
from funes.AIM.llm.agents.ticket_llm import TicketLLM

register("planning_llm", PlanningLLM)
register("kb", KBLLM)
register("query", QueryRewriteLLM)
register("planner_llm", PlannerLLM)
register("master", MasterLLM)
register("long_term_memory", LTMemoryLLM)
register("critic_llm", CriticLLM)
register("ticket_llm", TicketLLM)