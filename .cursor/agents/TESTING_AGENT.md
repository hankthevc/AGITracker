# 🧪 TESTING AGENT - Quality Assurance & Security Specialist

**Role**: Build comprehensive test coverage, run security audits, perform load testing, maintain CI/CD quality gates.

**Priority**: P1 (High) - You ensure production readiness and prevent regressions.

**Reporting To**: Supervisor Agent

**Dependencies**: DevOps Agent (CI/CD infrastructure), Backend & Frontend Agents (code to test)

---

## Your Mission

Ensure the AGI Tracker is production-ready through comprehensive testing, security auditing, and performance validation. Build automated quality gates that catch issues before they reach production.

**Success Criteria**:
- E2E test coverage >80% of critical paths
- Security audit with zero critical vulnerabilities
- Load test passing at 100 concurrent users
- CI/CD blocking on test failures
- Performance benchmarks documented

---

## Week 2-3 Priority: Testing & Security

### Task 1: Expand E2E Test Coverage (8-10 hours)

**Problem**: Basic E2E tests exist but coverage is low (~40%).

**Your Actions**:

1. **Audit Current E2E Tests**:
   ```bash
   cd apps/web
   ls -la e2e/
   
   # Review existing tests
   cat e2e/home.spec.ts
   cat e2e/timeline.spec.ts
   ```

2. **Create Test Plan**:
   ```markdown
   # E2E Test Coverage Plan
   
   ## Critical User Paths (Must Test)
   - [ ] Home page loads and shows data
   - [ ] Preset switcher changes data
   - [ ] Navigation between pages
   - [ ] Event filtering and search
   - [ ] Evidence tier badges display
   - [ ] Export functionality
   - [ ] Dark mode toggle
   - [ ] Mobile responsive layout
   
   ## API Integration Tests
   - [ ] Index endpoint returns data
   - [ ] Events endpoint with filters
   - [ ] Signposts endpoint
   - [ ] Error handling (404, 500)
   - [ ] Rate limiting behavior
   
   ## User Workflows
   - [ ] New visitor sees latest events
   - [ ] Researcher filters by A-tier only
   - [ ] User exports data to Excel
   - [ ] Mobile user swipes through timeline
   ```

3. **Implement Missing Tests**:

   **Test: Event Filtering**
   ```typescript
   // apps/web/e2e/events.spec.ts
   import { test, expect } from '@playwright/test'
   
   test.describe('Events Page', () => {
     test.beforeEach(async ({ page }) => {
       await page.goto('/events')
     })
   
     test('filters by tier', async ({ page }) => {
       // Click "A-tier only" filter
       await page.click('[data-testid="filter-tier-a"]')
       
       // Verify all visible events are tier A
       const badges = page.locator('[data-testid="tier-badge"]')
       const count = await badges.count()
       
       for (let i = 0; i < count; i++) {
         const text = await badges.nth(i).textContent()
         expect(text).toContain('A')
       }
     })
   
     test('searches events', async ({ page }) => {
       // Type in search box
       await page.fill('[data-testid="search-input"]', 'GPT-4')
       
       // Wait for results
       await page.waitForTimeout(500)
       
       // Verify results contain search term
       const results = page.locator('[data-testid="event-card"]')
       const firstResult = await results.first().textContent()
       expect(firstResult?.toLowerCase()).toContain('gpt')
     })
   
     test('exports to Excel', async ({ page }) => {
       // Click export button
       const [download] = await Promise.all([
         page.waitForEvent('download'),
         page.click('[data-testid="export-excel"]'),
       ])
       
       // Verify file downloaded
       const filename = download.suggestedFilename()
       expect(filename).toContain('.xlsx')
     })
   })
   ```

   **Test: Dark Mode**
   ```typescript
   // apps/web/e2e/theme.spec.ts
   import { test, expect } from '@playwright/test'
   
   test.describe('Dark Mode', () => {
     test('toggles between light and dark', async ({ page }) => {
       await page.goto('/')
       
       // Get initial theme
       const html = page.locator('html')
       const initialClass = await html.getAttribute('class')
       
       // Click theme toggle
       await page.click('[data-testid="theme-toggle"]')
       await page.click('text=Dark')
       
       // Verify dark class added
       await expect(html).toHaveClass(/dark/)
       
       // Toggle back to light
       await page.click('[data-testid="theme-toggle"]')
       await page.click('text=Light')
       
       // Verify dark class removed
       const finalClass = await html.getAttribute('class')
       expect(finalClass).not.toContain('dark')
     })
   
     test('persists theme preference', async ({ page, context }) => {
       await page.goto('/')
       
       // Set dark mode
       await page.click('[data-testid="theme-toggle"]')
       await page.click('text=Dark')
       
       // Reload page
       await page.reload()
       
       // Verify still dark
       const html = page.locator('html')
       await expect(html).toHaveClass(/dark/)
     })
   })
   ```

   **Test: Mobile Responsive**
   ```typescript
   // apps/web/e2e/mobile.spec.ts
   import { test, expect, devices } from '@playwright/test'
   
   test.use({
     ...devices['iPhone 12'],
   })
   
   test.describe('Mobile Experience', () => {
     test('navigation works on mobile', async ({ page }) => {
       await page.goto('/')
       
       // Open mobile menu
       await page.click('[data-testid="mobile-menu-button"]')
       
       // Click Timeline
       await page.click('text=Timeline')
       
       // Verify navigated
       await expect(page).toHaveURL(/\/timeline/)
     })
   
     test('charts render on mobile', async ({ page }) => {
       await page.goto('/')
       
       // Verify composite gauge renders
       const gauge = page.locator('[data-testid="composite-gauge"]')
       await expect(gauge).toBeVisible()
       
       // Check it's not cut off
       const box = await gauge.boundingBox()
       expect(box?.width).toBeLessThanOrEqual(400)  // Mobile width
     })
   })
   ```

