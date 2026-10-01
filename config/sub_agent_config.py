import os
from config.crypto_agent_config import CRYPTO_AGENT_PROMPT

SUB_AGENT = [
    {
        "model": "gemma-4-31b-it",
        "provider": "google-gen-ai",
        "key": os.getenv("GOOGLE_API_KEY"),
        "base_url": "",
        "system_prompt": "Kamu adalah agent bawahan bernama gemma 4, kamu harus menjawab setiap pertanyaan delegate dari supervisor dengan bahasa yang lebih sederhana seperti anak SD",
        "description": "Agent yang selalu menjawab apa adanya dengan bahasa sederhana yang mudah dimengerti",
        "tools": ["library"]
    },
    {
        "model": "gemma-4-26b-a4b-it",
        "provider": "google-gen-ai",
        "key": os.getenv("GOOGLE_API_KEY"),
        "base_url": "",
        "system_prompt": "Kamu adalah agent bawahan bernama gemma 4 26b, kamu adalah karakter cewe anime yang selalu menjawab dengan nada tsundere, keahlianmu adalah ngoding",
        "description": "Agent tsundere namun jago ngoding",
        "tools": ["library"]
    },
    {
        "model": "nvidia/nemotron-3-ultra-550b-a55b",
        "provider": "nvidia",
        "key": os.getenv("NVIDIA_API_KEY"),
        "base_url": "",
        "system_prompt": "Kamu adalah agent yang punya karakter dingin, hemat bicara, dan efisien",
        "description": "Agent yang punya karakteristik dingin",
        "tools": ["library"]
    },
    {
        "model": "gemini-3.6-flash",
        "provider": "google-gen-ai",
        "key": os.getenv("GOOGLE_API_KEY"),
        "base_url": "",
        "system_prompt": CRYPTO_AGENT_PROMPT,
        "description": "Crypto Agent Analysis yang bekerja pada pukul 00:00 - 11:00, periode 4 jam sekali",
        "tools": ["crypto", "news"]
    },
    {
        "model": "gemini-3.7-flash",
        "provider": "google-gen-ai",
        "key": os.getenv("GOOGLE_API_KEY"),
        "base_url": "",
        "system_prompt": CRYPTO_AGENT_PROMPT,
        "description": "Crypto Agent Analysis yang bekerja pada pukul 12:00 - 23:00, periode 4 jam sekali",
        "tools": ["crypto", "news"]
    },
    {
        "model": "gemini-3.8-flash",
        "provider": "google-gen-ai",
        "key": os.getenv("GOOGLE_API_KEY"),
        "base_url": "",
        "system_prompt": CRYPTO_AGENT_PROMPT,
        "description": "Crypto Agent Analysis yang bekerja setiap pukul 08:00 setiap hari",
        "tools": ["crypto", "news"]
    },
]
