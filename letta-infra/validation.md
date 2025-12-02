# Letta Infrastructure Validation Guide

Step-by-step validation checklist to ensure your Letta deployment is working correctly.

## Prerequisites Validation

### Step 1: Verify System Requirements

```bash
# Check Docker version (should be 24.0+)
docker --version

# Check Docker Compose version (should be 2.20+)
docker compose version

# Check Git version (should be 2.30+)
git --version

# Verify Docker daemon is running
docker ps
```

**Expected:** All commands return version numbers without errors.

---

## Infrastructure Validation

### Step 2: Verify Repository Structure

```bash
cd letta/letta-infra

# Check required files exist
ls -la .env.example docker-compose.yml Dockerfile.dev

# Verify parent directory has required files
ls -la ../pyproject.toml ../alembic.ini
```

**Expected:** All files exist without "No such file or directory" errors.

### Step 3: Verify Environment Configuration

```bash
# Check .env file exists
test -f .env && echo "✓ .env exists" || echo "✗ .env missing - run: cp .env.example .env"

# Verify API key is set (without exposing the key)
grep -q "OPENAI_API_KEY=sk-" .env && echo "✓ OpenAI API key configured" || echo "✗ API key not set"
```

**Expected:** `.env` file exists with at least one API key configured.

---

## Container Validation

### Step 4: Start Services

```bash
# Start containers in detached mode
docker-compose up -d

# Wait 10 seconds for startup
sleep 10
```

### Step 5: Verify Container Status

```bash
# Check all three containers are running
docker-compose ps

# Expected output should show:
# letta-postgres   running   0.0.0.0:5432->5432/tcp
# letta-server     running   0.0.0.0:8283->8283/tcp
# letta-ade        running   0.0.0.0:3000->3000/tcp
```

**Expected:** All three containers show "running" status.

### Step 6: Check Container Health

```bash
# Verify PostgreSQL health check
docker inspect letta-postgres --format='{{.State.Health.Status}}'

# Expected: "healthy"
```

**Expected:** PostgreSQL reports "healthy" status.

### Step 7: Verify Container Logs

```bash
# Check PostgreSQL logs (should show "ready to accept connections")
docker-compose logs postgres | grep "ready to accept connections"

# Check Letta logs (should show "Running on" without errors)
docker-compose logs letta | tail -20
```

**Expected:** No error messages; Letta server shows startup completion.

---

## Database Validation

### Step 8: Test PostgreSQL Connection

```bash
# Connect to database and verify pgvector extension
docker exec letta-postgres psql -U letta -d letta -c "SELECT version();"

# Verify pgvector extension is available
docker exec letta-postgres psql -U letta -d letta -c "SELECT * FROM pg_extension WHERE extname='vector';"
```

**Expected:** PostgreSQL version displayed; pgvector extension listed.

### Step 9: Verify Database Schema

```bash
# Check Alembic migrations were applied
docker exec letta-postgres psql -U letta -d letta -c "\dt" | grep alembic_version

# List all tables
docker exec letta-postgres psql -U letta -d letta -c "\dt"
```

**Expected:** `alembic_version` table exists; multiple Letta tables present.

---

## API Validation

### Step 10: Test Health Endpoint

```bash
# Test health endpoint
curl -s http://localhost:8283/v1/health

# Expected: {"status":"ok"} or similar health response
```

**Expected:** HTTP 200 response with health status.

### Step 11: Test API Connectivity

```bash
# List available models (requires API key, -L follows redirects)
curl -sL http://localhost:8283/v1/models | jq .

# Expected: JSON array of available models
```

**Expected:** JSON response listing available LLM models.

### Step 12: Verify Port Accessibility

```bash
# Check PostgreSQL port is listening
nc -zv localhost 5432

# Check Letta API port is listening
nc -zv localhost 8283

# Check ADE web UI port is listening
nc -zv localhost 3000
```

**Expected:** All three ports report "succeeded" or "open".

---

## SDK Validation

### Step 13: Test Python SDK Connection

Create a test file `test_connection.py`:

```python
from letta_client import Letta

try:
    client = Letta(base_url="http://localhost:8283")
    
    # Test connection by listing agents
    agents = client.agents.list()
    print(f"✓ SDK connected successfully")
    print(f"  Found {len(agents)} existing agents")
    
except Exception as e:
    print(f"✗ SDK connection failed: {e}")
```

Run the test:

```bash
python test_connection.py
```

**Expected:** "SDK connected successfully" message.

### Step 14: Create Test Agent

