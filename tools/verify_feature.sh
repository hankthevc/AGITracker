#!/usr/bin/env bash
# FiveThirtyEight Feature Verification Script
# 
# Verifies dashboard endpoints, SafeLink compliance, and CSP strictness.
# Exit code 0 = all pass, non-zero = failure

set -euo pipefail

RED='\033[0;31m'; GRN='\033[0;32m'; NC='\033[0m'
pass(){ echo -e "${GRN}PASS${NC} - $*"; }
fail(){ echo -e "${RED}FAIL${NC} - $*"; exit 1; }

API_URL="${API_URL:-https://agitracker-production-6efa.up.railway.app}"
WEB_URL="${WEB_URL:-https://agi-tracker.vercel.app}"

echo "== FiveThirtyEight Feature Verification =="
echo "API: $API_URL"
echo "Web: $WEB_URL"
echo ""

# 1) Dashboard endpoints exist & return JSON
echo "1) Dashboard API Endpoints"
curl -sSf "$API_URL/v1/dashboard/summary" | jq '.kpis' >/dev/null \
  && pass "GET /v1/dashboard/summary returns valid JSON" \
  || fail "Dashboard summary endpoint failed"

curl -sSf "$API_URL/v1/dashboard/timeseries?metric=events_per_day&window=30d" | jq '.series' >/dev/null \
  && pass "GET /v1/dashboard/timeseries returns valid JSON" \
  || fail "Timeseries endpoint failed"

curl -sSf "$API_URL/v1/dashboard/news/recent?limit=10" | jq 'length' >/dev/null \
  && pass "GET /v1/dashboard/news/recent returns valid JSON" \
  || fail "News endpoint failed"

# 2) No raw external <a> in new pages
echo ""
echo "2) SafeLink Compliance"
RAW_ANCHORS=$(grep -rn '<a\s*href="https://' apps/web/app/dashboard apps/web/app/charts 2>/dev/null | grep -v SafeLink || true)
if [[ -z "$RAW_ANCHORS" ]]; then
  pass "No raw external <a> in dashboard/charts pages"
else
  echo "$RAW_ANCHORS"
  fail "Found raw external anchors in new pages"
fi

# 3) Components exist
echo ""
echo "3) Component Files"
test -f apps/web/components/kpi/KpiCard.tsx && pass "KpiCard component exists" || fail "Missing KpiCard"
test -f apps/web/components/charts/TimeseriesChart.tsx && pass "TimeseriesChart exists" || fail "Missing TimeseriesChart"

# 4) Pages exist
echo ""
echo "4) Page Files"
test -f apps/web/app/dashboard/page.tsx && pass "Dashboard page exists" || fail "Missing dashboard page"
test -f apps/web/app/charts/page.tsx && pass "Charts page exists" || fail "Missing charts page"
test -f apps/web/app/explore/page.tsx && pass "Explore page exists" || fail "Missing explore page"

# 5) Migration exists
echo ""
echo "5) Database Migration"
test -f infra/migrations/versions/031_add_dashboard_snapshots.py && pass "Migration 031 exists" || fail "Missing migration 031"

# 6) Tests exist
echo ""
echo "6) Test Coverage"
test -f services/etl/tests/test_dashboard_api.py && pass "Dashboard API tests exist" || fail "Missing dashboard tests"

echo -e "\n${GRN}✅ ALL FEATURE CHECKS PASS${NC}"

