# Security Audit — user-profile-service

## OWASP Coverage Matrix

| # | OWASP Category | Status | Findings | Severity |
|---|---------------|--------|----------|----------|
| A01 | Broken Access Control | ✅ | none | - |
| A02 | Cryptographic Failures | ✅ | none | - |
| A03 | Injection | ✅ | none | - |
| A04 | Insecure Design | ✅ | none | - |
| A05 | Security Misconfiguration | ⚠️ | debug endpoint left enabled | LOW |
| A06 | Vulnerable Components | ✅ | none | - |
| A07 | Auth Failures | ✅ | none | - |
| A08 | Data Integrity Failures | ✅ | none | - |
| A09 | Logging & Monitoring | ⚠️ | no alert on repeated auth failures | MEDIUM |
| A10 | SSRF | ✅ | none | - |

## VERDICT

- **Status**: CONDITIONAL_PASS
- **CRITICAL findings**: 0
- **HIGH findings**: 0
- **MEDIUM findings**: 1
- **LOW findings**: 1
- **OWASP coverage**: 10/10 categories assessed
- **Blocker IDs**: none
- **Auditor**: security-engineer
- **Timestamp**: 2026-08-13T13:00:00Z

Conditions before deploy: add alerting on repeated auth failures (A09); disable debug endpoint
in production config (A05).
