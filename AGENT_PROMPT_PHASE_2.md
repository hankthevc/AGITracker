# 🤖 Agent Prompt: AGI Tracker Phase 2 Implementation

**Date**: October 28, 2025  
**Context**: Phase 1 (Foundation) complete - Production-ready with events, timeline, AI analysis  
**Task**: Implement Phase 2 automation, intelligence, and advanced features  
**Estimated Time**: 60-80 hours of agent work across 8 sprints

---

## 📋 Your Mission

You are implementing Phase 2 of the AGI Signpost Tracker, building upon a production-ready foundation. Your goal is to transform this from a manually-operated dashboard into a fully automated, intelligent AGI progress tracking system.

**What's Already Working:**
- ✅ Backend API deployed on Railway: https://agi-tracker-api-production.up.railway.app
- ✅ Frontend deployed on Vercel: https://agi-tracker.vercel.app
- ✅ Database: PostgreSQL on Neon with pgvector extension
- ✅ Core features: Events display, timeline visualization, AI analysis
- ✅ 10 real AI events from Sept-Dec 2024 ingested
- ✅ Golden set testing framework in place

**Your Task:**
Work through all sprints in `AGENT_TASKS_PHASE_2.md` to add:
1. Production automation (Celery workers, automated ingestion)
2. Intelligence features (LLM predictions, mapper improvements)
3. Data quality (retractions, credibility tracking)
4. Advanced features (live scraping, weekly digests, chatbot)
5. Security & compliance (API keys, GDPR)
6. Performance optimization (query caching, pagination)
7. UX enhancements (search, mobile optimization)
8. Scenario explorer (what-if analysis, RAG chatbot)

---

## 🎯 Implementation Strategy

### Phase 2.A: Critical Path (Do First) - Sprints 4-6

**Priority 1**: Sprint 4 - Production Automation (8-10 hours)
- Deploy Celery worker and beat services to Railway
- Enable automated ingestion (arXiv, labs, wire services)
- Add task monitoring dashboard
- Verify 48 hours of zero-touch operation

**Priority 2**: Sprint 6 - Data Quality (7-10 hours)
- Implement retraction monitoring system
- Build source credibility tracking with Wilson scores
- Expand golden set to 50+ examples
- Add CI/CD for mapper testing

**Priority 3**: Sprint 5 - Intelligence (10-12 hours)
- LLM-powered forecast extraction from PDFs
- Improve mapper accuracy to F1 >= 0.80
- Build surprise score dashboard

### Phase 2.B: Feature Expansion (Do Second) - Sprint 7

**Sprint 7**: Advanced Features (8-12 hours)
- Replace fixtures with live news scraping
- Weekly digest generation and email
- Multi-model analysis comparison

### Phase 2.C: Production Hardening (Do Third) - Sprints 8-9

**Sprint 8**: Security & Compliance (5-7 hours)
- API rate limiting and key management
- PII scrubbing and GDPR compliance
- Privacy policy and terms pages

**Sprint 9**: Performance & Scale (5-8 hours)
- Database query optimization
- Frontend performance (Lighthouse >90)
- Cursor-based pagination

### Phase 2.D: Advanced UX (Do Last) - Sprints 10-11

**Sprint 10**: UX Enhancements (6-8 hours)
- Full-text search with PostgreSQL
- Advanced filters and saved searches
- Mobile responsiveness audit

**Sprint 11**: Scenario Explorer (10-15 hours)
- What-if scenario builder
- RAG-powered AI analyst chatbot
- Vector embeddings for semantic search

---

## 🚨 Critical Guidelines (READ FIRST)

### Sacred Rules (NEVER Break These)

**Evidence Tier Policy** (from repo rules):
- ❌ **NEVER** let C/D tier evidence move gauges
- ✅ A-tier → moves gauges directly (peer-reviewed, leaderboards)
- ✅ B-tier → provisional, awaiting A-tier corroboration
- ❌ C/D tier → "if true" only, display but don't score
- ❌ HLE signpost stays `first_class=False` (monitor-only)

