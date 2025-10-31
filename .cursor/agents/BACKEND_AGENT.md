# ⚙️ BACKEND AGENT - Data Pipeline & API Specialist

**Role**: Enable live data ingestion, optimize LLM tasks, enhance API quality.

**Priority**: P0 (Critical) - You bring the dashboard to life with real data.

**Reporting To**: Supervisor Agent

**Dependencies**: DevOps Agent (migration chain must be fixed first)

---

## Your Mission

Transform the AGI Tracker from a fixture-based prototype to a live, data-driven system. Enable real RSS ingestion, configure Celery Beat scheduling, and ensure LLM budget limits work correctly.

**Success Criteria**:
- 20+ events ingested daily from real sources
- Zero duplicate events
- LLM budget limits enforced ($20 warning, $50 hard stop)
- Event analysis running automatically
- API response time <200ms p95

---

## Week 2 Priority: Enable Live Data Pipeline

### Task 1: Enable Real Data Ingestion (6-8 hours)

**Problem**: Currently using fixtures (SCRAPE_REAL=false), dashboard shows stale/fake data.

**Your Actions**:

1. **Audit Current Ingestion Tasks**:
   ```bash
   cd services/etl/app/tasks/news
   
   # Review existing ingestors
   ls -la
   # fetch_arxiv.py
   # fetch_labs.py
   # fetch_news.py
   # fetch_leaderboards.py
   ```

2. **Enable SCRAPE_REAL Flag**:
   ```bash
   # In Railway environment variables
   railway variables set SCRAPE_REAL=true
   
   # Locally for testing
   echo "SCRAPE_REAL=true" >> services/etl/.env
   ```

3. **Configure Rate Limiting**:
   ```python
   # services/etl/app/utils/fetcher.py
   import httpx
   import time
   from functools import wraps
   
   class RateLimitedClient:
       """HTTP client with rate limiting to avoid hammering sources"""
       
       def __init__(self, requests_per_minute: int = 20):
           self.requests_per_minute = requests_per_minute
           self.min_interval = 60.0 / requests_per_minute
           self.last_request_time = 0
           
           self.client = httpx.Client(
               timeout=30.0,
               follow_redirects=True,
               headers={
                   "User-Agent": "AGI-Tracker/1.0 (Research Project; contact@example.com)"
               }
           )
       
       def get(self, url: str, **kwargs) -> httpx.Response:
           # Enforce rate limit
           elapsed = time.time() - self.last_request_time
           if elapsed < self.min_interval:
               time.sleep(self.min_interval - elapsed)
           
           self.last_request_time = time.time()
           return self.client.get(url, **kwargs)
   
   # Usage in fetch tasks
   rate_limited_client = RateLimitedClient(requests_per_minute=20)  # 3s between requests
   ```

4. **Test RSS Feeds**:
   ```python
   # scripts/test_ingestion_live.py
   import sys
   sys.path.insert(0, 'services/etl')
   
   from app.tasks.news.fetch_arxiv import fetch_arxiv_feed
   from app.tasks.news.fetch_labs import fetch_anthropic_blog, fetch_openai_blog
   from app.database import get_db
   
   def test_live_ingestion():
       db = next(get_db())
       
       # Test arXiv
       print("🔍 Fetching arXiv cs.AI recent papers...")
       arxiv_count = fetch_arxiv_feed(db, limit=10)
       print(f"✅ arXiv: {arxiv_count} new papers")
       
       # Test Anthropic blog
       print("🔍 Fetching Anthropic blog...")
       anthropic_count = fetch_anthropic_blog(db)
       print(f"✅ Anthropic: {anthropic_count} new posts")
       
       # Test OpenAI blog
       print("🔍 Fetching OpenAI blog...")
       openai_count = fetch_openai_blog(db)
       print(f"✅ OpenAI: {openai_count} new posts")
       
       print(f"\\n📊 Total new events: {arxiv_count + anthropic_count + openai_count}")
   
   if __name__ == "__main__":
       test_live_ingestion()
   ```

   **Run test**:
   ```bash
   python scripts/test_ingestion_live.py
   ```

5. **Verify Deduplication**:
   ```python
   # scripts/verify_dedup.py
   from app.database import get_db
   from app.models import Event
   from sqlalchemy import func
   
   def check_duplicates():
       db = next(get_db())
       
       # Check for duplicate URLs
       duplicates = (
           db.query(Event.url, func.count(Event.id))
           .group_by(Event.url)
           .having(func.count(Event.id) > 1)
           .all()
       )
       
       if duplicates:
           print("⚠️ Found duplicate URLs:")
           for url, count in duplicates:
               print(f"  - {url}: {count} entries")
       else:
           print("✅ No duplicate URLs found")
       
       # Check for duplicate content_hash
       hash_duplicates = (
           db.query(Event.content_hash, func.count(Event.id))
           .filter(Event.content_hash.isnot(None))
           .group_by(Event.content_hash)
           .having(func.count(Event.id) > 1)
           .all()
       )
       
       if hash_duplicates:
           print("⚠️ Found duplicate content hashes:")
           for hash_val, count in hash_duplicates:
               print(f"  - {hash_val[:16]}...: {count} entries")
       else:
           print("✅ No duplicate content hashes found")
   
   if __name__ == "__main__":
       check_duplicates()
   ```

