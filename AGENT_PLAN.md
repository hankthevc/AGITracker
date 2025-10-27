# AGI Tracker: News Pipeline Implementation Plan

**Status**: Ready for Cursor Agent execution  
**Backend**: https://agi-tracker-api-production.up.railway.app  
**Frontend**: https://agi-tracker.vercel.app  
**Database**: Neon PostgreSQL (connected)

---

## Mission

Implement comprehensive news ingestion → event mapping → forecast comparison pipeline following evidence-first principles: **A/B tier moves gauges, C/D tier NEVER moves gauges**.

---

## Pre-Execution Checklist

Before starting, verify:
- [ ] Railway backend is running (`curl https://agi-tracker-api-production.up.railway.app/health`)
- [ ] Database is connected (check `/v1/index` returns data)
- [ ] CORS allows Vercel origin (`https://agi-tracker.vercel.app`)
- [ ] Git status is clean (`git status`)

---

## Implementation Plan

### **Phase 0: Pre-Flight Audit** (Print Only)

**Goal**: Verify environment and current state

**Actions**:
1. Print repo basics:
   ```bash
   git rev-parse --short HEAD
   python3 --version
   node --version
   ```

2. Print tree structure (top-level):
   ```bash
   ls -la | grep -E '^d' | awk '{print $9}'
   ```

3. Verify critical files exist (print ✅/❌):
   - `REAL_NEWS_SAMPLE.json`
   - `fetch_real_news_now.py`
   - `apps/web/app/page.tsx`
   - `services/etl/app/main.py`
   - `.env.example`

4. Test health endpoints:
   ```bash
   curl -s https://agi-tracker-api-production.up.railway.app/health
   curl -s "https://agi-tracker-api-production.up.railway.app/v1/index?preset=equal" | head -20
   ```

**Verify**: Print compact summary with all checks

**Commit**: Not needed (audit only)

---

### **Phase A: Data Model for News/Events**

**Goal**: Create idempotent Alembic migration for events pipeline

**A1. Create Migration**

File: `infra/migrations/versions/016_news_events_pipeline.py`

Tables to create:

```python
# events (extend existing or create new)
- id: PK (already exists)
- title: TEXT (already exists)
- summary: TEXT (already exists)
- source_url: TEXT (already exists)
- source_domain: TEXT (NEW - extract from source_url)
- source_type: ENUM {paper, blog, news, leaderboard, gov} (may exist as string)
- outlet_cred: ENUM {A, B, C, D} (NEW - maps to evidence_tier)
- published_at: TIMESTAMPTZ (already exists)
- ingested_at: TIMESTAMPTZ DEFAULT now() (NEW)
- content_text: TEXT NULL (NEW - full article text)
- author: TEXT NULL (NEW)
- lang: TEXT NULL (NEW - default 'en')
- retracted: BOOLEAN DEFAULT false (already exists)
- created_at: TIMESTAMPTZ DEFAULT now() (may exist)
- dedup_hash: TEXT UNIQUE (NEW - computed from normalized_title + source_domain + date)

# event_signpost_links (already exists, verify columns)
- event_id: FK (exists)
- signpost_id: FK (exists)
- link_type: ENUM {supports, contradicts, related} (NEW)
- confidence: FLOAT 0..1 (exists)
- tier: ENUM {A, B, C, D} (NEW - redundant with event.outlet_cred but denormalized)
- provisional: BOOLEAN (exists)
- observed_at: TIMESTAMPTZ (NEW - when link was created)
- value: FLOAT NULL (exists)
- rationale: TEXT (exists)
- created_at: TIMESTAMPTZ DEFAULT now() (exists)
- PK: (event_id, signpost_id) (exists)

# ingest_runs (NEW table)
- id: SERIAL PK
- connector_name: TEXT (e.g., 'arxiv', 'lab_blogs', 'wire_services')
- started_at: TIMESTAMPTZ
- finished_at: TIMESTAMPTZ NULL
- status: ENUM {success, fail, running}
- new_events_count: INTEGER DEFAULT 0
- new_links_count: INTEGER DEFAULT 0
- error: TEXT NULL
- created_at: TIMESTAMPTZ DEFAULT now()
```

Indexes:
```sql
CREATE INDEX IF NOT EXISTS idx_events_published_at ON events(published_at DESC);
CREATE INDEX IF NOT EXISTS idx_events_outlet_cred ON events(outlet_cred);
CREATE INDEX IF NOT EXISTS idx_events_dedup_hash ON events(dedup_hash) WHERE dedup_hash IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_event_signpost_links_signpost_observed ON event_signpost_links(signpost_id, observed_at DESC);
CREATE INDEX IF NOT EXISTS idx_ingest_runs_connector ON ingest_runs(connector_name, started_at DESC);
```

