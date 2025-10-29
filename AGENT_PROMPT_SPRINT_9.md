# Agent Prompt: Sprint 9 - Performance & Scale

**Status**: Ready for agent execution  
**Prerequisites**: ✅ Sprint 8 complete (API keys, GDPR compliance)  
**Estimated Time**: 5-8 hours  
**Priority**: High - Ensure scalability for 10,000+ events

---

## 📋 Required Reading

Before starting, read these files for context:
1. `AGENT_TASKS_PHASE_2.md` - Full task breakdown (lines 622-706)
2. `PHASE_2_PROGRESS.md` - What's completed (Sprints 4-8)
3. `SPRINT_8_COMPLETE.md` - Current infrastructure status

---

## 🎯 Your Mission

Implement ALL tasks in Sprint 9 from AGENT_TASKS_PHASE_2.md:

### Task 9.1: Database Query Optimization

**Goal**: Ensure <100ms query times as data scales to 10,000+ events

**What needs to be done:**

1. **Run Performance Audit**
   - Check current query performance on Railway:
     ```bash
     # Connect to Railway PostgreSQL
     railway connect postgres
     
     # Run EXPLAIN ANALYZE on slow queries
     EXPLAIN ANALYZE SELECT * FROM events WHERE evidence_tier = 'A' ORDER BY published_at DESC LIMIT 100;
     EXPLAIN ANALYZE SELECT * FROM event_signpost_links WHERE signpost_id = 1;
     EXPLAIN ANALYZE SELECT * FROM events e JOIN event_signpost_links l ON e.id = l.event_id WHERE l.signpost_id = 1;
     ```
   - Document baseline query times
   - Identify missing indexes
   - Look for N+1 query problems in `/v1/events` endpoint

2. **Create Performance Indexes Migration**
   - New file: `infra/migrations/versions/018_add_performance_indexes.py`
   - Add composite indexes for common queries:
     ```sql
     -- Event queries
     CREATE INDEX IF NOT EXISTS idx_events_tier_published ON events(evidence_tier, published_at DESC);
     CREATE INDEX IF NOT EXISTS idx_events_retracted_published ON events(retracted, published_at DESC);
     CREATE INDEX IF NOT EXISTS idx_events_provisional_published ON events(provisional, published_at DESC);
     
     -- Signpost link queries
     CREATE INDEX IF NOT EXISTS idx_event_signpost_tier_confidence ON event_signpost_links(tier, confidence DESC);
     CREATE INDEX IF NOT EXISTS idx_event_signpost_created ON event_signpost_links(created_at DESC);
     
     -- Analysis queries
     CREATE INDEX IF NOT EXISTS idx_events_analysis_event_generated ON events_analysis(event_id, generated_at DESC);
     
     -- Full-text search (for Sprint 10)
     CREATE INDEX IF NOT EXISTS idx_events_title_fts ON events USING gin(to_tsvector('english', title));
     CREATE INDEX IF NOT EXISTS idx_events_summary_fts ON events USING gin(to_tsvector('english', summary));
     ```
   - Test on Railway after applying

3. **Optimize Cache TTLs**
   - Already using FastAPI-cache with Redis
   - Update TTLs in `services/etl/app/main.py`:
     ```python
     # Current caching
     @cache(expire=3600)  # /v1/index - Good
     @cache(expire=300)   # /v1/events - Should be 600 (10 min)
     @cache(expire=3600)  # /v1/signposts - Good
     ```
   - Add cache warming for popular queries (optional)
   - Monitor cache hit rate via Redis INFO

4. **Add Cursor-Based Pagination**
   - Current: `/v1/events?limit=100` (offset-based, slow at scale)
   - Implement: `/v1/events?cursor={last_event_id}&limit=50`
   - Endpoint changes:
     ```python
     @app.get("/v1/events")
     async def list_events(
         cursor: str = None,  # Base64-encoded event_id + timestamp
         limit: int = Query(50, le=100),
         ...
     ):
         # Decode cursor
         # Query: WHERE (published_at, id) < (cursor_time, cursor_id)
         # Return: {"events": [...], "next_cursor": "...", "has_more": bool}
     ```
   - Frontend: Update `/events` page for infinite scroll (optional for now)