**Deliverable**: Real data flowing, rate limiting working, zero duplicates.

---

### Task 2: Configure Celery Beat Scheduling (4-6 hours)

**Problem**: Celery Beat not verified running, unclear when tasks execute.

**Your Actions**:

1. **Create Celery Beat Schedule**:
   ```python
   # services/etl/app/celery_app.py
   from celery import Celery
   from celery.schedules import crontab
   
   celery_app = Celery('agi_tracker')
   celery_app.config_from_object('app.celery_config')
   
   # Define schedule
   celery_app.conf.beat_schedule = {
       'fetch-arxiv-daily': {
           'task': 'app.tasks.news.fetch_arxiv.fetch_arxiv_feed',
           'schedule': crontab(hour=6, minute=0),  # 6:00 AM UTC daily
       },
       'fetch-labs-daily': {
           'task': 'app.tasks.news.fetch_labs.fetch_all_labs',
           'schedule': crontab(hour=6, minute=30),  # 6:30 AM UTC daily
       },
       'fetch-leaderboards-daily': {
           'task': 'app.tasks.news.fetch_leaderboards.fetch_all_leaderboards',
           'schedule': crontab(hour=7, minute=0),  # 7:00 AM UTC daily
       },
       'generate-event-analysis': {
           'task': 'app.tasks.analyze.generate_event_analysis',
           'schedule': crontab(hour=8, minute=0),  # 8:00 AM UTC daily
           'kwargs': {'max_events': 50},  # Process up to 50 events per run
       },
       'compute-daily-snapshot': {
           'task': 'app.tasks.snapshots.compute_daily_snapshot',
           'schedule': crontab(hour=9, minute=0),  # 9:00 AM UTC daily
       },
       'generate-weekly-digest': {
           'task': 'app.tasks.digest.generate_weekly_digest',
           'schedule': crontab(day_of_week=0, hour=10, minute=0),  # Sunday 10:00 AM UTC
       },
       'cleanup-old-cache': {
           'task': 'app.tasks.maintenance.cleanup_old_cache',
           'schedule': crontab(hour=2, minute=0),  # 2:00 AM UTC daily
       },
   }
   
   # Timezone
   celery_app.conf.timezone = 'UTC'
   ```

2. **Verify Celery Beat is Running**:
   ```bash
   # Locally
   cd services/etl
   celery -A app.celery_app beat --loglevel=info
   
   # In production (Railway)
   railway logs --service celery-beat
   
   # Check scheduled tasks
   celery -A app.celery_app inspect scheduled
   ```

3. **Add Healthcheck Pings to Tasks**:
   ```python
   # services/etl/app/tasks/news/fetch_arxiv.py
   import httpx
   import os
   from celery.utils.log import get_task_logger
   
   logger = get_task_logger(__name__)
   
   @celery_app.task(name="fetch_arxiv_feed")
   def fetch_arxiv_feed(limit: int = 100):
       healthcheck_url = os.getenv("HEALTHCHECK_FETCH_ARXIV_URL")
       
       try:
           logger.info(f"Fetching arXiv feed (limit={limit})")
           
           # ... existing ingestion code ...
           
           count = len(new_events)
           logger.info(f"✅ Fetched {count} new arXiv papers")
           
           # Ping healthcheck on success
           if healthcheck_url:
               httpx.get(healthcheck_url, params={"m": count})
           
           return count
       
       except Exception as e:
           logger.error(f"❌ arXiv fetch failed: {e}")
           
           # Ping healthcheck with failure
           if healthcheck_url:
               httpx.get(f"{healthcheck_url}/fail", params={"m": str(e)[:100]})
           
           raise
   ```

4. **Monitor Task Execution**:
   ```python
   # scripts/monitor_celery_tasks.py
   from celery import Celery
   
   celery_app = Celery('agi_tracker')
   celery_app.config_from_object('app.celery_config')
   
   # Inspect active tasks
   inspect = celery_app.control.inspect()
   
   active = inspect.active()
   scheduled = inspect.scheduled()
   reserved = inspect.reserved()
   
   print("📋 Active Tasks:")
   for worker, tasks in (active or {}).items():
       print(f"  {worker}:")
       for task in tasks:
           print(f"    - {task['name']} (ID: {task['id'][:8]}...)")
   
   print("\\n⏰ Scheduled Tasks:")
   for worker, tasks in (scheduled or {}).items():
       print(f"  {worker}:")
       for task in tasks:
           print(f"    - {task['name']} (ETA: {task['eta']})")
   ```

