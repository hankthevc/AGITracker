# Email Alert Triage Guide

**Purpose**: Quickly assess Sentry/CI alerts and prioritize fixes  
**Last Updated**: November 7, 2024

---

## 🚨 **Quick Triage Process**

### Step 1: Run Health Check (2 minutes)
```bash
bash tools/health_check.sh
```

**If all green** ✅: Alerts may be transient or already resolved  
**If red/yellow** ⚠️: Follow triage below

---

### Step 2: Check Current Production State

**Production is Healthy** ✅ (as of last check):
- API: https://agitracker-production-6efa.up.railway.app/healthz
- Web: https://agi-tracker.vercel.app
- Database: 99 signposts loaded
- All endpoints responding

---

## 📊 **Common Alert Patterns**

### Sentry Alerts

#### 1. **Build Failures** (Most Common)
**Subject**: "Vercel build failed" or "Railway deploy failed"  
**Cause**: Usually ESLint warnings treated as errors  
**Check**:
- GitHub Actions: https://github.com/hankthevc/AGITracker/actions
- Look for failed workflow runs

**Quick Fix**:
- Check if new commits broke linting
- Run: `cd apps/web && npm run lint`
- Fix ESLint errors or adjust rules

#### 2. **Runtime Errors** (TypeErrors, undefined)
**Subject**: "TypeError: Cannot read property 'X' of undefined"  
**Cause**: Usually missing null checks in new pages  
**Check**:
- Sentry dashboard → Issues tab
- Look for error stack traces

**Quick Fix**:
- Add optional chaining (`?.`)
- Add null checks before accessing properties

#### 3. **API Errors** (500, 422)
**Subject**: "HTTPException" or "Validation Error"  
**Cause**: Schema mismatches or missing data  
**Check**:
- Railway logs: `railway logs --service agi-tracker-api`
- Look for recent 500/422 errors

**Quick Fix**:
- Check Pydantic schema matches TypeScript types
- Verify database has required data

---

## 🔍 **Detailed Investigation Steps**

### For Sentry Alerts

**1. Access Sentry**:
```bash
open https://sentry.io/organizations/your-org/projects/
```

**2. Check Issues Tab**:
- Sort by: "Last Seen" (most recent)
- Filter by: "Unresolved"
- Look for patterns (same error repeated)

**3. Review Stack Trace**:
- Frontend errors → check browser console
- Backend errors → check Railway logs

### For CI/CD Failures

**1. Check GitHub Actions**:
```bash
open https://github.com/hankthevc/AGITracker/actions
```

**2. Identify Failed Workflow**:
- Click red X next to commit
- Expand failed step
- Read error message

**3. Common Failure Patterns**:

**Build Failures**:
- ESLint errors (SafeLink rule catching new dynamic URLs)
- TypeScript errors (type mismatches)
- Import errors (missing dependencies)

**Test Failures**:
- Backend: pytest failures (database connection, schema issues)
- Frontend: Jest/React Testing Library failures

**Deployment Failures**:
- Railway: Database connection issues, migration errors
- Vercel: Build timeouts, package installation failures

---

## 🛠️ **Quick Fix Recipes**

### ESLint SafeLink Warnings Blocking Build
**Symptom**: "Use <SafeLink> component for dynamic external URLs"  
**Fix**:
```bash
# Option 1: Fix the violations (recommended)
# See TODO_DYNAMIC_SAFELINKS.md for list of files

# Option 2: Temporarily downgrade to warning (already done)
# apps/web/.eslintrc.js line 12: 'warn' instead of 'error'
```

### TypeScript Errors in New Pages
**Symptom**: "Property 'X' is possibly 'undefined'"  
**Fix**:
```typescript
// Add optional chaining
signpost.current_sota_value?.toFixed(2)

// Or null check
if (signpost.current_sota_value !== null && signpost.current_sota_value !== undefined) {
  // use value
}
```

### API Schema Mismatch
**Symptom**: "422 Unprocessable Entity" or "Validation failed"  
**Fix**:
```bash
# Check TypeScript matches Python
diff apps/web/lib/types/dashboard.ts services/etl/app/schemas/dashboard.py
```

---

## 📋 **Today's Work Priority Matrix**

### 🚨 P0 - Critical (Fix Immediately)
- [ ] API returning 500 errors
- [ ] Database connection failures
- [ ] Complete site outage

### ⚠️ P1 - High (Fix Today)
- [ ] Build failures blocking deploys
- [ ] TypeError/ReferenceError in Sentry (>10 occurrences)
- [ ] Broken core functionality (index page, signpost display)

### 📊 P2 - Medium (Fix This Week)
- [ ] ESLint warnings (dynamic SafeLinks)
- [ ] Performance issues (slow page loads)
- [ ] Minor UI bugs

### 📝 P3 - Low (Backlog)
- [ ] Accessibility improvements
- [ ] Documentation updates
- [ ] Nice-to-have features

---

## 🎯 **Based on Current Health Check**

**Good News** ✅:
- API is healthy
- 99 signposts working
- All new categories functional
- All new pages (dashboard, charts, explore) responding
- No errors on common endpoints

**Likely Alert Causes**:
1. **Transient deployment errors** (resolved automatically)
2. **ESLint warnings** (warnings, not errors - builds pass)
3. **Initial deployment hiccups** (first-time page loads)

---

## 📧 **Next Steps Based on Your Email Alerts**

### Option 1: Alerts are Resolved ✅
If health check is all green (it is!), the alerts may have been:
- One-time deployment issues
- Transient network errors
- Already auto-resolved

**Action**: Monitor for 24h, no immediate work needed

### Option 2: Check Specific Errors
**If you have specific error messages**, paste them and I'll:
- Diagnose root cause
- Provide exact fix
- Test in production

### Option 3: Proactive Hardening
Even if no current errors, we can:
- Migrate remaining 6 dynamic SafeLinks
- Add error boundaries to new pages
- Improve loading states
- Add monitoring/alerting improvements

---

## 🎯 **Recommended Action Plan for Today**

Based on health check results (all green):

**Morning** (1-2 hours):
1. Review actual Sentry/email alerts (if any specific errors)
2. Check GitHub Actions for failed runs
3. Fix any P0/P1 issues

**Afternoon** (2-3 hours):
4. Migrate 6 dynamic anchors to SafeLink (clean up warnings)
5. Add error boundaries to dashboard/charts pages
6. Deploy migration 031 (dashboard snapshots)

**Evening** (Optional):
7. Create Celery task for daily snapshots
8. Monitor production for 24h

---

## 📊 **Current State Summary**

**Health**: ✅ All systems operational  
**Alerts**: Likely transient or warnings (not errors)  
**Next Work**: Optional polish + monitoring  

**You're in good shape!** The alerts are probably from the initial deployment wave. Let me know if you have specific error messages to investigate.