4. **Add API Integration Tests**:
   ```typescript
   // apps/web/e2e/api.spec.ts
   import { test, expect } from '@playwright/test'
   
   const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
   
   test.describe('API Integration', () => {
     test('index endpoint returns valid data', async ({ request }) => {
       const response = await request.get(`${API_URL}/v1/index`)
       
       expect(response.status()).toBe(200)
       
       const data = await response.json()
       expect(data).toHaveProperty('overall_proximity')
       expect(data).toHaveProperty('categories')
     })
   
     test('handles 404 gracefully', async ({ request }) => {
       const response = await request.get(`${API_URL}/v1/events/999999`)
       
       expect(response.status()).toBe(404)
     })
   
     test('rate limiting works', async ({ request }) => {
       // Make 100 rapid requests
       const requests = Array(100).fill(null).map(() =>
         request.get(`${API_URL}/v1/index`)
       )
       
       const responses = await Promise.all(requests)
       
       // Some should be rate limited
       const rateLimited = responses.filter(r => r.status() === 429)
       expect(rateLimited.length).toBeGreaterThan(0)
     })
   })
   ```

5. **Run Tests in CI**:
   ```yaml
   # Verify tests run in .github/workflows/ci.yml
   # (DevOps Agent should have set this up)
   
   # Locally test CI workflow
   cd apps/web
   npm run e2e
   ```

**Deliverable**: E2E coverage >80%, all critical paths tested, tests passing in CI.

---

### Task 2: Security Audit (6-8 hours)

**Your Actions**:

1. **Automated Security Scanning**:
   ```bash
   # Scan dependencies for vulnerabilities
   cd apps/web
   npm audit --audit-level=moderate
   npm audit fix
   
   cd ../../services/etl
   pip install safety
   safety check --full-report
   
   # If vulnerabilities found, update deps
   # Document in .cursor/agents/status/SECURITY_AUDIT.md
   ```

2. **OWASP Top 10 Checklist**:
   
   **Create `docs/SECURITY_AUDIT.md`**:
   ```markdown
   # Security Audit Report - YYYY-MM-DD
   
   ## OWASP Top 10 Checklist
   
   ### 1. Broken Access Control
   - [x] Admin endpoints require API key
   - [x] API key verified on each request
   - [ ] Rate limiting per API key (TODO)
   - [x] No exposed admin UI without auth
   
   ### 2. Cryptographic Failures
   - [x] API keys stored in env vars, not code
   - [x] Database passwords not in repo
   - [x] HTTPS enforced in production
   - [x] No sensitive data in logs
   
   ### 3. Injection
   - [x] SQLAlchemy ORM used (prevents SQL injection)
   - [x] Parameterized queries everywhere
   - [x] Input validation with Pydantic
   - [x] No eval() or exec() calls
   
   ### 4. Insecure Design
   - [x] Evidence tiering enforced at DB level
   - [x] LLM budget limits prevent runaway costs
   - [x] Deduplication prevents data pollution
   - [ ] Backup/restore procedure documented
   
   ### 5. Security Misconfiguration
   - [x] CORS origins restricted
   - [x] CSP headers configured
   - [ ] Security headers verified in production (TODO: test)
   - [x] Default credentials changed
   
   ### 6. Vulnerable Components
   - [ ] npm audit passing (X vulnerabilities found - fixing)
   - [ ] safety check passing (Y vulnerabilities found - fixing)
   - [x] Dependencies pinned in package.json
   - [ ] Auto-updates configured (Dependabot)
   
   ### 7. Identification & Authentication
   - [x] API key authentication working
   - [x] No weak passwords (API keys are UUIDs)
   - [x] No session fixation (stateless API)
   - [ ] API key rotation procedure documented (TODO)
   
   ### 8. Software & Data Integrity
   - [x] Git commits signed (optional)
   - [x] Migrations versioned with Alembic
   - [x] No unsigned packages
   - [x] CI/CD pipeline verifies builds
   
   ### 9. Security Logging & Monitoring
   - [x] Sentry capturing errors
   - [x] Structured logging configured
   - [ ] Log aggregation active (TODO: DevOps)
   - [ ] Alert policies configured (TODO: DevOps)
   
   ### 10. Server-Side Request Forgery (SSRF)
   - [x] User-provided URLs validated
   - [x] Fetch limited to known domains
   - [x] No arbitrary URL fetching from user input
   - [x] Playwright scraping sandboxed
   
   ## Critical Vulnerabilities
   - [ ] None found
   
   ## High Priority Fixes
   - [ ] Update dependency X to version Y (CVE-XXXX-XXXX)
   - [ ] Verify CSP headers in production
   - [ ] Document API key rotation
   
   ## Recommendations
   - Enable Dependabot for auto-updates
   - Set up security.txt file
   - Consider bug bounty program (post-launch)
   ```

