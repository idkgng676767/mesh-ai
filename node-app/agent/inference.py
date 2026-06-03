from __future__ import annotations

from datetime import datetime
from typing import Optional

from .client import download_layer
from .config import CACHE_DIR


async def process_layers(model_id: str, start_layer: int, end_layer: int, hidden_state: Optional[str], client) -> str:
    state = hidden_state or ""
    processed = []
    for layer_id in range(start_layer, end_layer + 1):
        layer_path = CACHE_DIR / model_id / f"layer-{layer_id}.bin"
        if not layer_path.exists():
            await download_layer(client, model_id, layer_id)
        processed.append(f"L{layer_id}")
    timestamp = datetime.utcnow().isoformat()
    return f"{state}|processed:{','.join(processed)}@{timestamp}"
