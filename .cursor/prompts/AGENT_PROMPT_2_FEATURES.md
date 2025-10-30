# Mission: Phase 3 Features + Deep Code Quality Review

You are a senior full-stack engineer building Phase 3 features AND conducting a deep code quality audit. Sprint 8-10 work is done. Your job: ship Phase 3 features while surfacing all code issues.

## Context
- Project: AGI Signpost Tracker
- Recent work: Sprint 8-10 just shipped (8,494 insertions!)
- Current version: v1.0.0 (production)
- Project path: /Users/HenryAppel/AI Doomsday Tracker
- Read FIRST: README.md, ROADMAP.md, SPRINT_10_COMPLETE.md

## What's Already Done (Build On This)
- ✅ Full-text search (Sprint 10)
- ✅ Advanced filtering (Sprint 10)
- ✅ Mobile optimization (Sprint 10)
- ✅ Keyboard shortcuts (Sprint 10)
- ✅ API key management (Sprint 8)
- ✅ Performance indexes (Sprint 9)

## Phase 3 Features to Build

### 1. Signpost Deep-Dive Pages (/signposts/[code])

**Goal**: Educational, comprehensive page for each of 27 signposts

Create: apps/web/app/signposts/[code]/page.tsx

**Sections**:
1. **Hero**: Signpost name, category badge, current progress bar
2. **Why This Matters**: 
   - Economic impact explanation
   - Technical significance
   - Connection to AGI timeline
3. **Current State**:
   - Baseline → Current → Target with visual
   - Data source with tier badge
   - Last updated timestamp
4. **Methodology**:
   - How we measure this
   - Scoring formula
   - Why we chose this metric
5. **Linked Events Timeline**:
   - All events mapped to this signpost
   - Chronological order
   - Impact on progress over time
   - Mini event cards
6. **Expert Predictions**:
   - Pull from expert_predictions table
   - Show forecast vs reality
   - Days ahead/behind schedule
   - Multiple sources (AI2027, Aschenbrenner, etc.)
7. **Academic Citations**:
   - Key papers (from signpost.citations field if exists)
   - Links to arXiv/papers
   - Brief summaries
8. **Related Signposts**:
   - Other signposts in same category
   - Dependencies/prerequisites

**Backend Support**:
- GET /v1/signposts/by-code/{code}/full
- Returns: signpost + events + predictions + related
- Cache for 1 hour
- Include confidence intervals

### 2. Custom Preset Builder (/presets/custom)

**Goal**: Let users create and save custom category weights

Create: apps/web/app/presets/custom/page.tsx

**Features**:
- 4 sliders for category weights (Capabilities, Agents, Inputs, Security)
- Real-time index calculation as they adjust
- Comparison view: Show custom vs Equal vs Aschenbrenner
- Save preset to localStorage
- Name custom presets
- Download as JSON
- Share via URL (encode weights in query params)

**Backend Support**:
- GET /v1/index/custom?weights={"capabilities":0.4,"agents":0.3,...}
- Validate weights sum to 1.0
- Return calculated index
- Cache with weight hash

### 3. Historical Index Chart (enhance home page)

**Goal**: Show index progress over time

Add to: apps/web/app/page.tsx

**Chart Features**:
- Line chart showing overall index over time
- Multiple preset lines (Equal, Aschenbrenner, AI-2027)
- Annotations for major events (GPT-4o, Claude 3.5, etc.)
- Zoom controls (1 month, 3 months, 6 months, all time)
- Hover to see exact value + date
- Download as PNG
- Responsive (works on mobile)

**Backend Support**:
- GET /v1/index/history?preset=equal&days=90
- Returns: Array of {date, value, events} objects
- Aggregate daily snapshots
- Include major events for annotations

### 4. Advanced Search Enhancements

Build on Sprint 10's search:
- Add filters to search dropdown (tier, date range)
- Search in signpost names and descriptions
- Search in digest content
- Keyboard navigation in results (arrow keys)
- Search history (last 5 searches in localStorage)

### 5. Export Enhancements

Add new export formats:
- PDF export for reports (use jsPDF)
- Excel export for events (use xlsx)
- iCal export for timeline events
- Add to existing export buttons

## Code Quality Deep Dive