**Migration Requirements**:
- Use `IF NOT EXISTS` for all `ADD COLUMN` statements (idempotent)
- Check if columns already exist before adding
- Use `op.execute()` for conditional DDL

**Verify**:
```bash
cd infra/migrations
python3 -m alembic upgrade head
python3 -m alembic current
psql $DATABASE_URL -c "\dt events*"
psql $DATABASE_URL -c "\d events" | grep -E "dedup_hash|source_domain|outlet_cred"
```

**Commit**: `feat: Add news events pipeline data model (Phase A)`

---

### **Phase B: Ingestors (Fixture-First)**

**Goal**: Build 4 ingestion connectors that work with fixtures (no live scraping yet)

**B1. arXiv Connector (A-tier, papers)**

File: `services/etl/app/tasks/news/ingest_arxiv.py`

```python
@celery_app.task(name="ingest_arxiv")
def ingest_arxiv(use_fixtures: bool = True):
    """Ingest arXiv papers from fixtures or live feed."""
    if use_fixtures:
        # Read from infra/fixtures/arxiv/*.json
        data = load_fixture("arxiv/cs_ai_sample.json")
    else:
        # Live fetch (Phase B later)
        if not os.getenv("ARXIV_REAL"):
            raise ValueError("Live arXiv requires ARXIV_REAL=true")
        data = fetch_arxiv_live()
    
    for entry in data:
        event = upsert_event(
            title=entry["title"],
            summary=entry["summary"],
            source_url=entry["url"],
            source_domain="arxiv.org",
            source_type="paper",
            outlet_cred="A",
            published_at=entry["published"],
            author=", ".join(entry.get("authors", [])),
            dedup_hash=compute_dedup_hash(entry)
        )
```

**Verify**:
```bash
# Run with fixtures
python3 -m pytest services/etl/tests/test_ingest_arxiv.py -v
# Check DB
psql $DATABASE_URL -c "SELECT COUNT(*) FROM events WHERE source_type='paper'"
```

**B2. Lab Blogs Connector (B-tier, blog)**

File: `services/etl/app/tasks/news/ingest_lab_blogs.py`

Sources: OpenAI, Anthropic, Google DeepMind, Meta AI, xAI, Cohere, Mistral

Fixture: `infra/fixtures/labs/*.json`

```python
@celery_app.task(name="ingest_lab_blogs")
def ingest_lab_blogs(use_fixtures: bool = True):
    """Ingest lab blog posts."""
    for lab in ["openai", "anthropic", "deepmind", "meta", "xai", "cohere", "mistral"]:
        if use_fixtures:
            data = load_fixture(f"labs/{lab}.json")
        else:
            if not os.getenv("LABS_REAL"):
                raise ValueError("Live labs require LABS_REAL=true")
            data = fetch_lab_blog_live(lab)
        
        for post in data:
            event = upsert_event(
                title=post["title"],
                summary=post.get("summary", ""),
                source_url=post["url"],
                source_domain=f"{lab}.com",
                source_type="blog",
                outlet_cred="B",
                published_at=post["date"],
                dedup_hash=compute_dedup_hash(post)
            )
```

**B3. Wire Services Connector (C-tier, news)**

File: `services/etl/app/tasks/news/ingest_wire_services.py`

Sources: Reuters, AP (AI/tech sections only)

Fixture: `infra/fixtures/wires/*.json`

```python
@celery_app.task(name="ingest_wire_services")
def ingest_wire_services(use_fixtures: bool = True):
    """Ingest wire service news."""
    for wire in ["reuters", "ap"]:
        if use_fixtures:
            data = load_fixture(f"wires/{wire}.json")
        else:
            if not os.getenv("WIRE_REAL"):
                raise ValueError("Live wire requires WIRE_REAL=true")
            data = fetch_wire_live(wire)
        
        for article in data:
            event = upsert_event(
                title=article["title"],
                summary=article.get("summary", ""),
                source_url=article["url"],
                source_domain=f"{wire}.com",
                source_type="news",
                outlet_cred="C",  # C-tier: "If true" only, never moves gauges
                published_at=article["date"],
                dedup_hash=compute_dedup_hash(article)
            )
```

**B4. Leaderboard Events (A-tier, leaderboard)**

File: `services/etl/app/tasks/news/ingest_leaderboard_events.py`

