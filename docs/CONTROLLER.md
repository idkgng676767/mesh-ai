# Controller Server Architecture

## Overview

The central orchestration server manages:
- Node registration & health monitoring
- Model storage & distribution
- Monthly voting system
- Layer-to-node assignment
- Inference request routing
- Rebalancing logic

## Key Endpoints

### Node Management
- `POST /nodes/register` - Register a new node
- `GET /nodes/{id}` - Get node status
- `PUT /nodes/{id}/heartbeat` - Heartbeat ping
- `DELETE /nodes/{id}` - Deregister node

### Model Registry
- `POST /models` - Register a model
- `GET /models` - List models
- `GET /models/{id}` - Model details
- `POST /models/activate` - Activate a model for the current period
- `GET /models/{model_id}/layers/{layer_id}` - Stream a model layer

### Voting & Model Selection
- `POST /votes/{tier}` - Cast vote for model in tier
- `GET /votes/results` - Current voting results
- `GET /current-model` - Active model for this month
 - `POST /admin/rollover` - Force monthly selection (MVP)

### Inference
- `POST /infer` - Submit inference request
- `GET /infer/{request_id}` - Get inference status

### Layer Management
- `GET /layers/{model_id}` - Get layer assignments
- `POST /layers/rebalance` - Trigger rebalancing

### Points
- `GET /points/{node_id}/balance` - Points balance
- `POST /points/accrue` - Manual daily accrual (MVP)

## Data Models

### Node
```
{
  "id": "node-1",
  "ip": "192.168.1.100",
  "port": 5000,
  "ram_gb": 8,
  "cpu_freq_ghz": 3.5,
  "gpu_vram_gb": 12,
  "current_utilization": 0.8,
  "assigned_layers": [1, 2, 3, 4, 5],
  "last_heartbeat": "2026-06-03T10:30:00Z",
  "status": "active"
}
```

### Vote
```
{
  "node_id": "node-1",
  "tier": "72b",
  "model_choice": "qwen-72b",
  "timestamp": "2026-06-03T10:30:00Z"
}
```

### Model
```
{
  "id": "qwen-72b",
  "tier": "72b",
  "parameters": 72000000000,
  "size_gb": 144,
  "layers": 80,
  "url": "huggingface.co/Qwen/Qwen2-72B"
}
```

## Rebalancing Algorithm

```python
def rebalance_layers(active_nodes):
    total_ram_gb = sum(node.ram_gb * node.current_utilization for node in active_nodes)
    model = get_current_model()
    total_layers = model.layers
    
    layers_per_gb = total_layers / total_ram_gb
    
    for node in active_nodes:
        available_capacity = node.ram_gb * node.current_utilization
        num_layers = int(available_capacity * layers_per_gb)
        node.assigned_layers = assign_contiguous_layers(num_layers)
    
    broadcast_new_assignments()
```

## Voting System

Monthly voting occurs on the 1st of each month:
1. Nodes vote on preferred model per tier
2. Highest vote count wins per tier
3. System selects highest tier that fits mesh capacity
4. New model deployed

See `docs/VOTING.md` for detailed voting mechanics.
