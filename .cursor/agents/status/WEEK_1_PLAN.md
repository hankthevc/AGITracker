# Week 1 Plan - Cleanup & Stabilization

**Dates**: October 31 - November 6, 2025  
**Focus**: Fix critical infrastructure and clean repository  
**Active Agents**: Supervisor, DevOps, Documentation  
**Goal**: Professional repository + working migrations + single Railway service

---

## Objectives

### Primary Goals (P0 - Must Complete)
1. ✅ Repository cleanup (93 → <20 root files)
2. ✅ Migration chain repair (works on clean DB)
3. ✅ Railway consolidation (2 → 1 service)
4. ✅ Monitoring setup (Sentry + Healthchecks.io)

### Secondary Goals (P1 - Nice to Have)
1. Documentation accuracy (QUICKSTART.md tested)
2. Performance baseline (current metrics recorded)
3. Dependency audit (security vulnerabilities)

---

## Agent Assignments

### DevOps Agent - Priority Tasks

**Task 1: Migration Chain Repair** (6-8 hours)
- **Status**: 🎯 Start Immediately
- **Deliverable**: Migration 022 that consolidates/fixes chain
- **Success Criteria**: `alembic upgrade head` works on fresh DB
- **Files**: `infra/migrations/versions/022_*.py`
- **Testing**: Test on clean PostgreSQL instance
- **Blocker Risk**: Medium (complex migration logic)

**Task 2: Railway Service Consolidation** (4-6 hours)
- **Status**: ⏳ After Task 1
- **Deliverable**: Single Railway service configuration
- **Success Criteria**: One service running web + workers
- **Files**: `railway.json`, `Dockerfile`, `docker-compose.dev.yml`
- **Testing**: Deploy to Railway staging
- **Blocker Risk**: Low (straightforward config)

**Task 3: Monitoring Setup** (2-3 hours)
- **Status**: ⏳ After Task 2
- **Deliverable**: Sentry + Healthchecks.io configured
- **Success Criteria**: Alerts firing on test errors
- **Files**: `.env.example`, monitoring config
- **Testing**: Trigger test alert
- **Blocker Risk**: Low (well-documented APIs)

**Total Estimated Time**: 12-17 hours

---

### Documentation Agent - Priority Tasks

**Task 1: Execute Documentation Cleanup** (3-4 hours)
- **Status**: 🎯 Start Immediately
- **Deliverable**: 70+ files archived, root cleaned
- **Success Criteria**: Root directory has <20 files
- **Files**: Run `scripts/cleanup_docs.sh`
- **Testing**: Verify no broken links in README
- **Blocker Risk**: Low (scripted process)

**Task 2: Update Core Documentation** (3-4 hours)
- **Status**: ⏳ After Task 1
- **Deliverable**: README.md, QUICKSTART.md, DEPLOYMENT.md updated
- **Success Criteria**: New user can set up in <15 min
- **Files**: `README.md`, `QUICKSTART.md`, `DEPLOYMENT.md`
- **Testing**: Follow QUICKSTART on fresh machine
- **Blocker Risk**: Low (existing docs are good base)

**Task 3: Create Launch Materials Draft** (2-3 hours)
- **Status**: ⏳ After Task 2
- **Deliverable**: Draft Hacker News, Twitter, Reddit posts
- **Success Criteria**: Ready for Week 4 refinement
- **Files**: `docs/launch/*.md`
- **Testing**: Review with human operator
- **Blocker Risk**: Very Low (informational)

**Total Estimated Time**: 8-11 hours

---

### Supervisor Agent - Coordination Tasks

**Daily Standups** (30 min/day × 7 days = 3.5 hours)
- Collect agent status updates
- Write DAILY_STANDUP_YYYY-MM-DD.md
- Resolve blockers
- Update metrics

**Integration Testing** (1 hour/day × 7 days = 7 hours)
- Merge agent branches
- Test combined changes
- Resolve conflicts
- Update FILE_OWNERSHIP.md

**Weekly Summary** (2 hours Friday)
- Write WEEK_1_SUMMARY.md
- Update METRICS.md
- Plan Week 2
- Report to human operator

**Total Estimated Time**: 12.5 hours

---

## Daily Schedule

### Friday, Oct 31 (Initialization Day)
- **Supervisor**: Create coordination files, brief agents
- **DevOps**: Start migration chain analysis
- **Documentation**: Run cleanup script
- **End of Day**: First daily standup, status updates

### Saturday, Nov 1
- **DevOps**: Continue migration 022 development
- **Documentation**: Archive files, update README
- **Supervisor**: Monitor progress, resolve questions

### Sunday, Nov 2
- **DevOps**: Test migration on clean DB, debug if needed
- **Documentation**: Update QUICKSTART.md, test locally
- **Supervisor**: Integration check

