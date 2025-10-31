# AGI Tracker - Agent Orchestration System

This directory contains the agent orchestration system for parallel Cursor AI agents working on the AGI Tracker project.

---

## Quick Start

**First Time**:
1. Read `ACTIVATION_GUIDE.md`
2. Activate Supervisor Agent first
3. Then activate DevOps and Documentation agents
4. Monitor progress in `status/` directory

**Daily Routine**:
1. Check `status/DAILY_STANDUP_YYYY-MM-DD.md`
2. Review agent status files
3. Address any blockers
4. Approve decisions if needed

---

## Agent Prompts

### Coordination
- **SUPERVISOR_AGENT.md** - Orchestrates all agents, prevents conflicts

### Specialists
- **DEVOPS_AGENT.md** - Infrastructure, migrations, deployment, monitoring
- **BACKEND_AGENT.md** - Data pipeline, API, LLM tasks
- **FRONTEND_AGENT.md** - UI/UX, dark mode, PWA, social sharing
- **TESTING_AGENT.md** - E2E tests, security, load testing
- **DOCUMENTATION_AGENT.md** - Docs, guides, launch materials

---

## Supporting Files

- **FILE_OWNERSHIP.md** - Who owns which files (prevents conflicts)
- **ACTIVATION_GUIDE.md** - Step-by-step activation instructions
- **status/** - Daily standups, agent status, metrics

---

## Workflow

```
Week 1: Cleanup & Stabilization
├── Supervisor (coordinate)
├── DevOps (fix migrations, consolidate deployment)
└── Documentation (cleanup 70+ files)

Week 2: Production Enablement
├── Supervisor (integrate work)
├── DevOps (monitoring, CI/CD)
├── Backend (live data, Celery Beat)
└── Documentation (API docs)

Week 3: Security & Performance
├── Supervisor (quality gates)
├── DevOps (PgBouncer)
├── Backend (API optimization)
├── Frontend (dark mode, PWA)
├── Testing (security audit, load testing)
└── Documentation (user guides)

Week 4: Polish & Launch
├── All agents (final features)
└── LAUNCH 🚀
```

---

## File Organization

```
.cursor/
└── agents/
    ├── README.md (this file)
    ├── ACTIVATION_GUIDE.md
    ├── FILE_OWNERSHIP.md
    ├── SUPERVISOR_AGENT.md
    ├── DEVOPS_AGENT.md
    ├── BACKEND_AGENT.md
    ├── FRONTEND_AGENT.md
    ├── TESTING_AGENT.md
    ├── DOCUMENTATION_AGENT.md
    └── status/
        ├── DAILY_STANDUP_YYYY-MM-DD.md
        ├── WEEK_N_PLAN.md
        ├── WEEK_N_SUMMARY.md
        ├── WEEK_N_RETRO.md
        ├── METRICS.md
        ├── DEVOPS_status.md
        ├── BACKEND_status.md
        ├── FRONTEND_status.md
        ├── TESTING_status.md
        └── DOCUMENTATION_status.md
```

---

## Success Metrics

| Week | Goal | Progress |
|------|------|----------|
| 1 | Cleanup & Stabilization | [  ] |
| 2 | Production Enablement | [  ] |
| 3 | Security & Performance | [  ] |
| 4 | Polish & Launch | [  ] |

**Overall Production Readiness**: 70% → 100%

---

## Support

- Questions about agent system: See ACTIVATION_GUIDE.md
- Technical issues: See TROUBLESHOOTING.md (root)
- Agent conflicts: Check FILE_OWNERSHIP.md
- Code review results: See CODE_REVIEW_2025.md (root)

---

**Built for**: Taking AGI Tracker from 70% → 100% production-ready with minimal human intervention.

**Last Updated**: 2025-10-30

