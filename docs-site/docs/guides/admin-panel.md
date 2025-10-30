# Admin Panel Guide

Manage API keys, review event mappings, validate URLs, and monitor system health.

## Overview

The Admin Panel provides tools for:
- **API Key Management**: Create, revoke, monitor usage
- **Event Review**: Approve/reject event-signpost mappings
- **URL Validation**: Check for broken source links
- **Source Credibility**: Track retraction rates
- **System Monitoring**: Health checks, task status, analytics

**Access**: Admin API key required

## Accessing the Admin Panel

### Authentication

Admin endpoints require `x-api-key` header:

```bash
curl -H "x-api-key: your-admin-key" \
  http://localhost:8000/v1/admin/api-keys
```

**Web UI**: http://localhost:3000/admin

Login with admin API key (stored in `.env` as `API_KEY`).

### Setting Admin Key

**Development**:
```env
# services/etl/.env
API_KEY=dev-key-change-in-production
```

**Production**:
```bash
# Generate secure key
openssl rand -hex 32

# Set in environment
API_KEY=your-64-char-hex-key
```

## API Key Management

### Creating API Keys

**Web UI**:
1. Go to `/admin/api-keys`
2. Click **Create New Key**
3. Fill form:
   ```
   Name: [Research API Key]
   Tier: [ Authenticated ] (Public/Authenticated/Admin)
   Rate Limit: [300] req/min (optional override)
   Expires: [2026-10-29] (optional)
   ```
4. Click **Create**
5. **Copy key immediately** (shown once!)

**API**:
```bash
curl -X POST http://localhost:8000/v1/admin/api-keys \
  -H "x-api-key: $ADMIN_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Research API Key",
    "tier": "authenticated",
    "rate_limit_override": 300,
    "expires_at": "2026-10-29T00:00:00Z"
  }'
```

Response:
```json
{
  "key_id": 1,
  "key": "agi-...random-32-chars...",
  "name": "Research API Key",
  "tier": "authenticated",
  "created_at": "2025-10-29T12:00:00Z"
}
```

⚠️ **SECURITY**: The full key is only shown once. Store it securely!

### Listing API Keys

**Web UI**: `/admin/api-keys` shows table:

| ID | Name | Tier | Requests (24h) | Last Used | Status |
|----|------|------|----------------|-----------|--------|
| 1 | Research Key | Auth | 1,247 | 2 min ago | ✅ Active |
| 2 | Old Test Key | Auth | 0 | 30 days ago | ⚠️ Inactive |

**API**:
```bash
curl http://localhost:8000/v1/admin/api-keys \
  -H "x-api-key: $ADMIN_API_KEY"
```

### Revoking API Keys

**Web UI**:
1. Click **Revoke** button next to key
2. Confirm: "Are you sure?"
3. Key immediately invalid

**API**:
```bash
curl -X DELETE http://localhost:8000/v1/admin/api-keys/1 \
  -H "x-api-key: $ADMIN_API_KEY"
```

**Effect**: All requests with that key return `401 Unauthorized`.

### Monitoring Usage

**Web UI**: `/admin/api-keys/usage` shows:

```
Key: Research API Key
24h Requests: 1,247
Peak Hour: 142 req (11 AM UTC)
Rate Limit Hits: 3
Top Endpoints:
  /v1/events: 782 (62%)
  /v1/index: 312 (25%)
  /v1/signposts: 153 (13%)
```

**API**:
```bash
curl http://localhost:8000/v1/admin/api-keys/1/usage \
  -H "x-api-key: $ADMIN_API_KEY"
```

## Event Review Queue

### Why Review Is Needed

Events are auto-mapped to signposts via LLM. Low-confidence mappings (<0.7) are flagged for human review to prevent:
- False positives (irrelevant event linked)
- False negatives (relevant event missed)
- Incorrect signpost (event mapped to wrong milestone)

### Accessing Review Queue

**Web UI**: `/admin/review`

**API**:
```bash
curl http://localhost:8000/v1/admin/review/queue \
  -H "x-api-key: $ADMIN_API_KEY"
```

### Review Interface

Each pending item shows:

```
Event: "GPT-5 Achieves 85% on SWE-bench Verified"
Tier: A-tier
Date: 2025-10-15

Proposed Mapping:
  Signpost: SWE-bench ≥70%
  Confidence: 0.62 (flagged: < 0.7)
  Link Type: supports

[ ✅ Approve ] [ ❌ Reject ] [ 🚩 Flag for Discussion ]
```

### Approving Mappings

**Web UI**: Click **✅ Approve**

