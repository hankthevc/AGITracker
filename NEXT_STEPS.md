# 🚀 AGI Signpost Tracker - Next Steps for Content Expansion

**Current Status:** 42 commits on main, Streamlit live with 9 real events

---

## ✅ What's Live Now

**Neon Database:**
- 9 real AI events (Sept 2023 - Dec 2024)
- 15 signpost mappings
- 27 signposts across 4 categories
- 12 roadmap predictions

**News Sources (Active):**
- Company blogs: OpenAI, Anthropic, Google DeepMind, Meta AI (fixtures)
- arXiv papers: SWE-bench, OSWorld, WebArena (fixtures)
- Press: Reuters, AP (fixtures)

**RSS Feeds Configured (12 total):**
- ✅ Major AI labs (6): OpenAI, Anthropic, Google, Meta, Cohere, Mistral
- ✅ Research orgs (2): Microsoft Research, Google Research  
- ✅ Open source (1): Hugging Face
- ✅ Compute (1): NVIDIA
- ✅ AI Safety (2): Anthropic Research, OpenAI Research

---

## 📋 Phase 1: Comprehensive Signpost Content (In Progress)

**Created:**
- ✅ `infra/seeds/signpost_citations.yaml` with academic citations
  - Source papers (arXiv IDs)
  - Methodology descriptions
  - Baseline SOTA values
  - Target rationales
  - Why each matters for AGI

**Next:**
- [ ] Loader script to populate `signpost_content` table
- [ ] Display citations on signpost detail pages
- [ ] Add "References" section with clickable paper links
- [ ] Monitor-only signposts (HLE) show upgrade criteria

---

## 📋 Phase 2: Expanded News Ingestion (In Progress)

**Completed:**
- ✅ 12 RSS/Atom feeds configured
- ✅ Live arXiv fetcher (fetch_arxiv_live.py)
- ✅ URL validation
- ✅ LLM fallback parsing (OpenAI integration)

**Next:**
- [ ] Test live RSS fetching (SCRAPE_REAL=true)
- [ ] Add governance sources:
  - AI Safety orgs (CAIS, FLI, Center for AI Policy)
  - Government reports (NIST AI RMF, EU AI Act updates)
  - Industry frameworks (Partnership on AI)
- [ ] Add leaderboard→event connectors:
  - Emit event when SOTA changes on tracked benchmarks
  - Auto-link with confidence=0.95
- [ ] Backfill last 6-12 months of real news

---

## 📋 Phase 3: Multi-Roadmap Mapping

**Planned:**
- [ ] Show which roadmap(s) each event relates to
- [ ] Timeline view: plot events on roadmap predictions chart
- [ ] Comparative analysis dashboard:
  - Which roadmap is proving most accurate?
  - Events ahead/on/behind each forecast
  - Confidence-weighted accuracy scores
- [ ] Export: "Roadmap Scorecard" showing prediction accuracy

---

## 🎯 Immediate Actions (High Impact)

### A. Populate Signpost Content (1-2 hours)
```bash
# Create loader
python3 scripts/load_signpost_content.py

# Updates signpost_content table with:
# - why_matters, current_state, key_papers, technical_explanation
```

### B. Test Live News Fetching (30 min)
```bash
export SCRAPE_REAL=true
export OPENAI_API_KEY='your-key'
export ENABLE_LLM_MAPPING=true

# Fetch from all 12 RSS feeds
python3 scripts/backfill_live_news.py --days=30
```

Expected: 50-100 real events from last month across all sources

### C. Add Leaderboard Events (1 hour)
```bash
# Extend existing leaderboard connectors
# When SOTA changes: create Event + EventSignpostLink
```

---

## 📊 Target End State

**News Aggregator:**
- 200+ real AI events from last 12 months
- 12+ active RSS/Atom sources
- Live arXiv integration (cs.AI/CL/LG/CV)
- Governance/policy sources
- Leaderboard change events

**Signpost Content:**
- Every signpost has:
  - Academic citation with paper link
  - "Why this matters" explanation
  - Current SOTA value
  - Methodology description
  - Key papers and announcements
  - Technical deep dive

**Multi-Roadmap View:**
- Events mapped to relevant roadmaps
- Timeline showing actual vs predicted
- Scorecard: which forecasters are most accurate
- Filter by roadmap (Aschenbrenner, AI-2027, Cotra, etc.)

---

## 🛠️ Technical Debt to Address

- [ ] Apply migrations 008-009 (outlet_cred, approved_at)
- [ ] Fix main.py syntax errors preventing FastAPI from loading
- [ ] Implement B-tier corroboration tracking (14-day window)
- [ ] Add rate limiting for live RSS fetching
- [ ] Implement URL verification for live mode (avoid dead links)

---

**Ready to continue?** Let me know which phase to tackle next!
