import os

CONTROLLER_URL = os.getenv("CONTROLLER_URL", "http://localhost:8000")
GUI_BACKEND_PORT = int(os.getenv("GUI_BACKEND_PORT", "7000"))
