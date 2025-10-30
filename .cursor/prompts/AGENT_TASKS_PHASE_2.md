# 🤖 Agent Tasks - Phase 2: Production Automation & Intelligence

**Status**: Ready for agent execution  
**Prerequisites**: ✅ Phase 1 complete (backend deployed, frontend live, database seeded)  
**Estimated Time**: 15-25 hours of agent work  
**Priority**: High - Enables full automation and intelligence features

---

## 📋 Overview

This document outlines the next major phase of AGI Tracker development, focusing on:
1. **Production automation** (Celery workers, automated ingestion)
2. **Intelligence features** (LLM-powered analysis, predictions)
3. **Data quality** (golden set validation, monitoring)
4. **User experience** (retraction handling, credibility tracking)

---

## 🎯 Sprint 4: Production Automation (8-10 hours)

### Task 4.1: Deploy Celery Workers on Railway ⭐ PRIORITY

**Goal**: Enable automated background tasks for event ingestion and analysis

**What needs to be done:**

1. **Add Redis to Railway** (if not already added)
   - In Railway dashboard: AGI Tracker project → "+ New" → Database → Redis
   - Verify `REDIS_URL` environment variable is created

2. **Create Celery Worker Service**
   - Create new service in Railway from GitHub repo `hankthevc/AGITracker`
   - Root directory: `services/etl`
   - Start command: `celery -A app.celery_app worker --loglevel=info`
   - Copy all environment variables from main API service
   - Verify deployment succeeds

3. **Create Celery Beat Service** (Scheduler)
   - Create new service in Railway from GitHub repo
   - Root directory: `services/etl`
   - Start command: `celery -A app.celery_app beat --loglevel=info`
   - Copy all environment variables from main API service
   - Verify deployment succeeds

4. **Verify Tasks Are Running**
   - Check Railway logs for worker service
   - Look for: "celery@hostname ready"
   - Check beat logs for scheduled tasks
   - Look for: "Scheduler: Sending due task..."

5. **Test Automated Ingestion**
   - Wait for next scheduled run (check celery_app.py for times)
   - Or manually trigger: `railway run -s celery-worker celery -A app.celery_app call ingest_arxiv`
   - Verify new events appear in database
   - Check /events page for new content

**Success Metrics:**
- [ ] 3 Railway services running (API, worker, beat)
- [ ] Worker shows "ready" in logs
- [ ] Beat shows scheduled tasks
- [ ] Events auto-ingest twice daily
- [ ] LLM analysis runs on new A/B tier events
- [ ] Zero manual interventions for 48 hours

**Files to reference:**
- `services/etl/app/celery_app.py` - Task schedule configuration
- `RAILWAY_DEPLOYMENT.md` - Deployment guide
- `MONITORING_SETUP.md` - Health check instructions

---

### Task 4.2: Add Celery Task Monitoring

**Goal**: Know when background tasks fail or fall behind

**What needs to be done:**

1. **Create Task Health Endpoint**
   - Add `/v1/admin/tasks/health` endpoint in `main.py`
   - Returns status of last run for each task
   - Shows: last_run, next_run, success_count, error_count
   - Use `app.utils.task_tracking` (already exists)

2. **Add Healthchecks.io Integration** (Optional)
   - Sign up at https://healthchecks.io (free tier)
   - Add ping URLs to Celery tasks
   - Ping on success, ping/fail endpoint on error
   - Get email alerts when tasks don't run

3. **Create Task Dashboard Page**
   - Add `/admin/tasks` page in frontend
   - Shows all scheduled tasks with status
   - Last run time, next run time
   - Success/error counts
   - Manual trigger buttons

**Success Metrics:**
- [ ] Can see task status at /v1/admin/tasks/health
- [ ] Email alerts when tasks fail (if using Healthchecks.io)
- [ ] Dashboard shows green/yellow/red status
- [ ] Can manually trigger tasks from UI

**Files to create:**
- `services/etl/app/utils/healthchecks.py` - Healthchecks.io integration
- `apps/web/app/admin/tasks/page.tsx` - Task monitoring dashboard

---

## 🧠 Sprint 5: Intelligence & Predictions (10-12 hours)

### Task 5.1: LLM-Powered Forecast Extraction

**Goal**: Auto-extract predictions from roadmap PDFs using GPT-4

**What needs to be done:**

