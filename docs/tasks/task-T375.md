# Task T375 — Validation gate and merge to develop

**ID:** T375
**Owner:** tech-lead, orchestrator
**Status:** pending
**Priority:** P0
**Depends on:** T373, T374
**Created:** 2026-08-09
**Based on:** docs/plans/plan-032-render-agents-cline-platform-map-fix.md (P032-03)

This brief is self-contained. It has two roles: `tech-lead` performs a read-only review and issues
a VERDICT; the orchestrator then runs the verification bar and performs the actual git mechanics
(push, open MR, merge). `tech-lead` must never edit code during this review (per
`.claude/rules/security-guidelines.md`'s "Read-Only Agents" classification) and must never push,
open an MR, or merge — those are the orchestrator's steps below.

## Objective
Independently verify T373's fix and T374's test coverage on branch
`bugfix/T373-render-agents-cline-platform-map`, and if verification passes, land the branch on
`develop` via the standard branch + MR flow per `.claude/rules/git-workflow.md`. This is the
Implementation Gate for plan-032 — no merge to `develop` happens without this gate passing.

## Inputs
- Branch `bugfix/T373-render-agents-cline-platform-map` (created by T373, extended by T374) —
  check out its current tip, do not use a stale local copy.
- `git diff develop...bugfix/T373-render-agents-cline-platform-map` — the full diff to review.
  Expected scope: exactly two files, `scripts/render_installed_agents.py` (T373) and
  `tests/functional/test_install_agents_mapping.py` (T374). Any other file appearing in this diff
  is out-of-scope collateral and must be flagged, not silently accepted.

## Allow-list (what this task may do)
- Read-only review of the diff (tech-lead).
- Running the verification commands listed below (no file edits produced by running them).
- Git operations only: checkout, push the existing branch, open a merge request, merge after CI is
  green (orchestrator). No source file edits by either role in this task.

## Deny-list (do not do — no exceptions)
- Do NOT edit `scripts/render_installed_agents.py`, the test file, or any other file in this task.
  If verification fails, the fix belongs in a new fix task routed back to T373's or T374's owner —
  not hand-patched here.
- Do NOT push directly to `develop` or `main`.
- Do NOT merge if any verification command fails, or if CI is not green.
- Do NOT force-push, do NOT skip CI, do NOT use `--no-verify`.
- Do NOT merge based solely on T373's/T374's own completion reports — the diff and verification
  commands below must be independently re-run and re-reviewed in this task, not assumed from prior
  reports.

## Verification bar (literal commands, run from repo root `/home/emage/Code/emage/emage.code`,
after checking out `bugfix/T373-render-agents-cline-platform-map`)

1. ```
   make verify
   ```
   This runs `node implementation/scripts/sync.mjs --root implementation --check` under the hood —
   running `make verify` once is sufficient; do not also run the raw `sync.mjs --check` command
   separately, it is the same check. PASS = `OK - no drift across 550 files.` (or current file
   count), exit 0.

2. ```
   python3 implementation/scripts/generate-registry.py --root implementation --check
   ```
   PASS = `registry is up to date`, exit 0.

3. ```
   python3 docs/tasks/validate-tasks.py
   ```
   PASS = output starts with `TASK LEDGER: PASS`, exit 0.

4. ```
   python3 tests/run.py
   ```
   PASS = exits 0. Confirm the `all`-platform test in
   `tests/functional/test_install_agents_mapping.py` specifically passed (visible with `-v`:
   `python3 tests/run.py -v` if you need to confirm which test ran, not just the aggregate exit
   code).

5. Full diff review (tech-lead, read-only):
   ```
   git diff develop...bugfix/T373-render-agents-cline-platform-map --stat
   git diff develop...bugfix/T373-render-agents-cline-platform-map
   ```
   Confirm: exactly the two expected files changed; `scripts/render_installed_agents.py`'s diff is
   scoped to the `platform == "all"` branch only (no changes to `PLATFORM_MAP`, the per-platform
   branch, or `main()`); the test file's diff only adds assertions to
   `test_all_platform_install_includes_projection_map` without touching other methods.

## Acceptance criteria (all must be true)
- [ ] All 4 verification commands above pass (exit 0, matching the stated PASS conditions).
- [ ] The diff touches exactly `scripts/render_installed_agents.py` and
      `tests/functional/test_install_agents_mapping.py` — no other file.
- [ ] `tech-lead` issues an explicit VERDICT: `PASS`, `CONDITIONAL_PASS`, or `FAIL`, referencing
      the specific diff and command output reviewed (not a generic approval).
- [ ] On `PASS` or `CONDITIONAL_PASS`: orchestrator independently re-reviews the full diff (not
      just trusting T373's/T374's/tech-lead's reports), pushes the branch, opens an MR from
      `bugfix/T373-render-agents-cline-platform-map` to `develop` referencing T373 and T374 in the
      title or description, waits for CI to go green, then merges (squash-and-merge, per
      `git-workflow.md`'s convention for bugfix branches).
- [ ] On `FAIL`: merge is blocked. A fix task is created and routed to T373's or T374's owner
      (whichever produced the failing component); this gate is re-run after the fix lands on the
      same branch.
- [ ] Branch name is exactly `bugfix/T373-render-agents-cline-platform-map` (already created by
      T373 — do not rename it).

## Blocker protocol
STOP and report a blocker if:
- The branch doesn't exist, or T373's/T374's commits aren't both present on it → `type:
  dependency`, `severity: critical`.
- Any verification command fails → `type: technical`, `severity: major` (or `critical` if
  `python3 tests/run.py` fails), do not merge, create a fix task instead.
- The diff includes files outside the two expected → `type: technical`, `severity: major` — this
  is scope creep beyond T373/T374's allow-lists and must be resolved (either removed from the
  branch or explicitly re-scoped by the orchestrator) before merge, not silently accepted.
- CI does not go green after pushing/opening the MR → `type: technical`, `severity: major`, do not
  merge, investigate the specific failing job before retrying.

Max 2 retries before escalating to the user with full context (what was tried, exact failure).

## Git workflow
1. Check out `bugfix/T373-render-agents-cline-platform-map` at its current tip.
2. Run the verification bar (all 4 commands above); tech-lead reviews the diff and issues VERDICT.
3. On `PASS`/`CONDITIONAL_PASS`: `git push -u origin bugfix/T373-render-agents-cline-platform-map`.
4. Open a merge request targeting `develop`, title referencing T373 and T374 (e.g.
   "fix(install): derive render_installed_agents.py all-branch platform refs from PLATFORM_MAP
   (T373, T374)").
5. Wait for CI to report green on the MR. Do not merge before CI completes.
6. Merge via squash-and-merge (standard for `bugfix/*` branches per `git-workflow.md`).
7. Do NOT delete the remote branch reference needed by any still-pending stacked work — at this
   point T373 and T374 are both merged, so normal branch cleanup (delete the merged branch) is
   fine per the Worktree Lifecycle in `git-workflow.md`.
8. Confirm post-merge `develop` tip re-passes the same 4 verification commands (re-run them on
   fresh `develop`, not just trust the pre-merge branch state).

## Constraints
- Token budget: ≤8k tokens.
- No source file edits in this task.
- Never commit directly to `develop` or `main` — only merge via the reviewed MR.
