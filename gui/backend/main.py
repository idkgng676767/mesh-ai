from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .controller_client import get_current_model, get_nodes, get_points_balance, submit_inference

app = FastAPI(title="Mesh AI GUI Backend")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TOKENS: dict[str, str] = {}


class LoginRequest(BaseModel):
    username: str


class LoginResponse(BaseModel):
    token: str
    issued_at: datetime


class InferenceRequest(BaseModel):
    prompt: str


async def _require_token(authorization: str | None) -> str:
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing token")
    token = authorization.replace("Bearer ", "")
    if token not in TOKENS:
        raise HTTPException(status_code=401, detail="Invalid token")
    return token


@app.post("/auth/login", response_model=LoginResponse)
async def login(payload: LoginRequest) -> LoginResponse:
    token = str(uuid4())
    TOKENS[token] = payload.username
    return LoginResponse(token=token, issued_at=datetime.utcnow())


@app.get("/status")
async def status(authorization: str | None = Header(default=None)) -> dict:
    await _require_token(authorization)
    nodes = await get_nodes()
    total_capacity = sum(node["ram_gb"] * node["current_utilization"] for node in nodes)
    return {
        "nodes": len(nodes),
        "total_capacity_gb": round(total_capacity, 2),
    }


@app.get("/models/current")
async def current_model(authorization: str | None = Header(default=None)) -> dict:
    await _require_token(authorization)
    model = await get_current_model()
    if not model:
        raise HTTPException(status_code=404, detail="No active model")
    return model


@app.get("/points/{node_id}")
async def points(node_id: str, authorization: str | None = Header(default=None)) -> dict:
    await _require_token(authorization)
    return await get_points_balance(node_id)


@app.post("/infer")
async def infer(payload: InferenceRequest, authorization: str | None = Header(default=None)) -> dict:
    await _require_token(authorization)
    return await submit_inference(payload.prompt)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=7000)