1. **Create Forecast Extraction Task**
   - New file: `services/etl/app/tasks/predictions/extract_forecasts.py`
   - Input: PDF documents from `infra/seeds/forecasts/*.pdf`
   - LLM: gpt-4o (better reasoning than mini for this)
   - Output: Structured predictions with dates, values, confidence intervals

2. **Prompt Engineering**
   - System: "You are an expert at extracting AGI timeline predictions from research documents"
   - User: Provide PDF text + signpost descriptions
   - Output: JSON with signpost_code, predicted_date, predicted_value, rationale, confidence

3. **Validation Pipeline**
   - Cross-reference extracted predictions with existing signposts
   - Flag predictions that don't map to known signposts
   - Store in `expert_predictions` table
   - Create changelog entry for new predictions

4. **Budget Management**
   - Estimate: ~$5-10 to process all 8 forecast documents
   - Use same budget tracking system ($50/day limit)
   - Cache results (re-run only when PDFs change)

**Success Metrics:**
- [ ] Extract 50+ predictions from 8 roadmap sources
- [ ] 90%+ map to existing signposts
- [ ] Confidence intervals populated
- [ ] Total cost < $10
- [ ] Results validated against manual examples

**Files to create:**
- `services/etl/app/tasks/predictions/extract_forecasts.py`
- `services/etl/app/prompts/forecast_extraction_v1.txt`
- `services/etl/tests/test_forecast_extraction.py`

---

### Task 5.2: Mapper Accuracy Improvement

**Goal**: Achieve F1 >= 0.80 on golden set (currently targeting 0.75)

**What needs to be done:**

1. **Run Current Golden Set Test**
   ```bash
   cd services/etl
   pytest tests/test_mapper_accuracy.py -v
   ```
   - Record baseline F1, precision, recall
   - Identify failure patterns

2. **Analyze Failure Cases**
   - Which golden set examples are failing?
   - Are false positives or false negatives the issue?
   - Does tier affect accuracy?

3. **Improve Mapping Logic**
   - Enhance `services/etl/app/tasks/news/map_events_to_signposts.py`
   - Options:
     - Better keyword matching
     - Add synonym dictionary
     - Use embeddings for semantic matching
     - Add LLM-powered mapping for edge cases

4. **Expand Golden Set**
   - Add 10-20 more examples to `infra/seeds/news_goldset.json`
   - Cover edge cases found in step 2
   - Include multi-signpost events
   - Include negative examples (no mapping)

5. **Re-test and Iterate**
   - Run tests after each improvement
   - Target: F1 >= 0.80, Precision >= 0.75, Recall >= 0.75
   - Document changes in changelog

**Success Metrics:**
- [ ] F1 score >= 0.80 on golden set
- [ ] Precision >= 0.75
- [ ] Recall >= 0.75
- [ ] High-confidence predictions (>0.7) are 90%+ accurate
- [ ] Golden set expanded to 25+ examples

**Files to modify:**
- `services/etl/app/tasks/news/map_events_to_signposts.py`
- `infra/seeds/news_goldset.json`
- `services/etl/tests/test_mapper_accuracy.py`

---

### Task 5.3: Surprise Score Dashboard

**Goal**: Highlight events that surprised expert forecasts

**What needs to be done:**

1. **Implement Surprise Calculation**
   - Compare event dates vs predicted dates
   - Calculate z-score based on prediction uncertainty
   - Higher score = more surprising timing
   - Formula: `|actual_date - predicted_date| / prediction_uncertainty`

2. **Create Surprise Endpoint**
   - Endpoint: `/v1/predictions/surprises`
   - Returns top 10 most surprising events
   - Shows: event, signpost, predicted_date, actual_date, surprise_score
   - Filters: last 30/60/90 days

3. **Build Surprise Dashboard**
   - New page: `/insights/surprises`
   - Visual: Timeline with predicted vs actual markers
   - Cards for top surprises with explanation
   - "Why this was unexpected" analysis

4. **LLM Analysis of Surprises**
   - For high-surprise events, generate explanation
   - Prompt: "Why was this event X months earlier/later than predicted?"
   - Store in `event_surprise_analysis` table

**Success Metrics:**
- [ ] Surprise scores calculated for all events with predictions
- [ ] Top 10 surprises displayed on dashboard
- [ ] Visual timeline shows prediction vs reality
- [ ] LLM explains why surprising events occurred