### Monday, Nov 3
- **DevOps**: Finalize migration 022, start Railway consolidation
- **Documentation**: Update DEPLOYMENT.md
- **Supervisor**: Weekly checkpoint 1 (50% complete)

### Tuesday, Nov 4
- **DevOps**: Railway consolidation, test deployment
- **Documentation**: Create launch materials draft
- **Supervisor**: Monitor integration

### Wednesday, Nov 5
- **DevOps**: Monitoring setup (Sentry + Healthchecks)
- **Documentation**: Final documentation polish
- **Supervisor**: Pre-checkpoint testing

### Thursday, Nov 6 (Checkpoint Day)
- **DevOps**: Verify all tasks complete, documentation
- **Documentation**: Verify all tasks complete
- **Supervisor**: Run full integration test, write Week 1 Summary
- **End of Day**: Go/No-Go decision for Week 2

---

## Success Criteria (Go/No-Go Gates)

### Required for Week 2 Greenlight
- ✅ `alembic upgrade head` works on clean database
- ✅ Root directory has <20 files
- ✅ Single Railway service deployed successfully
- ✅ Monitoring alerts configured and tested
- ✅ README.md and QUICKSTART.md accurate
- ✅ All tests still passing (no regressions)

### Nice to Have (Don't Block Week 2)
- ⚠️ Launch materials draft (can continue in Week 2)
- ⚠️ Dependency audit (can do in Week 3)
- ⚠️ Performance baseline (Backend Agent in Week 2)

---

## Risk Management

### Known Risks

**Migration Consolidation Complexity**
- **Risk**: Migration 022 might have unforeseen edge cases
- **Mitigation**: DevOps tests thoroughly, Supervisor reviews
- **Backup Plan**: Keep old migrations, create additive migration instead
- **Owner**: DevOps Agent

**Documentation Cleanup Breaking Links**
- **Risk**: Archiving files might break internal links
- **Mitigation**: Test all README links before committing
- **Backup Plan**: Git revert, restore critical docs
- **Owner**: Documentation Agent

**Railway Deployment Issues**
- **Risk**: Service consolidation might break production
- **Mitigation**: Test in staging first, keep old config as backup
- **Backup Plan**: Revert to 2-service architecture temporarily
- **Owner**: DevOps Agent

---

## Integration Points

### DevOps ↔ Documentation
- **Handoff**: DevOps completes migrations → Documentation updates deployment guide
- **Shared File**: `DEPLOYMENT.md`
- **Coordination**: Sequential edits (DevOps first, then Documentation)

### Both Agents → Supervisor
- **Daily**: Status updates in `.cursor/agents/status/[AGENT]_status.md`
- **Blockers**: Escalate to Supervisor immediately
- **Questions**: Ask in status file, Supervisor responds in daily standup

---

## Metrics to Track

### Repository Health
- Root directory files: 93 → Target <20
- Documentation pages: 120+ → Target ~30
- Migration files: 27 → Target 22 (consolidated)

### Infrastructure
- Railway services: 2 → Target 1
- Migration success rate: ~70% → Target 100%
- Monitoring alerts: 0 → Target 5+ configured

### Documentation Quality
- QUICKSTART.md accuracy: Unknown → Target 100%
- Broken links: Unknown → Target 0
- Setup time: Unknown → Target <15 min

---

## Communication Protocol

### Agent → Supervisor
- **Daily Status Update**: Write to `.cursor/agents/status/[AGENT_NAME]_status.md` by 6 PM daily
- **Blockers**: Flag immediately, don't wait for daily update
- **Questions**: Document in status file under "Questions for Supervisor"

### Supervisor → Agents
- **Daily Standup**: Published by 9 AM, includes responses to questions
- **Priority Changes**: Communicated immediately if needed
- **Integration Feedback**: Provided after merging branches

### Supervisor → Human Operator
- **Daily Summary**: Brief update in daily standup
- **Blocker Escalation**: Flag issues requiring human decision
- **Weekly Report**: Comprehensive summary on Friday

---

## Handoff to Week 2

### Prerequisites for Week 2 Start
1. All Week 1 P0 tasks complete
2. No critical blockers
3. Human operator approval
4. Backend Agent briefed and ready

### Week 2 Preview
- **Active Agents**: Supervisor, DevOps, Backend, Testing, Documentation
- **Focus**: Live data ingestion, API optimization, CI/CD
- **Backend Agent**: Starts on enabling SCRAPE_REAL=true
- **Testing Agent**: Starts on CI/CD pipeline setup

---

## Notes

- **Week 1 is foundational** - Don't rush, quality over speed
- **Communication is key** - Agents should over-communicate blockers
- **Integration testing is critical** - Supervisor must test thoroughly
- **Flexibility is okay** - If something takes longer, adjust schedule
- **Document learnings** - Update retrospective with lessons learned

---

**Week 1 Motto**: "Clean foundation, stable infrastructure, accurate documentation"

**Let's execute!** 🚀

