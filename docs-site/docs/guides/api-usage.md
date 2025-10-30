# API Usage Guide

Integrate AGI Tracker data into your applications with our public JSON API.

## Overview

The AGI Tracker provides a **read-only public API** for accessing:
- **Events**: AI developments with evidence tiers
- **Signposts**: Measurable milestones and progress
- **Index scores**: Overall and category proximity scores
- **Expert predictions**: Forecast comparisons
- **Weekly digests**: AI-generated summaries

**Base URL**: `https://agitracker-production-6efa.up.railway.app` (production)  
**Docs**: `/docs` (interactive Swagger UI)

## Quick Start

### No Authentication Required

Most endpoints are public (no API key needed):

```bash
# Get current AGI proximity index
curl https://agitracker-production-6efa.up.railway.app/v1/index

# Get recent events
curl https://agitracker-production-6efa.up.railway.app/v1/events?limit=10

# Get signposts
curl https://agitracker-production-6efa.up.railway.app/v1/signposts
```

### With Authentication (Optional)

Get an API key for higher rate limits:

1. Contact admin for API key
2. Add header: `x-api-key: your-key`
3. Enjoy 300 req/min (vs 60 public)

```bash
curl -H "x-api-key: your-key" \
  https://agitracker-production-6efa.up.railway.app/v1/events
```

## Core Endpoints

### GET /v1/index

Get current AGI proximity scores.

**Parameters**:
- `preset` (optional): `equal` | `aschenbrenner` | `ai2027` (default: `equal`)
- `date` (optional): `YYYY-MM-DD` (historical snapshot)

**Example**:
```bash
curl "https://agitracker-production-6efa.up.railway.app/v1/index?preset=aschenbrenner"
```

**Response**:
```json
{
  "as_of_date": "2025-10-29",
  "preset": "aschenbrenner",
  "overall": 0.52,
  "capabilities": 0.68,
  "agents": 0.12,
  "inputs": 0.78,
  "security": 0.05,
  "safety_margin": -0.63
}
```

### GET /v1/events

List AI events with filtering and pagination.

**Parameters**:
- `tier` (optional): `A` | `B` | `C` | `D` (multiple allowed)
- `since` (optional): `YYYY-MM-DD` (events after this date)
- `category` (optional): `capabilities` | `agents` | `inputs` | `security`
- `min_significance` (optional): `0.0`-`1.0` (minimum impact score)
- `limit` (optional): Max results (default: 50, max: 100)
- `cursor` (optional): Pagination cursor from previous response

**Example**:
```bash
curl "https://agitracker-production-6efa.up.railway.app/v1/events?tier=A&tier=B&since=2025-10-01&limit=20"
```

**Response**:
```json
{
  "events": [
    {
      "id": 123,
      "title": "GPT-5 Achieves 85% on SWE-bench Verified",
      "summary": "OpenAI's GPT-5 achieves new state-of-the-art...",
      "published_at": "2025-10-15T00:00:00Z",
      "evidence_tier": "A",
      "source_type": "paper",
      "source_url": "https://openai.com/research/gpt-5",
      "signposts": ["swebench_70", "swebench_90"]
    }
  ],
  "next_cursor": "MjAyNS0xMC0xNVQwMDowMDowMHwxMjM=",
  "has_more": true,
  "total_count": 847
}
```

### GET /v1/signposts

List all signposts with current progress.

**Parameters**:
- `category` (optional): `capabilities` | `agents` | `inputs` | `security`
- `first_class` (optional): `true` | `false` (filter by first-class status)

**Example**:
```bash
curl "https://agitracker-production-6efa.up.railway.app/v1/signposts?category=capabilities&first_class=true"
```

**Response**:
```json
{
  "signposts": [
    {
      "id": 1,
      "code": "swebench_70",
      "name": "SWE-bench ≥70%",
      "category": "capabilities",
      "first_class": true,
      "baseline": 0.139,
      "target": 0.70,
      "current_value": 0.523,
      "progress": 0.685,
      "direction": ">=",
      "unit": "percentage"
    }
  ]
}
```

### GET /v1/signposts/by-code/\{code\}/events

Get events linked to a specific signpost.

