# 🤖 RoutPrompt: Sprint 7 - Advanced Features Implementation

**PriorityMenuHIGH  
**Target BranchMenu`main` (commit directly, no PRs)  
**Estimated Time**: 2-3 hours  
**Context**: Phase 2 production infrastructure is deployed and working on Railway

---

## 🎯 Your Mission

Implement Sprint 7 (Advanced Features) from AGENT_TASKS_PHASE_2.md, focusing on getting real data flowing and adding intelligence features before the Vercel deployment limit resets in ~3 hours.

**Key ConstraintMenuWork on `main` branch directly. Commit after each task completion. NO pull requests, NO feature branches.

---

## ✅ Current State (What's Already Working)

### Infrastructure (Railway - All Active)
- ✅ Redis database running
- ✅ FastAPI backend deployed at: https://api-production-8535.up.railway.app
- ✅ Celery Worker (concurrency=2, 16 tasks loaded)
- ✅ Celery Beat scheduler (running, sending scheduled tasks)
- ✅ PostgreSQL database connected (Neon)

### Features Completed (Sprints 4-6)
- ✅ Task health monitoring (`/v1/admin/tasks/health` + `/admin/tasks` dashboard)
- ✅ Surprise score analysis (`/v1/predictions/surprises` + `/insights/surprises` dashboard)
- ✅ Source credibility tracking (`/v1/admin/source-credibility` + `/admin/sources` dashboard)
- ✅ 50 golden set examples for mapper testing
- ✅ 50+ expert predictions loaded from 8 sources

### What's Working Right Now
- API responding to requests: `{"status":"ok"}`
- Events endpoint returning data with signpost links
- Surprise scores calculated (top surprise: 13.47σ!)
- Interactive API docs at `/docs`
- All 15 scheduled tasks configured and ready

---

## 📋 Tasks to Complete (In Order)

### Task 7.1: Live News Scraping (PRIORITY 1 - 45 min)

**Goal**: Replace dev fixtures with real-time news ingestion from actual APIs

**Current State**:
- Ingestion tasks exist: `services/etl/app/tasks/news/ingest_arxiv.py`, `ingest_company_blogs.py`, etc.
- Currently using fixtures/mock data
- `SCRAPE_REAL=false` in config

**What to do**:

1. **Update arXiv Integration** (`services/etl/app/tasks/news/ingest_arxiv.py`):
   ```python
   # Use arXiv API: http://export.arxiv.org/api/query
   # Query categories: cs.AI, cs.LG, cs.CL
   # Filter for keywords: "AGI", "frontier", "scaling", "benchmark", etc.
   # Parse XML responses
   # Respect rate limit: 3 second delay between requests
   # Store in Event model with evidence_tier="A" (peer-reviewed)
   ```

2. **Update Company Blog RSS** (`ingest_company_blogs.py`):
   ```python
   # Add RSS feeds:
   FEEDS = {
       "OpenAI": "https://openai.com/blog/rss.xml",
       "Anthropic": "https://anthropic.com/news/rss",  
       "DeepMind": "https://deepmind.google/discover/blog/rss.xml",
       "Meta AI": "https://ai.meta.com/blog/rss/",
       # Add more as needed
   }
   # Use feedparser library (already in requirements)
   # Store with evidence_tier="B" (official announcements)
   # Deduplicate by URL
   ```

3. **Update Press Release RSS** (`ingest_press_reuters_ap.py`):
   ```python
   # Add feeds:
   FEEDS = {
       "Reuters AI": "https://www.reuters.com/technology/artificial-intelligence/rss",
       "AP Technology": "https://apnews.com/hub/technology/rss",
   }
   # evidence_tier="C" (press, unverified)
   # Filter for AI-relevant articles
   ```

4. **Update Config**:
   ```python
   # In services/etl/app/config.py
   scrape_real: bool = True  # Change default to True for production
   ```

5. **Add Deduplication**:
   ```python
   # In ingestion tasks, before creating Event:
   existing = db.query(Event).filter(
       Event.source_url == url
   ).first()
   if existing:
       print(f"⚠️ Duplicate: {url}")
       continue
   ```

