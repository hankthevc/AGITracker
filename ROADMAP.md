# AGI Signpost Tracker - Product Roadmap

## Vision

The AGI Signpost Tracker provides the first evidence-based, real-time dashboard for measuring progress toward artificial general intelligence. By tracking measurable signposts across capabilities, agents, inputs, and security domains, we enable researchers, policymakers, and the public to make informed decisions about AI development timelines and risks.

## Differentiator

Unlike prediction markets or expert surveys, we anchor exclusively on verifiable evidence: peer-reviewed papers, official benchmark leaderboards, and lab announcements. Our harmonic mean aggregation prevents cherry-picking—progress requires advancement across *all* domains. We display speculative claims (C/D tier) for transparency but never let them influence our core metrics.

---

## Current State

### ✅ Already Built

- [x] Core index calculation (harmonic mean, 4 categories)
- [x] Evidence tiering system (A/B/C/D with clear policies)
- [x] Signposts catalog (30+ metrics across 4 domains)
- [x] Basic ingestion (arXiv, press, company blogs, social)
- [x] FastAPI backend with caching, rate limiting, CORS
- [x] Next.js web UI with CompositeGauge, LaneProgress, SafetyDial
- [x] PostgreSQL schema with pgvector for semantic search
- [x] Celery task infrastructure for ETL
- [x] Weekly digest generation
- [x] Roadmap predictions tracking (AI2027, Aschenbrenner)
- [x] Changelog API and UI panel
- [x] Docker Compose dev environment
- [x] Playwright E2E tests for critical paths

---

## Phase 0: Foundations (Operations & Data Quality)

**Goal**: Ensure data integrity, prevent duplicates, improve observability.

### Database
- [ ] Add unique constraint on `event_signpost_links(event_id, signpost_id)`
- [ ] Add index on `event_signpost_links(signpost_id, created_at)`
- [ ] Add `events.content_hash` for deduplication (SHA-256 of canonicalized URL + title)
- [ ] Add `created_at` to `event_signpost_links` for link tracking

### Ingestion
- [ ] Create `services/etl/app/utils/fetcher.py` with shared HTTP client (retries, backoff, UA)
- [ ] Add `canonicalize_url()` and `normalize_title()` utilities
- [ ] Update all ingestion tasks to compute `content_hash` before insert
- [ ] Skip duplicates based on `content_hash` or `url` match

### Operations
- [ ] Add `DRY_RUN` config flag for testing without DB writes
- [ ] Enhance `/health/full` to show per-task last success time and queue lag
- [ ] Add task registry for monitoring (Celery inspect integration)

**Acceptance**: Re-ingesting sample data produces zero duplicates; `/health/full` shows task statuses.

---

## Phase 1: Events as First-Class UX + Stored Analysis

**Goal**: Make events discoverable, filterable, and AI-explained. Ship `/events` feed and `/timeline` visualization.

### Backend
- [ ] Create `events_analysis` table (summary, impact timeline, significance score)
- [ ] Add `EventAnalysis` SQLAlchemy model with relationship to `Event`
- [ ] Create `services/etl/app/utils/llm_budget.py` (Redis-based daily budget tracking)
  - Warning at $20/day, hard stop at $50/day
- [ ] Create Celery task `generate_event_analysis` (12h schedule)
  - Query A/B tier events without analysis in last 7 days
  - Call OpenAI gpt-4o-mini with structured prompt
  - Upsert into `events_analysis` table
  - Log cost and prompt version
- [ ] Add API endpoint `GET /v1/events/{id}/analysis`

### Frontend
- [ ] Install Recharts (`npm install recharts`)
- [ ] Create `EventCard` component (shadcn Card + Badge)
  - Expandable "Why this matters" section fetches `/v1/events/{id}/analysis`
  - Tier badges: A=green, B=blue, C=yellow, D=red
  - "Moves gauges" indicator for A/B tier
- [ ] Create `/events` page
  - Filterable list (tier, date range, category, impact level)
  - Search by title/keywords
  - Export to JSON/CSV
  - Pagination (50 per page) + infinite scroll
- [ ] Create `/timeline` page
  - Recharts ScatterChart or custom timeline
  - Horizontal scrollable (desktop), vertical (mobile)
  - Click marker → drawer with EventCard
  - Virtualized for 100+ events

