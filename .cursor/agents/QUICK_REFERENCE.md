# Agent System - Quick Reference Card

**Print or keep open in a tab for quick lookups**

---

## Activation Order

1. **SUPERVISOR** (first, always)
2. **DEVOPS + DOCUMENTATION** (Week 1, parallel)
3. **BACKEND** (Week 2, after migrations fixed)
4. **FRONTEND + TESTING** (Week 3, after API stable)
5. **ALL AGENTS** (Week 4, final push)

---

## Daily Routine (5 minutes)

```bash
# Morning checklist
cd "/Users/HenryAppel/AI Doomsday Tracker"

# 1. Read daily standup
cat .cursor/agents/status/DAILY_STANDUP_$(date +%Y-%m-%d).md

# 2. Check for blockers
grep -A 3 "Blockers" .cursor/agents/status/*_status.md

# 3. Review Git activity
git log --oneline --since="24 hours ago"

# 4. Check metrics
cat .cursor/agents/status/METRICS.md
```

---

## Agent Responsibilities

| Agent | Week 1 | Week 2 | Week 3 | Week 4 |
|-------|--------|--------|--------|--------|
| **Supervisor** | Coordinate | Integrate | Quality Gates | Launch Prep |
| **DevOps** | Migrations + Railway | Monitoring + CI/CD | PgBouncer | Backups |
| **Backend** | - | Live Data + Celery | API Optimization | Final Tests |
| **Frontend** | - | - | Dark + PWA | Social Sharing |
| **Testing** | - | E2E Tests | Security + Load | Pre-Launch |
| **Documentation** | Cleanup | API Docs | User Guides | Launch Materials |

---

## File Ownership (Quick Lookup)

**DevOps**:
- `infra/migrations/`
- `docker-compose.dev.yml`
- `.github/workflows/`
- `DEPLOYMENT.md`

**Backend**:
- `services/etl/app/tasks/`
- `services/etl/app/celery_*.py`
- `scripts/*_ingest*.py`

**Frontend**:
- `apps/web/app/`
- `apps/web/components/`
- `apps/web/public/`

**Testing**:
- `apps/web/e2e/`
- `services/etl/tests/`
- `docs/SECURITY_AUDIT.md`

**Documentation**:
- `README.md`
- `QUICKSTART.md`
- `docs/**/*.md`

**Shared** (coordinate!):
- `services/etl/app/main.py` (see FILE_OWNERSHIP.md for sections)
- `package.json`
- `requirements.txt`

---

## Common Commands

### Activate Agent

```bash
# Open new Cursor window
cat .cursor/agents/[AGENT_NAME]_AGENT.md

# Then say to Cursor:
You are the [Agent Name] Agent. Your Week [N] priorities are:
1. [Task 1]
2. [Task 2]

Start with Task 1: [Task Name].
Report to Supervisor Agent.
```

### Check Agent Status

```bash
cat .cursor/agents/status/[AGENT]_status.md
```

### View Progress

```bash
# Today's standup
cat .cursor/agents/status/DAILY_STANDUP_$(date +%Y-%m-%d).md

# This week's summary
cat .cursor/agents/status/WEEK_1_SUMMARY.md

# Metrics dashboard
cat .cursor/agents/status/METRICS.md
```

### Pause/Resume All

```
@Supervisor: Pause all agents. [Reason]
@Supervisor: Resume all agents. Continue Week N plan.
```

---

## Decision Tree

**Agent asks for approval?**
→ Review request → Approve or reject → Agent proceeds

**Merge conflict?**
→ Check FILE_OWNERSHIP.md → Reassign if needed → Supervisor integrates

**Agent stuck?**
→ Check status file → Check for blockers → Provide guidance

**Need to change priorities?**
→ Talk to Supervisor → Update weekly plan → Agents adjust

**Production incident?**
→ All agents pause → DevOps investigates → Supervisor coordinates

---

## Weekly Checkpoints

### Week 1
- [ ] 70+ docs archived
- [ ] Migration chain works
- [ ] Railway = 1 service

### Week 2
- [ ] Live data flowing (20+ events/day)
- [ ] Monitoring active
- [ ] CI/CD passing

### Week 3
- [ ] Security audit clean
- [ ] Lighthouse >90
- [ ] Load test passed

### Week 4
- [ ] All features complete
- [ ] Launch materials ready
- [ ] Production deployed

---

## Emergency Contacts

**Agent not responding?**
→ Reload agent prompt file

**Supervisor needs human decision?**
→ Check `status/` for escalation request

**Production issue?**
→ Message: `@All: PRODUCTION DOWN - Stop work. @DevOps: Investigate.`

**Need to abort?**
→ Message: `@Supervisor: Abort current tasks. Need strategic pivot.`

---

## Metrics to Watch

| Metric | Start | Target | Current |
|--------|-------|--------|---------|
| Production Readiness | 70% | 100% | [  ]% |
| Root Files | 93 | <20 | [  ] |
| E2E Coverage | 40% | 80% | [  ]% |
| Lighthouse Score | 75 | 90+ | [  ] |
| Events/Day | 0 | 20+ | [  ] |

Update `status/METRICS.md` weekly.

---

## Success Signals

**Week 1**: Clean repo, working migrations, single Railway service  
**Week 2**: Real data ingesting, alerts firing, tests in CI  
**Week 3**: Dark mode live, security clean, fast performance  
**Week 4**: **PRODUCTION LAUNCH** 🚀

---

## Troubleshooting

**"Agent keeps editing wrong file"**
→ Check FILE_OWNERSHIP.md, correct agent if needed

**"Two agents conflicting"**
→ Supervisor should handle, if not: reassign files

**"Agent wants to add out-of-scope feature"**
→ Remind agent of Phase priorities, defer to backlog

**"Falling behind schedule"**
→ Review METRICS.md, adjust timeline or descope

**"Not sure which agent to activate"**
→ Follow activation order: Supervisor → DevOps/Docs → Backend → Frontend/Testing

---

## Pro Tips

1. **Trust the Process** - Agents know their roles
2. **Daily Standups** - 5 min review prevents surprises
3. **Let Supervisor Coordinate** - Don't micromanage
4. **Clear Communication** - Specific requests get better results
5. **Celebrate Wins** - Each checkpoint is progress

---

**Remember**: You're orchestrating, not doing. Let the agents work!

---

**Questions?** Check ACTIVATION_GUIDE.md for detailed instructions.

**First time?** Start with: Activate Supervisor Agent.

**Stuck?** Read the agent's .md file for their full instructions.

---

**Print this page and keep it handy during the 4-week sprint!**

