from langchain_core.messages import HumanMessage, RemoveMessage
from src.utils.state import SupervisorState
from src.lib.agents import Agents

def call_other_agent(agent: Agents):
    def call_other_agent_bind(state: SupervisorState):
        print(f"Call Agent : {state['target_agent']}")
        agent_info = agent.get().get(state["target_agent"])
        subagent_app = agent_info["graph"]

        task_text = state.get("task")

        if task_text:
            task_msg = HumanMessage(content=task_text)
        else:
            task_msg = state["messages"][-1]
            for m in reversed(state["messages"]):
                if isinstance(m, dict):
                    if m.get("role") == "user":
                        task_msg = m
                        break
                else:
                    if getattr(m, "type", "") == "human":
                        task_msg = m
                        break

        sub_result = subagent_app.invoke({"messages": [task_msg]})
        final_answer = sub_result["messages"][-1]
    
        already_asked = state.get("consulted_agent", [])
        hop_count = state.get("hop_count", 0)

        update = {
            "consulted_agent": already_asked + [state["target_agent"]],
            "hop_count": hop_count + 1,
        }

        if state["mode"] == "consult":
            update["consult_result"] = final_answer
        else:
            messages_to_remove = [
            #    RemoveMessage(id=m.id)
            #    for m in state["messages"]
            #    if getattr(m, "type", "") == "ai"
            ]
            update["messages"] = messages_to_remove + [final_answer]

        return update

    return call_other_agent_bind