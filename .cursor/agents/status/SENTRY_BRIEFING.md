# 🔍 Sentry Monitoring - Complete Briefing

**Date**: October 31, 2025  
**For**: Henry Appel  
**From**: Supervisor Agent  
**Purpose**: Understand Sentry monitoring and how to use it for system health

---

## 📚 What is Sentry?

### Overview
**Sentry** is an **error tracking and performance monitoring platform** that automatically captures, aggregates, and alerts you about errors and performance issues in your applications.

**Think of it as**: A smart security camera for your code that:
- 📹 Records every error that happens
- 🔍 Shows you the exact code line that failed
- 📊 Groups similar errors together
- 🚨 Alerts you when things break
- 📈 Tracks performance over time

### How It Works

1. **Initialization**: Sentry SDK installed in your app (frontend + backend)
2. **Automatic Capture**: SDK intercepts errors, exceptions, and slow operations
3. **Smart Grouping**: Similar errors grouped into "Issues"
4. **Context Enrichment**: Adds user info, request data, stack traces, breadcrumbs
5. **Alerting**: Notifies you via email/Slack when issues occur
6. **Analysis**: Dashboard shows trends, frequency, affected users

---

## 🎯 What Sentry is Monitoring in Your AGI Tracker

### Frontend (Next.js/Vercel)
**Configured**: ✅ Yes (Testing Agent set this up)

**Config Files**:
- `sentry.server.config.js` - Server-side rendering errors
- `sentry.edge.config.js` - Edge middleware errors
- `instrumentation.js` - Next.js instrumentation
- `next.config.js` - Sentry webpack plugin

**DSN**: `https://4da7aeb6938e51d9ca13ad25ba3f4dda@o4510274025422848.ingest.us.sentry.io/4510274033811456`

