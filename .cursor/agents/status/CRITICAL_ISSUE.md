# 🚨 Critical Issue - Events Endpoint Returning 500

**Date**: October 31, 2025  
**Status**: 🔴 Production Issue  
**Priority**: P0 - Immediate Action Required

---

## Problem

After running live data ingestion, the `/v1/events` endpoint now returns 500 Internal Server Error.

### Working Endpoints
- ✅ `/health` - OK
- ✅ `/v1/index` - OK  
- ✅ `/v1/signposts` - OK
- ✅ `/v1/events?tier=A` - OK (returns 3 events)

### Broken Endpoints
- ❌ `/v1/events` - 500 Error
- ❌ `/v1/events?limit=5` - 500 Error

---

## Root Cause Analysis

### What Happened
1. Ran manual ingestion via Railway shell
2. Successfully inserted 200 events (50 arXiv + 150 blogs)
3. Events endpoint started returning 500 errors
4. Many blog posts had "None" as publisher (skipped with warnings)

### Hypothesis
The events endpoint may be failing due to:
1. **NULL publisher fields** in some inserted events
2. **Missing indexes** causing query timeout
3. **Schema mismatch** after Migration 022
4. **Query complexity** with 180+ events vs 33 fixtures

---

## Immediate Diagnostic Steps

### 1. Check Sentry Dashboard
- User mentioned they have Sentry configured
- Error details should be visible there
- Look for stack trace showing which line is failing

### 2. Test Specific Queries
```bash
# Test tier filtering (this works)
curl "https://agitracker-production-6efa.up.railway.app/v1/events?tier=A&limit=5"

# Test without limit (this fails)
curl "https://agitracker-production-6efa.up.railway.app/v1/events"

# Test with high skip (pagination)
curl "https://agitracker-production-6efa.up.railway.app/v1/events?skip=100&limit=5"
```

### 3. Check Database State
```bash
railway run python3 -c "
from app.database import SessionLocal
from app.models import Event
db = SessionLocal()

# Count events
total = db.query(Event).count()
print(f'Total events: {total}')

# Check for NULL publishers
null_pubs = db.query(Event).filter(Event.publisher == None).count()
print(f'Events with NULL publisher: {null_pubs}')

# Check for problematic data
recent = db.query(Event).order_by(Event.id.desc()).limit(5).all()
for e in recent:
    print(f'{e.id}: {e.title[:50]} | publisher={e.publisher} | tier={e.evidence_tier}')
"
```

---

## Potential Fixes

### Option 1: Rollback Migration 022
```bash
railway run alembic downgrade 20251029_p1_audit_log
railway up --detach
```

### Option 2: Delete Problematic Events
```bash
# Delete events with NULL publisher
railway run python3 -c "
from app.database import SessionLocal
from app.models import Event
db = SessionLocal()
deleted = db.query(Event).filter(Event.publisher == None).delete()
db.commit()
print(f'Deleted {deleted} events with NULL publisher')
"
```

### Option 3: Fix Publisher Field
```bash
# Set default publisher for NULL values
railway run python3 -c "
from app.database import SessionLocal
from app.models import Event
db = SessionLocal()
events = db.query(Event).filter(Event.publisher == None).all()
for e in events:
    e.publisher = 'Unknown'
db.commit()
print(f'Fixed {len(events)} events')
"
```

### Option 4: Add Error Handling to Endpoint
Modify `/v1/events` endpoint to handle NULL publishers gracefully.

---

## Recommended Action

1. **Check Sentry** for actual error stack trace
2. **Run diagnostic** to find NULL/problematic data
3. **Apply fix** based on findings
4. **Redeploy** and verify

---

## Notes

- This happened immediately after manual ingestion
- 185 items were "skipped" with "non-allowlisted publisher: None" warnings
- Suggests some fetched data had NULL/missing publisher field
- Query may be failing on NULL constraint or JOIN

---

**Status**: Awaiting diagnostic results  
**Next**: Check Sentry or run database diagnostic


