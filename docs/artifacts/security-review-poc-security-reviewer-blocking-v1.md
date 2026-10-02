# Security review of `poc-security-reviewer-blocking-v1.md` (T578 / O1)

> Filename: `security-review-poc-security-reviewer-blocking-v1.md`. Immutable once produced; revisions bump `<N>`.

## Metadata

- **Reviewer:** security-engineer (read-only; this agent has no write tools)
- **Recorded by:** orchestrator, who transcribed the reviewer's hand-back on 2026-10-02
- **Reviewed:** `docs/artifacts/poc-security-reviewer-blocking-v1.md`, checked against `security-guidelines.md`, the reviewer's
  own earlier O1 rating (`security-review-poc-security-shortcuts-v1.md` § O1) and GitLab's documentation on removing
  sensitive data
- **Outcome applied in:** `docs/artifacts/poc-security-reviewer-blocking-v2.md`, which supersedes v1. The reviewer's
  delta re-review of v2 is recorded separately.

## Verdict: CONDITIONAL_PASS

The ruling points in the right direction. Every edit is stricter than the current text, and none weakens an existing
control. It closes O1's main route: findings no longer default to debt handoff, and it names the speed directive,
the timebox and the token envelope as things that cannot waive a finding.

The ruling has no CRITICAL or HIGH findings of its own. **O1 itself stays SECURITY:HIGH until the fix (FU-1)
merges, and the release block stands until then.**

| Severity | Count |
|---|---|
| CRITICAL | 0 |
| HIGH | 0 against the ruling; O1 stays open until FU-1 merges |
| MEDIUM | 7 (M1–M7), each a condition before FU-1 |
| LOW | 5 (L1–L5) |

## MEDIUM findings: each a condition before FU-1

- **M1: some security gaps below HIGH never block.** A removed or weakened control graded below HIGH does not
  block at the scan. The PoC workflow has no guaranteed pre-merge review gate where E11 would catch it. "Remove or
  weaken" also misses a control that was never implemented, for example string-concatenated SQL.
  - **Fix:** the blocking class becomes: any Immutable Constraint breach; any required security control that is
    omitted, removed, disabled or weakened, tagged or not, whatever its severity; and any CRITICAL or HIGH
    finding.
  - The fix is mirrored in E1, E4, E5, E8 and E10.
- **M2: there is no grading anchor.** An injection or authorization gap could be graded MEDIUM and pass. Secrets
  that were never committed were not covered.
  - **Fix:** a severity floor. A real credential (committed or not), an injection path reachable from external
    input, or a missing or bypassable authentication or authorization check on non-public data is never graded
    below HIGH.
  - A "not yet committed" path is added: steps 1, 2 and 4 apply, and step 1 may be skipped only for a value the
    user confirms is valid only on an ephemeral local instance.
- **M3: an open finding can be buried.** Stopping, cancelling or timing out the PoC buried it, because `AGENTS.md`
  archives `cancelled` rows.
  - **Fix:** each open blocking finding gets its own durable `blocked` task, which stays active until the reviewer
    confirms it resolved.
  - A timebox expiry records the Rule 3 verdict but does not close the PoC.
  - Escalation never turns a finding into debt.
- **M4: the issuer side and copies were not covered.**
  - **Fix:** the user reviews the issuer's audit logs for any use between exposure and revocation. Unrecognised use
    is an incident: stop.
  - Key material needs a statement of what it protected or signed.
  - Every copy the project controls (branches, tags, worktrees, CI logs, artifacts, caches, images, merge-request
    diffs) is listed by location and deleted or expired by the user.
- **M5: a history rewrite alone does not purge GitLab.** Commit content stays cached, and merge-request and
  pipeline refs keep the old commits until a maintainer runs Remove blobs, Redact text or Repository cleanup.
  - **Fix:** the user performs step 3 for any pushed secret.
  - Re-check needs a pattern-based scan of all branches and tags, never a search by the literal value.
- **M6: scan coverage had gaps.** The early check covered only steps 4, 5 and 7, and only "the first time".
  Steps 10, 13 and 14 run after step 9 and were never scanned, and the scans could be dropped to save scope.
  - **Fix:** a secrets, credentials and PII check before every first push and every merge, at any step. Neither
    this check nor step 9 is ever dropped to reduce scope, time or tokens.
- **M7: E11 left escape routes.** A finding could still enter the debt ledger as `accepted-risk`, or be waived by
  a Tech Lead (`code-review:150`).
  - **Fix:** no Tech Lead waiver applies to a security breach.
  - Such a finding enters the ledger only as `resolved`, never as `open`, `in-progress` or `accepted-risk`.

## LOW findings

- **L1:** the HIGH-blocks line is `security-guidelines:182`, not `:183`.
- **L2:** the speed-directive exception named only secrets. It now covers real PII and every Immutable Constraint.
- **L3:** secret handling now also bans copying the value into chat, issues, merge requests or tool arguments, and
  says to identify `.env` and `*.key` files by name without opening them.
- **L4:** `poc-security-engineer` keeps the `execute` tool. Replacing it with a fixed-command scanner is **parked**
  with X5. It is not a condition for FU-1.
- **L5:** the MEDIUM remediation-plan deadline is bounded: no later than the production handoff.

## Explicit answers to the ruling's questions

- **Q1. Should a removed or weakened control block below HIGH?** Yes (M1).
- **Q2. What if the user declines the history rewrite?** The reviewer proposed a conditional acceptance path.
  Because it changes scope the user approved, the user decided on 2026-10-02: **"Allow, with strict
  conditions"**. The finding may close as "revoked; retained in history by the user's decision" only if all
  three hold:
  - (a) revocation is confirmed;
  - (b) the audit log showed no unrecognised use;
  - (c) the secret is not key material.

  The decision is recorded and never treated as debt.
- **Q3. Is a hardcoded secret that was never committed at least HIGH?** Yes, for any real credential. Its value
  has already passed through agent contexts and is one `git add` away from breaching Constraint 1. A
  non-functional placeholder is not a secret.

## The reviewer's blocker, settled by the orchestrator

The reviewer's `security-audit` `grep_content` tool failed, so the orchestrator ran the requested sweep with a
shell. It searched `implementation/knowledge/` for `debt handoff`, `without blocking`, `non-critical`,
`accepted-risk` and `Tech Lead waiver`.

Outside the three amended files, nothing else routes security findings to debt. The only general routes are
`code-review:150` (Tech Lead waiver) and `technical-debt-tracking:93` (`accepted-risk`). v2 closes both for security
findings inside E11. `code-review:150` is noted as a candidate for a matching security carve-out.
