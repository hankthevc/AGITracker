# Week 2 Plan - Production Enablement

**Dates**: November 7-13, 2025  
**Focus**: Live data ingestion, monitoring deployment, CI/CD pipeline  
**Active Agents**: Supervisor, Backend, Testing, Documentation, DevOps (support)  
**Goal**: Real data flowing + Observable system + Automated quality

---

## Objectives

### Primary Goals (P0 - Must Complete)

1. ✅ Live data ingestion (20+ events/day)
2. ✅ Celery Beat schedule running reliably
3. ✅ LLM budget limits enforced ($20 warning, $50 stop)
4. ✅ Monitoring active (Sentry + Healthchecks.io)
5. ✅ CI/CD pipeline functional (GitHub Actions)

### Secondary Goals (P1 - Nice to Have)

1. API documentation complete
2. User guides (2-3 completed)
3. Performance baseline recorded
4. Security scan initiated

---

## Prerequisites (From Week 1)

- ✅ Migration 022 deployed to production
- ✅ Sentry account created + DSN added to Railway
- ✅ Healthchecks.io account created + ping URLs added
- ✅ DEPLOYMENT.md available as reference
- ✅ MONITORING_SETUP.md available as guide

---

## Agent Assignments

### Backend Agent - Priority Tasks

**Task 1: Enable Live Data Ingestion** (8-10 hours)

- **Status**: 🎯 Start Monday (Nov 7)
- **Deliverable**: Real events flowing from arXiv, lab blogs, leaderboards
- **Success Criteria**: 20+ new events/day ingested
- **Files**: `services/etl/app/tasks/news/*.py`, `.env`
- **Testing**: Verify data quality, no duplicates
- **Blocker Risk**: Medium (real data may surprise us)

**Details**:

1. Set `SCRAPE_REAL=true` in Railway environment
2. Test each ingestor individually first:
   - ArXiv: `python scripts/test_ingestion_live.py --source arxiv`
   - HuggingFace leaderboards: Test individual leaderboards
   - Lab blogs: Test Anthropic, OpenAI feeds
3. Monitor first 24h closely (check logs, Sentry)
4. Verify deduplication working (no duplicate events)
5. Check LLM analysis quality (reasonable summaries)

**Task 2: Celery Beat Scheduling** (4-6 hours)

- **Status**: ⏳ After Task 1 stable
- **Deliverable**: Automated daily ingestion schedule
- **Success Criteria**: Tasks run on schedule, healthchecks ping
- **Files**: `services/etl/app/celery_config.py`, `services/etl/app/celery_app.py`
- **Testing**: Verify schedule via `railway run celery -A app.celery_app inspect active`
- **Blocker Risk**: Low (infrastructure ready)

**Details**:

1. Configure Celery Beat schedule:
   - Daily feeds: 6 AM UTC
   - Leaderboard updates: 12 PM UTC
   - Index calculation: After feeds complete
   - Weekly digest: Sunday 8 AM UTC
2. Add healthcheck pings (see `HEALTHCHECKS_INTEGRATION_GUIDE.md`)
3. Test schedule locally first
4. Deploy to Railway
5. Verify first scheduled run succeeds

**Task 3: LLM Budget Management** (2-3 hours)

- **Status**: ⏳ After Task 1-2 complete
- **Deliverable**: Budget tracking and enforcement
- **Success Criteria**: Stays under $20/day, hard stop at $50
- **Files**: `services/etl/app/utils/llm_budget.py`, `services/etl/app/tasks/analyze/*.py`
- **Testing**: Simulate high usage, verify stop
- **Blocker Risk**: Very Low (code exists, needs verification)

**Details**:

1. Review existing budget manager (`app/utils/llm_budget.py`)
2. Add budget checks to all LLM-calling tasks
3. Set Redis keys:
   - `llm_budget:daily:{YYYY-MM-DD}` - tracks spend
   - `llm_budget:warning_sent` - prevents spam
4. Configure alerts:
   - $20: Email notification
   - $50: Disable LLM tasks, alert
5. Test with mock spend

**Total Estimated Time**: 14-19 hours

---

### Testing Agent - Priority Tasks

**Task 1: GitHub Actions CI/CD Pipeline** (8-10 hours)

- **Status**: 🎯 Start Tuesday (Nov 8)
- **Deliverable**: Automated testing on every PR
- **Success Criteria**: Tests run on PR, auto-deploy on merge
- **Files**: `.github/workflows/ci.yml`, `.github/workflows/deploy.yml`
- **Testing**: Create test PR, verify workflow
- **Blocker Risk**: Low (DevOps provided template)

