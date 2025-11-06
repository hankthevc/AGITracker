# Security Hardening Status Report

**Date**: November 6, 2024  
**Commit**: Current HEAD  
**Status**: ⚠️ **IN PROGRESS** - Migration fixes complete, security enforcement in progress

---

## ✅ COMPLETED (Production-Safe)

### 1. Migration Integrity ✅ 
- Restored deleted migration 023
- Created merge migration 028
- Created forward-only migrations 029, 030
- Single migration head: `030_openai_prep_conf`
- **Result**: Migration policy violations resolved

### 2. Repository Organization ✅
- Moved ephemeral docs to `docs/archived/`
- No temp scripts in repo
- Clean git status

### 3. Concurrent Index Safety ✅
- Migration 026 uses `CREATE INDEX CONCURRENTLY` in autocommit blocks
- Proper downgrade with `DROP INDEX CONCURRENTLY`
- 23 occurrences verified

### 4. Seed Loader Validation ✅
- Type validation (dates, numerics, confidence ranges)
- Direction validation ({'>=', '<='})
- Category validation (8 allowed categories)
- Single transaction with rollback
- Duplicate detection in YAML

---

## 🚧 IN PROGRESS (Blocking for Production)

### A) SafeLink Enforcement ⚠️
**Status**: Partially complete  
**Blocking**: Yes

**Found Issues**:
- 10 raw external `<a>` tags in:
  - `apps/web/app/layout.tsx` (2 instances) - ✅ FIXED
  - `apps/web/app/legal/privacy/page.tsx` (4 instances) - ⏳ IN PROGRESS
  - `apps/web/app/legal/terms/page.tsx` (4 instances) - ⏳ IN PROGRESS

**Required Actions**:
1. ✅ Replace `<a href="https://...">` with `<SafeLink href="https://...">`
2. ❌ Add ESLint rule to prevent regressions
3. ❌ Add `apps/web/lib/__tests__/safelink.test.tsx`
4. ❌ Add CI step for SafeLink tests

**ESLint Rule** (to add to `apps/web/.eslintrc.js`):
```javascript
rules: {
  'no-restricted-syntax': [
    'error',
    {
      selector: 'JSXOpeningElement[name.name="a"][attributes.0.name.name="href"][attributes.0.value.type=/Literal|JSXExpressionContainer/]',
      message: 'Use SafeLink component for external URLs instead of raw <a> tags. Import from @/lib/SafeLink'
    }
  ]
}
```

### B) CSP Production Strictness ❌
**Status**: Not started  
**Blocking**: Yes

**Current State**:
- CSP includes `'unsafe-inline'` and `'unsafe-eval'` unconditionally
- No environment-based gating

**Required Changes** (in `apps/web/next.config.js`):
```javascript
const isDev = process.env.NODE_ENV !== 'production'

const securityHeaders = [
  {
    key: 'Content-Security-Policy',
    value: `
      default-src 'self';
      script-src 'self' ${isDev ? "'unsafe-eval' 'unsafe-inline'" : ''} https://vercel.live;
      style-src 'self' 'unsafe-inline' https://fonts.googleapis.com;
      // ... rest of CSP
    `.replace(/\s{2,}/g, ' ').trim()
  },
  // ... other headers
]
```

**Required Actions**:
1. ❌ Add `isDev` check
2. ❌ Remove unsafe-inline/eval in production
3. ❌ Add Playwright/Node smoke test for CSP headers

### C) Seed Loader: ON CONFLICT Upsert ⚠️
**Status**: Validation complete, needs upsert upgrade  
**Blocking**: No (nice-to-have)

**Current State**:
- Uses ORM query-then-update pattern
- Has validation but not using PostgreSQL `ON CONFLICT`

**Required Changes**:
```python
from sqlalchemy.dialects.postgresql import insert

for sp_data in all_signposts:
    stmt = insert(Signpost).values(**sp_data)
    stmt = stmt.on_conflict_do_update(
        index_elements=[Signpost.code],
        set_={k: v for k, v in sp_data.items() if k != 'code'}
    )
    db.execute(stmt)
```

**Required Actions**:
1. ❌ Convert to `ON CONFLICT` upsert
2. ❌ Create `services/etl/app/validation/validate_signposts.py`
3. ❌ Add `services/etl/tests/test_seeds_validation.py`
4. ❌ Add CI gate for validation

### D) Audit Logging Test ⚠️
**Status**: Wired but not tested  
**Blocking**: No (verification only)

