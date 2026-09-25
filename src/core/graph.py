from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import SystemMessage
from src.lib.agents import Agents
from src.utils.state import SupervisorState, SupervisorDecision, Summarization
from src.core.supervisor_think import supervisor_think
from src.core.call_other_agent import call_other_agent
from src.core.supervisor_finalize import supervisor_finalize
from src.core.check_tool_call import check_tool_call
from src.core.route_after_decision import route_after_decision
from src.core.route_after_agent import route_after_agent
from src.core.route_decision import route_decision
from src.core.summarize_node import summarize_node

def create_sub_agent_graph(
    sub_agent: Agents
):  
    for agent_name, agent_prop in sub_agent.get().items():
        def think(state: MessagesState, _prop=agent_prop):
            messages = state["messages"]
            if not messages or not isinstance(messages[0], SystemMessage):
                messages = [{ "role": "system", "content": _prop.get("system_prompt", "") }] + messages
            response = _prop["factory"].invoke(messages)
            return { "messages": [response] }

        def agent_continue(state: MessagesState):
            last = state["messages"][-1]
            return "tools" if getattr(last, "tool_calls", None) else END

        sub_agent_graph = StateGraph(MessagesState)
        sub_agent_graph.add_node("think", think)
        sub_agent_graph.add_edge(START, "think")
        if(agent_prop["tools"]):
            sub_agent_graph.add_node("tools", ToolNode(agent_prop["tools"]))
            sub_agent_graph.add_edge("tools", "think")
        sub_agent_graph.add_conditional_edges("think", agent_continue, { "tools": "tools", "__end__": END } if agent_prop["tools"] else {"__end__": END})

        sub_agent.add_graph(agent_name, sub_agent_graph.compile())

def create_graph(
    supervisor,
    sub_agent: Agents,
    tools,
):
    tools_list = list(tools.values()) + [ SupervisorDecision ]
    supervisor_with_tools = supervisor.bind_tools(tools_list)
    supervisor_summary = supervisor.with_structured_output(Summarization)

    create_sub_agent_graph(sub_agent)
    
    graph = StateGraph(SupervisorState)
    graph.add_node("summarize", summarize_node(supervisor_summary))
    graph.add_node("think", supervisor_think(supervisor_with_tools, sub_agent, tools))
    graph.add_node("tools", ToolNode(tools_list))
    graph.add_node("route_decision", route_decision)
    graph.add_node("other_agent", call_other_agent(sub_agent))
    graph.add_node("finalize", supervisor_finalize)

    graph.add_edge(START, "summarize")
    graph.add_edge("summarize", "think")
    graph.add_conditional_edges("think", check_tool_call, { 
        "tools": "tools", 
        "route_decision": "route_decision",
        "__end__": END
    })
    graph.add_edge("tools", "think")
    graph.add_conditional_edges("route_decision", route_after_decision, { "answer": END, "other_agent": "other_agent" })
    graph.add_conditional_edges("other_agent", route_after_agent, { "finalize": "finalize", "__end__": END })
    graph.add_edge("finalize", "summarize")

    return graph