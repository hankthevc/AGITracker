#!/usr/bin/env bash
# Quick health check and triage script
# Runs against production to assess current state

set -euo pipefail

RED='\033[0;31m'; GRN='\033[0;32m'; YLW='\033[0;33m'; NC='\033[0m'
pass(){ echo -e "${GRN}✓${NC} $*"; }
fail(){ echo -e "${RED}✗${NC} $*"; }
warn(){ echo -e "${YLW}⚠${NC} $*"; }

API_URL="${API_URL:-https://agitracker-production-6efa.up.railway.app}"
WEB_URL="${WEB_URL:-https://agi-tracker.vercel.app}"

echo "╔════════════════════════════════════════╗"
echo "║  AGI Tracker Health Check & Triage    ║"
echo "╚════════════════════════════════════════╝"
echo ""

# 1. Production API Health
echo "1️⃣  API Health Check"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if HEALTH=$(curl -sSf "$API_URL/healthz" 2>&1); then
  pass "API is responding"
  echo "$HEALTH" | jq '.' 2>/dev/null || echo "$HEALTH"
else
  fail "API is DOWN or unreachable"
  echo "Error: $HEALTH"
fi
echo ""

# 2. Database Migration Status
echo "2️⃣  Database Migration Status"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if railway run alembic current 2>/dev/null; then
  pass "Migration status retrieved"
else
  warn "Could not check migration (Railway CLI may not be configured)"
fi
echo ""

# 3. Signpost Count
echo "3️⃣  Signpost Data"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if COUNT=$(curl -sSf "$API_URL/v1/signposts" 2>&1 | jq 'length' 2>/dev/null); then
  if [ "$COUNT" -eq 99 ]; then
    pass "Signposts: $COUNT (expected 99)"
  else
    warn "Signposts: $COUNT (expected 99)"
  fi
else
  fail "Could not fetch signposts"
fi
echo ""

# 4. New Category Support
echo "4️⃣  New Categories (Economic, Research, etc.)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
for cat in economic research geopolitical safety_incidents; do
  if curl -sSf "$API_URL/v1/signposts?category=$cat" >/dev/null 2>&1; then
    pass "Category '$cat' works"
  else
    fail "Category '$cat' returns error"
  fi
done
echo ""

# 5. Dashboard Endpoints
echo "5️⃣  FiveThirtyEight Dashboard Endpoints"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if curl -sSf "$API_URL/v1/dashboard/summary" >/dev/null 2>&1; then
  pass "GET /v1/dashboard/summary works"
else
  fail "Dashboard summary endpoint not responding"
fi

if curl -sSf "$API_URL/v1/dashboard/timeseries?metric=events_per_day&window=30d" >/dev/null 2>&1; then
  pass "GET /v1/dashboard/timeseries works"
else
  fail "Timeseries endpoint not responding"
fi
echo ""

# 6. Frontend Pages
echo "6️⃣  Frontend Deployment"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
for page in "" "explore" "dashboard" "charts"; do
  URL="$WEB_URL/$page"
  if HTTP_CODE=$(curl -sSf -o /dev/null -w "%{http_code}" "$URL" 2>&1); then
    if [ "$HTTP_CODE" -eq 200 ]; then
      pass "/$page → HTTP 200"
    else
      warn "/$page → HTTP $HTTP_CODE"
    fi
  else
    fail "/$page is not accessible"
  fi
done
echo ""

# 7. Recent Errors (check if API returns errors)
echo "7️⃣  Recent API Errors"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
# Try a few endpoints that might have issues
ERROR_COUNT=0
for endpoint in "/v1/index" "/v1/events" "/v1/changelog"; do
  if ! curl -sSf "$API_URL$endpoint" >/dev/null 2>&1; then
    warn "$endpoint returned error"
    ERROR_COUNT=$((ERROR_COUNT + 1))
  fi
done

if [ $ERROR_COUNT -eq 0 ]; then
  pass "No errors on common endpoints"
else
  warn "Found $ERROR_COUNT endpoint(s) with errors"
fi
echo ""

# 8. Git Status
echo "8️⃣  Local Repository Status"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Current branch: $(git branch --show-current)"
echo "Latest commit: $(git log -1 --oneline)"
echo "Commits ahead of origin: $(git rev-list @{u}..HEAD 2>/dev/null | wc -l || echo 'N/A')"
echo ""

echo "╔════════════════════════════════════════╗"
echo "║  Health Check Complete                 ║"
echo "╚════════════════════════════════════════╝"
echo ""
echo "Next steps:"
echo "1. Check Railway logs: railway logs --service agi-tracker-api"
echo "2. Check Sentry: https://sentry.io (if configured)"
echo "3. Check GitHub Actions: https://github.com/hankthevc/AGITracker/actions"
echo "4. Review EMAIL_TRIAGE.md for common alert patterns"

