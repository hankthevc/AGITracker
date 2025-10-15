# AGI Signpost Tracker

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

**Evidence-first dashboard tracking proximity to AGI via measurable signposts**

A neutral, reproducible system that ingests AI news and research, maps it to a fused set of AGI signposts drawn from multiple expert roadmaps (Aschenbrenner's Situational Awareness, AI 2027 scenarios, Cotra Bio Anchors), and presents progress through a clean, viral-ready dashboard.

## Vision & Approach

### Operational Definition of AGI (for this product)

We track proximity to AGI via measurable signposts rather than claiming the exact "moment." Our working notion: a general-purpose AI system that can:

1. **Autonomously perform** the majority of economically valuable remote cognitive tasks at median professional quality and cost with oversight-level supervision
2. **Demonstrate strong generalization** across "computer-using" and "reasoning" benchmarks

We operationalize this via thresholds on **four first-class benchmark families:**
- **SWE-bench Verified** (real-world software engineering)
- **OSWorld** (operating system-level tasks)
- **WebArena** (web navigation and interaction)
- **GPQA Diamond** (PhD-level scientific reasoning)

Plus **Inputs** (training compute, algorithmic efficiency) and **Security** posture.

**Monitor-Only Benchmarks:**
- **HLE (Humanity's Last Exam):** PhD-level reasoning breadth benchmark with known label-quality issues in Bio/Chem subsets. Currently B-tier (Provisional). Does not affect main composite until A-tier evidence available.

### Evidence Policy

- **A (Primary):** Peer-reviewed/archived papers, official leaderboards/APIs, model cards with reproducible evals → Directly moves main gauges
- **B (Official Lab):** Lab blog posts/model cards → Provisional, contributes to metrics
- **C (Reputable Press):** Reuters, AP, Bloomberg → Displayed as unverified, does not move main gauges
- **D (Social):** Twitter, Reddit → Displayed as unverified, never moves main gauges

If credible press arrives before leaderboard, we show as provisional and auto-monitor; update once A/B arrives. Full retraction workflow included.

## Architecture

```mermaid
graph TB
    subgraph "Frontend"
        WEB[Next.js App<br/>Tailwind + shadcn/ui]
    end
    
    subgraph "Backend Services"
        API[FastAPI<br/>Public API]
        ETL[Celery Workers<br/>ETL Pipeline]
        BEAT[Celery Beat<br/>Scheduler]
    end
    
    subgraph "Data Layer"
        DB[(PostgreSQL<br/>+ pgvector)]
        REDIS[(Redis<br/>Queue + Cache)]
    end
    
    subgraph "External Sources"
        ARXIV[arXiv RSS]
        LABS[Lab Blogs]
        BOARDS[Leaderboards]
    end
    
    subgraph "Shared Libraries"
        SCORING[Scoring Library<br/>TS + Python]
        SCHEMAS[Type Schemas<br/>Zod + Pydantic]
    end
    
    WEB -->|SWR| API
    BEAT -->|Schedule| ETL
    ETL -->|Fetch| ARXIV
    ETL -->|Fetch| LABS
    ETL -->|Playwright| BOARDS
    ETL -->|LLM Extract| OPENAI[OpenAI API]
    ETL -->|Write| DB
    ETL -->|Queue| REDIS
    API -->|Read| DB
    API -->|Cache| REDIS
    API --> SCORING
    ETL --> SCORING
    API --> SCHEMAS
    ETL --> SCHEMAS
```

### Technology Stack

**Frontend:**
- Next.js 14 (App Router)
- React, TypeScript
- Tailwind CSS + shadcn/ui
- SWR for data fetching
- Zod for schema validation

**Backend:**
- FastAPI (Python 3.11+)
- SQLAlchemy 2.0 + Alembic
- Celery + Redis
- Pydantic v2
- OpenAI SDK (GPT-4o-mini + GPT-4o)
- Playwright (headless browser for leaderboards)

**Database:**
- PostgreSQL 15+ with pgvector extension

**Infrastructure:**
- Docker + docker-compose
- Vercel (web hosting)
- Fly.io (API + ETL)
- Neon (Postgres)

## Repository Structure

```
/Users/HenryAppel/AI Doomsday Tracker/
├── apps/
│   └── web/                    # Next.js frontend
│       ├── app/                # App Router pages
│       ├── components/         # React components
│       ├── hooks/              # Custom hooks
│       └── lib/                # Utilities
├── services/
│   └── etl/                    # FastAPI + Celery backend
│       ├── app/
│       │   ├── main.py         # FastAPI app
│       │   ├── celery_app.py   # Celery configuration
│       │   ├── models.py       # SQLAlchemy models
│       │   └── tasks/          # ETL tasks
│       └── pyproject.toml
├── packages/
│   ├── shared/                 # Cross-language schemas
│   │   ├── typescript/         # Zod schemas
│   │   ├── python/             # Pydantic models
│   │   └── config/             # weights.json presets
│   └── scoring/                # Dual TS/Py scoring logic
│       ├── typescript/
│       └── python/
├── infra/
│   ├── migrations/             # Alembic migrations
│   ├── seeds/                  # Seed data
│   └── docker/                 # Dockerfiles
├── scripts/                    # Utility scripts
│   └── seed.py                 # Database seeding
├── .github/workflows/          # CI/CD
├── docker-compose.dev.yml
├── Makefile
└── README.md
```

## UI Features

### Dashboard Components

- **Overall AGI Proximity Gauge:** Composite harmonic mean of Capabilities and Inputs with "N/A" state when data is insufficient
- **Category Progress Lanes:** Individual progress bars for Capabilities, Agents, Inputs, Security with confidence bands
- **Safety Margin Dial:** Real-time visualization of Security - Capabilities gap
- **Preset Switcher:** Toggle between Equal, Aschenbrenner, and AI-2027 weighting schemes with URL persistence
- **What Moved This Week?:** Changelog panel displaying recent significant index changes with event types and dates
- **Evidence Cards:** Provenance-badged claim displays with A/B/C/D tier indicators, sources, and timestamps

### Data States

- **Loading:** Skeleton screens and spinners during data fetch
- **Error:** Clear error messages with fallback instructions
- **Empty:** Contextual "no data yet" messages with links to methodology
- **Insufficient Data:** "N/A" displays when required categories lack A/B-tier evidence

## Local Development

### Prerequisites

- Node.js 20+
- Python 3.11+
- Docker & Docker Compose
- PostgreSQL 15+ (or use Docker)
- Redis (or use Docker)

### Quick Start

1. **Clone and Bootstrap**

```bash
git clone <repo-url>
cd "AI Doomsday Tracker"
make bootstrap
```

2. **Set Environment Variables**

Copy `.env.example` and configure:

```bash
cp .env.example .env
```

Required variables:
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/agi_signpost_tracker
REDIS_URL=redis://localhost:6379/0
OPENAI_API_KEY=sk-proj-your-key-here
LLM_BUDGET_DAILY_USD=20
```

3. **Start Services with Docker**

```bash
make dev
```

This starts:
- PostgreSQL (port 5432)
- Redis (port 6379)
- FastAPI (port 8000)
- Celery Worker
- Celery Beat
- Next.js Dev Server (port 3000)

4. **Run Migrations & Seed Data**

```bash
make migrate
make seed
```

5. **Access the Dashboard**

- **Web:** http://localhost:3000
- **API Docs:** http://localhost:8000/docs
- **API Health:** http://localhost:8000/health
- **Debug:** http://localhost:3000/_debug

### API Connectivity & Debugging

The web app automatically resolves the API base URL in this order:

1. **`NEXT_PUBLIC_API_URL` environment variable** (set in `.env.local`)
2. **Browser auto-detection** (port 8000 if web is on :3000)
3. **Fallback:** `http://localhost:8000`

**Set custom API URL:**
```bash
# apps/web/.env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Default preset behavior:**
The `/v1/index` endpoint defaults to `preset=equal` if no query param is provided, so calling `/v1/index` without parameters returns valid data.

**CORS Configuration:**
The API CORS middleware is configurable via environment variable:
```bash
# services/etl/.env
CORS_ORIGINS=http://localhost:3000,https://your-frontend.vercel.app
```

**Debugging connectivity issues:**

1. Visit **http://localhost:3000/_debug** to see:
   - Resolved API base URL
   - `/health` and `/health/full` status
   - Sample `/v1/index` response
   - CORS configuration
   - Troubleshooting tips

2. Check browser console for:
   - Network requests (should point to the base URL shown on `/_debug`)
   - CORS errors (ensure `localhost:3000` in API's CORS origins)
   - HTTP status codes and error messages

3. Verify API is running:
   ```bash
   curl http://localhost:8000/health
   # Should return: {"status":"ok","service":"agi-tracker-api","version":"1.0.0"}
   ```

### Development Commands

```bash
# Bootstrap project (install dependencies)
make bootstrap

# Start all services (Docker Compose)
make dev

# Run database migrations
make migrate

# Create new migration
make migrate-create

# Seed database with initial data
make seed

# Run tests
make test

# Run linters
make lint

# Run type checkers
make typecheck

# Run E2E tests
make e2e

# Build for production
make build

# Clean build artifacts
make clean
```

## Data Model

### Core Tables

- **roadmaps:** Preset configurations (Aschenbrenner, AI-2027, Cotra)
- **signposts:** 25 measurable milestones across categories
- **benchmarks:** First-class benchmark definitions
- **sources:** Tracked news sources with credibility tiers
- **claims:** Extracted metrics from sources
- **claim_benchmarks:** Links claims to benchmarks
- **claim_signposts:** Mapping results with fit scores
- **index_snapshots:** Daily computed index values
- **changelog:** Significant changes and retractions
- **weekly_digest:** Weekly summary JSON
- **api_keys:** Admin access control

### Signpost Categories

1. **Capabilities** (8 signposts): SWE-bench, OSWorld, WebArena, GPQA thresholds
2. **Agents** (5 signposts): Reliability, latency, self-improvement, economic impact
3. **Inputs** (7 signposts): Compute (10^26-10^27 FLOP), algorithmic efficiency, DC power
4. **Security** (5 signposts): Maturity levels L1-L3, governance, mandatory evals

## Scoring Methodology

### Signpost Progress

```python
# For increasing metrics (direction: ">=")
progress = (observed - baseline) / (target - baseline)

# For decreasing metrics (direction: "<=")
progress = (baseline - observed) / (baseline - target)

# Clamped to [0, 1]
```

### Category Aggregation

Weighted mean of signpost progresses. First-class signposts receive 2x weight.

### Overall Proximity

```python
overall = 2 / (1/capabilities + 1/inputs)  # Harmonic mean
```

The harmonic mean ensures both dimensions must advance together—bottleneck in either significantly reduces overall score.

**Insufficient Data Gating:** If either Inputs or Security have 0 progress from A/B-tier evidence, the overall index displays as **"N/A – waiting for Inputs/Security"** rather than showing a potentially misleading 0% or undefined value. Category gauges still display their individual progress. This ensures the dashboard doesn't prematurely signal "no progress" when we simply haven't gathered data for a required dimension yet.

### Safety Margin

```python
safety_margin = security - capabilities
```

Negative values (red) indicate capabilities outpacing security readiness.

### Preset Weights

**Equal:** 25% each category

**Aschenbrenner:** Inputs 40%, Agents 30%, Capabilities 20%, Security 10%

**AI-2027:** Agents 35%, Capabilities 30%, Inputs 25%, Security 10%

## ETL Pipeline

### Daily Schedule (Celery Beat)

1. **6:00 AM UTC:** Fetch feeds (arXiv, lab blogs, leaderboards)
2. **7:00 AM UTC:** Compute daily index snapshots
3. **Sunday 8:00 AM UTC:** Generate weekly digest

### Pipeline Stages

1. **fetch_feeds:** Ingest RSS/Atom + Playwright scraping
2. **dedupe_normalize:** Compute URL hashes, drop duplicates
3. **extract_claims:** GPT-4o-mini extraction (fallback to regex)
4. **link_entities:** Map to benchmarks + signposts (deterministic rules + GPT-4o for complex)
5. **score_impact:** Estimate fit_score and impact_estimate
6. **verify_and_tag:** Assign credibility tier (A/B/C/D)
7. **snap_index:** Recompute index with A/B claims only
8. **digest_weekly:** Assemble top 5 deltas

### LLM Budget Management

- **Daily Budget:** $20 USD (configurable via `LLM_BUDGET_DAILY_USD`)
- **Strategy:** GPT-4o-mini for extraction (~$0.30/day), GPT-4o for complex mapping (~$1.50/day)
- **Degradation:** Auto-fallback to cached/rule-based when budget exhausted
- **Tracking:** Redis counter `llm_spend_today_usd`, resets daily

## API Endpoints

### Public (Read-Only)

```
GET /v1/index?date=YYYY-MM-DD&preset=equal
GET /v1/signposts?category=capabilities&first_class=true
GET /v1/signposts/{id}
GET /v1/evidence?signpost_id=1&tier=A&skip=0&limit=50
GET /v1/feed.json                  # CC BY 4.0 public feed
GET /v1/changelog?skip=0&limit=50
GET /health
```

### Admin (Protected by API Key)

```
POST /v1/retract                   # Retract a claim
POST /v1/recompute                 # Trigger index recomputation
```

## Testing

### Unit Tests

```bash
# Python tests
cd services/etl && pytest

# TypeScript tests
cd apps/web && npm test
```

### E2E Tests (Playwright)

```bash
# Run E2E tests (requires API and web server running)
make e2e

# Or manually:
cd apps/web
npm run e2e
```

Test coverage:
- Home page loads and shows composite gauge
- Capabilities gauge shows non-zero value (from SWE-bench)
- Overall gauge shows "N/A" when Inputs/Security are zero, or positive value otherwise
- Preset switcher updates URL and data
- "What Moved This Week?" panel displays recent changelog entries
- Evidence panels show provenance badges (A/B/C/D) with correct testids
- Category progress lanes render with individual values

**Local E2E setup:**
1. Start services: `make dev` (Docker Postgres + Redis)
2. Run migrations: `make migrate`
3. Seed data: `make seed`
4. (Optional) Add dev fixtures: `make seed-dev-fixtures` for non-N/A overall
5. Start API: `cd services/etl && uvicorn app.main:app`
6. Start web: `cd apps/web && npm run dev`
7. Run tests: `cd apps/web && npm run e2e`

### Golden Set Evaluation

`scripts/eval_mapping.py` - Asserts mapping F1 ≥ 0.75 on hand-labeled test set.

## Deployment

### Web (Vercel)

```bash
cd apps/web
vercel deploy
```

Environment variables: `NEXT_PUBLIC_API_URL`

### API + ETL (Fly.io)

```bash
cd services/etl
fly deploy
```

Environment variables: `DATABASE_URL`, `REDIS_URL`, `OPENAI_API_KEY`, `LLM_BUDGET_DAILY_USD`

### Database (Neon)

1. Create Neon project
2. Enable pgvector extension
3. Run migrations: `alembic upgrade head`
4. Seed data: `python scripts/seed.py`

## Observability

- **Sentry:** Error tracking for web + API
- **Structured Logs:** JSON output via `structlog`
- **Healthchecks.io:** Celery Beat pings after each ETL cycle
- **Metrics:** Redis tracking of LLM spend, claims ingested, mapping precision

## Contributing

### Code Style

- **Python:** Ruff (linter), mypy (type checker)
- **TypeScript:** ESLint, Prettier
- **Commit Messages:** Conventional commits

### Pull Requests

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `make test`
5. Run linters: `make lint`
6. Submit PR with clear description

## License

- **Code:** MIT License (or specify your preferred license)
- **Public JSON Feed:** CC BY 4.0
- **Data:** Sources retain their original licenses

## v0.1 Sprint Acceptance Checklist ✅

### Vertical Slice Deliverables

- [x] **SWE-bench-Verified Scraper Working**: Playwright scraper fetches real leaderboard data and creates claims
- [x] **Snapshots Computing with Real Progress**: Capabilities category shows >0% after SWE-bench ingestion
- [x] **E2E Tests Configured**: Playwright E2E tests set up for home page with gauges
- [x] **Unit Tests Passing**: Both Python (pytest) and TypeScript (Jest) scoring tests pass
- [x] **Web UI Displays Real Data**: Dashboard renders composite gauge with actual SWE-bench evidence
- [x] **Documentation Complete**: QUICKSTART.md provides step-by-step local setup instructions
- [x] **Evidence Cards with Tier Badges**: Claims display with A-tier source badges
- [x] **API Endpoints Functional**: `/v1/index`, `/v1/signposts`, `/v1/evidence` all return data
- [x] **Database Migrations Working**: Alembic migrations create all tables with proper constraints
- [x] **Preset Switching Functional**: Equal, Aschenbrenner, AI-2027 presets compute different values

### Technical Validation

- [x] **Harmonic Mean Calculation**: Overall = H(combined_cap, inputs) with zero handling
- [x] **Safety Margin**: security - combined_capabilities displayed correctly
- [x] **Confidence Bands**: Evidence quality affects uncertainty visualization
- [x] **Claim-Signpost Mapping**: `fit_score=1.0` for direct metric matches
- [x] **Impact Estimation**: Delta from baseline normalized to [0,1]
- [x] **Snapshot Persistence**: `(as_of_date, preset)` unique constraint working

## Roadmap

### Current (MVP - v0.1) ✅

- [x] Monorepo structure with npm workspaces
- [x] Database schema + Alembic migrations
- [x] 25 signposts across 4 categories
- [x] Dual TS/Python scoring library
- [x] FastAPI public endpoints
- [x] Celery ETL pipeline with LLM budget
- [x] Next.js dashboard with composite gauge
- [x] Evidence tiers (A/B/C/D)
- [x] Preset switcher (Equal, Aschenbrenner, AI-2027)
- [x] **Playwright scraper for live leaderboards** (SWE-bench)
- [x] **Unit tests** (Python pytest + TypeScript Jest)
- [x] **E2E tests** (Playwright configuration)
- [x] **QUICKSTART.md** documentation

### Phase 2

- [ ] Vector embedding for fuzzy claim matching (pgvector)
- [ ] OOM meter visualization (Compute page)
- [ ] Security maturity ladder visualization
- [ ] Weekly digest email/RSS
- [ ] OpenGraph image generation for social sharing
- [ ] Golden test set (100 labeled examples)
- [ ] Full CI/CD pipeline (GitHub Actions E2E integration)

### Phase 3

- [ ] Timeline view (AI-2027 scenario alignment)
- [ ] Custom preset builder
- [ ] Evidence panel with side sheets
- [ ] Multi-language support
- [ ] Public API rate limiting
- [ ] Admin dashboard for claim review
- [ ] Historical index chart

## Support

- **Documentation:** See `/methodology` page in web app
- **Issues:** GitHub Issues
- **Discussions:** GitHub Discussions
- **Email:** contact@example.com

## Documentation

- **Quickstart:** [QUICKSTART.md](QUICKSTART.md) for local setup
- **Methodology:** See `/methodology` page in web app for scoring details
- **Archive:** Historical planning docs in [docs/archive/](docs/archive/)

## Acknowledgments

Built with insights from:
- Leopold Aschenbrenner's "Situational Awareness" essays
- Cotra Bio Anchors methodology (Epoch)
- AI 2027 scenario frameworks
- Open-source benchmark communities (SWE-bench, OSWorld, WebArena, GPQA)

---

**Made with 🧠 for transparent AGI progress tracking**

