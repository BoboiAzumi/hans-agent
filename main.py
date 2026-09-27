import warnings
import threading
from dotenv import load_dotenv
from src.core.entrypoint import build_multi_agent

warnings.filterwarnings('ignore')

load_dotenv()

build_multi_agent()

stop_event = threading.Event()
try:
    while not stop_event.wait(timeout=1.0):
        pass
except KeyboardInterrupt:
    print("\nShutting down...")