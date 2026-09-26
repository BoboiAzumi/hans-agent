# Hans Agent

Framework multi-agent berbasis plugin yang dibangun di atas LangGraph. Idenya sederhana: kalau kamu mau nambahin interface baru atau tool baru, cukup buat satu folder plugin tanpa harus ngutak-ngatik kode inti.

## Konsep

Arsitektur framework ini mirip seperti lego. Setiap blok berdiri sendiri, dan kamu tinggal pasang blok mana yang kamu butuhkan. Blok-blok itu disebut **plugin**.

Setiap plugin bisa berisi salah satu dari dua hal:

- **Interface** : antarmuka yang menghubungkan agent dengan dunia luar, misalnya chat UI atau bot Discord
- **Tool** : kemampuan yang bisa dipakai oleh agent untuk melakukan sesuatu, misalnya menyimpan atau mengambil memori

Satu plugin hanya boleh berisi satu interface atau satu tool. Tidak bisa keduanya sekaligus dalam jumlah lebih dari satu. Kalau sebuah plugin kebetulan berfungsi sebagai interface sekaligus tool (seperti plugin Discord yang punya bot sebagai interface sekaligus fungsi kirim pesan sebagai tool), itu masih dihitung satu plugin karena keduanya berkaitan erat dalam satu konteks yang sama.

## Struktur Plugin

Setiap plugin tinggal di dalam folder `plugins/<nama_plugin>/` dan minimal harus punya dua file:

```
plugins/
  nama_plugin/
    service.py   # logika utama plugin
    setup.py     # mendaftarkan plugin ke sistem
```

File `setup.py` adalah yang terpenting. Di situlah kamu mendeklarasikan apakah plugin ini membawa interface, tool, atau keduanya.

```python
# plugin yang hanya punya interface
plugin = {
    "interface": NamaClass
}

# plugin yang hanya punya tool
plugin = {
    "tool": nama_fungsi_tool
}

# plugin yang punya keduanya (seperti Discord)
plugin = {
    "interface": bot.graph_bind,
    "tool": tool_call
}
```

Sistem akan membaca semua plugin yang ada di folder `plugins/` secara otomatis, mengambil tools-nya, mengikatnya ke agent, lalu menginisialisasi interface-nya dengan graph yang sudah dikompilasi.

### Plugin bawaan yang tersedia
| Nama plugin | Fungsi |
| --------- | --------- |
| **gradio** | membuka chat UI berbasis web menggunakan Gradio. Agent langsung bisa diakses lewat browser.|
| **discord** | menjalankan bot Discord yang mendengarkan pesan di server. Selain sebagai interface, plugin ini juga menyediakan tool untuk mengirim pesan ke channel Discord dari agent. |
| **library** | tool memori jangka panjang menggunakan Milvus. Agent bisa menyimpan, mencari, dan menghapus informasi. Pencarian dilakukan dengan hybrid search (dense vector + BM25) |
| **weather** | tool untuk cek cuaca saat ini di sebuah kota |
| **roleplay_api** | membangun rest API untuk kebutuhan chat roleplay seperti ryza (future project) |

---

## Mode Operasi

### Single Agent

Kalau kamu tidak membutuhkan sub-agent, cukup kosongkan `SUB_AGENT` di `config/sub_agent_config.py`:

```python
SUB_AGENT = []
```

Dalam mode ini, supervisor akan menangani semua permintaan sendiri tanpa mendelegasikan ke siapapun.

### Multi Agent

Isi `SUB_AGENT` dengan daftar agent yang ingin kamu jalankan:

```python
SUB_AGENT = [
    {
        "model": "gemma-4-26b-a4b-it",
        "provider": "google-gen-ai",
        "key": os.getenv("GOOGLE_API_KEY"),
        "base_url": "",
        "system_prompt": "Kamu adalah karakter cewe anime yang selalu menjawab dengan nada tsundere, keahlianmu adalah ngoding",
        "description": "Agent tsundere namun jago ngoding",
        "tools": ["library"]
    },
]
```

Penjelasan tiap field:

| Field | Keterangan |
|---|---|
| `model` | Nama model yang digunakan |
| `provider` | Provider LLM (saat ini mendukung `google-gen-ai`, `nvidia`, `openrouter`, `openai`, `custom`) |
| `key` | API key, ambil dari environment variable |
| `base_url` | Base URL custom jika diperlukan, kosongkan jika tidak |
| `system_prompt` | Kepribadian dan instruksi khusus untuk agent ini |
| `description` | Deskripsi singkat yang akan dibaca supervisor untuk memilih agent yang tepat |
| `tools` | Daftar nama plugin tool yang bisa dipakai agent ini |

