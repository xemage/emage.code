---
description: "Use for proof-of-concept workstreams where speed and hypothesis validation are primary goals. Enforces mandatory debt tracking, hypothesis-first validation, and debt scorecards."
applyTo: "**"
maturity: stable
---

# PoC Guidelines

## Rails
**Inputs**: Triggers on `**` — applies whenever `poc-orchestrator` or a PoC
specialist agent begins hypothesis-driven exploratory work, per
`poc-orchestrator.md`'s Plan Phase, which restates the hypothesis before any
task is created.

**Out of scope**: Does not apply to production-track work — see
`git-workflow.md` and `coding-standards.md` for that track's rules instead.
Does not waive the Immutable Security Constraints in `security-guidelines.md`
(no exposed secrets, no real PII in demos) merely because a workstream is
time-boxed.

**Failure mode**: A PoC that starts implementation without a documented
hypothesis, or that is closed without a finalized Debt Scorecard, violates
this instruction's own "Not Allowed" list; per the Debt Scorecard Rules, "No
PoC task may be marked complete without a finalized scorecard" — an
incomplete scorecard blocks the PoC's own completion, not merely a warning.

## Primary Goal
Validate the target hypothesis quickly and clearly.

## Hypothesis-First Validation

Every PoC must begin with a clearly stated hypothesis before any code is written.

### Hypothesis Format
```
HYPOTHESIS: [What we believe]
VALIDATION: [How we will prove/disprove it]
SUCCESS CRITERIA: [Measurable outcome that confirms the hypothesis]
FAILURE CRITERIA: [Measurable outcome that disproves the hypothesis]
```

### Example
```
HYPOTHESIS: WebSocket-based real-time sync can maintain <100ms latency
             with 50 concurrent users on a single server instance.
VALIDATION: Build minimal WebSocket server with echo test, measure p95 latency
            under simulated 50-user load using k6.
SUCCESS CRITERIA: p95 latency < 100ms over a 5-minute sustained test
FAILURE CRITERIA: p95 latency > 200ms OR connection drops > 1%
```

### Rules
1. **No code before hypothesis** — The hypothesis must be documented before implementation starts
2. **One hypothesis per PoC** — Keep scope tight. If multiple hypotheses emerge, split into separate PoCs
3. **Time-box strictly** — Every PoC has a hard deadline. If the hypothesis isn't validated by the deadline, it fails
4. **Binary outcome** — A PoC either validates or invalidates the hypothesis. "Partially validated" requires a follow-up PoC with refined criteria

## Priorities
1. Demonstrability over completeness
2. Feasibility evidence over architecture perfection
3. Fast iteration over broad scope

## Allowed Shortcuts
- Narrow test coverage to happy path
- Minimal infrastructure setup
- Temporary integration adapters

Shortcuts may simplify how security controls are built but never remove or weaken them. Every rule in `security-guidelines.md` applies to PoC code, and its Immutable Security Constraints apply in full; Constraint 3 holds "even in development or PoC mode": input validation, authentication checks and security middleware stay in place and stay enforced. What may be simplified is how a control is built, not what it enforces: for example, hand-written validation checks instead of a schema library, or a CORS allowlist hardcoded to the one demo origin. Tag the simplification like any other shortcut. A `POC-DEBT` tag records a shortcut; it does not make a forbidden shortcut permissible.

## Mandatory Debt Tracking

Every shortcut taken during a PoC **must** be tracked. Untracked debt is unacceptable — it becomes invisible and compounds.

### Inline Debt Tags
When introducing a shortcut in code, mark it with an HTML comment tag:

```
<!-- POC-DEBT: description of the shortcut and what the production version needs -->
```

### Examples
```python
# <!-- POC-DEBT: Hardcoded local database URL (no credentials in it); production must read the URL from configuration and the credentials from the secret vault. The local Postgres must run with TLS enabled; the CA certificate is loaded from libpq's default location or PGSSLROOTCERT, never committed -->
db_url = "postgresql://localhost:5432/poc_db?sslmode=verify-full"

import re

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]{1,64}@[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,63}")

# <!-- POC-DEBT: Hand-written inline validation instead of the shared request-schema layer; production must move these checks into the schema layer and return the project's standard validation error response; keep inserting only allowlisted fields (never pass the request object through), via parameterized queries -->
def create_user(name, email):
    if not (isinstance(name, str) and 1 <= len(name) <= 100 and name.isprintable() and name.strip()):
        log.warning("input_rejected", extra={"field": "name"})
        raise ValueError("invalid name")
    if not (isinstance(email, str) and len(email) <= 254 and EMAIL_RE.fullmatch(email)):
        log.warning("input_rejected", extra={"field": "email"})
        raise ValueError("invalid email")
    return db.insert({"name": name, "email": email})

# external_api_url is fixed HTTPS configuration, never user input (OWASP A10, SSRF)
# <!-- POC-DEBT: Synchronous call with no retry; production should use async with retry. The response is validated before use, in the PoC as in production -->
response = requests.post(external_api_url, json=payload, timeout=10)
```

### Debt Tag Rules
1. Every `POC-DEBT` tag must describe **what** the shortcut is and **what** the production solution needs
2. Tags must be placed directly adjacent to the shortcut code (same line or line above)
3. Generic tags like `<!-- POC-DEBT: fix later -->` are not acceptable — be specific
4. Debt tags must also be registered in the debt scorecard (see below)

## Debt Scorecard

Before a PoC can be marked as complete, a **debt scorecard** must be produced. This is a summary document that inventories all shortcuts taken.

### Scorecard Format
Create a `POC-DEBT-SCORECARD.md` file in the PoC root with this structure:

```markdown
# PoC Debt Scorecard

## Hypothesis
[Copy the hypothesis from the PoC definition]

## Result
[VALIDATED / INVALIDATED]

## Debt Inventory

| # | File | Line | Category | Description | Production Effort |
|---|------|------|----------|-------------|-------------------|
| 1 | src/db.py | 12 | Security | Hardcoded local database URL (no credentials) | S — read URL from configuration, credentials from vault |
| 2 | src/api.py | 34 | Validation | Hand-written inline input validation instead of the shared schema layer | M — move checks into the request-schema layer |
| 3 | src/sync.py | 56 | Reliability | No retry logic | M — add retry with backoff |

## Summary
- Total debt items: N
- Critical (must fix before production): X
- Medium (should fix before production): Y
- Low (nice to have): Z

## Recommendation
[Go / No-Go for production implementation, with conditions]
```

### Scorecard Rules
1. The scorecard must account for **every** `POC-DEBT` tag in the codebase
2. Each item must have an estimated production effort: `S` (small), `M` (medium), `L` (large)
3. The scorecard must be reviewed by the Tech Lead before the PoC is closed
4. No PoC task may be marked complete without a finalized scorecard

## Required Debt Marking (Legacy)
When introducing shortcuts, document them with `DEBT:` comments and update `TECHNICAL-DEBT.md`.

> **Note:** The `POC-DEBT` tag format above supersedes the legacy `DEBT:` comment format. Use `POC-DEBT` tags for all new PoC work.

## Not Allowed
- Exposing secrets in code
- Using real PII in demos
- Removing or weakening any security control in `security-guidelines.md` — including every Immutable Security Constraint — with or without a `POC-DEBT` tag
- Claiming production readiness without explicit criteria
- Marking a PoC complete without a debt scorecard
- Starting implementation without a documented hypothesis
