# Layer Rebalancing (MVP)

## Trigger Events
- Node register / deregister
- Heartbeat utilization updates
- Manual call to `/layers/rebalance`

## Algorithm (MVP)
1. Calculate total available capacity = Σ (ram_gb × utilization)
2. Calculate layers per GB = total_layers / total_capacity
3. Assign each node a contiguous range proportional to its capacity
4. Persist assignments and notify nodes on next heartbeat

## API Surface
- `GET /layers/{model_id}`
- `POST /layers/rebalance`