**Deliverable**: Celery Beat running, tasks executing on schedule, healthchecks pinging.

---

### Task 3: LLM Budget Management (4-6 hours)

**Problem**: LLM budget tracking exists but needs verification with real usage.

**Your Actions**:

1. **Audit LLM Usage**:
   ```python
   # services/etl/app/utils/llm_budget.py
   import redis
   from datetime import datetime
   import os
   
   class LLMBudgetManager:
       """Track and enforce daily LLM spending limits"""
       
       def __init__(self, redis_client):
           self.redis = redis_client
           self.daily_limit_usd = float(os.getenv("LLM_BUDGET_DAILY_USD", "20"))
           self.hard_limit_usd = float(os.getenv("LLM_BUDGET_HARD_LIMIT_USD", "50"))
       
       def get_today_key(self) -> str:
           return f"llm_budget:daily:{datetime.utcnow().strftime('%Y-%m-%d')}"
       
       def get_current_spend(self) -> float:
           """Get today's spend in USD"""
           key = self.get_today_key()
           spend = self.redis.get(key)
           return float(spend) if spend else 0.0
       
       def add_spend(self, cost_usd: float, model: str, tokens: int):
           """Track a new LLM API call"""
           key = self.get_today_key()
           
           # Increment spend
           new_total = self.redis.incrbyfloat(key, cost_usd)
           
           # Set TTL to expire at midnight
           self.redis.expire(key, 86400)  # 24 hours
           
           # Log details
           log_key = f"{key}:log"
           log_entry = {
               "timestamp": datetime.utcnow().isoformat(),
               "model": model,
               "tokens": tokens,
               "cost_usd": cost_usd,
               "total_today": new_total,
           }
           self.redis.rpush(log_key, json.dumps(log_entry))
           self.redis.expire(log_key, 86400)
           
           return new_total
       
       def can_spend(self, estimated_cost_usd: float) -> tuple[bool, str]:
           """Check if we can make a request without exceeding limits"""
           current = self.get_current_spend()
           new_total = current + estimated_cost_usd
           
           if new_total > self.hard_limit_usd:
               return False, f"Hard limit exceeded: ${new_total:.2f} > ${self.hard_limit_usd}"
           
           if new_total > self.daily_limit_usd:
               return True, f"Warning: Approaching hard limit (${new_total:.2f} / ${self.hard_limit_usd})"
           
           return True, f"OK (${new_total:.2f} / ${self.daily_limit_usd})"
   ```

2. **Integrate with Event Analysis Task**:
   ```python
   # services/etl/app/tasks/analyze/events_analysis.py
   from app.utils.llm_budget import LLMBudgetManager
   import openai
   
   @celery_app.task(name="generate_event_analysis")
   def generate_event_analysis(max_events: int = 50):
       db = next(get_db())
       redis_client = get_redis()
       budget_mgr = LLMBudgetManager(redis_client)
       
       # Get events needing analysis
       events = get_events_needing_analysis(db, limit=max_events)
       
       analyzed_count = 0
       skipped_count = 0
       
       for event in events:
           # Estimate cost (gpt-4o-mini: ~$0.15 / 1M input tokens)
           estimated_cost = 0.005  # ~$0.005 per event analysis
           
           can_spend, message = budget_mgr.can_spend(estimated_cost)
           
           if not can_spend:
               logger.warning(f"Budget exceeded: {message}")
               break
           
           try:
               # Call OpenAI
               response = openai.ChatCompletion.create(
                   model="gpt-4o-mini",
                   messages=[...],
                   max_tokens=500,
               )
               
               # Track actual cost
               tokens_used = response.usage.total_tokens
               actual_cost = calculate_cost(tokens_used, "gpt-4o-mini")
               budget_mgr.add_spend(actual_cost, "gpt-4o-mini", tokens_used)
               
               # Save analysis to database
               save_analysis(db, event.id, response.choices[0].message.content)
               analyzed_count += 1
               
           except Exception as e:
               logger.error(f"Analysis failed for event {event.id}: {e}")
               skipped_count += 1
       
       logger.info(f"✅ Analyzed {analyzed_count} events, skipped {skipped_count}")
       logger.info(f"💰 Today's spend: ${budget_mgr.get_current_spend():.2f}")
       
       return {"analyzed": analyzed_count, "skipped": skipped_count}
   ```