```python
@celery_app.task(name="emit_leaderboard_event")
def emit_leaderboard_event(benchmark: str, old_sota: float, new_sota: float, paper_url: str):
    """Emit an event when SOTA changes on a benchmark."""
    event = upsert_event(
        title=f"New SOTA on {benchmark}: {new_sota:.1f}% (was {old_sota:.1f}%)",
        summary=f"Leaderboard update: {benchmark} improved from {old_sota:.1f}% to {new_sota:.1f}%",
        source_url=paper_url,
        source_domain=get_domain(paper_url),
        source_type="leaderboard",
        outlet_cred="A",  # Leaderboards are A-tier evidence
        published_at=datetime.utcnow(),
        dedup_hash=f"{benchmark}_{new_sota}_{date.today()}"
    )
    
    # Auto-link to corresponding signpost
    signpost = find_signpost_for_benchmark(benchmark)
    if signpost:
        link_event_to_signpost(
            event_id=event.id,
            signpost_id=signpost.id,
            link_type="supports",
            confidence=0.9,
            tier="A",
            provisional=False,
            value=new_sota
        )
```

**B5. Ingest Run Audit**

Add helper: `services/etl/app/utils/ingest_tracking.py`

```python
from contextlib import contextmanager

@contextmanager
def track_ingest_run(connector_name: str, db: Session):
    """Context manager to track ingestion runs."""
    run = IngestRun(
        connector_name=connector_name,
        started_at=datetime.utcnow(),
        status="running"
    )
    db.add(run)
    db.commit()
    
    try:
        yield run
        run.status = "success"
        run.finished_at = datetime.utcnow()
    except Exception as e:
        run.status = "fail"
        run.error = str(e)
        run.finished_at = datetime.utcnow()
        raise
    finally:
        db.commit()
```

**Verify**:
```bash
# Run all ingestors with fixtures
make backfill-news

# Check results
psql $DATABASE_URL -c "
  SELECT source_type, outlet_cred, COUNT(*) 
  FROM events 
  GROUP BY source_type, outlet_cred 
  ORDER BY outlet_cred, source_type
"

psql $DATABASE_URL -c "
  SELECT connector_name, status, new_events_count 
  FROM ingest_runs 
  ORDER BY started_at DESC 
  LIMIT 10
"
```

**Commit**: `feat: Add news ingestors (arxiv, labs, wire, leaderboards) (Phase B)`

---

### **Phase C: Rule-First Mapper**

**Goal**: Map events to signposts using aliases/regex rules (60+ entries), with LLM fallback optional

**C1. Mapping Rules**

File: `infra/seeds/mapping_rules.yaml`

```yaml
# Capabilities signposts
- aliases: ["SWE-bench Verified", "SWE-bench-verified", "SWEbench verified"]
  pattern: "SWE[-\\s]?bench\\s+[Vv]erified"
  signpost_code: "capabilities_swe_bench"
  confidence_base: 0.7
  tier_boost: {A: 0.2, B: 0.1}

- aliases: ["OSWorld", "OS-World"]
  pattern: "OSWorld|OS[-\\s]?World"
  signpost_code: "capabilities_os_world"
  confidence_base: 0.7

- aliases: ["WebArena", "VisualWebArena", "Web Arena"]
  pattern: "(Visual)?Web[-\\s]?Arena"
  signpost_code: "capabilities_web_arena"
  confidence_base: 0.7

- aliases: ["GPQA Diamond", "GPQA-Diamond"]
  pattern: "GPQA\\s+Diamond"
  signpost_code: "capabilities_gpqa"
  confidence_base: 0.7

- aliases: ["HLE", "human-level evaluation", "human level eval"]
  pattern: "HLE|human[-\\s]?level\\s+(evaluation|eval)"
  signpost_code: "capabilities_hle"
  confidence_base: 0.5
  monitor_only: true  # HLE never moves gauges

# Inputs signposts
- aliases: ["10^26 FLOP", "1e26 FLOP", "10e26 FLOP"]
  pattern: "(10\\^26|1e26|10e26)\\s*FLOP"
  signpost_code: "inputs_flops_26"
  confidence_base: 0.8
  value_extract: true  # Try to extract numeric value

- aliases: ["10^27 FLOP", "1e27 FLOP"]
  pattern: "(10\\^27|1e27)\\s*FLOP"
  signpost_code: "inputs_flops_27"
  confidence_base: 0.8

- aliases: ["1 GW", "1GW", "gigawatt"]
  pattern: "1\\s*GW|gigawatt"
  signpost_code: "inputs_dc_power_1gw"
  confidence_base: 0.7

# Security signposts
- aliases: ["weight security", "model weights", "HSM", "hardware security module"]
  pattern: "(weight|model)\\s+security|HSM|hardware\\s+security\\s+module"
  signpost_code: "security_weights"
  confidence_base: 0.6

- aliases: ["red team", "red-team", "adversarial testing"]
  pattern: "red[-\\s]?team|adversarial\\s+testing"
  signpost_code: "security_red_team"
  confidence_base: 0.6

# ... (add 60+ total entries)
```

