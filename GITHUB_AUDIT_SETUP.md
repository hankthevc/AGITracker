# GitHub Audit Mirror Setup Guide

**Problem**: ChatGPT/GPT-5 Pro cannot access private repositories for code verification.

**Solution**: Automatically publish a sanitized audit snapshot to a public mirror repository.

---

## Setup Instructions

### 1. Create Public Mirror Repository

1. Go to https://github.com/new
2. Repository name: `AGITracker-audit-mirror`
3. Description: "Public audit snapshot for security verification"
4. Visibility: **Public**
5. Initialize with README: No (workflow will create it)
6. Click "Create repository"

### 2. Create Fine-Grained Personal Access Token

1. Go to https://github.com/settings/tokens?type=beta
2. Click "Generate new token"
3. Token name: `AGI Tracker Audit Mirror`
4. Expiration: 90 days (or custom)
5. Repository access: **Only select repositories**
   - Select: `AGITracker-audit-mirror`
6. Repository permissions:
   - **Contents**: Read and write ✅
7. Click "Generate token"
8. **Copy the token immediately** (you won't see it again)

### 3. Add Secret to Private Repository

1. Go to https://github.com/hankthevc/AGITracker/settings/secrets/actions
2. Click "New repository secret"
3. Name: `GH_MIRROR_TOKEN`
4. Secret: Paste the token from step 2
5. Click "Add secret"

### 4. Commit and Push Workflow

The workflow file has been created at:
`.github/workflows/publish-audit-snapshot.yml`

Commit and push it:
```bash
git add .github/workflows/publish-audit-snapshot.yml
git commit -m "ci: add public audit mirror workflow for GPT-5 verification"
git push origin main
```

### 5. Verify Workflow Runs

1. Go to https://github.com/hankthevc/AGITracker/actions
2. You should see "Publish audit snapshot to public mirror" running
3. Wait for green checkmark ✅
4. Visit https://github.com/hankthevc/AGITracker-audit-mirror
5. You should see the sanitized snapshot

---

## What Gets Published

### ✅ Included (Safe for Public)
- All database migrations (no secrets)
- Frontend security code (SafeLink, CSP config)
- Test suites (SafeLink, seeds, audit)
- Backend security utilities (audit logging, auth structure)
- CI/CD workflows
- Documentation (engineering, security, methodology)
- README and top-level docs

### ❌ Excluded (Private)
- Environment variables (.env files)
- API keys and secrets
- Production database connection strings
- Sentry DSN and tokens
- Railway/Vercel deployment configs
- Private business logic
- User data or analytics

---

## Usage for GPT-5 Pro Audits

### Before (Requires ZIP Upload)
```
User: Creates ZIP manually
User: Uploads to ChatGPT
GPT-5: Extracts and audits
```

### After (Direct Code Access)
```
User: Pushes to main
GitHub: Auto-publishes to mirror
GPT-5: Reads mirror directly at https://github.com/hankthevc/AGITracker-audit-mirror
```

### Example Audit Request
```
Please audit the AGI Tracker codebase at:
https://github.com/hankthevc/AGITracker-audit-mirror

Specifically verify:
1. Migration 030 exists and is forward-only
2. Zero raw external <a> tags in apps/web/
3. CSP removes unsafe-inline in production
4. Seed validator passes

The mirror is auto-updated on every push to main.
```

---

## Maintenance

### Token Renewal
- Token expires in 90 days
- GitHub will email you 7 days before expiration
- Regenerate token and update `GH_MIRROR_TOKEN` secret

### Updating Snapshot Contents
Edit `.github/workflows/publish-audit-snapshot.yml` to add/remove files.

### Manual Trigger
You can manually trigger the workflow:
1. Go to https://github.com/hankthevc/AGITracker/actions/workflows/publish-audit-snapshot.yml
2. Click "Run workflow"
3. Select branch: main
4. Click "Run workflow"

---

## Security Notes

- ✅ Mirror contains **no secrets** (all sensitive data excluded)
- ✅ Workflow uses fine-grained token (minimal permissions)
- ✅ Token only has access to mirror repo (not main repo)
- ✅ Workflow runs in isolated GitHub Actions environment
- ✅ rsync --delete ensures old files are removed

---

## Troubleshooting

### Workflow Fails with "Permission denied"
- Verify `GH_MIRROR_TOKEN` secret is set
- Check token has "Contents: Read and write" permission
- Ensure token hasn't expired

### Mirror Repository Empty
- Check workflow logs in Actions tab
- Verify rsync command succeeded
- Manually trigger workflow to test

### GPT-5 Still Can't Access
- Verify mirror repository is **Public** (not Private)
- Check repository URL is correct
- Try accessing mirror in incognito browser

---

## Benefits

1. **Real-time audits**: GPT-5 can verify code on every push
2. **No manual uploads**: Workflow runs automatically
3. **Deterministic**: Mirror always matches latest main
4. **Transparent**: Public snapshot builds trust
5. **Secure**: No secrets or sensitive data exposed

---

**Status**: Workflow ready to deploy  
**Next Step**: Complete steps 1-4 above to enable GPT-5 direct access

