# Task T376 — Verify/regenerate already-affected rendered `AGENTS.md` output

**ID:** T376
**Owner:** devops-engineer
**Status:** done
**Priority:** P1
**Depends on:** T375
**Created:** 2026-08-09
**Based on:** docs/plans/plan-032-render-agents-cline-platform-map-fix.md (P032-04)

This brief is self-contained. You do not need to read plan-032 or T373/T374/T375's briefs to
execute this task.

## Objective
T373 fixed `scripts/render_installed_agents.py` so `--platform all` renders now include Cline.
That fix only changes the *script's future behavior* — it does not by itself touch any
already-committed file. This repository self-hosts its own install at its root (root `AGENTS.md`
is itself an installed/rendered artifact, refreshed by `scripts/install.sh --target . --platform
all --update`, most recently in T372). Determine whether root `AGENTS.md`
(`/home/emage/Code/emage/emage.code/AGENTS.md`) currently reflects the fixed generator's output,
and if not, regenerate exactly that one file through the normal branch + MR flow.

**Orchestrator's pre-investigation finding (verify independently, do not just trust this) — as of
2026-08-09, before T373 has landed:** root `AGENTS.md` is only PARTIALLY correct today, not fully
protected as earlier analysis assumed. Confirmed by direct `grep` against the current file:
- Line ~89, the "Knowledge Base" bullet ("Use the installed platform folders...") — DOES already
  contain `.clinerules/` and `.cline/` (hand-added in T356, unrelated to the generator bug).
- Line ~60 ("Skill Workflow"), line ~74 ("Code Standards"), line ~80 ("Security"), and line ~93
  ("MCP Servers") — do NOT contain any Cline reference at all today. Confirmed directly:
  ```
  grep -c '`\.cline/skills/`' AGENTS.md            # → 0
  grep -c '`\.clinerules/coding-standards\.md`' AGENTS.md   # → 0
  grep -c '`\.clinerules/security-guidelines\.md`' AGENTS.md # → 0
  grep -c '`\.cline/mcp\.json`' AGENTS.md          # → 0
  ```
  All four currently print `0`. This means 4 of the 5 sections T373 fixes are genuinely missing
  Cline in the committed root `AGENTS.md` right now — this is not just a "protected by a prior
  revert, no action needed" situation for those four sections. Re-run these exact `grep` commands
  yourself against `develop`'s current tip before concluding anything — repo state may have
  changed since this brief was written.

## Inputs
- `develop` post-T375 merge (check out fresh — do not reuse a pre-merge worktree).
- `/home/emage/Code/emage/emage.code/AGENTS.md` (repo root — the file you may regenerate).
- `/home/emage/Code/emage/emage.code/implementation/AGENTS.md` (canonical source template read by
  the renderer — read-only reference, never edit).
- `scripts/render_installed_agents.py` (post-T373 fix — read-only reference, do not edit).
- `docs/tasks/task-T372.md` (prior task's execution notes — documents the earlier revert of this
  exact regression and the discovery that led to this plan; read-only reference).

## Allow-list (files you may touch)
- `/home/emage/Code/emage/emage.code/AGENTS.md` (repo root) — ONLY if the dry-run diff in Step 1
  below shows a real difference, and only by running the exact render command in Step 2 (never by
  hand-editing prose).

## Deny-list (do not touch — no exceptions)
- Do NOT edit `implementation/AGENTS.md` — that is the canonical source, not the rendered output;
  it is unaffected by this bug (confirmed by plan-032's investigation: `diff` between it and root
  `AGENTS.md` shows only expected canonical-vs-rendered wording differences, unrelated to Cline).
- Do NOT edit `scripts/render_installed_agents.py` or any test file — those are closed by T373/
  T374/T375; this task only verifies/regenerates root `AGENTS.md`, it does not touch the generator
  itself again.