**Files to create:**
- `services/etl/app/services/surprise_calculation.py`
- `services/etl/app/models.py` - Add `EventSurpriseAnalysis` table
- `apps/web/app/insights/surprises/page.tsx`
- `infra/migrations/versions/add_surprise_analysis.py`

---

## 📊 Sprint 6: Data Quality & Credibility (7-10 hours)

### Task 6.1: Retraction Monitoring System

**Goal**: Auto-detect when papers/claims are retracted and flag affected events

**What needs to be done:**

1. **Create Retraction Scanner**
   - Monitor Retraction Watch database
   - Check arXiv for withdrawn papers
   - Scan publisher correction pages
   - Run weekly (Celery task)

2. **Implement Retraction Workflow**
   - When retraction detected:
     - Mark event as retracted
     - Flag all dependent signpost links
     - Update source credibility score
     - Create changelog entry
     - Send notification (email/Slack)

3. **Build Retraction UI**
   - Add retraction banner to EventCard
   - Show "This claim was retracted" warning
   - Link to retraction evidence
   - Show impact on affected signposts
   - Timeline view: grey out retracted events

4. **Automated Recomputation**
   - When event retracted, trigger index recalculation
   - Update affected signpost scores
   - Invalidate caches
   - Show before/after comparison

**Success Metrics:**
- [ ] Retraction scanner runs weekly
- [ ] Retractions flagged within 7 days
- [ ] UI shows clear warnings
- [ ] Affected signposts auto-update
- [ ] Email notifications work

**Files to create:**
- `services/etl/app/tasks/monitoring/scan_retractions.py`
- `services/etl/app/services/retraction_workflow.py`
- `apps/web/components/events/RetractionBanner.tsx`

---

### Task 6.2: Source Credibility Tracking

**Goal**: Track publisher reliability over time using Wilson score intervals

**What needs to be done:**

1. **Implement Wilson Score Calculation**
   - Already exists: `app.utils.statistics.wilson_lower_bound`
   - Calculate for each publisher based on retraction rate
   - Account for sample size (few articles = wider confidence interval)

2. **Create Credibility Snapshots**
   - Daily snapshot task (Celery)
   - Store in `source_credibility_snapshots` table
   - Track: publisher, total_articles, retracted_count, credibility_score, tier

3. **Build Credibility Dashboard**
   - New page: `/admin/sources`
   - Table of all publishers with:
     - Total articles
     - Retraction rate
     - Credibility score (Wilson)
     - Tier (A/B/C/D)
     - 30-day trend (up/down/stable)
   - Sortable by score, volume, tier

4. **Auto-Tier Assignment**
   - When credibility score drops below thresholds:
     - A-tier: >0.95 + 20+ articles
     - B-tier: >0.90 + 10+ articles
     - C-tier: >0.80 + 5+ articles
     - D-tier: <0.80 or <5 articles
   - Flag tier changes in changelog
   - Re-evaluate all events from that source

**Success Metrics:**
- [ ] Credibility scores calculated daily
- [ ] Publishers auto-tiered based on reliability
- [ ] Dashboard shows credibility trends
- [ ] Tier downgrades trigger re-evaluation
- [ ] Changelog tracks tier changes

**Files already exist:**
- ✅ `services/etl/app/utils/statistics.py` - Wilson score
- ✅ `/v1/admin/source-credibility` endpoint - Already implemented

**Files to enhance:**
- `services/etl/app/tasks/monitoring/update_credibility.py` - Daily task
- `apps/web/app/admin/sources/page.tsx` - Dashboard UI

---

### Task 6.3: Golden Set Expansion & Continuous Testing

**Goal**: Expand test coverage and run mapper tests in CI/CD

**What needs to be done:**

1. **Expand Golden Set to 50 Examples**
   - Current: 12 examples in `infra/seeds/news_goldset.json`
   - Target: 50+ examples covering:
     - All signpost categories (capabilities, agents, inputs, security)
     - All tiers (A/B/C/D)
     - Multi-signpost events
     - Negative cases (no mapping)
     - Edge cases (ambiguous wording)

2. **Add CI/CD Testing**
   - Create GitHub Actions workflow
   - Run mapper tests on every PR
   - Fail if F1 < 0.75 or precision/recall < 0.70
   - Generate test report artifact

3. **Create Mapper Benchmark**
   - Track F1 score over time
   - Store in database: `mapper_benchmark_runs` table
   - Show trend on admin dashboard
   - Alert if score drops >5%

