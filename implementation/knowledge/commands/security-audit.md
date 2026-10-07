---
description: "Request a security audit of the project or specific components, checking for OWASP Top 10 vulnerabilities."
agent: "security-engineer"
argument-hint: "Specify scope: full project, specific feature, or files..."
maturity: stable
audience: both
---

Please perform a security audit on:

{{input}}

## Audit Scope

1. OWASP Top 10 compliance check
2. Authentication and authorization review
3. Input validation and injection prevention
4. Cryptographic implementation review
5. Secrets management verification
6. Dependency vulnerability scan
7. Security headers and configuration

## OWASP Coverage Matrix

8. **Produce an OWASP Top 10 coverage matrix**:

| # | OWASP Category | Status | Findings | Severity |
|---|---------------|--------|----------|----------|
| A01 | Broken Access Control | ✅/⚠️/❌ | ... | ... |
| A02 | Cryptographic Failures | ✅/⚠️/❌ | ... | ... |
| A03 | Injection | ✅/⚠️/❌ | ... | ... |
| A04 | Insecure Design | ✅/⚠️/❌ | ... | ... |
| A05 | Security Misconfiguration | ✅/⚠️/❌ | ... | ... |
| A06 | Vulnerable Components | ✅/⚠️/❌ | ... | ... |
| A07 | Auth Failures | ✅/⚠️/❌ | ... | ... |
| A08 | Data Integrity Failures | ✅/⚠️/❌ | ... | ... |
| A09 | Logging & Monitoring | ✅/⚠️/❌ | ... | ... |
| A10 | SSRF | ✅/⚠️/❌ | ... | ... |

## Severity Classification

9. Classify each finding with severity:
   - **CRITICAL**: Actively exploitable, immediate remediation required
   - **HIGH**: Exploitable with moderate effort; blocks merge until resolved (`security-guidelines.md` § Security Review Workflow)
   - **MEDIUM**: Potential risk; requires a remediation plan (owner, fix, deadline) before merge
   - **LOW**: Hardening recommendation, add to backlog

## Verdict Output

10. **Produce a structured VERDICT** at the end of the audit:

```
## VERDICT

- **Status**: PASS | CONDITIONAL_PASS | FAIL
- **CRITICAL findings**: <count>
- **HIGH findings**: <count>
- **MEDIUM findings**: <count>
- **LOW findings**: <count>
- **OWASP coverage**: <n>/10 categories assessed
- **Blocker IDs**: [if FAIL — list blocking findings]
- **Auditor**: security-engineer
- **Timestamp**: <ISO-8601>
```

Provide a structured security report with findings, severity levels, and remediation steps.
If any CRITICAL or HIGH finding exists, or any Immutable Security Constraint in `security-guidelines.md` is breached, or any security control that `security-guidelines.md` requires for the code under review is omitted, removed, disabled or weakened, the verdict MUST be FAIL (`security-guidelines.md` § Security Review Workflow: "`CRITICAL` and `HIGH` findings block merge until resolved"). A required control missing only from code outside the change under review is graded at its own severity. A change that adds or alters code which the missing control should protect is code under review for that control. With no change under review (for example a full-project `/security-audit`), the whole project is the code under review. If any MEDIUM finding exists, the verdict is at best CONDITIONAL_PASS, with a remediation plan (owner, fix, deadline) listed as a condition for each MEDIUM finding. PASS requires no CRITICAL, HIGH or MEDIUM finding.

## Rails

**Inputs**: The scope to audit (`{{input}}`: full project, a feature, or specific files).
**Out of scope**: Fixing any finding directly — this command only produces findings, severity, and remediation recommendations.
**Failure mode**: If any CRITICAL or HIGH finding exists, an Immutable Security Constraint is breached, or a security control that `security-guidelines.md` requires for the code under review is omitted, removed, disabled or weakened, the verdict MUST be FAIL — the command cannot return PASS/CONDITIONAL_PASS while such a finding is unresolved. With no change under review (for example a full-project `/security-audit`), the whole project is the code under review.
