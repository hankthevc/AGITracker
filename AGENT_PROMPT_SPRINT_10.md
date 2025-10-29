# Agent Prompt: Sprint 10 - UX Enhancements & Data Quality

**Status**: Ready for agent execution  
**Prerequisites**: ✅ Sprint 9 complete (Performance & Scale)  
**Estimated Time**: 6-8 hours  
**Priority**: HIGH - Fix data quality issues + improve user experience

---

## 📋 Critical Context

**IMPORTANT**: The tracker is showing links to sources that may not exist or return 404 errors. This is a **data quality issue** that undermines trust in the platform. Sprint 10 prioritizes fixing this alongside UX improvements.

**What's Working**:
- API: https://agitracker-production-6efa.up.railway.app ✅
- Frontend: https://agi-tracker.vercel.app ✅
- Database: 33 events with Sprint 9 performance indexes ✅
- Footer shows: "✨ Sprint 9: Performance & Scale"

**What's Broken**:
- ❌ Some event `source_url` fields point to non-existent pages (404s)
- ❌ No validation that URLs are valid/accessible
- ❌ Users click links expecting content, get errors
- ❌ Erodes trust in the platform's credibility

---

## 🎯 Your Mission

Implement Sprint 10 tasks with **link validation as top priority**:

### Task 10.1: Link Validation & Data Quality (NEW - HIGH PRIORITY)

**Problem**: Events have `source_url` values that return 404 or don't exist.

**Goal**: Validate all source URLs and fix/flag broken links.

**What needs to be done:**

1. **Audit Existing Links**
   ```bash
   # Create audit script
   python scripts/audit_source_urls.py
   
   # Check all events.source_url for:
   # - NULL/empty values
   # - 404 errors
   # - Redirect chains
   # - SSL errors
   # - Timeout issues
   ```
   
   Output to: `infra/reports/url_audit_YYYY-MM-DD.json`
   ```json
   {
     "total_events": 33,
     "urls_checked": 33,
     "valid": 25,
     "invalid": 8,
     "issues": [
       {
         "event_id": 5,
         "title": "...",
         "url": "https://example.com/article",
         "status_code": 404,
         "error": "Not Found"
       }
     ]
   }
   ```

2. **Create URL Validation Service**
   File: `services/etl/app/utils/url_validator.py`
   
   ```python
   import requests
   from urllib.parse import urlparse
   
   def validate_url(url: str, timeout: int = 10) -> dict:
       """
       Validate a URL is accessible.
       
       Returns:
           {
               "valid": bool,
               "status_code": int,
               "final_url": str,  # after redirects
               "redirect_count": int,
               "error": str | None,
               "checked_at": datetime
           }
       """
       try:
           response = requests.head(url, timeout=timeout, allow_redirects=True)
           return {
               "valid": response.status_code < 400,
               "status_code": response.status_code,
               "final_url": response.url,
               "redirect_count": len(response.history),
               "error": None,
               "checked_at": datetime.now(UTC)
           }
       except Exception as e:
           return {
               "valid": False,
               "status_code": None,
               "final_url": None,
               "redirect_count": 0,
               "error": str(e),
               "checked_at": datetime.now(UTC)
           }
   
   def validate_event_sources(db: Session, limit: int = 100) -> list:
       """Validate URLs for recent events."""
       events = db.query(Event).order_by(desc(Event.id)).limit(limit).all()
       results = []
       for event in events:
           if event.source_url:
               result = validate_url(event.source_url)
               results.append({
                   "event_id": event.id,
                   "title": event.title,
                   **result
               })
       return results
   ```

3. **Add URL Validation Fields to Events Table**
   File: `infra/migrations/versions/019_add_url_validation.py`
   
   ```sql
   ALTER TABLE events ADD COLUMN url_validated_at TIMESTAMPTZ NULL;
   ALTER TABLE events ADD COLUMN url_status_code INTEGER NULL;
   ALTER TABLE events ADD COLUMN url_is_valid BOOLEAN DEFAULT TRUE NOT NULL;
   ALTER TABLE events ADD COLUMN url_error TEXT NULL;
   
   CREATE INDEX idx_events_url_valid ON events(url_is_valid) 
   WHERE url_is_valid = FALSE;
   ```

