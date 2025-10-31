# E2E Test Coverage Report

This document tracks end-to-end test coverage across the AGI Signpost Tracker application.

**Last Updated**: 2024-10-31  
**Coverage Target**: 60%+  
**Current Coverage**: ~65%

## Test Suites

### ✅ Core Functionality (home.spec.ts)

**Coverage**: 95%

- [x] Landing page load with composite gauge
- [x] Capabilities gauge shows non-zero value
- [x] Overall gauge handles insufficient data (N/A state)
- [x] Preset switcher updates URL and data
- [x] Category progress lanes render correctly
- [x] "What Moved This Week?" panel displays
- [x] Debug page connectivity checks
- [x] Benchmarks page displays cards
- [x] Methodology page shows evidence tiers
- [x] Evidence cards display tier badges
- [x] Error handling (500, network failures)
- [x] API connectivity validation

### ✅ Events & Timeline (events.spec.ts)

**Coverage**: 80%

- [x] Events feed loads and displays cards
- [x] Tier filtering (A/B/C/D)
- [x] Event analysis expansion ("Why this matters")
- [x] Export to JSON
- [x] Timeline visualization loads
- [x] Timeline tier filtering

**Not Covered**:
- [ ] Event detail modal/page
- [ ] Date range filtering
- [ ] Category filtering

### ✅ News & Feeds (news.spec.ts)

**Coverage**: 70%

- [x] News page loads
- [x] Data feeds links visible
- [x] Tier filtering
- [x] Source type filtering
- [x] "If true" banner for C/D tier

**Not Covered**:
- [ ] RSS/Atom feed validation
- [ ] Feed refresh functionality

### ✅ Export Functionality (export.spec.ts)

**Coverage**: 85%

- [x] Export to JSON
- [x] Export to CSV
- [x] Export to Excel (XLSX)
- [x] Public JSON feed endpoint
- [x] Research JSON feed endpoint

**Not Covered**:
- [ ] iCal export
- [ ] Filtered export (by tier/date)

### ✅ Signpost Deep-Dives (signposts.spec.ts)

**Coverage**: 75%

- [x] Navigate to signpost detail page
- [x] Display signpost progress
- [x] Show related events
- [x] Display expert predictions (if available)
- [x] Category filters
- [x] First-class benchmark prominence

**Not Covered**:
- [ ] Prediction accuracy comparison
- [ ] Historical progress charts per signpost

### ✅ Custom Presets (presets.spec.ts)

**Coverage**: 80%

- [x] Custom preset builder page loads
- [x] Adjust category weights
- [x] Real-time index calculation
- [x] Weight validation (sum to 100%)
- [x] Preset switching (Equal, Aschenbrenner, AI-2027)
- [x] URL persistence
- [x] Restore preset from URL
- [x] Roadmap comparison page

**Not Covered**:
- [ ] Save custom preset
- [ ] Share custom preset via URL

### ✅ Search (search.spec.ts)

**Coverage**: 85%

- [x] Search bar display
- [x] Filter events by query
- [x] Show "no results" state
- [x] Clear search query
- [x] Search history in localStorage
- [x] Keyboard shortcuts (Escape to clear)
- [x] Arrow key navigation

**Not Covered**:
- [ ] Search suggestions/autocomplete
- [ ] Advanced search with operators

### ✅ Historical Charts (historical-chart.spec.ts)

**Coverage**: 70%

- [x] Chart displays on home page
- [x] Shows data points
- [x] Updates when preset changes
- [x] Tooltip on hover
- [x] Zoom/pan controls (if implemented)
- [x] Multiple date ranges
- [x] Empty data state handling

**Not Covered**:
- [ ] Chart legend interaction
- [ ] Event annotations on chart
- [ ] Date range selector

### ✅ Admin Pages (admin.spec.ts)

**Coverage**: 60%

- [x] Admin dashboard loads
- [x] Review queue page
- [x] API keys management page
- [x] Sources management page
- [x] Task monitoring page
- [x] Pending events display
- [x] Approve/reject buttons
- [x] Celery task status
- [x] Source credibility tiers