**Scoring Math**:
- ❌ **NEVER** change harmonic mean aggregation
- ❌ **NEVER** let single category dominate overall index
- ✅ Cap at 2 signpost links per event (avoid over-linking)

**Development Practices**:
- ✅ **ALWAYS** use Alembic migrations (never raw SQL DDL)
- ✅ **ALWAYS** commit after each subtask (small, verifiable diffs)
- ✅ **ALWAYS** test with fixtures first, live scraping behind env flags
- ✅ **ALWAYS** respect robots.txt and rate limits
- ✅ **ALWAYS** use `IF NOT EXISTS` in migrations (idempotent)

**LLM Budget Management**:
- ✅ Track all OpenAI/Anthropic spend in Redis
- ✅ Daily budget: $20 warning, $50 hard stop
- ✅ Use gpt-4o-mini for routine tasks, gpt-4o only when needed
- ✅ Cache expensive LLM calls (24h TTL minimum)
- ✅ Log all prompts with version tags (e.g., `gpt-4o-mini-2024-07-18/v1`)

---

## 📖 Working Instructions

### Before You Start

1. **Read the full task document**:
   ```bash
   cat AGENT_TASKS_PHASE_2.md
   ```

2. **Verify environment**:
   ```bash
   # Check backend is running
   curl https://agi-tracker-api-production.up.railway.app/health
   
   # Check frontend is live
   curl -I https://agi-tracker.vercel.app
   
   # Check git status
   git status
   
   # Check current commit
   git rev-parse --short HEAD
   ```

3. **Review project structure**:
   ```bash
   # Backend code
   ls -la services/etl/app/
   
   # Frontend code
   ls -la apps/web/app/
   
   # Database migrations
   ls -la infra/migrations/versions/
   ```

### How to Work Through Each Sprint

**For Every Task:**

1. **Read the full task description** in `AGENT_TASKS_PHASE_2.md`
2. **Check what already exists** - Many utilities/helpers may be implemented
3. **Create/modify files** as specified in task
4. **Write tests** for new functionality
5. **Run tests** to verify functionality
6. **Commit with descriptive message** following convention:
   ```
   feat(sprint-X): Brief description of what was added
   
   - Detailed point 1
   - Detailed point 2
   
   Implements Sprint X, Task X.Y from AGENT_TASKS_PHASE_2.md
   ```
7. **Verify** using the success metrics in each task
8. **Document** any manual steps needed in a `MANUAL_STEPS_SPRINT_X.md` file

**For Database Changes:**
```bash
# Always create a migration
cd infra/migrations
alembic revision -m "descriptive_name"

# Edit the migration file with upgrade/downgrade logic
# Use op.execute() with IF NOT EXISTS for idempotency

# Test migration
alembic upgrade head

# Verify
alembic current
```

**For New Celery Tasks:**
```python
# 1. Create task file in services/etl/app/tasks/
# 2. Add task to celery_app.py imports
# 3. Add to beat schedule if needed
# 4. Create test in services/etl/tests/
# 5. Document in MONITORING_SETUP.md
```

**For New Frontend Pages:**
```typescript
// 1. Create page.tsx in apps/web/app/
// 2. Create components in apps/web/components/
// 3. Add to navigation if needed
// 4. Test responsive design
// 5. Verify dark mode works
```

### Testing Strategy

**Backend Testing:**
```bash
cd services/etl
pytest tests/ -v --cov=app --cov-report=term-missing

# Test specific module
pytest tests/test_mapper_accuracy.py -v

# Test with fixtures
pytest tests/ --fixtures-only
```

**Frontend Testing:**
```bash
cd apps/web
npm run lint
npm run type-check
npm run build  # Verify no build errors

# E2E tests (optional, but recommended for critical paths)
npx playwright test
```

**Integration Testing:**
```bash
# Test full pipeline
python3 scripts/test_ingestion_pipeline.py

# Test LLM analysis
python3 - <<'PY'
import sys
sys.path.insert(0, 'services/etl')
from app.tasks.analyze.generate_event_analysis import generate_event_analysis_task
print(generate_event_analysis_task())
PY
```

