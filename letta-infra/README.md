# Letta Infrastructure - Docker Development Setup

Self-hosted Letta deployment using Docker Compose with source code integration for live development.

## Quick Start

```bash
cd letta/letta-infra
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY=sk-proj-...
docker-compose up
```

**Access:**
- API: http://localhost:8283
- Web UI: http://localhost:3000

## Prerequisites

- Docker Engine 24.0+
- Docker Compose 2.20+
- Git 2.30+
- OpenAI API key (or Anthropic/Groq)

**Verify:**
```bash
docker --version
docker compose version
git --version
```

## Architecture

- **postgres**: PostgreSQL with pgvector extension (ankane/pgvector:v0.5.1)
- **letta**: Alpine-based Python 3.11 application server
- **ade**: Web UI for agent development (nginx on Alpine)
- **Volume mount**: `../letta:/app/letta` for live code editing
- **Data persistence**: `postgres_data` volume

## Common Commands

```bash
# Start (foreground with logs)
docker-compose up

# Start (background)
docker-compose up -d

# Rebuild after Dockerfile changes
docker-compose up --build

# View logs
docker-compose logs -f letta

# Stop containers
docker-compose down

# Stop and delete data
docker-compose down -v

# Check status
docker-compose ps
```

## Development Workflow

1. Edit code in `letta/` directory
2. Changes are reflected immediately (no rebuild)
3. View logs: `docker-compose logs -f letta`
4. If modifying `Dockerfile.dev` or `docker-compose.yml`: `docker-compose up --build`

## Remote Access

The server binds to `0.0.0.0:8283` for network access.

**Direct connection:**
```python
from letta_client import Letta
client = Letta(base_url="http://<remote-ip>:8283")
```

**SSH tunnel (recommended):**
```bash
ssh -L 3000:localhost:3000 -L 8283:localhost:8283 user@remote-server
# Then access:
# - Web UI: http://localhost:3000
# - API: http://localhost:8283
```

## Troubleshooting

**Port conflicts:**
```yaml
# Edit docker-compose.yml
ports:
  - "5433:5432"  # PostgreSQL
  - "8284:8283"  # Letta API
  - "3001:3000"  # ADE Web UI
```

**Database connection issues:**
```bash
docker-compose logs postgres
docker exec letta-postgres pg_isready -U letta
```

**Clear cache and rebuild:**
```bash
docker-compose down
docker system prune -a
docker-compose up --build
```

## Database Operations

**Backup:**
```bash
docker exec letta-postgres pg_dump -U letta letta > backup.sql
```

**Restore:**
```bash
docker exec -i letta-postgres psql -U letta letta < backup.sql
```

**Direct access:**
```bash
docker exec -it letta-postgres psql -U letta -d letta
```

## Security Notes

⚠️ **Default credentials (letta/letta) are for development only**

For production:
1. Change `POSTGRES_USER` and `POSTGRES_PASSWORD` in `docker-compose.yml`
2. Update `LETTA_PG_URI` to match new credentials
3. Use SSH tunnels instead of exposing ports
4. Enable SSL/TLS for database connections

## Documentation

See [infra_instructions.md](./infra_instructions.md) for complete architecture documentation.