6. **Add Rate Limiting**:
   ```python
   import time
   # Between API calls:
   time.sleep(3)  # Respect rate limits
   ```

**Success Criteria**:
- [ ] arXiv ingestion fetches real papers
- [ ] Company blogs fetch real RSS feeds
- [ ] Press releases fetch real articles
- [ ] Duplicates prevented (<5% duplicate rate)
- [ ] Rate limits respected (no 429 errors)
- [ ] 10+ real events ingested in first run

**Commit message**: `feat(sprint-7.1): Implement live news scraping from real APIs`

---

### Task 7.2: Weekly Digest Generation (PRIORITY 2 - 30 min)

**GoalMenuAuto-generate weekly summary of top AGI progress events

**Current State**:
- Task scheduled: Sunday 8:08 AM UTC in `celery_app.py`
- Task stub exists: `services/etl/app/tasks/snap_index.py::generate_weekly_digest`

**What to do**:

1. **Implement Digest Generation**:
   ```python
   # In services/etl/app/tasks/snap_index.py
   @shared_task(name="app.tasks.snap_index.generate_weekly_digest")
   def generate_weekly_digest():
       """Generate weekly digest of top events."""
       from datetime import datetime, timedelta
       
       # Query events from past 7 days
       week_ago = datetime.utcnow() - timedelta(days=7)
       events = db.query(Event).filter(
           Event.published_at >= week_ago,
           Event.evidence_tier.in_(["A", "B"])
       ).order_by(Event.published_at.desc()).limit(10).all()
       
       # Generate LLM summary
       prompt = f"Summarize these {len(events)} AGI progress events from the past week..."
       summary = call_openai(prompt, events_json)
       
       # Save to file
       digest = {
           "week_ending": datetime.utcnow().date().isoformat(),
           "summary": summary,
           "top_events": [serialize_event(e) for e in events],
           "a_tier_count": len([e for e in events if e.evidence_tier == "A"]),
           "b_tier_count": len([e for e in events if e.evidence_tier == "B"]),
       }
       
       # Save to public directory
       output_path = Path("public/digests") / f"{digest['week_ending']}.json"
       output_path.parent.mkdir(exist_ok=True)
       with open(output_path, 'w') as f:
           json.dump(digest, f, indent=2)
   ```

2. **Create Frontend Digest Page** (`apps/web/app/digests/page.tsx`):
   ```typescript
   // List all available digests
   // Show latest digest with summary
   // Cards for each event in the digest
   // Download as PDF/JSON option
   ```

3. **Add API Endpoint** (optional):
   ```python
   @app.get("/v1/digests/latest")
   def get_latest_digest():
       # Return most recent digest JSON
   ```

**Success Criteria**:
- [ ] Digest generation task implemented
- [ ] LLM generates 2-3 paragraph summary
- [ ] Digest saved to `public/digests/{date}.json`
- [ ] Frontend page shows digests
- [ ] Cost < $1 per digest

**Commit messageMenu`feat(sprint-7.2): Add weekly digest generation with LLM summaries`

---

### Task 7.3: Multi-Model Analysis Comparison (PRIORITY 3 - 45 min)

**Goal**: Run event analysis through multiple LLMs for consensus

**Current State**:
- Event analysis uses gpt-4o-mini: `services/etl/app/tasks/analyze/generate_event_analysis.py`
- Single model per analysis

**What to do**:

1. **Add Claude Support** (`services/etl/app/utils/llm_client.py`):
   ```python
   from anthropic import Anthropic
   
   def call_claude(prompt: str, model="claude-3-5-sonnet-20241022"):
       client = Anthropic(api_key=settings.anthropic_api_key)
       response = client.messages.create(
           model=model,
           messages=[{"role": "user", "content": prompt}],
           max_tokens=1000
       )
       return response.content[0].text
   ```

