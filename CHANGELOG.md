# Changelog

All notable changes to the AGI Signpost Tracker will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v0.2.1] - 2025-10-15

### Added
- **HLE (Humanity's Last Exam)** benchmark integration as monitor-only with B-tier (Provisional) evidence policy
  - Text-only version (2,500 questions) tracking PhD-level reasoning breadth
  - Two signposts: `hle_text_50` (≥50%) and `hle_text_70` (≥70%)
  - Marked as `first_class=False` to exclude from main composite gauges
  - Dual-source scraping: Scale SEAL (primary) + Artificial Analysis (fallback)
  - Quality notes displayed in UI about Bio/Chem subset label issues

### Improved
- **CI reliability**: Python test execution normalized, artifact uploads non-blocking, nightly E2E workflow
- **Observability**: `/health/full` endpoint enriched with per-task watchdog status
- **Request tracing**: `X-Request-ID` header echoed on all API responses including admin endpoints
- **Documentation**: Archived historical planning docs to `docs/archive/` with clear non-authoritative banners

### Fixed
- Admin endpoint canonicalization: `/v1/admin/recompute` is now the canonical route, legacy `/v1/recompute` returns 410 Gone
- Benchmarks UI: HLE tile now shows "Monitor-Only" chip, "Provisional" badge, quality tooltip, and optional version pill

## [v0.2.0] - 2025-10-14

### Added
- **Agentic Benchmarks**: OSWorld, WebArena connectors with Playwright scrapers
- **GPQA Diamond**: Scientific reasoning benchmark connector
- **Inputs OOM Meter**: Training compute milestones (6e25 FLOPs → 1e28+ FLOPs)
- **Security Maturity Aggregator**: Model weight security, deployment controls, incident response tracking
- **AI-2027 Roadmap**: Timeline predictions with structured storage in `roadmap_predictions` table
- **Production Hardening**:
  - HTTP caching with ETags and Redis backend (fastapi-cache2)
  - Rate limiting (slowapi) - 60 req/min default
  - Connector hygiene: robots.txt checks, User-Agent headers, timeout/retry/backoff envelope
  - Sentry integration for error tracking (backend + frontend)
  - Celery Beat task watchdogs with Redis-backed status tracking

### Improved
- **Admin UI**: Claim retraction interface at `/admin` with source and signpost impact warnings
- **Methodology Page**: Comprehensive explanation of scoring logic, evidence tiers, and N/A handling rules
- **Dynamic OG Images**: Auto-generated OpenGraph images for social sharing using `@vercel/og`
- **Structured Logging**: JSON logs with contextual info, PII scrubbing, and request tracing

## [v0.1.0] - 2025-10-13

### Added
- **Core ETL Pipeline**: Feed ingestion, LLM extraction (GPT-4o-mini), entity linking, impact scoring
- **SWE-bench Verified**: First benchmark connector with dual-source scraping (swebench.com + Epoch AI)
- **Composite Gauge**: Multi-preset scoring (Equal, Aschenbrenner, AI-2027) with harmonic mean aggregation
- **Web Dashboard**: Next.js app with real-time gauges, evidence cards, and preset switcher
- **Evidence Tiering**: A/B/C/D credibility system with automatic filtering
- **API**: FastAPI with `/v1/index`, `/v1/signposts`, `/v1/evidence`, `/v1/feed.json` endpoints
- **Testing**: 
  - Python unit tests (pytest) for ETL tasks and scoring logic
  - TypeScript tests (Jest) for scoring library
  - E2E tests (Playwright) for web app
  - Golden set evaluation for mapping quality (F1 ≥ 0.75)

### Infrastructure
- Monorepo with npm workspaces (`/apps/web`, `/services/api`, `/services/etl`, `/packages/*`)
- PostgreSQL with pgvector, Redis for queues and caching
- Docker Compose for local development
- GitHub Actions CI/CD
- Alembic migrations for schema versioning

---

**Legend:**
- `[Added]` - New features
- `[Improved]` - Enhancements to existing features
- `[Fixed]` - Bug fixes
- `[Breaking]` - Breaking changes requiring migration