**Example**:
```bash
curl "https://agitracker-production-6efa.up.railway.app/v1/signposts/by-code/swebench_70/events"
```

**Response**:
```json
{
  "signpost": {
    "code": "swebench_70",
    "name": "SWE-bench ≥70%",
    "progress": 0.685
  },
  "events": [
    {
      "id": 123,
      "title": "GPT-5 Achieves 85%...",
      "evidence_tier": "A",
      "impact_estimate": 0.324
    }
  ]
}
```

### GET /v1/search

Full-text search across events.

**Parameters**:
- `q` (required): Search query
- `tier` (optional): Filter by evidence tier
- `limit` (optional): Max results (default: 10, max: 50)

**Example**:
```bash
curl "https://agitracker-production-6efa.up.railway.app/v1/search?q=GPT-5&tier=A"
```

**Response**:
```json
{
  "query": "GPT-5",
  "results": [
    {
      "id": 123,
      "title": "GPT-5 Achieves 85% on SWE-bench Verified",
      "match_score": 0.95,
      "evidence_tier": "A"
    }
  ],
  "total_matches": 8
}
```

## Code Examples

### Python

```python
import requests

# Get current index
response = requests.get(
    "https://agitracker-production-6efa.up.railway.app/v1/index",
    params={"preset": "aschenbrenner"}
)
data = response.json()
print(f"Overall AGI proximity: {data['overall']:.1%}")

# Get recent A-tier events
response = requests.get(
    "https://agitracker-production-6efa.up.railway.app/v1/events",
    params={"tier": "A", "limit": 10}
)
events = response.json()["events"]
for event in events:
    print(f"{event['published_at']}: {event['title']}")

# Search for specific topic
response = requests.get(
    "https://agitracker-production-6efa.up.railway.app/v1/search",
    params={"q": "reasoning", "tier": "A"}
)
results = response.json()["results"]
print(f"Found {len(results)} matching events")
```

### JavaScript/TypeScript

```typescript
// Get current index
const response = await fetch(
  "https://agitracker-production-6efa.up.railway.app/v1/index?preset=equal"
);
const data = await response.json();
console.log(`Overall: ${(data.overall * 100).toFixed(1)}%`);

// Get events with cursor pagination
let cursor = null;
const allEvents = [];

do {
  const url = new URL("https://agitracker-production-6efa.up.railway.app/v1/events");
  url.searchParams.set("tier", "A");
  url.searchParams.set("limit", "50");
  if (cursor) url.searchParams.set("cursor", cursor);

  const response = await fetch(url);
  const data = await response.json();
  
  allEvents.push(...data.events);
  cursor = data.has_more ? data.next_cursor : null;
} while (cursor);

console.log(`Fetched ${allEvents.length} events`);
```

### cURL

```bash
#!/bin/bash

# Save events to JSON file
curl "https://agitracker-production-6efa.up.railway.app/v1/events?tier=A&limit=100" \
  -o events.json

# Extract just titles
curl "https://agitracker-production-6efa.up.railway.app/v1/events?tier=A" | \
  jq -r '.events[].title'

# Get signposts and format as CSV
curl "https://agitracker-production-6efa.up.railway.app/v1/signposts" | \
  jq -r '.signposts[] | [.code, .name, .progress] | @csv' \
  > signposts.csv
```

### R

```r
library(httr)
library(jsonlite)

# Get index data
response <- GET("https://agitracker-production-6efa.up.railway.app/v1/index")
data <- fromJSON(content(response, "text"))
cat(sprintf("Overall: %.1f%%\n", data$overall * 100))

# Get events as data frame
response <- GET(
  "https://agitracker-production-6efa.up.railway.app/v1/events",
  query = list(tier = "A", limit = 100)
)
events <- fromJSON(content(response, "text"))$events

# Plot timeline
library(ggplot2)
events$published_at <- as.Date(events$published_at)

ggplot(events, aes(x = published_at, y = 1)) +
  geom_point() +
  labs(title = "A-tier Events Timeline")
```

## Rate Limiting

### Limits by Tier

| Tier | Rate Limit | Cost |
|------|------------|------|
| **Public** (no key) | 60 req/min | Free |
| **Authenticated** | 300 req/min | Free (request key) |
| **Admin** | Unlimited | Internal only |

