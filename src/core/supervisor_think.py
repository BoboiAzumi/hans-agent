from src.utils.state import SupervisorState
from src.lib.agents import Agents
from langchain_core.messages import SystemMessage
from config.base_prompt_config import BASE_PROMPT
from config.print_config import PRINT

def supervisor_think(llm, sub_agents: Agents = None, tools: dict = None):
    def supervisor_think_llm_bind(state: SupervisorState):
        messages = state["messages"]
        summary = state.get("summary", "")
        important = state.get("important", "")

        if not messages or not isinstance(messages[0], SystemMessage):
            agent_catalog = sub_agents.catalog() if sub_agents else "Tidak ada sub-agent"
            tool_names = ", ".join(tools.keys()) if tools else "Tidak ada tools"
            summary_prompt = summary if summary else "Belum ada"
            important_prompt = important if important else "Belum ada"
            additional = "Instruksi tambahan : **WAJIB** mencatat informasi penting menggunakan tool pencatatan (jika tersedia) segera setelah informasi tersebut teridentifikasi, apabila informasi tersebut belum tercatat sebelumnya. Jangan menunda pencatatan hingga akhir percakapan." if important else ""

            dynamic_prompt = (
                BASE_PROMPT + "\n\n"
                f"Sub-agent yang terhubung:\n{agent_catalog}\n\n"
                f"Tools yang tersedia: {tool_names}\n\n"
                f"Ringkasan saat ini : {summary_prompt}\n\n"
                f"Informasi penting : {important_prompt}\n\n" +
                additional
            )

            messages = [SystemMessage(content=dynamic_prompt)] + messages

        response = llm.invoke(messages)
        if PRINT: print(f"Response > { response }")
        return { "messages": [response] }

    return supervisor_think_llm_bind