- Do NOT run the full installer (`scripts/install.sh --target . --platform all --update`) for this
  task. That command touches every platform tree (`.github/`, `.cursor/`, `.gemini/`, `.opencode/`,
  `.pi/`, `.claude/`, `.cline/`, `.clinerules/`) and both MCP JSON files
  (`.vscode/mcp.json`, `.mcp.json`) — all of which T372 already confirmed are current and
  unaffected by this specific bug. Re-running the full installer risks reintroducing unrelated
  collateral (T372 had to revert `.claude/settings.json` and `AGENTS.md` collateral from exactly
  this class of full-installer run). Use the narrower, single-file render command in Step 2
  instead — it touches only `AGENTS.md` and nothing else on disk.
- Do NOT hand-edit `AGENTS.md` prose directly, even to "fix" the same Cline gap manually. The only
  correct source of truth is the generator's output — apply it via the command in Step 2, never by
  typing replacement text yourself.
- Do NOT create any new file.
- Do NOT commit directly to `develop` or `main` — this is a real mutation of a committed file in
  this repo's own root and goes through the normal branch + MR flow, same as any other change
  (per `.claude/rules/git-workflow.md`, and per T372's own explicit precedent of treating root
  self-install changes as non-exempt from branch policy).

## Step 1 — Dry-run comparison (always do this first, regardless of expected outcome)
Run from repo root `/home/emage/Code/emage/emage.code`, on a fresh checkout of `develop` post-T375
merge:
```
mkdir -p /tmp/t376-check
python3 scripts/render_installed_agents.py --source implementation/AGENTS.md --dest /tmp/t376-check/AGENTS-all.md --platform all
diff AGENTS.md /tmp/t376-check/AGENTS-all.md
```
This does NOT modify `AGENTS.md` — it only writes to the scratch path `/tmp/t376-check/` and
diffs. Capture the full `diff` output; you will need it for Step 3 either way.

## Step 2 — Regenerate (only if Step 1's diff is non-empty)
If the diff in Step 1 is empty, skip this step entirely and go to Step 3 with "no regeneration
needed" as your finding.

If the diff is non-empty, apply the fixed render directly to `AGENTS.md` (this is the ONLY
sanctioned way to modify it in this task):
```
python3 scripts/render_installed_agents.py --source implementation/AGENTS.md --dest AGENTS.md --platform all
git diff AGENTS.md
```
Review the resulting `git diff AGENTS.md` line by line. It must show ONLY: additions/changes that
add Cline-related content to the five sections named in T373's objective (Skill Workflow, Code
Standards, Security, Knowledge Base, MCP Servers). If the diff shows anything else — wording
changes unrelated to Cline, reordering of unrelated content, deletion of hand-written prose that
isn't part of the five templated sections — STOP and report a blocker (see below) rather than
committing an unexpected diff.

## Step 3 — State the finding plainly
Your task report must say explicitly one of:
- **"No regeneration needed."** — with the empty `diff` output from Step 1 as evidence.
- **"Regeneration needed and applied."** — with the non-empty `diff` output from Step 1 (before)
  and the final `git diff AGENTS.md` (after regeneration) as evidence, listing exactly which of
  the five sections changed.