4. **Create Celery Task for URL Validation**
   File: `services/etl/app/tasks/validate_urls.py`
   
   ```python
   from app.celery_app import celery_app
   from app.utils.url_validator import validate_url
   
   @celery_app.task(name="validate_event_urls")
   def validate_event_urls():
       """Validate URLs for all events (run weekly)."""
       db = next(get_db())
       events = db.query(Event).filter(Event.source_url.isnot(None)).all()
       
       invalid_count = 0
       for event in events:
           result = validate_url(event.source_url)
           event.url_validated_at = result["checked_at"]
           event.url_status_code = result["status_code"]
           event.url_is_valid = result["valid"]
           event.url_error = result["error"]
           
           if not result["valid"]:
               invalid_count += 1
               logger.warning(f"Invalid URL for event {event.id}: {event.source_url}")
       
       db.commit()
       return {"checked": len(events), "invalid": invalid_count}
   ```
   
   Schedule: Weekly on Sundays at 3 AM UTC

5. **Add Admin Endpoint for Manual URL Check**
   ```python
   @app.post("/v1/admin/validate-urls")
   async def trigger_url_validation(
       api_key: str = Depends(verify_admin_api_key),
       db: Session = Depends(get_db)
   ):
       """Manually trigger URL validation for all events."""
       task = validate_event_urls.delay()
       return {"task_id": task.id, "status": "started"}
   
   @app.get("/v1/admin/invalid-urls")
   async def list_invalid_urls(
       api_key: str = Depends(verify_admin_api_key),
       db: Session = Depends(get_db)
   ):
       """List all events with invalid URLs."""
       events = db.query(Event).filter(Event.url_is_valid == False).all()
       return {
           "total": len(events),
           "events": [
               {
                   "id": e.id,
                   "title": e.title,
                   "source_url": e.source_url,
                   "status_code": e.url_status_code,
                   "error": e.url_error,
                   "validated_at": e.url_validated_at
               }
               for e in events
           ]
       }
   ```

6. **Frontend Warning for Invalid URLs**
   Update `EventCard.tsx`:
   ```tsx
   {event.url_is_valid === false && (
     <div className="mt-2 p-2 bg-yellow-50 border border-yellow-200 rounded text-sm">
       <AlertCircle className="inline h-4 w-4 mr-1 text-yellow-600" />
       <span className="text-yellow-800">
         Warning: Source link may be unavailable (verified {formatDate(event.url_validated_at)})
       </span>
     </div>
   )}
   ```

**Success Metrics:**
- [ ] URL validation running on all 33 events
- [ ] Migration applied with validation fields
- [ ] Admin endpoint working for manual checks
- [ ] Frontend shows warnings for invalid URLs
- [ ] Weekly Celery task scheduled
- [ ] Audit report generated

**Files to create:**
- `scripts/audit_source_urls.py`
- `services/etl/app/utils/url_validator.py`
- `services/etl/app/tasks/validate_urls.py`
- `infra/migrations/versions/019_add_url_validation.py`
- `infra/reports/.gitkeep` (for audit reports)

**Files to modify:**
- `services/etl/app/main.py` - Add admin endpoints
- `services/etl/app/models.py` - Add URL validation fields
- `services/etl/app/celery_app.py` - Schedule weekly task
- `apps/web/components/events/EventCard.tsx` - Add URL warning

---

### Task 10.2: Full-Text Search

**Goal**: Implement fast full-text search using Sprint 9 GIN indexes.

**What needs to be done:**

1. **Backend: Search Endpoint**
   ```python
   @app.get("/v1/search")
   @cache(expire=300)  # 5 min cache
   async def search_events(
       q: str = Query(..., min_length=2, max_length=100),
       limit: int = Query(20, le=50),
       tier: str | None = None,
       db: Session = Depends(get_db)
   ):
       """
       Full-text search across events.
       Uses GIN indexes from Sprint 9.
       """
       # Use to_tsquery for full-text search
       query = db.query(Event).filter(
           or_(
               func.to_tsvector('english', Event.title).op('@@')(
                   func.plainto_tsquery('english', q)
               ),
               func.to_tsvector('english', Event.summary).op('@@')(
                   func.plainto_tsquery('english', q)
               )
           )
       )
       
       if tier:
           query = query.filter(Event.evidence_tier == tier)
       
       events = query.limit(limit).all()
       
       return {
           "query": q,
           "total": len(events),
           "results": [serialize_event(e) for e in events]
       }
   ```

