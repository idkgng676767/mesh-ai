from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Optional

import httpx
from fastapi import FastAPI
from pydantic import BaseModel

from .client import download_layer, get_assignments, get_current_model, register_node, send_heartbeat
from .config import HEARTBEAT_INTERVAL_SEC, NODE_HOST, NODE_PORT
from .inference import process_layers
from .monitor import get_cpu_freq_ghz, get_gpu_vram_gb, get_ram_gb, get_utilization_multiplier

app = FastAPI(title="Mesh AI Node")


class NodeInferenceRequest(BaseModel):
    prompt: str
    hidden_state: Optional[str] = None
    start_layer: int
    end_layer: int


class NodeInferenceResponse(BaseModel):
    hidden_state: str
    output: Optional[str] = None


@dataclass
class NodeRuntime:
    node_id: Optional[str] = None
    model_id: Optional[str] = None
    assignments: list[dict] = field(default_factory=list)
    client: Optional[httpx.AsyncClient] = None


runtime = NodeRuntime()


async def _update_assignments(client: httpx.AsyncClient) -> None:
    model = await get_current_model(client)
    if not model:
        runtime.model_id = None
        runtime.assignments = []
        return
    runtime.model_id = model["id"]
    assignments = await get_assignments(client, runtime.model_id)
    runtime.assignments = assignments
    for assignment in assignments:
        for layer_id in range(assignment["start_layer"], assignment["end_layer"] + 1):
            await download_layer(client, runtime.model_id, layer_id)


async def _heartbeat_loop(client: httpx.AsyncClient) -> None:
    while True:
        if not runtime.node_id:
            await asyncio.sleep(HEARTBEAT_INTERVAL_SEC)
            continue
        utilization = get_utilization_multiplier()
        await send_heartbeat(client, runtime.node_id, utilization)
        await _update_assignments(client)
        await asyncio.sleep(HEARTBEAT_INTERVAL_SEC)


@app.on_event("startup")
async def startup() -> None:
    runtime.client = httpx.AsyncClient()
    payload = {
        "host": NODE_HOST,
        "port": NODE_PORT,
        "ram_gb": get_ram_gb(),
        "cpu_freq_ghz": get_cpu_freq_ghz(),
        "gpu_vram_gb": get_gpu_vram_gb(),
        "current_utilization": get_utilization_multiplier(),
    }
    response = await register_node(runtime.client, payload)
    runtime.node_id = response["id"]
    await _update_assignments(runtime.client)
    asyncio.create_task(_heartbeat_loop(runtime.client))


@app.on_event("shutdown")
async def shutdown() -> None:
    if runtime.client:
        await runtime.client.aclose()


@app.post("/infer", response_model=NodeInferenceResponse)
async def infer(payload: NodeInferenceRequest) -> NodeInferenceResponse:
    if not runtime.model_id:
        return NodeInferenceResponse(hidden_state=payload.hidden_state or "", output="no model")
    if not runtime.client:
        runtime.client = httpx.AsyncClient()
    new_state = await process_layers(runtime.model_id, payload.start_layer, payload.end_layer, payload.hidden_state, runtime.client)
    output = None
    if runtime.assignments:
        final_layer = max(a["end_layer"] for a in runtime.assignments)
        if payload.end_layer == final_layer:
            output = f"Answer for '{payload.prompt}'"
    return NodeInferenceResponse(hidden_state=new_state, output=output)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=NODE_PORT)
