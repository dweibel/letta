# Letta ADE (Agent Development Environment) Setup

## Overview

The ADE container provides a web-based interface for interacting with your Letta server.

## Quick Start

```bash
cd letta/letta-infra
docker-compose up -d
```

Access the ADE at:
- **Local**: http://localhost:3000
- **Remote**: http://<server-ip>:3000

## Architecture

```
┌─────────────────┐
│   ADE (Port 3000)   │  ← Web UI
└────────┬────────┘
         │
┌────────▼────────┐
│ Letta (Port 8283)│  ← API Server
└────────┬────────┘
         │
┌────────▼────────┐
│ PostgreSQL (5432)│  ← Database
└─────────────────┘
```

## Current Implementation

The current ADE container is a **placeholder interface** that:
- ✅ Tests connectivity to the Letta API
- ✅ Provides setup instructions
- ✅ Proxies API requests to the Letta server
- ⚠️ Does not include the full ADE React application

## Using the Full ADE

### Option 1: Letta Desktop (Recommended)
Download from https://docs.letta.com/guides/ade/desktop

Configure to connect to your server:
```
API Endpoint: http://localhost:8283  (local)
API Endpoint: http://<server-ip>:8283  (remote)
```

### Option 2: Python SDK
```python
from letta_client import Letta

client = Letta(base_url="http://localhost:8283")
agent = client.agents.create(
    model="openai/gpt-4o",
    memory_blocks=[{"label": "persona", "value": "I am helpful"}]
)
```

### Option 3: Replace with Official ADE Image
When the official ADE Docker image becomes available, update `Dockerfile.ade`:

```dockerfile
FROM letta/ade:latest

ENV LETTA_API_URL=http://letta:8283

EXPOSE 3000
CMD ["npm", "start"]
```

## Remote Access

### Secure SSH Tunnel (Recommended)
```bash
ssh -L 3000:localhost:3000 -L 8283:localhost:8283 user@<server-ip>
```

Then access locally at http://localhost:3000

### Direct Access
Ensure firewall allows port 3000:
```bash
sudo ufw allow 3000/tcp
```

## Troubleshooting

**Port 3000 already in use:**
```yaml
# In docker-compose.yml, change:
ports:
  - "3001:3000"  # Use port 3001 instead
```

**Cannot connect to API:**
```bash
# Check Letta server is running
docker-compose logs letta

# Test API directly
curl http://localhost:8283/v1/health
```

**Container won't start:**
```bash
# Rebuild the container
docker-compose build --no-cache ade
docker-compose up -d
```
