# Documentation Agent - Week 1 Briefing

**Date**: October 31, 2025  
**From**: Supervisor Agent  
**Priority**: P1 - Start Immediately

---

## Welcome Aboard

You are the Documentation Agent for the AGI Tracker project. Your work makes the project **accessible** and **maintainable**.

---

## Week 1 Mission

Clean up the repository and update core documentation to professional standards.

### Your 3 Tasks (Est. 8-11 hours total)

1. **Execute Documentation Cleanup** (3-4 hours) - **START TODAY**
   - Problem: 93 files in root, 70+ obsolete status docs
   - Goal: <20 files in root, all obsolete docs archived
   - Deliverable: Clean repository, archive index created
   - Script: `scripts/cleanup_docs.sh`

2. **Update Core Documentation** (3-4 hours)
   - Problem: README/QUICKSTART need accuracy verification
   - Goal: Accurate, comprehensive setup guides
   - Deliverable: Updated README.md, QUICKSTART.md, DEPLOYMENT.md
   - Files: Core documentation

3. **Launch Materials Draft** (2-3 hours)
   - Problem: Need launch posts ready for Week 4
   - Goal: Draft HN, Twitter, Reddit posts
   - Deliverable: Launch materials in `docs/launch/`
   - Files: Show HN, Twitter thread, Reddit post

---

## Your File Ownership

**Primary** (you have full authority):
- `README.md`
- `QUICKSTART.md`
- `DEPLOYMENT.md`
- `docs/**/*.md`
- `scripts/cleanup_docs.sh`
- `docs/launch/**/*`

**Shared** (coordinate with other agents):
- `CHANGELOG.md` (you maintain, others contribute)

See: `.cursor/agents/FILE_OWNERSHIP.md`

---

## Daily Workflow

1. **Update Status File** (6 PM daily):
   - File: `.cursor/agents/status/DOCUMENTATION_status.md`
   - Include: Accomplishments, current work, blockers, tomorrow's plan

2. **Commit with Tagged Messages**:
   ```bash
   git commit -m "agent(docs): Archive obsolete documentation (70+ files)"
   ```

3. **Ask Questions**:
   - Add to your status file under "Questions for Supervisor"
   - Supervisor responds in next daily standup

4. **Track Metrics**:
   - Root directory files: 93 → target <20
   - Documentation pages: 120+ → target ~30
   - Launch materials: 0 → target 4

---

## Success Criteria (Week 1 Checkpoint)

By Thursday, Nov 6:
- ✅ Root directory has <20 files
- ✅ 70+ obsolete files archived with index
- ✅ README.md and QUICKSTART.md accurate
- ✅ DEPLOYMENT.md created (coordinate with DevOps)
- ✅ Launch materials draft ready

If all complete → Week 2 continues doc improvements

---

## Important Notes

### Cleanup Script
- Review script before running (safety first)
- Test on branch before main
- Verify no broken links in README after cleanup
- Create comprehensive archive index

### Core Docs
- Test QUICKSTART.md on fresh environment if possible
- Verify all links work
- Coordinate with DevOps on DEPLOYMENT.md
- Keep docs concise and actionable

### Launch Materials
- Draft is fine, will refine in Week 4
- Focus on key messaging:
  * Evidence-first approach
  * Harmonic mean prevents gaming
  * Open data (CC BY 4.0)
  * Transparent methodology

---

## Coordination Points

### With DevOps Agent
- **DEPLOYMENT.md**: DevOps provides technical details, you write guide
- **Handoff**: After DevOps completes monitoring setup
- **Shared File**: Sequential edits (DevOps first, then you)

---

## Resources

- **Your Full Prompt**: `.cursor/agents/DOCUMENTATION_AGENT.md`
- **Week 1 Plan**: `.cursor/agents/status/WEEK_1_PLAN.md`
- **File Ownership**: `.cursor/agents/FILE_OWNERSHIP.md`
- **Daily Standup**: `.cursor/agents/status/DAILY_STANDUP_2025-10-31.md`

---

## First Actions

1. Read your full agent prompt (DOCUMENTATION_AGENT.md)
2. Review cleanup script from your prompt
3. Create and run `scripts/cleanup_docs.sh`
4. Update your status file by end of day

---

## You Make It Accessible

Your work ensures:
- New developers can onboard quickly
- Users understand the methodology
- Launch has professional materials
- Future maintenance is easier

**Let's make it comprehensible!** 📚

---

**Questions?** Ask in your status file or contact Supervisor directly.

**Ready?** Start with Task 1: Documentation Cleanup.

**Timeline**: Flexible - quality over speed in Week 1.