### Handling Rate Limits

When you hit the limit, you'll receive:

**Response**:
```json
{
  "error": "Rate limit exceeded",
  "retry_after": 42
}
```

**Status code**: `429 Too Many Requests`

**Headers**:
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1635532800
Retry-After: 42
```

**Best practice**:
```python
import time

def fetch_with_retry(url, max_retries=3):
    for attempt in range(max_retries):
        response = requests.get(url)
        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 60))
            print(f"Rate limited. Retrying in {retry_after}s...")
            time.sleep(retry_after)
            continue
        return response.json()
    raise Exception("Max retries exceeded")
```

## Caching

### Cache Headers

Responses include cache directives:

```
Cache-Control: public, max-age=600
ETag: "abc123def456"
Last-Modified: Mon, 29 Oct 2025 12:00:00 GMT
```

**Meaning**:
- `max-age=600`: Cache for 10 minutes
- `ETag`: Unique version identifier
- `Last-Modified`: When data last changed

### Conditional Requests

Use `ETag` to avoid re-downloading unchanged data:

**First request**:
```bash
curl -I "https://agitracker-production-6efa.up.railway.app/v1/index"
# Returns: ETag: "abc123"
```

**Subsequent request**:
```bash
curl -H 'If-None-Match: "abc123"' \
  "https://agitracker-production-6efa.up.railway.app/v1/index"
# Returns: 304 Not Modified (if unchanged)
```

**Benefits**:
- Saves bandwidth
- Faster responses
- Counts toward rate limit but less expensive

### Client-Side Caching

```python
import requests_cache

# Cache responses for 10 minutes
session = requests_cache.CachedSession(expire_after=600)

response = session.get("https://agitracker-production-6efa.up.railway.app/v1/index")
# First request: fetches from API
# Subsequent requests within 10 min: served from cache
```

## Pagination

### Cursor-Based Pagination

For large result sets, use cursor pagination (more efficient than offset):

**First page**:
```bash
curl "https://agitracker-production-6efa.up.railway.app/v1/events?limit=50"
```

**Response**:
```json
{
  "events": [...],
  "next_cursor": "MjAyNS0xMC0yOVQxMjowMDowMHwxMjM=",
  "has_more": true
}
```

**Next page**:
```bash
curl "https://agitracker-production-6efa.up.railway.app/v1/events?cursor=MjAyNS0xMC0yOVQxMjowMDowMHwxMjM=&limit=50"
```

**Python helper**:
```python
def fetch_all_events(tier="A"):
    events = []
    cursor = None
    
    while True:
        params = {"tier": tier, "limit": 100}
        if cursor:
            params["cursor"] = cursor
        
        response = requests.get(
            "https://agitracker-production-6efa.up.railway.app/v1/events",
            params=params
        )
        data = response.json()
        
        events.extend(data["events"])
        
        if not data.get("has_more"):
            break
        cursor = data["next_cursor"]
    
    return events
```

## Error Handling

### HTTP Status Codes

| Code | Meaning | Action |
|------|---------|--------|
| `200` | Success | Process response |
| `304` | Not Modified | Use cached data |
| `400` | Bad Request | Fix query parameters |
| `401` | Unauthorized | Check API key |
| `404` | Not Found | Check endpoint URL |
| `429` | Rate Limited | Wait and retry |
| `500` | Server Error | Retry with backoff |

### Error Response Format

```json
{
  "error": "Invalid parameter: tier",
  "detail": "tier must be one of: A, B, C, D",
  "code": "INVALID_PARAMETER"
}
```

### Robust Client

```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def create_session():
    session = requests.Session()
    
    # Retry on 500, 502, 503, 504
    retry = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    
    return session

session = create_session()
response = session.get("https://agitracker-production-6efa.up.railway.app/v1/index")
```

## Advanced Use Cases

### Building a Custom Dashboard

Fetch index, events, and signposts in parallel:

```python
import asyncio
import aiohttp