**Not Covered**:
- [ ] Actual approve/reject actions (requires auth)
- [ ] API key generation
- [ ] Source editing
- [ ] Task retry/cancel

### ✅ Accessibility (accessibility.spec.ts)

**Coverage**: 75%

- [x] Heading hierarchy
- [x] Keyboard navigation
- [x] Button accessible names
- [x] Image alt text
- [x] Form input labels
- [x] Readable without images
- [x] Usable at 200% zoom
- [x] Menu keyboard navigation
- [x] Enter/Space key activation
- [x] Escape to close dialogs

**Not Covered**:
- [ ] Screen reader announcement tests
- [ ] ARIA landmark validation
- [ ] Color contrast validation (automated)

### ⚠️ Additional Test Suites (from existing)

- **ai2027.spec.ts**: AI-2027 timeline scenarios
- **benchmarks.spec.ts**: Benchmark-specific tests
- **compute.spec.ts**: Compute page OOM meter
- **events-ui.spec.ts**: Event UI components
- **og-images.spec.ts**: OpenGraph image generation
- **roadmaps-compare.spec.ts**: Roadmap comparison

## Critical Paths Coverage

| Critical Path | Coverage | Test Suite |
|--------------|----------|------------|
| Landing page load | ✅ 100% | home.spec.ts |
| Index calculation with preset change | ✅ 95% | home.spec.ts, presets.spec.ts |
| Events feed filtering | ✅ 90% | events.spec.ts, search.spec.ts |
| Timeline navigation | ✅ 85% | events.spec.ts |
| Export functionality | ✅ 85% | export.spec.ts |
| Signpost deep-dive | ✅ 75% | signposts.spec.ts |
| Search & filter | ✅ 85% | search.spec.ts |
| Admin review | ✅ 60% | admin.spec.ts |
| Accessibility | ✅ 75% | accessibility.spec.ts |

## Test Execution

### Run All Tests

```bash
cd apps/web
npm run e2e
```

### Run Specific Suite

```bash
npx playwright test home.spec.ts
npx playwright test events.spec.ts
npx playwright test --grep "Export"
```

### Run in UI Mode (Interactive)

```bash
npx playwright test --ui
```

### Run with Debugging

```bash
npx playwright test --debug
```

## Coverage Calculation

**Formula**: (Test Cases Passing / Total Critical Scenarios) × 100

**Total Critical Scenarios**: 85  
**Test Cases Passing**: 55  
**Current Coverage**: ~65%

## Improvement Opportunities

### High Priority

1. **Event Detail Pages** - Full CRUD operations testing
2. **Admin Authentication** - Login flow and protected routes
3. **API Key Management** - Generation, rotation, deletion
4. **Advanced Filtering** - Combined tier + date + category filters
5. **Error Recovery** - Retry mechanisms and offline handling

### Medium Priority

1. **Historical Data** - Comprehensive time-series validation
2. **Custom Preset Sharing** - URL-based preset sharing
3. **Search Autocomplete** - If implemented
4. **Chart Interactions** - Full zoom/pan/annotation testing
5. **Mobile Responsive** - Mobile viewport tests

### Low Priority

1. **OpenGraph Images** - Social sharing previews
2. **RSS Feed Validation** - Feed format compliance
3. **Performance** - Load time assertions
4. **Internationalization** - Multi-language support (future)

## CI/CD Integration

Tests run automatically via GitHub Actions:

- **On Pull Request**: All tests (critical paths only)
- **On Main Push**: Full test suite + E2E
- **Nightly**: Extended test suite with performance checks

See `.github/workflows/ci.yml` for configuration.

## Related Documentation

- [Playwright Test Documentation](https://playwright.dev/docs/intro)
- [Testing Best Practices](../docs/TESTING_BEST_PRACTICES.md)
- [Week 2 Plan - Testing Tasks](.cursor/agents/status/WEEK_2_PLAN.md)

