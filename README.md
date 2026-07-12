# Enterprise Digital COO

AI-powered executive command center for detecting business crises, explaining root cause, and recommending operational action.

## Hackathon Story

Enterprises do not fail because one dashboard turns red. They fail because revenue, operations, finance, and customer signals are separated until it is too late.

Enterprise Digital COO turns those scattered signals into one executive workflow:

1. **Detect the crisis**: revenue drops, inventory rises, churn risk spikes, and cash runway tightens.
2. **Explain the root cause**: the AI connects operational issues to financial impact and customer risk.
3. **Simulate the impact**: leaders see projected revenue exposure, savings, and risk reduction.
4. **Recommend action**: the system produces a COO-style response plan that can be approved or explored.

The demo scenario is a "perfect storm" at a B2B company: revenue is down 15%, inventory is up 35%, churn risk is up 12%, and the AI COO identifies the operational chain behind the crisis.

## What Is Working Now

This repository currently ships a working FastAPI + static dashboard prototype:

- Executive dashboard served from `backend/static/index.html`
- Sales, finance, operations, and summary APIs under `/api/v1/metrics`
- Report upload, AI import, and report chat APIs under `/api/v1/reports`
- Slack, Microsoft Teams, and approval email notification APIs under `/api/v1/notifications`
- Static pages for sales, finance, operations, reports, and Excel analysis
- Vercel-compatible serverless entrypoint at `api/index.py`
- Optional OpenAI-powered chat and report analysis when `OPENAI_API_KEY` is configured
- React + TypeScript voice conversation UI with live transcripts, waveform feedback, and conversation history
- Browser-native wake phrase support for **"Hey Enterprise Digital COO"**
- Accessible microphone controls across dashboard, Sales, Finance, Operations, Reports, and Excel Analysis
- OpenAI Realtime WebRTC handshake endpoint for low-latency speech conversations
- Optional Slack and Teams alerts when notification credentials are configured
- Demo approval email capture, with real email delivery when SMTP settings are configured
- Architecture docs for the larger multi-agent vision using LangGraph, ChromaDB, PostgreSQL, Redis, and WebSockets

The production vision includes multi-agent orchestration, memory, and persistent infrastructure. The hackathon demo surface is intentionally lighter so judges can run and inspect it quickly.

## Demo Flow

1. Open the dashboard.
2. Start with the impact strip: revenue loss, inventory spike, churn risk, and action plan.
3. Ask the AI COO: "What happened to revenue this quarter?"
4. Alternatively, grant microphone permission and say **"Hey Enterprise Digital COO"**, then speak the command after the bot displays **"I'm listening..."**.
5. Open Sales, Finance, and Operations to show cross-domain signals.
6. Use Reports or Excel Analysis to show how business data can be uploaded and summarized.
7. Close with the recommendation: supplier quality recovery, customer save plan, inventory rebalance, and cash protection.

## Architecture

### Current Prototype

```text
Browser
  |
  | Static HTML dashboard + React/TypeScript voice layer
  | Web Speech API wake phrase + WebRTC audio
  v
FastAPI
  |
  | /api/v1/metrics
  | /api/v1/reports
  | /api/v1/notifications
  | /api/v1/realtime
  v
Deterministic demo data + optional OpenAI analysis
  |
  v
Optional Slack, Teams, and approval email notifications
```

### Larger System Vision

```text
Executive Dashboard
  |
FastAPI + WebSocket API
  |
LangGraph COO Orchestrator
  |
Specialized Agents: Sales, Finance, Operations, Procurement, HR, Risk
  |
Intelligence Layer: anomaly detection, root cause analysis, simulation, recommendations
  |
PostgreSQL + ChromaDB + Redis + OpenAI
```

## Key Features

- **Executive command center**: one screen for business health, risk, and recommended action.
- **Cross-domain metrics**: sales, finance, and operations endpoints expose fiscal-year data and comparisons.
- **AI COO assistant**: dashboard chat summarizes risks and recommends next steps.
- **Hands-free wake phrase**: continuously ignores unrelated speech until "Hey Enterprise Digital COO" is detected, then captures one command and returns to wake mode.
- **Voice conversation**: synthesized responses, live transcript, animated waveform, interruption support, and locally persisted conversation history.
- **Accessible AI compose fields**: visible microphone control, listening status, keyboard support, and screen-reader announcements.
- **Motion-aware dashboard**: progressive 3D spiral scrolling with reduced-motion and mobile fallbacks; the Ask Enterprise COO compose card remains flat.
- **Report intelligence**: upload JSON, Excel, or Power BI-style files and ask questions about them.
- **Notification integrations**: send approved actions and COO summary alerts to Slack, Microsoft Teams, and demo approval email.
- **Deployment-friendly prototype**: `api/index.py` excludes persistent database startup so the demo can run serverlessly.

## Project Structure

```text
enterprise-digital-coo/
├── api/
│   └── index.py                  # Vercel/serverless FastAPI entrypoint
├── backend/
│   ├── api/v1/endpoints/         # Metrics and reports APIs
│   ├── agents/                   # Agent prototypes
│   ├── database/                 # PostgreSQL session/models for full-stack vision
│   ├── memory/                   # ChromaDB client for full-stack vision
│   ├── orchestration/            # Workflow prototypes
│   ├── services/                 # Shared services, including notification integrations
│   ├── static/                   # Working dashboard and demo pages
│   ├── config.py                 # App configuration
│   └── main.py                   # Full backend entrypoint
├── frontend/
│   └── realtime-voice/           # React + TypeScript voice/wake-word source and Vite build
├── docs/                         # Architecture, demo, and presentation material
├── tools/                        # Node helper scripts
├── pyproject.toml                # Lightweight deploy/runtime dependencies
└── vercel.json                   # Vercel routing
```

