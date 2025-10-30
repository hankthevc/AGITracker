# Mission: World-Class Documentation + Developer Experience Audit

You are a technical writer and DX specialist creating comprehensive documentation AND auditing the entire developer experience. Sprint 8-10 are done. Your job: make this the best-documented AGI tracker project.

## Context
- Project: AGI Signpost Tracker
- Recent work: Sprints 8-10 added 52 files, 8,494 lines
- Current docs: README.md, QUICKSTART.md, ROADMAP.md, multiple SPRINT_*.md
- Project path: /Users/HenryAppel/AI Doomsday Tracker
- Read FIRST: README.md, QUICKSTART.md, all SPRINT_*_COMPLETE.md files

## What's Already Done
- ✅ Comprehensive README (updated recently)
- ✅ QUICKSTART guide
- ✅ Multiple sprint completion docs
- ✅ API with OpenAPI/Swagger docs

## Your Tasks

### 1. Documentation Site (High Priority)

**Goal**: Professional docs site at docs.agi-tracker.vercel.app

#### A. Set Up Docusaurus
```bash
cd docs
npx create-docusaurus@latest . classic --typescript
```

#### B. Site Structure
```
docs/
├── docs/
│   ├── intro.md
│   ├── getting-started/
│   │   ├── installation.md
│   │   ├── configuration.md
│   │   └── first-steps.md
│   ├── features/
│   │   ├── events-feed.md
│   │   ├── timeline.md
│   │   ├── signpost-deep-dives.md
│   │   ├── custom-presets.md
│   │   ├── rag-chatbot.md
│   │   └── scenario-explorer.md
│   ├── api/
│   │   ├── overview.md
│   │   ├── authentication.md
│   │   ├── endpoints.md
│   │   └── examples.md
│   ├── architecture/
│   │   ├── overview.md
│   │   ├── frontend.md
│   │   ├── backend.md
│   │   └── database.md
│   ├── contributing/
│   │   ├── code-standards.md
│   │   ├── pull-requests.md
│   │   └── testing.md
│   └── deployment/
│       ├── vercel.md
│       ├── railway.md
│       └── production.md
├── blog/
│   └── 2025-10-29-sprint-10-complete.md
├── src/
└── docusaurus.config.js
```

#### C. Deploy to Vercel
- Configure vercel.json for docs subdomain
- Deploy docs site
- Add link to main README

### 2. API Documentation Enhancement

**Goal**: Best-in-class API docs

#### A. OpenAPI Enhancements
Edit services/etl/app/main.py:
- Add detailed descriptions to EVERY endpoint
- Include request/response examples for all
- Document all query parameters
- Add response codes and error examples
- Group endpoints by tag
- Add authentication requirements
- Document rate limits

#### B. Interactive API Playground
Create: apps/web/app/api-playground/page.tsx

**Features**:
- Dropdown to select endpoint
- Auto-generate form from endpoint params
- "Try it" button with real API calls
- Formatted JSON response viewer
- Request/response headers display
- Example requests for common use cases
- API key input field
- Save favorites to localStorage

#### C. API Quick Reference
Create: docs/api/QUICK_REFERENCE.md

Table format:
| Endpoint | Method | Auth | Rate Limit | Description |
|----------|--------|------|------------|-------------|

Include curl examples for each.

### 3. User Guides (Create 8+ Comprehensive Guides)

**All guides in**: docs/guides/

#### Guide 1: events-feed.md
- Overview of events feed
- Using filters (tier, date, category)
- Understanding tier badges
- Searching events
- Exporting data (JSON, CSV, PDF, Excel)
- Screenshots with annotations

#### Guide 2: timeline-visualization.md
- Understanding the timeline
- Scatter vs cumulative view
- Filtering and searching
- Interpreting significance scores
- Screenshots

#### Guide 3: signpost-deep-dives.md
- What are signposts
- Navigating deep-dive pages
- Understanding metrics
- Expert predictions comparison
- Related signposts

