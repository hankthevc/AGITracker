# API Quick Reference

Fast lookup for AGI Tracker API endpoints.

## Base URL

```
Production: https://agitracker-production-6efa.up.railway.app
Local:      http://localhost:8000
```

## Authentication

| Tier | Header | Rate Limit |
|------|--------|------------|
| Public | None | 60 req/min |
| Authenticated | `x-api-key: your-key` | 300 req/min |
| Admin | `x-api-key: admin-key` | Unlimited |

## Quick Examples

```bash
# Get current AGI proximity index
curl https://agitracker-production-6efa.up.railway.app/v1/index

# Get recent A-tier events
curl "https://agitracker-production-6efa.up.railway.app/v1/events?tier=A&limit=10"

# Search for events
curl "https://agitracker-production-6efa.up.railway.app/v1/search?q=GPT-5"

# Get all signposts
curl https://agitracker-production-6efa.up.railway.app/v1/signposts
```

## Core Endpoints

### Index & Scores

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/v1/index` | GET | Public | Current AGI proximity scores |
| `/v1/index?preset=aschenbrenner` | GET | Public | Index with specific preset |
| `/v1/index?date=2025-10-01` | GET | Public | Historical snapshot |

**Example**:
```bash
curl "https://agitracker-production-6efa.up.railway.app/v1/index?preset=equal"
```

**Response**:
```json
{
  "as_of_date": "2025-10-29",
  "preset": "equal",
  "overall": 0.45,
  "capabilities": 0.68,
  "agents": 0.12,
  "inputs": 0.78,
  "security": 0.05
}
```

---

### Events

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/v1/events` | GET | Public | List events with pagination |
| `/v1/events?tier=A` | GET | Public | Filter by evidence tier |
| `/v1/events?since=2025-10-01` | GET | Public | Events after date |
| `/v1/events?category=capabilities` | GET | Public | Filter by category |
| `/v1/events?min_significance=0.8` | GET | Public | High-impact events |
| `/v1/events/{id}` | GET | Public | Single event details |

**Example**:
```bash
curl "https://agitracker-production-6efa.up.railway.app/v1/events?tier=A&tier=B&limit=20"
```

**Response**:
```json
{
  "events": [
    {
      "id": 123,
      "title": "GPT-5 Achieves 85% on SWE-bench",
      "published_at": "2025-10-15T00:00:00Z",
      "evidence_tier": "A",
      "source_url": "https://openai.com/research/gpt-5"
    }
  ],
  "next_cursor": "MjAyNS0xMC0xNVQwMDowMDowMHwxMjM=",
  "has_more": true
}
```

---

### Search

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/v1/search?q={query}` | GET | Public | Full-text search |
| `/v1/search?q={query}&tier=A` | GET | Public | Search with tier filter |

**Example**:
```bash
curl "https://agitracker-production-6efa.up.railway.app/v1/search?q=reasoning&limit=10"
```

**Response**:
```json
{
  "query": "reasoning",
  "results": [
    {
      "id": 124,
      "title": "Chain-of-Thought Reasoning Breakthrough",
      "match_score": 0.95,
      "evidence_tier": "A"
    }
  ]
}
```

---

### Signposts

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/v1/signposts` | GET | Public | List all signposts |
| `/v1/signposts?category=capabilities` | GET | Public | Filter by category |
| `/v1/signposts?first_class=true` | GET | Public | First-class signposts only |
| `/v1/signposts/{id}` | GET | Public | Single signpost details |
| `/v1/signposts/by-code/{code}` | GET | Public | Get by code (e.g., swebench_70) |
| `/v1/signposts/by-code/{code}/events` | GET | Public | Linked events |
| `/v1/signposts/by-code/{code}/predictions` | GET | Public | Expert predictions |

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
      "current_value": 0.523,
      "progress": 0.685
    }
  ]
}
```

---

### Predictions

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/v1/predictions` | GET | Public | All expert predictions |
| `/v1/predictions?source=ai2027` | GET | Public | Filter by source |
| `/v1/predictions/compare` | GET | Public | Compare predictions vs actual |
| `/v1/predictions/surprise-score` | GET | Public | Calculate surprise scores |