4. **A/B Testing Framework**
   - Support multiple mapping strategies
   - Compare accuracy side-by-side
   - Track which strategy works best
   - Promote winner to production

**Success Metrics:**
- [ ] 50+ examples in golden set
- [ ] CI/CD runs tests on every commit
- [ ] F1 score tracked over time
- [ ] Baseline established: F1 >= 0.80

**Files to create:**
- `.github/workflows/test-mapper.yml` - CI/CD workflow
- `services/etl/app/models.py` - Add MapperBenchmarkRun table
- `infra/migrations/versions/add_mapper_benchmarks.py`

**Files to enhance:**
- `infra/seeds/news_goldset.json` - Expand to 50+ examples
- `services/etl/tests/test_mapper_accuracy.py` - Add more test cases

---

## 🚀 Sprint 7: Advanced Features (8-12 hours)

### Task 7.1: Live News Scraping (Remove Fixtures)

**Goal**: Replace dev fixtures with real-time news ingestion

**What needs to be done:**

1. **arXiv API Integration**
   - Use arXiv API v2: http://export.arxiv.org/api/query
   - Query categories: cs.AI, cs.LG, cs.CL
   - Filter for AGI-relevant keywords
   - Respect rate limits (3 sec delay between requests)
   - Parse XML responses

2. **Company Blog RSS Feeds**
   - OpenAI: https://openai.com/blog/rss.xml
   - Anthropic: https://anthropic.com/news/rss
   - DeepMind: https://deepmind.google/discover/blog/rss.xml
   - Add: Meta AI, Mistral, Cohere, etc.
   - Parse RSS with feedparser
   - Deduplicate by URL

3. **Press Release Monitoring**
   - Reuters AI section RSS
   - AP Technology RSS
   - Add rate limiting (respect robots.txt)
   - Filter for AI-relevant articles

4. **Remove Dev Fixtures**
   - Update `query_active_events()` to exclude synthetic events in production
   - Keep fixtures for testing/development
   - Add `INCLUDE_DEV_FIXTURES` env var (default: false)

**Success Metrics:**
- [ ] 50+ real events ingested per week
- [ ] Zero dev fixtures in production
- [ ] No rate limit violations
- [ ] Duplicates < 5%
- [ ] All sources respect robots.txt

**Files to modify:**
- `services/etl/app/tasks/news/ingest_arxiv.py` - Real API calls
- `services/etl/app/tasks/news/ingest_company_blogs.py` - Real RSS parsing
- `services/etl/app/utils/query_helpers.py` - Exclude synthetics

---

### Task 7.2: Weekly Digest Generation

**Goal**: Auto-generate weekly email digest of top AGI progress events

**What needs to be done:**

1. **Create Digest Generation Task**
   - Celery task: `generate_weekly_digest()`
   - Schedule: Sunday 8 AM UTC (already in celery_app.py)
   - Queries events from past 7 days
   - Groups by tier, sorts by significance

2. **LLM Summary Generation**
   - Prompt: "Summarize this week's top 5 AGI progress events"
   - Include: A/B tier highlights, C/D tier "if true" section
   - Generate: Executive summary (2-3 paragraphs)
   - Format: Plain text + HTML

3. **Email Integration**
   - Use SendGrid or Mailgun
   - Template: Clean, readable design
   - Sections: A/B tier highlights, C/D speculation, signpost updates
   - Footer: Unsubscribe link, methodology link

4. **Digest Archive**
   - Store in `public/digests/{YYYY-MM-DD}.json`
   - Display on `/digests` page
   - Show past 12 weeks
   - RSS feed for digest archive

**Success Metrics:**
- [ ] Digest generated every Sunday
- [ ] Email sent to subscribers
- [ ] Open rate >30%
- [ ] Archive page shows past digests
- [ ] LLM cost < $1 per digest

**Files to create:**
- `services/etl/app/tasks/digest/generate_digest.py`
- `services/etl/app/services/email_sender.py`
- `apps/web/app/digests/page.tsx`
- Email template: `services/etl/app/templates/digest.html`

---

### Task 7.3: Multi-Model Analysis Comparison

**Goal**: Compare outputs from different LLMs for more robust analysis

**What needs to be done:**