#### Guide 4: custom-presets.md
- What are presets
- Creating custom weights
- Saving and sharing
- Comparing presets
- Use cases

#### Guide 5: rag-chatbot.md
- How to use the chatbot
- Best practices for questions
- Understanding citations
- Limitations (out-of-scope)
- Example conversations

#### Guide 6: scenario-explorer.md
- What-if analysis
- Adjusting signpost progress
- Saving scenarios
- Sharing scenarios
- Use cases

#### Guide 7: admin-panel.md
- Accessing admin features
- API key management
- Review queue workflow
- URL validation
- Analytics dashboard

#### Guide 8: api-usage.md
- Getting started
- Authentication
- Common queries
- Code examples (Python, JavaScript, curl)
- Rate limiting
- Best practices

**Each guide must have**:
- Clear learning objectives
- Step-by-step instructions
- Screenshots or diagrams
- Code examples
- Troubleshooting section
- "Next steps" links

### 4. Video Walkthrough Scripts

Create: docs/video-scripts/

**Scripts for future video recording**:

#### Script 1: getting-started.md (5 min)
- Project overview
- Installation
- First run
- Accessing UI

#### Script 2: events-and-timeline.md (5 min)
- Browsing events
- Using filters
- Timeline visualization
- Exporting data

#### Script 3: admin-features.md (7 min)
- API key management
- Review queue
- Analytics
- System monitoring

#### Script 4: api-tutorial.md (8 min)
- API authentication
- Common endpoints
- Python examples
- Best practices

#### Script 5: advanced-features.md (10 min)
- RAG chatbot
- Scenario explorer
- Custom presets
- Advanced analytics

**Each script includes**:
- Exact words to say
- Actions to demonstrate
- Screen transitions
- Time markers

### 5. Developer Experience Audit

**CRITICAL**: Deep dive into DX

Create: docs/developer-experience-audit.md

#### A. Onboarding Experience
- Clone repo
- Install dependencies
- First run
- First contribution

**Time each step. Document friction points.**

Test onboarding:
- Fresh Mac (simulate with new directory)
- Record every command needed
- Note every error encountered
- Time from clone to running app

**Report**:
- Current time: X minutes
- Friction points: Y issues
- Recommended improvements
- Target time: Z minutes

#### B. Local Development Experience
- How easy is it to run locally?
- Are error messages helpful?
- Is hot reload working?
- Are types helping or hindering?
- Is debugging easy?

**Test scenarios**:
1. Make a small UI change
2. Add a new API endpoint
3. Fix a bug
4. Run tests

Time each. Document pain points.

#### C. Testing Experience
- How do you run tests?
- Are tests fast?
- Are error messages clear?
- Is coverage useful?
- E2E tests easy to run?

#### D. Deployment Experience
- How easy to deploy?
- Is it documented?
- Are errors clear?
- How do you rollback?

#### E. Documentation Quality
- Is README helpful?
- Is QUICKSTART accurate?
- Are API docs complete?
- Are guides discoverable?

**Create**: DX improvement roadmap with priorities

### 6. Contribution Guide Enhancement

Expand CONTRIBUTING.md:

**Add sections**:
1. **Development Setup** (detailed)
2. **Code Standards** (with examples)
3. **Git Workflow** (branch naming, commits)
4. **Testing Requirements** (when to test, how to test)
5. **Documentation Requirements** (when to update docs)
6. **Pull Request Process** (checklist)
7. **Example PRs** (3+ with detailed walkthroughs)

**Example PR Walkthroughs**:
- Example 1: Adding a new API endpoint
  - Step-by-step code
  - Tests to write
  - Docs to update
  - PR description template

- Example 2: Creating a new React component
  - Component structure
  - Props typing
  - Styling with Tailwind
  - Tests
  - Storybook (if applicable)

- Example 3: Adding a database migration
  - Alembic commands
  - Migration file structure
  - Testing migration
  - Rollback plan

### 7. Dependency Documentation

Create: docs/dependencies.md

