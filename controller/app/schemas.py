from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field


class NodeRegister(BaseModel):
    host: str
    port: int
    ram_gb: float
    cpu_freq_ghz: float
    gpu_vram_gb: float = 0.0
    current_utilization: float = 1.0
    node_id: Optional[str] = None


class NodeHeartbeat(BaseModel):
    current_utilization: float


class NodeResponse(BaseModel):
    id: str
    host: str
    port: int
    ram_gb: float
    cpu_freq_ghz: float
    gpu_vram_gb: float
    current_utilization: float
    status: str
    last_heartbeat: datetime


class VoteRequest(BaseModel):
    node_id: str
    model_choice: str


class ModelCreate(BaseModel):
    id: str = Field(..., description="model id")
    tier: str
    parameters: int
    size_gb: float
    layers: int
    url: str


class ActivateModelRequest(BaseModel):
    model_id: str


class LayerAssignmentResponse(BaseModel):
    node_id: str
    start_layer: int
    end_layer: int


class InferenceInput(BaseModel):
    prompt: str


class InferenceStatus(BaseModel):
    request_id: str
    status: str
    output: Optional[str] = None
    error: Optional[str] = None


class NodeInferenceRequest(BaseModel):
    prompt: str
    hidden_state: Optional[str] = None
    start_layer: int
    end_layer: int


class NodeInferenceResponse(BaseModel):
    hidden_state: str
    output: Optional[str] = None


class PointsBalance(BaseModel):
    node_id: str
    balance: int


class VoteResult(BaseModel):
    tier: str
    model_id: str
    votes: int


class ModelResponse(BaseModel):
    id: str
    tier: str
    parameters: int
    size_gb: float
    layers: int
    url: str
    is_active: bool


class VoteResultsResponse(BaseModel):
    period: str
    results: List[VoteResult]
