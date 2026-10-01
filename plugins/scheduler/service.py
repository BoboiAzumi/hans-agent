from apscheduler.schedulers.background import BackgroundScheduler
from langchain_core.tools import tool

class Scheduler():
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()

    def graph_bind(self, graph):
        self.graph = graph
        return self

    def run_job(self, prompt):
        try:
            self.graph.invoke({
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            })
        except Exception as e:
            print(f"Error scheduler: {str(e)}")

    def tool_call(self, prompt, hour, minute, id):
        self.scheduler.add_job(
            self.run_job,
            "cron",
            hour=hour,
            minute=minute,
            args=[prompt],
            id=id
        )

    def remove(self, ids):
        self.scheduler.remove_job(ids)

scheduler = Scheduler()

@tool
def tool_call(action, prompt, hour, minute, ids):
    """
    Tool untuk membuat penjadwalan (cron).

    Arguments:
        action: hanya bisa berisi add dan remove, add kalau mau tambah jadwal baru, remove kalau mau hapus jadwal
        prompt: Prompt yang akan dijalankan secara otomatis sesuai jadwal.
        hour: Jam ketika prompt akan dijalankan. Gunakan format 0-23.
        minute: Menit ketika prompt akan dijalankan. Gunakan format 0-59.
        id: ID unik untuk penjadwalan. ID ini PENTING dan harus selalu
            dicatat di memory jangka panjang agar penjadwalan dapat
            dikelola atau dihapus kembali.

    Contoh:
        hour=8, minute=30
        Prompt dijalankan setiap hari pada pukul 08:30.

        jika action adalah remove, maka hour dan minute isi 0 saja
    """
    print(f"{action} {hour} {minute} {ids}\nPrompt: {prompt}")
    try:
        if action == "remove":
            scheduler.remove(ids)
            return
        else:
            scheduler.tool_call(prompt, hour, minute, ids)
            return
    except Exception as e:
        print(e)
        return e