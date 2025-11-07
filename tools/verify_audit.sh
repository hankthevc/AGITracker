#!/usr/bin/env bash
set -euo pipefail

RED='\033[0;31m'; GRN='\033[0;32m'; YLW='\033[0;33m'; NC='\033[0m'
pass(){ echo -e "${GRN}PASS${NC} - $*"; }
fail(){ echo -e "${RED}FAIL${NC} - $*"; exit 1; }
warn(){ echo -e "${YLW}WARN${NC} - $*"; }

echo "== AGI Tracker Audit Mirror Verification =="

# 1) Migration integrity: single head == 030_openai_prep_conf
pushd infra/migrations >/dev/null
source ../../services/etl/.venv/bin/activate 2>/dev/null || true
HEADS=$(alembic heads | sed 's/ (head).*//')
echo "Heads: $HEADS"
[[ $(echo "$HEADS" | wc -l) -eq 1 ]] || fail "Multiple alembic heads: $HEADS"
echo "$HEADS" | grep -qE "(030_openai_prep_conf|031_dashboard_snaps)" && pass "Single head at expected revision (030 or 031)" || fail "Head is not at expected revision"
popd >/dev/null

# 2) SafeLink enforcement: zero raw external <a>
RAW_ANCHORS=$(grep -rn '<a\s*href="https://' apps/web/app --include="*.tsx" 2>/dev/null | grep -v SafeLink || true)
if [[ -z "$RAW_ANCHORS" ]]; then
  pass "No raw external <a> anchors under apps/web/app"
else
  echo "$RAW_ANCHORS"
  fail "Found raw external <a> anchors above"
fi

# 3) CSP prod strict: no unsafe-inline/eval in production branch
NCFG="apps/web/next.config.js"
grep -n "isDev" "$NCFG" >/dev/null || fail "No isDev gate in $NCFG"
if grep -n "script-src.*unsafe-\(inline\|eval\)" "$NCFG" >/dev/null; then
  grep -n "isDev.*process\.env\.NODE_ENV.*production" "$NCFG" >/dev/null \
    && pass "CSP gated by isDev; unsafe only in dev" \
    || fail "unsafe-inline/eval present without production guard in $NCFG"
else
  pass "No unsafe-inline/eval in CSP (production strict)"
fi

# 4) Seed validation: ON CONFLICT + validator script
SEED="scripts/seed_comprehensive_signposts.py"
grep -n "on_conflict_do_update" "$SEED" >/dev/null && pass "Seed loader uses ON CONFLICT upsert" || fail "Seed loader missing ON CONFLICT upsert"
test -f services/etl/app/validation/validate_signposts.py && pass "Standalone validator present" || fail "Missing services/etl/app/validation/validate_signposts.py"
test -f services/etl/tests/test_seeds_validation.py && pass "Seed validation test present" || fail "Missing test_seeds_validation.py"
# Optional: run validator (won't modify DB)
python3 services/etl/app/validation/validate_signposts.py >/dev/null 2>&1 && pass "Seed validator passed" || fail "Seed validator failed"

# 5) No deleted migrations: both 023 files present
ls infra/migrations/versions | grep '^023_.*\.py$' >/dev/null || fail "Missing one or both 023_* migration files"
COUNT_023=$(ls infra/migrations/versions | grep '^023_.*\.py$' | wc -l | tr -d ' ')
[[ "$COUNT_023" -ge 2 ]] && pass "Both 023 migrations present ($COUNT_023 files)" || fail "Only $COUNT_023 of 2 expected 023 migrations"

# 6) Concurrent indexes: CONCURRENTLY + autocommit
M026="infra/migrations/versions/026_concurrent_index_rebuild.py"
grep -n "CREATE INDEX CONCURRENTLY\|DROP INDEX CONCURRENTLY" "$M026" >/dev/null || fail "026 missing CONCURRENTLY"
grep -n "autocommit_block(" "$M026" >/dev/null && pass "026 uses autocommit_block with CONCURRENTLY" || fail "026 missing autocommit_block"

# 7) Audit logging: all admin routes call log_admin_action
ADMIN="services/etl/app/routers/admin.py"
CALLS=$(grep -n "log_admin_action(" "$ADMIN" | wc -l | tr -d ' ')
ROUTES=$(grep -E '@router\.(post|put|delete)\(' "$ADMIN" | wc -l | tr -d ' ')
echo "Admin routes: $ROUTES, audit calls: $CALLS"
[[ "$CALLS" -ge "$ROUTES" ]] && pass "All admin mutations appear to call log_admin_action (calls >= routes)" \
  || fail "Not all admin mutations call log_admin_action"

# 8) Test coverage: safelink, seeds, audit tests exist
test -f apps/web/lib/__tests__/safelink.test.tsx && pass "SafeLink test exists" || fail "Missing safelink.test.tsx"
test -f services/etl/tests/test_seeds_validation.py && pass "Seed validation test exists" || fail "Missing test_seeds_validation.py"
test -f services/etl/tests/test_audit_logging.py && pass "Audit logging test exists" || fail "Missing test_audit_logging.py"

echo -e "\n${GRN}✅ ALL CHECKS PASS${NC}"