2. **Multi-Model Analysis Service** (`services/etl/app/services/multi_model_analysis.py`):
   ```python
   def analyze_event_multi_model(event: Event):
       """Run analysis through multiple models."""
       prompt = generate_analysis_prompt(event)
       
       results = []
       
       # GPT-4o-mini (cost-effective)
       gpt_result = call_openai(prompt, model="gpt-4o-mini")
       results.append({
           "model": "gpt-4o-mini",
           "summary": gpt_result.get("summary"),
           "significance": gpt_result.get("significance"),
           "why_matters": gpt_result.get("why_matters"),
       })
       
       # Claude (second opinion for A/B tier)
       if event.evidence_tier in ["A", "B"] and settings.anthropic_api_key:
           claude_result = call_claude(prompt)
           results.append({
               "model": "claude-3-5-sonnet",
               "summary": parse_claude_response(claude_result),
               ...
           })
       
       # Calculate consensus
       avg_significance = sum(r["significance"] for r in results) / len(results)
       variance = calculate_variance([r["significance"] for r in results])
       
       return {
           "analyses": results,
           "consensus_significance": avg_significance,
           "variance": variance,
           "models_agree": variance < 0.1
       }
   ```

3. **Update EventAnalysis Model**:
   ```python
   # Add fields to events_analysis table:
   model_name = Column(String(50))  # e.g., "gpt-4o-mini", "claude-3-5-sonnet"
   consensus_score = Column(Numeric)
   variance = Column(Numeric)
   ```

4. **Frontend Consensus Indicator** (`apps/web/components/events/ConsensusIndicator.tsx`):
   ```typescript
   // Show badge: "2 models agree ✓" or "Models diverge ⚠️"
   // Tooltip: "GPT-4: 8.5/10, Claude: 8.7/10"
   ```

**Success Criteria**:
- [ ] Can call both GPT-4 and Claude
- [ ] Consensus score calculated
- [ ] High-variance events flagged
- [ ] Cost stays under $30/day budget

**Commit message**: `feat(sprint-7.3): Add multi-model analysis with consensus scoring`

---

### Task 6.1: Retraction Monitoring (BONUS - 20 min)

**Goal**: UI for manually flagging retractions (automated scanning comes later)

**What to do**:

1. **Add Retraction Endpoint** (`services/etl/app/main.py`):
   ```python
   @app.post("/v1/admin/events/{event_id}/retract")
   def retract_event(
       event_id: int,
       reason: str,
       evidence_url: Optional[str] = None,
       verified: bool = Depends(verify_api_key),
       db: Session = Depends(get_db)
   ):
       """Mark an event as retracted."""
       event = db.query(Event).filter(Event.id == event_id).first()
       if not event:
           raise HTTPException(404, "Event not found")
       
       event.retracted = True
       event.retraction_reason = reason
       event.retraction_url = evidence_url
       event.retracted_at = datetime.utcnow()
       
       # Create changelog entry
       changelog = ChangelogEntry(
           change_type="retraction",
           description=f"Event retracted: {event.title}",
           metadata={"event_id": event_id, "reason": reason}
       )
       db.add(changelog)
       
       # Flag affected signpost links for review
       links = db.query(EventSignpostLink).filter(
           EventSignpostLink.event_id == event_id
       ).all()
       for link in links:
           link.needs_review = True
       
       db.commit()
       return {"message": "Event retracted", "affected_signposts": len(links)}
   ```

2. **Add Retraction Banner** (`apps/web/components/events/RetractionBanner.tsx`):
   ```typescript
   export function RetractionBanner({ event }) {
     if (!event.retracted) return null
     
     return (
       <Alert variant="destructive">
         <AlertTriangle className="h-4 w-4" />
         <AlertTitle>This claim was retracted</AlertTitle>
         <AlertDescription>
           {event.retraction_reason}
           {event.retraction_url && (
             <a href={event.retraction_url}>View evidence</a>
           )}
         </AlertDescription>
       </Alert>
     )
   }
   ```

3. **Add Retract Button to EventCard**:
   ```typescript
   // Admin-only button
   <Button variant="destructive" onClick={handleRetract}>
     Flag as Retracted
   </Button>
   ```

