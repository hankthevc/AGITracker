# AGI Signpost Tracker - Quick Start Guide

Get the AGI Tracker running locally in under 10 minutes.

## Prerequisites

- **Docker Desktop** - [Download here](https://www.docker.com/products/docker-desktop/)
- **Node.js 18+** - [Download here](https://nodejs.org/)
- **Python 3.11+** - Included on macOS, or [download here](https://www.python.org/downloads/)

## One-Command Setup

```bash
make dev
```

This will:
1. Start PostgreSQL and Redis containers
2. Run database migrations
3. Seed initial data
4. Start the API server
5. Start the web app
6. Open your browser to http://localhost:3000

## Step-by-Step Setup

If you prefer manual control or the Makefile doesn't work:

### 1. Clone the Repository

```bash
git clone https://github.com/hankthevc/AGITracker.git
cd "AGI Doomsday Tracker"
```

### 2. Install Dependencies

```bash
# Install Node dependencies (monorepo root)
npm install

# Install Python dependencies
cd services/etl
pip install -e .
cd ../..
```

### 3. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and set your API keys (optional for local dev)
# - OPENAI_API_KEY: For LLM-assisted extraction (optional)
# - API_KEY: For admin endpoints (default: "dev-key-change-in-production")
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

### 5. Run Database Migrations

```bash
cd infra/migrations
../../services/etl/.venv/bin/alembic upgrade head
cd ../..
```

### 6. Seed the Database

```bash
cd scripts
../services/etl/.venv/bin/python seed.py
cd ..
```

This will:
- Create 3 roadmap presets (Equal, Aschenbrenner, AI-2027)
- Add 25 signposts (SWE-bench, OSWorld, WebArena, GPQA, Compute, Security)
- Insert 4 benchmarks
- Fetch current leaderboard data (requires internet)

### 7. Install Playwright Browsers (for web scraping)

```bash
cd services/etl
./.venv/bin/playwright install chromium
cd ../..
```

**Note**: If this fails due to network issues, you can retry later. The app will work without it, but the SWE-bench scraper won't function.

### 8. Start the API Server

```bash
cd services/etl
../../services/etl/.venv/bin/uvicorn app.main:app --reload --port 8000
```

Leave this running in one terminal. The API will be available at http://localhost:8000

### 9. Start the Web App

Open a new terminal:

```bash
cd apps/web
npm run dev
```

The web app will start at http://localhost:3000

### 10. Open Your Browser

Navigate to http://localhost:3000 and you should see:
- Composite AGI proximity gauge
- Category progress lanes (Capabilities, Agents, Inputs, Security)
- Safety margin dial
- Preset switcher (Equal / Aschenbrenner / AI-2027)

## Common Issues & Solutions

### Port 5432 Already in Use

If you have PostgreSQL installed locally via Homebrew:

```bash
# Stop local PostgreSQL
brew services stop postgresql@16

# Or if using a different version
brew services list
brew services stop postgresql@<version>
```

### Docker Not Found

1. Install [Docker Desktop](https://www.docker.com/products/docker-desktop/)
2. Open Docker Desktop and wait for it to say "Docker Desktop is running"
3. Verify: `docker ps` should return an empty list or running containers

### Missing Dependencies

```bash
# Re-install Node dependencies
npm install

# Re-install Python dependencies
cd services/etl
pip install -e .
```

### Database Connection Errors

```bash
# Check if containers are running
docker ps

# Should show agi-postgres and agi-redis

# If not running, start them
docker compose -f docker-compose.dev.yml up -d postgres redis

# Check logs
docker logs agi-postgres
docker logs agi-redis
```

### "Module not found" Errors

Ensure you're using the virtual environment Python:

```bash
# Instead of: python seed.py
# Use:
/Users/HenryAppel/AI\ Doomsday\ Tracker/services/etl/.venv/bin/python seed.py
```

## Running Specific Commands

### Fetch Latest SWE-bench Data

```bash
cd services/etl
./.venv/bin/python -c "from app.tasks.fetch_swebench import fetch_swebench; fetch_swebench()"
```

### Manually Recompute Snapshots

```bash
curl -X POST http://localhost:8000/v1/recompute \
  -H "X-API-Key: dev-key-change-in-production"
```

### View API Documentation

Open http://localhost:8000/docs in your browser for interactive Swagger docs.

### Check Database Contents

```bash
# View claims
docker exec -i agi-postgres psql -U postgres -d agi_signpost_tracker \
  -c "SELECT title, metric_value, unit FROM claims ORDER BY id DESC LIMIT 5;"

# View snapshots
docker exec -i agi-postgres psql -U postgres -d agi_signpost_tracker \
  -c "SELECT as_of_date, preset, ROUND(capabilities::numeric, 3) as capabilities FROM index_snapshots;"

# View signposts
docker exec -i agi-postgres psql -U postgres -d agi_signpost_tracker \
  -c "SELECT code, name, category FROM signposts WHERE first_class = true;"
```

## Running Tests

### Unit Tests (Python)

```bash
cd packages/scoring/python
pytest test_core.py -v
```

### Unit Tests (TypeScript)

```bash
cd packages/scoring/typescript
npm test
```

### E2E Tests (Playwright)

```bash
cd apps/web
npx playwright install chromium  # First time only
npm run e2e
```

## Stopping Services

### Stop Web and API

Press `Ctrl+C` in each terminal running the services.

### Stop Docker Containers

```bash
docker compose -f docker-compose.dev.yml down
```

### Or Stop Everything at Once

```bash
# Kill processes on ports 3000 and 8000
lsof -ti:3000,8000 | xargs kill

# Stop Docker
docker compose -f docker-compose.dev.yml down
```

## Next Steps

- **View Methodology**: http://localhost:3000/methodology
- **Check Benchmarks**: http://localhost:3000/benchmarks
- **Try Different Presets**: Click "Aschenbrenner" or "AI-2027" to see different weightings
- **Read the Full Documentation**: See [README.md](README.md)
- **Deploy to Production**: See deployment guides (coming soon)

## Getting Help

- Check the [README](README.md) for architecture details
- View API docs at http://localhost:8000/docs
- Open an issue on [GitHub](https://github.com/hankthevc/AGITracker/issues)

---

**License**: This project's public JSON feed is licensed under CC BY 4.0. See footer for details.