### Tests
- [ ] Pytest: migrations, LLM budget gate, event analysis task
- [ ] Playwright: `/events` filtering, card expansion, pagination

**Acceptance**: 100+ events render smoothly; A/B tier show AI summaries; filtering/search work; timeline is mobile-usable.

---

## Phase 2: Structured Mapping + Calibration + Review Queue

**Goal**: Improve event→signpost mapping quality; enable human-in-the-loop review.

### Mapping Engine
- [ ] LLM-powered signpost mapping with confidence scores
- [ ] Semantic similarity (pgvector) + keyword matching hybrid
- [ ] Calibration: compare predicted relevance vs human labels
- [ ] Auto-reject low-confidence mappings for review

### Review Queue
- [ ] `GET /v1/review/queue` returns events pending approval
- [ ] `POST /v1/review/submit` accepts/rejects mappings
- [ ] Admin UI at `/admin/review` with keyboard shortcuts
- [ ] Track inter-rater agreement for quality metrics

### Data Quality
- [ ] Deduplicate signposts across roadmaps (canonical codes)
- [ ] Backfill missing `published_at` dates via heuristics
- [ ] Flag anomalous claims (e.g., 100x jumps) for review

**Acceptance**: Mapping precision >90% on gold set; review queue clears <30min/day.

---

## Phase 3: Expert Predictions + Forecasts Compare + Tracking Deltas

**Goal**: Compare actual progress vs expert forecasts; quantify surprise/acceleration.

### Predictions Database
- [ ] `expert_predictions` table (source, signpost, date, value, confidence interval)
- [ ] `prediction_accuracy` table (evaluated_at, actual_value, error_magnitude, calibration)
- [ ] Seed predictions from AI2027, Aschenbrenner, Metaculus, prediction markets

### Comparison UI
- [ ] `/roadmaps/compare` page showing ahead/on-track/behind status per signpost
- [ ] Forecast delta charts (predicted vs actual over time)
- [ ] Surprise score: normalized error weighted by confidence
- [ ] Export comparison data for research (CSV/JSON)

