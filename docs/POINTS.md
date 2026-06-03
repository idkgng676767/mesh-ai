# Points Policy (MVP)

## Daily Accrual
```
Daily Points = (RAM_GB × CPU_GHZ) × 100 × utilization_multiplier
```
- Utilization multiplier is reported by the node app
- Minimum multiplier: 0.1
- Accrual runs once per day at 00:05 UTC

## Inference Costs
- Short prompt: 30 points
- Standard prompt: 50 points
- Long prompt: 80 points

## Ledger
- Points are stored as immutable ledger entries
- Balance = sum(ledger entries)

## API Surface
- `GET /points/{node_id}/balance`
- `POST /points/accrue`
