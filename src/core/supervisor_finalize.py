from langchain_core.messages import HumanMessage
from src.utils.state import SupervisorState

def supervisor_finalize(state: SupervisorState):
    consult_result = state["consult_result"]

    if hasattr(consult_result, "content"):
        result_text = consult_result.content
    else:
        result_text = str(consult_result)

    note = HumanMessage(
        content=f"[Pendapat dari {state['target_agent']}]: {result_text}"
    )
    return { "messages": [note] }