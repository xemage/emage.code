# Task T393 — Validation gate and merge to develop

**ID:** T393
**Owner:** tech-lead, orchestrator
**Status:** pending
**Priority:** P0
**Depends on:** T391, T392
**Created:** 2026-08-10
**Based on:** docs/plans/plan-034-mcp-provenance-tracking.md (P034-05)

This brief is self-contained. It has two roles: `tech-lead` performs a read-only review and issues a
VERDICT; the orchestrator then runs the verification bar and performs the actual git mechanics (push,
open MR, merge). `tech-lead` must never edit code during this review (per
`.claude/rules/security-guidelines.md`'s "Read-Only Agents" classification) and must never push, open
an MR, or merge — those are the orchestrator's steps below.

## Objective
Independently verify T389 (ADR-002 design), T390 (provenance sidecar + pruning + bootstrap bridge
implementation), T391 (test coverage), and T392 (documentation) on branch
`feature/T389-mcp-merge-provenance-tracking`, and if verification passes, land the branch on `develop`
via the standard branch + MR flow per `.claude/rules/git-workflow.md`. This is the Implementation Gate
for plan-034's provenance-tracking mechanism — no merge to `develop` happens without this gate
passing. `docs/tasks/task-T382.md` (the repo-root proof-point re-attempt) is explicitly **not** in
scope for this gate and must not be started until this gate reaches `PASS`/`CONDITIONAL_PASS` and the
branch is actually merged (T382's own brief encodes this as `Depends on: T381, T388, T393`).

## Inputs
- Branch `feature/T389-mcp-merge-provenance-tracking` (created by T389, extended by T390, T391, T392)
  — check out its current tip, do not use a stale local copy.
- `git diff develop...feature/T389-mcp-merge-provenance-tracking` — the full diff to review. Expected
  scope: `docs/decisions/ADR-002-mcp-merge-provenance-tracking.md` (T389);
  `scripts/merge-mcp-json.py`, `scripts/install.sh`, `implementation/scripts/sync.mjs`, plus every
  regenerated file under `implementation/` that changed as a side effect of adding the sidecar output
  (T390); `tests/functional/test_install_script.py` (T391); `README.md`, `docs/wiki/mcp-servers.md`
  (T392). Any other file appearing in this diff is out-of-scope collateral and must be flagged, not
  silently accepted.

## Allow-list (what this task may do)
- Read-only review of the diff (tech-lead).
- Running the verification commands listed below (no file edits produced by running them).
- Git operations only: checkout, push the existing branch, open a merge request, merge after CI is
  green (orchestrator). No source file edits by either role in this task.

## Deny-list (do not do — no exceptions)
- Do NOT edit the ADR, `scripts/merge-mcp-json.py`, `scripts/install.sh`, `sync.mjs`, any test file,
  `README.md`, or `docs/wiki/mcp-servers.md` in this task. If verification fails, the fix belongs in a
  new fix task routed back to the owning task's original owner (T389/T390/T391/T392) — not
  hand-patched here.
- Do NOT push directly to `develop` or `main`.
- Do NOT merge if any verification command fails, or if CI is not green.
- Do NOT force-push, do NOT skip CI, do NOT use `--no-verify`.
- Do NOT merge based solely on T389's/T390's/T391's/T392's own completion reports — the diff and
  verification commands below must be independently re-run and re-reviewed in this task, not assumed
  from prior reports.
- Do NOT start or delegate `docs/tasks/task-T382.md` from within this task — that only happens after
  this gate's merge completes, as a separate, later delegation by the orchestrator.

## Verification bar (literal commands, run from repo root `/home/emage/Code/emage/emage.code`, after
checking out `feature/T389-mcp-merge-provenance-tracking`)

1. ```
   make verify
   ```
   Runs `node implementation/scripts/sync.mjs --root implementation --check` under the hood — this is
   sufficient on its own, do not also run the raw `sync.mjs --check` command separately, it is the
   same check. PASS = drift-free output, exit 0. This is the single most important check for this
   gate — it directly validates that T390's sidecar-emission change in `sync.mjs` is self-consistent
   and that every regenerated `implementation/` file (including every new
   `<mcpfile>.provenance.json`-style sidecar, using T390's actual committed naming) matches what the
   generator currently produces.

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
   PASS = exits 0. Confirm (with `-v` if needed) that T391's new test methods in
   `tests/functional/test_install_script.py` specifically ran and passed — not just that the aggregate
   exit code is 0 — including, at minimum, the retired-key-pruning test and the
   currently-active-key-refresh-not-pruned test (the single most safety-critical proof point in this
   whole plan).

5. `ADR-002` sanity check:
   ```
   test -f docs/decisions/ADR-002-mcp-merge-provenance-tracking.md && echo "PASS: ADR-002 exists"
   grep -c "^- \*\*Status\*\*: Accepted" docs/decisions/ADR-002-mcp-merge-provenance-tracking.md
   ```
   PASS = `PASS: ADR-002 exists` printed; second command prints `1` (Status is `Accepted`, not left as
   `proposed`).

6. No literal secret ever written by the new code path — spot-check every `.provenance.json`-style
   sidecar file that changed in this diff (using T390's actual naming) contains only server *names*,
   never a resolved credential value, and confirm no MCP JSON file in the diff lost its placeholder
   syntax:
   ```
   git diff develop...feature/T389-mcp-merge-provenance-tracking -- implementation/ | grep -E '\$\{env:|"env"' | grep -v '\$\{env:[A-Z_]+\}' | head -20
   ```
   PASS = empty output (every `env`-related line in the diff still uses `${env:VAR}` placeholder
   syntax, never a literal resolved value).

7. Full diff review (tech-lead, read-only):
   ```
   git diff develop...feature/T389-mcp-merge-provenance-tracking --stat
   git diff develop...feature/T389-mcp-merge-provenance-tracking -- docs/decisions/ADR-002-mcp-merge-provenance-tracking.md scripts/merge-mcp-json.py scripts/install.sh implementation/scripts/sync.mjs README.md docs/wiki/mcp-servers.md tests/functional/test_install_script.py
   ```
   Confirm: ADR-002's Decision section is unambiguous and internally consistent with what T390 actually
   implemented (spot-check at least the sidecar naming convention and the pruning algorithm's shape
   match between the ADR text and the `merge-mcp-json.py` diff); `scripts/install.sh`'s diff is scoped
   to the sidecar exclude-list/call-site wiring only (no unrelated function touched);
   `test_install_script.py`'s diff only adds new test methods, none of the 16 pre-existing methods
   changed; `README.md`'s diff is scoped to the one paragraph (now extended) documented in T392's
   brief; `docs/wiki/mcp-servers.md`'s diff is scoped to exactly one new section, no existing section
   altered.

## Acceptance criteria (all must be true)
- [ ] All 6 verification commands above pass (exit 0 / matching stated PASS conditions).
- [ ] The diff touches exactly the expected files (ADR-002, the three implementation files plus their
      sanctioned regenerated `implementation/` output, the one test file, `README.md`, and
      `docs/wiki/mcp-servers.md`) — no other file.
- [ ] `tech-lead` issues an explicit VERDICT: `PASS`, `CONDITIONAL_PASS`, or `FAIL`, referencing the
      specific diff and command output reviewed (not a generic approval).
- [ ] On `PASS` or `CONDITIONAL_PASS`: orchestrator independently re-reviews the full diff (not just
      trusting T389's/T390's/T391's/T392's/tech-lead's reports), pushes the branch, opens an MR from
      `feature/T389-mcp-merge-provenance-tracking` to `develop` referencing T389, T390, T391, and T392
      in the title or description, waits for CI to go green, then merges (squash-and-merge, per
      `git-workflow.md`'s convention for `feature/*` branches).
- [ ] On `FAIL`: merge is blocked. A fix task is created and routed to the owning task's original
      owner (whichever of T389/T390/T391/T392 produced the failing component); this gate is re-run
      after the fix lands on the same branch.
- [ ] Branch name is exactly `feature/T389-mcp-merge-provenance-tracking` (already created by T389 —
      do not rename it).
- [ ] Post-merge `develop` tip re-passes verification commands 1-4 (re-run fresh, not just trusted
      from the pre-merge branch state).
- [ ] `docs/tasks/task-T382.md` remains untouched by this task — its own execution is a separate,
      later delegation, only after this gate's merge is confirmed.

## Blocker protocol
STOP and report a blocker if:
- The branch doesn't exist, or T389's/T390's/T391's/T392's commits aren't all present on it → `type:
  dependency`, `severity: critical`.
- Any verification command fails → `type: technical`, `severity: major` (or `critical` if
  `python3 tests/run.py` fails), do not merge, create a fix task instead.
- The diff includes files outside the expected set → `type: technical`, `severity: major` — this is
  scope creep beyond T389-T392's allow-lists and must be resolved (either removed from the branch or
  explicitly re-scoped by the orchestrator) before merge, not silently accepted.
- Test 5 finds ADR-002 missing or its Status is not `Accepted` → `type: dependency`, `severity:
  major` — do not merge an unresolved or still-`proposed` design decision.
- Test 6 finds a literal (non-placeholder) secret-shaped value anywhere in the diff → `type:
  technical`, `severity: critical` — do not merge under any circumstance; escalate immediately per
  the Immutable Security Constraints in `.claude/rules/security-guidelines.md`.
- CI does not go green after pushing/opening the MR → `type: technical`, `severity: major`, do not
  merge, investigate the specific failing job before retrying.

Max 2 retries before escalating to the user with full context (what was tried, exact failure).

## Git workflow
1. Check out `feature/T389-mcp-merge-provenance-tracking` at its current tip.
2. Run the verification bar (all 6 commands above); tech-lead reviews the diff and issues VERDICT.
3. On `PASS`/`CONDITIONAL_PASS`: `git push -u origin feature/T389-mcp-merge-provenance-tracking`.
4. Open a merge request targeting `develop`, title referencing T389-T392 (e.g. "feat(mcp): MCP merge
   provenance tracking — sidecar pruning + bootstrap bridge (T389-T392)").
5. Wait for CI to report green on the MR. Do not merge before CI completes.
6. Merge via squash-and-merge (standard for `feature/*` branches per `git-workflow.md`).
7. Delete the merged branch (normal cleanup per the Worktree Lifecycle in `git-workflow.md`) — at this
   point T389-T392 are all merged; only `docs/tasks/task-T382.md`'s own separate `chore/T382-*` branch
   (created fresh from post-merge `develop`) remains to complete this plan's goal.
8. Confirm post-merge `develop` tip re-passes verification commands 1-4 (re-run them on fresh
   `develop`, not just trust the pre-merge branch state).

## Constraints
- Token budget: ≤12k tokens.
- No source file edits in this task.
- Never commit directly to `develop` or `main` — only merge via the reviewed MR.
