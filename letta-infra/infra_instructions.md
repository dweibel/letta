# **Sovereign Intelligence: Architecting a Fully Dockerized Letta Infrastructure with OpenAI and Alpine Linux**

## **1\. Introduction: Containerized Cognitive Architectures**

As the Letta (formerly MemGPT) framework evolves from a research prototype into a production-grade "LLM OS," deployment strategies must shift towards reproducibility and isolation. A fully containerized approach—encapsulating the application logic, database state, web UI, and runtime environment—ensures a deterministic deployment suitable for both active development and production stability.

This report outlines the architecture for self-hosting Letta using **OpenAI** as the unified intelligence provider. The deployment includes a **three-tier architecture**: web UI (ADE), API server, and database. The application uses **Debian-based Python 3.11** for compatibility with all dependencies, while the database leverages the pre-built **ankane/pgvector** image. The web UI uses **Alpine Linux with nginx** for minimal footprint.

## ---

**2\. Infrastructure Prerequisites**

**Table 1: Host System Requirements**

| Component | Requirement | Architectural Role |
| :---- | :---- | :---- |
| **Docker Engine** | 24.0+ | Runtime for container orchestration. |
| **Docker Compose** | 2.20+ | Orchestrates the multi-container topology (UI \+ Server \+ Database). |
| **Git** | 2.30+ | Required to clone the Letta source code for volume mounting. |
| **OpenAI API Key** | sk-... | Provides both LLM (GPT-4) and Embedding (text-embedding-3) services. |

### **2.1 Verifying Prerequisites**

```bash
docker --version          # Should be 24.0+
docker compose version    # Should be 2.20+
git --version             # Should be 2.30+
```

### **2.2 Windows-Specific Requirements**

- Use **WSL2 backend** for Docker Desktop
- Ensure line endings are **LF** (not CRLF) - configure git:
  ```bash
  git config --global core.autocrlf input
  ```
- Clone repository within WSL2 filesystem for better performance
- The `.env.example` file is pre-configured with LF line endings

## ---

**3\. Repository Management**

```bash
git clone https://github.com/dweibel/letta.git
cd letta/letta-infra
ls -la  # Verify infrastructure files exist
```

## ---

**4\. The Data Layer: Pre-Built pgvector Image**

The `ankane/pgvector:v0.5.1` image includes:
- PostgreSQL with pgvector extension pre-installed
- No compilation required
- Minimal footprint (~200MB)

### **4.1 Database Initialization**

The `init-db.sh` script ensures the pgvector extension is enabled:
```bash
#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE EXTENSION IF NOT EXISTS vector;
EOSQL
```

This script is automatically executed on first database startup via the docker-entrypoint-initdb.d mechanism.

## ---

**5\. The Application Layer: Docker Compose Orchestration**

Docker Compose orchestrates three services: **postgres** (database), **letta** (API server), and **ade** (web UI).

### **5.1 The docker-compose.yml Configuration**

```yaml
services:
  postgres:
    image: ankane/pgvector:v0.5.1
    container_name: letta-postgres
    environment:
      POSTGRES_USER: letta
      POSTGRES_PASSWORD: letta
      POSTGRES_DB: letta
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U letta"]
      interval: 10s
      timeout: 5s
      retries: 3

  letta:
    build:
      context: ..
      dockerfile: letta-infra/Dockerfile.dev
    container_name: letta-server
    depends_on:
      postgres:
        condition: service_healthy
    env_file:
      - .env
    environment:
      LETTA_PG_URI: postgresql://letta:letta@postgres:5432/letta
    volumes:
      - ../letta:/app/letta
    ports:
      - "0.0.0.0:8283:8283"

  ade:
    build:
      context: .
      dockerfile: Dockerfile.ade
    container_name: letta-ade
    depends_on:
      - letta
    environment:
      LETTA_API_URL: http://letta:8283
      VITE_API_URL: http://localhost:8283
    ports:
      - "0.0.0.0:3000:3000"

volumes:
  postgres_data:
```

**Configuration Notes:**

- **Health Check**: Ensures PostgreSQL is ready before starting services
- **Data Persistence**: `postgres_data` volume persists across restarts
- **Volume Mount**: `../letta:/app/letta` enables live code editing
- **Web UI**: ADE container provides browser-based interface

⚠️ **SECURITY WARNING**: Default credentials (letta/letta) are for development only.

## ---

**6\. Configuration: The Unified OpenAI Stack**

Create `.env` file in `letta/letta-infra/`:

