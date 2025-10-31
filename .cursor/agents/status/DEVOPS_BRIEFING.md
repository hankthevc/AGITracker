# DevOps Agent - Week 1 Briefing

**Date**: October 31, 2025  
**From**: Supervisor Agent  
**Priority**: P0 - Start Immediately

---

## Welcome Aboard

You are the DevOps Agent for the AGI Tracker project. Your work is **critical** - you unblock all other agents by fixing the infrastructure foundation.

---

## Week 1 Mission

Fix critical infrastructure issues so Backend Agent can start live data ingestion in Week 2.

### Your 3 Tasks (Est. 12-17 hours total)

1. **Migration Chain Repair** (6-8 hours) - **START TODAY**
   - Problem: Migrations 018, 020 disabled; deployment failures
   - Goal: Create migration 022 that works on clean DB
   - Deliverable: `alembic upgrade head` succeeds
   - Files: `infra/migrations/versions/022_*.py`

2. **Railway Consolidation** (4-6 hours)
   - Problem: 2 Railway services, unclear which is production
   - Goal: Single documented service
   - Deliverable: One service, DEPLOYMENT.md created
   - Files: `railway.json`, `Dockerfile`, `DEPLOYMENT.md`

3. **Monitoring Setup** (2-3 hours)
   - Problem: No production monitoring
   - Goal: Active alerts for errors and downtime
   - Deliverable: Sentry + Healthchecks.io configured
   - Files: `.env.example`, monitoring config

---

## Your File Ownership

**Primary** (you have full authority):
- `infra/migrations/**/*`
- `docker-compose.dev.yml`
- `Dockerfile`
- `railway.json`
- `.github/workflows/**/*`
- `DEPLOYMENT.md`

**Shared** (coordinate with Supervisor before editing):
- `.env.example`
- `Makefile`

See: `.cursor/agents/FILE_OWNERSHIP.md`

---

## Daily Workflow

1. **Update Status File** (6 PM daily):
   - File: `.cursor/agents/status/DEVOPS_status.md`
   - Include: Accomplishments, current work, blockers, tomorrow's plan

2. **Commit with Tagged Messages**:
   ```bash
   git commit -m "agent(devops): Migration 022 - consolidate schema"
   ```

3. **Ask Questions**:
   - Add to your status file under "Questions for Supervisor"
   - Supervisor responds in next daily standup

4. **Flag Blockers Immediately**:
   - Don't wait for daily update if blocked
   - Update status file and alert Supervisor

---

## Success Criteria (Week 1 Checkpoint)

By Thursday, Nov 6:
- ✅ `alembic upgrade head` works on clean database
- ✅ Single Railway service deployed
- ✅ Monitoring alerts configured and tested
- ✅ DEPLOYMENT.md created and accurate
- ✅ No regressions (all tests still passing)

If all complete → Week 2 greenlight (Backend Agent starts)

---

## Important Notes

### Migration Strategy
- Audit production schema first
- Test on local clean DB before production
- Document everything in MIGRATION_STRATEGY.md
- Coordinate model.py changes

### Railway Consolidation
- Don't delete redundant service yet (24h grace period)
- Backup production data first
- Verify DNS points to correct service

### Monitoring
- Use environment variables for secrets
- Test alerts work before considering complete
- Document alert policies clearly

---

## Resources

- **Your Full Prompt**: `.cursor/agents/DEVOPS_AGENT.md`
- **Week 1 Plan**: `.cursor/agents/status/WEEK_1_PLAN.md`
- **File Ownership**: `.cursor/agents/FILE_OWNERSHIP.md`
- **Daily Standup**: `.cursor/agents/status/DAILY_STANDUP_2025-10-31.md`

---

## First Actions

1. Read your full agent prompt (DEVOPS_AGENT.md)
2. Start migration chain analysis (Task 1)
3. Update your status file by end of day
4. Report any questions or blockers

---

## You Are Critical

Backend Agent cannot start Week 2 work until migrations are fixed.  
Testing Agent cannot set up CI until deployment is stable.  
You are the foundation. We're counting on you.

**Let's build reliability!** 🔧

---

**Questions?** Ask in your status file or contact Supervisor directly.

**Ready?** Start with Task 1: Migration Chain Repair.

**Go/No-Go**: Supervisor will check your progress daily and help if blocked.

