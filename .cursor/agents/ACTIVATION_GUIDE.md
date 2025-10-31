# 🚀 Agent Orchestration System - Activation Guide

**Date**: October 30, 2025  
**Purpose**: Activate and coordinate 6 parallel Cursor agents to complete AGI Tracker production readiness

---

## Overview

You now have a team of specialized AI agents ready to work in parallel on the AGI Tracker. This guide explains how to activate them and what to expect.

---

## Your Agent Team

### 1. **SUPERVISOR_AGENT** (The Conductor)
- **Role**: Coordinates all other agents
- **Priority**: P0 (activate first)
- **File**: `.cursor/agents/SUPERVISOR_AGENT.md`
- **Responsibility**: Integration, deduplication, conflict resolution

### 2. **DEVOPS_AGENT** (Infrastructure Specialist)
- **Role**: Migrations, deployment, monitoring, CI/CD
- **Priority**: P0 (starts immediately)
- **File**: `.cursor/agents/DEVOPS_AGENT.md`
- **Dependencies**: None (can start right away)

### 3. **BACKEND_AGENT** (Data Pipeline Specialist)
- **Role**: Live data ingestion, LLM tasks, API optimization
- **Priority**: P0 (starts Week 2)
- **File**: `.cursor/agents/BACKEND_AGENT.md`
- **Dependencies**: DevOps (needs migration chain fixed)

### 4. **FRONTEND_AGENT** (UI/UX Specialist)
- **Role**: Dark mode, PWA, social sharing, mobile optimization
- **Priority**: P1 (starts Week 3-4)
- **File**: `.cursor/agents/FRONTEND_AGENT.md`
- **Dependencies**: Backend (needs stable API)

### 5. **TESTING_AGENT** (Quality Assurance Specialist)
- **Role**: E2E tests, security audit, load testing
- **Priority**: P1 (starts Week 2-3)
- **File**: `.cursor/agents/TESTING_AGENT.md`
- **Dependencies**: DevOps (CI/CD), Backend & Frontend (code to test)

### 6. **DOCUMENTATION_AGENT** (Knowledge Specialist)
- **Role**: Cleanup, user guides, API docs, launch materials
- **Priority**: P1 (starts immediately, continues throughout)
- **File**: `.cursor/agents/DOCUMENTATION_AGENT.md`
- **Dependencies**: Other agents (documents their work)

---

## Quick Start

### Step 1: Activate Supervisor (5 minutes)

Open a new Cursor window and load the supervisor:

```bash
# In Cursor, open a new chat
# Paste the entire contents of:
cat .cursor/agents/SUPERVISOR_AGENT.md
```

Then say:
```
You are the Supervisor Agent. Initialize the agent coordination system:
1. Create the .cursor/agents/status/ directory
2. Create FILE_OWNERSHIP.md
3. Create WEEK_1_PLAN.md
4. Brief all other agents
5. Start DevOps and Documentation agents on Week 1 tasks

Report back when initialization is complete.
```

### Step 2: Activate DevOps & Documentation Agents (Parallel)

**DevOps Window**:
```bash
# New Cursor window
cat .cursor/agents/DEVOPS_AGENT.md

# Then say:
You are the DevOps Agent. Your Week 1 priorities are:
1. Fix migration chain (create migration 022)
2. Consolidate Railway services
3. Set up production monitoring

Start with Task 1: Migration Chain Repair.
Update your status in .cursor/agents/status/DEVOPS_status.md daily.
Report to Supervisor Agent.
```

**Documentation Window**:
```bash
# New Cursor window
cat .cursor/agents/DOCUMENTATION_AGENT.md

# Then say:
You are the Documentation Agent. Your Week 1 priority is:
1. Execute cleanup_docs.sh script
2. Archive 70+ obsolete files
3. Update README.md and QUICKSTART.md

Start with Task 1: Execute Documentation Cleanup.
Update your status in .cursor/agents/status/DOCUMENTATION_status.md daily.
Report to Supervisor Agent.
```

### Step 3: Monitor Progress (Daily)

**Check Supervisor Dashboard**:
```bash
# View daily standup
cat .cursor/agents/status/DAILY_STANDUP_$(date +%Y-%m-%d).md

# View agent status
cat .cursor/agents/status/DEVOPS_status.md
cat .cursor/agents/status/DOCUMENTATION_status.md
```

