from datetime import datetime
from typing import List

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlmodel import Session, select

from .db import init_db, get_session
from .models import InferenceRequest, LayerAssignment, ModelRegistry, Node, Vote
from .schemas import (
    ActivateModelRequest,
    InferenceInput,
    InferenceStatus,
    LayerAssignmentResponse,
    ModelCreate,
    ModelResponse,
    NodeHeartbeat,
    NodeRegister,
    NodeResponse,
    PointsBalance,
    VoteRequest,
    VoteResultsResponse,
    VoteResult,
)
from .services import (
    accrue_daily_points,
    advance_period_if_needed,
    ensure_layer_file,
    ensure_state,
    points_balance,
    rebalance_layers,
    route_inference,
    select_active_model,
    select_monthly_model,
    set_active_model,
    vote_results,
)
from .settings import MVP_TIERS

app = FastAPI(title="Mesh AI Controller")


@app.on_event("startup")
def startup() -> None:
    init_db()
    with get_session() as session:
        ensure_state(session)
    scheduler = BackgroundScheduler(daemon=True)
    scheduler.add_job(lambda: _monthly_tick(), "interval", hours=1, id="monthly_tick")
    scheduler.add_job(lambda: _daily_points(), "cron", hour=0, minute=5, id="daily_points")
    scheduler.start()


def _monthly_tick() -> None:
    with get_session() as session:
        advance_period_if_needed(session)


def _daily_points() -> None:
    with get_session() as session:
        accrue_daily_points(session)


@app.post("/nodes/register", response_model=NodeResponse)
def register_node(payload: NodeRegister, session: Session = Depends(get_session)) -> NodeResponse:
    node = None
    if payload.node_id:
        node = session.get(Node, payload.node_id)
    if not node:
        node = Node(
            id=payload.node_id or None,
            host=payload.host,
            port=payload.port,
            ram_gb=payload.ram_gb,
            cpu_freq_ghz=payload.cpu_freq_ghz,
            gpu_vram_gb=payload.gpu_vram_gb,
            current_utilization=payload.current_utilization,
        )
    else:
        node.host = payload.host
        node.port = payload.port
        node.ram_gb = payload.ram_gb
        node.cpu_freq_ghz = payload.cpu_freq_ghz
        node.gpu_vram_gb = payload.gpu_vram_gb
        node.current_utilization = payload.current_utilization
        node.last_heartbeat = datetime.utcnow()
        node.status = "active"

    session.add(node)
    session.commit()
    session.refresh(node)

    model = select_active_model(session)
    if model:
        rebalance_layers(session, model)

    return NodeResponse(**node.model_dump())


@app.get("/nodes", response_model=List[NodeResponse])
def list_nodes(session: Session = Depends(get_session)) -> List[NodeResponse]:
    nodes = session.exec(select(Node)).all()
    return [NodeResponse(**node.model_dump()) for node in nodes]


@app.get("/nodes/{node_id}", response_model=NodeResponse)
def get_node(node_id: str, session: Session = Depends(get_session)) -> NodeResponse:
    node = session.get(Node, node_id)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    return NodeResponse(**node.model_dump())


@app.put("/nodes/{node_id}/heartbeat", response_model=NodeResponse)
def heartbeat(node_id: str, payload: NodeHeartbeat, session: Session = Depends(get_session)) -> NodeResponse:
    node = session.get(Node, node_id)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    node.current_utilization = payload.current_utilization
    node.last_heartbeat = datetime.utcnow()
    node.status = "active"
    session.add(node)
    session.commit()
    session.refresh(node)
    model = select_active_model(session)
    if model:
        rebalance_layers(session, model)
    return NodeResponse(**node.model_dump())


@app.delete("/nodes/{node_id}")
def deregister(node_id: str, session: Session = Depends(get_session)) -> dict:
    node = session.get(Node, node_id)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    node.status = "offline"
    session.add(node)
    session.commit()
    model = select_active_model(session)
    if model:
        rebalance_layers(session, model)
    return {"status": "offline"}


@app.post("/models", response_model=ModelResponse)
def create_model(payload: ModelCreate, session: Session = Depends(get_session)) -> ModelResponse:
    model = session.get(ModelRegistry, payload.id)
    if model:
        raise HTTPException(status_code=409, detail="Model already exists")
    model = ModelRegistry(**payload.model_dump())
    session.add(model)
    session.commit()
    session.refresh(model)
    return ModelResponse(**model.model_dump())


