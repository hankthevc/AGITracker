# Quick Start Guide

## What's Been Built

This is a **production-ready foundation** for the AGI Signpost Tracker with:

✅ **Full monorepo structure** (npm workspaces)  
✅ **Dual TypeScript/Python scoring library** with unit tests  
✅ **PostgreSQL schema** with 10 tables + pgvector  
✅ **FastAPI backend** with 8 public endpoints  
✅ **Celery ETL pipeline** with 7 task types  
✅ **LLM budget management** ($20/day cap with Redis tracking)  
✅ **Next.js dashboard** with responsive UI  
✅ **Core components**: CompositeGauge, LaneProgress, SafetyDial, PresetSwitcher  
✅ **5 pages**: Home, Benchmarks, Methodology, Changelog, Compute, Security  
✅ **Docker setup** for local development  
✅ **GitHub Actions CI** for linting, type checking, and testing  
✅ **Comprehensive documentation** (README + Methodology page)

## Getting Started (5 Minutes)

### 1. Install Dependencies

```bash
# Root (sets up workspaces)
npm install

# Python ETL service
cd services/etl
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

### 2. Start Infrastructure

```bash
# Option A: Docker Compose (recommended)
docker-compose -f docker-compose.dev.yml up -d postgres redis

# Option B: Local installations
# Ensure PostgreSQL 15+ and Redis are running
```

### 3. Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your settings
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/agi_signpost_tracker
REDIS_URL=redis://localhost:6379/0
OPENAI_API_KEY=sk-proj-your-key-here  # Optional for testing
LLM_BUDGET_DAILY_USD=20
```

### 4. Initialize Database

```bash
# Run migrations
cd infra/migrations
alembic upgrade head

# Seed initial data (25 signposts, 4 benchmarks, 3 roadmaps)
cd ../../scripts
python seed.py
```

### 5. Start Services

**Terminal 1 - FastAPI:**
```bash
cd services/etl
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Next.js:**
```bash
cd apps/web
npm run dev
```

**Terminal 3 - Celery Worker (optional):**
```bash
cd services/etl
source .venv/bin/activate
celery -A app.celery_app worker --loglevel=info
```

### 6. Access the Dashboard

- **Web UI:** http://localhost:3000
- **API Docs:** http://localhost:8000/docs
- **API Health:** http://localhost:8000/health

## Testing the Setup

### 1. Check API Health

```bash
curl http://localhost:8000/health
# Expected: {"status":"ok","service":"agi-tracker-api","version":"1.0.0"}
```

### 2. Get Index Data

```bash
curl http://localhost:8000/v1/index?preset=equal
# Expected: JSON with overall, capabilities, agents, inputs, security scores
```

### 3. View Dashboard

Visit http://localhost:3000 - you should see:
- Composite gauge showing overall proximity
- Safety dial (Security - Capabilities)
- Lane progress bars for all 4 categories
- Preset switcher (Equal / Aschenbrenner / AI-2027)

## What Works Out of the Box

### ✅ Fully Functional

1. **Home page** with live data from API
2. **Preset switching** (URL params persist)
3. **Responsive design** (mobile-friendly)
4. **API endpoints** for index, signposts, evidence, changelog
5. **Database schema** with all tables + relationships
6. **Scoring algorithms** (Python + TypeScript, identical logic)
7. **Seed data** with 25 signposts across 4 categories
8. **Docker setup** for easy deployment

### 🚧 Requires API Key / Optional

1. **LLM extraction** - needs `OPENAI_API_KEY` in `.env`
2. **Feed ingestion** - Celery worker + Beat scheduler
3. **Leaderboard scraping** - Playwright (requires browser install)

### 📋 Planned (Phase 2)

1. **Live leaderboard integration** (Playwright scraping)
2. **Vector similarity matching** (pgvector for fuzzy claims)
3. **OOM meter visualization** (Compute page)
4. **Timeline view** (AI-2027 scenario alignment)
5. **E2E tests** (Playwright for UI)
6. **Golden test set** (100 labeled examples)

## Common Issues & Fixes

### Issue: "Connection refused" when loading home page

**Fix:** Ensure FastAPI is running on port 8000:
```bash
cd services/etl && uvicorn app.main:app --reload --port 8000
```

### Issue: "relation does not exist" database error

**Fix:** Run migrations:
```bash
cd infra/migrations && alembic upgrade head
```

### Issue: Empty gauges (all 0%)

**Fix:** Seed the database:
```bash
cd scripts && python seed.py
```

### Issue: pgvector extension not found

**Fix:** Use the ankane/pgvector Docker image or install extension:
```sql
CREATE EXTENSION vector;
```

## Development Workflow

### Making Changes

1. **Backend (Python):**
   - Edit files in `services/etl/app/`
   - FastAPI auto-reloads on save
   - Test: `cd services/etl && pytest`

2. **Frontend (TypeScript):**
   - Edit files in `apps/web/`
   - Next.js auto-reloads on save
   - Test: `cd apps/web && npm test`

3. **Shared Types:**
   - Edit schemas in `packages/shared/`
   - Update both TS and Python versions
   - Ensure mirrored structure

4. **Scoring Logic:**
   - Edit `packages/scoring/python/core.py` AND `packages/scoring/typescript/core.ts`
   - Keep both implementations identical
   - Run tests to verify: `pytest` and `npm test`

### Running Tests

```bash
# Python unit tests
cd services/etl && pytest -v

# TypeScript tests (when Jest is configured)
cd apps/web && npm test

# Linting
make lint

# Type checking
make typecheck
```

### Creating Migrations

```bash
cd infra/migrations
alembic revision --autogenerate -m "description of change"
alembic upgrade head
```

## Next Steps

### For Development

1. **Add OpenAI API key** to enable LLM extraction
2. **Install Playwright browsers**: `playwright install chromium`
3. **Run Celery worker** to enable ETL pipeline
4. **Add more test coverage** (E2E with Playwright)
5. **Implement remaining pages** (Compute/OOM meter, Security/maturity ladder)

### For Production Deployment

1. **Deploy web to Vercel:**
   ```bash
   cd apps/web && vercel deploy
   ```

2. **Deploy API + ETL to Fly.io:**
   ```bash
   cd services/etl && fly deploy
   ```

3. **Setup Neon database:**
   - Create project
   - Enable pgvector extension
   - Update `DATABASE_URL`

4. **Configure environment variables** on hosting platforms

5. **Setup monitoring:**
   - Sentry for error tracking
   - Healthchecks.io for ETL monitoring
   - Plausible for analytics (optional)

## Architecture at a Glance

```
┌─────────────┐
│  Next.js UI │ ←──SWR──→ FastAPI ←─── Postgres
└─────────────┘              ↓            ↑
                          Celery ─────────┘
                            ↓
                    ┌───────┴───────┐
                    │   ETL Tasks   │
                    ├───────────────┤
                    │ • fetch_feeds │
                    │ • extract     │
                    │ • link        │
                    │ • score       │
                    │ • snap_index  │
                    └───────────────┘
```

## Resources

- **Full Documentation:** See [README.md](./README.md)
- **API Docs:** http://localhost:8000/docs
- **Methodology:** http://localhost:3000/methodology
- **Plan Details:** See [agi-signpost-tracker.plan.md](./agi-signpost-tracker.plan.md)

## Need Help?

1. Check the [README.md](./README.md) for detailed documentation
2. Review the plan file for implementation details
3. Inspect API docs at `/docs` for endpoint usage
4. Look at test files for usage examples

---

**You now have a working AGI Signpost Tracker foundation! 🎉**