**Success Metrics:**
- [ ] P95 response time < 100ms for `/v1/events`
- [ ] P95 response time < 50ms for `/v1/signposts/{id}`
- [ ] Cache hit rate > 70% (check Redis stats)
- [ ] Cursor pagination working for 10,000+ events
- [ ] All indexes applied successfully

**Files to create:**
- `infra/migrations/versions/018_add_performance_indexes.py`

**Files to modify:**
- `services/etl/app/main.py` - Update cache TTLs, add cursor pagination

---

### Task 9.2: Frontend Performance Optimization

**Goal**: Achieve Lighthouse score >90 on all pages

**What needs to be done:**

1. **Run Lighthouse Audit**
   - Test pages:
     - Homepage: https://agi-tracker.vercel.app/
     - Events: https://agi-tracker.vercel.app/events
     - Timeline: https://agi-tracker.vercel.app/timeline
     - Insights: https://agi-tracker.vercel.app/insights/surprises
   - Document baseline scores (Performance, Accessibility, Best Practices, SEO)
   - Identify top issues

2. **Code Splitting & Lazy Loading**
   - Lazy load heavy Recharts components:
     ```typescript
     // apps/web/app/timeline/page.tsx
     import dynamic from 'next/dynamic'
     
     const TimelineChart = dynamic(() => import('@/components/TimelineChart'), {
       loading: () => <div>Loading chart...</div>,
       ssr: false
     })
     ```
   - Lazy load EventCard analysis sections (expand on click)
   - Use Next.js dynamic imports for admin pages

3. **Bundle Size Analysis**
   - Add bundle analyzer to `next.config.js`:
     ```javascript
     const withBundleAnalyzer = require('@next/bundle-analyzer')({
       enabled: process.env.ANALYZE === 'true',
     })
     
     module.exports = withBundleAnalyzer({
       // existing config
     })
     ```
   - Run: `ANALYZE=true npm run build`
   - Target: Total bundle < 500KB
   - Look for:
     - Duplicate dependencies
     - Unused shadcn/ui components
     - Heavy Recharts imports (use tree-shaking)

4. **Image Optimization**
   - Use Next.js Image component for all images
   - Add loading placeholders
   - Optimize signpost icons (if any large images exist)

5. **Improve Time to Interactive**
   - Defer non-critical JavaScript
   - Use `loading.tsx` files for better perceived performance
   - Add Suspense boundaries around heavy components

**Success Metrics:**
- [ ] Lighthouse Performance score > 90 (all pages)
- [ ] Time to Interactive < 3s
- [ ] First Contentful Paint < 1.5s
- [ ] Total bundle size < 500KB
- [ ] No console errors or warnings

**Files to modify:**
- `apps/web/next.config.js` - Add bundle analyzer
- `apps/web/app/timeline/page.tsx` - Lazy load chart
- `apps/web/app/events/page.tsx` - Code splitting
- `apps/web/components/events/EventCard.tsx` - Lazy load analysis

**Optional (if time permits):**
- Add service worker for offline capability
- Implement stale-while-revalidate caching
- Add loading skeletons

---

## 🚨 Critical Rules

1. **Work on main branch only** - NO PRs, NO feature branches
2. **Commit after each task** with descriptive messages
3. **Test after each commit** - verify API and frontend still work
4. **Update PHASE_2_PROGRESS.md** as you complete tasks
5. **If blocked, create BLOCKED_SPRINT_9.md** and continue with other tasks

---

## 🧪 Git Workflow

```bash
git checkout main
git pull origin main

# After each task:
git add -A
git commit -m "feat(sprint-9.X): description"
git push origin main
```

---

## 🧪 Testing Checklist

