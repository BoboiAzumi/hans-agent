import threading
import json
from flask import Flask, jsonify, request

class Graph:
    def __init__(self):
        self.graph = None

    def bind(self, graph):
        self.graph = graph
        return self

    def get(self):
        if not self.graph == None:
            return self.graph
        return None

    def call(self, message, thread_id):
        config = {
            "configurable": {
                "thread_id": thread_id
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
            return str(content)

graph = Graph()
app = Flask(__name__)

@app.route("/", methods=["POST"])
def inference():
    if graph.get() == None:
        return jsonify({
            "status": "error",
            "message": "graph not initialize"
        })

    body = request.get_json()
    try:
        response = graph.call(f"ROLEPLAY\n{body['message']}", "roleplay")
        parsed = json.loads(response)
        return jsonify(parsed)
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": e
        })

def run():
    app.run(
        host="0.0.0.0",
        port="3000"
    )

threading.Thread(
    target=run,
    daemon=True,
).start()