1. **Add Multi-Model Support**
   - Support: gpt-4o-mini, gpt-4o, claude-3-5-sonnet
   - Run same analysis through 2-3 models
   - Store all responses in `events_analysis` table
   - Track which model generated each analysis

2. **Consensus Analysis**
   - Compare significance scores across models
   - Flag high-variance events (models disagree)
   - Show "confidence in consensus" metric
   - Display divergent opinions to users

3. **Model Performance Tracking**
   - Track which model's predictions align best with:
     - Expert reviews
     - Later validation
     - User feedback
   - Auto-select best model per task

4. **Cost Optimization**
   - Use mini for routine events
   - Use gpt-4o for high-significance events
   - Use Claude for second opinions
   - Budget: $30/day across all models

**Success Metrics:**
- [ ] 2-3 models analyze each A/B tier event
- [ ] Consensus metric shown on EventCard
- [ ] High-variance events flagged for review
- [ ] Cost stays under $30/day
- [ ] Best-performing model identified per category

**Files to create:**
- `services/etl/app/services/multi_model_analysis.py`
- `services/etl/app/models.py` - Add model_name to EventAnalysis
- `apps/web/components/events/ConsensusIndicator.tsx`

---

## 🔒 Sprint 8: Security & Compliance (5-7 hours)

### Task 8.1: API Rate Limiting & Authentication

**Goal**: Protect API from abuse and prepare for public usage

**What needs to be done:**

1. **Enhance Rate Limiting**
   - Current: 120 req/min (SlowAPI)
   - Add per-IP limits
   - Add API key-based limits (higher for authenticated)
   - Track usage per key

2. **API Key Management**
   - Add `/v1/admin/api-keys` endpoints
   - Create, list, revoke keys
   - Track usage stats per key
   - Expire inactive keys after 90 days

3. **Public vs Authenticated Tiers**
   - Public: 60 req/min, basic endpoints only
   - Authenticated: 300 req/min, all endpoints
   - Admin: Unlimited, admin endpoints

4. **Usage Dashboard**
   - Show API usage stats
   - Top consumers
   - Rate limit violations
   - Error rates by endpoint

**Success Metrics:**
- [ ] Rate limits enforced per IP and API key
- [ ] Admin can create/revoke keys
- [ ] Usage tracked in dashboard
- [ ] No abuse incidents

**Files to create:**
- `services/etl/app/models.py` - Add APIKey table
- `services/etl/app/middleware/auth.py` - Enhanced auth
- `apps/web/app/admin/api-keys/page.tsx`

---

### Task 8.2: PII Scrubbing & GDPR Compliance

**Goal**: Ensure no personally identifiable information is stored or exposed

**What needs to be done:**

1. **Audit Data Storage**
   - Review all database tables for PII
   - Check: emails, names, IP addresses in logs
   - Identify retention policies needed

2. **Implement Scrubbing**
   - Remove/redact PII from logs
   - Already exists: Sentry scrubbing in `observability.py`
   - Add to database ingestion pipeline
   - Anonymize IP addresses in rate limiting

3. **Privacy Policy & Terms**
   - Create `/legal/privacy` page
   - Create `/legal/terms` page
   - Add cookie consent banner
   - Link in footer

4. **Data Retention**
   - Set TTL for logs (30 days)
   - Archive old events (>1 year) to cold storage
   - Automated cleanup task

**Success Metrics:**
- [ ] No PII in database
- [ ] Privacy policy published
- [ ] Cookie consent working
- [ ] GDPR compliant

**Files to create:**
- `apps/web/app/legal/privacy/page.tsx`
- `apps/web/app/legal/terms/page.tsx`
- `apps/web/components/CookieConsent.tsx`

---

## 📈 Sprint 9: Performance & Scale (5-8 hours)

### Task 9.1: Database Query Optimization

**Goal**: Ensure <100ms query times as data scales to 10,000+ events

**What needs to be done:**

1. **Run Performance Audit**
   - Use `EXPLAIN ANALYZE` on slow queries
   - Identify missing indexes
   - Find N+1 query problems

2. **Add Missing Indexes**
   - Migration already created: `add_performance_indexes.py`
   - But needs proper revision chain (was deleted)
   - Re-create with correct `down_revision`
   - Test index effectiveness

3. **Implement Query Caching**
   - Already exists: FastAPI-cache with Redis
   - Optimize TTLs per endpoint:
     - `/v1/index`: 3600s (1 hour)
     - `/v1/events`: 300s (5 min)
     - `/v1/signposts`: 3600s (1 hour)
   - Add cache warming for popular queries

