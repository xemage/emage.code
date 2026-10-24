# T693 — Apply the ruling on the release self-review (P112-P41-O1, option A+)

**ID:** T693
**Owner:** devops-engineer
**Status:** pending
**Priority:** P2
**Tier:** standard
**Depends on:** T691
**Affects:** —
**Created:** 2026-10-24
**Completed:** —
**Based on:**
- `docs/plans/plan-123-post-release-follow-ups.md` (Addendum of 2026-10-24: T693)
- `docs/artifacts/ruling-p112-p41-o1-release-self-review-v1.md` (the ruling; section 5.1 hunks E1 to E3 and section 5.2 the task shape)
- The user's decision of 2026-10-24: "O1 have the Solution Architect rule on it" (the user may overrule the ruling before this task starts)

## 1. What and why

Apply the Solution Architect's ruling A+ on P112-P41-O1 verbatim (`docs/artifacts/ruling-p112-p41-o1-release-self-review-v1.md` section 5.1, hunks E1 to E3 by exact Before text): Release Gate Policy item 5 in `implementation/knowledge/agents/release-manager.md` (~line 45: a named independent check of the release document, with the commit it covered, and the statement that the verdict is an input to the top-level session's verification and the user's tag approval), a Gate Inputs row in `release-manager.md` (~line 173) and a pointer bullet in `implementation/knowledge/agents/orchestrator.md` (~line 217). **Stop and report if a Before text is missing or not unique.** Run the pre-flight of section 5.2 first (counts only: `grep -rnF` of the Before lines and of "Release document, independent check" over `implementation/`, `docs/wiki`, `docs/guides`, `README.md`, `CONTRIBUTING.md` and `tests/`; a non-golden hit is a `dependency` blocker; read `tests/functional/` tests that pin `release-manager` or `orchestrator` text; never open `tests/golden/held-out/`). No edit to `validation-gates`, any command, `AGENTS.md`, `tests/golden/**` or `scripts/scorecard.py`. Regenerate (`node implementation/scripts/sync.mjs --root implementation`, `python3 implementation/scripts/generate-registry.py`), declare the root drift (do not refresh the root install), add an anchored test for the three hunks with a mutation proof. Knowledge edits to agents can change the scorecard or the evaluator hash inputs: if `scripts/scorecard.py --check` or the evaluator hash reports drift, STOP and report. *Acceptance:* the three hunks in both files and all projections; registry and mirrors regenerated; all gates and the suite pass; a Security Engineer read of the changed gate text follows. **Start only after the user has had the chance to overrule the ruling.**

## 2. Output

As stated in section 1.

## 3. Constraints

- Work in your own worktree/branch; one Conventional Commit ending with `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`. Do not push; do not merge; never create, push or delete a tag or release; never use or print `WIKI_TOKEN`; do not edit `docs/tasks/active-tasks.md`, `completed-tasks.md` or any brief's Status line. Agents without a shell (solution-architect, technical-writer) write their artifact text for the orchestrator to commit.
- Gates for any change under `implementation/`, `scripts/` or `tests/`: `node implementation/scripts/sync.mjs --root implementation --check`, `python3 implementation/scripts/generate-registry.py --check`, `python3 implementation/scripts/check-maturity.py --root implementation`, `python3 scripts/scorecard.py --check`, `python3 docs/tasks/validate-tasks.py`, the evaluator hash (`check_evaluator_hash()`, no drift unless the brief says otherwise), `python3 -m unittest tests.functional.test_golden_held_out_isolation`, and the full suite `python3 tests/run.py > file` (summary lines). Declare root drift in `tests/_baselines/root-install-drift.json` (sorted `python3 -m tests.functional.test_root_install_parity --print-drift` paths plus one comment line starting `Declared <date> by <task> (`); do NOT refresh the root install.
- Never open `tests/golden/held-out/`; never write a held-out case id anywhere; only T668 may modify `tests/golden/**` (grant G-2). No `.env*` or credential files (the primary checkout has an untracked local `.env` that must not be read or grepped); do not read the user's local `.claude/settings*.json` or `.vscode/mcp.json`. Mark anything you did not verify **(unverified)**.

## 4. Acceptance criteria

As stated in section 1.

## 5. Blocker protocol



Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