**Details**:

1. Create `.github/workflows/ci.yml` (see `DEVOPS_AGENT.md` for template):
   - Backend tests (pytest)
   - Frontend tests (lint, typecheck, build)
   - E2E tests (Playwright, main branch only)
2. Create `.github/workflows/deploy.yml`:
   - Deploy API to Railway (on main push)
   - Deploy web to Vercel (automatic)
3. Add GitHub secrets:
   - `RAILWAY_TOKEN`
   - `VERCEL_TOKEN`
   - `VERCEL_ORG_ID`
   - `VERCEL_PROJECT_ID`
4. Test with draft PR
5. Add status badges to README.md

**Task 2: Expand E2E Test Coverage** (6-8 hours)

- **Status**: ⏳ After Task 1 complete
- **Deliverable**: 40% → 60% E2E coverage
- **Success Criteria**: Critical paths tested
- **Files**: `apps/web/e2e/**/*.ts`
- **Testing**: All new tests pass locally and in CI
- **Blocker Risk**: Low (Playwright already set up)

**Details**:

1. Identify critical paths:
   - Landing page load
   - Index calculation with preset change
   - Events feed filtering
   - Timeline navigation
   - Export functionality
2. Write tests for each (see existing tests in `apps/web/e2e/`)
3. Run locally: `cd apps/web && npm run e2e`
4. Verify in CI
5. Document in `tests/README.md`

**Task 3: Security Audit Preparation** (4-6 hours)

- **Status**: ⏳ After Task 1-2 complete
- **Deliverable**: Initial security scan results
- **Success Criteria**: No critical vulnerabilities found
- **Files**: New `docs/SECURITY_AUDIT.md`
- **Testing**: Run scans, document findings
- **Blocker Risk**: Low (preparation only, fixes in Week 3)

**Details**:

1. Run dependency audit:
   - Backend: `pip-audit`
   - Frontend: `npm audit`
2. Run OWASP ZAP scan (or similar)
3. Check for common issues:
   - SQL injection (should be prevented by SQLAlchemy)
   - XSS (should be prevented by React)
   - CSRF (verify CORS settings)
   - Secrets in code (scan with `truffleHog`)
4. Document findings in `docs/SECURITY_AUDIT.md`
5. Prioritize fixes for Week 3

**Total Estimated Time**: 18-24 hours

---

### Documentation Agent - Continue Tasks

**Task 1: User Guides Content** (6-8 hours)

- **Status**: 🎯 Continue (Quick Tour already done)
- **Deliverable**: 2-3 more user guides
- **Success Criteria**: Comprehensive, with screenshots
- **Files**: `docs/user-guides/*.md`
- **Testing**: Follow guides yourself, verify accuracy
- **Blocker Risk**: Very Low (independent work)

**Guides to Create**:

1. **Dashboard Guide** (explaining gauges, charts)
2. **Evidence Tiers Explained** (A/B/C/D system)
3. **Filtering Events** (how to find relevant events)
4. **Optional**: Presets Guide or Exporting Data

**Task 2: API Documentation Enhancements** (4-6 hours)

- **Status**: ⏳ After Backend Agent adds features
- **Deliverable**: Complete API reference
- **Success Criteria**: All endpoints documented with examples
- **Files**: `services/etl/app/main.py` (OpenAPI), `docs/user-guides/api.md`
- **Testing**: Test all example code snippets
- **Blocker Risk**: Low (coordinate with Backend Agent)

**Details**:

1. Review Backend Agent's new endpoints (if any)
2. Enhance FastAPI OpenAPI descriptions
3. Add request/response examples
4. Create user-facing API guide (`docs/user-guides/api.md`)
5. Test all example code
6. Generate OpenAPI spec: `curl http://localhost:8000/openapi.json > docs/openapi.json`

**Task 3: Support Other Agents** (2-4 hours)

- **Status**: 🔄 Ongoing
- **Deliverable**: Document new features as developed
- **Success Criteria**: All new features documented
- **Files**: Various (coordinate with agents)
- **Testing**: Accuracy review with agent
- **Blocker Risk**: Very Low (coordination task)

**Details**:

1. Backend Agent: Document new ingestion sources
2. Testing Agent: Document test procedures
3. DevOps Agent: Update deployment docs if needed
4. Update CHANGELOG.md weekly

**Total Estimated Time**: 12-18 hours

---

### DevOps Agent - Support Role

**Task 1: Monitor Migration 022 Deployment** (2-3 hours)

