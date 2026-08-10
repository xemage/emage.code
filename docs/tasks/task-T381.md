# Task T381 — Validation gate and merge to develop

**ID:** T381
**Owner:** tech-lead, orchestrator
**Status:** done
**Priority:** P0
**Depends on:** T378, T379, T380
**Created:** 2026-08-09
**Based on:** docs/plans/plan-033-mcp-settings-hardening.md (P033-05)

This brief is self-contained. It has two roles: `tech-lead` performs a read-only review and issues a
VERDICT; the orchestrator then runs the verification bar and performs the actual git mechanics
(push, open MR, merge). `tech-lead` must never edit code during this review (per
`.claude/rules/security-guidelines.md`'s "Read-Only Agents" classification) and must never push,
open an MR, or merge — those are the orchestrator's steps below.

## Objective
Independently verify T377 (installer merge-safety fix), T378 (test coverage), T379 (AGENTS.md tag
drift fix), and T380 (README.md doc update) on branch
`bugfix/T377-install-mcp-merge-all-platforms`, and if verification passes, land the branch on
`develop` via the standard branch + MR flow per `.claude/rules/git-workflow.md`. This is the
Implementation Gate for plan-033's core merge-safety fix (P033-01 through P033-04) — no merge to
`develop` happens without this gate passing. T386-T388 (the separate server-removal work) are
**not** in scope for this gate; they land through their own gate, T388.

## Inputs
- Branch `bugfix/T377-install-mcp-merge-all-platforms` (created by T377, extended by T378, T379,
  T380) — check out its current tip, do not use a stale local copy.
- `git diff develop...bugfix/T377-install-mcp-merge-all-platforms` — the full diff to review.
  Expected scope: exactly six files —
  `scripts/install.sh` (T377), `tests/functional/test_install_script.py` (T378),
  `implementation/AGENTS.md`, `AGENTS.md`, `docs/wiki/mcp-servers.md` (T379), and `README.md`
  (T380). Any other file appearing in this diff is out-of-scope collateral and must be flagged, not
  silently accepted.

## Allow-list (what this task may do)
- Read-only review of the diff (tech-lead).
- Running the verification commands listed below (no file edits produced by running them).
- Git operations only: checkout, push the existing branch, open a merge request, merge after CI is
  green (orchestrator). No source file edits by either role in this task.

## Deny-list (do not do — no exceptions)
- Do NOT edit `scripts/install.sh`, any test file, either `AGENTS.md`, `docs/wiki/mcp-servers.md`,
  `README.md`, or any other file in this task. If verification fails, the fix belongs in a new fix
  task routed back to the owning task's original owner — not hand-patched here.
- Do NOT push directly to `develop` or `main`.
- Do NOT merge if any verification command fails, or if CI is not green.
- Do NOT force-push, do NOT skip CI, do NOT use `--no-verify`.
- Do NOT merge based solely on T377's/T378's/T379's/T380's own completion reports — the diff and
  verification commands below must be independently re-run and re-reviewed in this task, not
  assumed from prior reports.
- Do NOT include T386/T387 (the separate server-removal work) in this MR, even if their branch
  happens to already exist by the time this gate runs — they are a deliberately separate MR (see
  T388) with a different Conventional Commit type and root cause.

## Verification bar (literal commands, run from repo root `/home/emage/Code/emage/emage.code`, after
checking out `bugfix/T377-install-mcp-merge-all-platforms`)

1. ```
   make verify
   ```
   Runs `node implementation/scripts/sync.mjs --root implementation --check` under the hood — this
   is sufficient on its own; do not also run the raw `sync.mjs --check` command separately, it is
   the same check. PASS = drift-free output, exit 0. (This check only covers
   `implementation/`-tree generated output; it does not, and is not expected to, touch
   `scripts/install.sh`, `docs/wiki/`, `README.md`, or root `AGENTS.md`, none of which T377-T380
   touch inside `implementation/`'s generated trees except `implementation/AGENTS.md` itself, which
   is hand-authored source, not generated output — confirm `make verify` still passes regardless.)

2. ```
   python3 implementation/scripts/generate-registry.py --root implementation --check
   ```
   PASS = registry up to date, exit 0.

3. ```
   python3 docs/tasks/validate-tasks.py
   ```
   PASS = output starts with `TASK LEDGER: PASS`, exit 0.

4. ```
   python3 tests/run.py
   ```
   PASS = exits 0. Confirm (with `-v` if needed) that the new tests T378 added to
   `tests/functional/test_install_script.py` specifically ran and passed, not just that the
   aggregate exit code is 0.