### Step 4: Activate Backend Agent (Week 2)

After DevOps fixes migrations:

```bash
# New Cursor window
cat .cursor/agents/BACKEND_AGENT.md

# Then say:
You are the Backend Agent. Your Week 2 priorities are:
1. Enable live data ingestion (SCRAPE_REAL=true)
2. Configure Celery Beat scheduling
3. Verify LLM budget limits

Start with Task 1: Enable Real Data Ingestion.
Coordinate with DevOps Agent on database schema.
Report to Supervisor Agent.
```

### Step 5: Activate Frontend & Testing Agents (Week 3)

**Frontend Window**:
```bash
cat .cursor/agents/FRONTEND_AGENT.md

# Then say:
You are the Frontend Agent. Your Week 3 priorities are:
1. Implement dark mode
2. Add PWA features
3. Create social sharing with OpenGraph

Start with Task 1: Dark Mode Implementation.
Report to Supervisor Agent.
```

**Testing Window**:
```bash
cat .cursor/agents/TESTING_AGENT.md

# Then say:
You are the Testing Agent. Your Week 3 priorities are:
1. Expand E2E test coverage to 80%
2. Run security audit
3. Perform load testing

Start with Task 1: Expand E2E Test Coverage.
Report to Supervisor Agent.
```

---

## What to Expect

### Week 1 (Cleanup & Stabilization)

**Active Agents**: Supervisor, DevOps, Documentation

**You'll See**:
- Supervisor creates coordination files
- DevOps fixes migration chain
- Documentation archives 70+ files
- Daily status reports in `.cursor/agents/status/`

**Your Actions**:
- Review daily standups
- Approve any major decisions (Supervisor will ask)
- Monitor Git activity

### Week 2 (Production Enablement)

**Active Agents**: All agents + Backend

**You'll See**:
- Real data flowing (20+ events/day)
- Monitoring alerts configured
- CI/CD pipeline running
- Test coverage increasing

**Your Actions**:
- Verify live data looks correct
- Test production monitoring
- Review security findings

### Week 3 (Security & Performance)

**Active Agents**: All agents (full team)

**You'll See**:
- Dark mode in action
- PWA installable
- Security audit report
- Load test results
- Performance optimizations

**Your Actions**:
- Test dark mode on your devices
- Install PWA on phone
- Review security audit
- Approve performance changes

### Week 4 (Polish & Launch)

**Active Agents**: All agents (final push)

**You'll See**:
- Social sharing working
- Launch materials ready
- All tests passing
- Production deployment successful

**Your Actions**:
- Final review of launch posts
- Approve production deployment
- **LAUNCH!** 🚀

---

## Communication with Agents

### How to Give Instructions

Each agent operates independently but reports to Supervisor. You can:

1. **Talk to Individual Agents**:
   ```
   @DevOps: Can you add an alert for database connection failures?
   ```

2. **Talk to Supervisor**:
   ```
   @Supervisor: I need to prioritize mobile optimization. 
   Can you have Frontend Agent work on that before dark mode?
   ```

3. **Broadcast to All**:
   ```
   @All: We're presenting to investors on Friday. 
   Need a working demo by Thursday EOD.
   ```

### How to Get Updates

**Daily Standup** (auto-generated):
```bash
cat .cursor/agents/status/DAILY_STANDUP_$(date +%Y-%m-%d).md
```

**Weekly Summary**:
```bash
cat .cursor/agents/status/WEEK_1_SUMMARY.md
```

**Metrics Dashboard**:
```bash
cat .cursor/agents/status/METRICS.md
```

---

## Decision Points

### When You Must Approve

Agents will ask for approval on:
- Major architecture changes
- Database schema changes (new tables)
- Production deployment
- Security policy changes
- API breaking changes
- Feature scope changes

### When Agents Decide Autonomously

Agents can decide on:
- Task prioritization within weekly goals
- Code style and formatting
- Test coverage targets
- Documentation structure
- Minor bug fixes
- Performance optimizations

---

## Troubleshooting

### Agent Seems Stuck

