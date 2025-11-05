# Security Policy

## Reporting a Vulnerability

**Please do NOT create a public GitHub issue for security vulnerabilities.**

### How to Report

**Email**: security@agi-tracker.app (or contact@agi-tracker.app if dedicated security email not set up)

**Please include**:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if you have one)

### What to Expect

**Response Time**: Within 48 hours
- We'll acknowledge receipt
- Assess severity and impact
- Provide an initial timeline for fix

**Disclosure Window**: 90 days
- We aim to fix critical issues within 7 days
- High severity within 30 days
- Medium/Low within 90 days
- Coordinated disclosure after fix is deployed

**Credit**: Security researchers will be credited in:
- CHANGELOG.md
- Security advisory (if applicable)
- Hall of fame section (if we create one)

## Security Posture

**Last Audit**: November 2025 (2x independent GPT-5 Pro reviews)

**Current Status**: Production-hardened
- All P0 critical issues resolved
- Full-stack monitoring (Sentry)
- See [docs/SECURITY_AUDIT.md](../docs/SECURITY_AUDIT.md) for details

**Bug Bounty**: Not currently offered (may add for public launch)

## Supported Versions

| Version | Supported | Notes |
|---------|-----------|-------|
| main branch | ✅ Yes | Production deployment |
| < 1.0 | ❌ No | Pre-release development |

## Known Security Considerations

### Authentication
- Admin endpoints protected by API key (constant-time comparison)
- Rate limiting on auth endpoints
- No user accounts (public read-only API)

### Data Privacy
- No user PII collected
- Sentry monitoring configured with PII scrubbing
- All data from public sources (arXiv, company blogs)

### Infrastructure
- Deployment: Vercel (web), Railway (API)
- Database: Neon PostgreSQL (managed, encrypted)
- Secrets: Railway/Vercel environment variables

## Security Features

- ✅ XSS Prevention (URL sanitization, React escaping)
- ✅ CSRF Protection (SameSite cookies, CORS policies)
- ✅ SQL Injection Prevention (SQLAlchemy ORM, parameterized queries)
- ✅ CSV Injection Prevention (Formula character escaping)
- ✅ Rate Limiting (Per-IP, per-endpoint)
- ✅ Security Headers (CSP, HSTS, X-Frame-Options, etc.)
- ✅ Dependency Scanning (Dependabot enabled)

## Contact

For security concerns: security@agi-tracker.app  
For general issues: https://github.com/hankthevc/AGITracker/issues