Field `tools` berisi nama folder plugin, bukan nama file. Kalau plugin-nya ada di `plugins/library`, maka isi `"library"`. Kalau plugin-nya ada di `plugins/discord`, isi `"discord"`.

Dalam mode multi-agent, ada satu supervisor yang bertugas memutuskan tiga hal untuk setiap pesan yang masuk:

- **answer** : supervisor jawab sendiri
- **delegate** : supervisor sepenuhnya menyerahkan tugas ke sub-agent tertentu
- **consult** : supervisor minta masukan dari sub-agent, tapi menyusun jawaban akhir sendiri

---

## Konfigurasi

### Supervisor (`config/supervisor_agent_config.py`)

```python
SUPERVISOR = {
    "model": "gemini-3.5-flash-lite",
    "provider": "google-gen-ai",
    "key": os.getenv("GOOGLE_API_KEY"),
    "base_url": "",
    "max_hop": 10
}
```

`max_hop` adalah batas maksimal berapa kali supervisor bisa memanggil agent atau tool dalam satu sesi sebelum dipaksa berhenti.

### System Prompt Supervisor (`config/base_prompt_config.py`)

File ini berisi instruksi yang diberikan ke supervisor setiap sesi dimulai. Di sinilah kamu bisa mengatur perilaku supervisor: kapan harus delegate, kapan consult, kapan jawab sendiri, dan aturan-aturan khusus lainnya.

### Summarization (`config/summerization_config.py`)

```python
MAX_TOKEN = 15000
KEEP_TOKEN = 7000
```

Karena percakapan bisa terus berlanjut dan riwayat pesan bisa sangat panjang, ada mekanisme summarization otomatis. Kalau total token dalam riwayat melebihi `MAX_TOKEN`, sistem akan meringkas riwayat tersebut sampai kira-kira `KEEP_TOKEN` token. Ini mencegah context window meledak di tengah percakapan yang panjang.

---

## Instalasi

Salin file environment dan isi dengan API key yang kamu punya:

```bash
cp .env.example .env
```

```
GOOGLE_API_KEY="TOKEN"
NVIDIA_API_KEY="TOKEN"
DISCORD_KEY="TOKEN"
OPENROUTER_API_KEY="TOKEN"
OPENAI_API_KEY="TOKEN"
```

Tidak semua key harus diisi, sesuaikan dengan provider dan plugin yang kamu pakai.

### Custom Provider

Kalau kamu mau pakai provider lain tanpa mengubah kode, gunakan `"provider": "custom"` di config lalu atur semuanya lewat `.env`:

```
CUSTOM_API_TYPE="anthropic"   # "anthropic" atau "openai", default "openai"
CUSTOM_MODEL="claude-sonnet-4-6"
CUSTOM_API_KEY="TOKEN"
CUSTOM_BASE_URL="https://api.anthropic.com"
CUSTOM_MAX_TOKENS="8000"
CUSTOM_TIMEOUT="6000"
```

`CUSTOM_API_TYPE="anthropic"` memakai format Messages API Anthropic, jadi endpoint apa pun yang Anthropic-compatible (misalnya proxy atau gateway) bisa dipakai cukup dengan mengubah `CUSTOM_BASE_URL`. Untuk endpoint OpenAI-compatible, pakai `CUSTOM_API_TYPE="openai"`. Field `model`, `key`, dan `base_url` di config akan menimpa nilai `.env` jika diisi.

Install dependencies lalu jalankan:

```bash
pip install -r requirements.txt
python main.py
```

---

## Membuat Plugin Baru

Buat folder baru di `plugins/`, isi dengan `service.py` dan `setup.py`.

Contoh plugin tool sederhana:

```python
# plugins/kalkulator/service.py
from langchain_core.tools import tool

@tool
def tool_call(expression: str) -> str:
    """
    Hitung ekspresi matematika sederhana.
    arguments:
        expression: ekspresi seperti "2 + 2" atau "10 * 5"
    """
    try:
        return str(eval(expression))
    except Exception as e:
        return f"Error: {e}"
```

```python
# plugins/kalkulator/setup.py
from plugins.kalkulator.service import tool_call

plugin = {
    "tool": tool_call
}
```

Setelah itu, plugin langsung bisa dipakai oleh sub-agent dengan menambahkan `"kalkulator"` ke field `tools` di konfigurasi sub-agent.

Untuk plugin interface, class-nya perlu menerima `graph` sebagai argumen pertama di constructor karena sistem akan mengoper compiled graph ke sana saat startup.

