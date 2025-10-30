# Mission: Complete CI/CD Pipeline & Deployment Automation

You are a DevOps engineer completing the CI/CD infrastructure for the AGI Signpost Tracker. Sprints 8-10 are done (security, performance, UX). Your job: automate EVERYTHING.

## Context
- Project: AGI Signpost Tracker (evidence-based AGI progress tracking)
- Repository: https://github.com/hankthevc/AGITracker
- Recent work: Sprints 8-10 just shipped (security, performance, UX)
- Tech stack: Next.js 14, FastAPI, PostgreSQL, Redis, Celery
- Project path: /Users/HenryAppel/AI Doomsday Tracker
- Read FIRST: README.md, SPRINT_10_COMPLETE.md, PHASE_2_PROGRESS.md

## What's Already Done (Don't Duplicate)
- ✅ API key authentication (Sprint 8)
- ✅ Security headers (Sprint 8)
- ✅ Performance indexes (Sprint 9)
- ✅ Full-text search (Sprint 10)
- ✅ Mobile optimization (Sprint 10)
- ✅ One workflow exists: .github/workflows/ci.yml

## Your Tasks

### 1. Complete GitHub Actions CI/CD Pipeline

#### Audit Existing Workflow
- Review .github/workflows/ci.yml thoroughly
- Identify gaps, missing jobs, or inefficiencies
- Check if it's actually running (look at GitHub Actions tab)
- Test locally if possible

#### Create Missing Workflows
Create these if they don't exist or are incomplete:

**A. Deployment Workflow** (.github/workflows/deploy.yml):
- Trigger: Successful merge to main after CI passes
- Jobs:
  - deploy-frontend: Deploy to Vercel via CLI
  - deploy-backend: Deploy to Railway via CLI
  - run-migrations: Alembic migrations automatically
  - smoke-test: Hit /health endpoint post-deploy
- Use secrets: VERCEL_TOKEN, RAILWAY_TOKEN (already in GitHub)
- Post deployment status to commit
- Rollback on failure

**B. E2E Nightly Tests** (.github/workflows/e2e-nightly.yml):
- Schedule: 2 AM UTC daily (cron: '0 2 * * *')
- Manual trigger option (workflow_dispatch)
- Start test database + Redis in Docker
- Run Playwright tests from apps/web/e2e/
- Upload artifacts: screenshots, videos, trace
- Create GitHub issue if tests fail
- Tag with "e2e-failure" label

**C. Dependency Updates** (.github/workflows/dependencies.yml):
- Schedule: Weekly on Mondays
- Run npm audit, pip-audit
- Check for outdated packages
- Create PR with updates
- Run CI on that PR automatically

#### Add Advanced Features
- Cache optimization (npm cache, pip cache, Docker layers)
- Parallel job execution where possible
- Conditional jobs (skip E2E if only docs changed)
- Matrix testing (test on multiple Node/Python versions)
- Performance budgets (fail if bundle size increases >10%)

### 2. Pre-commit Hooks (Developer Experience)

Create .pre-commit-config.yaml:
```yaml
repos:
  - repo: local
    hooks:
      - id: ruff-format
        name: Ruff Format
        entry: ruff format
        language: system
        types: [python]
      - id: ruff-check
        name: Ruff Check
        entry: ruff check
        language: system
        types: [python]
      - id: prettier
        name: Prettier
        entry: prettier --write
        language: system
        types: [javascript, typescript, json, yaml, markdown]
      - id: eslint
        name: ESLint
        entry: eslint --fix
        language: system
        types: [typescript, javascript]
      - id: no-commit-to-main
        name: Don't commit to main
        entry: bash -c 'if [ "$(git branch --show-current)" = "main" ]; then echo "Cannot commit directly to main!"; exit 1; fi'
        language: system
        always_run: true
```

Add installation instructions to CONTRIBUTING.md

### 3. Railway Celery Workers (CRITICAL - BLOCKED ITEM)

**This is the #1 blocker from BLOCKED.md:**

