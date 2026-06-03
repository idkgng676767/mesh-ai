#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../controller"
python -m pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
