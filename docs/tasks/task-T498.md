# Task T498 — Fix four diagnosed golden-suite checker-brittleness bugs (protected-path exception)

**ID:** T498
**Owner:** backend-developer
**Status:** in_progress
**Priority:** P1
**Depends on:** None structurally blocking (T456 and T493 are both `done`; this task is motivated
by their findings but does not depend on any currently-blocked task).
**Blocks:** Nothing structurally. **Does not itself re-run T456's ship-gate measurement** — that
is a separate, future follow-up task, not created here and not in this task's scope.
**Created:** 2026-09-17
**Based on:** `docs/plans/plan-052-t498-golden-checker-brittleness-fixes.md` (this task's backing
plan — read it in full before starting, especially "Direct verification performed before writing
this plan" and "Risks and mitigations"); `docs/benchmarks/baseline-v6.17.0-retrieval.md` §6/§7/§9
(exists only on the unmerged branch `agent/orchestrator/T456` — fetch and read via `git show
origin/agent/orchestrator/T456:docs/benchmarks/baseline-v6.17.0-retrieval.md`, not from
`develop`); `docs/tasks/task-T493.md` (bug 1's original, pre-dating-T456 diagnosis);
`docs/artifacts/protected-paths-v1.md` §5 (the exception process this brief invokes, see dedicated
section below); `docs/benchmarks/baseline-v6.12.0.md` / `scorecard-v6.12.0.md` (T414's frozen
Phase-1 baseline, the regression-parity target for the three named `open` cases).

## Objective

Fix exactly four already-diagnosed, arm-agnostic checker-brittleness bugs in the golden suite's
own `expect.py` files, spanning five files (one bug's mechanism is independently duplicated across
an `open` case and its `held-out` sibling — two separate files, same bug, no shared code). Each fix
must be minimal and targeted — a surgical correction to the specific defective logic, not a
rewrite of the checker. This task's motivation, evidence chain, and exact scope boundary are
recorded in `plan-052`; re-derive the bug mechanisms from the live files yourself before touching
anything, per "Direct verification" below — do not trust this brief's summary over the real file
content if they disagree.

## The four bugs, and the five files

1. **`matrix_self_consistency_slip`** —
   `tests/golden/open/security-audit-coverage-consistency/expect.py`. The checker requires
   `declared_n == len(rows)` (the declared `**OWASP coverage**: n/10` field must exactly equal the
   count of distinct `A0X` matrix rows present), with no allowance for a matrix that legitimately
   lists all 10 categories for completeness (including N/A ones) while the declared count reflects
   a narrower assessed/in-scope/out-of-scope subset. This is the cause `task-T493.md` diagnosed
   before T456's session began, and the one `baseline-v6.17.0-retrieval.md` §6 attributes the
   entire measured floor-miss to (control 4/5, treatment 1/5 across k=5 live trials — an
   arm-agnostic effect, not retrieval-caused).

2. **Nested-fence heading truncation** — two independent files, same bug mechanism, fix both:
   - `tests/golden/open/prepare-release-real-verdict-missing/expect.py`
   - The held-out sibling referred to as **HO-5** in `baseline-v6.17.0-retrieval.md` (`/prepare-
     release`, `expected_pass` per that report's §4 row). **Do not use the alias to guess the
     path.** Independently re-derive the real directory by reading every `expect.py` under
     `tests/golden/held-out/` and finding the one whose `_verdict_section()` implementation is
     byte-identical to `prepare-release-real-verdict-missing`'s own (same `\n#{1,2}\s` boundary
     regex, same `REQUIRED_FIELDS` list, same `fixture/release-notes.md` target file) — cross-check
     against the command surface (`/prepare-release`) and `expected_pass` status to confirm.
   Both files' `_verdict_section(text)` finds `## RELEASE VERDICT`, then finds the next
   heading boundary via `re.search(r"\n#{1,2}\s", rest)` — this matches a fenced-code-block's
   *inner* reproduction of a `## RELEASE VERDICT` heading (a structure both the real command
   template and realistic session output can produce) and truncates the section before real field
   data is reached, even when the real fields are present later in the document.

3. **Numeric-index-vs-literal-`A0N` mismatch** — the held-out case referred to as **HO-6** in
   `baseline-v6.17.0-retrieval.md` (`/security-audit`, `expected_pass` per that report's §4 row).
   Independently re-derive the real directory the same way as HO-5 above: read every `expect.py`
   under `tests/golden/held-out/`, find the one requiring literal `\|\s*A0[1-9]\s*\|` /
   `\|\s*A10\s*\|`-style tokens as their own table cell for all ten categories, cross-check against
   `/security-audit` + `expected_pass`. The checker requires the literal `A01`–`A10` token as its
   own cell; a session that numbers matrix rows `1`–`10` in a `#` column and folds the category
   code into the name cell instead (`| 1 | A01: Broken Access Control | ...` vs. the required
   `| A01 | Broken Access Control | ...`) fails even though the content is substantively complete
   and correct.

4. **First-regex-match `Status` field** —
   `tests/golden/open/security-audit-critical-not-fail/expect.py`. `status_match = re.search(r"\*\*Status\*\*\s*:\s*(\S+)", text)`
   scans the whole document and returns the *first* match, not one scoped to the real `## VERDICT`
   block. A document with an earlier informal `**Status**: Fail` mention (e.g. in a `## Summary`
   section) ahead of the real, later `**Status**: FAIL` field in `## VERDICT` fails the check even
   when the real verdict field is correct.

## Held-out isolation discipline — mandatory, not optional

`tests/functional/test_golden_held_out_isolation.py` Check B flags any file **outside**
`tests/golden/` that mentions one of the six real held-out case IDs as a whole token. The two real
directory names for HO-5 and HO-6 **must never appear literally** in any file outside
`tests/golden/` that this task produces or touches — not in commit messages, not in the MR
title/description, not in this task brief's own status updates, not in any scratch note you leave
in the repo. Refer to them only as `HO-5` / `HO-6` (or the redacted scorecard IDs `held-out-case-5`
/ `held-out-case-6`) in anything committed outside `tests/golden/`. The actual code edits to
`tests/golden/held-out/<real-name>/expect.py` are fine — that path is *inside* `tests/golden/`, so
Check B does not apply there; only literal-ID mentions in files *outside* that tree are the
problem. Verify `tests/functional/test_golden_held_out_isolation.py` still passes as part of your
own final verification pass, before reporting completion.

## Protected-path exception — explicit invocation of `docs/artifacts/protected-paths-v1.md` §5

`protected-paths-v1.md` declares `tests/golden/**` protected: "no agent definition may edit these
paths as part of normal improvement-task work, full stop." §5 ("Exception path for genuine future
maintenance") sets out three numbered requirements for any exception. **This brief satisfies all
three, stated explicitly here, not left implicit:**

1. **"Never a silent edit."** This is not a silent edit incidental to unrelated work — this entire
   brief exists for the sole purpose of authorizing and scoping five specific, disclosed edits
   inside `tests/golden/**`.
2. **"Always a named, authorized task... The brief is authored by the orchestrator (or, per this
   repo's protocol, explicitly requested by the user) — not invented unilaterally by a dispatched
   agent mid-task."** This document, `docs/tasks/task-T498.md`, is that named, authorized task
   brief, authored by the orchestrator following the user's own explicit, current-turn dispatch
   instruction (quoted in full in `plan-052`'s "Status" section). **This brief explicitly
   authorizes editing exactly these five files, and no others, inside `tests/golden/**`:**
   - `tests/golden/open/security-audit-coverage-consistency/expect.py`
   - `tests/golden/open/prepare-release-real-verdict-missing/expect.py`
   - `tests/golden/open/security-audit-critical-not-fail/expect.py`
   - `tests/golden/held-out/<HO-5, independently re-derived — see bug 2 above>/expect.py`
   - `tests/golden/held-out/<HO-6, independently re-derived — see bug 3 above>/expect.py`

   `scripts/scorecard.py` is **not** authorized and must not be touched — none of these four bugs
   are in it. No other file under `tests/golden/**` (no `fixture/`, no `brief.md`, no other case's
   `expect.py`, no manifest file) is authorized either.
3. **"Ordinary review still applies... the exception authorizes that a change to a protected path
   may be proposed, it does not bypass review."** This change goes through the same
   branch/worktree/MR flow as any other change in this repo (this project's own Git Workflow
   instructions) — see "Git workflow" below. No self-merge by you or by the orchestrator; the
   orchestrator will
   independently review the diff before anything is left for the user, and the user makes the
   final merge decision.

## Constraints

- **Branch:** create `agent/backend-developer/T498` from `origin/develop` (not from the current
  checkout's `feature/T475-codex-platform-integration` branch — never touch that branch, never
  fetch or merge from it, never reference it for any reason).
- **Never touch:** `.mcp.json`, `docs/benchmarks/tb-subset.json`, `docs/benchmarks/tb-subset.md`,
  `docs/benchmarks/scorecard-v6.12.0.json`, `docs/benchmarks/scorecard-v6.12.0.md` (running
  `scripts/scorecard.py` regenerates these two in place with a timestamp-only diff — if you run it
  for verification, `git checkout --` them immediately afterward so no stray diff is left),
  `feature/T475-codex-platform-integration`.
- **Do not touch `scripts/scorecard.py`.**
- **Do not touch any `tests/golden/**` content beyond the five named `expect.py` files** — no
  `fixture/` changes, no `brief.md` changes, no touching any other case's `expect.py`, no
  "cleanup."
- **Do not fold in T456's ship-gate re-measurement.** That is explicitly out of scope for this
  task — a separate future task's job.
- Each fix must be **minimal and targeted** — a surgical correction to the specific defective
  logic identified above, not a broader rewrite of the checker's structure or style.
- **If bug 1's fix turns out to require a genuine design decision** — e.g., no clean, mechanical
  way to distinguish "a legitimately narrower declared count" from "a genuinely wrong count"
  without more context than `expect.py`/`fixture/` can access — **report this as a real blocker**
  (type `technical`, per this repo's Blocker Protocol) rather than picking an arbitrary
  interpretation and implementing it silently. The orchestrator will route this to the user if it
  occurs, per the standing 2-retry-then-escalate rule.
- **If any bug's real mechanism, once you read the live file, doesn't match this brief's
  description** — trust the real file, fix the real mechanism, and disclose the discrepancy
  plainly in your completion report rather than forcing a fix to match a possibly-stale
  description.

## Expected Outputs

1. Five modified `expect.py` files (see the authorized list above), each fix minimal and targeted.
2. For each of the four bugs: an explicit before/after trace or regression test proving the fix
   resolves the diagnosed false-negative **without introducing a new false-positive** — i.e. a
   deliberately-constructed genuinely-non-compliant document must still fail the fixed checker.
   This can be a new small unit test alongside the case (if the golden-suite format supports it
   without violating its own purity/determinism contract — check
   `docs/artifacts/golden-suite-format-v1.md` first) or a documented before/after `check()` call
   trace in your completion report; either is acceptable, but it must be concrete, not asserted.
3. A completion report (in your final message back to the orchestrator, not a new committed file)
   documenting: the real paths re-derived for HO-5/HO-6 (via the orchestrator's private channel —
   do not commit them, see "Held-out isolation discipline" above), each fix's before/after trace,
   the frozen-baseline cross-check results (see Acceptance Criteria), and full verification bar
   output.

## Acceptance Criteria

1. Exactly the five named `expect.py` files are modified — confirmed via `git diff
   origin/develop...HEAD --stat` showing no other file touched, and a second check specifically
   confirming zero diff against `scripts/scorecard.py` and every `fixture/`/`brief.md` file in
   `tests/golden/**`.
2. Each of the four bugs is fixed at its real, directly-confirmed mechanism (not this brief's
   summary alone) — re-verified by the orchestrator reading each diff hunk against the live
   pre-fix file content.
3. Each fix has a concrete before/after trace or regression test proving it resolves the diagnosed
   false-negative without creating a new false-positive on a genuinely-non-compliant document.
4. `python3 tests/run.py` passes with no regressions (including
   `tests/functional/test_golden_held_out_isolation.py` and
   `tests/functional/test_protected_paths_declared.py`).
5. Frozen/fresh-baseline parity, confirmed via `scripts/scorecard.py` (run, inspect, then
   `git checkout --` its two output files so no diff is left committed):
   - `security-audit-coverage-consistency`: must remain `pass` (Phase-1 frozen baseline:
     `expected_pass` / `pass`, per `scorecard-v6.12.0.md`).
   - `prepare-release-real-verdict-missing`: must remain `fail` / `known_failing` /
     `tracked_defect` (per `scorecard-v6.12.0.md`) — this case's fixture is a deliberate
     known-failing example; the *fix* to the checker's heading-boundary logic must not
     accidentally flip this specific fixture to passing merely because the checker got less
     strict in the wrong dimension. If your fix causes this case's static fixture result to
     change, treat that as a signal to re-examine the fix, not something to silently accept.
   - `security-audit-critical-not-fail`: must remain `fail` / `known_failing` / `tracked_defect`,
     same reasoning as above.
   - `HO-5` and `HO-6`: must remain `pass` (both currently `expected_pass` / `pass` on today's
     fresh run, captured in `plan-052`'s cross-check table — held-out identity/results are not
     published by name in any committed doc, by design; use the redacted `held-out-case-5` /
     `held-out-case-6` scorecard IDs to confirm parity, not the real directory names, in anything
     you write outside `tests/golden/`).
6. No new committed file, commit message, or MR text anywhere outside `tests/golden/` contains the
   real literal directory name for HO-5 or HO-6.
7. Branch/MR discipline followed exactly (see "Git workflow" below) — no self-merge.

## Git workflow

- Branch: `agent/backend-developer/T498`, created from `origin/develop`.
- Commits: Conventional Commits format, `fix(golden-suite): ...`-style scope, one commit per bug
  is acceptable but not required — squash-friendly either way.
- Open a merge request from `agent/backend-developer/T498` to `develop`. Title must reference
  `T498`. **Do not merge it.** Report the branch name and MR link (or MR creation command output,
  if `glab`/GitLab MR creation is unavailable in this environment) back to the orchestrator.

## Blocker Protocol

Report blockers with type (`technical` / `dependency` / `unclear_requirements` / `external`) and
severity (`critical` / `major` / `minor`), per this repo's standing protocol. Bug 1's fix is the
most likely source of a genuine `unclear_requirements`-or-`technical` blocker — see the dedicated
Constraints bullet above. Do not silently fail or silently narrow scope without disclosing it.
