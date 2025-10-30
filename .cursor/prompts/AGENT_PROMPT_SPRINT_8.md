# Agent Prompt: Sprint 8 - Security & Compliance

**Status**: Ready for agent execution  
**Prerequisites**: ✅ Sprint 7 complete (live scraping, digests, multi-model, retraction UI)  
**Estimated Time**: 5-7 hours  
**Priority**: High - Production API needs security hardening

---

## 📋 Required Reading

Before starting, read these files for context:
1. `AGENT_TASKS_PHASE_2.md` - Full task breakdown (lines 538-620)
2. `PHASE_2_PROGRESS.md` - What's completed (Sprints 4-7)
3. `SPRINT_7_FINAL_STATUS.md` - Current infrastructure status

---

## 🎯 Your Mission

Implement ALL tasks in Sprint 8 from AGENT_TASKS_PHASE_2.md:

### Task 8.1: API Rate Limiting & Authentication

**Goal**: Protect API from abuse and prepare for public usage

**What needs to be done:**

1. **Enhance Rate Limiting**
   - Current: 120 req/min (SlowAPI) for all users
   - Add per-IP limits (different tiers)
   - Add API key-based limits (higher for authenticated)
   - Track usage per key in Redis

2. **API Key Management**
   - Add `/v1/admin/api-keys` CRUD endpoints:
     - `POST /v1/admin/api-keys` - Create new key
     - `GET /v1/admin/api-keys` - List all keys
     - `DELETE /v1/admin/api-keys/{key_id}` - Revoke key
   - Create `APIKey` table in database
   - Track usage stats per key
   - Auto-expire inactive keys after 90 days

3. **Public vs Authenticated Tiers**
   - **Public** (no key): 60 req/min, basic endpoints only
   - **Authenticated** (with key): 300 req/min, all endpoints
   - **Admin** (ADMIN_API_KEY): Unlimited, admin endpoints
   - Enforce in middleware

4. **Usage Dashboard**
   - Frontend page: `/admin/api-keys`
   - Show API usage stats
   - Top consumers
   - Rate limit violations
   - Error rates by endpoint
   - Create/revoke keys UI

**Success Metrics:**
- [ ] Rate limits enforced per IP and API key
- [ ] Admin can create/revoke keys via UI
- [ ] Usage tracked in Redis and displayed
- [ ] Public endpoints accessible without key
- [ ] Admin endpoints require ADMIN_API_KEY

**Files to create:**
- `services/etl/app/models.py` - Add `APIKey` table
- `services/etl/app/middleware/api_key_auth.py` - Enhanced auth middleware
- `apps/web/app/admin/api-keys/page.tsx` - Key management UI
- `infra/migrations/versions/add_api_keys_table.py` - Database migration

---

### Task 8.2: PII Scrubbing & GDPR Compliance

**Goal**: Ensure no personally identifiable information is stored or exposed

**What needs to be done:**

1. **Audit Data Storage**
   - Review all database tables for PII
   - Check: emails, names, IP addresses in logs
   - Document retention policies
   - Already done: Sentry scrubbing in `observability.py`

2. **Implement Additional Scrubbing**
   - Anonymize IP addresses in rate limiting (last octet = 0)
   - Remove/redact PII from error logs
   - Add PII detection to ingestion pipeline
   - Ensure no user data stored unnecessarily

3. **Privacy Policy & Terms**
   - Create `/legal/privacy` page
   - Create `/legal/terms` page
   - Add cookie consent banner component
   - Link in footer of all pages
   - Include:
     - What data we collect (none from users!)
     - How we use data (public research only)
     - No cookies/tracking
     - CC BY 4.0 license for data

4. **Data Retention**
   - Set TTL for logs (30 days)
   - Document data retention policy
   - Add automated cleanup task (optional for now)

**Success Metrics:**
- [ ] No PII stored in database (verify with audit)
- [ ] Privacy policy published and accessible
- [ ] Terms of service published
- [ ] Cookie consent working (even if not needed)
- [ ] GDPR compliant

**Files to create:**
- `apps/web/app/legal/privacy/page.tsx` - Privacy policy
- `apps/web/app/legal/terms/page.tsx` - Terms of service
- `apps/web/components/CookieConsent.tsx` - Cookie banner (optional)
- `services/etl/app/utils/pii_scrubber.py` - PII detection utilities