**What It Tracks**:
- ✅ Frontend JavaScript errors (React crashes, uncaught exceptions)
- ✅ API route errors (Next.js /api/* endpoints)
- ✅ Server-side rendering failures
- ✅ Edge middleware issues
- ✅ Page load performance (Web Vitals)
- ✅ User sessions (which pages visited, actions taken)

**Example Errors It Catches**:
- "Failed to fetch /v1/events" (API down)
- "Cannot read property 'map' of undefined" (React crash)
- "Network request failed" (connectivity issues)
- "Chart rendering timeout" (performance)

---

### Backend (FastAPI/Railway)
**Configured**: ⚠️ Partially (code ready, DSN might need setting)

**Config File**:
- `services/etl/app/observability.py` - Sentry initialization for backend

**Environment Variable Needed**:
- `SENTRY_DSN_API` - Backend Sentry DSN (separate from frontend)

**What It SHOULD Track** (when fully configured):
- ✅ API endpoint errors (500 errors, exceptions)
- ✅ Database query failures
- ✅ Celery task failures (ingestion errors, LLM timeouts)
- ✅ Migration errors
- ✅ Performance issues (slow queries, timeouts)

**Example Errors It Would Catch**:
- "NULL value in non-nullable column" (like we just had!)
- "OpenAI API rate limit exceeded"
- "Database connection timeout"
- "Celery task exceeded timeout"

---

## 🔑 Your Sentry Project

### Access Your Dashboard
1. Go to https://sentry.io
2. Log in with your account
3. Select organization (if you have one)
4. Select project: "AGI Tracker" or similar

### Dashboard Overview

**Issues Tab** (Most Important):
- Shows all errors grouped by type
- Each "Issue" = group of similar errors
- Click to see full stack trace, context, affected users

**Performance Tab**:
- Shows slow endpoints
- Database query performance
- Frontend page load times

**Releases Tab**:
- Shows which deployment introduced errors
- Links errors to specific commits

---

## 📊 What You'll See in Sentry

### During Normal Operation (Green)
- **0-5 issues/day**: Minor edge cases, expected
- **Examples**: "User closed browser mid-request", "Temporary network timeout"
- **Action**: None needed (noise)

### During Problems (Yellow/Red)
- **10+ similar errors**: Something is wrong
- **Critical errors**: Database down, API key invalid
- **Examples**: Today's "NULL published_at" would show as:
  ```
  Issue: AttributeError in /v1/events
  Count: 47 occurrences (last 1 hour)
  Users Affected: 12
  Stack Trace: Line 1350 in main.py - ORDER BY published_at
  ```

---

## 🔄 How to Feed Sentry Logs to Me (Supervisor Agent)

### Method 1: Share Issue Link (Fastest)
**When you see an error in Sentry**:

1. Click on the Issue
2. Click "Share" button in top right
3. Copy the link (e.g., `https://sentry.io/organizations/xxx/issues/123456/`)
4. Paste in chat:
   ```
   @Supervisor: Sentry showing error - https://sentry.io/organizations/xxx/issues/123456/
   
   Analyze and fix please.
   ```

5. I'll:
   - Look at the stack trace (you can paste it)
   - Identify the root cause
   - Create a fix
   - Deploy the fix
   - Verify it resolved the issue

---

### Method 2: Screenshot + Context (Detailed)
**For complex issues**:

1. Open Sentry Issue
2. Take screenshot of:
   - Error message
   - Stack trace (top 10-15 lines)
   - Breadcrumbs (user actions leading to error)
   - Tags (release, environment, user info)

3. Share with context:
   ```
   @Supervisor: Getting errors on /v1/events endpoint
   
   Sentry details:
   - Error: "TypeError: Cannot read property 'map' of null"
   - File: main.py, line 1350
   - Occurrences: 23 in last hour
   - First seen: 2025-10-31 20:15 UTC
   - Release: b56662b
   
   [Screenshot attached]
   
   What should we do?
   ```

4. I'll:
   - Analyze the error pattern
   - Check if it's related to recent changes
   - Propose fix with explanation
   - Implement and test
   - Monitor Sentry to confirm resolution

---

### Method 3: Sentry API Export (Advanced)
**For batch analysis**:

Sentry has an API to export issues programmatically:

```bash
# Get all issues from last 24h
curl -H "Authorization: Bearer YOUR_SENTRY_TOKEN" \
  "https://sentry.io/api/0/projects/YOUR_ORG/YOUR_PROJECT/issues/?query=is:unresolved" \
  > sentry_issues.json

# Share with me
cat sentry_issues.json
```

I can then:
- Parse all issues
- Prioritize by severity/frequency
- Create fixes for top issues
- Generate a remediation plan

---

### Method 4: Daily Summary (Recommended)
**Every morning** (or when you check):

1. Open Sentry dashboard
2. Note these key metrics:
   ```
   @Supervisor: Daily Sentry Check - Nov 1
   
   New Issues: 2
   - Issue #1: "Database timeout on /v1/events" (5 occurrences)
   - Issue #2: "CORS error from unknown origin" (1 occurrence)
   
   Resolved: 1 (the NULL published_at issue)
   
   Performance:
   - /v1/events: avg 450ms (was 200ms yesterday - slower?)
   - /v1/index: avg 120ms (good)
   
   Should we investigate the timeout?
   ```

3. I'll:
   - Assess severity
   - Recommend action (fix now vs monitor vs ignore)
   - Implement fixes if needed

---

## 🎯 Sentry Issue Priority Guide

### 🔴 P0 - Critical (Fix Immediately)
**What**: System down, data loss risk, security breach

**Sentry Signals**:
- 100+ errors in 1 hour
- Error rate >10%
- Error: "Database connection failed"
- Error: "Authentication bypass"
- All users affected

**What to Do**:
1. Paste Sentry link immediately: `@Supervisor: CRITICAL - [link]`
2. I'll drop everything and fix
3. We'll rollback if needed

---

### 🟡 P1 - High (Fix Within 24h)
**What**: Feature broken, bad user experience, performance degraded

**Sentry Signals**:
- 10-50 errors in 1 hour
- Error rate 1-10%
- Error: "500 on /v1/events" (today's issue)
- Error: "Chart failed to render"
- 10-50% of users affected

**What to Do**:
1. Share Sentry summary: `@Supervisor: Issue with /v1/events - 23 errors, stack trace shows...`
2. I'll analyze and propose fix
3. You approve, I implement
4. Monitor Sentry to confirm resolved

---

### 🟢 P2 - Medium (Fix This Week)
**What**: Minor bugs, edge cases, optimization opportunities

**Sentry Signals**:
- 1-10 errors/day
- Error rate <1%
- Error: "Image failed to load"
- Error: "Timeout on slow query"
- <5% of users affected

**What to Do**:
1. Weekly batch: `@Supervisor: This week's Sentry issues: [list]`
2. I'll prioritize and fix in batch
3. Deploy with next release

---

### ⚪ P3 - Low (Monitor Only)
**What**: Expected errors, user-caused, network issues

**Sentry Signals**:
- 1-5 errors/day
- Error: "User canceled request"
- Error: "Network timeout" (temporary)
- Error: "Browser extension blocked request"

**What to Do**:
- Note the pattern
- If it becomes frequent (P2), then investigate
- Otherwise ignore (noise)

---

## 📖 How to Read a Sentry Error Report

### Anatomy of a Sentry Issue

**1. Title & Summary**
```
TypeError: Cannot read properties of null (reading 'published_at')
```
**Tells you**: What broke and where

**2. Stack Trace**
```python
File "services/etl/app/main.py", line 1350, in list_events
    events = query.order_by(desc(Event.published_at)).limit(limit).all()
                                   ^^^^^^^^^^^^^^^^^^^
TypeError: Cannot read properties of null
```
**Tells you**: Exact line of code that failed

**3. Breadcrumbs**
```
1. User navigated to /events
2. API called /v1/events
3. Database query started
4. ERROR: NULL value encountered
```
**Tells you**: What user was doing when it broke

**4. Context**
```
Request: GET /v1/events?limit=50
User: Anonymous (IP: 192.168.1.1)
Release: b56662b
Environment: production
```
**Tells you**: Environment details

**5. Similar Issues**
```
Grouped with 47 similar errors
First seen: 2025-10-31 20:15 UTC
Last seen: 2025-10-31 20:45 UTC
```
**Tells you**: Frequency and pattern

---

## 🔧 Remediation Workflow with Supervisor Agent

### Standard Process

**Step 1: You Discover Issue in Sentry**
```
Morning check → Sentry shows new issue → 23 occurrences
```

**Step 2: Share with Supervisor Agent (Me)**
```
@Supervisor: Sentry Issue - TypeError in /v1/events

Details from Sentry:
- Error: "Cannot read properties of null (reading 'published_at')"
- File: main.py, line 1350
- Count: 23 occurrences (last 1 hour)
- First seen: 20:15 UTC
- Release: b56662b

[Paste stack trace or link]
```

**Step 3: I Analyze**
```
I'll respond with:
- Root cause analysis
- Impact assessment (how many users affected)
- Proposed fix (code changes)
- Risk level (is this critical?)
- Timeline (fix now vs later)
```

**Step 4: I Implement Fix**
```
I'll:
1. Locate the problematic code
2. Write the fix
3. Test locally if possible
4. Deploy to Railway
5. Monitor Sentry to confirm resolution
```

**Step 5: Verification**
```
30 minutes after fix deployed:
- Check Sentry: New occurrences stopped?
- Mark issue as "Resolved" in Sentry
- Document in daily standup
```

---

## 🎬 Real Example (Today's Issue)

### What Happened

**1. You Reported**:
```
"Events pages broken - showing 500 errors"
```

**2. Sentry WOULD Have Shown** (if fully configured):
```
Issue: sqlalchemy.exc.InternalError
Message: ORDER BY published_at failed - NULL values present
File: main.py, line 1350
Count: 47 errors
First seen: 20:10 UTC
Release: d59fdaa
```

**3. I Diagnosed**:
- Ran database query to find NULL values
- Found 150 events with NULL published_at
- Identified root cause: Blog ingestion didn't set dates

**4. I Fixed**:
```python
# Set published_at = ingested_at for NULL values
for event in null_published:
    event.published_at = event.ingested_at
db.commit()
```

**5. Verified**:
- Tested `/v1/events` → Working ✅
- Sentry would show: Issue resolved, no new occurrences

**With Sentry, this would have been even faster** - I'd see the exact error line immediately instead of debugging blind.

---

## 📱 How to Access Your Sentry Data

### Dashboard Access
1. **Go to**: https://sentry.io
2. **Login**: Your account
3. **Select**: Your AGI Tracker project

### Key Pages

**Issues** (Main Dashboard):
- Shows all errors grouped by type
- Sorted by frequency (most common first)
- Color-coded by severity (red = critical, yellow = warning)

**Performance**:
- Shows slow endpoints
- Database query times
- Frontend page load times
- Trends over time

**Releases**:
- Shows which commit introduced errors
- Links to GitHub commits
- Shows error distribution per release

**Discover**:
- Query custom metrics
- Build custom dashboards
- Export data for analysis

---

## 📋 Daily Sentry Check Template

### Quick 2-Minute Review

Open Sentry and check:

**1. New Issues (30 seconds)**
```
How many new issues today? _____
Any critical (red) issues? _____
Any high-frequency issues (>10 occurrences)? _____
```

**2. Top Issue (30 seconds)**
```
Most common error: _____________
Occurrences: _____
File/line: _____________
Severity: P0/P1/P2/P3
```

**3. Performance (30 seconds)**
```
Slowest endpoint: _____________
Average response time: _____ ms
Any endpoints >1 second? _____
```

**4. Decision (30 seconds)**
```
Action needed?
[ ] No - all green
[ ] Yes - share with Supervisor: [describe]
[ ] Monitor - check again tomorrow
```

---

## 🤖 How to Work with Me (Supervisor Agent)

### For Individual Issues

**Quick Fix** (5-10 minutes):
```
@Supervisor: Fix this Sentry issue

Issue: TypeError in /v1/events
Link: https://sentry.io/issues/123456
Stack trace:
  File "main.py", line 1350
  TypeError: Cannot read property 'map' of null

Please fix and deploy.
```

**I'll**:
1. Read the stack trace
2. Find the code
3. Identify root cause
4. Implement fix
5. Deploy to Railway
6. Mark issue as resolved in Sentry

---

### For Batch Issues (Weekly Review)

**Comprehensive Analysis** (30-60 minutes):
```
@Supervisor: Weekly Sentry Review

Here are this week's issues from Sentry:

P1 Issues:
1. "Database timeout on /v1/events" - 23 occurrences
   Link: https://sentry.io/issues/111111

2. "CORS error from unknown domain" - 15 occurrences  
   Link: https://sentry.io/issues/222222

P2 Issues:
3. "Image load timeout" - 8 occurrences
4. "Chart render slow" - 5 occurrences

Please analyze, prioritize, and create fixes for P1 items.
```

**I'll**:
1. Analyze all issues
2. Prioritize by impact
3. Create comprehensive fix plan
4. Implement fixes in order
5. Deploy and verify
6. Document in weekly summary

---

### For Performance Issues

**Optimization Request**:
```
@Supervisor: Sentry Performance Analysis

Performance data from Sentry:
- /v1/events: p95 = 850ms (slow!)
- /v1/index: p95 = 120ms (good)
- /v1/signposts: p95 = 200ms (acceptable)

The /v1/events endpoint is 4x slower than expected.
Can you investigate and optimize?
```

**I'll**:
1. Profile the slow endpoint
2. Check database query plan
3. Add/optimize indexes if needed
4. Add caching if appropriate
5. Test performance improvement
6. Monitor Sentry for confirmation

---

## 🛠️ Backend Sentry Setup (Optional)

**Current State**: Frontend ✅ configured, Backend ⚠️ needs DSN

### To Enable Backend Monitoring

**Option 1: Use Same DSN** (Simpler):
```bash
# Use frontend DSN for backend too
railway variables --set "SENTRY_DSN_API=https://4da7aeb6938e51d9ca13ad25ba3f4dda@o4510274025422848.ingest.us.sentry.io/4510274033811456"
railway up --detach
```

**Option 2: Separate Project** (Better Organization):
```bash
# Create new Sentry project "AGI Tracker API"
# Copy DSN
railway variables --set "SENTRY_DSN_API=<new DSN>"
railway up --detach
```

**After enabling**, backend will report:
- Celery task failures
- Database errors
- API endpoint exceptions
- Performance issues

---

## 📈 Sentry Metrics to Track

### Daily Metrics
- **New Issues**: Should be 0-2/day
- **Total Errors**: Should be <20/day
- **Critical Issues**: Should be 0
- **Performance p95**: /v1/events <500ms, /v1/index <200ms

### Weekly Metrics
- **Resolved Issues**: Should resolve 80%+ of issues
- **Mean Time to Resolution**: <24 hours for P1
- **Error Rate**: <0.1% of requests
- **Performance Trend**: Stable or improving

---

## 🎯 Example Sentry Workflow (Real Scenario)

### Scenario: You Wake Up, Check Sentry

**Sentry Shows**:
```
⚠️ 1 New Issue (Last 24h)
   
Issue: "OpenAI API Rate Limit Exceeded"
Count: 15 occurrences
First seen: Nov 2, 6:30 AM
Last seen: Nov 2, 7:15 AM
File: generate_event_analysis.py, line 45
Users affected: 0 (background task)
```

**You Share**:
```
@Supervisor: Sentry alert - OpenAI rate limit

Issue from Sentry:
- OpenAI API Rate Limit Exceeded  
- 15 occurrences during morning ingestion
- File: generate_event_analysis.py, line 45
- Happened between 6:30-7:15 AM (during scheduled run)

Link: https://sentry.io/issues/789456

Is this normal? Should we fix?
```

**I Analyze**:
```
📊 Analysis:

Root Cause: 
- Morning ingestion fetched 50 new events
- LLM analysis tried to process all at once
- OpenAI rate limit: 500 RPM (requests per minute)
- 50 requests in ~6 minutes = rate limit hit

Severity: P2 (Medium)
- Only affects background processing
- No user impact
- Self-resolves after rate limit window

Fix Options:

Option A: Add rate limiting to LLM calls
- Add delay between requests (3s/request)
- Pros: Prevents rate limit
- Cons: Slower processing (but acceptable)
- Effort: 30 min

Option B: Batch process with backoff
- Process in smaller batches
- Retry with exponential backoff
- Pros: More robust
- Cons: More complex
- Effort: 2 hours

Option C: Monitor only (no fix)
- If it only happened once, might be transient
- OpenAI rate limits reset quickly
- Celery will retry failed tasks
- Pros: Zero effort
- Cons: Could recur

Recommendation: Option C (monitor)
- If happens again tomorrow → Option A
- If happens 3+ days → Option B
```

**You Decide**:
```
@Supervisor: Let's go with Option C. Monitor for now.
If it happens again, implement Option A.
```

**I Document**:
```
✅ Logged in daily standup
📋 Added to watch list
📊 Will check Sentry tomorrow for recurrence
```

---

## 🔍 What Each Error Type Means

### Frontend Errors (Next.js)

**"Cannot read property 'X' of undefined"**
- **Meaning**: React component received null/undefined data
- **Typical Cause**: API returned unexpected format
- **Fix**: Add null checks or fix API response

**"Network request failed"**
- **Meaning**: Frontend couldn't reach backend API
- **Typical Cause**: Backend down, CORS issue, network problem
- **Fix**: Check backend health, verify CORS settings

**"ChunkLoadError"**
- **Meaning**: JavaScript bundle failed to load
- **Typical Cause**: Deployment race condition
- **Fix**: Usually self-resolves, user refresh needed

---

### Backend Errors (FastAPI)

**"sqlalchemy.exc.InternalError"**
- **Meaning**: Database query failed
- **Typical Cause**: Schema issue, NULL constraint, timeout
- **Fix**: Fix schema or add NULL handling (like we just did)

**"HTTPException: 500"**
- **Meaning**: Unhandled exception in endpoint
- **Typical Cause**: Bug in business logic
- **Fix**: Add error handling or fix logic

**"openai.RateLimitError"**
- **Meaning**: OpenAI API rate limit hit
- **Typical Cause**: Too many requests too fast
- **Fix**: Add rate limiting or batching

**"celery.exceptions.SoftTimeLimitExceeded"**
- **Meaning**: Celery task took too long
- **Typical Cause**: Slow API call, large data processing
- **Fix**: Optimize task or increase timeout

---

## 📊 Sentry Configuration Status

### Frontend (Vercel) ✅
- **Status**: Fully configured
- **DSN**: Set in config files
- **Coverage**: All pages, API routes, edge functions
- **Sampling**: 100% (all errors captured)
- **Performance**: Tracking Web Vitals

### Backend (Railway) ⚠️
- **Status**: Code ready, DSN needed
- **File**: `services/etl/app/observability.py`
- **To Enable**: Set `SENTRY_DSN_API` environment variable
- **Benefit**: Will catch backend errors (today's NULL issue would have shown immediately)

**Recommendation**: Enable backend Sentry now (5 min setup):
```bash
railway variables --set "SENTRY_DSN_API=https://4da7aeb6938e51d9ca13ad25ba3f4dda@o4510274025422848.ingest.us.sentry.io/4510274033811456"
railway up --detach
```

---

## 🎯 Summary: Your Sentry Setup

### What It Is
Real-time error tracking that automatically captures and reports problems in your app.

### What It's Monitoring
- ✅ **Frontend**: All React errors, API route failures, performance
- ⚠️ **Backend**: Ready to enable (just needs DSN set)

### How to Use It with Me
1. **Check Sentry** daily (2 min)
2. **Share issues** with me: `@Supervisor: Sentry issue - [link or description]`
3. **I analyze** and propose fixes
4. **I implement** and deploy
5. **We verify** in Sentry that it's resolved

### When to Check
- **Daily**: Morning health check (2 min)
- **When alerted**: Sentry emails you about critical issues
- **When bugs reported**: Check if Sentry caught it

### What to Share
- **P0/P1**: Immediately (link + brief description)
- **P2**: Weekly batch (list all medium issues)
- **P3**: Optional (only if pattern emerges)

---

## ✅ Next Steps

### Recommended (5 minutes):
1. **Enable backend Sentry** (set SENTRY_DSN_API)
2. **Bookmark** Sentry dashboard
3. **Set up email alerts** (Sentry → Settings → Alerts)

### Tomorrow Morning (2 minutes):
1. Check Sentry for new issues
2. If none: ✅ System healthy
3. If some: Share with me, I'll fix

### This Week:
1. Monitor Sentry daily
2. Share any P1 issues immediately
3. After 7 days of stability → Week 3 features

---

**Sentry is your early warning system. I'm your remediation agent. Together we keep the system healthy.** 🛡️

**Just check Sentry each morning and ping me if you see anything concerning!** 👍


