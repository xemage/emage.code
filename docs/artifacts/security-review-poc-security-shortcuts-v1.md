# Security review: `poc-security-shortcut-examples-v1.md` (T576 / P42)

> Filename: `security-review-poc-security-shortcuts-v1.md`. Immutable once produced; a revision bumps `<N>`.

## Metadata

- **Reviewer**: security-engineer (read-only review; this agent has no write tools)
- **Recorded by**: orchestrator. This file transcribes the reviewer's hand-back on 2026-10-02, because the reviewer
  cannot write files.
- **Reviewed**: `docs/artifacts/poc-security-shortcut-examples-v1.md` (T576), against `security-guidelines.md`.
- **Outcome applied in**: `docs/artifacts/poc-security-shortcut-examples-v2.md`, which supersedes v1.

## Verdict: CONDITIONAL_PASS

| Severity | Count | Items |
|---|---|---|
| CRITICAL | 0 | — |
| HIGH | 1 | O1. It predates the ruling and is outside its scope (see below). |
| MEDIUM | 2 | F1, F2. Both are conditions for FU-1's dispatch. |
| LOW | 5 + 1 | F3, F4, F5, F6, F8, plus `rapid-prototyping:54`, which is out of scope. |

The ruling's direction is correct, and every change it makes is an improvement on today's text. R7 and R9 are fully
compliant. R2 and R8 are sound minimal validation and log no PII.

## Findings

- **F1 (MEDIUM): scope gap.** R4–R6 bind only the Immutable Security Constraints. CORS, parameterized queries, DB
  TLS, password hashing, rate limiting and security headers are not Immutable Constraints. The authority
  (`security-guidelines` Rails, "a security control") covers them all.
  - **Correction:** widen R4–R6 to "any security control in `security-guidelines.md`, including the Immutable
    Constraints".
  - **Wording:** "it does not permit one" becomes "it does not make a forbidden shortcut permissible".
- **F2 (MEDIUM): R1 used `sslmode=require`.** In libpq, `require` gives eavesdropping protection but no MITM
  protection; only `verify-full` gives both. So R1 weakened server authentication silently, contradicting R4. A
  default local Postgres runs with `ssl=off`, so `require` would fail to connect, and the obvious "fix" removes the
  control entirely.
  - **Correction:** use `sslmode=verify-full`. The tag says TLS must be enabled locally and the CA certificate is
    loaded from libpq's default location or `PGSSLROOTCERT`, never committed (Constraint 1 names certificates).
- **F3 (LOW):** `EMAIL_RE` was undefined. Define an allowlist pattern in the example.
- **F4 (LOW):** a whitespace-only name passed `isprintable()`. Add `and name.strip()`, and reject rather than trim.
- **F5 (LOW):** scorecard row 1 still presented the database URL itself as a secret. Align it with R1.
- **F6 (LOW):** state that only allowlisted fields are inserted (never the request object), via parameterized
  queries.
- **F8 (LOW):** the synchronous-call example has no timeout (Bandit B113; A04 resource exhaustion), and its response
  would be used unvalidated (Constraint 4).
  - **Correction:** add `timeout=10` and response validation. `external_api_url` stays fixed configuration, never user
    input (A10).
- **Out of scope (LOW):** `rapid-prototyping:54` treats an untagged shortcut as "🟡 Should Fix". An untagged removal
  of a security control should block. This is batched with O1.

## O1: SECURITY:HIGH (pre-existing; re-rated from the architect's "major")

The stable `poc-security-engineer` agent defers critical findings instead of blocking on them:
- `:19–20`: "Do not block progress by default / Record findings for debt handoff".
- `:47`, the Failure mode: "a critical risk (exposed secret, obvious injection/auth gap) … records it explicitly for
  debt handoff".

Related text compounds this:
- `:35` in the same agent: "prefer unblocking over perfection".
- `poc-orchestrator.md:53`, `:66` and `:114`: no text anywhere says that a critical PoC finding blocks.

This contradicts Immutable Constraint 1 ("not negotiable regardless of PoC status") and the Security Review Workflow
("CRITICAL and HIGH findings block merge"). A committed secret recorded as "debt" stays in git history unrotated.

**Rated HIGH rather than CRITICAL** because the text is not itself exploitable: it only matters once a secret or a
gap exists.

**Fix direction, which the reviewer did not write as text:**
- Keep "do not block by default" for non-critical findings only.
- Add an explicit carve-out: any breach of an Immutable Constraint, or any SECURITY:CRITICAL or HIGH finding, blocks
  the PoC and escalates to `@poc-orchestrator`. These findings never take the debt-handoff route.
- For an exposed secret, require revocation and rotation plus removal from history.
- Matching edits in `poc-orchestrator.md`:
  - state that critical findings block;
  - add a security exception to the speed directive;
  - consider moving the secrets scan earlier than step 9.

The reviewer asks that O1 get its own task rather than being parked, and that any release shipping the current text
be blocked until it is fixed.

## Reviewer's blocker (technical, minor)

The `security-audit` `grep_content` tool errored on every pattern, so the reviewer could not run the repository-wide
sweep for other forbidden examples. **The orchestrator ran it with a shell.** The only hits are
`rapid-prototyping:33,37,46` and `poc-guidelines:84,119`, all ruled. The `security-guidelines:157` hit is the
constraint itself.
