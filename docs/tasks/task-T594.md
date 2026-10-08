# T594 — Apply the P41 ruling (verdict renderings, second vocabularies, project-planning, release executor)

**ID:** T594
**Owner:** backend-developer
**Status:** pending
**Priority:** P2
**Tier:** mechanical
**Affects:** agent/qa-engineer, agent/security-engineer, agent/release-manager, agent/tech-lead, skill/code-review, skill/project-planning, command/prepare-release
**Depends on:** T593
**Created:** 2026-10-08
**Based on:**
- `docs/artifacts/remaining-verdict-renderings-v1.md`: **the single implementation input.** §7 holds the edits as
  fenced Before/After pairs, and §8.2–8.3 hold the hit counts and the mechanics.
- `docs/plans/plan-107-remaining-verdict-renderings.md` §4
- The user's decision of 2026-10-08: Q-G4 "Orchestrator runs, RM decides (Recommended)", i.e. option 1.

## 1. What

Apply these nine edits **verbatim**. Extract each Before/After pair from the artifact §7 fences with a script; do not
retype it.

| Edit | File (`implementation/knowledge/…` unless stated) |
|---|---|
| E-Q1 | `agents/qa-engineer.md` |
| E-S1 | `agents/security-engineer.md` |
| E-R1 | `agents/release-manager.md` (released by the user's Q-G4 decision) |
| E-G6a | `skills/code-review/SKILL.md` |
| E-G6b | `agents/tech-lead.md` |
| E-G7a, E-G7b | `skills/project-planning/SKILL.md` |
| C-G4a | `commands/prepare-release.md` **and** `docs/releases/_template.md` (the same Before/After, once in each file) |
| C-G4b | `commands/prepare-release.md` |

- Apply each edit with exact Python string replacement.
- Assert that each Before occurs exactly once in its target file, and that each file changes.
- Never reword. If an anchor is missing or not unique, stop and report it as a blocker.

## 2. Then regenerate and declare

1. Run `node implementation/scripts/sync.mjs --root implementation`, then
   `python3 implementation/scripts/generate-registry.py`.
2. Run `python3 -m tests.functional.test_root_install_parity --print-drift`. Declare exactly the printed paths in
   `tests/_baselines/root-install-drift.json`. Do not refresh the repo root.

## 3. Verification (report every result)

- **Per file:** base plus the edits equals the new file, and nothing else changed.
- **Hit counts:** every count in artifact §8.2, as both line counts and occurrence counts.
- **Gates:**
  - `sync.mjs --check`
  - `generate-registry.py --check`
  - `check-maturity.py --root implementation`
  - `scripts/scorecard.py --check` (must report 34 / 26 / 0)
  - `validate-tasks.py`
- **Golden:** no file under `tests/golden/` changes, and the evaluator-hash tests stay green against **v17**.
- **Suite:** run `python3 tests/run.py`, redirecting output to a file. Expect 904 tests and 0 failures.

## 4. Constraints

- **Write scope:**
  - the seven knowledge files;
  - `docs/releases/_template.md`;
  - the regenerated mirrors and registry;
  - the drift baseline;
  - this brief's `**Status:**` line.
- **Do not touch:** anything under `tests/golden/` (never open `tests/golden/held-out/`), `scripts/scorecard.py` or
  the evaluator-hash files. Do not read `.env*`, credential or key files.
- **Commit:** one Conventional Commit, ending with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- **Do not push. Never run `glab mr merge` or any merge/approve API, with no exception.**

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity
(`critical` | `major` | `minor`).
