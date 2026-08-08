# Task T346 — GATE: verify T343/T344/T345, record BUG-G disposition, close T316

**ID:** T346
**Owner:** qa-engineer
**Status:** pending
**Priority:** P2
**Depends on:** T343, T344, T345
**Created:** 2026-08-08
**Based on:** `docs/plans/plan-023-t316-pattern-a-cleanup.md`, `docs/tasks/task-T316.md`

## Objective
Independently verify T343 (BUG-H), T344 (BUG-A + BUG-F), and T345 (BUG-E) are all correctly
merged to `develop` and the combined result is sound (no interaction bugs between the three
independent changes), record BUG-G's deferral disposition, and produce the evidence needed for the
orchestrator to close T316 itself.

## Context
- Phase: Validation Gate (review only — MUST NOT modify code, per `.claude/rules/security-guidelines.md`
  § "Read-Only Agents" / `AGENTS.md` § "Validation Gates": review agents do not modify code during
  review)
- This task only starts once T343/T344/T345 have all been merged to `develop` — do not begin
  before confirming all three MRs are merged (check `git log develop` for the three merge commits,
  or ask the orchestrator to confirm before you start if it's unclear).
- BUG-G's disposition (deferred, not routed to CWSO) was already decided and reasoned in
  `docs/plans/plan-023-t316-pattern-a-cleanup.md` § 3.4 — this task records that decision in
  `docs/tasks/task-T316.md`'s own Execution notes, it does not re-litigate it.

## Inputs
- `docs/plans/plan-023-t316-pattern-a-cleanup.md` — full design rationale
- `docs/tasks/task-T343.md`, `task-T344.md`, `task-T345.md` — Outcome sections with per-task
  evidence
- `docs/tasks/task-T316.md` — the original task, to be updated with final disposition

## Constraints
- Read-only for application code — this is a verification gate, not an implementation task.
- May write to `docs/tasks/task-T316.md` only (recording the verification result and BUG-G's
  disposition) — do not touch `active-tasks.md`/`completed-tasks.md` (orchestrator-only archival)
  and do not touch this task's own `**Status:**` header beyond what's needed to report your result
  to the orchestrator.
- Token budget: ≤ 40k.

## Expected Outputs
- A VERDICT (`PASS` | `CONDITIONAL_PASS` | `FAIL`) per `.claude/rules/*` validation-gate
  convention, covering:
  1. Full local test suite green on current `develop` tip (after all three merges)
  2. `implementation.runtime.cwso.ast_conflict_check.CwsoClient is
     implementation.runtime.cwso.concurrent_merge.CwsoClient` → `True` (BUG-H's fix, re-verified
     independently, not just trusting T343's own report)
  3. `ConcurrentMergeOrchestrator`'s new two-client constructor works as designed (re-run or
     independently inspect T344's regression tests)
  4. Same-path 3+-worker collision raises the expected error (re-run or independently inspect
     T344's regression test)
  5. `write_shadow_file`'s best-effort `blob_oid` extraction behaves as designed on the real
     example format from BUG-E (re-run or independently inspect T345's regression test)
- A written disposition for BUG-G appended to `docs/tasks/task-T316.md`'s Execution notes: quote
  plan-023 § 3.4's reasoning, confirm it as this task's own independent recommendation (not just a
  copy), and confirm no active caller of `ConcurrentMergeOrchestrator` outside tests has emerged
  that would change that reasoning.

## Acceptance Criteria
- [ ] Full test suite result cited with exact command/output
- [ ] All 5 checks above independently re-verified (not just re-stating what T343/T344/T345
      already claimed) — re-run the relevant tests/commands yourself
- [ ] BUG-G disposition recorded in `task-T316.md` Execution notes
- [ ] VERDICT stated explicitly
- [ ] No application code modified by this task

## Blocker Protocol
Report blockers per `AGENTS.md`: type + severity. A `FAIL` verdict is not itself a blocker — it's
a valid, expected outcome; report it plainly with the specific failing check, and the orchestrator
will create a fix task and re-route (per `AGENTS.md` § "Validation Gates").
