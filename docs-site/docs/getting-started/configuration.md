# Configuration

Learn how to configure the AGI Tracker for different environments.

## Environment Variables

The AGI Tracker uses environment variables for configuration. All settings are stored in `.env` files.

### Backend Configuration

Located in: `services/etl/.env`

```env
# ===== Database =====
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/agi_signpost_tracker

# ===== Redis =====
REDIS_URL=redis://localhost:6379/0

# ===== OpenAI API =====
OPENAI_API_KEY=sk-proj-your-key-here
LLM_BUDGET_DAILY_USD=20  # Daily spend limit

# ===== Authentication =====
API_KEY=your-admin-api-key-change-in-production

# ===== CORS =====
CORS_ORIGINS=http://localhost:3000,https://agi-tracker.vercel.app

# ===== Optional: Observability =====
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
LOG_LEVEL=INFO  # DEBUG | INFO | WARNING | ERROR

# ===== Optional: External APIs =====
HEALTHCHECKS_URL=https://hc-ping.com/your-uuid
```

### Frontend Configuration

Located in: `apps/web/.env.local`

```env
# API base URL (auto-detected if not set)
NEXT_PUBLIC_API_URL=http://localhost:8000

# Optional: Sentry for error tracking
NEXT_PUBLIC_SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
```

## Database Configuration

### Local Development (Docker)

Use the default connection string:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/agi_signpost_tracker
```

### Production (Neon / Managed Postgres)

1. Create a PostgreSQL 15+ database
2. Enable pgvector extension:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

3. Update connection string:

```env
DATABASE_URL=postgresql://user:password@host:5432/dbname?sslmode=require
```

### Connection Pool Settings

For high-traffic deployments, use connection pooling:

```env
# PgBouncer or pgpool
DATABASE_URL=postgresql://user:password@pooler-host:5432/dbname?sslmode=require

# SQLAlchemy pool settings (optional)
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10
```

## Redis Configuration

### Local Development

```env
REDIS_URL=redis://localhost:6379/0
```

### Production (Upstash / Redis Cloud)

```env
REDIS_URL=rediss://default:password@host:6379
```

## OpenAI API Configuration

### API Key

Get your API key from [platform.openai.com/api-keys](https://platform.openai.com/api-keys)

```env
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Budget Management

The tracker uses two budget thresholds:

```env
LLM_BUDGET_DAILY_USD=20  # Warning threshold
# Hard stop at $50/day (hardcoded)
```

**How it works**:
- Tracks daily spend in Redis: `llm_budget:daily:{YYYY-MM-DD}`
- Warning logged at $20
- Tasks gracefully degrade (skip analysis) at $50
- Resets at midnight UTC

### Model Selection

Configured in code (`services/etl/app/config.py`):

```python
# Event analysis (cheap, fast)
EVENT_ANALYSIS_MODEL = "gpt-4o-mini"

# Complex mapping (expensive, accurate)
MAPPING_MODEL = "gpt-4o"
```

## CORS Configuration

### Development

Allow localhost:

