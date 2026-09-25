from src.core.agents_init import supervisor_init, sub_agent_init, sub_agent_bind_tools
from src.core.graph import create_graph
from src.lib.loader import plugin_load
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3

def build_multi_agent():
    supervisor = supervisor_init()
    sub_agent = sub_agent_init()

    plugins = plugin_load()
    tools = {}
    for i in plugins:
        if not "tool" in plugins[i]:
            continue
        plugins[i]["tool"].name = i
        tools[i] = plugins[i]["tool"]

    sub_agent_bind_tools(sub_agent, tools)

    graph = create_graph(supervisor, sub_agent, tools)

    conn = sqlite3.connect(
        "checkpoints.db",
        check_same_thread=False
    )
    
    checkpointer = SqliteSaver(conn)
    app = graph.compile(checkpointer=checkpointer)

    for i in plugins:
        if not "interface" in plugins[i]:
            continue
        plugins[i]["interface"](app)

    return app