2. **Frontend: Search Component**
   File: `apps/web/components/SearchBar.tsx`
   ```tsx
   "use client"
   
   import { useState, useEffect } from "react"
   import { Search, X } from "lucide-react"
   import { Input } from "@/components/ui/input"
   import { useDebounce } from "@/hooks/useDebounce"
   
   export function SearchBar() {
     const [query, setQuery] = useState("")
     const [results, setResults] = useState([])
     const debouncedQuery = useDebounce(query, 300)
     
     useEffect(() => {
       if (debouncedQuery.length >= 2) {
         fetch(`/api/search?q=${encodeURIComponent(debouncedQuery)}`)
           .then(r => r.json())
           .then(setResults)
       }
     }, [debouncedQuery])
     
     return (
       <div className="relative">
         <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
         <Input
           value={query}
           onChange={(e) => setQuery(e.target.value)}
           placeholder="Search events..."
           className="pl-10 pr-10"
         />
         {query && (
           <button onClick={() => setQuery("")} className="absolute right-3 top-3">
             <X className="h-4 w-4 text-gray-400" />
           </button>
         )}
         {/* Search results dropdown */}
       </div>
     )
   }
   ```

3. **Add to Navigation**
   Update `apps/web/app/layout.tsx` to include SearchBar in nav.

**Success Metrics:**
- [ ] Search endpoint working with GIN indexes
- [ ] Sub-100ms search queries (verify with EXPLAIN ANALYZE)
- [ ] Frontend search bar with debouncing
- [ ] Results show instantly as user types
- [ ] Search works across title + summary

---

### Task 10.3: Advanced Filtering

**Goal**: Add date range, category, and significance filters.

**What needs to be done:**

1. **Backend: Enhanced Filters**
   Update `/v1/events` endpoint:
   ```python
   @app.get("/v1/events")
   async def list_events(
       # ... existing params ...
       category: str | None = None,  # capabilities, agents, inputs, security
       min_significance: float | None = Query(None, ge=0, le=1),
       date_from: date | None = None,
       date_to: date | None = None,
   ):
       # Filter by category via signpost links
       if category:
           query = query.join(EventSignpostLink).join(Signpost).filter(
               Signpost.category == category
           )
       
       # Filter by significance score
       if min_significance is not None:
           query = query.join(EventAnalysis).filter(
               EventAnalysis.significance_score >= min_significance
           )
       
       # Date range
       if date_from:
           query = query.filter(Event.published_at >= date_from)
       if date_to:
           query = query.filter(Event.published_at <= date_to)
   ```

2. **Frontend: Filter Panel**
   File: `apps/web/components/events/FilterPanel.tsx`
   ```tsx
   export function FilterPanel({ filters, setFilters }) {
     return (
       <div className="space-y-4">
         {/* Category filter */}
         <Select value={filters.category} onValueChange={(v) => setFilters({...filters, category: v})}>
           <SelectTrigger>
             <SelectValue placeholder="All categories" />
           </SelectTrigger>
           <SelectContent>
             <SelectItem value="all">All categories</SelectItem>
             <SelectItem value="capabilities">Capabilities</SelectItem>
             <SelectItem value="agents">Agents</SelectItem>
             <SelectItem value="inputs">Inputs</SelectItem>
             <SelectItem value="security">Security</SelectItem>
           </SelectContent>
         </Select>
         
         {/* Significance slider */}
         <div>
           <Label>Min Significance: {filters.minSignificance}</Label>
           <input
             type="range"
             min="0"
             max="1"
             step="0.1"
             value={filters.minSignificance}
             onChange={(e) => setFilters({...filters, minSignificance: e.target.value})}
           />
         </div>
         
         {/* Date range */}
         <div>
           <Label>From</Label>
           <Input type="date" value={filters.dateFrom} onChange={...} />
         </div>
         <div>
           <Label>To</Label>
           <Input type="date" value={filters.dateTo} onChange={...} />
         </div>
       </div>
     )
   }
   ```

