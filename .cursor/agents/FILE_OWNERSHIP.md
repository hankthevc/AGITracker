# File Ownership Matrix

**Last Updated**: 2025-10-30  
**Purpose**: Prevent merge conflicts by clearly assigning file ownership to agents

---

## Ownership Rules

1. **Primary Owner**: Agent has full authority to edit these files
2. **Shared**: Must coordinate with Supervisor before editing
3. **Read-Only**: Agent can read but should not edit

---

## DevOps Agent (Primary Owner)

### Infrastructure & Deployment
- `infra/migrations/**/*` - All migration files
- `infra/docker/**/*` - Dockerfiles
- `docker-compose.dev.yml` - Development environment
- `Dockerfile` - Production Docker config
- `railway.json` - Railway deployment config
- `.github/workflows/**/*` - CI/CD pipelines

### Monitoring & Operations
- `infra/monitoring/**/*` - Alert policies, dashboards
- `scripts/backup_production.sh` - Backup script
- `DEPLOYMENT.md` - Deployment guide

### Configuration (Shared)
- `.env.example` - Coordinate with Backend Agent
- `Makefile` - Coordinate before adding new targets

---

## Backend Agent (Primary Owner)

### ETL Pipeline
- `services/etl/app/tasks/**/*` - All Celery tasks
- `services/etl/app/celery_app.py` - Celery configuration
- `services/etl/app/celery_config.py` - Celery settings
- `services/etl/app/utils/llm_budget.py` - LLM budget manager
- `services/etl/app/utils/fetcher.py` - HTTP client

### Scripts
- `scripts/test_ingestion_live.py` - Live ingestion test
- `scripts/monitor_celery_tasks.py` - Task monitoring
- `scripts/backfill_live_news.py` - News backfill
- `scripts/run_ingestors.py` - Ingestor runner

### Database (Read-Only)
- `services/etl/app/models.py` - Read schemas, coordinate changes with DevOps

### API Routes (Shared - Assign Sections)
- `services/etl/app/main.py` - **Coordinate with Supervisor**
  - Lines 1-500: Backend Agent (events endpoints)
  - Lines 501-1000: DevOps Agent (health/monitoring)
  - Lines 1001-2000: Backend Agent (LLM analysis)
  - Lines 2001-3361: Testing Agent (admin endpoints)

---

## Frontend Agent (Primary Owner)

### Web Application
- `apps/web/app/**/*.tsx` - All pages
- `apps/web/components/**/*.tsx` - All components
- `apps/web/hooks/**/*.ts` - Custom hooks
- `apps/web/lib/**/*.ts` - Utilities
- `apps/web/styles/**/*.css` - Styles
- `apps/web/public/**/*` - Static assets (images, manifest, etc.)

### Configuration
- `apps/web/tailwind.config.ts` - Tailwind config
- `apps/web/next.config.js` - Next.js config
- `apps/web/components.json` - shadcn/ui config
- `apps/web/tsconfig.json` - TypeScript config

### Shared Libraries (Coordinate)
- `packages/scoring/typescript/**/*` - Coordinate with Backend on algorithm changes

---

## Testing Agent (Primary Owner)

### Test Files
- `apps/web/e2e/**/*.ts` - Playwright E2E tests
- `services/etl/tests/**/*.py` - Backend unit tests
- `tests/load/**/*` - Load testing scripts
- `tests/smoke-test.sh` - Smoke test script

### Test Configuration
- `apps/web/playwright.config.ts` - Playwright config
- `services/etl/pytest.ini` - pytest config (if created)

### Documentation
- `docs/SECURITY_AUDIT.md` - Security audit report

### CI Workflows (Shared with DevOps)
- `.github/workflows/ci*.yml` - Coordinate changes with DevOps

---

## Documentation Agent (Primary Owner)

### Core Documentation
- `README.md` - Project overview
- `QUICKSTART.md` - Setup guide
- `DEPLOYMENT.md` - Deployment procedures
- `CONTRIBUTING.md` - Contribution guidelines
- `CHANGELOG.md` - Change log

