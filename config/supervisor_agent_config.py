import os

SUPERVISOR = {
    "model": "gemini-3.1-flash-lite",
    "provider": "google-gen-ai",
    "key": os.getenv("GOOGLE_API_KEY"),
    "base_url": "",
    "max_hop": 10
}