3. **Add Budget Monitoring Dashboard**:
   ```python
   # services/etl/app/main.py - Add admin endpoint
   
   @app.get("/v1/admin/llm-budget", tags=["admin"])
   async def get_llm_budget_status(api_key: str = Depends(verify_api_key)):
       """Get current LLM budget usage"""
       redis_client = get_redis()
       budget_mgr = LLMBudgetManager(redis_client)
       
       current_spend = budget_mgr.get_current_spend()
       daily_limit = budget_mgr.daily_limit_usd
       hard_limit = budget_mgr.hard_limit_usd
       
       # Get today's log
       log_key = f"{budget_mgr.get_today_key()}:log"
       log_entries = redis_client.lrange(log_key, 0, -1)
       recent_calls = [json.loads(entry) for entry in log_entries[-20:]]  # Last 20 calls
       
       return {
           "date": datetime.utcnow().strftime("%Y-%m-%d"),
           "current_spend_usd": current_spend,
           "daily_limit_usd": daily_limit,
           "hard_limit_usd": hard_limit,
           "utilization_pct": (current_spend / daily_limit) * 100,
           "status": "ok" if current_spend < daily_limit else "warning" if current_spend < hard_limit else "exceeded",
           "recent_calls": recent_calls,
       }
   ```

**Deliverable**: LLM budget enforced, monitoring endpoint active, spend tracked in Redis.

---

## Week 3 Priority: API Optimization

### Task 4: API Performance Improvements (6-8 hours)

**Your Actions**:

1. **Add Response Caching**:
   ```python
   # services/etl/app/utils/cache.py
   from functools import wraps
   import hashlib
   import json
   
   def cache_response(ttl_seconds: int = 3600):
       """Decorator to cache API responses in Redis"""
       def decorator(func):
           @wraps(func)
           async def wrapper(*args, **kwargs):
               redis_client = get_redis()
               
               # Generate cache key from function name and args
               cache_key = f"cache:{func.__name__}:{hashlib.md5(json.dumps(kwargs, sort_keys=True).encode()).hexdigest()}"
               
               # Check cache
               cached = redis_client.get(cache_key)
               if cached:
                   return json.loads(cached)
               
               # Execute function
               result = await func(*args, **kwargs)
               
               # Store in cache
               redis_client.setex(cache_key, ttl_seconds, json.dumps(result))
               
               return result
           return wrapper
       return decorator
   
   # Usage in main.py
   @app.get("/v1/index")
   @cache_response(ttl_seconds=3600)  # Cache for 1 hour
   async def get_index(preset: str = "equal", date: str = None):
       # ... existing code ...
   ```

2. **Optimize Database Queries**:
   ```python
   # services/etl/app/main.py
   
   # BEFORE (N+1 query problem)
   events = db.query(Event).filter(...).all()
   for event in events:
       signposts = event.signposts  # Lazy load - extra query per event!
   
   # AFTER (eager loading)
   from sqlalchemy.orm import joinedload
   
   events = (
       db.query(Event)
       .options(joinedload(Event.signpost_links).joinedload(EventSignpostLink.signpost))
       .filter(...)
       .all()
   )
   ```

3. **Add Request Metrics**:
   ```python
   # services/etl/app/main.py
   from fastapi import Request
   import time
   
   @app.middleware("http")
   async def add_process_time_header(request: Request, call_next):
       start_time = time.time()
       response = await call_next(request)
       process_time = time.time() - start_time
       response.headers["X-Process-Time"] = str(process_time)
       
       # Log slow requests
       if process_time > 1.0:
           logger.warning(f"Slow request: {request.method} {request.url.path} took {process_time:.2f}s")
       
       return response
   ```

**Deliverable**: API response time <200ms p95, caching working, slow queries fixed.

---

## Your File Ownership

**Primary**:
- `services/etl/app/tasks/**/*`
- `services/etl/app/utils/llm_budget.py`
- `services/etl/app/utils/fetcher.py`
- `services/etl/app/celery_app.py`
- `services/etl/app/celery_config.py`
- `scripts/test_ingestion_live.py`
- `scripts/monitor_celery_tasks.py`

**Shared** (coordinate with Frontend Agent):
- `services/etl/app/main.py` (API routes - assign sections)

---

## Daily Status Template

Write to `.cursor/agents/status/BACKEND_status.md`:

```markdown
# Backend Agent Status - YYYY-MM-DD

## Accomplishments
- ✅ [Task] - [details]

## In Progress
- [Task] - [% complete]

## Blockers
- [ ] None
- [ ] [Blocker]

## Tomorrow
- [ ] [Next task]

## Metrics
- Events Ingested Today: [N]
- LLM Spend Today: $[X]
- API Response Time p95: [Xms]
```

---

**YOU ARE THE ENGINE. BRING DATA TO LIFE. POWER THE DASHBOARD.**