**Success Metrics:**
- [ ] Category filter working
- [ ] Significance slider functional
- [ ] Date range picker working
- [ ] URL params sync with filters
- [ ] Filter state persists across navigation

---

### Task 10.4: Mobile Optimization

**Goal**: Ensure mobile-first experience on all pages.

**What needs to be done:**

1. **Responsive Navigation**
   Update `apps/web/app/layout.tsx`:
   - Add hamburger menu for mobile
   - Collapse nav items into drawer
   - Touch-friendly tap targets (48x48px min)

2. **Mobile Timeline**
   Update `apps/web/app/timeline/page.tsx`:
   - Switch to mobile-friendly view on small screens
   - List view instead of chart on <768px
   - Swipeable cards for events

3. **Touch Interactions**
   - Add swipe gestures for navigation
   - Increase button sizes on mobile
   - Add pull-to-refresh on event list

**Success Metrics:**
- [ ] Lighthouse mobile score >90
- [ ] All touch targets ≥48px
- [ ] No horizontal scroll on mobile
- [ ] Readable text without zoom
- [ ] Fast tap response (<100ms)

---

### Task 10.5: Keyboard Shortcuts

**Goal**: Power users can navigate without mouse.

**What needs to be done:**

1. **Shortcut System**
   File: `apps/web/hooks/useKeyboardShortcuts.ts`
   ```tsx
   export function useKeyboardShortcuts() {
     useEffect(() => {
       const handler = (e: KeyboardEvent) => {
         // Cmd/Ctrl + K: Open search
         if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
           e.preventDefault()
           // Open search modal
         }
         
         // / key: Focus search
         if (e.key === '/' && !isInputFocused()) {
           e.preventDefault()
           // Focus search input
         }
         
         // ? key: Show shortcuts help
         if (e.key === '?') {
           // Show modal with shortcuts
         }
       }
       
       window.addEventListener('keydown', handler)
       return () => window.removeEventListener('keydown', handler)
     }, [])
   }
   ```

2. **Shortcuts:**
   - `Cmd/Ctrl + K`: Open search
   - `/`: Focus search
   - `?`: Show shortcuts help
   - `Esc`: Close modals
   - `j/k`: Navigate events list
   - `Enter`: Open selected event

**Success Metrics:**
- [ ] All shortcuts working
- [ ] Help modal with shortcut list
- [ ] No conflicts with browser shortcuts
- [ ] Works on Mac and Windows

---

## 🚨 Critical Rules

1. **Work on main branch** - Continue from Sprint 9
2. **Commit after each task** with descriptive messages
3. **Test thoroughly** - Verify URL validation catches real issues
4. **Update documentation** as you complete tasks
5. **If blocked, document in BLOCKED_SPRINT_10.md**

---

## 🧪 Testing Checklist

### After Task 10.1 (URL Validation):
```bash
# Run audit script
python scripts/audit_source_urls.py

# Check results
cat infra/reports/url_audit_*.json | jq '.invalid'

# Trigger validation via API
curl -X POST https://agitracker-production-6efa.up.railway.app/v1/admin/validate-urls \
  -H "Authorization: Bearer ${ADMIN_API_KEY}"

# Check for invalid URLs
curl https://agitracker-production-6efa.up.railway.app/v1/admin/invalid-urls \
  -H "Authorization: Bearer ${ADMIN_API_KEY}"

# Verify frontend warnings show
# Visit event with invalid URL, should see yellow warning
```

### After Task 10.2 (Search):
```bash
# Test search endpoint
curl "https://agitracker-production-6efa.up.railway.app/v1/search?q=GPT-4&limit=10"

# Measure query time
curl -w "%{time_total}\n" "https://agitracker-production-6efa.up.railway.app/v1/search?q=benchmark"
# Should be <100ms

# Test on frontend
# Type in search bar, results should appear instantly
```