@app.get("/models", response_model=List[ModelResponse])
def list_models(session: Session = Depends(get_session)) -> List[ModelResponse]:
    models = session.exec(select(ModelRegistry)).all()
    return [ModelResponse(**model.model_dump()) for model in models]


@app.get("/models/{model_id}", response_model=ModelResponse)
def get_model(model_id: str, session: Session = Depends(get_session)) -> ModelResponse:
    model = session.get(ModelRegistry, model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    return ModelResponse(**model.model_dump())


@app.post("/models/activate", response_model=ModelResponse)
def activate_model(payload: ActivateModelRequest, session: Session = Depends(get_session)) -> ModelResponse:
    model = session.get(ModelRegistry, payload.model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    set_active_model(session, model)
    rebalance_layers(session, model)
    return ModelResponse(**model.model_dump())


@app.get("/models/{model_id}/layers/{layer_id}")
def stream_layer(model_id: str, layer_id: int) -> FileResponse:
    layer_path = ensure_layer_file(model_id, layer_id)
    return FileResponse(layer_path, filename=f"layer-{layer_id}.bin")


@app.post("/votes/{tier}")
def cast_vote(tier: str, payload: VoteRequest, session: Session = Depends(get_session)) -> dict:
    if tier not in MVP_TIERS:
        raise HTTPException(status_code=400, detail="Tier not enabled in MVP")
    vote = Vote(node_id=payload.node_id, tier=tier, model_choice=payload.model_choice, period=ensure_state(session).current_period)
    session.add(vote)
    session.commit()
    return {"status": "ok"}


@app.get("/votes/results", response_model=VoteResultsResponse)
def get_vote_results(session: Session = Depends(get_session)) -> VoteResultsResponse:
    period = ensure_state(session).current_period
    results = [VoteResult(tier=tier, model_id=model_id, votes=votes) for tier, model_id, votes in vote_results(session, period)]
    return VoteResultsResponse(period=period, results=results)


@app.post("/admin/rollover")
def rollover(session: Session = Depends(get_session)) -> dict:
    model = select_monthly_model(session)
    if model:
        set_active_model(session, model)
        rebalance_layers(session, model)
        return {"active_model": model.id}
    return {"active_model": None}


@app.get("/current-model", response_model=ModelResponse)
def current_model(session: Session = Depends(get_session)) -> ModelResponse:
    model = select_active_model(session)
    if not model:
        raise HTTPException(status_code=404, detail="No active model")
    return ModelResponse(**model.model_dump())


@app.get("/layers/{model_id}", response_model=List[LayerAssignmentResponse])
def get_assignments(model_id: str, session: Session = Depends(get_session)) -> List[LayerAssignmentResponse]:
    assignments = session.exec(select(LayerAssignment).where(LayerAssignment.model_id == model_id).order_by(LayerAssignment.start_layer)).all()
    return [LayerAssignmentResponse(node_id=a.node_id, start_layer=a.start_layer, end_layer=a.end_layer) for a in assignments]


@app.post("/layers/rebalance", response_model=List[LayerAssignmentResponse])
def rebalance(session: Session = Depends(get_session)) -> List[LayerAssignmentResponse]:
    model = select_active_model(session)
    if not model:
        raise HTTPException(status_code=404, detail="No active model")
    assignments = rebalance_layers(session, model)
    return [LayerAssignmentResponse(node_id=a.node_id, start_layer=a.start_layer, end_layer=a.end_layer) for a in assignments]


@app.post("/points/accrue")
def accrue_points(session: Session = Depends(get_session)) -> dict:
    total = accrue_daily_points(session)
    return {"awarded": total}


@app.get("/points/{node_id}/balance", response_model=PointsBalance)
def get_balance(node_id: str, session: Session = Depends(get_session)) -> PointsBalance:
    balance = points_balance(session, node_id)
    return PointsBalance(node_id=node_id, balance=balance)


@app.post("/infer", response_model=InferenceStatus)
def infer(payload: InferenceInput, session: Session = Depends(get_session)) -> InferenceStatus:
    request = route_inference(session, payload.prompt)
    return InferenceStatus(request_id=request.id, status=request.status, output=request.output, error=request.error)


@app.get("/infer/{request_id}", response_model=InferenceStatus)
def infer_status(request_id: str, session: Session = Depends(get_session)) -> InferenceStatus:
    request = session.get(InferenceRequest, request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    return InferenceStatus(request_id=request.id, status=request.status, output=request.output, error=request.error)