**C2. Event Mapper**

File: `services/etl/app/utils/event_mapper.py`

```python
def map_event_to_signposts(
    event: Event, 
    rules: List[MappingRule], 
    db: Session,
    max_links: int = 2
) -> List[EventSignpostLink]:
    """
    Map event to signposts using rules.
    
    Confidence calculation:
    - Start with rule's confidence_base (0.5-0.8)
    - +0.2 if numeric value extracted (e.g., "achieved 95.3%")
    - +0.2 if multiple independent cues (e.g., title + summary mention)
    - Tier boost: A +0.2, B +0.1, C/D +0.0
    - Cap at 0.95
    
    Tier inheritance:
    - Link tier = event.outlet_cred (A/B/C/D)
    
    Provisional rules:
    - A-tier: provisional=False (direct evidence)
    - B-tier: provisional=True initially
      → If A-tier corroboration arrives within 14 days: bump confidence, clear provisional
    - C/D-tier: Always provisional=True, NEVER moves gauges
    
    Gauge movement rules:
    - Only A/B tier links can move gauges
    - Only if signpost.first_class=True
    - C/D links are "If true" only (displayed but ignored in scoring)
    
    Returns:
    - List of EventSignpostLink objects (max 2 per event to avoid over-linking)
    """
    links = []
    text = f"{event.title} {event.summary or ''}".lower()
    
    for rule in rules:
        # Check if rule matches
        if not matches_rule(text, rule):
            continue
        
        # Find signpost
        signpost = db.query(Signpost).filter(
            Signpost.code == rule.signpost_code
        ).first()
        if not signpost:
            continue
        
        # Skip if monitor-only (e.g., HLE)
        if rule.get("monitor_only"):
            continue
        
        # Calculate confidence
        confidence = rule.confidence_base
        
        # Boost for value extraction
        value = extract_numeric_value(text, rule)
        if value:
            confidence += 0.2
        
        # Boost for multiple cues
        if count_mentions(text, rule) >= 2:
            confidence += 0.2
        
        # Tier boost
        tier_boost = {"A": 0.2, "B": 0.1, "C": 0.0, "D": 0.0}
        confidence += tier_boost.get(event.outlet_cred, 0)
        
        # Cap at 0.95
        confidence = min(confidence, 0.95)
        
        # Determine provisional status
        provisional = event.outlet_cred in ["C", "D"]  # C/D always provisional
        if event.outlet_cred == "B":
            provisional = True  # B starts provisional, needs A corroboration
        
        # Create link
        link = EventSignpostLink(
            event_id=event.id,
            signpost_id=signpost.id,
            link_type="supports",  # Default, could be enhanced later
            confidence=confidence,
            tier=event.outlet_cred,
            provisional=provisional,
            observed_at=datetime.utcnow(),
            value=value,
            rationale=f"Matched rule: {rule.pattern}",
            created_at=datetime.utcnow()
        )
        links.append(link)
        
        # Stop at max_links
        if len(links) >= max_links:
            break
    
    return links
```

**C3. B-tier Corroboration Logic**

File: `services/etl/app/utils/corroboration.py`

```python
def check_b_tier_corroboration(db: Session):
    """
    Check if any B-tier links can be corroborated by A-tier evidence.
    
    Rule: If B-tier link exists, and within 14 days an A-tier event
    links to the same signpost, upgrade the B-tier link:
    - provisional = False
    - confidence += 0.1 (boost for corroboration)
    """
    # Find B-tier provisional links
    b_links = db.query(EventSignpostLink).join(Event).filter(
        EventSignpostLink.tier == "B",
        EventSignpostLink.provisional == True,
        Event.outlet_cred == "B"
    ).all()
    
    for b_link in b_links:
        # Look for A-tier evidence on same signpost within 14 days
        cutoff = b_link.observed_at + timedelta(days=14)
        
        a_link = db.query(EventSignpostLink).join(Event).filter(
            EventSignpostLink.signpost_id == b_link.signpost_id,
            EventSignpostLink.tier == "A",
            Event.outlet_cred == "A",
            EventSignpostLink.observed_at >= b_link.observed_at,
            EventSignpostLink.observed_at <= cutoff
        ).first()
        
        if a_link:
            # Corroborate B-tier link
            b_link.provisional = False
            b_link.confidence = min(b_link.confidence + 0.1, 0.95)
            b_link.rationale += f" | Corroborated by A-tier event #{a_link.event_id}"
            db.commit()
```

