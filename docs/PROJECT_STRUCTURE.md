# Enterprise Digital COO - Complete Project Structure

## Overview

This document provides a complete overview of the project structure, showing all components and their relationships.

## Directory Structure

```
enterprise-digital-coo/
│
├── README.md                          # Project overview and quick start
├── .gitignore                         # Git ignore rules
├── .env.example                       # Environment variables template
├── docker-compose.yml                 # Docker orchestration
├── LICENSE                            # Project license
│
├── docs/                              # Documentation
│   ├── architecture/                  # Architecture documentation
│   │   ├── SYSTEM_ARCHITECTURE.md    # Complete system architecture
│   │   ├── DATABASE_SCHEMA.md        # Database design
│   │   └── LANGGRAPH_ORCHESTRATION.md # LangGraph workflow design
│   ├── api/                          # API documentation
│   │   ├── API_REFERENCE.md          # API endpoints reference
│   │   └── WEBSOCKET_PROTOCOL.md     # WebSocket protocol
│   ├── deployment/                    # Deployment guides
│   │   ├── DEPLOYMENT_GUIDE.md       # Complete deployment guide
│   │   ├── KUBERNETES.md             # Kubernetes specific guide
│   │   └── DOCKER.md                 # Docker specific guide
│   ├── development/                   # Development guides
│   │   ├── DEVELOPMENT_GUIDE.md      # Development setup
│   │   ├── CONTRIBUTING.md           # Contribution guidelines
│   │   └── CODE_STYLE.md             # Code style guide
│   └── PROJECT_STRUCTURE.md          # This file
│
├── backend/                           # Backend application
│   ├── main.py                       # FastAPI application entry point
│   ├── config.py                     # Configuration management
│   ├── requirements.txt              # Python dependencies
│   ├── Dockerfile                    # Backend Docker image
│   ├── .env                          # Environment variables (not in git)
│   ├── alembic.ini                   # Database migration config
│   │
│   ├── agents/                       # AI Agent implementations
│   │   ├── __init__.py
│   │   ├── base_agent.py            # Abstract base agent class
│   │   ├── sales_agent.py           # Sales monitoring agent
│   │   ├── finance_agent.py         # Finance monitoring agent
│   │   ├── supply_chain_agent.py    # Supply chain monitoring agent
│   │   ├── procurement_agent.py     # Procurement monitoring agent
│   │   ├── hr_agent.py              # HR monitoring agent
│   │   └── risk_agent.py            # Enterprise risk monitoring agent
│   │
│   ├── orchestration/                # LangGraph orchestration
│   │   ├── __init__.py
│   │   ├── coo_graph.py             # Main COO state graph
│   │   ├── nodes.py                 # Graph node implementations
│   │   ├── state.py                 # State definitions
│   │   └── routing.py               # Conditional routing logic
│   │
│   ├── engines/                      # Intelligence engines
│   │   ├── __init__.py
│   │   ├── anomaly_detection.py     # Anomaly detection engine
│   │   ├── root_cause_analysis.py   # Root cause analysis engine
│   │   ├── simulation.py            # Simulation engine
│   │   └── recommendation.py        # Recommendation engine
│   │
│   ├── api/                          # API layer
│   │   ├── __init__.py
│   │   ├── v1/                      # API version 1
│   │   │   ├── __init__.py
│   │   │   ├── router.py            # Main API router
│   │   │   ├── endpoints/           # API endpoints
│   │   │   │   ├── __init__.py
│   │   │   │   ├── agents.py        # Agent endpoints
│   │   │   │   ├── anomalies.py     # Anomaly endpoints
│   │   │   │   ├── analytics.py     # Analytics endpoints
│   │   │   │   ├── recommendations.py # Recommendation endpoints
│   │   │   │   ├── simulations.py   # Simulation endpoints
│   │   │   │   └── health.py        # Health check endpoints
│   │   │   └── dependencies.py      # API dependencies
│   │   └── middleware.py            # Custom middleware
│   │
│   ├── models/                       # Data models
│   │   ├── __init__.py
│   │   ├── domain/                  # Domain models
│   │   │   ├── __init__.py
│   │   │   ├── sales.py             # Sales models
│   │   │   ├── finance.py           # Finance models
│   │   │   ├── supply_chain.py      # Supply chain models
│   │   │   ├── procurement.py       # Procurement models
│   │   │   ├── hr.py                # HR models
│   │   │   └── risk.py              # Risk models
│   │   ├── anomaly.py               # Anomaly models
│   │   ├── recommendation.py        # Recommendation models
│   │   ├── simulation.py            # Simulation models
│   │   └── user.py                  # User models
│   │
│   ├── schemas/                      # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── agent.py                 # Agent schemas
│   │   ├── anomaly.py               # Anomaly schemas
│   │   ├── recommendation.py        # Recommendation schemas
│   │   ├── simulation.py            # Simulation schemas
│   │   └── response.py              # Response schemas
│   │
│   ├── services/                     # Business logic services
│   │   ├── __init__.py
│   │   ├── agent_service.py         # Agent coordination service
│   │   ├── anomaly_service.py       # Anomaly management service
│   │   ├── recommendation_service.py # Recommendation service
│   │   ├── simulation_service.py    # Simulation service
│   │   ├── websocket_manager.py     # WebSocket connection manager
│   │   └── notification_service.py  # Notification service
│   │
│   ├── database/                     # Database layer
│   │   ├── __init__.py
│   │   ├── session.py               # Database session management
│   │   ├── base.py                  # Base model class
│   │   ├── repositories/            # Repository pattern
│   │   │   ├── __init__.py
│   │   │   ├── base_repository.py   # Base repository
│   │   │   ├── anomaly_repository.py
│   │   │   ├── recommendation_repository.py
│   │   │   └── metrics_repository.py
│   │   └── migrations/              # Alembic migrations
│   │       ├── env.py
│   │       ├── script.py.mako
│   │       └── versions/            # Migration versions
│   │
│   ├── memory/                       # Memory layer (ChromaDB)
│   │   ├── __init__.py
│   │   ├── chromadb_client.py       # ChromaDB client
│   │   ├── collections.py           # Collection management
│   │   └── embeddings.py            # Embedding utilities
│   │
│   ├── cache/                        # Cache layer (Redis)
│   │   ├── __init__.py
│   │   ├── redis_client.py          # Redis client
│   │   └── cache_manager.py         # Cache management
│   │
│   ├── utils/                        # Utility functions
│   │   ├── __init__.py
│   │   ├── logger.py                # Logging utilities
│   │   ├── security.py              # Security utilities
│   │   ├── validators.py            # Validation utilities
│   │   └── helpers.py               # Helper functions
│   │
│   ├── tasks/                        # Background tasks (Celery)
│   │   ├── __init__.py
│   │   ├── celery_app.py            # Celery application
│   │   ├── agent_tasks.py           # Agent execution tasks
│   │   └── maintenance_tasks.py     # Maintenance tasks
│   │
│   └── tests/                        # Backend tests
│       ├── __init__.py
│       ├── conftest.py              # Test configuration
│       ├── unit/                    # Unit tests
│       │   ├── test_agents.py
│       │   ├── test_engines.py
│       │   └── test_services.py
│       ├── integration/             # Integration tests
│       │   ├── test_api.py
│       │   └── test_workflows.py
│       └── e2e/                     # End-to-end tests
│           └── test_scenarios.py
│
├── frontend/                         # Frontend application
│   ├── package.json                 # Node dependencies
│   ├── package-lock.json
│   ├── tsconfig.json                # TypeScript configuration
│   ├── Dockerfile                   # Frontend Docker image
│   ├── .env                         # Environment variables (not in git)
│   ├── .env.example                 # Environment template
│   │
│   ├── public/                      # Public assets
│   │   ├── index.html
│   │   ├── favicon.ico
│   │   └── manifest.json
│   │
│   └── src/                         # Source code
│       ├── index.tsx                # Application entry point
│       ├── App.tsx                  # Root component
│       ├── setupTests.ts            # Test setup
│       │
│       ├── components/              # React components
│       │   ├── common/              # Common components
│       │   │   ├── Button.tsx
│       │   │   ├── Card.tsx
│       │   │   ├── Modal.tsx
│       │   │   ├── Spinner.tsx
│       │   │   └── Alert.tsx
│       │   ├── layout/              # Layout components
│       │   │   ├── Header.tsx
│       │   │   ├── Sidebar.tsx
│       │   │   ├── Footer.tsx
│       │   │   └── Layout.tsx
│       │   ├── dashboard/           # Dashboard components
│       │   │   ├── DashboardOverview.tsx
│       │   │   ├── MetricsCard.tsx
│       │   │   ├── AnomalyAlert.tsx
│       │   │   └── RecommendationCard.tsx
│       │   ├── agents/              # Agent components
│       │   │   ├── AgentStatus.tsx
│       │   │   ├── AgentList.tsx
│       │   │   └── AgentDetails.tsx
│       │   ├── analytics/           # Analytics components
│       │   │   ├── ChartContainer.tsx
│       │   │   ├── TimeSeriesChart.tsx
│       │   │   ├── BarChart.tsx
│       │   │   └── PieChart.tsx
│       │   └── simulations/         # Simulation components
│       │       ├── SimulationRunner.tsx
│       │       ├── SimulationResults.tsx
│       │       └── ScenarioBuilder.tsx
│       │
│       ├── pages/                   # Page components
│       │   ├── Dashboard.tsx        # Main dashboard
│       │   ├── Agents.tsx           # Agents page
│       │   ├── Anomalies.tsx        # Anomalies page
│       │   ├── Analytics.tsx        # Analytics page
│       │   ├── Recommendations.tsx  # Recommendations page
│       │   ├── Simulations.tsx      # Simulations page
│       │   └── Settings.tsx         # Settings page
│       │
│       ├── services/                # API services
│       │   ├── api.ts               # Base API client
│       │   ├── websocket.ts         # WebSocket client
│       │   ├── agentService.ts      # Agent API service
│       │   ├── anomalyService.ts    # Anomaly API service
│       │   ├── recommendationService.ts
│       │   └── simulationService.ts
│       │
│       ├── hooks/                   # Custom React hooks
│       │   ├── useWebSocket.ts      # WebSocket hook
│       │   ├── useAgents.ts         # Agents data hook
│       │   ├── useAnomalies.ts      # Anomalies data hook
│       │   └── useRealTimeUpdates.ts
│       │
│       ├── store/                   # State management (Zustand)
│       │   ├── index.ts
│       │   ├── agentStore.ts        # Agent state
│       │   ├── anomalyStore.ts      # Anomaly state
│       │   ├── uiStore.ts           # UI state
│       │   └── authStore.ts         # Auth state
│       │
│       ├── types/                   # TypeScript types
│       │   ├── agent.ts
│       │   ├── anomaly.ts
│       │   ├── recommendation.ts
│       │   ├── simulation.ts
│       │   └── api.ts
│       │
│       ├── utils/                   # Utility functions
│       │   ├── formatters.ts        # Data formatters
│       │   ├── validators.ts        # Validators
│       │   └── helpers.ts           # Helper functions
│       │
│       ├── styles/                  # Styles
│       │   ├── globals.css          # Global styles
│       │   └── tailwind.css         # Tailwind imports
│       │
│       └── tests/                   # Frontend tests
│           ├── components/          # Component tests
│           ├── pages/               # Page tests
│           └── integration/         # Integration tests
│
├── scripts/                          # Utility scripts
│   ├── seed_data.py                 # Database seeding
│   ├── generate_test_data.py       # Test data generation
│   ├── backup.sh                    # Backup script
│   ├── restore.sh                   # Restore script
│   └── deploy.sh                    # Deployment script
│
├── k8s/                             # Kubernetes manifests
│   ├── namespace.yaml               # Namespace definition
│   ├── configmap.yaml               # Configuration
│   ├── secrets.yaml                 # Secrets (template)
│   ├── postgres-deployment.yaml     # PostgreSQL deployment
│   ├── redis-deployment.yaml        # Redis deployment
│   ├── chromadb-deployment.yaml     # ChromaDB deployment
│   ├── backend-deployment.yaml      # Backend deployment
│   ├── frontend-deployment.yaml     # Frontend deployment
│   ├── ingress.yaml                 # Ingress configuration
│   └── hpa.yaml                     # Horizontal Pod Autoscaler
│
├── monitoring/                       # Monitoring configuration
│   ├── prometheus/                  # Prometheus config
│   │   ├── prometheus.yml
│   │   └── alerts.yml
│   ├── grafana/                     # Grafana dashboards
│   │   ├── dashboards/
│   │   │   ├── coo-overview.json
│   │   │   ├── agents-metrics.json
│   │   │   └── system-metrics.json
│   │   └── provisioning/
│   └── alertmanager/                # Alert manager config
│       └── alertmanager.yml
│
└── .github/                         # GitHub specific files
    ├── workflows/                   # GitHub Actions
    │   ├── ci.yml                   # Continuous Integration
    │   ├── cd.yml                   # Continuous Deployment
    │   └── tests.yml                # Test automation
    ├── ISSUE_TEMPLATE/              # Issue templates
    └── PULL_REQUEST_TEMPLATE.md     # PR template
```