**Current State**:
- 8 `log_admin_action()` calls for 4 admin routes (success + failure)
- Import verified: `from app.utils.audit import log_admin_action`

**Required Actions**:
1. ❌ Add `services/etl/tests/test_audit_logging.py`
2. ❌ Test success and failure paths
3. ❌ Ensure test is blocking in CI

---

## 📊 Deployment Readiness Matrix

| Component | Migration | Security | Tests | Status |
|-----------|-----------|----------|-------|--------|
| Database Schema | ✅ Pass | N/A | N/A | READY |
| Migration Chain | ✅ Pass | N/A | N/A | READY |
| Seed Loader | ✅ Pass | ⚠️ Partial | ❌ Missing | NOT READY |
| Frontend SafeLink | ⚠️ Partial | ❌ Fail | ❌ Missing | NOT READY |
| CSP Headers | N/A | ❌ Fail | ❌ Missing | NOT READY |
| Admin Auth | ✅ Pass | ✅ Pass | ⚠️ Partial | READY |
| Audit Logging | ✅ Pass | ✅ Pass | ❌ Missing | READY |

---

## 🚨 Blocking Issues for Production

### Critical (Must Fix Before Deploy)
1. **SafeLink Enforcement** - 8 remaining raw `<a>` tags, no ESLint guard
2. **CSP Production Mode** - Allows unsafe-inline/eval in production

### High Priority (Should Fix)
3. **SafeLink Tests** - No test coverage for XSS prevention
4. **CSP Smoke Test** - No verification of production CSP headers

### Medium Priority (Nice to Have)
5. **Seed Loader ON CONFLICT** - More efficient upsert pattern
6. **Separate Validator** - Standalone validation script + CI gate
7. **Audit Test** - Verify audit logging actually works

---

## 🎯 Next Steps (Priority Order)

### Immediate (Today)
1. ✅ Finish replacing raw `<a>` tags in legal pages
2. ✅ Add ESLint SafeLink rule
3. ✅ Update CSP for production strictness

### Short-term (This Week)
4. Add SafeLink test suite
5. Add CSP verification test
6. Add audit logging test

### Medium-term (Next Sprint)
7. Convert seed loader to ON CONFLICT
8. Create separate validator script
9. Add seed validation to CI

---

## 📝 Files Modified

### Completed
- `infra/migrations/versions/023_add_unique_dedup_hash.py` (restored)
- `infra/migrations/versions/024_add_composite_indexes.py` (reverted edits)
- `infra/migrations/versions/027_add_signpost_rich_metadata.py` (cleaned)
- `infra/migrations/versions/028_merge_heads.py` (created)
- `infra/migrations/versions/029_update_category_constraint.py` (created)
- `infra/migrations/versions/030_add_openai_prep_confidence.py` (created)
- `scripts/seed_comprehensive_signposts.py` (hardened validation)
- `docs/ops/STATE_REPORT.md` (created)
- `GPT5_AUDIT_RESPONSE.md` (created)
- `MIGRATION_POLICY_FIX.md` (created)

### In Progress
- `apps/web/app/layout.tsx` (2/2 fixed)
- `apps/web/app/legal/privacy/page.tsx` (0/4 fixed)
- `apps/web/app/legal/terms/page.tsx` (0/4 fixed)

### To Create
- `apps/web/.eslintrc.js` (add SafeLink rule)
- `apps/web/lib/__tests__/safelink.test.tsx`
- `services/etl/app/validation/validate_signposts.py`
- `services/etl/tests/test_seeds_validation.py`
- `services/etl/tests/test_audit_logging.py`

---

## ✅ Success Criteria

### Before Production Deploy
- [ ] Zero raw external `<a>` tags (verified with grep/rg)
- [ ] ESLint rule prevents future regressions
- [ ] CSP in production has no unsafe-inline/unsafe-eval
- [ ] SafeLink tests pass (javascript:/data: rejected)

### Nice to Have
- [ ] Seed validator exits non-zero on bad data
- [ ] Seed validator is blocking in CI
- [ ] Audit logging test verifies actual DB writes
- [ ] CSP smoke test verifies production headers

---

**Status**: Migration fixes complete ✅. Security hardening in progress ⚠️.  
**Blockers**: SafeLink enforcement (8 files), CSP production mode  
**ETA**: 2-4 hours for full completion

**Recommendation**: Do NOT deploy to production until SafeLink and CSP issues are resolved. These are XSS attack vectors.