4. **Add Pagination**
   - Current: max 100 events
   - Add cursor-based pagination
   - Return `next_cursor`, `prev_cursor`
   - Frontend: Infinite scroll

**Success Metrics:**
- [ ] P95 response time < 100ms for list endpoints
- [ ] P95 response time < 50ms for detail endpoints
- [ ] Cache hit rate > 70%
- [ ] Pagination supports 10,000+ events

**Files to modify:**
- `infra/migrations/versions/` - Re-create performance indexes migration
- `services/etl/app/main.py` - Add cursor pagination
- `apps/web/app/events/page.tsx` - Infinite scroll

---

### Task 9.2: Frontend Performance Optimization

**Goal**: Achieve Lighthouse score >90 on all pages

**What needs to be done:**

1. **Code Splitting**
   - Lazy load heavy components (Timeline charts)
   - Dynamic imports for EventCard analysis sections
   - Split by route

2. **Image Optimization**
   - Use Next.js Image component
   - Optimize signpost icons
   - Add loading placeholders

3. **Bundle Size Reduction**
   - Analyze with `npm run analyze`
   - Remove unused dependencies
   - Tree-shake Recharts (only import needed components)

4. **Caching Strategy**
   - Add service worker for offline capability
   - Cache static assets (1 year)
   - Cache API responses (5 minutes)
   - Implement stale-while-revalidate

**Success Metrics:**
- [ ] Lighthouse Performance > 90
- [ ] Time to Interactive < 3s
- [ ] Bundle size < 500KB
- [ ] Works offline (basic functionality)

**Files to modify:**
- `apps/web/next.config.js` - Bundle analyzer
- `apps/web/app/timeline/page.tsx` - Lazy load charts
- `apps/web/public/sw.js` - Service worker (new)

---

## 🎨 Sprint 10: UX Enhancements (6-8 hours)

### Task 10.1: Enhanced Search & Filtering

**Goal**: Make it easy to find specific events and signposts

**What needs to be done:**

1. **Full-Text Search**
   - Add PostgreSQL full-text search
   - Index: event title, summary, publisher
   - Endpoint: `/v1/events/search?q={query}`
   - Support: AND, OR, phrase matching

2. **Advanced Filters**
   - Date range picker (not just presets)
   - Multiple tier selection (A+B, not just one)
   - Signpost category filter
   - Significance threshold slider
   - Combine filters (AND logic)

3. **Saved Searches**
   - Allow users to save filter combinations
   - Store in localStorage
   - Quick-access buttons
   - Share via URL params

4. **Search Suggestions**
   - Autocomplete for signpost names
   - Recent searches
   - Popular searches
   - Typo tolerance

**Success Metrics:**
- [ ] Full-text search returns results <100ms
- [ ] Advanced filters work correctly
- [ ] Users can save searches
- [ ] Autocomplete works

**Files to create:**
- `services/etl/app/utils/search.py` - Full-text search helpers
- `apps/web/components/events/AdvancedFilters.tsx`
- `apps/web/hooks/useSavedSearches.ts`

---

### Task 10.2: Mobile Responsiveness Audit

**Goal**: Perfect mobile experience (already good, make it great)

**What needs to be done:**

1. **Mobile-Specific Testing**
   - Test on iPhone, Android
   - Test on tablet
   - Check touch targets (min 44x44px)
   - Verify swipe gestures work

2. **Timeline Mobile View**
   - Current scatter plot may be hard to read on mobile
   - Add mobile-optimized view (vertical timeline)
   - Swipe between events
   - Pinch to zoom

3. **Event Card Mobile Layout**
   - Optimize for small screens
   - Collapsible sections work smoothly
   - "Why this matters" expands nicely
   - Share button (native share API)

4. **Performance on Mobile**
   - Reduce initial bundle size
   - Lazy load images
   - Defer non-critical JS
   - Target: <3s load on 3G

**Success Metrics:**
- [ ] All pages work on mobile
- [ ] Touch targets meet WCAG standards
- [ ] Timeline has mobile-specific view
- [ ] Load time < 3s on 3G
- [ ] Lighthouse mobile score > 85

**Files to modify:**
- `apps/web/app/timeline/page.tsx` - Mobile timeline view
- `apps/web/components/events/EventCard.tsx` - Mobile optimizations
- `apps/web/app/globals.css` - Mobile breakpoints