```python
from letta_client import Letta

client = Letta(base_url="http://localhost:8283")

# Create a test agent
agent = client.agents.create(
    model="openai/gpt-4o-mini",
    memory_blocks=[
        {"label": "persona", "value": "I am a test agent."}
    ]
)

print(f"✓ Agent created: {agent.id}")

# Send test message
response = client.agents.messages.create(
    agent_id=agent.id,
    messages=[{"role": "user", "content": "Hello, can you hear me?"}]
)

print(f"✓ Agent responded with {len(response.messages)} messages")

# Cleanup
client.agents.delete(agent.id)
print(f"✓ Test agent deleted")
```

**Expected:** Agent creation, message exchange, and deletion all succeed.

---

## Volume Mount Validation

### Step 15: Test Live Code Editing

```bash
# Create a marker file in the mounted directory
touch ../letta/test_marker.txt

# Verify file appears in container
docker exec letta-server ls /app/letta/test_marker.txt

# Cleanup
rm ../letta/test_marker.txt
```

**Expected:** File is visible inside container without rebuild.

---

## Performance Validation

### Step 16: Check Resource Usage

```bash
# View container resource usage
docker stats --no-stream letta-postgres letta-server

# Check disk usage
docker system df
```

**Expected:** Reasonable CPU/memory usage; no excessive disk consumption.

---

## Network Validation

### Step 17: Test Remote Access (if applicable)

From a different machine or terminal:

```bash
# Replace <server-ip> with your server's IP address
curl -s http://<server-ip>:8283/v1/health
```

**Expected:** Health endpoint accessible from remote machine.

### Step 18: Test SSH Tunnel (recommended for remote)

```bash
# From local machine, create SSH tunnel
ssh -L 8283:localhost:8283 user@remote-server

# In another terminal, test connection
curl -s http://localhost:8283/v1/health
```

**Expected:** Health endpoint accessible through tunnel.

---

## Validation Summary

Run this comprehensive check:

```bash
#!/bin/bash
echo "=== Letta Infrastructure Validation ==="
echo ""

# Container status
echo "1. Container Status:"
docker-compose ps | grep -E "(letta-postgres|letta-server|letta-ade)" && echo "✓ Containers running" || echo "✗ Containers not running"
echo ""

# PostgreSQL health
echo "2. PostgreSQL Health:"
docker exec letta-postgres pg_isready -U letta && echo "✓ PostgreSQL ready" || echo "✗ PostgreSQL not ready"
echo ""

# API health
echo "3. API Health:"
curl -sf http://localhost:8283/v1/health > /dev/null && echo "✓ API responding" || echo "✗ API not responding"
echo ""

# Web UI health
echo "4. Web UI Health:"
curl -sf http://localhost:3000 > /dev/null && echo "✓ Web UI responding" || echo "✗ Web UI not responding"
echo ""

# Database tables
echo "5. Database Schema:"
docker exec letta-postgres psql -U letta -d letta -c "\dt" | grep -q "alembic_version" && echo "✓ Migrations applied" || echo "✗ Migrations missing"
echo ""

# Port accessibility
echo "6. Port Accessibility:"
nc -zv localhost 5432 2>&1 | grep -q "succeeded\|open" && echo "✓ PostgreSQL port open" || echo "✗ PostgreSQL port closed"
nc -zv localhost 8283 2>&1 | grep -q "succeeded\|open" && echo "✓ API port open" || echo "✗ API port closed"
nc -zv localhost 3000 2>&1 | grep -q "succeeded\|open" && echo "✓ Web UI port open" || echo "✗ Web UI port closed"
echo ""

echo "=== Validation Complete ==="
```

Save as `validate.sh`, make executable, and run:

```bash
chmod +x validate.sh
./validate.sh
```

---

## Troubleshooting Failed Validations

### If containers won't start:
```bash
docker-compose logs
docker-compose down
docker-compose up --build
```

### If database connection fails:
```bash
docker-compose restart postgres
docker exec letta-postgres pg_isready -U letta
```

### If API doesn't respond:
```bash
docker-compose logs letta
docker-compose restart letta
```

### If migrations fail:
```bash
docker exec -it letta-server alembic upgrade head
```

### Complete reset:
```bash
docker-compose down -v
docker system prune -a
docker-compose up --build
```

---

## Success Criteria

Your deployment is validated when:

- ✓ All three containers are running and healthy
- ✓ PostgreSQL accepts connections and has pgvector extension
- ✓ Database schema is initialized (alembic_version exists)
- ✓ API health endpoint returns 200 OK
- ✓ Web UI is accessible and can connect to API
- ✓ Python SDK can connect and create agents
- ✓ Volume mounts reflect code changes immediately
- ✓ Ports 5432, 8283, and 3000 are accessible

**All checks passing?** Your Letta infrastructure is ready for development! 🚀
