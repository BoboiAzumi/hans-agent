from src.utils.state import SupervisorState

def route_after_decision(state: SupervisorState):
    return "answer" if state["mode"] == "answer" else "other_agent"