```env
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Production

Add your production domains:

```env
CORS_ORIGINS=https://agi-tracker.vercel.app,https://docs.agi-tracker.vercel.app
```

**Security**: Never use `*` in production. Always specify exact origins.

## API Key Configuration

### Admin API Key

Used for protected endpoints (`/v1/admin/*`):

```env
API_KEY=your-secure-random-key-at-least-32-chars
```

**Generate a secure key**:

```bash
openssl rand -hex 32
```

### User API Keys

Managed via the admin UI at `/admin/api-keys`:

- **Public**: No key required (60 req/min)
- **Authenticated**: API key (300 req/min)
- **Admin**: Admin key (unlimited)

## Logging Configuration

### Log Level

```env
LOG_LEVEL=INFO  # DEBUG | INFO | WARNING | ERROR
```

- **DEBUG**: Verbose logs for development
- **INFO**: Standard logs (default)
- **WARNING**: Only warnings and errors
- **ERROR**: Only errors

### Structured Logging

Logs are JSON-formatted for easy parsing:

```json
{
  "timestamp": "2025-10-29T12:34:56Z",
  "level": "INFO",
  "message": "Event analysis completed",
  "event_id": 123,
  "duration_ms": 450
}
```

## Observability Configuration

### Sentry (Error Tracking)

```env
# Backend
SENTRY_DSN=https://xxx@sentry.io/123

# Frontend
NEXT_PUBLIC_SENTRY_DSN=https://xxx@sentry.io/456
```

### Healthchecks.io (Uptime Monitoring)

```env
HEALTHCHECKS_URL=https://hc-ping.com/your-uuid
```

Celery tasks ping this URL after each successful run.

## Celery Configuration

### Broker and Backend

Uses Redis for both:

```python
# services/etl/app/celery_app.py
broker_url = os.getenv("REDIS_URL")
result_backend = os.getenv("REDIS_URL")
```

### Task Schedules

Configured in `services/etl/app/celery_app.py`:

```python
beat_schedule = {
    "fetch-feeds-daily": {
        "task": "app.tasks.fetch_feeds.fetch_all",
        "schedule": crontab(hour=6, minute=0),  # 6 AM UTC
    },
    "compute-snapshots-daily": {
        "task": "app.tasks.snap_index.compute_snapshots",
        "schedule": crontab(hour=7, minute=0),  # 7 AM UTC
    },
    # ... more tasks
}
```

## Docker Compose Configuration

Located in: `docker-compose.dev.yml`

### PostgreSQL

```yaml
postgres:
  image: pgvector/pgvector:pg15
  environment:
    POSTGRES_USER: postgres
    POSTGRES_PASSWORD: postgres
    POSTGRES_DB: agi_signpost_tracker
  ports:
    - "5432:5432"
  volumes:
    - postgres_data:/var/lib/postgresql/data
```

### Redis

```yaml
redis:
  image: redis:7-alpine
  ports:
    - "6379:6379"
  volumes:
    - redis_data:/data
```

## Production Configuration Checklist

Before deploying to production:

- [ ] Change `API_KEY` to a secure random value
- [ ] Set `DATABASE_URL` to production database
- [ ] Set `REDIS_URL` to production Redis
- [ ] Add `OPENAI_API_KEY` (required)
- [ ] Configure `CORS_ORIGINS` with production domains
- [ ] Set `SENTRY_DSN` for error tracking
- [ ] Set `LOG_LEVEL=WARNING` (reduce noise)
- [ ] Enable SSL for database (`?sslmode=require`)
- [ ] Set `LLM_BUDGET_DAILY_USD` to reasonable limit
- [ ] Configure `HEALTHCHECKS_URL` for monitoring

## Configuration by Environment

### Development

Optimized for fast iteration:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/agi_signpost_tracker
REDIS_URL=redis://localhost:6379/0
LOG_LEVEL=DEBUG
CORS_ORIGINS=http://localhost:3000
```

### Staging

Test production settings:

```env
DATABASE_URL=postgresql://user:pass@staging-db:5432/dbname?sslmode=require
REDIS_URL=rediss://default:pass@staging-redis:6379
LOG_LEVEL=INFO
CORS_ORIGINS=https://staging.agi-tracker.vercel.app
SENTRY_DSN=https://xxx@sentry.io/staging
```

### Production

Maximum security and observability:

```env
DATABASE_URL=postgresql://user:pass@prod-db:5432/dbname?sslmode=require
REDIS_URL=rediss://default:pass@prod-redis:6379
LOG_LEVEL=WARNING
CORS_ORIGINS=https://agi-tracker.vercel.app
SENTRY_DSN=https://xxx@sentry.io/prod
API_KEY=<64-char-random-hex>
LLM_BUDGET_DAILY_USD=50
```

## Verifying Configuration

### Check Backend Config

```bash
# Start Python shell
cd services/etl
python

>>> from app.config import get_settings
>>> settings = get_settings()
>>> print(f"API Key set: {'API_KEY' in settings.dict()}")
>>> print(f"Database: {settings.database_url}")
```

### Check Frontend Config

Visit http://localhost:3000/_debug to see:
- Resolved API base URL
- CORS configuration
- Health check results

## Environment Variable Precedence

1. **OS environment variables** (highest priority)
2. **`.env.local`** (local overrides, gitignored)
3. **`.env`** (committed defaults)
4. **Hardcoded defaults** in code (lowest priority)

## Next Steps

- [Take Your First Steps](/docs/getting-started/first-steps)
- [Explore Architecture](/docs/architecture/overview)
- [Deploy to Production](/docs/deployment/production)

