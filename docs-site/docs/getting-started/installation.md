# Installation

Get the AGI Tracker running locally in under 10 minutes.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Docker Desktop** - [Download here](https://www.docker.com/products/docker-desktop/)
- **Node.js 20+** - [Download here](https://nodejs.org/)
- **Python 3.11+** - Included on macOS, or [download here](https://www.python.org/downloads/)
- **Git** - For cloning the repository

### System Requirements

- **OS**: macOS, Linux, or Windows (with WSL2)
- **RAM**: 4GB minimum, 8GB recommended
- **Disk Space**: 5GB for Docker images and dependencies
- **Network**: Internet connection for downloading dependencies

## Quick Start (One Command)

If you just want to get started fast:

```bash
git clone https://github.com/hankthevc/AGITracker.git
cd "AI Doomsday Tracker"
make dev
```

This single command will:
1. Start PostgreSQL and Redis containers
2. Run database migrations
3. Seed initial data
4. Start the API server (port 8000)
5. Start the web app (port 3000)
6. Open your browser to http://localhost:3000

**That's it!** Skip to [First Steps](/docs/getting-started/first-steps) if this works.

---

## Step-by-Step Installation

If the one-command setup doesn't work, or you prefer manual control, follow these steps:

### 1. Clone the Repository

```bash
git clone https://github.com/hankthevc/AGITracker.git
cd "AI Doomsday Tracker"
```

### 2. Install Dependencies

#### Node.js Dependencies

```bash
# Install monorepo dependencies (root level)
npm install
```

This installs dependencies for:
- Web app (`apps/web`)
- Shared TypeScript packages (`packages/scoring`, `packages/shared`)

#### Python Dependencies

```bash
cd services/etl
pip install -e .
cd ../..
```

Or using a virtual environment (recommended):

```bash
cd services/etl
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .
cd ../..
```

### 3. Configure Environment

```bash
# Copy example environment file
cp .env.example .env
```

Edit `.env` and configure:

```env
# Database (auto-configured for Docker)
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/agi_signpost_tracker

# Redis (auto-configured for Docker)
REDIS_URL=redis://localhost:6379/0

# OpenAI (optional for local dev, required for production)
OPENAI_API_KEY=sk-proj-your-key-here

# LLM Budget (default: $20/day warning, $50/day hard stop)
LLM_BUDGET_DAILY_USD=20

# Admin API Key (change in production!)
API_KEY=dev-key-change-in-production

# CORS Origins (add your frontend URL)
CORS_ORIGINS=http://localhost:3000,https://agi-tracker.vercel.app
```

### 4. Start Database Services

```bash
# Start PostgreSQL with pgvector and Redis
docker compose -f docker-compose.dev.yml up -d postgres redis

# Wait for databases to be ready (about 15-20 seconds)
sleep 20

# Verify they're running
docker ps
```

You should see containers named `agi-postgres` and `agi-redis`.

### 5. Run Database Migrations

```bash
cd infra/migrations
alembic upgrade head
cd ../..
```

This creates all database tables and indexes.

### 6. Seed the Database

```bash
cd scripts
python seed.py
cd ..
```

This seeds:
- 3 roadmap presets (Equal, Aschenbrenner, AI-2027)
- 25+ signposts across 4 categories
- 4 benchmarks (SWE-bench, OSWorld, WebArena, GPQA)
- Sample events and expert predictions

### 7. Install Playwright Browsers

For web scraping leaderboards:

```bash
cd services/etl
playwright install chromium
cd ../..
```

**Note**: This requires ~300MB download. Skip if you don't plan to run scrapers.

### 8. Start the API Server

```bash
cd services/etl
uvicorn app.main:app --reload --port 8000
```

Leave this running in one terminal. API will be at http://localhost:8000

**Verify it's working**:
```bash
curl http://localhost:8000/health
# Should return: {"status":"ok","service":"agi-tracker-api","version":"1.0.0"}
```

### 9. Start the Web App

Open a new terminal:

```bash
cd apps/web
npm run dev
```

The web app will start at http://localhost:3000

### 10. Open Your Browser

Navigate to http://localhost:3000 and you should see:

✅ Composite AGI proximity gauge  
✅ Category progress lanes (Capabilities, Agents, Inputs, Security)  
✅ Safety margin dial  
✅ Preset switcher (Equal / Aschenbrenner / AI-2027)

## Verification Checklist

After installation, verify these endpoints work:

- [ ] **Web App**: http://localhost:3000 (shows dashboard)
- [ ] **API Health**: http://localhost:8000/health (returns `{"status":"ok"}`)
- [ ] **API Docs**: http://localhost:8000/docs (Swagger UI)
- [ ] **Index Endpoint**: http://localhost:8000/v1/index (returns JSON with composite score)
- [ ] **Debug Page**: http://localhost:3000/_debug (shows API connectivity status)

## Troubleshooting

### Port Already in Use

**Error**: `Address already in use: 5432` (or 8000, 3000)

**Solution**:

```bash
# For PostgreSQL (port 5432)
brew services stop postgresql@16

# For API (port 8000)
lsof -ti:8000 | xargs kill

# For web (port 3000)
lsof -ti:3000 | xargs kill
```

### Docker Not Found

**Error**: `docker: command not found`

**Solution**:
1. Install [Docker Desktop](https://www.docker.com/products/docker-desktop/)
2. Open Docker Desktop and wait for it to say "Docker Desktop is running"
3. Retry: `docker ps`

### Database Connection Failed

**Error**: `could not connect to server: Connection refused`

**Solution**:

```bash
# Check if containers are running
docker ps

# If not running, start them
docker compose -f docker-compose.dev.yml up -d postgres redis

# Check logs
docker logs agi-postgres
```

### Module Not Found (Python)

**Error**: `ModuleNotFoundError: No module named 'app'`

**Solution**:

```bash
# Ensure you're using the virtual environment
cd services/etl
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .
```

### Module Not Found (Node.js)

**Error**: `Cannot find module '@/components/...'`

**Solution**:

```bash
# Re-install dependencies
cd apps/web
rm -rf node_modules package-lock.json
npm install
```

## Next Steps

Now that you have the AGI Tracker installed:

1. **Configure**: [Configure Environment Variables](/docs/getting-started/configuration)
2. **Learn**: [Take Your First Steps](/docs/getting-started/first-steps)
3. **Explore**: [Browse User Guides](/docs/guides/events-feed)
4. **Develop**: [Read Architecture Docs](/docs/architecture/overview)

## Need Help?

- Check the [Troubleshooting Guide](/docs/troubleshooting)
- Search [GitHub Issues](https://github.com/hankthevc/AGITracker/issues)
- Ask in [GitHub Discussions](https://github.com/hankthevc/AGITracker/discussions)