5. Full diff review (tech-lead, read-only):
   ```
   git diff develop...bugfix/T377-install-mcp-merge-all-platforms --stat
   git diff develop...bugfix/T377-install-mcp-merge-all-platforms
   ```
   Confirm: exactly the six expected files changed (see Inputs above); `scripts/install.sh`'s diff
   is scoped to `sync_tree_into()`, `install_tree_into()`, `validate_before_update()`, and the five
   named `install_<platform>()` functions only (no changes to `install_github()`,
   `install_claude_code()`, `merge_or_copy_mcp_json()`, or the argument-parsing/dispatch blocks);
   `test_install_script.py`'s diff only adds new test methods, none of the ten pre-existing methods
   changed; `implementation/AGENTS.md`/`AGENTS.md`/`docs/wiki/mcp-servers.md`'s diffs are each
   scoped to exactly the one table row/line documented in T379's brief (no `Extended servers
   (opt-in)` bullet changes — that's T387's separate, later-sequenced scope); `README.md`'s diff is
   scoped to exactly the one paragraph documented in T380's brief.

## Acceptance criteria (all must be true)
- [ ] All 4 verification commands above pass (exit 0, matching the stated PASS conditions).
- [ ] The diff touches exactly the six expected files — no other file.
- [ ] `tech-lead` issues an explicit VERDICT: `PASS`, `CONDITIONAL_PASS`, or `FAIL`, referencing the
      specific diff and command output reviewed (not a generic approval).
- [ ] On `PASS` or `CONDITIONAL_PASS`: orchestrator independently re-reviews the full diff (not just
      trusting T377's/T378's/T379's/T380's/tech-lead's reports), pushes the branch, opens an MR from
      `bugfix/T377-install-mcp-merge-all-platforms` to `develop` referencing T377, T378, T379, and
      T380 in the title or description, waits for CI to go green, then merges (squash-and-merge, per
      `git-workflow.md`'s convention for bugfix branches).
- [ ] On `FAIL`: merge is blocked. A fix task is created and routed to the owning task's original
      owner (whichever of T377/T378/T379/T380 produced the failing component); this gate is re-run
      after the fix lands on the same branch.
- [ ] Branch name is exactly `bugfix/T377-install-mcp-merge-all-platforms` (already created by T377
      — do not rename it).
- [ ] Post-merge `develop` tip re-passes all 4 verification commands (re-run fresh, not just trusted
      from the pre-merge branch state).

## Blocker protocol
STOP and report a blocker if:
- The branch doesn't exist, or T377's/T378's/T379's/T380's commits aren't all present on it →
  `type: dependency`, `severity: critical`.
- Any verification command fails → `type: technical`, `severity: major` (or `critical` if
  `python3 tests/run.py` fails), do not merge, create a fix task instead.
- The diff includes files outside the six expected → `type: technical`, `severity: major` — this is
  scope creep beyond T377-T380's allow-lists and must be resolved (either removed from the branch or
  explicitly re-scoped by the orchestrator) before merge, not silently accepted.
- CI does not go green after pushing/opening the MR → `type: technical`, `severity: major`, do not
  merge, investigate the specific failing job before retrying.

Max 2 retries before escalating to the user with full context (what was tried, exact failure).

## Git workflow
1. Check out `bugfix/T377-install-mcp-merge-all-platforms` at its current tip.
2. Run the verification bar (all 4 commands above); tech-lead reviews the diff and issues VERDICT.
3. On `PASS`/`CONDITIONAL_PASS`: `git push -u origin bugfix/T377-install-mcp-merge-all-platforms`.
4. Open a merge request targeting `develop`, title referencing T377-T380 (e.g. "fix(install): extend
   MCP merge-safety to cursor/gemini/opencode/pi/cline (T377-T380)").
5. Wait for CI to report green on the MR. Do not merge before CI completes.
6. Merge via squash-and-merge (standard for `bugfix/*` branches per `git-workflow.md`).
7. Delete the merged branch (normal cleanup per the Worktree Lifecycle in `git-workflow.md`) — at
   this point T377-T380 are all merged, nothing else stacks on this branch.
8. Confirm post-merge `develop` tip re-passes the same 4 verification commands (re-run them on fresh
   `develop`, not just trust the pre-merge branch state).

## Constraints
- Token budget: ≤12k tokens.
- No source file edits in this task.
- Never commit directly to `develop` or `main` — only merge via the reviewed MR.
