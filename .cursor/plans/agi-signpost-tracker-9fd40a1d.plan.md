<!-- 9fd40a1d-7f8c-4ea4-a095-79f00bd3a09c 46db5ce5-0929-4805-8657-ddd5959329b5 -->
# v0.2.1: CI Green + HLE Verification

## Pre-flight Results Summary

**PASSING (13/16)**:

- ✓ Admin endpoints canonicalized (/v1/admin/recompute + legacy 410)
- ✓ X-Request-ID and ETag headers present
- ✓ ETag variance by preset confirmed
- ✓ Beat schedule with fetch-hle at 08:02 UTC
- ✓ Task watchdog tracking fetch_hle
- ✓ HLE signposts seeded (first_class=False)
- ✓ Connector implements B-tier dual-source strategy
- ✓ UI shows HLE tile with Provisional badge
- ✓ .env.example has all required keys

**BLOCKING (1/16)**:

- ❌ **HLE benchmark (humanitys_last_exam_text) NOT in database**

**MINOR (3/16)**:

- ⚠️ 2 *_COMPLETE.md files at root (need archiving)
- ⚠️ CI status unknown (gh CLI not authenticated)
- ⚠️ Playwright artifact upload may fail

---

## P0: Critical Fixes & CI Reconciliation

### P0.1 Fix HLE Benchmark Seeding (BLOCKING)

**Issue**: `humanitys_last_exam_text` benchmark missing from database despite signposts existing.

**Root cause**: Seed script added benchmark to definition but DB insert may have failed silently or was skipped by idempotency check.

**Files**: `scripts/seed.py`

**Actions**:

1. Verify benchmark definition in seed.py (should exist with family="OTHER")
2. Add explicit debug logging to benchmark seeding section
3. Re-run seed script with verbose output
4. Verify benchmark appears in DB with `SELECT * FROM benchmarks WHERE code LIKE '%hle%'`

**Success criteria**: Query returns `humanitys_last_exam_text | Humanity's Last Exam (Text-Only) | OTHER`

### P0.2 Archive Root COMPLETE.md Files

**Issue**: 2 completion docs at root should be in docs/archive/

**Files to move**:

- `V0.2.1_IMPLEMENTATION_COMPLETE.md` → `docs/archive/`
- `VERIFICATION_LAUNCH_POLISH_COMPLETE.md` → `docs/archive/`

**Actions**:

1. `git mv V0.2.1_IMPLEMENTATION_COMPLETE.md docs/archive/`
2. `git mv VERIFICATION_LAUNCH_POLISH_COMPLETE.md docs/archive/`
3. Prepend banner to both files:
   ```markdown
   > **Archived note:** Non-authoritative; engineering must follow code & issues.
   
   ---
   ```

4. Update README to link docs/archive/ if not already present

### P0.3 Fix Playwright Artifact Upload

**Issue**: Artifact upload may fail if no report directory exists

**File**: `.github/workflows/ci.yml`

**Change**:

```yaml
- name: Upload test results
  uses: actions/upload-artifact@v4
  if: failure()
  with:
    name: playwright-report
    path: apps/web/playwright-report/
    retention-days: 7
    if-no-files-found: ignore  # Add this line
```

### P0.4 Verify CI Status

**Cannot automate** (gh CLI not authenticated)

**Manual steps**:

1. Visit https://github.com/hankthevc/AGITracker/actions
2. Check last 3 workflow runs
3. If failing, identify specific job/step
4. Document failure mode for P0.5

### P0.5 Fix CI if Failing (Conditional)

**Only if P0.4 reveals failures**

Common failure modes:

- Python dependencies: Ensure `pip install -e .[test]` or add missing test deps
- Playwright install: Already has `--with-deps` ✓
- Database migrations: Check Alembic path
- Port conflicts: Ensure unique ports or cleanup

---

## P1: HLE Integration Verification

### P1.1 Manual HLE Connector Test

**Goal**: Prove fetch_hle can execute end-to-end

**Steps**:

1. Ensure HLE benchmark is seeded (depends on P0.1)
2. Run connector manually:
   ```bash
   cd scripts
   python -c "
   import sys
   sys.path.insert(0, '../services/etl')
   from app.tasks.fetch_hle import fetch_hle
   result = fetch_hle()
   print(result)
   "
   ```

3. Verify output shows:

   - `status: success`
   - `credibility: B`
   - `claim_id: <number>`

4. Check DB: `SELECT * FROM claims WHERE metric_name = 'HLE Text Accuracy'`

**Success criteria**: At least 1 HLE claim in DB with source credibility='B'

### P1.2 Verify Monitor-Only Status

**Goal**: Prove HLE does NOT affect main composite gauge

**Test**:

1. Query current overall index: `curl -s 'http://localhost:8000/v1/index?preset=equal' | jq .overall`
2. Manually insert HLE claim with score=60% (or use existing from P1.1)
3. Trigger recompute: `curl -X POST -H "X-API-Key: changeme" http://localhost:8000/v1/admin/recompute`
4. Query overall index again
5. **Expected**: Overall score UNCHANGED (HLE is first_class=false)

**Success criteria**: Overall gauge unaffected by HLE claims

### P1.3 UI Integration Test

**Goal**: Verify HLE tile renders correctly

**Manual browser test**:

1. Visit http://localhost:3000/benchmarks
2. Scroll to HLE tile
3. Verify:

   - "Provisional" badge visible (orange bg)
   - Quality note present: "Bio/Chem subsets have known label-quality issues"
   - Current score displays (~37.5% or from P1.1)
   - "Monitor-Only" status badge

