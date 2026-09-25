import gradio as gr
from config.print_config import PRINT

class GradioInterface:
    def __init__(self, graph):
        self.graph = graph
        demo = gr.ChatInterface(
            fn=self.chat,
            title="My AI Agent",
            description="Simple Gradio Chat",
        )
        demo.launch(prevent_thread_lock=True)

    def chat(self, message, history):
        if self.graph is not None:
            config = {
                "configurable": {
                    "thread_id": "gradio"
                }
            }
            response = self.graph.invoke({
                "messages": [
                    {
                        "role": "user",
                        "content": message
                    }
                ]
            }, config)

            messages = response.get("messages", [])
            if messages:
                last = messages[-1]
                content = last.content if hasattr(last, "content") else str(last)
                if isinstance(content, list):
                    return "".join(
                        block.get("text", "") if isinstance(block, dict) else str(block)
                        for block in content
                    )
                if PRINT: print(f"Output > {messages}")
                return str(content)

        return ""
