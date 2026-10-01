from src.utils.state import SupervisorState
from langchain_core.messages import ToolMessage, AIMessage

def route_decision(state: SupervisorState):
    last = state["messages"][-1]
    decision_call = next(tc for tc in last.tool_calls if tc["name"] == "SupervisorDecision")
    args = decision_call["args"]

    tool_response = ToolMessage(
        content=args.get("task"),
        tool_call_id=decision_call["id"],
    )

    updates = {
        "mode": args["mode"], 
        "target_agent": args.get("target_agent"), 
        "task": args.get("task"),
    }

    if args["mode"] == "answer" and args.get("answer_text"):
        updates["messages"] = [AIMessage(content=args["answer_text"])]
    else:
        updates["messages"] = [tool_response]

    return updates