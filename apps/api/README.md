# API service

Fastify + TypeScript API that receives inbound messages/calls via webhooks, normalizes them, and pushes them into a unified inbox.

## Endpoints
- `GET /health`
- `POST /v1/webhooks/:channel/inbound` (e.g. `whatsapp`, `instagram`, `webchat`, `voice`)
- `GET /v1/inbox` (returns recent items)

