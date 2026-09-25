from langgraph.graph import END
from src.utils.state import SupervisorState

def route_after_agent(state: SupervisorState):
    return "finalize" if state["mode"] == "consult" else END