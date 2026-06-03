#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../gui/backend"
python -m pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port ${GUI_BACKEND_PORT:-7000}
