# Mesh AI - Decentralized Frontier Model Distribution

A peer-to-peer distributed inference network where users donate compute resources and earn access to frontier AI models in return.

## Core Concept

- **10,000+ users** donate RAM + GPU resources
- **Monthly democratic vote** on which model runs (8B, 24B, 72B, 144B, or Frontier tier)
- **80TB+ mesh capacity** = run Kimi K1.6, Llama, or whatever frontier model wins the vote
- **Zero cost:** Users contribute compute → earn points → get free API/GUI access
- **Dynamic scaling:** App automatically scales down when user needs their GPU back

## Architecture

```
┌─────────────────────┐
│  Central Controller  │
│  (Model storage,    │
│   voting, routing)  │
└──────────┬──────────┘
           │
    ┌──────┴──────┐
    │             │
┌───▼───┐    ┌───▼───┐
│Node 1 │    │Node 2 │  ... 10,000 nodes
│8GB RAM│    │16GB   │
│GPU 50%│    │GPU 30%│
└───────┘    └───────┘

Each node holds layers of the active model.
Inference flows through: Node1 → Node2 → ... → NodeN
```

## Monthly Voting System

1. **Community votes** on model per tier:
   - 8B tier: 20 models to choose from
   - 24B tier: 20 models to choose from
   - 72B tier: 20 models to choose from
   - 144B tier: 20 models to choose from
   - Frontier tier: 20 frontier models

2. **Automatic tier selection** based on total mesh capacity

3. **Layer distribution** to all nodes

4. **Inference enabled** for the entire month

## Resource Contribution

**User's Machine:**
- Idle: 8GB VRAM + 50% GPU cores allocated to app
- Gaming/Heavy use: App scales down to 1GB VRAM + 5% GPU cores
- User never loses performance

**Point Calculation:**
```
Daily Points = (RAM GB × CPU Frequency GHz) × 100 × current_utilization_multiplier
```

Example:
- 8GB + 3.5GHz CPU at 100% utilization = 2,800 points/day
- During 50% utilization = 1,400 points/day

**Point Usage:**
- 5,000+ points/day = unlimited API access to current month's model

## Components

### 1. Controller Server
- Model orchestration & storage
- Node registry & heartbeat monitoring
- Monthly voting system
- Layer-to-node assignment
- Request routing & inference coordination
- Rebalancing on node join/leave

### 2. Node App
- Resource monitoring (RAM, GPU, CPU)
- Dynamic scaling based on user activity
- Layer streaming from controller
- Inter-node inference communication
- Point calculation & reporting

### 3. API & GUI
- Web interface for inference
- REST API for programmatic access
- Point balance display
- Network status dashboard

### 4. Inference Pipeline
- Distributed layer processing
- Fault tolerance & redundancy
- Latency optimization

## MVP Scope (Initial Release)

- **Supported tiers:** 8B, 24B, 72B (144B and Frontier are listed but not enabled in MVP)
- **Points policy:** Daily points are accrued from actual utilization; inference costs use a simple fixed-rate table
- **Throughput targets:** ~5 requests/second for 200 active nodes (MVP goal)
- **Node count targets:** 100–500 nodes during MVP rollout

## Project Structure

```
mesh-ai/
├── controller/           # Central orchestration server (FastAPI)
│   ├── app/              # API, models, scheduler
│   ├── requirements.txt
│   └── tests/
├── node-app/             # User-facing node application (FastAPI)
│   ├── agent/            # Monitoring + inference agent
│   ├── requirements.txt
│   └── tests/
├── gui/                  # Web interface
│   ├── frontend/         # React frontend (Vite)
│   └── backend/          # FastAPI server
├── docs/                 # Architecture & docs
├── scripts/              # Deployment & setup
└── docker-compose.yml
```

## Tech Stack

- **Controller:** Python (FastAPI)
- **Node App:** Python (PyTorch, psutil, GPUtil)
- **GUI:** React + FastAPI
- **Database:** PostgreSQL
- **Caching:** Redis
- **Inference:** vLLM / TorchServe
- **Deployment:** Docker, Kubernetes (optional)

## Getting Started

### Development

```bash
# Clone repo
git clone https://github.com/idkgng676767/mesh-ai.git
cd mesh-ai

# Setup controller
cd controller
pip install -r requirements.txt
python -m app.main

# Setup node (separate terminal)
cd node-app
pip install -r requirements.txt
python -m agent.main

# Setup GUI (separate terminal)
cd gui/backend
pip install -r requirements.txt
python -m main
```

## Key Milestones

- [ ] Phase 1: Controller + Basic Node App
- [ ] Phase 2: Voting & Rebalancing
- [ ] Phase 3: GUI & API
- [ ] Phase 4: Optimization
- [ ] Phase 5: Scale to 10,000+ nodes

## License

MIT