**E2E test** (already exists):

```bash
cd apps/web
npm run e2e -- benchmarks.spec.ts
```

Expected: Test "HLE tile shows provisional badge and quality note" passes

### P1.4 Unit Test Coverage

**Verify existing tests**:

```bash
cd services/etl
pytest tests/test_hle_parser.py -v
```

**Expected output**:

- `test_fetch_hle_scale_fixture` PASSED
- `test_fetch_hle_artificial_analysis_fixture` PASSED
- `test_hle_maps_to_signposts` PASSED
- `test_hle_claim_idempotency` PASSED
- `test_hle_credibility_b_tier` PASSED

**If any fail**: Debug and fix before proceeding

---

## P2: Acceptance Criteria Verification

All must pass before considering v0.2.1 complete:

### CI & Docs

- [ ] CI green on main (all 4 jobs pass: lint, unit-tests, e2e-tests, build)
- [ ] Root cleaned (no *_COMPLETE.md files)
- [ ] docs/archive/ has banner on all files
- [ ] README links to docs/archive/ (or explains deprecation policy)

### Admin Endpoints

- [ ] POST /v1/admin/recompute returns 200 (with valid API key)
- [ ] POST /v1/recompute returns 410 with hint
- [ ] Both admin endpoints under /v1/admin/* namespace

### HLE Integration

- [ ] Benchmark `humanitys_last_exam_text` exists in DB (family=OTHER)
- [ ] Signposts `hle_text_50` and `hle_text_70` exist (first_class=False)
- [ ] fetch_hle connector executes successfully (P1.1 passes)
- [ ] Claims created with credibility='B' (Provisional)
- [ ] /health/full shows fetch_hle status
- [ ] Celery Beat schedule includes fetch_hle at 08:02 UTC

### Monitor-Only Confirmation

- [ ] HLE claims do NOT change overall composite gauge (P1.2 passes)
- [ ] UI shows "Monitor-Only" status for HLE
- [ ] Provisional badge visible on /benchmarks
- [ ] Quality note about Bio/Chem displayed

### Tests

- [ ] Python unit tests pass (pytest services/etl/tests/test_hle_parser.py)
- [ ] E2E test passes (HLE tile + badge + tooltip)
- [ ] No test regressions in existing suites

---

## Implementation Order

**After approval, execute in this sequence:**

1. **P0.1** (CRITICAL): Fix HLE benchmark seeding
2. **P0.2**: Archive root COMPLETE.md files  
3. **P0.3**: Fix Playwright artifact upload
4. **P0.4**: Verify CI status (manual)
5. **P0.5**: Fix CI if needed (conditional)
6. **P1.1**: Manual HLE connector test
7. **P1.2**: Verify monitor-only status
8. **P1.3**: UI integration test
9. **P1.4**: Unit test coverage check
10. **P2**: Final acceptance criteria checklist

**Diff size commitment**: Each task ≤ 50 lines changed, with verification step after each.

---

## Notes

- **HLE is monitor-only**: Does NOT affect main Capabilities composite or overall gauge
- **Evidence tier**: B (Provisional) until peer-reviewed OR label-quality fix
- **Schedule**: Daily at 08:02 UTC (3 min before daily snapshot)
- **Calibration**: Thresholds set for 2026-2028 horizon (far from current SOTA ~35%)
- **Quality caveat**: Bio/Chem subsets have known issues per FutureHouse audit

### To-dos

- [ ] Initialize monorepo with npm workspaces, Docker configs, Makefile, and directory structure
- [ ] Create shared package with TS/Py schemas, Pydantic models, Zod schemas, and preset weights config
- [ ] Implement dual TS/Py scoring library with progress calculation, category aggregation, and harmonic mean logic + unit tests
- [ ] Create Alembic migration with all tables (roadmaps, signposts, benchmarks, sources, claims, etc.) and pgvector setup
- [ ] Build seed script with Playwright to fetch current leaderboard values for 25 signposts, 4 benchmarks, and 3 roadmaps
- [ ] Implement Celery tasks: fetch_feeds, extract_claims (GPT-4o-mini), link_entities (rules + GPT-4o), score_impact, verify_and_tag, snap_index, digest_weekly
- [ ] Implement LLM budget tracker in Redis with daily $20 cap, degradation to rule-based fallback, and spend monitoring
- [ ] Build FastAPI endpoints: /v1/index, /v1/signposts, /v1/evidence, /v1/feed.json, /v1/changelog, /health, admin endpoints
- [ ] Create Next.js components: CompositeGauge, LaneProgress, SafetyDial, OOMMeter, ScenarioTimeline, EvidenceCard, PresetSwitcher
- [ ] Build Next.js pages: Home, roadmaps/*, benchmarks, compute, security, changelog, methodology with SWR API integration
- [ ] Write Python pytest and TypeScript Jest tests for scoring, extraction, mapping, and components
- [ ] Implement Playwright E2E tests: home page gauges, scenario timeline badges, evidence panels with tier badges
- [ ] Create goldset.json with 100 labeled examples and eval script asserting mapping F1 ≥0.75
- [ ] Setup Sentry SDK, structured logging, Healthchecks pings, and metrics tracking (LLM spend, precision)
- [ ] Create GitHub Actions workflow for lint, typecheck, unit tests, and E2E tests with blocking on failures
- [ ] Write comprehensive README with architecture diagram, local dev instructions, and methodology page explaining scoring/tiers