## Tests to run (literal commands, run from repo root, after Step 2 if you regenerated, or after
Step 1 if you did not)
1. If you regenerated `AGENTS.md`, re-confirm the four previously-missing strings are now present:
   ```
   grep -c '`\.cline/skills/`' AGENTS.md
   grep -c '`\.clinerules/coding-standards\.md`' AGENTS.md
   grep -c '`\.clinerules/security-guidelines\.md`' AGENTS.md
   grep -c '`\.cline/mcp\.json`' AGENTS.md
   ```
   PASS = every `grep -c` prints `1` (was `0` before your change, per the pre-investigation finding
   above — re-verify your own "before" state, don't assume it matches this brief exactly).
2. Full verification bar (same 4 commands T375 already ran on the fix — re-run them now against
   post-regeneration `develop`/your branch state to confirm nothing else broke):
   ```
   make verify
   python3 implementation/scripts/generate-registry.py --root implementation --check
   python3 docs/tasks/validate-tasks.py
   python3 tests/run.py
   ```
   PASS = all four exit 0, matching the same PASS conditions documented in T375's brief (`make
   verify` → "no drift"; `generate-registry.py --check` → "registry is up to date";
   `validate-tasks.py` → starts with `TASK LEDGER: PASS`; `tests/run.py` → exits 0).

## Acceptance criteria (all must be true)
- [ ] Step 1's dry-run diff was executed and its full output captured, before any file was
      written to `AGENTS.md`.
- [ ] The finding is stated plainly per Step 3, with the actual diff output as evidence — not a
      vague "looks fine" or "probably fine" statement.
- [ ] If regeneration was needed: `git diff` (final, on your branch) touches exactly one file,
      `AGENTS.md`, and every changed line is attributable to one of the five Cline-related
      sections named above — no unrelated content changed.
- [ ] If regeneration was needed: the four `grep -c` checks in "Tests to run" step 1 all print `1`.
- [ ] The full verification bar (4 commands) passes after any change (or, if no regeneration was
      needed, passes on `develop`'s current tip as confirmation nothing is broken).
- [ ] If regeneration was needed, it was committed via branch + MR (never a direct commit to
      `develop`) — see Git workflow below.

## Blocker protocol
STOP and report a blocker (do not improvise a different fix) if:
- `develop` post-T375 merge does not actually contain T373's/T374's fix (e.g. the four `grep -c`
  checks against a fresh render still print `0` even from
  `scripts/render_installed_agents.py` directly) → `type: dependency`, `severity: critical` — T376
  cannot proceed if T375 hasn't actually landed the fix.
- Step 2's `git diff AGENTS.md` shows anything beyond the five expected Cline-related sections
  (unrelated wording changes, deleted hand-written prose, reordering) → `type: technical`,
  `severity: major` — do not commit an unexpected diff; report the exact unexpected lines.
- Any verification command in "Tests to run" step 2 fails → `type: technical`, `severity: major`,
  include exact command output; do not attempt an ad-hoc fix outside this task's allow-list.
- You find a third committed `AGENTS.md`-type file beyond root `AGENTS.md` and
  `implementation/AGENTS.md` (re-run `find . -name AGENTS.md -not -path './.git/*'` from repo root
  to check) → `type: unclear_requirements`, `severity: minor` — this task's scope only covers the
  two files named in Inputs; a third file was not anticipated by this plan and needs orchestrator
  disposition before you touch it.

Max 2 retries before escalating to the orchestrator with full context.

## Git workflow
1. Create branch `chore/T376-verify-regenerate-agents-md` from the current tip of `develop` (post
   T375 merge).
2. Run Step 1 (dry-run diff) immediately, before any edit.
3. If regeneration is needed, run Step 2, review the diff, run the verification bar.
4. If regeneration was needed, commit with a Conventional Commit message, e.g.:
   ```
   chore(docs): regenerate root AGENTS.md with Cline platform refs

   scripts/render_installed_agents.py's `all` branch omitted Cline from its
   platform-reference strings until T373 fixed it. Root AGENTS.md (this repo's
   own self-hosted install) predates that fix in 4 of its 5 templated sections
   (Skill Workflow, Code Standards, Security, MCP Servers — the Knowledge Base
   section already had Cline from T356's hand-authored documentation pass).
   Regenerated via `render_installed_agents.py --platform all` against the
   fixed generator; no other file changed.

   Refs T376
   ```
   If no regeneration was needed, do not create an empty commit — report the "no regeneration
   needed" finding with evidence and stop; there is nothing to push or merge.
5. If a commit was made: push the branch, open a merge request to `develop` referencing T376, wait
   for CI to go green, then stop — do NOT merge yourself. Report completion to the orchestrator for
   independent re-review and merge (same as every other task in this plan — the orchestrator
   merges after independently re-verifying, not on the strength of this task's own report alone).
6. Do NOT push to `develop` or `main` directly under any circumstance.

## Constraints
- Token budget: ≤8k tokens.
- File ownership: `AGENTS.md` (repo root) only, and only via the Step 2 render command.
- This task does not cut a new release/version tag.