- **Status**: 🎯 Week 2 start (after deployment)
- **Deliverable**: Deployment verified successful
- **Success Criteria**: No errors, indexes created
- **Files**: Check Railway logs
- **Testing**: Verify schema matches models.py
- **Blocker Risk**: Very Low (migration well-tested)

**Details**:

1. Monitor Railway logs during deployment
2. Verify indexes created: `railway run psql -c "\d events"`
3. Check for any errors
4. Confirm migration head: `railway run alembic current`
5. Report success to Supervisor

**Task 2: Support Backend Agent** (2-4 hours)

- **Status**: ⏳ As needed
- **Deliverable**: Backend Agent unblocked
- **Success Criteria**: Any infrastructure issues resolved
- **Files**: Various (as needed)
- **Testing**: N/A (support role)
- **Blocker Risk**: Low (Backend Agent should be smooth)

**Details**:

1. Available for questions about deployment
2. Help debug Railway/database issues if they arise
3. Assist with environment variable configuration
4. Monitor infrastructure metrics

**Task 3: Optional - Start CI/CD if Testing Agent Delayed** (6-8 hours)

- **Status**: ⏸️ Only if needed
- **Deliverable**: GitHub Actions workflow
- **Success Criteria**: CI tests passing
- **Files**: `.github/workflows/ci.yml`
- **Testing**: Test PR workflow
- **Blocker Risk**: Low (template ready)

**Note**: Defer to Testing Agent if they're on schedule

**Total Estimated Time**: 4-15 hours (depends on support needs)

---

### Supervisor Agent - Coordination Tasks

**Daily Standups** (30 min/day × 7 days = 3.5 hours)

- Collect agent status updates
- Write DAILY_STANDUP_YYYY-MM-DD.md
- Resolve blockers
- Coordinate dependencies

**Integration Testing** (1 hour/day × 7 days = 7 hours)

- Merge agent branches
- Test combined changes
- Resolve conflicts
- Monitor live data quality

**Weekly Summary** (3 hours Friday)

- Write WEEK_2_SUMMARY.md
- Update METRICS.md
- Plan Week 3
- Report to human operator

**Total Estimated Time**: 13.5 hours

---

## Daily Schedule

### Monday, Nov 7 (Week 2 Start)

- **Backend Agent**: Activate, start Task 1 (enable live ingestion)
- **Testing Agent**: Activate, start Task 1 (CI/CD pipeline)
- **Documentation Agent**: Continue user guides (Dashboard Guide)
- **DevOps Agent**: Monitor migration 022 deployment
- **Supervisor**: Coordinate activations, daily standup

### Tuesday, Nov 8

- **Backend Agent**: Test individual ingestors, verify data
- **Testing Agent**: Continue CI/CD setup, add GitHub secrets
- **Documentation Agent**: Dashboard Guide, start Evidence Tiers
- **Supervisor**: Monitor live data, resolve issues

### Wednesday, Nov 9

- **Backend Agent**: Enable all ingestors, monitor closely
- **Testing Agent**: Finalize CI/CD, test with draft PR
- **Documentation Agent**: Evidence Tiers guide, start API docs
- **Supervisor**: Integration check, verify CI working

### Thursday, Nov 10 (Midweek Checkpoint)

- **Backend Agent**: Start Celery Beat configuration
- **Testing Agent**: Start E2E test expansion
- **Documentation Agent**: API documentation enhancements
- **Supervisor**: 50% checkpoint, assess progress

### Friday, Nov 11

- **Backend Agent**: Test Celery Beat schedule locally
- **Testing Agent**: Continue E2E tests
- **Documentation Agent**: Support other agents, update docs
- **Supervisor**: Integration testing

### Saturday, Nov 12

- **Backend Agent**: Deploy Celery Beat, verify LLM budget
- **Testing Agent**: Continue E2E tests, start security audit prep
- **Documentation Agent**: Polish user guides
- **Supervisor**: Monitor production

### Sunday, Nov 13 (Week 2 Checkpoint)

- **All Agents**: Finalize tasks, documentation
- **Supervisor**: Run full integration test, write Week 2 Summary
- **Checkpoint**: Go/No-Go decision for Week 3

---

## Success Criteria (Go/No-Go Gates)

### Required for Week 3 Greenlight

- ✅ 20+ events/day ingesting from real sources
- ✅ Celery Beat schedule running reliably
- ✅ LLM budget tracking active (<$20/day observed)
- ✅ Monitoring active (Sentry receiving errors, Healthchecks pinging)
- ✅ CI/CD pipeline passing on PRs
- ✅ No critical blockers

### Nice to Have (Don't Block Week 3)