## Quick Start

### Serverless-style demo app

This path is closest to the judging/demo surface.

```bash
pip install -e .
uvicorn api.index:app --reload --port 8001
```

Open:

```text
http://localhost:8001/
```

### Full backend app

Use this only when PostgreSQL and related services are configured.

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python main.py
```

The full backend starts on the configured `PORT`, defaulting to `8001`.

### Voice frontend development

The production bundle is committed under `backend/static/assets/realtime-voice/`. Rebuild it after changing the React or TypeScript source:

```bash
cd frontend/realtime-voice
npm install
npm run build
```

The build writes directly to the backend static assets directory.

## Useful Endpoints

```text
GET  /health
GET  /api/v1/metrics/sales
GET  /api/v1/metrics/sales/fy
GET  /api/v1/metrics/finance
GET  /api/v1/metrics/operations
GET  /api/v1/metrics/summary
POST /api/v1/metrics/chat
POST /api/v1/reports/upload
POST /api/v1/reports/chat
POST /api/v1/reports/ai-import
POST /api/v1/realtime/call
GET  /api/v1/notifications/integrations/status
GET  /api/v1/notifications/slack/status
POST /api/v1/notifications/slack/test
POST /api/v1/notifications/slack/message
POST /api/v1/notifications/slack/coo-summary
GET  /api/v1/notifications/teams/status
POST /api/v1/notifications/teams/test
POST /api/v1/notifications/teams/message
POST /api/v1/notifications/teams/coo-summary
GET  /api/v1/notifications/email/status
POST /api/v1/notifications/approval
```

## Environment

Copy `backend/.env.example` to `backend/.env` for local full-backend runs.

For the demo, `OPENAI_API_KEY` is optional. Without it, the deterministic dashboard and metrics still work; OpenAI-backed chat/report analysis requires a valid key.

The Realtime WebRTC conversation also uses `OPENAI_API_KEY`. The permanent key remains on the FastAPI server; the browser sends its SDP offer to `/api/v1/realtime/call`, and the backend performs the authenticated OpenAI handshake.

```env
OPENAI_API_KEY=your-openai-api-key
```

### Voice and wake-word browser support

- Microphone access requires user permission and a secure context: HTTPS or localhost.
- The wake phrase uses the browser Web Speech API and works best in current Chrome and Edge.
- Other browsers may support the microphone compose control while lacking continuous wake-word recognition.
- The wake-word recognizer ignores other final transcripts until it detects "Hey Enterprise Digital COO".
- After activation, it waits up to 10 seconds for one command, speaks the AI response using Speech Synthesis, and automatically returns to wake mode.
- Voice history is stored locally in the browser and can be cleared from the voice panel.
- Reduced-motion preferences disable nonessential blinking and motion effects.

Slack is optional. For the simplest setup, create a Slack incoming webhook and set:

```env
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
```

Microsoft Teams is optional. Set an incoming webhook URL:

```env
TEAMS_WEBHOOK_URL=https://...
```

The dashboard Approve button opens a confirmation popup. Leaders can approve immediately, keep reviewing, or approve with a timed undo window of 15 seconds, 1 minute, 3 minutes, or 5 minutes. Approved actions keep their glowing state after refresh; the Undo option appears only during the selected review window. The backend still supports approval email delivery for future flows; without SMTP settings, the backend captures approval email as a demo preview, and with SMTP settings it sends a real email:

```env
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USERNAME=your-smtp-user
SMTP_PASSWORD=your-smtp-password
SMTP_USE_TLS=true
EMAIL_FROM=coo@example.com
```

When deploying on Vercel, add the same Slack, Teams, and SMTP variables in the Vercel project environment settings. The serverless entrypoint at `api/index.py` includes the notification routes.

## Validation

Validate the React voice interface and regenerate its production assets:

```bash
cd frontend/realtime-voice
npx tsc --noEmit
npm run build
```

From `backend/`:

```bash
python test_routes.py
```

Expected result: health, API health, sales, finance, operations, summary, and notification status routes return `200`.

To verify notification configuration without posting a message:

```text
GET /api/v1/notifications/integrations/status
```

To send a Slack smoke-test message after configuring Slack:

```text
POST /api/v1/notifications/slack/test
```

## Node.js Developer Tooling

The `tools/` directory contains optional helper scripts.

```bash
cd tools
npm install
npm run health
npm run validate-env
npm run watch-logs
```

## Winning Position

Enterprise Digital COO is strongest when presented as a working executive decision prototype backed by a credible enterprise architecture:

- **Innovation**: AI COO experience that connects siloed operational signals.
- **Execution**: working dashboard, APIs, report upload, and AI assistant.
- **Business impact**: faster crisis detection, root-cause clarity, and action prioritization.
- **Scalability**: documented path to multi-agent orchestration, memory, and persistent enterprise data.

## License

MIT License - Built for Business Transformation Hackathon 2026