```bash
# LLM Provider API Keys
OPENAI_API_KEY=sk-proj-...
ANTHROPIC_API_KEY=
GROQ_API_KEY=

# Local LLM (optional)
# Uncomment and configure if using Ollama
#OLLAMA_BASE_URL=http://host.docker.internal:11434
```

### **6.1 Minimal Setup**

```bash
cd letta/letta-infra
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
docker-compose up
```

**Common Commands:**

```bash
docker-compose up              # Foreground
docker-compose up -d           # Background
docker-compose up --build      # Rebuild
docker-compose down            # Stop
docker-compose down -v         # Stop + delete data
docker-compose logs -f letta   # View API logs
docker-compose logs -f ade     # View UI logs
docker-compose ps              # Check status
```

**Access Points:**
- **Web UI**: http://localhost:3000 (local) or http://\<server-ip\>:3000 (remote)
- **API**: http://localhost:8283 (local) or http://\<server-ip\>:8283 (remote)
- **SSH tunnel** (recommended): `ssh -L 3000:localhost:3000 -L 8283:localhost:8283 user@server`

### **6.2 Verify Installation**

```bash
# Check containers
docker-compose ps

# Test API
curl http://localhost:8283/v1/health

# Test Web UI
curl http://localhost:3000

# Test database
docker exec -it letta-postgres psql -U letta -d letta -c "SELECT version();"
```

### **6.3 Troubleshooting**

**Port conflicts:**
```bash
# Edit docker-compose.yml:
# postgres: "5433:5432"
# letta: "8284:8283"
# ade: "3001:3000"
```

**Database connection refused:**
```bash
docker-compose logs postgres
docker exec letta-postgres pg_isready -U letta
docker-compose restart
```

**Build failures:**
```bash
docker-compose down
docker system prune -a
docker-compose up --build
```

## ---

**7\. Using the System**

### **7.1 Web UI**

Access http://localhost:3000 for:
- API connectivity testing
- Setup instructions
- Links to Letta Desktop

### **7.2 Python SDK**

```python
from letta_client import Letta

client = Letta(base_url="http://localhost:8283")

agent = client.agents.create(
    model="openai/gpt-4o",
    memory_blocks=[{"label": "persona", "value": "I am helpful."}]
)

response = client.agents.messages.create(
    agent_id=agent.id,
    messages=[{"role": "user", "content": "Hello!"}]
)
```

### **7.3 Database Operations**

**Backup:**
```bash
docker exec letta-postgres pg_dump -U letta letta > backup.sql
```

**Restore:**
```bash
docker exec -i letta-postgres psql -U letta letta < backup.sql
```

### **7.4 Development Workflow**

```bash
# Edit files in letta/* directory
# Changes reflected immediately (no rebuild)

# View logs
docker-compose logs -f letta

# Restart service
docker-compose restart letta

# Run migrations
docker exec -it letta-server alembic upgrade head
```

## ---

**8\. The Web UI Layer**

The **ade** container provides a functional web interface built with nginx and Alpine Linux that:
- Tests API connectivity with automatic health checks
- Provides setup instructions and links to Letta Desktop
- Proxies API requests to the Letta server
- Serves a responsive HTML interface on port 3000

### **8.1 ADE Architecture**

The ADE container uses:
- **Base Image**: `node:20-alpine` for minimal footprint
- **Web Server**: nginx for serving static content and proxying API calls
- **Interface**: Single-page HTML application with JavaScript API testing

### **8.2 Using the Full ADE**

For the complete Agent Development Environment, download Letta Desktop from https://docs.letta.com/guides/ade/desktop and configure:
```
API Endpoint: http://localhost:8283
```

## ---

**9\. Multi-Container Alternatives**

### **Alternative A: Job Queue (Celery/Redis)**
Add Redis and Celery worker for async task processing.

### **Alternative B: Monitoring Stack**
Add Prometheus and Grafana for observability.

### **Alternative C: Proxy Layer**
Add LiteLLM or Helicone for token usage monitoring.

## ---

**10\. Conclusion**

This three-tier architecture (UI + API + Database) provides a complete development environment with:
- Browser-based agent interaction via nginx-served web interface
- Live code editing with volume-mounted source code
- Optimized container images (Alpine for UI, Debian for API compatibility)
- Unified OpenAI pipeline with support for multiple LLM providers
- Local and remote access support with configurable port bindings
- Automatic database initialization with pgvector extension

Setup requires just three commands: clone, configure, and run.

#### **Works cited**

1. Letta Docs: Letta Developer Platform, accessed December 1, 2025, https://docs.letta.com/