**Success Criteria**:
- [ ] Endpoint works (test with curl)
- [ ] Retraction banner shows on event cards
- [ ] Admin can flag retractions
- [ ] Affected signposts marked for review

**Commit message**: `feat(sprint-6.1): Add manual retraction flagging UI`

---

## 🔧 Implementation Guidelines

### Git Workflow (IMPORTANT!)

```bash
# Work directly on main
git checkout main
git pull origin main

# After each task:
git add -A
git commit -m "feat(sprint-X.Y): [description]"
git push origin main

# NO branches, NO PRs - commit directly to main
```

### Code Standards

**Python**:
- Type hints required (PEP 484)
- Docstrings for all public functions (Google style)
- Error handling with try/except
- Logging with print statements for Celery tasks
- Test imports before committing

**TypeScript**:
- Use existing shadcn/ui components
- Functional components with hooks
- Proper type definitions
- Follow existing patterns in `apps/web/components/`

**API Endpoints**:
- Cache read-only endpoints (1 hour TTL)
- Require API key for admin endpoints
- Return proper HTTP status codes
- Include error messages

### Testing Before Commit

```bash
# Test Python imports
cd services/etl
python -c "from app.tasks.news.ingest_arxiv import *"

# Test API endpoints (after pushing)
curl https://api-production-8535.up.railway.app/v1/events?limit=1

# Check Railway logs for errors
railway logs -s api
```

---

## 📦 Environment & Access

### API Keys Needed

**Already Set in Railway**:
- ✅ `OPENAI_API_KEY` - For GPT-4 analysis
- ✅ `DATABASE_URL` - Neon PostgreSQL
- ✅ `REDIS_URL` - Railway Redis
- ✅ `ADMIN_API_KEY` - Admin endpoints

**May Need to Add** (for Task 7.3):
- ⏸️ `ANTHROPIC_API_KEY` - For Claude (if available)
- ⏸️ If not available, skip Claude and use GPT-4o as second model

### File Paths

**Backend code**: `/Users/HenryAppel/AI Doomsday Tracker/services/etl/app/`
- Tasks: `tasks/news/`, `tasks/analyze/`
- Models: `models.py`
- API: `main.py`
- Utils: `utils/`

**Frontend code**: `/Users/HenryAppel/AI Doomsday Tracker/apps/web/`
- Pages: `app/digests/`, `app/events/`, etc.
- Components: `components/events/`, `components/ui/`
- API routes: `app/api/`

---

## 🚫 Blockers & What to Do

### If You Need Environment Variables

Create `BLOCKED_SPRINT_7.md` with:
```markdown
# Blocked: Need Environment Variables

## ANTHROPIC_API_KEY (Optional)
For multi-model analysis (Task 7.3).

If not available, use GPT-4o as second model instead of Claude.

## SENDGRID_API_KEY (Deferred)
For email digests (Task 7.2 email sending).

Skip email sending for now - just generate digest JSON files.
```

### If API Calls Fail

- Use try/except with fallbacks
- Log errors but don't crash
- Return empty results gracefully

### If Railway Redeploys Break Things

- Check Railway logs immediately
- Revert commit if needed: `git revert HEAD && git push`
- Fix issue and recommit

---

## 📊 Success Metrics

By the end of Sprint 7, you should have:

**Data Flow**:
- [ ] 20+ real events ingested from arXiv
- [ ] 10+ real events from company blogs
- [ ] 5+ real events from press releases
- [ ] Zero duplicate events
- [ ] All with proper evidence tiers (A/B/C)

**Features**:
- [ ] Weekly digest generation working
- [ ] Digest saved to `public/digests/` directory
- [ ] Digest page showing summaries
- [ ] (Optional) Multi-model analysis for top events
- [ ] (Optional) Retraction UI functional

**Code Quality**:
- [ ] 4-6 commits to main
- [ ] All tests pass (if any exist)
- [ ] No Railway deployment errors
- [ ] API stays healthy throughout

