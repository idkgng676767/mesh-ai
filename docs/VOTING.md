# Voting System (MVP)

## MVP Tier Support
- Enabled: 8B, 24B, 72B tiers
- Not enabled in MVP: 144B, Frontier

## Voting Window
- Voting opens on the 1st of each month (UTC)
- Voting closes on the last day of the month at 23:59 UTC

## How It Works
1. Nodes cast one vote per tier for the active period.
2. The controller aggregates votes per tier.
3. The highest-voted model wins each tier.
4. The system selects the highest tier that fits total mesh capacity.
5. The winning model for that tier becomes active for the next period.

## Tie-Breaks
- Ties resolve by most recent model registration time.

## API Surface (Controller)
- `POST /votes/{tier}` cast a vote
- `GET /votes/results` list current period results
- `GET /current-model` returns active model
- `POST /admin/rollover` forces monthly selection (MVP testing)
