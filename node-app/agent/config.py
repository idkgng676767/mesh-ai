import os
from pathlib import Path

CONTROLLER_URL = os.getenv("CONTROLLER_URL", "http://localhost:8000")
NODE_HOST = os.getenv("NODE_HOST", "localhost")
NODE_PORT = int(os.getenv("NODE_PORT", "9000"))
CACHE_DIR = Path(os.getenv("NODE_CACHE_DIR", Path(__file__).resolve().parents[1] / "cache"))
HEARTBEAT_INTERVAL_SEC = int(os.getenv("HEARTBEAT_INTERVAL_SEC", "20"))
