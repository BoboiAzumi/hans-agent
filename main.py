import warnings
import threading
from dotenv import load_dotenv
from src.core.entrypoint import build_multi_agent

warnings.filterwarnings('ignore')

load_dotenv()

build_multi_agent()

try:
    threading.Event().wait()
except KeyboardInterrupt:
    print("\nShutting down...")