### Deployment Process

**For Backend Changes:**
```bash
# Railway auto-deploys on push to main
git push origin main

# Wait for deployment (~2-3 minutes)
# Check Railway dashboard or logs

# Verify deployment
curl https://agi-tracker-api-production.up.railway.app/health

# Run migrations if needed (Railway should auto-run)
railway run -s agi-tracker-api alembic upgrade head
```

**For Frontend Changes:**
```bash
# Vercel auto-deploys on push to main
git push origin main

# Wait for deployment (~1-2 minutes)
# Check Vercel dashboard

# Verify deployment
curl -I https://agi-tracker.vercel.app
```

---

## 🛑 When to Stop and Ask for Help

**Automatic Stoppers** (pause and create a `BLOCKED.md` file):

1. **Environment Variables Needed**:
   - If you need to add Railway environment variables (e.g., REDIS_URL, API keys)
   - Document what's needed in `MANUAL_STEPS_SPRINT_X.md`

2. **External Service Setup**:
   - SendGrid/Mailgun for email (Sprint 7.2)
   - Healthchecks.io for cron monitoring (optional)
   - Third-party API keys (Twitter, Reddit for Sprint 13)

3. **Budget Concerns**:
   - If LLM costs will exceed $50/day
   - If you need to increase budget limits
   - If unexpected costs arise

4. **Data Safety**:
   - If migration will delete data
   - If changes affect production scoring
   - If breaking changes to API

5. **Deployment Issues**:
   - If Railway/Vercel deployment fails repeatedly
   - If you need to modify Railway configuration
   - If you need to add new Railway services

**How to Report Blocks**:
```markdown
# BLOCKED.md

## Sprint X.Y: [Task Name]

**Issue**: Brief description of blocker

**What I tried**:
- Attempt 1
- Attempt 2

**What's needed**:
- [ ] Specific action needed from human
- [ ] Estimated time: X minutes

**Files affected**: 
- file1.py
- file2.tsx

**Can continue with other tasks?**: Yes/No
```

---

## 📊 Progress Tracking

### Update Task Document

After completing each task, update `AGENT_TASKS_PHASE_2.md`:
```markdown
- [x] Task 4.1: Deploy Celery Workers ✅ COMPLETE (2 hours)
- [x] Task 4.2: Add Celery Task Monitoring ✅ COMPLETE (1.5 hours)
```

### Create Sprint Summaries

After each sprint, create `SPRINT_X_COMPLETE.md`:
```markdown
# Sprint X Complete: [Name]

**Duration**: X hours
**Commits**: X commits
**Lines Changed**: +XXX, -XXX

## What Was Built
- Feature 1
- Feature 2

## Success Metrics
- [x] Metric 1: achieved
- [x] Metric 2: achieved

## Known Issues
- Issue 1 (non-blocking)

## Next Steps
- Sprint X+1 ready to start
```

### Maintain a Live Progress Log

Create `PHASE_2_PROGRESS.md` and update after each task:
```markdown
# Phase 2 Progress Log

**Started**: [Date]
**Last Updated**: [Date]
**Estimated Completion**: [Date]

## Sprints

### Sprint 4: Production Automation (8-10h estimated)
- [x] 4.1: Celery Workers (2h actual)
- [x] 4.2: Task Monitoring (1.5h actual)
- **Status**: ✅ Complete (3.5h total)

### Sprint 5: Intelligence (10-12h estimated)
- [x] 5.1: Forecast Extraction (4h actual)
- [ ] 5.2: Mapper Improvement (in progress)
- [ ] 5.3: Surprise Dashboard
- **Status**: 🚧 In Progress (40% complete)

...

## Overall Stats
- Sprints complete: 2/11
- Hours spent: 15.5
- Commits: 24
- Tests passing: 156/156
- LLM spend: $12.50/day avg
```

---

## 💰 Budget Management

### LLM Cost Tracking

**Budget Limits**:
- Daily: $50 hard limit (configured in code)
- Monthly target: <$625 (from AGENT_TASKS_PHASE_2.md)

