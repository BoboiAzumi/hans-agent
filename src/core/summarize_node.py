from config.summerization_config import MAX_TOKEN, KEEP_TOKEN
from src.utils.state import SupervisorState
from langchain_core.messages.utils import count_tokens_approximately, trim_messages
from langchain_core.messages import SystemMessage, HumanMessage, RemoveMessage

def summarize_node(llm):
    def summarize_node_bind(state: SupervisorState):
        messages = state["messages"]
        if count_tokens_approximately(messages) <= MAX_TOKEN:
            print(f"Skip Summarize, Token: {count_tokens_approximately(messages)}")
            return {}

        print(f"Summarize, Token: {count_tokens_approximately(messages)}")
        recent = trim_messages(
            messages,
            strategy="last",
            max_tokens=KEEP_TOKEN,
            token_counter=count_tokens_approximately,
            start_on="human",
            include_system=False
        )

        keep_ids = { m.id for m in recent }
        old = [ m for m in messages if m.id not in keep_ids ]

        prev = state.get("summary", "")
        output = llm.invoke([
            SystemMessage(
                "Ringkas percakapan berikut secara padat, bagi menjadi 2 kategori yaitu:\n"
                "1. Ringkasan percakapan (summary)\n"
                "2. Informasi penting (important)\n\n"
                "ATURAN INFORMASI PENTING: \n"
                "1. Jika riwayat percakapan menunjukkan bahwa suatu informasi penting sudah dicatat, jangan melampirkan informasi itu kembali ke kategori important.\n"
                "2. Jika informasi penting muncul setelah proses pencatatan, informasi tersebut tetap harus dipertimbangkan dan dilampirkan jika belum tercatat.\n"
                f"Ringkasan sebelumnya: {prev}"
            ),
            *old, HumanMessage("Ringkas")
        ])

        delete_messages = [ RemoveMessage(id=m.id) for m in old ]

        return {
            "summary": output.summary,
            "important": output.important,
            "messages": delete_messages
        }
    
    return summarize_node_bind