**CRITICAL**: While building features, audit ALL code:

### Frontend Code Review

**Audit these directories:**
- apps/web/app/ (all pages)
- apps/web/components/ (all components)
- apps/web/lib/ (utilities)
- apps/web/hooks/ (custom hooks)

**Look for:**
1. **React anti-patterns**:
   - Missing useCallback on callbacks
   - Missing useMemo on expensive computations
   - Improper dependency arrays
   - Props drilling (should use context)
   - Re-renders (use React DevTools Profiler)

2. **TypeScript issues**:
   - Any usage of `any` type (replace with proper types)
   - Missing types on function params
   - Implicit returns that should be explicit
   - Unused imports

3. **Performance issues**:
   - Large bundle imports (import whole library vs specific function)
   - Missing code splitting
   - Unoptimized images
   - Unnecessary re-renders

4. **Accessibility**:
   - Missing ARIA labels
   - Keyboard navigation issues
   - Color contrast problems
   - Missing alt text

5. **Security**:
   - XSS vulnerabilities (dangerouslySetInnerHTML)
   - Hardcoded secrets
   - Insecure API calls

**Create**: docs/frontend-code-audit.md

### Backend Code Review

**Audit these files:**
- services/etl/app/main.py (2000+ lines - needs review)
- services/etl/app/models.py
- services/etl/app/tasks/ (all Celery tasks)
- services/etl/app/utils/ (all utilities)

**Look for:**
1. **Python anti-patterns**:
   - Missing type hints
   - Overly long functions (>50 lines)
   - Nested conditionals (>3 levels)
   - Magic numbers (should be constants)
   - Mutable default arguments

2. **Database issues**:
   - N+1 queries
   - Missing indexes
   - Inefficient queries
   - SQL injection risks

3. **API design**:
   - Inconsistent naming
   - Missing validation
   - Poor error messages
   - Missing pagination

4. **Error handling**:
   - Bare except clauses
   - Not logging errors
   - Swallowing exceptions
   - Missing rollback on error

5. **Security**:
   - SQL injection
   - Command injection
   - Path traversal
   - Insecure random

**Create**: docs/backend-code-audit.md

### Database Schema Review

**Audit**: services/etl/app/models.py

**Look for**:
- Missing indexes on foreign keys
- Missing unique constraints
- Nullable fields that shouldn't be
- Missing cascade deletes
- Inefficient data types

**Create**: docs/database-schema-audit.md

## Success Criteria
- [ ] All 27 signposts have deep-dive pages
- [ ] Custom preset builder functional
- [ ] Historical chart on home page
- [ ] Enhanced search with filters
- [ ] 3+ export formats (PDF, Excel, iCal)
- [ ] Frontend code audit complete with action items
- [ ] Backend code audit complete with action items
- [ ] Database schema audit complete

## Deliverables

**Phase 3 Features**:
1. apps/web/app/signposts/[code]/page.tsx
2. apps/web/app/presets/custom/page.tsx
3. Enhanced home page with historical chart
4. Search enhancements
5. Export enhancements (PDF, Excel, iCal)
6. Backend endpoints for new features

**Code Audits**:
7. docs/frontend-code-audit.md (comprehensive)
8. docs/backend-code-audit.md (comprehensive)
9. docs/database-schema-audit.md
10. Create GitHub issues for top 10 critical findings
11. Fix at least 5 critical issues you find

**Documentation**:
12. Update README.md with new features
13. Add user guide: docs/guides/signpost-deep-dives.md
14. Add user guide: docs/guides/custom-presets.md

## Deep Dive Requirements
- Don't just list issues - categorize by severity
- Provide specific line numbers and files
- Include code snippets showing the problem
- Suggest concrete fixes with example code
- Estimate effort for each fix (S/M/L)
- Prioritize by impact

## Resources
- Next.js Best Practices: https://nextjs.org/docs/app/building-your-application/optimizing
- React Profiler: https://react.dev/reference/react/Profiler
- ESLint Rules: https://eslint.org/docs/latest/rules/
- WCAG Guidelines: https://www.w3.org/WAI/WCAG21/quickref/

Create a feature branch, build features, audit code, document findings, open PR. Good luck! 🎨

