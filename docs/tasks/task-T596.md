# T596 — Apply the P32 path-conventions ruling (plan path and release notes)

**ID:** T596
**Owner:** backend-developer
**Status:** in_review
**Priority:** P2
**Tier:** mechanical
**Affects:** skill/plan-approve-execute, skill/project-planning, skill/release-workflow, skill/validation-gates, agent/orchestrator, agent/poc-orchestrator, command/new-feature, command/new-project
**Depends on:** T595
**Created:** 2026-10-08
**Based on:**
- `docs/artifacts/path-conventions-v3.md`, **the single implementation input**. It holds 12 four-backtick fences
  (P-1 to P-10, R-1 to R-3; P-8/P-9 is one pair applied to two templates) and the hit counts.
- `docs/plans/plan-108-path-conventions.md` §4
- The user's decisions of 2026-10-08: Q-P32a "plan-<NNN>-<slug>.md (Recommended)"; Q-P32b "One, at docs/releases/
  (Recommended)".

## 1. What

Apply all 12 fences **verbatim**: 13 applications across 10 files.

- **Knowledge files** (under `implementation/knowledge/`):
  - `skills/plan-approve-execute/SKILL.md`: P-1, P-2
  - `agents/orchestrator.md`: P-3
  - `commands/new-feature.md`: P-4
  - `commands/new-project.md`: P-5
  - `skills/project-planning/SKILL.md`: P-6
  - `agents/poc-orchestrator.md`: P-7
  - `skills/validation-gates/SKILL.md`: P-10
  - `skills/release-workflow/SKILL.md`: R-1, R-2, R-3
- **Templates:** `implementation/docs/plans/_template.md` and `docs/plans/_template.md`, both by the P-8/P-9 pair.

How to apply:
- Extract each pair from the v3 fences with a script; do not retype them.
- Apply each pair with exact Python string replacement.
- Assert that each Before occurs exactly once in its target and that each file changes.
- Never reword. If an anchor is missing or not unique, stop and report it as a blocker.

## 2. Then regenerate and declare

1. Run `node implementation/scripts/sync.mjs --root implementation`, then
   `python3 implementation/scripts/generate-registry.py`.
2. Run `python3 -m tests.functional.test_root_install_parity --print-drift`. Declare exactly the printed paths in
   `tests/_baselines/root-install-drift.json`. Do not refresh the repo root.
   - If `implementation/docs/plans/_template.md` projects to the root, its path appears there too.

## 3. Verification (report every result)

- **Per file:** base + edits == new, and nothing else changed.
- **Hit counts:** every v3 count, as both lines and occurrences.
- **Gates:**
  - `sync.mjs --check`
  - `generate-registry.py --check`
  - `check-maturity.py --root implementation`
  - `scripts/scorecard.py --check` (must report 34 / 26 / 0)
  - `validate-tasks.py`
- **Golden:** no file under `tests/golden/` changes. The evaluator-hash tests stay green against **v17**. Golden
  realignment is FU-P32-G, a separate task.
- **Suite:** run `python3 tests/run.py` with output redirected to a file. Expect 904 tests and 0 failures.

## 4. Constraints

- **Write scope:**
  - the eight knowledge files;
  - the two plan templates;
  - the regenerated mirrors and registry;
  - the drift baseline;
  - this brief's `**Status:**` line.
- **Do not touch:**
  - anything under `tests/golden/` (never open `tests/golden/held-out/`);
  - `scripts/` and the evaluator-hash files;
  - `.env*`, credential or key files (do not read them).
- **Commit:** one Conventional Commit, ending with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- **Do not push. Never run `glab mr merge` or any merge/approve API, with no exception.**

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity
(`critical` | `major` | `minor`).