**API**:
```bash
curl -X POST http://localhost:8000/v1/admin/events/123/approve \
  -H "x-api-key: $ADMIN_API_KEY"
```

**Effect**:
- Mapping activated
- Event appears in signpost's linked events
- Progress recalculated (if A/B tier)

### Rejecting Mappings

**Web UI**:
1. Click **❌ Reject**
2. Provide reason: "Wrong benchmark version"
3. Submit

**API**:
```bash
curl -X POST "http://localhost:8000/v1/admin/events/123/reject?reason=Wrong+benchmark+version" \
  -H "x-api-key: $ADMIN_API_KEY"
```

**Effect**:
- Mapping deleted
- Event remains in database (unmapped)
- Logged in changelog

### Bulk Actions

**Approve all high-confidence** (≥0.65):
```bash
curl -X POST http://localhost:8000/v1/admin/review/bulk-approve?min_confidence=0.65 \
  -H "x-api-key: $ADMIN_API_KEY"
```

**Reject all C/D tier** (policy: never auto-approve):
```bash
curl -X POST http://localhost:8000/v1/admin/review/bulk-reject?tier=C,D \
  -H "x-api-key: $ADMIN_API_KEY"
```

## URL Validation

### Manual Validation

**Validate all events**:
```bash
curl -X POST http://localhost:8000/v1/admin/validate-urls \
  -H "x-api-key: $ADMIN_API_KEY"
```

**Validate specific event**:
```bash
curl -X POST http://localhost:8000/v1/admin/validate-url/123 \
  -H "x-api-key: $ADMIN_API_KEY"
```

### Viewing Invalid URLs

**Web UI**: `/admin/invalid-urls` shows:

| Event | URL | Error | Last Checked |
|-------|-----|-------|--------------|
| GPT-4.5 Announcement | https://... | 404 Not Found | 2 hours ago |
| Claude 3 Paper | https://... | Connection timeout | 1 day ago |

**API**:
```bash
curl http://localhost:8000/v1/admin/invalid-urls \
  -H "x-api-key: $ADMIN_API_KEY"
```

### URL Validation Stats

```bash
curl http://localhost:8000/v1/admin/url-stats \
  -H "x-api-key: $ADMIN_API_KEY"
```

Response:
```json
{
  "total_events": 1247,
  "valid_urls": 1189,
  "invalid_urls": 58,
  "never_validated": 0,
  "last_validation_run": "2025-10-29T06:00:00Z"
}
```

## Source Credibility

### Viewing Credibility Scores

**Web UI**: `/admin/source-credibility` shows:

| Source | Events | Retractions | Rate | Tier |
|--------|--------|-------------|------|------|
| arXiv | 342 | 2 | 0.6% | A |
| OpenAI Blog | 87 | 0 | 0.0% | B |
| Reuters | 156 | 8 | 5.1% | C |
| Twitter | 45 | 12 | 26.7% | D |

**API**:
```bash
curl http://localhost:8000/v1/admin/source-credibility \
  -H "x-api-key: $ADMIN_API_KEY"
```

### Credibility Score Calculation

```python
score = 1.0 - retraction_rate + volume_bonus

retraction_rate = retractions / total_events
volume_bonus = min(0.1, log10(total_events) / 100)
```

**Example**:
- arXiv: 342 events, 2 retractions
- Rate: 2/342 = 0.6%
- Volume bonus: log10(342)/100 = 0.025
- Score: 1.0 - 0.006 + 0.025 = **1.019** (excellent)

### Flagging Unreliable Sources

If a source's credibility drops below threshold:

1. Admin receives alert
2. Review source manually
3. Options:
   - **Downgrade tier** (B → C)
   - **Block source** (no new events)
   - **Retract all events** (if systemic issue)

**Blocking a source**:
```bash
curl -X POST http://localhost:8000/v1/admin/sources/123/block \
  -H "x-api-key: $ADMIN_API_KEY" \
  -d '{"reason": "Repeated false claims"}'
```

## Retraction Workflow

### Retracting an Event

**When to retract**:
- Original paper retracted
- Methodology found flawed
- Data fabricated
- Leaderboard corrected

**Web UI**:
1. Go to event detail page
2. Click **Retract** button
3. Fill form:
   ```
   Reason: [Paper methodology flawed]
   Evidence URL: [https://arxiv.org/retraction/...]
   ```
4. Submit

**API**:
```bash
curl -X POST http://localhost:8000/v1/admin/retract \
  -H "x-api-key: $ADMIN_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "event_id": 123,
    "reason": "Paper methodology flawed",
    "evidence_url": "https://arxiv.org/retraction/..."
  }'
```