---

## 🎯 Prioritization

If you run out of time, complete in this order:

**MUST HAVE** (do first):
1. ✅ Task 7.1 - Live scraping (get real data!)
2. ✅ Task 7.2 - Weekly digest (user-facing feature)

**NICE TO HAVE** (if time permits):
3. Task 6.1 - Retraction UI (quality/credibility)
4. Task 7.3 - Multi-model analysis (advanced intelligence)

---

## 📝 Progress Logging

After each task, update `PHASE_2_PROGRESS.md`:

```markdown
### ✅ Sprint 7: Advanced Features (In Progress)

**Sprint 7.1: Live News Scraping**
- ✅ arXiv API integration complete
- ✅ Company blog RSS parsing complete
- ✅ Press release monitoring complete
- ✅ Deduplication working
- ✅ Rate limiting implemented

**Sprint 7.2: Weekly Digest**
- ✅ Digest generation task complete
- ✅ LLM summary generation working
- ✅ Digest archive page created
```

---

## 🚀 Getting Started

1. **Read this entire prompt** to understand the scope
2. **Start with Task 7.1** (live scraping) - highest impact
3. **Commit after each subtask** (arXiv, then blogs, then press)
4. **Test after each commit** (check Railway logs, test endpoints)
5. **Move to Task 7.2** once scraping works
6. **Continue until time runs out** or all tasks complete

---

## ⚠️ Important Notes

### On Main Branch
- You're committing directly to main (production)
- Test carefully before each commit
- If something breaks, revert immediately
- Railway auto-deploys from main

### Railway Auto-Deploy
- Every push to main triggers Railway deployment
- Wait for deployment to complete before next commit
- Check logs after each deployment
- If deployment fails, fix before continuing

### LLM Budget
- Daily limit: $50
- Track spend in Redis: `llm_budget:daily:{YYYY-MM-DD}`
- Use gpt-4o-mini for routine tasks
- Use gpt-4o only for high-priority analysis

### Existing Code Patterns
- Look at existing ingestion tasks for patterns
- Follow same error handling approach
- Use same database session management
- Copy structure from working code

---

## 🎉 Expected Outcome

By the time you're done:

1. **Real data flowing**: arXiv papers, company blogs, press releases
2. **Weekly digests**: Auto-generated summaries ready to view
3. **Enhanced UI**: Retraction handling, digest archive
4. **(Bonus)** Multi-model consensus on event significance

When Vercel limit resets and deploys, users will see:
- Fresh, real events (not fixtures)
- Weekly digest page with AI summaries
- More robust, credible analysis
- Professional retraction handling

---

## 📞 Final Checklist Before Starting

- [ ] I understand I'm working on `main` branch directly
- [ ] I will commit after each task completion
- [ ] I will test after each commit
- [ ] I will check Railway logs for errors
- [ ] I will create BLOCKED_SPRINT_7.md if I need env vars
- [ ] I will update PHASE_2_PROGRESS.md with status

---

**Ready? Start with Task 7.1 (Live News Scraping)!** 

Good luck! 🚀

---

## Quick Reference Commands

```bash
# Start on main
cd "/Users/HenryAppel/AI Doomsday Tracker"
git checkout main
git pull origin main

# After each task
git add -A
git commit -m "feat(sprint-X.Y): description"
git push origin main

# Test API
curl https://api-production-8535.up.railway.app/health
curl https://api-production-8535.up.railway.app/v1/events?limit=5

# Check Railway logs
railway logs -s api
railway logs -s agi-tracker-celery-worker
railway logs -s agi-tracker-celery-beat

# Test Python imports
cd services/etl
python -c "from app.tasks.news.ingest_arxiv import ingest_arxiv_task"
```

---

**Current Time**: ~11:00 AM  
**Vercel Reset**: ~12:50 PM (1 hour 50 minutes)  
**Available Time**: ~1.5-2 hours  
**Target**: Complete Tasks 7.1 and 7.2 minimum (real data + digests)

**GO! 🏃‍♂️**