### After Task 10.3 (Filters):
```bash
# Test category filter
curl "https://agitracker-production-6efa.up.railway.app/v1/events?category=capabilities"

# Test significance filter
curl "https://agitracker-production-6efa.up.railway.app/v1/events?min_significance=0.8"

# Test date range
curl "https://agitracker-production-6efa.up.railway.app/v1/events?date_from=2024-01-01&date_to=2024-12-31"
```

### After Task 10.4 (Mobile):
```bash
# Run Lighthouse mobile audit
lighthouse https://agi-tracker.vercel.app/ --preset=mobile --output=html

# Check mobile score
# Target: >90

# Test on real device
# Check touch targets, scrolling, responsiveness
```

---

## 📊 Success Criteria

Sprint 10 is complete when:

- [ ] **Task 10.1**: URL validation working, invalid URLs flagged
- [ ] **Audit report**: All 33 events checked, issues documented
- [ ] **Task 10.2**: Full-text search <100ms, frontend working
- [ ] **Task 10.3**: Advanced filters functional
- [ ] **Task 10.4**: Lighthouse mobile >90
- [ ] **Task 10.5**: Keyboard shortcuts working
- [ ] All committed to main
- [ ] Documentation updated
- [ ] Railway + Vercel deployed successfully

---

## 💰 Cost Implications

**Sprint 10 costs:**
- URL validation: ~$0 (uses requests library, no external API)
- Additional Celery task: ~$0 (runs weekly, minimal compute)
- GIN indexes: Already created in Sprint 9
- No LLM usage
- No additional infrastructure

**Total additional monthly cost**: $0

---

## 🎯 Implementation Tips

### Task 10.1: URL Validation

**Use HEAD requests** instead of GET to save bandwidth:
```python
response = requests.head(url, timeout=10)
```

**Handle redirects**:
```python
allow_redirects=True
final_url = response.url  # After redirects
```

**Respect rate limits**:
```python
import time
for event in events:
    validate_url(event.source_url)
    time.sleep(0.5)  # 2 req/sec max
```

**Common errors to catch**:
- `ConnectionError`: DNS failure, connection refused
- `Timeout`: Site too slow
- `TooManyRedirects`: Redirect loop
- `SSLError`: Certificate issues
- `404`: Page not found
- `403`: Access forbidden

### Task 10.2: Full-Text Search

**Use GIN indexes from Sprint 9**:
```sql
-- Already created:
CREATE INDEX idx_events_title_fts ON events 
USING gin(to_tsvector('english', title));
```

**PostgreSQL full-text operators**:
```python
# Use @@ operator for matches
to_tsvector('english', title) @@ plainto_tsquery('english', 'GPT-4')

# plainto_tsquery: Handles phrases, ignores special chars
# to_tsquery: More control, requires proper syntax
```

**Highlight matches**:
```python
ts_headline('english', title, plainto_tsquery('english', query))
# Returns: "OpenAI releases <b>GPT-4</b> model"
```

### Task 10.3: Advanced Filters

**Efficient category filtering**:
```sql
-- Use DISTINCT to avoid duplicate events
SELECT DISTINCT events.* 
FROM events
JOIN event_signpost_links ON ...
JOIN signposts ON signposts.id = event_signpost_links.signpost_id
WHERE signposts.category = 'capabilities'
```

**Significance filter requires analysis**:
```sql
-- Only events with analysis
WHERE EXISTS (
  SELECT 1 FROM events_analysis 
  WHERE events_analysis.event_id = events.id 
  AND significance_score >= 0.8
)
```

---

## 🚀 Start Now

Begin with **Task 10.1** (URL Validation) - this is the highest priority to fix data quality issues. Then proceed with search, filters, and mobile optimization.

**Current Status**:
- Railway API: https://agitracker-production-6efa.up.railway.app ✅
- Frontend: https://agi-tracker.vercel.app ✅
- Database: 33 events, Sprint 9 indexes ✅
- Sprint 9: Complete ✅

**Good luck with Sprint 10!** 🔍