### After Task 9.1 (Database Optimization):
```bash
# Test query performance
curl -w "@curl-format.txt" https://agitracker-production-6efa.up.railway.app/v1/events?limit=100
# Should return in < 100ms

# Test cursor pagination
curl https://agitracker-production-6efa.up.railway.app/v1/events?limit=50
# Get next_cursor from response
curl https://agitracker-production-6efa.up.railway.app/v1/events?cursor={next_cursor}&limit=50

# Check Redis cache hit rate
redis-cli INFO stats | grep keyspace_hits
redis-cli INFO stats | grep keyspace_misses
# Calculate: hit_rate = hits / (hits + misses)
# Target: > 70%
```

### After Task 9.2 (Frontend Optimization):
```bash
# Run Lighthouse audit
npm install -g lighthouse
lighthouse https://agi-tracker.vercel.app/ --output=html --output-path=./lighthouse-report.html

# Check bundle size
cd apps/web
ANALYZE=true npm run build
# Review bundle analyzer output

# Test page load times
curl -w "%{time_total}\n" -o /dev/null -s https://agi-tracker.vercel.app/
# Should be < 1s for cached content
```

---

## 📊 Success Criteria

Sprint 9 is complete when:

- [ ] Task 9.1: Database indexes created and applied
- [ ] Query times < 100ms (verified on Railway)
- [ ] Cursor pagination working
- [ ] Cache hit rate > 70%
- [ ] Task 9.2: Lighthouse score > 90 on all pages
- [ ] Bundle size < 500KB
- [ ] Time to Interactive < 3s
- [ ] All committed to main
- [ ] Railway services still healthy
- [ ] Frontend and API responding correctly

---

## 💰 Cost Implications

**Sprint 9 has zero cost impact:**
- No additional LLM usage
- No additional infrastructure
- Uses existing Railway/Vercel services
- Performance improvements = cost savings (fewer queries, better caching)

**Total additional monthly cost**: $0

---

## 🎯 Implementation Tips

### Task 9.1: Database Optimization

**Use existing patterns:**
- `infra/migrations/versions/016_news_events_pipeline.py` - See migration format
- `services/etl/app/main.py` - See existing @cache decorators

**Index Strategy:**
- Composite indexes for multi-column WHERE clauses
- Cover most common query patterns
- Don't over-index (slows down writes)

**Cursor Pagination:**
```python
def encode_cursor(published_at: datetime, event_id: int) -> str:
    """Encode cursor for pagination."""
    cursor_data = f"{published_at.isoformat()}|{event_id}"
    return base64.b64encode(cursor_data.encode()).decode()

def decode_cursor(cursor: str) -> tuple[datetime, int]:
    """Decode cursor from base64."""
    cursor_data = base64.b64decode(cursor.encode()).decode()
    timestamp_str, event_id_str = cursor_data.split("|")
    return datetime.fromisoformat(timestamp_str), int(event_id_str)
```

### Task 9.2: Frontend Optimization

**Use Next.js features:**
- `dynamic()` for lazy loading
- `loading.tsx` for loading states
- `@next/bundle-analyzer` for analysis

**Quick wins:**
- Convert all `<img>` to `<Image>`
- Add Suspense boundaries
- Lazy load chart libraries
- Remove unused imports

**Lighthouse tips:**
- Run in incognito mode (no extensions)
- Test on mobile (slower device simulation)
- Focus on Performance score first
- Accessibility score should already be good

---

## 🚀 Start Now

Begin with **Task 9.1** (Database Query Optimization). Work through ALL tasks sequentially. Commit frequently. Test thoroughly.

When both tasks are complete, update `PHASE_2_PROGRESS.md` and create `SPRINT_9_COMPLETE.md`.

**Current Infrastructure Status**:
- Railway API: https://agitracker-production-6efa.up.railway.app ✅
- Frontend: https://agi-tracker.vercel.app ✅
- Database: 33 events, 34 signposts, 79 mappings ✅
- Sprint 8: API keys, GDPR compliance ✅
- All services healthy ✅

**Good luck with Sprint 9!** ⚡
