from src.utils.state import SupervisorState
from langgraph.graph import END

def check_tool_call(state: SupervisorState):
    last = state["messages"][-1]

    if not getattr(last, "tool_calls", None):
        return END

    tool_names = [tc["name"] for tc in last.tool_calls]

    if "SupervisorDecision" in tool_names:
        return "route_decision"
    return "tools"