**Example**:
```bash
curl https://agitracker-production-6efa.up.railway.app/v1/predictions/compare
```

---

### Digests

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/v1/digests/latest` | GET | Public | Latest weekly digest |
| `/v1/digests/{year}/{week}` | GET | Public | Specific week digest |

**Example**:
```bash
curl https://agitracker-production-6efa.up.railway.app/v1/digests/latest
```

---

### Health & Status

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/health` | GET | Public | Basic health check |
| `/health/full` | GET | Admin | Detailed system status |

**Example**:
```bash
curl https://agitracker-production-6efa.up.railway.app/health
```

**Response**:
```json
{
  "status": "ok",
  "service": "agi-tracker-api",
  "version": "1.0.0"
}
```

---

## Admin Endpoints

Require `x-api-key: admin-key` header.

### API Keys

| Endpoint | Method | Description |
|----------|--------|-------------|
| `POST /v1/admin/api-keys` | POST | Create new API key |
| `GET /v1/admin/api-keys` | GET | List all keys |
| `DELETE /v1/admin/api-keys/{id}` | DELETE | Revoke key |
| `GET /v1/admin/api-keys/usage` | GET | Usage statistics |

**Example**:
```bash
curl -X POST https://agitracker-production-6efa.up.railway.app/v1/admin/api-keys \
  -H "x-api-key: $ADMIN_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": "Research Key", "tier": "authenticated"}'
```

---

### Event Review

| Endpoint | Method | Description |
|----------|--------|-------------|
| `GET /v1/admin/review/queue` | GET | Pending review items |
| `POST /v1/admin/events/{id}/approve` | POST | Approve mapping |
| `POST /v1/admin/events/{id}/reject` | POST | Reject mapping |

**Example**:
```bash
curl http://localhost:8000/v1/admin/review/queue \
  -H "x-api-key: $ADMIN_API_KEY"
```

---

### URL Validation

| Endpoint | Method | Description |
|----------|--------|-------------|
| `POST /v1/admin/validate-urls` | POST | Validate all event URLs |
| `POST /v1/admin/validate-url/{id}` | POST | Validate specific event |
| `GET /v1/admin/invalid-urls` | GET | List invalid URLs |
| `GET /v1/admin/url-stats` | GET | Validation statistics |

**Example**:
```bash
curl -X POST http://localhost:8000/v1/admin/validate-urls \
  -H "x-api-key: $ADMIN_API_KEY"
```

---

### Retractions

| Endpoint | Method | Description |
|----------|--------|-------------|
| `POST /v1/admin/retract` | POST | Retract an event |
| `GET /v1/admin/source-credibility` | GET | Source credibility scores |

**Example**:
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

---

### Manual Triggers

| Endpoint | Method | Description |
|----------|--------|-------------|
| `POST /v1/admin/recompute` | POST | Recompute all indexes |
| `POST /v1/admin/tasks/{task_name}` | POST | Trigger specific task |

**Example**:
```bash
curl -X POST http://localhost:8000/v1/admin/recompute \
  -H "x-api-key: $ADMIN_API_KEY"
```

---

## Query Parameters Reference

### Common Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `limit` | int | Max results (default: 50, max: 100) | `?limit=20` |
| `skip` | int | Offset pagination (deprecated, use cursor) | `?skip=50` |
| `cursor` | string | Cursor for pagination | `?cursor=abc123` |

### Event Filters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `tier` | string | Evidence tier (A/B/C/D, multiple allowed) | `?tier=A&tier=B` |
| `since` | date | Events after date (YYYY-MM-DD) | `?since=2025-10-01` |
| `category` | string | Signpost category | `?category=capabilities` |
| `min_significance` | float | Minimum significance score (0.0-1.0) | `?min_significance=0.8` |
| `retracted` | bool | Include/exclude retracted | `?retracted=false` |

### Signpost Filters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `category` | string | Category filter | `?category=capabilities` |
| `first_class` | bool | First-class only | `?first_class=true` |

