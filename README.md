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
- Structured COO orchestration with intent detection, specialized agent routing, analysis, forecasts, confidence scoring, recommended actions, and dashboard-ready JSON
- React + TypeScript voice conversation UI with live transcripts, waveform feedback, and conversation history
- Browser-native wake phrase support for **"Hey Enterprise Digital COO"**
- OpenAI-powered compose dictation using MediaRecorder, adaptive silence detection, and `gpt-4o-mini-transcribe`
- Accessible microphone controls across dashboard, Sales, Finance, Operations, Reports, and Excel Analysis without relying on browser Web Speech for compose transcription
- OpenAI Realtime WebRTC handshake endpoint for low-latency speech conversations
- AI Email Agent in the existing Ask Enterprise COO input, with editable preview, AI drafting, explicit send confirmation, and delivery animation
- Optional Slack and Teams alerts when notification credentials are configured
- Transactional approval email delivery: cancellation or email failure leaves the action unapproved
- Persistent Judge Demo scenarios with a dedicated Undo Executive Approval control
- Architecture docs for the larger multi-agent vision using LangGraph, ChromaDB, PostgreSQL, Redis, and WebSockets

The production vision includes multi-agent orchestration, memory, and persistent infrastructure. The hackathon demo surface is intentionally lighter so judges can run and inspect it quickly.

## Demo Flow

1. Open the dashboard.
2. Start with the impact strip: revenue loss, inventory spike, churn risk, and action plan.
3. Ask the AI COO: "What happened to revenue this quarter?"
4. Alternatively, grant microphone permission and say **"Hey Enterprise Digital COO"**, then speak the command after the bot displays **"I'm listening..."**.
5. Ask the COO to draft or send an email, review the generated preview, optionally use **Draft with AI**, and explicitly confirm delivery.
6. Open Sales, Finance, and Operations to show cross-domain signals.
7. Use Reports or Excel Analysis to show how business data can be uploaded and summarized.
8. Demonstrate approval, refresh persistence, and the Judge Demo **Undo Executive Approval** control.

## Architecture

### Current Prototype

```text
Browser
  |
  | Static HTML dashboard + React/TypeScript voice layer
  | Web Speech API wake phrase + MediaRecorder compose audio + WebRTC conversation audio
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
- **AI COO assistant**: identifies business intent, selects the appropriate agent, analyzes connected dashboard data, forecasts impact, and returns structured executive JSON.
- **Hands-free wake phrase**: continuously ignores unrelated speech until "Hey Enterprise Digital COO" is detected, then captures one command and returns to wake mode.
- **Voice conversation**: synthesized responses, live transcript, animated waveform, interruption support, and locally persisted conversation history.
- **OpenAI compose transcription**: MediaRecorder captures microphone audio, adaptive silence detection ends the turn, and `gpt-4o-mini-transcribe` returns the text without Browser Web Speech dependency.
- **AI Email Agent**: draft, reply, summarize, and send email requests use the existing Ask COO input and open a themed editable confirmation modal.
- **Safe approval workflow**: approval completes only after recipient confirmation and successful email delivery; judge scenarios retain persistent demo Undo controls.
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

### Run the webpage

From the repository root, use these commands to install the lightweight demo dependencies and start the dashboard.

Windows PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e .
python -m uvicorn api.index:app --reload --host 127.0.0.1 --port 8001
```

macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e .
python -m uvicorn api.index:app --reload --host 127.0.0.1 --port 8001
```

Open the webpage at:

```text
http://127.0.0.1:8001/
```

Keep the terminal running while using the dashboard. Press `Ctrl+C` in that terminal to stop the server. OpenAI voice, transcription, AI chat, and email features read their credentials from `backend/.env`.

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
POST /api/v1/realtime/transcribe
POST /api/v1/realtime/speech
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
POST /api/v1/notifications/email/send
POST /api/v1/notifications/approval
```

## Environment

Copy `backend/.env.example` to `backend/.env` for local full-backend runs.

For the deterministic dashboard, `OPENAI_API_KEY` is optional. OpenAI chat, report analysis, compose transcription, spoken responses, and Realtime voice require a valid key.

The permanent key remains on the FastAPI server. The browser sends its SDP offer to `/api/v1/realtime/call`, microphone recordings to `/api/v1/realtime/transcribe`, and generated answer text to `/api/v1/realtime/speech`; the backend performs all authenticated OpenAI requests.

```env
OPENAI_API_KEY=your-openai-api-key
```

### Voice and wake-word browser support

- Microphone access requires user permission and a secure context: HTTPS or localhost.
- Compose dictation uses MediaRecorder and OpenAI transcription instead of the Browser Web Speech API.
- Compose dictation stops after approximately 1.4 seconds of detected silence, supports quiet desktop microphones with adaptive sensitivity, and keeps the mobile software keyboard closed during recording.
- The optional continuous wake phrase still uses the browser Web Speech API and works best in current Chrome and Edge.
- Browsers may support OpenAI compose dictation while lacking continuous wake-word recognition.
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

The dashboard Approve button opens a confirmation popup. Leaders can approve immediately, keep reviewing, or approve with a timed undo window of 15 seconds, 1 minute, 3 minutes, or 5 minutes. Final approval requires an email recipient and successful delivery; cancelling the popup or receiving an SMTP error returns the action to review. Judge scenarios and approval state survive refresh, and the Judge Demo Path exposes a persistent **Undo Executive Approval** control.

The AI Email Agent also uses SMTP for explicitly confirmed email drafts. Example Gmail configuration:

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-address@gmail.com
SMTP_PASSWORD=your-16-character-app-password
SMTP_USE_TLS=true
EMAIL_FROM=your-address@gmail.com
```

For Gmail, enable two-step verification and create an App Password. Do not use the Gmail account password or the dashboard demo password as `SMTP_PASSWORD`.

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
