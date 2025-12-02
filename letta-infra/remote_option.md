<div style="display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; padding: 200px 0 20px 0;">

<div style="font-size: 24px; margin-bottom: 12px;"><strong>Amazon Q</strong></div>
<div style="background: rgba(128, 128, 128, 0.15); border: 1px solid rgba(128, 128, 128, 0.25); border-radius: 8px; padding: 8px; margin: 4px 0; text-align: center;">
<div style="font-size: 14px; margin-bottom: 4px;"><strong>Did you know?</strong></div>
<div>Ask Q to review your code and see results in the code issues panel!</div>
</div>

Select code & ask me to explain, debug or optimize it, or type `/` for quick actions

</div>

---

does this infrastructure include a desktop environment?  If not, what are my options?

---


Based on the README and your infrastructure document, **yes, Letta includes a desktop environment**, but it's **not part of your current Docker infrastructure setup**.

## What Letta Offers:

1. **Letta Desktop** - A fully-local desktop application available for macOS and Windows
2. **Agent Development Environment (ADE)** - A no-code UI for building agents (available as cloud-hosted or self-hosted)
3. **Letta Cloud** - Cloud-hosted version at app.letta.com

## Your Current Infrastructure:

Your Docker setup only includes:
- **API Server** (letta-server container)
- **Database** (postgres container)

This provides the backend API but **no UI/desktop interface**.

## Your Options to Add a Desktop/UI Layer:

### **Option 1: Use Letta Desktop (Recommended for Local Dev)**
Download the native desktop app for Windows/macOS from Letta's website. Point it to your local server:
```python
# Configure desktop app to connect to:
http://localhost:8283
```

### **Option 2: Self-Host the ADE (Web UI)**
Add a third container as mentioned in your "Alternative C":

```yaml
# Add to docker-compose.yml
  ade-frontend:
    image: letta/ade:latest  # (if available)
    container_name: letta-ade
    depends_on:
      - letta
    environment:
      LETTA_API_URL: http://letta:8283
    ports:
      - "3000:3000"
```

Access at: `http://localhost:3000`

### **Option 3: Use Letta Cloud UI**
Point the cloud UI at app.letta.com to your self-hosted server (requires exposing your server or using a tunnel):
```bash
# SSH tunnel for secure access
ssh -L 8283:localhost:8283 user@your-server
```

### **Option 4: Build Custom UI**
Use the Python/TypeScript SDK to build your own interface that connects to `http://localhost:8283`.

## Recommendation:

For your Docker-based development setup, I'd suggest **Option 1 (Letta Desktop)** for the best local experience, or **Option 2 (self-hosted ADE)** if you want everything containerized and accessible via browser.

---

I will be running this setup remotely and using the ADE locally.  However, I want to have a desktop UI at the OS level and development tools to modify the code and rebuild from my local PC with the remote Letta server running on a different computer.

---


Perfect! You want a **remote-local hybrid development workflow**. Here's your setup:

## Architecture Overview

**Remote Server (Linux):**
- Docker containers (Letta server + PostgreSQL)
- Exposed on network for remote access

**Local PC (Windows):**
- Letta Desktop (UI for interacting with agents)
- VS Code or IDE (for code editing)
- Git (for version control and deployment)

## Setup Instructions

### 1. Remote Server Setup

On your remote Linux server:

```bash
# Clone and start services
git clone https://github.com/dweibel/letta.git
cd letta/letta-infra
cp .env.example .env
# Edit .env with your OPENAI_API_KEY
docker-compose up -d
```

**Firewall/Security:**
```bash
# Allow port 8283 (or use SSH tunnel for security)
sudo ufw allow 8283/tcp
```

### 2. Local PC Setup (Windows)

**A. Install Development Tools:**
- **VS Code** with Remote-SSH extension
- **Git for Windows**
- **Letta Desktop** (download from Letta website)

**B. Connect VS Code to Remote Server:**

```json
// .ssh/config
Host letta-server
    HostName <remote-ip>
    User <username>
    Port 22
    IdentityFile ~/.ssh/id_rsa
```

In VS Code: `Ctrl+Shift+P` → "Remote-SSH: Connect to Host" → `letta-server`

**C. Configure Letta Desktop:**

Open Letta Desktop → Settings:
```
API Endpoint: http://<remote-ip>:8283
```

Or use SSH tunnel for security:
```bash
# Run this on your local PC
ssh -L 8283:localhost:8283 user@<remote-ip>

# Then in Letta Desktop:
API Endpoint: http://localhost:8283
```

### 3. Development Workflow

**Edit Code Locally → Deploy to Remote:**

```bash
# On local PC - clone the repo
git clone https://github.com/dweibel/letta.git
cd letta

# Make changes in VS Code locally
# ... edit files ...

# Push to remote
git add .
git commit -m "Your changes"
git push origin your-branch

# SSH into remote server
ssh user@<remote-ip>

# Pull changes and restart
cd letta
git pull
cd letta-infra
docker-compose restart letta
```

**Or use VS Code Remote-SSH (Recommended):**

1. Connect VS Code to remote via SSH
2. Open `/home/user/letta` folder
3. Edit files directly on remote server
4. Changes reflect immediately (due to volume mount)
5. Restart container if needed: `docker-compose restart letta`

### 4. Quick Reference

**Local PC:**
- **Letta Desktop**: Interact with agents via GUI
- **VS Code**: Edit code (either locally or via Remote-SSH)
- **Git**: Version control

**Remote Server:**
- **Docker**: Run Letta server + PostgreSQL
- **Port 8283**: API endpoint

**Connection:**
```bash
# Secure tunnel (recommended)
ssh -L 8283:localhost:8283 -L 5432:localhost:5432 user@<remote-ip>

# Direct access (if firewall allows)
http://<remote-ip>:8283
```

### 5. Rebuild After Code Changes

```bash
# SSH into remote
ssh user@<remote-ip>
cd letta/letta-infra

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

This gives you:
- ✅ Desktop UI on Windows (Letta Desktop)
- ✅ Code editing on Windows (VS Code)
- ✅ Remote execution (Docker on Linux server)
- ✅ Live code updates (volume mount)
- ✅ Secure access (SSH tunnel)