### Analytics
- [ ] Aggregate calibration by source (who's most accurate?)
- [ ] Identify "black swan" events (low forecast, high impact)
- [ ] Track velocity: days ahead/behind schedule by category

**Acceptance**: 20+ signposts have forecast comparisons; calibration scores computed monthly.

---

## Phase 4: Pulse Landing + Signpost Deep-Dives + AI Analyst Panel

**Goal**: Engaging narrative landing page; deep-dive educational content per signpost.

### Pulse Landing Page
- [ ] Hero: animated gauge + "X% to AGI" headline
- [ ] This Week's Moves: horizontal carousel of recent A/B events
- [ ] Safety Margin alert banner (if <0)
- [ ] Quick explainer video (90 seconds)
- [ ] CTA: "Explore Timeline" + "Read Methodology"

### Signpost Pages
- [ ] `/signposts/{code}` deep-dive:
  - Why this matters (educational explainer)
  - Current state vs baseline/target
  - Key papers and announcements (curated)
  - Forecast comparison (Phase 3)
  - Evidence timeline with confidence bands
- [ ] Embed related events and entities (orgs, benchmarks)

### AI Analyst Panel
- [ ] LLM-generated weekly narrative (GPT-4 via budget)
- [ ] "What moved this week and why it matters"
- [ ] Multi-perspective: pessimistic/realistic/optimistic framings
- [ ] Store in `weekly_digest` table + serve via API

**Acceptance**: Landing page loads <2s; signpost pages answer "why does this matter?"; weekly digest published automatically.

---

## Phase 5: Credibility + Retractions + Prompt Audit

**Goal**: Handle corrections, track source reliability, audit AI reasoning.

### Retractions Workflow
- [ ] `/v1/admin/retract` endpoint with reason + evidence
- [ ] Retracted events shown with strikethrough + warning
- [ ] Recompute affected index snapshots automatically
- [ ] Changelog entry for all retractions

### Source Credibility
- [ ] Track per-source retraction rate
- [ ] Downgrade sources with >5% retraction rate
- [ ] Display credibility score on event cards
- [ ] Allow community flagging (Phase 6)

### Prompt Audit
- [ ] Store all LLM prompts in `llm_prompts` table (versioned)
- [ ] Link `events_analysis.llm_version` to prompt
- [ ] `/admin/prompts` UI to view/compare prompt versions
- [ ] A/B test prompt variants on accuracy

**Acceptance**: Retractions update gauges within 1 hour; source credibility visible; prompt history auditable.

---

## Phase 6: Scenario Explorer + Multi-Perspective + RAG Chatbot

**Goal**: Interactive "what-if" scenarios; multi-model consensus; Q&A chatbot.

### Scenario Explorer
- [ ] Adjust category weights (custom presets)
- [ ] Hypothetical events: "What if GPT-5 scores 90% on SWE-bench?"
- [ ] Forecast different timelines (optimistic/pessimistic)
- [ ] Export scenarios for reports (PDF/PPTX)

### Multi-Perspective Analysis
- [ ] Run same event through multiple models (GPT-4, Claude, Gemini)
- [ ] Display consensus + outliers
- [ ] Uncertainty quantification (model agreement)
- [ ] Cost optimization (use cheaper models for drafts)

### RAG Chatbot
- [ ] pgvector semantic search over events + signposts
- [ ] `/chat` endpoint with conversation history
- [ ] Grounded responses (cite sources)
- [ ] Detect out-of-scope questions (hallucination guard)

**Acceptance**: Scenario explorer used in 10+ research papers; chatbot answers 80% of questions correctly.

---

## Quick Wins (High Impact, Low Effort)

1. **Mobile PWA**: Add manifest.json + service worker for offline caching
2. **RSS Feed**: `/feed.xml` for A/B tier events
3. **Email Alerts**: Weekly digest + threshold crossing notifications
4. **Dark Mode**: shadcn theming + user preference storage
5. **Keyboard Shortcuts**: J/K navigation, / for search, ? for help
6. **Share Links**: Pre-filled tweets for notable events ("GPT-5 just hit 90% on GPQA!")

---

## Technical Debt

- [ ] Replace fixture-based ingestion with live scrapers (Phase 0 uses fixtures for stability)
- [ ] Add database connection pooling (PgBouncer) for >100 req/s
- [ ] Migrate from Celery Beat to durable scheduler (Temporal or Inngest)
- [ ] Add OpenTelemetry tracing for end-to-end observability
- [ ] Implement row-level security (RLS) for multi-tenancy (if needed)
- [ ] Optimize harmonic mean calculation (cached materialized views)
- [ ] Add CDN for static assets (Cloudflare or Vercel Edge)

---

## Success Criteria

**Phase 1 (Current)**:
- 100+ events render smoothly in <2s
- 90%+ of A/B tier events have AI-generated summaries
- Timeline works on mobile (tested on iPhone SE)
- Filtering/search returns results <500ms
- Zero duplicate events after ingestion runs

**Phase 2**:
- Mapping precision >90% on 100-event gold set
- Human review queue <30 items/day
- Inter-rater agreement >0.85 (Cohen's kappa)

**Phase 3**:
- 20+ signposts tracked vs expert forecasts
- Calibration scores published monthly
- Surprise score identifies 3+ unexpected events/quarter

**Phase 4**:
- Landing page Core Web Vitals: LCP <2s, CLS <0.1, FID <100ms
- Signpost pages answer "why this matters" (user testing: 8/10 clarity)
- Weekly digest opens >40% (email campaigns)

**Phase 5**:
- Retraction workflow <1 hour latency
- Source credibility visible on all events
- Prompt audit used in 2+ research papers

**Phase 6**:
- Scenario explorer in 10+ publications
- Chatbot accuracy >80% on FAQ dataset
- Multi-perspective analysis shows <10% model disagreement

---

## Non-Goals

- **Real-time alerts**: Email/push notifications deferred to Phase 4+
- **User accounts**: No auth required for public dashboard (admin API key only)
- **Predictive modeling**: We track, not forecast (use Metaculus for predictions)
- **Paywalls**: All data CC BY 4.0 (monetization TBD, likely donations/sponsorships)
- **Blockchain integration**: No web3 (evidence lives in Postgres)

---

**Current Phase: Phase 1 – Event Cards & Timeline** 🚧

Next up: Ship `/events` feed with AI summaries + `/timeline` visualization. Target: Q1 2025.

