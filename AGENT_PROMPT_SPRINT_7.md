# Agent Prompt: Sprint 7 Implementation

## Required Reading

Before starting, read these files for context:
1. `AGENT_TASKS_PHASE_2.md` - Full task breakdown
2. `PHASE_2_PROGRESS.md` - What's completed (Sprints 4-6)
3. `SPRINT_4_COMPLETE.md` - Current infrastructure status

## Your Mission

Implement ALL tasks in Sprint 7 from AGENT_TASKS_PHASE_2.md:

### Task 7.1: Live News Scraping
- Replace fixtures with real arXiv API calls
- Add company blog RSS parsing (OpenAI, Anthropic, DeepMind, Meta AI)
- Add press release RSS (Reuters, AP)
- Set `SCRAPE_REAL=true` in config
- Add deduplication by URL
- Respect rate limits (3 sec between requests)

### Task 7.2: Weekly Digest Generation
- Implement digest generation in `services/etl/app/tasks/snap_index.py`
- Query events from past 7 days
- Generate LLM summary (2-3 paragraphs)
- Save to `public/digests/{date}.json`
- Create frontend page at `apps/web/app/digests/page.tsx`

### Task 7.3: Multi-Model Analysis
- Add Claude API support
- Run analysis through GPT-4 AND Claude
- Calculate consensus scores
- Flag high-variance events (models disagree)
- Add frontend consensus indicator

### Bonus Task 6.1: Retraction UI
- Add `/v1/admin/events/{id}/retract` endpoint
- Create RetractionBanner component
- Add retract button to event cards (admin only)

## Critical Rules

1. **Work on main branch only** - NO PRs, NO feature branches
2. **Commit after each task** with descriptive messages
3. **Test after each commit** - verify API still works
4. **Update PHASE_2_PROGRESS.md** as you complete tasks
5. **If blocked, create BLOCKED_SPRINT_7.md** and continue with other tasks

## Git Workflow

```bash
git checkout main
git pull origin main

# After each task:
git add -A
git commit -m "feat(sprint-7.X): description"
git push origin main
```

## Testing

```bash
# Test API health
curl https://api-production-8535.up.railway.app/health

# Check Railway logs
railway logs -s api

# Test new endpoints
curl https://api-production-8535.up.railway.app/v1/events
```

## Success Criteria

- [ ] Task 7.1: Real data ingesting (50+ events from arXiv, blogs, press)
- [ ] Task 7.2: Weekly digest generates and displays
- [ ] Task 7.3: Multi-model consensus working
- [ ] Task 6.1: Retraction UI functional
- [ ] All committed to main
- [ ] Railway services still healthy
- [ ] API responding correctly

## Start Now

Begin with Task 7.1 (Live News Scraping). Work through ALL tasks sequentially. Commit frequently. Test thoroughly.

Good luck!