### User Guides
- `docs/**/*.md` - All documentation
- `docs/user-guides/**/*` - User guides
- `docs/launch/**/*` - Launch materials

### Scripts
- `scripts/cleanup_docs.sh` - Documentation cleanup

### Archive (Read-Only After Cleanup)
- `docs/archive/**/*` - Historical docs (preserve as-is)

---

## Shared Files (Supervisor Coordination Required)

### Package Management
- `package.json` (root) - Coordinate all changes
- `package-lock.json` (root) - Auto-generated, review before commit
- `apps/web/package.json` - Frontend Agent primary, coordinate major changes
- `services/etl/requirements.txt` - Backend Agent primary, coordinate major changes

### Environment
- `.env.example` - DevOps & Backend coordinate
- `.gitignore` - Coordinate before adding rules

### Database Schema
- `services/etl/app/models.py` - Backend reads, DevOps writes migrations
- Any schema changes MUST go through DevOps Agent for migration

### Scoring Logic (Critical - Dual Implementation)
- `packages/scoring/python/**/*` - Backend Agent
- `packages/scoring/typescript/**/*` - Frontend Agent
- **MUST STAY IN SYNC** - Coordinate all algorithm changes

---

## Special Cases

### main.py (3361 lines - Section Assignment)

```python
# services/etl/app/main.py

# Lines 1-100: Imports & Setup (Backend Agent)
# Lines 101-500: Events API (/v1/events/*) (Backend Agent)
# Lines 501-800: Index API (/v1/index) (Backend Agent)
# Lines 801-1200: Signposts API (/v1/signposts/*) (Backend Agent)
# Lines 1201-1600: Evidence API (/v1/evidence/*) (Backend Agent)
# Lines 1601-2000: Analysis API (/v1/analysis/*) (Backend Agent)
# Lines 2001-2400: Admin API (/v1/admin/*) (Testing Agent - for test setup)
# Lines 2401-2800: Health & Monitoring (/health/*) (DevOps Agent)
# Lines 2801-3361: Utility endpoints (Backend Agent)
```

**Protocol**:
1. Agent creates a branch: `agent/[name]/main-py-lines-[start]-[end]`
2. Edits only assigned lines
3. Commits with clear message: `agent(backend): Update events API (lines 101-500)`
4. Supervisor merges sequentially to avoid conflicts

---

## Conflict Resolution Protocol

### When Two Agents Need Same File

1. **Identify Conflict Early**: Daily standup detects this
2. **Supervisor Assigns Sections**: Assigns line ranges or sequential edits
3. **Agent A Edits First**: Commits to branch `agent/a/feature`
4. **Agent B Pulls and Rebases**: Gets A's changes, then edits
5. **Supervisor Integrates**: Tests combined changes

### Example: Both Editing models.py

```bash
# Scenario: DevOps adding migration, Backend reading for task

# DevOps: Goes first (has migration authority)
git checkout -b agent/devops/add-approved-at
# Edit models.py: Add approved_at column
git commit -m "agent(devops): Add approved_at to event_signpost_links"
git push

# Backend: Waits, then pulls
git checkout main
git pull origin agent/devops/add-approved-at
git checkout -b agent/backend/use-approved-at
# Edit tasks to use new column
git commit -m "agent(backend): Use approved_at in review queue"
git push

# Supervisor: Merges both
git merge agent/devops/add-approved-at
git merge agent/backend/use-approved-at
```

---

## Ownership Changelog

### 2025-10-30
- Initial ownership matrix created
- main.py sections assigned
- Shared file rules established

### [Future Dates]
- Document ownership changes here
- Note when files transfer between agents

---

## Questions?

Contact Supervisor Agent if:
- Unclear who owns a file
- Need to edit a shared file
- Two agents need same file simultaneously
- Want to propose ownership change

Supervisor will resolve conflicts and update this document.

