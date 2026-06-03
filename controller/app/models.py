from datetime import datetime, date
from typing import Optional
from uuid import uuid4

from sqlmodel import SQLModel, Field


def utc_now() -> datetime:
    return datetime.utcnow()


class Node(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    host: str
    port: int
    ram_gb: float
    cpu_freq_ghz: float
    gpu_vram_gb: float = 0.0
    current_utilization: float = 1.0
    status: str = "active"
    created_at: datetime = Field(default_factory=utc_now)
    last_heartbeat: datetime = Field(default_factory=utc_now)


class ModelRegistry(SQLModel, table=True):
    id: str = Field(primary_key=True)
    tier: str
    parameters: int
    size_gb: float
    layers: int
    url: str
    created_at: datetime = Field(default_factory=utc_now)
    is_active: bool = False


class Vote(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    node_id: str
    tier: str
    model_choice: str
    period: str
    created_at: datetime = Field(default_factory=utc_now)


class LayerAssignment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    model_id: str
    node_id: str
    start_layer: int
    end_layer: int
    updated_at: datetime = Field(default_factory=utc_now)


class PointsLedger(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    node_id: str
    points: int
    reason: str
    created_at: datetime = Field(default_factory=utc_now)


class InferenceRequest(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    prompt: str
    status: str = "queued"
    model_id: Optional[str] = None
    output: Optional[str] = None
    error: Optional[str] = None
    created_at: datetime = Field(default_factory=utc_now)
    completed_at: Optional[datetime] = None


class SystemState(SQLModel, table=True):
    id: int = Field(default=1, primary_key=True)
    current_period: str
    active_model_id: Optional[str] = None
    last_points_accrual: Optional[date] = None
