# Enterprise Digital COO - Deployment Guide

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Local Development Setup](#local-development-setup)
3. [Docker Deployment](#docker-deployment)
4. [Kubernetes Deployment](#kubernetes-deployment)
5. [Configuration](#configuration)
6. [Monitoring](#monitoring)
7. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements
- **OS**: Linux (Ubuntu 20.04+), macOS, or Windows with WSL2
- **CPU**: 4+ cores recommended
- **RAM**: 16GB minimum, 32GB recommended
- **Storage**: 50GB+ available space
- **Network**: Stable internet connection for API calls

### Software Requirements
- **Python**: 3.11 or higher
- **Node.js**: 18.x or higher
- **Docker**: 24.x or higher
- **Docker Compose**: 2.x or higher
- **PostgreSQL**: 15.x or higher
- **Redis**: 7.x or higher

### API Keys Required
- OpenAI API Key (GPT-4 access)
- LangSmith API Key (optional, for tracing)

## Local Development Setup

### 1. Clone Repository

```bash
git clone <repository-url>
cd Enterprise-Digital-COO
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env with your configuration
nano .env
```

### 3. Environment Configuration

Create `.env` file in backend directory:

```env
# Application
APP_NAME=Enterprise Digital COO
APP_VERSION=1.0.0
DEBUG=True
ENVIRONMENT=development

# API
API_V1_PREFIX=/api/v1
HOST=0.0.0.0
PORT=8000

# Security
SECRET_KEY=your-secret-key-change-in-production-use-openssl-rand-hex-32
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database - PostgreSQL
POSTGRES_USER=coo_user
POSTGRES_PASSWORD=secure_password_here
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=enterprise_coo

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# ChromaDB
CHROMA_HOST=localhost
CHROMA_PORT=8001
CHROMA_PERSIST_DIRECTORY=./chroma_data

# OpenAI
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_MODEL=gpt-4
OPENAI_EMBEDDING_MODEL=text-embedding-ada-002
OPENAI_TEMPERATURE=0.7
OPENAI_MAX_TOKENS=2000

# LangSmith (Optional)
LANGCHAIN_TRACING_V2=false
LANGCHAIN_API_KEY=
LANGCHAIN_PROJECT=enterprise-digital-coo

# CORS
CORS_ORIGINS=["http://localhost:3000","http://localhost:8000"]
```

### 4. Database Setup

```bash
# Start PostgreSQL (if using Docker)
docker run -d \
  --name postgres-coo \
  -e POSTGRES_USER=coo_user \
  -e POSTGRES_PASSWORD=secure_password_here \
  -e POSTGRES_DB=enterprise_coo \
  -p 5432:5432 \
  postgres:15

# Run migrations
alembic upgrade head

# Seed initial data (optional)
python scripts/seed_data.py
```

### 5. Redis Setup

```bash
# Start Redis (if using Docker)
docker run -d \
  --name redis-coo \
  -p 6379:6379 \
  redis:7-alpine
```

### 6. ChromaDB Setup

```bash
# ChromaDB will auto-initialize on first run
# Or start as separate service:
docker run -d \
  --name chromadb-coo \
  -p 8001:8000 \
  -v ./chroma_data:/chroma/chroma \
  chromadb/chroma:latest
```

### 7. Start Backend

```bash
# Development mode with auto-reload
python main.py

# Or using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 8. Frontend Setup

```bash
# Navigate to frontend directory
cd ../frontend

# Install dependencies
npm install

# Create .env file
cp .env.example .env

# Edit .env
nano .env
```

Frontend `.env`:

```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000
REACT_APP_VERSION=1.0.0
```

### 9. Start Frontend

```bash
# Development mode
npm start

# Build for production
npm run build
```

## Docker Deployment

### 1. Docker Compose Setup

Create `docker-compose.yml` in project root:

```yaml
version: '3.8'

services:
  # PostgreSQL Database
  postgres:
    image: postgres:15
    container_name: coo-postgres
    environment:
      POSTGRES_USER: coo_user
      POSTGRES_PASSWORD: secure_password_here
      POSTGRES_DB: enterprise_coo
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U coo_user"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis Cache
  redis:
    image: redis:7-alpine
    container_name: coo-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # ChromaDB Vector Database
  chromadb:
    image: chromadb/chroma:latest
    container_name: coo-chromadb
    ports:
      - "8001:8000"
    volumes:
      - chroma_data:/chroma/chroma
    environment:
      - IS_PERSISTENT=TRUE

  # Backend API
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: coo-backend
    ports:
      - "8000:8000"
    environment:
      - POSTGRES_HOST=postgres
      - REDIS_HOST=redis
      - CHROMA_HOST=chromadb
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
      chromadb:
        condition: service_started
    volumes:
      - ./backend:/app
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload

  # Frontend
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: coo-frontend
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:8000
      - REACT_APP_WS_URL=ws://localhost:8000
    depends_on:
      - backend
    volumes:
      - ./frontend:/app
      - /app/node_modules

volumes:
  postgres_data:
  redis_data:
  chroma_data:
```

### 2. Backend Dockerfile

Create `backend/Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 3. Frontend Dockerfile

Create `frontend/Dockerfile`:

```dockerfile
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy application code
COPY . .

# Expose port
EXPOSE 3000

# Start application
CMD ["npm", "start"]
```

### 4. Start All Services

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

## Kubernetes Deployment

### 1. Create Namespace

```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: enterprise-coo
```

### 2. PostgreSQL Deployment

```yaml
# k8s/postgres-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
  namespace: enterprise-coo
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15
        ports:
        - containerPort: 5432
        env:
        - name: POSTGRES_USER
          valueFrom:
            secretKeyRef:
              name: coo-secrets
              key: postgres-user
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: coo-secrets
              key: postgres-password
        - name: POSTGRES_DB
          value: enterprise_coo
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
      volumes:
      - name: postgres-storage
        persistentVolumeClaim:
          claimName: postgres-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: postgres
  namespace: enterprise-coo
spec:
  selector:
    app: postgres
  ports:
  - port: 5432
    targetPort: 5432
```

### 3. Backend Deployment

```yaml
# k8s/backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  namespace: enterprise-coo
spec:
  replicas: 3
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: backend
        image: your-registry/coo-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: POSTGRES_HOST
          value: postgres
        - name: REDIS_HOST
          value: redis
        - name: CHROMA_HOST
          value: chromadb
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: coo-secrets
              key: openai-api-key
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
---
apiVersion: v1
kind: Service
metadata:
  name: backend
  namespace: enterprise-coo
spec:
  selector:
    app: backend
  ports:
  - port: 8000
    targetPort: 8000
  type: LoadBalancer
```

### 4. Deploy to Kubernetes

```bash
# Create namespace
kubectl apply -f k8s/namespace.yaml

# Create secrets
kubectl create secret generic coo-secrets \
  --from-literal=postgres-user=coo_user \
  --from-literal=postgres-password=secure_password \
  --from-literal=openai-api-key=your-api-key \
  -n enterprise-coo

# Deploy all resources
kubectl apply -f k8s/

# Check status
kubectl get pods -n enterprise-coo

# View logs
kubectl logs -f deployment/backend -n enterprise-coo
```

## Configuration

### Production Settings

Update `.env` for production:

```env
DEBUG=False
ENVIRONMENT=production
SECRET_KEY=<generate-with-openssl-rand-hex-32>
CORS_ORIGINS=["https://your-domain.com"]
```

### Scaling Configuration

```yaml
# k8s/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: backend-hpa
  namespace: enterprise-coo
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: backend
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

## Monitoring

### Prometheus Setup

```yaml
# k8s/prometheus-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
  namespace: enterprise-coo
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
    scrape_configs:
      - job_name: 'backend'
        static_configs:
          - targets: ['backend:8000']
```

### Grafana Dashboards

Import pre-built dashboards:
- FastAPI metrics
- PostgreSQL metrics
- Redis metrics
- Custom COO metrics

## Troubleshooting

### Common Issues

**Issue**: Database connection failed
```bash
# Check PostgreSQL is running
docker ps | grep postgres

# Check connection
psql -h localhost -U coo_user -d enterprise_coo

# View logs
docker logs coo-postgres
```

**Issue**: OpenAI API errors
```bash
# Verify API key
echo $OPENAI_API_KEY

# Test API connection
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

**Issue**: Memory issues
```bash
# Increase Docker memory
# Docker Desktop > Settings > Resources > Memory: 8GB+

# Check container memory
docker stats
```

### Health Checks

```bash
# Backend health
curl http://localhost:8000/health

# Database health
docker exec coo-postgres pg_isready

# Redis health
docker exec coo-redis redis-cli ping
```

### Logs

```bash
# Backend logs
docker logs -f coo-backend

# All services logs
docker-compose logs -f

# Kubernetes logs
kubectl logs -f deployment/backend -n enterprise-coo
```

## Security Checklist

- [ ] Change all default passwords
- [ ] Use strong SECRET_KEY
- [ ] Enable HTTPS/TLS
- [ ] Configure firewall rules
- [ ] Set up API rate limiting
- [ ] Enable audit logging
- [ ] Regular security updates
- [ ] Backup encryption
- [ ] Secrets management (Vault)
- [ ] Network policies (K8s)

## Backup & Recovery

### Database Backup

```bash
# Backup PostgreSQL
docker exec coo-postgres pg_dump -U coo_user enterprise_coo > backup.sql

# Restore
docker exec -i coo-postgres psql -U coo_user enterprise_coo < backup.sql
```

### ChromaDB Backup

```bash
# Backup ChromaDB data
tar -czf chroma_backup.tar.gz ./chroma_data

# Restore
tar -xzf chroma_backup.tar.gz
```

## Performance Tuning

### PostgreSQL

```sql
-- Increase connection pool
ALTER SYSTEM SET max_connections = 200;

-- Optimize for analytics
ALTER SYSTEM SET shared_buffers = '4GB';
ALTER SYSTEM SET effective_cache_size = '12GB';
```

### Redis

```conf
# redis.conf
maxmemory 4gb
maxmemory-policy allkeys-lru
```

### Backend

```python
# Increase worker processes
uvicorn main:app --workers 4 --host 0.0.0.0 --port 8000
```

## Support

For issues and questions:
- GitHub Issues: <repository-url>/issues
- Documentation: <docs-url>
- Email: support@your-domain.com