**C4. Mapper Celery Task**

File: `services/etl/app/tasks/mapping/map_events_to_signposts.py`

```python
@celery_app.task(name="map_events_to_signposts")
def map_events_to_signposts():
    """Map unmapped events to signposts using rules."""
    db = SessionLocal()
    
    try:
        # Load rules
        rules = load_mapping_rules()
        
        # Find unmapped events
        unmapped = db.query(Event).outerjoin(EventSignpostLink).filter(
            EventSignpostLink.id == None,
            Event.retracted == False
        ).limit(100).all()
        
        stats = {
            "linked": 0,
            "needs_review": 0,
            "provisional_only": 0,
            "unmapped": 0
        }
        
        for event in unmapped:
            links = map_event_to_signposts(event, rules, db)
            
            if not links:
                stats["unmapped"] += 1
                continue
            
            for link in links:
                db.add(link)
                stats["linked"] += 1
                
                if link.confidence < 0.7:
                    link.needs_review = True
                    stats["needs_review"] += 1
                
                if link.provisional:
                    stats["provisional_only"] += 1
            
            db.commit()
        
        # Check for B-tier corroboration
        check_b_tier_corroboration(db)
        
        # Recompute index if any A/B first_class links were added
        recompute_index_if_needed(db)
        
        return stats
        
    finally:
        db.close()
```

**Verify**:
```bash
# Load rules
python3 scripts/load_mapping_rules.py

# Run mapper on fixtures
celery -A services.etl.app.celery_app call map_events_to_signposts

# Check results
psql $DATABASE_URL -c "
  SELECT 
    tier,
    COUNT(*) as total,
    SUM(CASE WHEN provisional THEN 1 ELSE 0 END) as provisional,
    SUM(CASE WHEN needs_review THEN 1 ELSE 0 END) as needs_review,
    AVG(confidence) as avg_confidence
  FROM event_signpost_links
  GROUP BY tier
  ORDER BY tier
"

# Sample 2 links
psql $DATABASE_URL -c "
  SELECT 
    e.title,
    s.code,
    esl.tier,
    esl.confidence,
    esl.provisional,
    esl.rationale
  FROM event_signpost_links esl
  JOIN events e ON esl.event_id = e.id
  JOIN signposts s ON esl.signpost_id = s.id
  LIMIT 2
" --json
```

**Commit**: `feat: Add rule-first event mapper with 60+ aliases (Phase C)`

---

### **Phase D: Forecast Comparison**

(Continue with Phases D-H following the same detailed structure...)

---

## Critical Guardrails (MUST FOLLOW)

### ❌ NEVER DO:
1. **Change scoring math** - Harmonic mean is sacred
2. **Let C/D tier move gauges** - C/D are "If true" only, display but don't score
3. **Remove HLE monitor-only flag** - HLE stays first_class=False
4. **Skip fixtures in CI** - Live scraping only behind *_REAL=true flags
5. **Ignore robots.txt** - Always respect, use polite UA
6. **Remove CC BY 4.0 from feeds** - Public feeds must have license

### ✅ ALWAYS DO:
1. **Commit after each subtask** - Small, verifiable diffs
2. **Run verification command** - Print compact log
3. **Print stats/sample data** - Show what was created
4. **Use IF NOT EXISTS** - All migrations idempotent
5. **A/B corroboration** - B-tier gets boost from A-tier within 14 days
6. **Max 2 links per event** - Avoid over-linking

---

## Verification Checklist

After all phases complete, verify:

- [ ] Events tables populated with dedup working
- [ ] Mapper links ≥ 60% of events with confidence ≥ 0.7
- [ ] A/B events can move gauges (only if signpost.first_class=True)
- [ ] C/D events NEVER move gauges (always provisional)
- [ ] Forecast chips render for ≥ 3 roadmaps on event detail
- [ ] Home strip, /news, event detail, signpost Events tab working
- [ ] Public vs research JSON feeds functional (license included)
- [ ] Golden-set F1 ≥ 0.75
- [ ] Unit + E2E tests green

---

## Notes

- **Current commit**: `0bfd08b`
- **Backend deployed**: Railway auto-deploys on push to main
- **Frontend deployed**: Vercel auto-deploys on push to main
- **Database**: Persistent, changes survive deployments
- **Celery**: Not yet running in Railway (will add in Phase G)

---

**Ready for agent execution!**

