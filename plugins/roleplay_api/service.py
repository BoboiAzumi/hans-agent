from plugins.roleplay_api.config import TTS, MAX_BATCH_TTS, REF_AUDIO, REF_TEXT
if TTS:
    import time
    import uuid
    import torch
    import gc
    from qwen_tts import Qwen3TTSModel
    from flask import send_file
    from pathlib import Path
    import soundfile as sf

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
if TTS:
    tts = Qwen3TTSModel.from_pretrained(
        "Qwen/Qwen3-TTS-12Hz-0.6B-Base",
        device_map="cuda:0",
        dtype=torch.bfloat16,
    )

    TEMP_DIR = Path("assets/temp_audio")
    AUDIO_DIR = Path("assets/audio")
    TEMP_DIR.mkdir(exist_ok=True)
    AUDIO_DIR.mkdir(exist_ok=True)
    RETENTION_SECONDS = 30 * 60

    def cleanup_worker():
        while True:
            now = time.time()
            for file in TEMP_DIR.iterdir():
                if not file.is_file():
                    continue
                try:
                    age = now - file.stat().st_mtime
                    if age > RETENTION_SECONDS:
                        file.unlink()
                        print(f"Deleted: {file}")

                except Exception as e:
                    print(f"Cleanup error: {file}: {e}")

            time.sleep(60)

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

        if TTS:
            items = list(enumerate(parsed))
            for batch_start in range(0, len(items), MAX_BATCH_TTS):
                batch = items[batch_start : batch_start + MAX_BATCH_TTS]
                texts = [parsed[i]["response_jp"] for i, _ in batch]
                file_ids = [uuid.uuid4().hex for _ in batch]

                batch_wavs, sample_rate = tts.generate_voice_clone(
                    text=texts,
                    language="Auto",
                    ref_audio=f"{AUDIO_DIR}/{REF_AUDIO}",
                    ref_text=REF_TEXT,
                    x_vector_only_mode=False,
                )

                gc.collect()
                torch.cuda.empty_cache()

                for (i, _), file_id, wav in zip(batch, file_ids, batch_wavs):
                    output_path = TEMP_DIR / f"{file_id}_output.wav"
                    sf.write(output_path, wav, sample_rate)
                    parsed[i]["audio"] = f"/audio/{file_id}_output.wav"
        
        return jsonify(parsed)
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": e
        })

if TTS:
    @app.get("/audio/<file_id>.wav")
    def get_audio(file_id):
        path = TEMP_DIR / f"{file_id}.wav"

        print(path)

        if not path.exists():
            return jsonify({
                "error": "audio not found or expired"
            }), 404

        return send_file(
            path,
            mimetype="audio/wav",
        )

def run():
    app.run(
        host="0.0.0.0",
        port="3000"
    )

threading.Thread(
    target=run,
    daemon=True,
).start()

if TTS:
    threading.Thread(
        target=cleanup_worker,
        daemon=True
    ).start()