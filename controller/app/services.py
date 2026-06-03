from collections import Counter
from datetime import date, datetime
from typing import List, Optional, Tuple

import httpx
from sqlmodel import Session, select, delete

from .models import LayerAssignment, ModelRegistry, Node, PointsLedger, SystemState, Vote, InferenceRequest
from .settings import STORAGE_DIR, TIER_ORDER, MVP_TIERS, DEFAULT_NODE_TIMEOUT_SEC, DEFAULT_NODE_RETRIES


def current_period() -> str:
    now = datetime.utcnow()
    return f"{now.year:04d}-{now.month:02d}"


def ensure_state(session: Session) -> SystemState:
    state = session.get(SystemState, 1)
    if not state:
        state = SystemState(id=1, current_period=current_period())
        session.add(state)
        session.commit()
        session.refresh(state)
    return state


def total_capacity(nodes: List[Node]) -> float:
    return sum(node.ram_gb * node.current_utilization for node in nodes)


def select_active_model(session: Session) -> Optional[ModelRegistry]:
    state = ensure_state(session)
    if state.active_model_id:
        model = session.get(ModelRegistry, state.active_model_id)
        if model:
            return model
    return session.exec(select(ModelRegistry).where(ModelRegistry.is_active == True)).first()


def set_active_model(session: Session, model: ModelRegistry) -> None:
    session.exec(select(ModelRegistry)).all()
    for existing in session.exec(select(ModelRegistry)).all():
        existing.is_active = existing.id == model.id
        session.add(existing)
    state = ensure_state(session)
    state.active_model_id = model.id
    session.add(state)
    session.commit()


def rebalance_layers(session: Session, model: ModelRegistry) -> List[LayerAssignment]:
    nodes = session.exec(select(Node).where(Node.status == "active")).all()
    if not nodes:
        session.exec(delete(LayerAssignment).where(LayerAssignment.model_id == model.id))
        session.commit()
        return []

    capacity = total_capacity(nodes)
    if capacity <= 0:
        return []

    layers_per_gb = model.layers / capacity
    sorted_nodes = sorted(nodes, key=lambda n: n.ram_gb * n.current_utilization, reverse=True)

    session.exec(delete(LayerAssignment).where(LayerAssignment.model_id == model.id))
    assignments: List[LayerAssignment] = []
    current_layer = 1

    for node in sorted_nodes:
        node_capacity = max(node.ram_gb * node.current_utilization, 0)
        estimated_layers = max(int(round(node_capacity * layers_per_gb)), 1)
        start_layer = current_layer
        end_layer = min(model.layers, start_layer + estimated_layers - 1)
        if start_layer > model.layers:
            break
        assignment = LayerAssignment(
            model_id=model.id,
            node_id=node.id,
            start_layer=start_layer,
            end_layer=end_layer,
        )
        assignments.append(assignment)
        current_layer = end_layer + 1

    if assignments and current_layer <= model.layers:
        assignments[-1].end_layer = model.layers

    for assignment in assignments:
        session.add(assignment)
    session.commit()
    return assignments


def vote_results(session: Session, period: str) -> List[Tuple[str, str, int]]:
    votes = session.exec(select(Vote).where(Vote.period == period)).all()
    grouped: dict[str, Counter] = {}
    for vote in votes:
        grouped.setdefault(vote.tier, Counter())
        grouped[vote.tier][vote.model_choice] += 1
    results: List[Tuple[str, str, int]] = []
    for tier, counter in grouped.items():
        model_choice, count = counter.most_common(1)[0]
        results.append((tier, model_choice, count))
    return results


def select_monthly_model(session: Session) -> Optional[ModelRegistry]:
    state = ensure_state(session)
    period = state.current_period
    results = vote_results(session, period)
    if not results:
        return None

    nodes = session.exec(select(Node).where(Node.status == "active")).all()
    capacity = total_capacity(nodes)

    tier_map = {tier: model_id for tier, model_id, _ in results}

    for tier in reversed([t for t in TIER_ORDER if t in MVP_TIERS]):
        model_id = tier_map.get(tier)
        if not model_id:
            continue
        model = session.get(ModelRegistry, model_id)
        if model and model.size_gb <= capacity:
            return model
    return None


def advance_period_if_needed(session: Session) -> Optional[ModelRegistry]:
    state = ensure_state(session)
    now_period = current_period()
    if state.current_period != now_period:
        state.current_period = now_period
        session.add(state)
        session.commit()
        model = select_monthly_model(session)
        if model:
            set_active_model(session, model)
            rebalance_layers(session, model)
            return model
    return None


def accrue_daily_points(session: Session) -> int:
    state = ensure_state(session)
    today = date.today()
    if state.last_points_accrual == today:
        return 0

    nodes = session.exec(select(Node).where(Node.status == "active")).all()
    total_awarded = 0
    for node in nodes:
        points = int(round(node.ram_gb * node.cpu_freq_ghz * 100 * node.current_utilization))
        ledger = PointsLedger(node_id=node.id, points=points, reason="daily_accrual")
        session.add(ledger)
        total_awarded += points
    state.last_points_accrual = today
    session.add(state)
    session.commit()
    return total_awarded


def points_balance(session: Session, node_id: str) -> int:
    rows = session.exec(select(PointsLedger).where(PointsLedger.node_id == node_id)).all()
    return sum(row.points for row in rows)


def ensure_layer_file(model_id: str, layer_id: int) -> str:
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    layer_path = STORAGE_DIR / model_id / f"layer-{layer_id}.bin"
    layer_path.parent.mkdir(parents=True, exist_ok=True)
    if not layer_path.exists():
        content = f"model={model_id};layer={layer_id};generated={datetime.utcnow().isoformat()}".encode("utf-8")
        layer_path.write_bytes(content)
    return str(layer_path)


def route_inference(session: Session, prompt: str) -> InferenceRequest:
    request = InferenceRequest(prompt=prompt, status="running")
    session.add(request)
    session.commit()
    session.refresh(request)

    model = select_active_model(session)
    if not model:
        request.status = "failed"
        request.error = "No active model"
        session.add(request)
        session.commit()
        return request

    request.model_id = model.id
    session.add(request)
    session.commit()

    assignments = session.exec(
        select(LayerAssignment).where(LayerAssignment.model_id == model.id).order_by(LayerAssignment.start_layer)
    ).all()

    if not assignments:
        request.status = "failed"
        request.error = "No layer assignments"
        session.add(request)
        session.commit()
        return request

    hidden_state: Optional[str] = None
    output: Optional[str] = None

    for assignment in assignments:
        node = session.get(Node, assignment.node_id)
        if not node:
            continue
        url = f"http://{node.host}:{node.port}/infer"
        payload = {
            "prompt": prompt,
            "hidden_state": hidden_state,
            "start_layer": assignment.start_layer,
            "end_layer": assignment.end_layer,
        }
        attempts = 0
        while attempts <= DEFAULT_NODE_RETRIES:
            try:
                with httpx.Client(timeout=DEFAULT_NODE_TIMEOUT_SEC) as client:
                    response = client.post(url, json=payload)
                    response.raise_for_status()
                    data = response.json()
                    hidden_state = data.get("hidden_state")
                    output = data.get("output")
                    break
            except Exception as exc:  # noqa: BLE001
                attempts += 1
                if attempts > DEFAULT_NODE_RETRIES:
                    request.status = "failed"
                    request.error = f"Node {node.id} failed: {exc}"
                    session.add(request)
                    session.commit()
                    return request

    request.status = "completed"
    request.output = output or hidden_state or ""
    request.completed_at = datetime.utcnow()
    session.add(request)
    session.commit()
    return request