## Key Components

### Backend Components

1. **Agents** (`backend/agents/`)
   - Base agent framework
   - 6 domain-specific agents
   - Memory integration
   - OpenAI integration

2. **Orchestration** (`backend/orchestration/`)
   - LangGraph state machine
   - Workflow coordination
   - Agent execution management

3. **Engines** (`backend/engines/`)
   - Anomaly detection
   - Root cause analysis
   - Simulation engine
   - Recommendation engine

4. **API** (`backend/api/`)
   - RESTful endpoints
   - WebSocket support
   - Authentication
   - Rate limiting

5. **Database** (`backend/database/`)
   - PostgreSQL integration
   - Repository pattern
   - Migrations (Alembic)

6. **Memory** (`backend/memory/`)
   - ChromaDB integration
   - Vector embeddings
   - Context retrieval

### Frontend Components

1. **Dashboard** (`frontend/src/pages/Dashboard.tsx`)
   - Real-time metrics
   - Anomaly alerts
   - Executive summary

2. **Components** (`frontend/src/components/`)
   - Reusable UI components
   - Charts and visualizations
   - Agent status displays

3. **Services** (`frontend/src/services/`)
   - API clients
   - WebSocket management
   - Data fetching

4. **State Management** (`frontend/src/store/`)
   - Zustand stores
   - Global state
   - Real-time updates

