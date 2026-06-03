# Inference Pipeline (MVP)

## Flow
1. User submits prompt to the controller.
2. Controller resolves ordered layer assignments for the active model.
3. Controller forwards the request to each node in order.
4. Each node processes its layer range and returns an updated hidden state.
5. Controller returns the final output to the user.

## Hidden State Payload
- JSON payload with a `hidden_state` field (string for MVP)
- The hidden state is opaque to the controller

## Timeouts & Retries
- Default node timeout: 10 seconds
- Retry count: 2
- Controller marks a request failed after retry exhaustion

## API Surface
- `POST /infer` on the controller
- `POST /infer` on the node app