- ⚠️ E2E coverage 60% (can be 50%+)
- ⚠️ Security audit complete (can start in Week 3)
- ⚠️ All user guides (can continue in Week 3)

---

## Risk Management

### Known Risks

**Real Data Quality Issues** (Medium)

- **Risk**: Live data may have unexpected formats
- **Mitigation**: Start with fixture mode, gradually enable one source at a time
- **Backup Plan**: Revert to SCRAPE_REAL=false, debug offline
- **Owner**: Backend Agent

**LLM Costs Spike** (Low)

- **Risk**: Real data volume causes budget overrun
- **Mitigation**: Hard $50/day stop, $20 warning
- **Backup Plan**: Disable LLM analysis temporarily, use rule-based
- **Owner**: Backend Agent

**CI/CD Configuration** (Low)

- **Risk**: GitHub Actions secrets misconfigured
- **Mitigation**: Test with draft PR first
- **Backup Plan**: Manual deployment fallback
- **Owner**: Testing Agent

**Celery Beat Reliability** (Low)

- **Risk**: Schedule doesn't run on Railway
- **Mitigation**: Test locally first, monitor closely
- **Backup Plan**: Manual task triggers via admin endpoint
- **Owner**: Backend Agent

---

## Integration Points

### Backend ↔ DevOps

- **Handoff**: DevOps monitors migration 022, Backend uses new schema
- **Shared Files**: None (Backend reads infra/)
- **Coordination**: DevOps supports if infrastructure issues

### Backend ↔ Testing

- **Handoff**: Backend deploys features → Testing tests them
- **Shared Files**: None (Testing tests Backend's code)
- **Coordination**: Testing reports bugs, Backend fixes

### Backend ↔ Documentation

- **Handoff**: Backend adds features → Documentation documents them
- **Shared Files**: `services/etl/app/main.py` (OpenAPI)
- **Coordination**: Sequential edits (Backend code, Docs enhance)

### Testing ↔ DevOps

- **Handoff**: Testing creates CI/CD, DevOps reviews if needed
- **Shared Files**: `.github/workflows/*.yml`
- **Coordination**: Testing owns CI/CD, DevOps supports

### All Agents → Supervisor

- **Daily**: Status updates in `.cursor/agents/status/[AGENT]_status.md`
- **Blockers**: Escalate immediately
- **Questions**: Document in status file

---

## Metrics to Track

### Live Data Quality

- Events ingested/day: Target 20-50
- Deduplication rate: <5% duplicates
- LLM analysis quality: Manual spot-check
- Sources active: ArXiv, Anthropic, OpenAI, HuggingFace

### Performance

- API response time (p95): <350ms (baseline)
- Database connections: <10 (baseline)
- Memory usage: <512MB (baseline)
- Error rate: <1%

### Testing

- Backend test coverage: 65% → 70%
- E2E test coverage: 40% → 60%
- CI/CD success rate: >95%
- Security vulnerabilities: Document count

### Monitoring

- Sentry errors/day: <10
- Healthchecks.io ping success: >95%
- Alert false positive rate: <10%

---

## Communication Protocol

### Agent → Supervisor

- **Daily Status Update**: Write to `.cursor/agents/status/[AGENT_NAME]_status.md` by 6 PM daily
- **Blockers**: Flag immediately, don't wait
- **Questions**: Document in status file under "Questions for Supervisor"

### Supervisor → Agents

- **Daily Standup**: Published by 9 AM with responses
- **Priority Changes**: Immediate notification if critical
- **Integration Feedback**: After merging branches

### Supervisor → Human Operator

- **Daily Summary**: Brief update in daily standup
- **Blocker Escalation**: Issues requiring human decision
- **Weekly Report**: Comprehensive summary on Sunday

---

## Handoff to Week 3

### Prerequisites for Week 3 Start

1. All Week 2 P0 tasks complete
2. Live data flowing reliably
3. Monitoring active and alerting
4. CI/CD functional
5. No critical blockers
6. Human operator approval

### Week 3 Preview

- **Active Agents**: All 6 (full team)
- **Focus**: Security audit, performance optimization, dark mode, PWA
- **Frontend Agent**: Activates for UI polish
- **Security**: Full OWASP audit and fixes
- **Performance**: Load testing, optimization

---

## Notes

- **Week 2 is production enablement** - Real data flowing is the goal
- **Monitor closely** - First week with live data requires attention
- **Be ready to scale back** - Can disable live ingestion if issues
- **Integration is key** - Multiple agents working in parallel
- **Communication critical** - Over-communicate blockers and questions

---

**Week 2 Motto**: "Live data flowing, observable system, automated quality"

**Let's enable production!** 🚀