### Index Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `preset` | string | Weighting scheme (equal/aschenbrenner/ai2027) | `?preset=aschenbrenner` |
| `date` | date | Historical snapshot (YYYY-MM-DD) | `?date=2025-10-15` |

---

## Response Format

All endpoints return JSON with consistent structure:

### Success Response

```json
{
  "data": { ... },
  "metadata": {
    "total_count": 847,
    "next_cursor": "abc123",
    "has_more": true
  }
}
```

### Error Response

```json
{
  "error": "Invalid parameter: tier",
  "detail": "tier must be one of: A, B, C, D",
  "code": "INVALID_PARAMETER"
}
```

---

## HTTP Status Codes

| Code | Meaning | Action |
|------|---------|--------|
| 200 | Success | Process response |
| 304 | Not Modified | Use cached data |
| 400 | Bad Request | Fix query parameters |
| 401 | Unauthorized | Check API key |
| 404 | Not Found | Check endpoint URL |
| 429 | Rate Limited | Wait and retry |
| 500 | Server Error | Retry with backoff |

---

## Rate Limits

| Tier | Limit | Reset |
|------|-------|-------|
| Public | 60/min | Every minute |
| Authenticated | 300/min | Every minute |
| Admin | Unlimited | N/A |

**Headers**:
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 42
X-RateLimit-Reset: 1635532800
Retry-After: 18
```

---

## Caching

### Response Headers

```
Cache-Control: public, max-age=600
ETag: "abc123def456"
Last-Modified: Mon, 29 Oct 2025 12:00:00 GMT
```

### Conditional Requests

```bash
# First request
curl -I https://agitracker-production-6efa.up.railway.app/v1/index
# ETag: "abc123"

# Subsequent request
curl -H 'If-None-Match: "abc123"' \
  https://agitracker-production-6efa.up.railway.app/v1/index
# Returns 304 if unchanged
```

---

## Pagination

### Cursor-Based (Recommended)

```bash
# Page 1
curl "https://agitracker-production-6efa.up.railway.app/v1/events?limit=50"

# Response includes next_cursor
{
  "events": [...],
  "next_cursor": "MjAyNS0xMC0yOVQxMjowMDowMHwxMjM=",
  "has_more": true
}

# Page 2
curl "https://agitracker-production-6efa.up.railway.app/v1/events?cursor=MjAyNS0xMC0yOVQxMjowMDowMHwxMjM=&limit=50"
```

---

## Code Examples

### Python

```python
import requests

# Get index
response = requests.get(
    "https://agitracker-production-6efa.up.railway.app/v1/index",
    params={"preset": "aschenbrenner"}
)
print(response.json())

# Get events with API key
response = requests.get(
    "https://agitracker-production-6efa.up.railway.app/v1/events",
    headers={"x-api-key": "your-key"},
    params={"tier": "A", "limit": 10}
)
```

### JavaScript

```javascript
// Get index
const response = await fetch(
  "https://agitracker-production-6efa.up.railway.app/v1/index?preset=equal"
);
const data = await response.json();

// Get events with API key
const response = await fetch(
  "https://agitracker-production-6efa.up.railway.app/v1/events?tier=A",
  {
    headers: {
      "x-api-key": "your-key"
    }
  }
);
```

### cURL

```bash
# Get index
curl https://agitracker-production-6efa.up.railway.app/v1/index

# Get events with API key
curl -H "x-api-key: your-key" \
  "https://agitracker-production-6efa.up.railway.app/v1/events?tier=A"

# Search
curl "https://agitracker-production-6efa.up.railway.app/v1/search?q=GPT-5"
```

---

## Interactive Documentation

Full interactive API docs with "Try it out" functionality:

**Swagger UI**: https://agitracker-production-6efa.up.railway.app/docs

**ReDoc**: https://agitracker-production-6efa.up.railway.app/redoc

---

## Support

- **Full API Guide**: [/docs/guides/api-usage](/docs/guides/api-usage)
- **GitHub Issues**: Report bugs and request features
- **Email**: api@agi-tracker.dev

---

**Last Updated**: 2025-10-29  
**API Version**: v1  
**License**: Data is CC BY 4.0