- Read BLOCKED.md and RAILWAY_DEPLOYMENT.md carefully
- Document exact manual steps needed
- Create automation script if possible: scripts/deploy-celery-railway.sh
- If automation isn't possible, create crystal-clear manual instructions
- Verify environment variables are documented
- Create health check for workers

### 4. Status Badges & Monitoring

Add to README.md:
```markdown
[![CI](https://github.com/hankthevc/AGITracker/workflows/CI/badge.svg)](https://github.com/hankthevc/AGITracker/actions)
[![Deploy](https://github.com/hankthevc/AGITracker/workflows/Deploy/badge.svg)](https://github.com/hankthevc/AGITracker/actions)
[![E2E](https://github.com/hankthevc/AGITracker/workflows/E2E%20Nightly/badge.svg)](https://github.com/hankthevc/AGITracker/actions)
```

### 5. Deep Dependency Audit

**Go DEEP - surface all issues:**

#### Frontend Dependencies (apps/web/package.json)
- Run npm audit and document all vulnerabilities
- Check for unused dependencies (use depcheck)
- Identify packages with better alternatives
- Check bundle size impact (use webpack-bundle-analyzer)
- Look for duplicate dependencies in lockfile
- Verify all @types packages are in devDependencies
- Check for deprecated packages

#### Backend Dependencies (services/etl/pyproject.toml)
- Run pip-audit
- Check for unused imports (use autoflake)
- Identify outdated packages (pip list --outdated)
- Check for security advisories (safety check)
- Verify version pinning is appropriate
- Look for conflicting transitive dependencies

#### Create Report
- docs/dependency-audit.md with findings
- Categorize: Critical, High, Medium, Low
- Provide recommendations
- Create issues for critical items

### 6. Docker Optimization

Review and optimize:
- Dockerfile for backend
- docker-compose.dev.yml
- Multi-stage builds to reduce image size
- Layer caching optimization
- Security scanning (trivy or similar)
- Non-root user in containers
- Health checks in docker-compose

### 7. Environment Variable Management

- Audit all required env vars across services
- Update .env.example with ALL variables
- Create .env.template for each service
- Add validation script: scripts/validate-env.sh
- Document which vars are required vs optional
- Check for hardcoded secrets (grep -r "sk-" .)

## Success Criteria
- [ ] Full CI/CD pipeline with zero manual steps
- [ ] E2E tests run nightly with failure notifications
- [ ] Pre-commit hooks prevent bad commits
- [ ] Celery workers deployment documented/automated
- [ ] Dependency audit complete with action plan
- [ ] Docker images optimized and secure
- [ ] All env vars documented and validated

## Deliverables
1. .github/workflows/deploy.yml (deployment automation)
2. .github/workflows/e2e-nightly.yml (nightly E2E)
3. .github/workflows/dependencies.yml (dependency updates)
4. .pre-commit-config.yaml (pre-commit hooks)
5. scripts/deploy-celery-railway.sh or detailed manual steps
6. docs/dependency-audit.md (comprehensive audit report)
7. Updated Dockerfile with optimizations
8. scripts/validate-env.sh (env var validation)
9. Update CONTRIBUTING.md with CI/CD workflow
10. Update README.md with status badges
11. docs/ci-cd.md (complete pipeline documentation)

## Deep Dive Requirements
- Test EVERYTHING locally before committing
- Document all assumptions
- Surface ALL dependency issues, don't hide them
- Provide specific version recommendations
- Include cost/benefit analysis for changes
- Note any breaking changes

## Resources
- GitHub Actions: https://docs.github.com/en/actions
- Vercel CLI: https://vercel.com/docs/cli
- Railway CLI: https://docs.railway.app/develop/cli
- Pre-commit: https://pre-commit.com/
- npm audit: https://docs.npmjs.com/cli/v8/commands/npm-audit
- pip-audit: https://pypi.org/project/pip-audit/

Create a feature branch, test thoroughly, document everything, and open a PR when complete. Good luck! 🚀