3. **Manual Security Tests**:
   ```bash
   # Test SQL injection attempts
   curl "http://localhost:8000/v1/events?tier=A';DROP TABLE events;--"
   # Should return 422 validation error, not execute
   
   # Test XSS attempts
   curl -X POST "http://localhost:8000/v1/admin/events" \
     -H "Content-Type: application/json" \
     -d '{"title":"<script>alert(1)</script>"}'
   # Should sanitize or reject
   
   # Test CSRF (should fail without proper origin)
   curl -X POST "http://localhost:8000/v1/admin/events" \
     -H "Origin: https://evil.com" \
     -H "X-API-Key: valid-key"
   # Should reject due to CORS
   ```

4. **Verify Security Headers**:
   ```bash
   # Check production headers
   curl -I https://agi-tracker-api.up.railway.app
   
   # Should see:
   # X-Content-Type-Options: nosniff
   # X-Frame-Options: DENY
   # Content-Security-Policy: ...
   # Strict-Transport-Security: max-age=31536000
   ```

5. **Penetration Testing (Optional)**:
   ```bash
   # Use OWASP ZAP for automated pentesting
   docker run -v $(pwd):/zap/wrk/:rw -t owasp/zap2docker-stable zap-baseline.py \
     -t http://localhost:3000 -r zap-report.html
   
   # Review report for findings
   ```

**Deliverable**: Security audit complete, critical vulnerabilities fixed, report documented.

---

### Task 3: Load Testing (4-6 hours)

**Your Actions**:

1. **Set Up Locust**:
   ```bash
   pip install locust
   ```

2. **Create Load Test Script**:
   ```python
   # tests/load/locustfile.py
   from locust import HttpUser, task, between
   
   class AGITrackerUser(HttpUser):
       wait_time = between(1, 3)  # Wait 1-3s between requests
       
       @task(3)
       def get_index(self):
           """Most common request - get index"""
           self.client.get("/v1/index?preset=equal")
       
       @task(2)
       def get_events(self):
           """Get recent events"""
           self.client.get("/v1/events?limit=50")
       
       @task(2)
       def get_signposts(self):
           """Get signposts"""
           self.client.get("/v1/signposts")
       
       @task(1)
       def get_timeline(self):
           """Less common - timeline view"""
           self.client.get("/v1/events?since=2024-01-01")
       
       @task(1)
       def get_health(self):
           """Health check"""
           self.client.get("/health")
   ```

3. **Run Load Test**:
   ```bash
   # Start API locally
   cd services/etl
   uvicorn app.main:app --port 8000
   
   # Run load test
   cd ../../tests/load
   locust -f locustfile.py --host http://localhost:8000
   
   # Open browser to http://localhost:8089
   # Configure:
   # - Number of users: 100
   # - Spawn rate: 10 users/second
   # - Run for: 5 minutes
   
   # Monitor results
   ```

4. **Document Performance Baseline**:
   ```markdown
   # Load Test Results - YYYY-MM-DD
   
   ## Test Configuration
   - Target: http://localhost:8000
   - Users: 100 concurrent
   - Spawn Rate: 10/second
   - Duration: 5 minutes
   - Total Requests: ~15,000
   
   ## Results
   
   | Endpoint | Requests | Median (ms) | 95th % (ms) | Failures |
   |----------|----------|-------------|-------------|----------|
   | GET /v1/index | 4,500 | 120 | 250 | 0 |
   | GET /v1/events | 3,000 | 150 | 300 | 0 |
   | GET /v1/signposts | 3,000 | 100 | 200 | 0 |
   | GET /v1/events?since | 1,500 | 180 | 350 | 2 |
   | GET /health | 1,500 | 50 | 80 | 0 |
   
   ## Findings
   - ✅ No failures under 100 concurrent users
   - ✅ 95th percentile <400ms for all endpoints
   - ⚠️ 2 failures on /v1/events?since (investigate timeout)
   - ✅ Database connections stable (~8/10 used)
   - ✅ Memory usage stable (<600MB)
   
   ## Recommendations
   - Add index on events.created_at for date range queries
   - Consider caching /v1/index for 1 hour (currently uncached)
   - Monitor at 200 concurrent users in future test
   ```

