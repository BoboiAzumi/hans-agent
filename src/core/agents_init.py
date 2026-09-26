from config.supervisor_agent_config import SUPERVISOR
from config.sub_agent_config import SUB_AGENT
from src.lib.agents import Agents
from src.utils.model import model_init

def supervisor_init():
    return model_init(
        SUPERVISOR.get("provider"),
        SUPERVISOR.get("model"),
        SUPERVISOR.get("key"),
        SUPERVISOR.get("base_url")
    )

def sub_agent_init():
    agents = Agents()
    for i in SUB_AGENT:
        llm = model_init(
            i.get("provider"),
            i.get("model"),
            i.get("key"),
            i.get("base_url")
        )
        agents.add_agent(i.get("model"), llm, i.get("system_prompt"), i.get("description"))

    return agents

def sub_agent_bind_tools(
    agents: Agents,
    tools
):
    for i in SUB_AGENT:
        _tools = []
        for j in i.get("tools"):
            if j not in tools:
                print(f"[warn] tool '{j}' not available for agent '{i.get('model')}', skipped")
                continue
            _tools.append(tools[j])
        agents.set_tools(i.get("model"), _tools)