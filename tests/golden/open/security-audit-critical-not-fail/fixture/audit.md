# Security Audit — legacy-export-endpoint

## OWASP Coverage Matrix

| # | OWASP Category | Status | Findings | Severity |
|---|---------------|--------|----------|----------|
| A01 | Broken Access Control | ❌ | export endpoint has no auth check | CRITICAL |
| A02 | Cryptographic Failures | ✅ | none | - |
| A03 | Injection | ✅ | none | - |
| A04 | Insecure Design | ✅ | none | - |
| A05 | Security Misconfiguration | ✅ | none | - |
| A06 | Vulnerable Components | ✅ | none | - |
| A07 | Auth Failures | ✅ | none | - |
| A08 | Data Integrity Failures | ✅ | none | - |
| A09 | Logging & Monitoring | ✅ | none | - |
| A10 | SSRF | ✅ | none | - |

## VERDICT

- **Status**: CONDITIONAL_PASS
- **CRITICAL findings**: 1
- **HIGH findings**: 0
- **MEDIUM findings**: 0
- **LOW findings**: 0
- **OWASP coverage**: 10/10 categories assessed
- **Blocker IDs**: SEC-CRIT-001 (unauthenticated export endpoint)
- **Auditor**: security-engineer
- **Timestamp**: 2026-08-13T14:00:00Z

Recommend fixing before next release; team elected to conditionally pass since a compensating
network-level restriction is in place today.