**Effect**:
1. Event marked `retracted=true`
2. Progress recalculated (impact removed)
3. Changelog entry created
4. Source credibility score updated
5. Users see retraction banner

## System Monitoring

### Health Dashboard

**Web UI**: `/admin/health` shows:

```
System Health: ✅ All Systems Operational

Database:  ✅ Connected (23ms latency)
Redis:     ✅ Connected (5ms latency)
Celery:    ✅ 4 workers active
API:       ✅ 127 req/min

Recent Tasks:
  fetch_feeds:      ✅ 6h ago
  compute_snapshots: ✅ 5h ago
  validate_urls:    ✅ 2h ago
```

**API**:
```bash
curl http://localhost:8000/health/full \
  -H "x-api-key: $ADMIN_API_KEY"
```

### Task Status

Check Celery task watchdogs:

```bash
curl http://localhost:8000/v1/admin/tasks \
  -H "x-api-key: $ADMIN_API_KEY"
```

Response:
```json
{
  "tasks": [
    {
      "name": "fetch_feeds",
      "last_run": "2025-10-29T06:00:00Z",
      "status": "success",
      "duration_ms": 12450
    },
    {
      "name": "validate_urls",
      "last_run": "2025-10-29T10:00:00Z",
      "status": "running",
      "duration_ms": null
    }
  ]
}
```

### Analytics

**Events ingested (last 7 days)**:
```bash
curl http://localhost:8000/v1/admin/analytics/events \
  -H "x-api-key: $ADMIN_API_KEY"
```

**LLM budget usage**:
```bash
curl http://localhost:8000/v1/admin/analytics/llm-budget \
  -H "x-api-key: $ADMIN_API_KEY"
```

Response:
```json
{
  "daily_limit_usd": 20,
  "today_spend_usd": 12.34,
  "remaining_usd": 7.66,
  "tasks_run": 42,
  "avg_cost_per_task": 0.29
}
```

## Manual Triggers

### Recompute Index

Force recalculation of all snapshots:

```bash
curl -X POST http://localhost:8000/v1/admin/recompute \
  -H "x-api-key: $ADMIN_API_KEY"
```

**Use when**:
- After bulk approvals
- After retractions
- After manual data fixes

### Trigger ETL Tasks

**Fetch feeds now** (don't wait for schedule):
```bash
curl -X POST http://localhost:8000/v1/admin/tasks/fetch-feeds \
  -H "x-api-key: $ADMIN_API_KEY"
```

**Generate weekly digest**:
```bash
curl -X POST http://localhost:8000/v1/admin/tasks/weekly-digest \
  -H "x-api-key: $ADMIN_API_KEY"
```

## Best Practices

✅ **Do**:
- Rotate admin API key quarterly
- Review queue daily (keep <30 items)
- Monitor source credibility monthly
- Validate URLs weekly
- Check health dashboard before deployments

❌ **Don't**:
- Share admin API key
- Auto-approve all low-confidence mappings
- Ignore URL validation failures
- Retract without evidence
- Skip changelog entries

## Security Tips

1. **Admin key security**:
   - Store in password manager
   - Never commit to git
   - Rotate every 3-6 months
   - Use different keys for staging/prod

2. **Rate limiting**:
   - Admin keys have unlimited requests
   - Monitor usage for anomalies
   - Revoke if compromised

3. **Audit logs**:
   - All admin actions logged
   - Review weekly for unauthorized access
   - Stored 90 days

## Troubleshooting

### "401 Unauthorized"

**Cause**: Invalid admin API key

**Fix**:
- Check `.env` for correct `API_KEY`
- Verify header: `x-api-key: ...`
- Test with curl: `curl -H "x-api-key: $API_KEY" .../health`

### Review Queue Empty but Events Unmapped

**Cause**: Confidence threshold too low

**Fix**:
- Lower threshold: `?min_confidence=0.5`
- Check for errors in LLM mapping task

### URL Validation Slow

**Cause**: Too many events (timeout)

**Fix**:
- Run in batches: `?limit=100`
- Increase timeout in config
- Run as background Celery task

## Next Steps

- [API Usage](/docs/guides/api-usage) - Build admin tools
- [Events Feed](/docs/guides/events-feed) - Understand event lifecycle
- [Troubleshooting](/docs/troubleshooting) - Debug common issues

## Related Resources

- **API Authentication**: [/docs/api/authentication](/docs/api/authentication)
- **Admin Endpoints**: [/docs/api/endpoints#admin](/docs/api/endpoints)
- **Security Policy**: [/legal/privacy](/legal/privacy) (on live site)

