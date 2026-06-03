from __future__ import annotations

from typing import Any

import httpx

from .config import CONTROLLER_URL


async def get_nodes() -> list[dict[str, Any]]:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{CONTROLLER_URL}/nodes")
        response.raise_for_status()
        return response.json()


async def get_current_model() -> dict[str, Any] | None:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{CONTROLLER_URL}/current-model")
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json()


async def get_points_balance(node_id: str) -> dict[str, Any]:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{CONTROLLER_URL}/points/{node_id}/balance")
        response.raise_for_status()
        return response.json()


async def submit_inference(prompt: str) -> dict[str, Any]:
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{CONTROLLER_URL}/infer", json={"prompt": prompt})
        response.raise_for_status()
        return response.json()