**Cost-Saving Strategies**:
```python
# Use mini for routine tasks
model = "gpt-4o-mini-2024-07-18"  # $0.15/1M input, $0.60/1M output

# Use gpt-4o only for complex reasoning
model = "gpt-4o-2024-08-06"  # $2.50/1M input, $10/1M output

# Cache aggressively
@cache(ttl=86400)  # 24 hours
def expensive_analysis():
    ...

# Batch process
events = get_unanalyzed_events(limit=20)  # Process in batches
```

**Cost Estimates by Sprint**:
- Sprint 4: $0 (no LLM)
- Sprint 5: $10 one-time + $5/day ongoing
- Sprint 6: $2/day
- Sprint 7: $5/day
- Sprint 8-10: $0
- Sprint 11: $10/day (RAG chatbot)

**Monitor Spend**:
```bash
# Check current spend
curl https://agi-tracker-api-production.up.railway.app/v1/admin/llm-budget

# View detailed breakdown
redis-cli GET "llm_budget:daily:$(date +%Y-%m-%d)"
```

### Infrastructure Costs

**Railway** (~$20/month):
- API service: ~$5/mo
- Celery worker: ~$5/mo
- Celery beat: ~$5/mo
- Redis: ~$5/mo

**Other Services**:
- Vercel: Free (hobby tier)
- Neon PostgreSQL: Free (or $19/mo for prod)
- SendGrid: Free tier (100 emails/day) or $15/mo

---

## 🔍 Quality Checklist (Before Each Commit)

### Code Quality
- [ ] Type hints on all Python functions (PEP 484)
- [ ] TypeScript strict mode (no `any` types)
- [ ] Docstrings on public functions (Google style)
- [ ] No `print()` statements (use `logger` instead)
- [ ] No hardcoded secrets (use environment variables)
- [ ] Error handling for all external calls

### Testing
- [ ] New functions have unit tests
- [ ] Tests pass locally (`pytest` for backend, `npm test` for frontend)
- [ ] Coverage doesn't decrease (target: 70%+)
- [ ] Golden set tests still pass (F1 >= 0.75)

### Database
- [ ] Migration has `upgrade()` and `downgrade()`
- [ ] Uses `IF NOT EXISTS` for idempotency
- [ ] Indexes added for new query patterns
- [ ] No data loss in migration

### Performance
- [ ] API endpoints respond in <500ms
- [ ] Database queries use indexes
- [ ] Frontend bundle size not increased >10%
- [ ] LLM calls are cached appropriately

### Documentation
- [ ] README updated if user-facing changes
- [ ] API docs updated if endpoint changes
- [ ] CHANGELOG.md entry for user-visible changes
- [ ] Comments explain *why*, not *what*

---

## 🎯 Sprint-Specific Guidance

### Sprint 4: Production Automation

**Key Files**:
- `services/etl/app/celery_app.py` - Task schedule
- `RAILWAY_DEPLOYMENT.md` - Deployment guide

**Railway Setup** (Manual - Document Needed):
```markdown
## Railway Services Configuration

### Service 1: API (Already exists)
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Service 2: Celery Worker (NEW)
- Repository: Same GitHub repo
- Root directory: `/services/etl`
- Start command: `celery -A app.celery_app worker --loglevel=info`
- Environment variables: Copy all from API service

### Service 3: Celery Beat (NEW)
- Repository: Same GitHub repo
- Root directory: `/services/etl`
- Start command: `celery -A app.celery_app beat --loglevel=info`
- Environment variables: Copy all from API service

### Service 4: Redis (NEW)
- Add from Railway marketplace
- No configuration needed (REDIS_URL auto-created)
```

**Success Metrics**:
- Worker shows "celery@hostname ready" in logs
- Beat shows "Scheduler: Sending due task..." in logs
- Tasks execute on schedule (check logs at scheduled times)
- Events auto-ingest without manual intervention

### Sprint 5: Intelligence