## Data Flow

```
External Systems → API Gateway → Orchestration Layer → Agents
                                        ↓
                                  Intelligence Engines
                                        ↓
                                  Memory & Storage
                                        ↓
                                  API Response → Frontend
```

## Technology Stack Summary

### Backend
- **Framework**: FastAPI
- **Language**: Python 3.11+
- **AI/ML**: OpenAI, LangChain, LangGraph
- **Databases**: PostgreSQL, ChromaDB, Redis
- **Task Queue**: Celery

### Frontend
- **Framework**: React 18
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State**: Zustand
- **Charts**: Recharts

### Infrastructure
- **Containers**: Docker
- **Orchestration**: Kubernetes
- **Monitoring**: Prometheus, Grafana
- **CI/CD**: GitHub Actions

## Development Workflow

1. **Local Development**
   - Use Docker Compose for services
   - Hot reload for both backend and frontend
   - Local database and cache

2. **Testing**
   - Unit tests for components
   - Integration tests for APIs
   - E2E tests for workflows

3. **Deployment**
   - Build Docker images
   - Push to registry
   - Deploy to Kubernetes
   - Run migrations

## File Naming Conventions

- **Python**: `snake_case.py`
- **TypeScript/React**: `PascalCase.tsx` for components, `camelCase.ts` for utilities
- **Configuration**: `kebab-case.yaml` or `lowercase.json`
- **Documentation**: `UPPERCASE.md` for main docs, `lowercase.md` for specific docs

## Import Conventions

### Python
```python
# Standard library
import os
from typing import Dict

# Third-party
from fastapi import FastAPI
from langchain import LLMChain

# Local
from agents.base_agent import BaseAgent
from config import settings
```

### TypeScript
```typescript
// React and libraries
import React from 'react';
import { useQuery } from 'react-query';

// Local components
import { Button } from '@/components/common';
import { agentService } from '@/services';

// Types
import type { Agent } from '@/types';
```

## Next Steps

1. Review architecture documentation
2. Set up development environment
3. Implement remaining agents
4. Build frontend dashboard
5. Add comprehensive tests
6. Deploy to staging
7. Performance optimization
8. Production deployment

## Resources

- [System Architecture](./architecture/SYSTEM_ARCHITECTURE.md)
- [Database Schema](./architecture/DATABASE_SCHEMA.md)
- [LangGraph Orchestration](./architecture/LANGGRAPH_ORCHESTRATION.md)
- [Deployment Guide](./DEPLOYMENT_GUIDE.md)
- [API Reference](./api/API_REFERENCE.md)