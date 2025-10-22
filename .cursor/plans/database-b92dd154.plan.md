<!-- b92dd154-27fa-4d17-89d8-30046b0cb669 abd0c1d2-4bd9-4cac-840d-74864735e437 -->
# Database Migration Fix & System Restoration Plan

## Current Issues

### 1. Database Migration Not Applied

**Error**: `column "retracted_at" does not exist`

**Root Cause**: Migration `011_add_retraction_fields.py` exists but hasn't been applied to the database. The migration adds:

- `retracted_at` (TIMESTAMP)
- `retraction_reason` (TEXT)
- `retraction_evidence_url` (TEXT)
- Index on `retracted` column

**Location**:

- Migration file: ```infra/migrations/versions/011_add_retraction_fields.py```
- Query failing at: ```streamlit_app.py:216``` (attempts to select `retracted_at`)
- Model definition: ```services/etl/app/models.py:373-375``` (Event model has these fields)

### 2. Streamlit Real-Time Analytics Broken

The "Real-Time Analytics" section at line 238 of `streamlit_app.py` fails because it queries the `events` table with columns that don't exist in the database.

## Migration Chain Analysis

Current migration chain (from grep results):

```
001_initial_schema
  ↓
502dc116251e (fix index snapshots)
  ↓
003_add_rich_content
  ↓
004_roadmap_predictions
  ↓
6e2841a56cb2 (add events)
  ↓
007_enhance_events_schema
  ↓
008_add_outlet_cred_and_link_type
  ↓
009_add_link_approved_at (DUPLICATE!)
  ↓
009_add_review_fields (DUPLICATE revision!)
  ↓
010_add_is_synthetic
  ↓
20251020115049_phase0_foundations
  ↓
20251020115050_events_analysis
  ↓
20251020115051_phase23_stubs
```

**Issue**: Two migrations with revision `009` exist:

- `009_add_link_approved_at.py`
- `009_add_review_fields.py`

Migration `011_add_retraction_fields.py` has `down_revision = '009_add_review_fields'` but Alembic may be following the wrong chain.

## Solution Steps

### Step 1: Verify Current Database State

Check which migrations are actually applied:

```bash
cd /Users/HenryAppel/AI\ Doomsday\ Tracker
alembic current
alembic history
```

### Step 2: Fix Migration Chain

The migration chain has conflicts. Need to:

1. Rename conflicting `009` migrations to avoid collisions
2. Update `down_revision` pointers to create a linear chain
3. Ensure `011_add_retraction_fields` comes after the correct parent

Proposed rename:

- Keep `009_add_review_fields.py` as `009`
- Rename `009_add_link_approved_at.py` to `009a_add_link_approved_at.py`
- Update `010_add_is_synthetic_to_events.py` to point to correct parent

### Step 3: Apply Missing Migrations

```bash
# Navigate to project root
cd /Users/HenryAppel/AI\ Doomsday\ Tracker

# Apply migrations up to current head
alembic upgrade head

# Verify all applied
alembic current
```

### Step 4: Verify Database Schema

Check that all expected columns exist:

```sql
\d events
-- Should show: retracted_at, retraction_reason, retraction_evidence_url
```

### Step 5: Test Streamlit App

```bash
# Set DATABASE_URL if not in environment
export DATABASE_URL="postgresql+psycopg://..."

# Run Streamlit
streamlit run streamlit_app.py

# Navigate to "📰 News Feed" page
# Verify "Real-Time Analytics" section loads without errors
```

## Project State Assessment

Based on code review, the project has:

### ✅ Completed (Phases 0-5)

1. **Phase 0**: Database foundations, deduplication, monitoring
2. **Phase 1**: Events feed, AI analysis, timeline visualization
3. **Phase 2**: LLM-powered mapping with review queue
4. **Phase 3**: Expert predictions tracking (7 predictions seeded)
5. **Phase 4**: Pulse landing page, signpost deep-dives
6. **Phase 5**: Retraction workflow, source credibility, prompt audit

### 🔍 Current Data

- 9 real AI events (Sept 2023 - Dec 2024)
- 27 signposts across 4 categories
- 15 signpost mappings
- 12 roadmap predictions
- 12 RSS feeds configured

### 🚧 Known Issues