**For each major dependency**:
- What it does
- Why we chose it
- Alternatives considered
- Version requirements
- Configuration
- Common issues

**Frontend deps**: Next.js, React, Tailwind, shadcn/ui, SWR, Recharts, etc.
**Backend deps**: FastAPI, SQLAlchemy, Celery, Redis, OpenAI, etc.

### 8. Troubleshooting Guide

Create: docs/TROUBLESHOOTING.md

**Common issues**:
- "Port 3000 already in use"
- "Database connection failed"
- "Redis connection failed"
- "API key invalid"
- "Migration failed"
- "Build failed"
- "Tests failing"

**Each issue needs**:
- Error message
- Cause
- Solution
- Prevention

### 9. JSDoc/Docstrings Audit

**Add comprehensive documentation to code**:

#### Frontend (TypeScript)
Add JSDoc to:
- All components in apps/web/components/
- All utilities in apps/web/lib/
- All hooks in apps/web/hooks/
- All API functions

**Format**:
```typescript
/**
 * Fetches events from the API with optional filters
 * 
 * @param filters - Optional filters for tier, date, category
 * @param page - Page number for pagination (default: 1)
 * @returns Promise resolving to events array
 * @throws {APIError} If the API request fails
 * 
 * @example
 * ```ts
 * const events = await fetchEvents({ tier: 'A', page: 1 });
 * ```
 */
```

#### Backend (Python)
Add docstrings to:
- All functions in services/etl/app/main.py
- All Celery tasks
- All utilities
- All models

**Format** (Google style):
```python
def fetch_events(tier: str | None = None, limit: int = 50) -> list[Event]:
    """
    Fetches events from database with optional filtering.
    
    Args:
        tier: Evidence tier filter ('A', 'B', 'C', or 'D')
        limit: Maximum number of events to return (default: 50)
        
    Returns:
        List of Event objects matching filters
        
    Raises:
        ValueError: If tier is invalid
        
    Examples:
        >>> events = fetch_events(tier='A', limit=10)
        >>> len(events)
        10
    """
```

### 10. Changelog Maintenance

Update CHANGELOG.md:
- Add entries for Sprints 8-10
- Follow Keep a Changelog format
- Categorize: Added, Changed, Fixed, Removed
- Link to PRs and issues
- Include migration notes

## Success Criteria
- [ ] Docusaurus site deployed at docs.agi-tracker.vercel.app
- [ ] 8+ comprehensive user guides
- [ ] API docs enhanced with examples
- [ ] Interactive API playground working
- [ ] 5 video scripts complete
- [ ] Developer experience audit with roadmap
- [ ] CONTRIBUTING.md with 3+ example PRs
- [ ] All TypeScript has JSDoc
- [ ] All Python has docstrings
- [ ] TROUBLESHOOTING.md with 10+ issues

## Deliverables
1. docs/ directory with Docusaurus site
2. 8+ user guides in docs/guides/
3. 5 video scripts in docs/video-scripts/
4. Enhanced OpenAPI docs in main.py
5. apps/web/app/api-playground/page.tsx
6. docs/developer-experience-audit.md
7. docs/dependencies.md
8. docs/TROUBLESHOOTING.md
9. Expanded CONTRIBUTING.md
10. JSDoc for all TypeScript
11. Docstrings for all Python
12. Updated CHANGELOG.md
13. docs/api/QUICK_REFERENCE.md

## Deep Dive Requirements
- Test every guide yourself (actually follow the steps)
- Find gaps in existing docs
- Identify outdated information
- Check all links work
- Verify all code examples run
- Time the onboarding process
- Document EVERYTHING you struggle with

## Resources
- Docusaurus: https://docusaurus.io/
- TSDoc: https://tsdoc.org/
- Google Style Docstrings: https://google.github.io/styleguide/pyguide.html
- Write the Docs: https://www.writethedocs.org/guide/

Create a feature branch, build docs, audit DX, test everything, open PR. Good luck! 📚

