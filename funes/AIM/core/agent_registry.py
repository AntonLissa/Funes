registry = {}

def register(agent_type, agent_class):
    registry[agent_type] = agent_class
