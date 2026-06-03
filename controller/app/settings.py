from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parents[1]
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'mesh_ai.db'}")
STORAGE_DIR = Path(os.getenv("MODEL_STORAGE_DIR", BASE_DIR / "storage"))

MVP_TIERS = ["8b", "24b", "72b"]
TIER_ORDER = ["8b", "24b", "72b", "144b", "frontier"]

DEFAULT_NODE_TIMEOUT_SEC = int(os.getenv("NODE_TIMEOUT_SEC", "10"))
DEFAULT_NODE_RETRIES = int(os.getenv("NODE_RETRIES", "2"))
