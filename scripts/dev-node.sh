#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../node-app"
python -m pip install -r requirements.txt
CONTROLLER_URL=${CONTROLLER_URL:-"http://localhost:8000"} \
NODE_HOST=${NODE_HOST:-"localhost"} \
NODE_PORT=${NODE_PORT:-"9000"} \
uvicorn agent.main:app --reload --host 0.0.0.0 --port ${NODE_PORT:-9000}