---

## 🔮 Sprint 11: Scenario Explorer (Phase 6 Feature) (10-15 hours)

### Task 11.1: What-If Scenario Analysis

**Goal**: Let users explore different AGI timeline scenarios

**What needs to be done:**

1. **Scenario Builder UI**
   - New page: `/scenarios`
   - Sliders to adjust:
     - Compute scaling rate
     - Algorithmic improvements rate
     - Policy restrictions
     - Funding levels
   - Real-time index recalculation

2. **Scenario Simulation Backend**
   - Endpoint: `/v1/scenarios/simulate`
   - Input: Parameter adjustments
   - Output: Projected index values, timeline shifts
   - Use Monte Carlo simulation (1000 runs)

3. **Scenario Comparison**
   - Compare 2-3 scenarios side-by-side
   - Show: Timeline shifts, index differences
   - Highlight: Which signposts affected most
   - Visualize: Probability distributions

4. **Save & Share Scenarios**
   - Save scenario configurations
   - Generate shareable URLs
   - Public gallery of interesting scenarios
   - Upvote/comment system

**Success Metrics:**
- [ ] Users can create custom scenarios
- [ ] Simulations complete <3s
- [ ] Scenarios shareable via URL
- [ ] Gallery has 10+ community scenarios

**Files to create:**
- `apps/web/app/scenarios/page.tsx` - Scenario builder
- `services/etl/app/services/scenario_simulator.py`
- `services/etl/app/models.py` - SavedScenario table
- `apps/web/components/scenarios/ScenarioComparison.tsx`

---

### Task 11.2: AI Analyst Chatbot (RAG)

**Goal**: Let users ask questions about AGI progress data

**What needs to be done:**

1. **Vector Database Setup**
   - Already have pgvector extension
   - Create embeddings for:
     - All events (title + summary)
     - All signposts (description + methodology)
     - Key papers abstract
   - Store in existing `embedding` columns

2. **RAG Implementation**
   - Endpoint: `/v1/chat`
   - Input: User question
   - Process:
     1. Embed question
     2. Find similar events/signposts (cosine similarity)
     3. Build context from top 5 results
     4. Call LLM with context
     5. Return answer with citations

3. **Chat UI**
   - New page: `/chat`
   - Chat interface (messages)
   - Show sources for each answer
   - "Ask follow-up" feature
   - Export conversation

4. **Example Questions**
   - "What's the latest on SWE-bench progress?"
   - "Which labs are ahead of Aschenbrenner's timeline?"
   - "Show me all A-tier events from last month"
   - "What surprised us most this quarter?"

**Success Metrics:**
- [ ] Chatbot answers questions accurately
- [ ] Sources cited for all claims
- [ ] Response time < 5s
- [ ] User satisfaction > 80%
- [ ] Cost < $0.10 per conversation

**Files to create:**
- `services/etl/app/services/rag_chat.py`
- `services/etl/app/tasks/embeddings/generate_embeddings.py`
- `apps/web/app/chat/page.tsx`
- `apps/web/components/chat/ChatInterface.tsx`

---

## 📦 Deliverables Checklist

### Sprint 4: Production Automation
- [ ] 3 Railway services deployed (API, worker, beat)
- [ ] Redis added and connected
- [ ] Tasks running on schedule
- [ ] Task monitoring dashboard
- [ ] 48 hours of zero manual intervention

### Sprint 5: Intelligence & Predictions
- [ ] LLM extracts predictions from PDFs
- [ ] Mapper F1 >= 0.80 on golden set
- [ ] Surprise score dashboard live
- [ ] 50+ predictions from 8 sources

### Sprint 6: Data Quality & Credibility
- [ ] Retraction monitoring active
- [ ] Source credibility tracked daily
- [ ] Golden set expanded to 50 examples
- [ ] CI/CD tests running

### Sprint 7: Advanced Features
- [ ] Live news scraping (no fixtures)
- [ ] Weekly digest emails sent
- [ ] 50+ real events/week ingested

### Sprint 8: Security & Compliance
- [ ] API keys working
- [ ] Privacy policy published
- [ ] GDPR compliant

### Sprint 9: Performance & Scale
- [ ] Query times < 100ms
- [ ] Lighthouse > 90
- [ ] Cursor pagination

