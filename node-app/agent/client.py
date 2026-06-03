from __future__ import annotations

from typing import List, Optional

import httpx

from .config import CACHE_DIR, CONTROLLER_URL


async def register_node(client: httpx.AsyncClient, payload: dict) -> dict:
    response = await client.post(f"{CONTROLLER_URL}/nodes/register", json=payload)
    response.raise_for_status()
    return response.json()


async def send_heartbeat(client: httpx.AsyncClient, node_id: str, utilization: float) -> dict:
    response = await client.put(
        f"{CONTROLLER_URL}/nodes/{node_id}/heartbeat",
        json={"current_utilization": utilization},
    )
    response.raise_for_status()
    return response.json()


async def get_current_model(client: httpx.AsyncClient) -> Optional[dict]:
    response = await client.get(f"{CONTROLLER_URL}/current-model")
    if response.status_code == 404:
        return None
    response.raise_for_status()
    return response.json()


async def get_assignments(client: httpx.AsyncClient, model_id: str) -> List[dict]:
    response = await client.get(f"{CONTROLLER_URL}/layers/{model_id}")
    response.raise_for_status()
    return response.json()


async def download_layer(client: httpx.AsyncClient, model_id: str, layer_id: int) -> str:
    layer_path = CACHE_DIR / model_id / f"layer-{layer_id}.bin"
    layer_path.parent.mkdir(parents=True, exist_ok=True)
    if layer_path.exists():
        return str(layer_path)
    response = await client.get(f"{CONTROLLER_URL}/models/{model_id}/layers/{layer_id}")
    response.raise_for_status()
    layer_path.write_bytes(response.content)
    return str(layer_path)
