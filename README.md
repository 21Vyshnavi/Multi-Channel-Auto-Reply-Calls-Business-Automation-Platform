# Multi Channel Auto Reply, Calls & Business Automation Platform

Unified conversational inbox + automation platform scaffold for businesses to handle enquiries across WhatsApp, Instagram, Facebook, LinkedIn, website chat, and phone calls.

## What’s included (scaffold)
- **API service** (`apps/api`): Fastify + TypeScript, webhook endpoints, simple in-memory storage.
- **Dashboard (Streamlit)** (`apps/streamlit`): Streamlit UI that shows the inbox and can send test enquiries.
- **Dashboard (React, optional)** (`apps/dashboard`): React + Vite + TypeScript UI (kept as an alternative).

## MVP features
- Unified inbox for inbound enquiries (`/v1/webhooks/:channel/inbound` → `/v1/inbox`)
- Auto-reply rules (keyword/channel matching) with CRUD (`/v1/rules`)
- Lead capture (`/v1/leads`)
- Appointment booking + cancel (`/v1/appointments`)

## Quick start
1) Install deps (works with older npm too)
```bash
npm install
npm run install:all
```

2) Configure env
```bash
cp apps/api/.env.example apps/api/.env
```

3) Run API (terminal 1)
```bash
npm run dev:api
```

4) Run React dashboard (terminal 2, optional)
```bash
npm run dev:dashboard
```

5) Run Streamlit dashboard (terminal 2 or 3)
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r apps/streamlit/requirements.txt
streamlit run apps/streamlit/app.py
```

API: `http://localhost:8080`  
React dashboard: `http://localhost:5173`  
Streamlit dashboard: shown in your terminal (usually `http://localhost:8501`)

## Next steps
- Add real channel credentials in `apps/api/.env`
- Implement providers in `packages/adapters/*`
- Replace in-memory storage with Postgres/Redis (optional)
