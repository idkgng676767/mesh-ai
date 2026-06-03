# Deployment (MVP)

## Local Dev
- Controller: `scripts/dev-controller.sh`
- Node app: `scripts/dev-node.sh`
- GUI backend: `scripts/dev-gui-backend.sh`
- GUI frontend: `scripts/dev-gui-frontend.sh`

## Docker
- `docker-compose.yml` runs controller + GUI backend
- Each component has a Dockerfile

## Environment Variables
- `CONTROLLER_URL` (node app, gui backend)
- `NODE_ID` (optional for node app)
- `GUI_BACKEND_PORT` (gui backend)