### Sprint 10: UX Enhancements
- [ ] Full-text search
- [ ] Mobile optimized
- [ ] Advanced filters

### Sprint 11: Scenario Explorer
- [ ] What-if scenarios
- [ ] AI chatbot working

---

## 🚀 How to Use This Document

**For Agent Execution:**

1. Start with **Sprint 4.1** (Celery workers) - Highest priority
2. Work through sprints sequentially
3. Test each feature before moving on
4. Commit frequently with descriptive messages
5. Update this document with ✅ as tasks complete

**For Human Review:**

- Review PRs for each sprint
- Test deployments on staging first
- Approve environment variable changes
- Monitor costs (especially LLM usage)

---

## 💰 Budget Estimates

| Sprint | LLM Cost | Infrastructure | Total |
|--------|----------|---------------|-------|
| Sprint 4 | $0 | $10/mo (Railway workers) | $10/mo |
| Sprint 5 | $10 one-time + $5/day ongoing | - | $160/mo |
| Sprint 6 | $2/day | - | $60/mo |
| Sprint 7 | $5/day | $5/mo (SendGrid) | $155/mo |
| Sprint 8-10 | $0 | - | - |
| Sprint 11 | $10/day | - | $300/mo |
| **TOTAL** | **~$20/day** | **~$25/mo** | **~$625/mo** |

**Cost Controls:**
- Daily LLM budget: $50 hard limit
- Railway: $20/mo estimate (actual usage-based)
- Can reduce by using mini over gpt-4o

---

## ⏰ Timeline Estimate

**If agent works continuously:**
- Sprint 4: 1-2 days
- Sprint 5: 2-3 days
- Sprint 6: 1-2 days
- Sprint 7: 2-3 days
- Sprints 8-11: 3-5 days

**Total: 2-3 weeks of agent time**

**If done in parallel with other work:**
- 4-6 weeks calendar time
- Can prioritize critical features first

---

## 🎯 Priority Ranking

**Must Have (Do First):**
1. ⭐⭐⭐ Task 4.1 - Celery Workers (enables automation)
2. ⭐⭐⭐ Task 6.2 - Source Credibility (data quality)
3. ⭐⭐ Task 7.1 - Live Scraping (remove fixtures)

**Should Have (Do Second):**
4. ⭐⭐ Task 5.1 - Forecast Extraction (more predictions)
5. ⭐⭐ Task 5.2 - Mapper Improvement (quality)
6. ⭐⭐ Task 6.1 - Retraction Monitoring (credibility)

**Nice to Have (Do Third):**
7. ⭐ Task 7.2 - Weekly Digest (user engagement)
8. ⭐ Task 5.3 - Surprise Dashboard (insights)
9. ⭐ Task 4.2 - Task Monitoring (ops)

**Future (Phase 6+):**
10. Task 11.1 - Scenario Explorer
11. Task 11.2 - AI Chatbot
12. Task 10.1 - Enhanced Search
13. Sprints 8-10 - Security, Performance, UX polish

---

## 📝 Agent Prompt Template

When delegating to an agent, use this prompt:

```
I need help implementing Phase 2 of the AGI Tracker project. 

Please work through AGENT_TASKS_PHASE_2.md starting with Sprint 4 (Production Automation).

Context:
- Backend API is live at: https://agi-tracker-production.up.railway.app
- Frontend is live at: https://agi-tracker.vercel.app
- Database migrations are current
- All Sprint 1-3 features are deployed and working

Start with Task 4.1 (Celery Workers) and work sequentially through the sprints.
Commit frequently, test thoroughly, and update the checklist as you go.

Only stop when you hit a blocker that requires my manual intervention (like adding Railway environment variables).

Good luck!
```

---

## 🎉 Summary

This document provides a comprehensive roadmap for the next 2-3 weeks of development:

- ✅ **Sprint 4**: Production automation (Celery)
- ✅ **Sprint 5**: Intelligence features (LLM predictions, mapper)
- ✅ **Sprint 6**: Data quality (retractions, credibility)
- ✅ **Sprint 7**: Advanced features (live scraping, digest)
- ✅ **Sprints 8-11**: Security, performance, UX, scenario explorer

**Total scope**: 60-80 hours of development work across 11 sprints.

**Result**: World-class AGI progress tracker with full automation, high-quality data, and advanced intelligence features.

**Ready to start? Begin with Sprint 4.1!** 🚀