1. **Migration not applied** (blocks Streamlit)
2. **Duplicate migration revisions** (009 conflict)
3. **Limited real events** (only 9 events, mostly fixtures)
4. **Content expansion needed** (signpost citations, live news)

## Next Steps Recommendations

### Immediate (Critical Path)

1. **Fix migrations** (resolve 009 conflict, apply 011-014)
2. **Test Streamlit** (verify Real-Time Analytics works)
3. **Verify FastAPI** (ensure `/v1/events` endpoint works)

### Short-Term (Content Expansion)

4. **Populate signpost content** 

   - Run: `python scripts/load_signpost_content.py`
   - Uses: `infra/seeds/signpost_citations.yaml`
   - Populates: `signpost_content` table

5. **Backfill real news** (expand from 9 to 100+ events)

   - Run: `python scripts/backfill_live_news.py --days=180`
   - Enable: `SCRAPE_REAL=true`, `ENABLE_LLM_MAPPING=true`
   - Sources: 12 configured RSS feeds

6. **Test live ingestion**

   - Verify arXiv connector works
   - Test RSS parsing for all 12 feeds
   - Validate LLM fallback parsing

### Medium-Term (Phase 6 Prep)

7. **Multi-roadmap comparison** 

   - Timeline view showing events vs predictions
   - Accuracy scorecard for forecasters
   - Filter by roadmap (Aschenbrenner, AI2027, etc.)

8. **Leaderboard→Event connectors**

   - Auto-emit events when SOTA changes
   - Link with high confidence (0.95)
   - Track SWE-bench, GPQA, OSWorld

9. **Add governance sources**

   - AI Safety orgs (CAIS, FLI, CAP)
   - Government reports (NIST, EU AI Act)
   - Industry frameworks (Partnership on AI)

### Long-Term (Phase 6)

10. **Scenario Explorer** (interactive what-if)
11. **Multi-perspective analysis** (GPT-4 vs Claude vs Gemini)
12. **RAG chatbot** (Q&A with pgvector search)

## Risk Mitigation

### Migration Risks

- **Backup database before applying migrations**
- **Test migrations on local/staging first**
- **Keep rollback plan ready** (`alembic downgrade -1`)

### Data Quality Risks

- **Live scraping may fetch duplicates** (dedup is in place)
- **LLM costs may spike** (budget tracking exists in Redis)
- **Low-quality C/D tier may pollute feed** (tier filtering works)

## Success Criteria

### Immediate Success

- ✅ Alembic shows all migrations applied
- ✅ Streamlit loads without database errors
- ✅ Real-Time Analytics displays charts
- ✅ FastAPI `/v1/events` returns data with retraction fields

### Content Expansion Success

- ✅ 100+ real events from last 6 months
- ✅ All signposts have citations and "why matters"
- ✅ 50+ signpost mappings (up from 15)
- ✅ Live RSS ingestion running daily

## Files to Modify

### Critical Path (Migration Fix)

1. `infra/migrations/versions/009_add_link_approved_at.py` - rename to `009a`
2. `infra/migrations/versions/010_add_is_synthetic_to_events.py` - update `down_revision`
3. Run: `alembic upgrade head`

### Content Expansion

4. `scripts/load_signpost_content.py` - run to populate content
5. `scripts/backfill_live_news.py` - run with `SCRAPE_REAL=true`
6. Verify: `streamlit_app.py` Real-Time Analytics section

## Estimated Timeline

- **Migration fix**: 30 minutes
- **Verify Streamlit**: 15 minutes
- **Load signpost content**: 1 hour
- **Backfill 6 months of news**: 2-3 hours (API rate limits)
- **Test and validate**: 1 hour

**Total**: ~5-6 hours for full restoration and content expansion.

### To-dos

- [ ] Check current Alembic migration state and identify which migrations are applied
- [ ] Resolve duplicate 009 revision conflict by renaming and updating down_revision pointers
- [ ] Run alembic upgrade head to apply all missing migrations (011-014)
- [ ] Verify events table has retracted_at, retraction_reason, retraction_evidence_url columns
- [ ] Test Streamlit app and verify Real-Time Analytics section loads without errors
- [ ] Run load_signpost_content.py script to populate signpost_content table from signpost_citations.yaml
- [ ] Run backfill_live_news.py with SCRAPE_REAL=true to fetch 6 months of real events
- [ ] End-to-end validation: verify events load, analytics display, and FastAPI endpoints work