**Files to modify:**
- `apps/web/app/layout.tsx` - Add footer links to legal pages
- `services/etl/app/middleware/rate_limit.py` - Anonymize IPs

---

## 🚨 Critical Rules

1. **Work on main branch only** - NO PRs, NO feature branches
2. **Commit after each task** with descriptive messages
3. **Test after each commit** - verify API still works
4. **Update PHASE_2_PROGRESS.md** as you complete tasks
5. **If blocked, create BLOCKED_SPRINT_8.md** and continue with other tasks

---

## 🧪 Git Workflow

```bash
git checkout main
git pull origin main

# After each task:
git add -A
git commit -m "feat(sprint-8.X): description"
git push origin main
```

---

## 🧪 Testing Checklist

### After Task 8.1 (API Keys):
```bash
# Create an API key
curl -X POST https://agitracker-production-6efa.up.railway.app/v1/admin/api-keys \
  -H "x-api-key: $ADMIN_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": "test-key", "tier": "authenticated"}'

# Use the key to access API
curl https://agitracker-production-6efa.up.railway.app/v1/events \
  -H "x-api-key: [returned-key]"

# Test rate limiting
for i in {1..70}; do curl -s https://agitracker-production-6efa.up.railway.app/v1/events > /dev/null; done
# Should hit rate limit at 60 requests
```

### After Task 8.2 (Privacy/Terms):
```bash
# Visit legal pages
open https://agi-tracker.vercel.app/legal/privacy
open https://agi-tracker.vercel.app/legal/terms

# Verify footer links
open https://agi-tracker.vercel.app
# Check footer has links to Privacy and Terms
```

---

## 📊 Success Criteria

Sprint 8 is complete when:

- [ ] Task 8.1: API key system working (create, list, revoke)
- [ ] Rate limits enforced (60/min public, 300/min authenticated)
- [ ] Admin UI shows usage stats
- [ ] Task 8.2: Privacy policy published
- [ ] Terms of service published
- [ ] Footer links to legal pages
- [ ] No PII in database (verified)
- [ ] All committed to main
- [ ] Railway services still healthy
- [ ] API responding correctly

---

## 💰 Cost Implications

**Sprint 8 has minimal cost impact:**
- No additional LLM usage
- No additional infrastructure
- Existing Railway/Vercel services sufficient
- API key tracking uses existing Redis

**Total additional monthly cost**: $0

---

## 🎯 Implementation Tips

### Task 8.1: API Keys

**Use existing patterns:**
- `services/etl/app/models.py` - See how other tables are defined
- `services/etl/app/main.py` - See existing `/v1/admin/*` endpoints
- `apps/web/app/admin/tasks/page.tsx` - Similar admin dashboard pattern

**API Key Table Schema:**
```python
class APIKey(Base):
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True)
    key_hash = Column(String(64), unique=True, nullable=False)  # SHA-256 of key
    name = Column(String(255), nullable=False)
    tier = Column(Enum("public", "authenticated", name="api_key_tier"))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    last_used_at = Column(TIMESTAMP(timezone=True))
    is_active = Column(Boolean, default=True)
    usage_count = Column(Integer, default=0)
```

### Task 8.2: Privacy & Terms

**Use existing page patterns:**
- `apps/web/app/methodology/page.tsx` - Similar static content page
- Keep it simple: Markdown-style content in React
- Use shadcn/ui components for consistency

**Key points to cover:**
- **Privacy**: No user accounts, no tracking, no PII collected
- **Data**: All event data is public (CC BY 4.0)
- **Usage**: Fair use for research purposes
- **Contact**: Email for questions/concerns

---

## 🚀 Start Now

Begin with **Task 8.1** (API Rate Limiting & Authentication). Work through ALL tasks sequentially. Commit frequently. Test thoroughly.

When both tasks are complete, update `PHASE_2_PROGRESS.md` and create `SPRINT_8_COMPLETE.md`.

**Current Infrastructure Status**:
- Railway API: https://agitracker-production-6efa.up.railway.app ✅
- Frontend: https://agi-tracker.vercel.app ✅
- Database: 33 events, 34 signposts, 79 mappings ✅
- All services healthy ✅

**Good luck with Sprint 8!** 🔒

