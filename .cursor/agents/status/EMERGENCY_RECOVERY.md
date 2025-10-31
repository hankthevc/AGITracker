# 🚨 Emergency Recovery Plan

**Issue**: Events endpoint returning 500 after live data ingestion  
**Time**: October 31, 2025, ~8:10 PM Pacific

---

## Immediate Actions for User

### Step 1: Check Sentry for Error Details
You mentioned you have Sentry configured. Check your Sentry dashboard:

1. Go to https://sentry.io
2. Select your AGI Tracker project
3. Look for errors from the last 30 minutes
4. Find the stack trace for `/v1/events` 500 error
5. Share the error message here

**This will tell us exactly what's failing.**

---

### Step 2: Quick Rollback Option (If Needed)

If you want to restore service immediately:

```bash
# Option A: Rollback the ingestion (delete new events)
railway run python3 -c "
from app.database import SessionLocal
from app.models import Event
db = SessionLocal()
# Delete events added today
deleted = db.query(Event).filter(Event.id > 33).delete()
db.commit()
print(f'Deleted {deleted} new events, restored to 33 original')
"
```

```bash
# Option B: Rollback migration 022
cd services/etl
railway run alembic downgrade 20251029_p1_audit_log
railway up --detach
```

---

### Step 3: Most Likely Fix

Based on the warnings during ingestion ("Skipping non-allowlisted publisher: None"), the issue is probably NULL publishers.

**Quick Fix**:
```bash
railway run python3 -c "
from app.database import SessionLocal
from app.models import Event
db = SessionLocal()

# Fix NULL publishers
events = db.query(Event).filter(Event.publisher.is_(None)).all()
for e in events:
    e.publisher = 'Unknown'
db.commit()
print(f'Fixed {len(events)} events with NULL publisher')

# Verify
count = db.query(Event).count()
print(f'Total events now: {count}')
"
```

Then test:
```bash
curl "https://agitracker-production-6efa.up.railway.app/v1/events?limit=5"
```

---

## What I Know So Far

### ✅ Working
- Health endpoint
- Index endpoint  
- Signposts endpoint
- Individual event endpoint (tier=A worked earlier)

### ❌ Broken
- `/v1/events` (no filters)
- `/v1/events` (with most filters)

### 🤔 Clues
- 185 items were skipped during ingestion with "publisher: None" warnings
- Error started immediately after ingestion
- Some endpoints work, suggesting partial issue

---

**Check Sentry first - that will tell us exactly what's wrong!**

Then we can apply the precise fix.


