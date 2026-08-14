# Security Audit — internal-admin-cli (scoped audit)

Scope: authentication and authorization paths only, per user request; not a full-project audit.

## OWASP Coverage Matrix

| # | OWASP Category | Status | Findings | Severity |
|---|---------------|--------|----------|----------|
| A01 | Broken Access Control | ✅ | none | - |
| A02 | Cryptographic Failures | ⚠️ | password reset token has short TTL margin | LOW |
| A07 | Auth Failures | ✅ | none | - |

## VERDICT

- **Status**: PASS
- **CRITICAL findings**: 0
- **HIGH findings**: 0
- **MEDIUM findings**: 0
- **LOW findings**: 1
- **OWASP coverage**: 3/10 categories assessed
- **Blocker IDs**: none
- **Auditor**: security-engineer
- **Timestamp**: 2026-08-13T15:00:00Z

Note: this was a scoped audit (auth paths only per user request); coverage is honestly reported
as 3/10, not padded to imply full-project coverage.