**Key Files**:
- `services/etl/app/tasks/predictions/extract_forecasts.py` - NEW
- `services/etl/app/tasks/news/map_events_to_signposts.py` - Enhance
- `infra/seeds/news_goldset.json` - Expand to 50 examples

**LLM Prompts**:
Store in `services/etl/app/prompts/`:
```
forecast_extraction_v1.txt
event_mapping_v1.txt
surprise_analysis_v1.txt
```

**Golden Set Expansion**:
Need 50+ examples covering:
- All signpost categories (capabilities, agents, inputs, security, governance)
- All evidence tiers (A, B, C, D)
- Multi-signpost events (event maps to 2 signposts)
- Negative cases (event shouldn't map to anything)
- Edge cases (ambiguous wording, similar benchmarks)

### Sprint 6: Data Quality

**Key Files**:
- `services/etl/app/tasks/monitoring/scan_retractions.py` - NEW
- `services/etl/app/utils/statistics.py` - Already has Wilson score
- `.github/workflows/test-mapper.yml` - NEW

**Retraction Sources**:
- Retraction Watch database: http://retractiondatabase.org/
- arXiv withdrawals: Check for "withdrawn" status in metadata
- Publisher corrections: Parse erratum/correction pages

**CI/CD Testing**:
```yaml
# .github/workflows/test-mapper.yml
name: Test Event Mapper

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: cd services/etl && pytest tests/test_mapper_accuracy.py -v
      - name: Check F1 Score
        run: |
          # Fail if F1 < 0.75
          pytest tests/test_mapper_accuracy.py -v | grep "F1:" | awk '{if ($2 < 0.75) exit 1}'
```

### Sprint 7: Advanced Features

**Key Files**:
- `services/etl/app/tasks/news/ingest_arxiv.py` - Remove fixture mode
- `services/etl/app/tasks/digest/generate_digest.py` - NEW
- `services/etl/app/services/email_sender.py` - NEW

**Live Scraping Requirements**:
```python
# Rate limiting
import time
from ratelimit import limits, sleep_and_retry

@sleep_and_retry
@limits(calls=1, period=3)  # 3 seconds between calls
def fetch_arxiv():
    ...

# Robots.txt compliance
from urllib.robotparser import RobotFileParser
rp = RobotFileParser()
rp.set_url("https://export.arxiv.org/robots.txt")
rp.read()
can_fetch = rp.can_fetch("AGITracker/1.0", url)
```

**Email Integration** (SendGrid Example):
```python
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content

def send_digest(to_email: str, html_content: str):
    sg = sendgrid.SendGridAPIClient(api_key=os.environ['SENDGRID_API_KEY'])
    
    message = Mail(
        from_email=Email("digest@agi-tracker.app"),
        to_emails=To(to_email),
        subject="AGI Progress Weekly Digest",
        html_content=Content("text/html", html_content)
    )
    
    response = sg.send(message)
    return response.status_code
```

### Sprint 8: Security & Compliance

**Key Files**:
- `services/etl/app/models.py` - Add APIKey table
- `apps/web/app/legal/privacy/page.tsx` - NEW
- `apps/web/app/legal/terms/page.tsx` - NEW

**API Key Schema**:
```python
class APIKey(Base):
    __tablename__ = "api_keys"
    
    id = Column(UUID, primary_key=True, default=uuid4)
    key_hash = Column(String, unique=True, nullable=False)  # SHA-256 hash
    name = Column(String, nullable=False)
    tier = Column(Enum("public", "authenticated", "admin"), default="public")
    rate_limit = Column(Integer, default=60)  # requests per minute
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used_at = Column(DateTime)
    expires_at = Column(DateTime)
    is_active = Column(Boolean, default=True)
```

**PII Scrubbing** (Already in observability.py, extend):
```python
# Scrub patterns
PII_PATTERNS = [
    (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]'),
    (r'\b\d{3}-\d{2}-\d{4}\b', '[SSN]'),
    (r'\b(?:\d{1,3}\.){3}\d{1,3}\b', '[IP]'),
]

def scrub_pii(text: str) -> str:
    for pattern, replacement in PII_PATTERNS:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text
```

### Sprint 9: Performance & Scale

**Key Files**:
- `infra/migrations/versions/add_performance_indexes.py` - Already exists, verify
- `services/etl/app/main.py` - Add cursor pagination
- `apps/web/next.config.js` - Add bundle analyzer

**Cursor Pagination**:
```python
@app.get("/v1/events")
async def get_events(
    cursor: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    query = db.query(Event).order_by(Event.published_at.desc())
    
    if cursor:
        # Decode cursor (base64 encoded timestamp)
        cursor_date = decode_cursor(cursor)
        query = query.filter(Event.published_at < cursor_date)
    
    events = query.limit(limit + 1).all()
    
    has_more = len(events) > limit
    if has_more:
        events = events[:limit]
        next_cursor = encode_cursor(events[-1].published_at)
    else:
        next_cursor = None
    
    return {
        "events": events,
        "next_cursor": next_cursor,
        "has_more": has_more
    }
```

**Bundle Analysis**:
```javascript
// next.config.js
const withBundleAnalyzer = require('@next/bundle-analyzer')({
  enabled: process.env.ANALYZE === 'true',
})

module.exports = withBundleAnalyzer({
  // ... existing config
})

// Run with: ANALYZE=true npm run build
```

### Sprint 10: UX Enhancements

**Key Files**:
- `services/etl/app/utils/search.py` - NEW (PostgreSQL full-text search)
- `apps/web/components/events/AdvancedFilters.tsx` - NEW
- `apps/web/hooks/useSavedSearches.ts` - NEW

**Full-Text Search** (PostgreSQL):
```python
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import TSVECTOR

# Add to Event model
class Event(Base):
    # ... existing columns
    search_vector = Column(TSVECTOR)

# Create GIN index in migration
op.execute("""
    CREATE INDEX idx_events_search 
    ON events 
    USING GIN(search_vector)
""")

# Update search vector on insert/update
op.execute("""
    CREATE TRIGGER events_search_update 
    BEFORE INSERT OR UPDATE ON events
    FOR EACH ROW EXECUTE FUNCTION
    tsvector_update_trigger(
        search_vector, 'pg_catalog.english', 
        title, summary
    )
""")

# Query
results = db.query(Event).filter(
    Event.search_vector.match("benchmark improvement")
).all()
```

### Sprint 11: Scenario Explorer

**Key Files**:
- `apps/web/app/scenarios/page.tsx` - NEW
- `services/etl/app/services/scenario_simulator.py` - NEW
- `services/etl/app/services/rag_chat.py` - NEW
- `services/etl/app/tasks/embeddings/generate_embeddings.py` - NEW

**Vector Embeddings** (pgvector already installed):
```python
from openai import OpenAI
import numpy as np

client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])

def generate_embedding(text: str) -> list[float]:
    response = client.embeddings.create(
        model="text-embedding-3-small",  # $0.02/1M tokens
        input=text
    )
    return response.data[0].embedding

def find_similar_events(query: str, limit: int = 5) -> list[Event]:
    query_embedding = generate_embedding(query)
    
    # pgvector cosine similarity
    results = db.query(Event).order_by(
        Event.embedding.cosine_distance(query_embedding)
    ).limit(limit).all()
    
    return results
```

**RAG Implementation**:
```python
def answer_question(question: str) -> dict:
    # 1. Generate embedding for question
    query_embedding = generate_embedding(question)
    
    # 2. Find top 5 relevant events
    relevant_events = find_similar_events(question, limit=5)
    
    # 3. Build context
    context = "\n\n".join([
        f"Event: {e.title}\n{e.summary}\nTier: {e.evidence_tier}\nDate: {e.published_at}"
        for e in relevant_events
    ])
    
    # 4. Call LLM with context
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an AI analyst for AGI progress tracking."},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}
        ]
    )
    
    return {
        "answer": response.choices[0].message.content,
        "sources": [e.id for e in relevant_events],
        "confidence": calculate_confidence(relevant_events)
    }
```

---

## 📝 Commit Message Conventions

Use conventional commits format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `refactor`: Code restructuring
- `test`: Adding tests
- `docs`: Documentation changes
- `chore`: Maintenance tasks
- `perf`: Performance improvements

**Examples**:
```
feat(celery): Add automated event ingestion workers

- Deploy Celery worker and beat services to Railway
- Configure scheduled tasks for arXiv, labs, and wire ingestion
- Add task monitoring dashboard at /admin/tasks

Implements Sprint 4.1 from AGENT_TASKS_PHASE_2.md
Closes #42
```

```
fix(mapper): Improve F1 score to 0.82 on golden set

- Add synonym dictionary for benchmark names
- Enhance confidence calculation with tier boosting
- Expand golden set to 50 examples

F1: 0.75 → 0.82
Precision: 0.78 → 0.85
Recall: 0.72 → 0.79

Implements Sprint 5.2 from AGENT_TASKS_PHASE_2.md
```

---

## 🎓 Learning Resources

### AGI Tracker Specific
- **Prime Directive**: See repo-specific rules (evidence-first, A/B tier only, harmonic mean)
- **Architecture**: `docs/AI_CONTEXT.md`
- **Deployment**: `RAILWAY_DEPLOYMENT.md`, `VERCEL_DEPLOYMENT.md`
- **Monitoring**: `MONITORING_SETUP.md`

### Technical References
- **FastAPI**: https://fastapi.tiangolo.com/
- **Celery**: https://docs.celeryq.dev/
- **Next.js**: https://nextjs.org/docs
- **SQLAlchemy**: https://docs.sqlalchemy.org/
- **Alembic**: https://alembic.sqlalchemy.org/
- **Recharts**: https://recharts.org/
- **shadcn/ui**: https://ui.shadcn.com/
- **pgvector**: https://github.com/pgvector/pgvector

### LLM Best Practices
- **OpenAI Cookbook**: https://cookbook.openai.com/
- **Prompt Engineering**: https://platform.openai.com/docs/guides/prompt-engineering
- **Cost Optimization**: https://platform.openai.com/docs/guides/optimization

---

## ✅ Final Checklist (Before Declaring Phase 2 Complete)

### Sprint 4: Production Automation
- [ ] 3 Railway services running (API, worker, beat)
- [ ] Redis connected and working
- [ ] Tasks running on schedule (verify logs)
- [ ] Task monitoring dashboard at /admin/tasks
- [ ] 48 hours of zero manual intervention

### Sprint 5: Intelligence & Predictions
- [ ] LLM extracts predictions from 8 PDFs
- [ ] Mapper F1 >= 0.80 on golden set
- [ ] Surprise score dashboard at /insights/surprises
- [ ] 50+ predictions stored in database

### Sprint 6: Data Quality & Credibility
- [ ] Retraction monitoring active (weekly scans)
- [ ] Source credibility tracked daily
- [ ] Golden set expanded to 50+ examples
- [ ] CI/CD tests running on every PR

### Sprint 7: Advanced Features
- [ ] Live news scraping (no fixtures in prod)
- [ ] Weekly digest emails sending
- [ ] 50+ real events/week ingested
- [ ] Multi-model analysis working

### Sprint 8: Security & Compliance
- [ ] API keys working (create/list/revoke)
- [ ] Privacy policy at /legal/privacy
- [ ] Terms at /legal/terms
- [ ] GDPR compliant (no PII stored)

### Sprint 9: Performance & Scale
- [ ] P95 response time < 100ms
- [ ] Lighthouse score > 90
- [ ] Cursor pagination working
- [ ] Cache hit rate > 70%

### Sprint 10: UX Enhancements
- [ ] Full-text search working
- [ ] Advanced filters functional
- [ ] Mobile responsive (Lighthouse mobile >85)
- [ ] Saved searches working

### Sprint 11: Scenario Explorer
- [ ] What-if scenario builder at /scenarios
- [ ] AI chatbot at /chat
- [ ] Vector embeddings generated
- [ ] RAG responses accurate

### Overall Quality
- [ ] All tests passing (backend + frontend)
- [ ] No linter errors
- [ ] All migrations applied
- [ ] Documentation updated
- [ ] CHANGELOG.md entries for user-facing changes
- [ ] Deployment successful (Railway + Vercel)
- [ ] LLM costs under $20/day average
- [ ] Total costs under $625/month

---

## 🚀 Ready to Begin?

You have everything you need:

1. **Task Document**: `AGENT_TASKS_PHASE_2.md` - Detailed instructions for all 11 sprints
2. **This Prompt**: Comprehensive guidelines, conventions, and guardrails
3. **Working Foundation**: Production-ready Phase 1 system to build upon
4. **Clear Success Metrics**: Each task has specific validation criteria

### Your First Steps:

1. Read `AGENT_TASKS_PHASE_2.md` in full
2. Verify environment (health checks, git status)
3. Start with **Sprint 4.1: Deploy Celery Workers** (highest priority)
4. Work sequentially through sprints
5. Commit frequently with descriptive messages
6. Test thoroughly before moving to next task
7. Create `BLOCKED.md` if you hit a manual step
8. Update progress log after each task

### Success Criteria:

- [ ] All 11 sprints complete
- [ ] All success metrics achieved
- [ ] All tests passing
- [ ] System running autonomously
- [ ] Costs under budget
- [ ] Documentation updated

**Time Estimate**: 60-80 hours of focused work

**Expected Outcome**: World-class AGI progress tracker with full automation, high-quality data, advanced intelligence features, and exceptional UX.

---

## 💬 Communication

### Progress Updates

Create status updates every 4-6 hours of work:

```markdown
# Progress Update: [Date/Time]

## Completed Since Last Update
- [x] Task 4.1: Celery workers deployed
- [x] Task 4.2: Task monitoring added

## In Progress
- [ ] Task 5.1: Forecast extraction (60% complete)

## Blockers
- None currently

## Stats
- Hours worked: 6.5
- Commits: 8
- Tests: 145 passing
- LLM spend today: $3.20

## Next Up
- Complete Task 5.1
- Start Task 5.2 (mapper improvement)
```

### Completion Report

When Phase 2 is complete, create `PHASE_2_COMPLETE.md`:

```markdown
# Phase 2 Complete Report

**Completion Date**: [Date]
**Total Time**: X hours
**Total Commits**: X

## All Sprints Delivered
- ✅ Sprint 4: Production Automation
- ✅ Sprint 5: Intelligence & Predictions
- ✅ Sprint 6: Data Quality & Credibility
- ✅ Sprint 7: Advanced Features
- ✅ Sprint 8: Security & Compliance
- ✅ Sprint 9: Performance & Scale
- ✅ Sprint 10: UX Enhancements
- ✅ Sprint 11: Scenario Explorer

## Success Metrics Achieved
[Copy from final checklist]

## Cost Analysis
- Average LLM spend: $X/day
- Infrastructure: $X/month
- Total Phase 2 cost: $X

## Known Issues
[List any non-blocking issues]

## Recommendations
[Suggestions for Phase 3]

## Demo Links
- Production: https://agi-tracker.vercel.app
- API Docs: https://agi-tracker-api-production.up.railway.app/docs
- Task Dashboard: https://agi-tracker.vercel.app/admin/tasks
- Chat: https://agi-tracker.vercel.app/chat

## Next Phase
Phase 3 could focus on:
- [Suggestions based on learnings]
```

---

## 🎉 Let's Build!

You're now equipped to transform the AGI Tracker from a solid foundation into a world-class, fully automated intelligence system.

**Your mission**: Implement all Phase 2 features while maintaining the sacred principles of evidence-first methodology, transparent scoring, and reproducible results.

**Remember**:
- Evidence tier policy is sacred (A/B moves gauges, C/D never)
- Harmonic mean aggregation is untouchable
- Commit frequently, test thoroughly
- Document blockers clearly
- Stay under budget
- Have fun building the future of AGI progress tracking! 🚀

**BEGIN WITH SPRINT 4.1: Deploy Celery Workers to Railway**

Good luck! 🎯

