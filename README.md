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
- Optional Slack and Teams alerts when notification credentials are configured
- Demo approval email capture, with real email delivery when SMTP settings are configured
- Architecture docs for the larger multi-agent vision using LangGraph, ChromaDB, PostgreSQL, Redis, and WebSockets

The production vision includes multi-agent orchestration, memory, and persistent infrastructure. The hackathon demo surface is intentionally lighter so judges can run and inspect it quickly.

## Demo Flow

1. Open the dashboard.
2. Start with the impact strip: revenue loss, inventory spike, churn risk, and action plan.
3. Ask the AI COO: "What happened to revenue this quarter?"
4. Open Sales, Finance, and Operations to show cross-domain signals.
5. Use Reports or Excel Analysis to show how business data can be uploaded and summarized.
6. Close with the recommendation: supplier quality recovery, customer save plan, inventory rebalance, and cash protection.

## Architecture

### Current Prototype

```text
Browser
  |
  | Static HTML dashboard and pages
  v
FastAPI
  |
  | /api/v1/metrics
  | /api/v1/reports
  | /api/v1/notifications
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

Slack is optional. For the simplest setup, create a Slack incoming webhook and set:

```env
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
```

Microsoft Teams is optional. Set an incoming webhook URL:

```env
TEAMS_WEBHOOK_URL=https://...
```

The dashboard includes demo approval notification options for Slack, Teams, and email. The user can enter an email address before approving an executive action. Without SMTP settings, the backend captures the approval email as a demo preview; with SMTP settings, it sends a real email:

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