async def fetch_all_data():
    async with aiohttp.ClientSession() as session:
        tasks = [
            session.get("https://agitracker-production-6efa.up.railway.app/v1/index"),
            session.get("https://agitracker-production-6efa.up.railway.app/v1/events?tier=A&limit=10"),
            session.get("https://agitracker-production-6efa.up.railway.app/v1/signposts?first_class=true")
        ]
        responses = await asyncio.gather(*tasks)
        
        index = await responses[0].json()
        events = await responses[1].json()
        signposts = await responses[2].json()
        
        return index, events, signposts

index, events, signposts = asyncio.run(fetch_all_data())
```

### Time-Series Analysis

Fetch historical snapshots:

```python
import pandas as pd
from datetime import date, timedelta

def fetch_index_history(days=90, preset="equal"):
    data = []
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    
    current = start_date
    while current <= end_date:
        response = requests.get(
            f"https://agitracker-production-6efa.up.railway.app/v1/index",
            params={"date": current.isoformat(), "preset": preset}
        )
        if response.status_code == 200:
            data.append(response.json())
        current += timedelta(days=1)
    
    return pd.DataFrame(data)

df = fetch_index_history(90, "aschenbrenner")
df.plot(x="as_of_date", y="overall", title="AGI Proximity (90 days)")
```

### Real-Time Monitoring

Poll for new events:

```python
import time

def monitor_new_events(check_interval=300):  # 5 minutes
    last_event_id = None
    
    while True:
        response = requests.get(
            "https://agitracker-production-6efa.up.railway.app/v1/events",
            params={"tier": "A", "limit": 1}
        )
        events = response.json()["events"]
        
        if events:
            latest = events[0]
            if last_event_id and latest["id"] != last_event_id:
                print(f"New event: {latest['title']}")
                # Send notification, update dashboard, etc.
            last_event_id = latest["id"]
        
        time.sleep(check_interval)

# Run in background
monitor_new_events()
```

## Webhooks (Future)

**Planned for Phase 6**: Subscribe to real-time updates.

```bash
curl -X POST "https://agitracker-production-6efa.up.railway.app/v1/webhooks" \
  -H "x-api-key: your-key" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://yourapp.com/webhook",
    "events": ["event.created", "index.updated"],
    "tiers": ["A", "B"]
  }'
```

When an A/B tier event is created, you receive:

```json
{
  "type": "event.created",
  "data": {
    "id": 124,
    "title": "GPT-6 Released",
    "tier": "A"
  },
  "timestamp": "2025-10-30T12:00:00Z"
}
```

## Best Practices

✅ **Do**:
- Cache responses (respect `Cache-Control`)
- Use cursor pagination for large datasets
- Handle rate limits gracefully (exponential backoff)
- Include User-Agent header with contact info
- Check API status before relying on data

❌ **Don't**:
- Poll more than once per minute (wasteful)
- Ignore pagination (max 100 items per request)
- Scrape the web UI (use API instead)
- Assume data is real-time (updates daily)
- Share admin API keys publicly

## Troubleshooting

### CORS Errors (Browser)

**Symptom**: `Access to fetch... has been blocked by CORS policy`

**Cause**: Browser security prevents cross-origin requests

**Fix**:
- Make API calls from your backend (not browser)
- Or contact admin to whitelist your domain

### "Invalid tier parameter"

**Symptom**: `400 Bad Request: tier must be one of: A, B, C, D`

**Cause**: Typo in tier value (lowercase `a` instead of `A`)

**Fix**: Use uppercase: `tier=A` not `tier=a`

### Empty Results Despite Data Existing

**Symptom**: `{"events": [], "has_more": false}`

**Cause**: Filters too restrictive or cache stale

**Fix**:
- Remove some filters
- Add `Cache-Control: no-cache` header
- Check web UI to verify data exists

## Next Steps

- [API Reference](/docs/api/endpoints) - Full endpoint documentation
- [Events Feed Guide](/docs/guides/events-feed) - Understanding event data
- [Signpost Deep-Dives](/docs/guides/signpost-deep-dives) - Milestone definitions

## Support

- **API Docs**: https://agitracker-production-6efa.up.railway.app/docs
- **Status Page**: https://status.agi-tracker.dev (planned)
- **GitHub Issues**: Report bugs and request features
- **Email**: api@agi-tracker.dev

---

**License**: Data is CC BY 4.0. API is free for non-commercial use. Contact for commercial licensing.