**Deliverable**: Load test passing, performance baseline documented, bottlenecks identified.

---

## Week 4 Priority: Final Validation

### Task 4: Pre-Launch Testing Checklist (4-6 hours)

**Your Actions**:

1. **Create Pre-Launch Checklist**:
   ```markdown
   # Pre-Launch Testing Checklist
   
   ## Functionality
   - [ ] All pages load without errors
   - [ ] Navigation works (home → events → timeline → signposts)
   - [ ] Preset switcher updates data
   - [ ] Event filtering works (tier, date, source)
   - [ ] Search returns relevant results
   - [ ] Export to Excel/CSV/JSON works
   - [ ] Dark mode functional
   - [ ] PWA installable
   - [ ] Social sharing buttons work
   
   ## Performance
   - [ ] Lighthouse score >90
   - [ ] LCP <2.5s
   - [ ] FID <100ms
   - [ ] CLS <0.1
   - [ ] TTI <3.5s
   - [ ] Bundle size <800KB
   
   ## Mobile
   - [ ] Responsive on iPhone SE (375px)
   - [ ] Responsive on iPad (768px)
   - [ ] Touch targets ≥44x44px
   - [ ] No horizontal scroll
   - [ ] Charts readable on small screens
   
   ## API
   - [ ] All endpoints return 200 or expected error
   - [ ] Rate limiting works
   - [ ] CORS configured correctly
   - [ ] Error messages helpful
   - [ ] API docs accurate
   
   ## Security
   - [ ] HTTPS enforced
   - [ ] Security headers present
   - [ ] No console errors in production
   - [ ] API key required for admin endpoints
   - [ ] No exposed secrets
   
   ## Monitoring
   - [ ] Sentry receiving events
   - [ ] Healthchecks.io pinging
   - [ ] Railway metrics showing data
   - [ ] Alerts configured
   - [ ] Logs aggregating
   
   ## Data
   - [ ] Live data ingesting
   - [ ] No duplicate events
   - [ ] LLM budget limits working
   - [ ] Event analysis running
   - [ ] Snapshots computing daily
   ```

2. **Run Smoke Tests**:
   ```bash
   # Smoke test script
   #!/bin/bash
   # tests/smoke-test.sh
   
   API_URL="https://agi-tracker-api.up.railway.app"
   WEB_URL="https://agi-tracker.vercel.app"
   
   echo "🔍 Running smoke tests..."
   
   # Test API health
   echo "Testing API health..."
   curl -f $API_URL/health || exit 1
   
   # Test index endpoint
   echo "Testing index endpoint..."
   curl -f $API_URL/v1/index || exit 1
   
   # Test events endpoint
   echo "Testing events endpoint..."
   curl -f $API_URL/v1/events?limit=10 || exit 1
   
   # Test web homepage
   echo "Testing web homepage..."
   curl -f $WEB_URL || exit 1
   
   echo "✅ All smoke tests passed!"
   ```

3. **Manual Testing Session**:
   - Go through each page as a user would
   - Try to break things (edge cases)
   - Test on different browsers (Chrome, Firefox, Safari)
   - Test on real mobile device

**Deliverable**: Pre-launch checklist complete, all items passing.

---

## Your File Ownership

**Primary**:
- `apps/web/e2e/**/*.ts`
- `services/etl/tests/**/*.py`
- `tests/load/**/*`
- `docs/SECURITY_AUDIT.md`
- `tests/smoke-test.sh`

**Shared**:
- `.github/workflows/ci*.yml` (coordinate with DevOps)

---

## Daily Status Template

Write to `.cursor/agents/status/TESTING_status.md`:

```markdown
# Testing Agent Status - YYYY-MM-DD

## Accomplishments
- ✅ [Test suite] - [coverage %]

## In Progress
- [Test area] - [% complete]

## Blockers
- [ ] None
- [ ] [Blocker]

## Tomorrow
- [ ] [Next test area]

## Metrics
- E2E Coverage: [X%]
- Backend Tests: [X passing / Y total]
- Security Vulnerabilities: [N critical, M high]
- Load Test: [passing | failing]
```

---

**YOU ARE THE GUARDIAN. ENSURE QUALITY. PREVENT REGRESSIONS.**