1. Check their status file:
   ```bash
   cat .cursor/agents/status/[AGENT]_status.md
   ```

2. Check for blockers in daily standup:
   ```bash
   cat .cursor/agents/status/DAILY_STANDUP_$(date +%Y-%m-%d).md | grep -A 5 "Blockers"
   ```

3. Ask Supervisor:
   ```
   @Supervisor: What's blocking Backend Agent?
   ```

### Merge Conflict

1. Supervisor should handle this automatically
2. If not, check FILE_OWNERSHIP.md
3. Reassign file ownership if needed

### Agent Made Wrong Decision

1. Provide feedback:
   ```
   @Agent: Please revert the change to X. 
   The correct approach is Y because Z.
   ```

2. Update their instructions:
   ```
   @Supervisor: Update [Agent]'s guidelines to include [new rule]
   ```

---

## Success Metrics

### Week 1 Checkpoint
- [ ] 70+ docs archived
- [ ] Migration chain works on clean DB
- [ ] Railway consolidated to 1 service
- [ ] FILE_OWNERSHIP.md created

### Week 2 Checkpoint
- [ ] 20+ events/day ingesting
- [ ] Alerts firing correctly
- [ ] CI tests passing

### Week 3 Checkpoint
- [ ] Zero critical vulnerabilities
- [ ] Lighthouse >90
- [ ] Load test passed

### Week 4 Checkpoint
- [ ] All features shipped
- [ ] Launch materials ready
- [ ] **PRODUCTION READY**

---

## Emergency Protocols

### Production Incident

All agents stop new work, Supervisor coordinates hotfix:

```
@All: PRODUCTION DOWN - Stop current work.
@DevOps: Investigate immediately.
@Supervisor: Coordinate hotfix.
```

### Need to Pause

Pause all agents:

```
@Supervisor: Pause all agents. I need to make a strategic decision.
```

Resume:

```
@Supervisor: Resume all agents. Continue with Week N plan.
```

---

## Tips for Success

### 1. Trust But Verify
- Let agents work autonomously
- Review daily standups
- Spot-check key changes

### 2. Clear Communication
- Be specific in requests
- Provide context
- Ask questions early

### 3. Manage Expectations
- 4 weeks is realistic but aggressive
- Some tasks may take longer
- Adjust timeline if needed

### 4. Leverage Parallelism
- Multiple agents can work simultaneously
- Supervisor prevents conflicts
- You multiply your productivity

### 5. Celebrate Progress
- Each week's checkpoint is a win
- Track metrics improving
- Share progress with stakeholders

---

## First Session Script

Copy/paste this to start your first session:

```
I'm activating the AGI Tracker agent orchestration system.

Phase 1: Supervisor Initialization
@Supervisor: You are the Supervisor Agent for the AGI Tracker project.

Your first actions:
1. Create .cursor/agents/status/ directory structure
2. Create FILE_OWNERSHIP.md from the template
3. Create WEEK_1_PLAN.md with detailed tasks for DevOps and Documentation agents
4. Create your first DAILY_STANDUP_YYYY-MM-DD.md

After initialization, activate:
- DevOps Agent on migration chain repair
- Documentation Agent on cleanup script

Report back when:
- All coordination files created
- Both agents briefed and started
- First status update available

Let's ship this! 🚀
```

---

## Questions?

**Common Issues**:
- "Agent not responding" → Reload agent prompt file
- "Merge conflict" → Supervisor handles, or reassign file
- "Wrong priority" → Update weekly plan via Supervisor
- "Need human decision" → Supervisor will escalate

**Getting Help**:
- Check agent .md files for detailed instructions
- Review FILE_OWNERSHIP.md for file conflicts
- Ask Supervisor for coordination issues
- Consult TROUBLESHOOTING.md for technical issues

---

## Next Steps

1. **Right Now**: Activate Supervisor Agent
2. **Next 5 min**: Activate DevOps + Documentation Agents
3. **Tomorrow**: Review first daily standup
4. **This Week**: Complete Week 1 checkpoint
5. **4 Weeks**: Launch! 🎉

---

**Ready to begin?** Activate the Supervisor Agent and let the team get to work!

Your repository is 70% done. These agents will complete the remaining 30%.

**Let's ship the AGI Tracker to production!** 💪

