# T692 — Rule where TECHNICAL-DEBT.md lives (RO621-N-2) and accept RO621-N-1

**ID:** T692
**Owner:** devops-engineer
**Status:** done
**Priority:** P2
**Tier:** standard
**Depends on:** T687
**Affects:** —
**Created:** 2026-10-24
**Completed:** 2026-10-24
**Based on:**
- `docs/plans/plan-123-post-release-follow-ups.md` (Addendum of 2026-10-24: T692)
- The user's decisions of 2026-10-24 (replies to the decision list of `docs/artifacts/tracked-debt-register-v2.md` section 5.2): "Accept N-1. Rule N-2 in one sentence (choose best location)."
- `docs/artifacts/tracked-debt-register-v2.md` (RO621-N-1, RO621-N-2)

## 1. What and why

RO621-N-1 (`technical-debt-narrator.md:46` names the legacy `DEBT:` tag format, which `poc-guidelines.md` says is superseded) is accepted by the user as harmless: no change. RO621-N-2: no document states where `TECHNICAL-DEBT.md` lives. The ruling (the orchestrator\'s choice, delegated by the user): it lives in the **PoC root**, the same directory as `POC-DEBT-SCORECARD.md` (the top-level directory of the PoC\'s code: the repository root when the PoC has its own repository, otherwise the directory that the PoC plan names as the PoC root; each PoC has its own file), because the narrative register and the scorecard describe the same PoC and the same inheriting team, and `poc-guidelines.md` already defines the PoC root for the scorecard. State it in one sentence in `implementation/knowledge/instructions/poc-guidelines.md` (the section "Narrative Debt Register (`TECHNICAL-DEBT.md`)") and in `implementation/knowledge/agents/technical-debt-narrator.md` (the output line, ~14), regenerate (`node implementation/scripts/sync.mjs --root implementation`, `python3 implementation/scripts/generate-registry.py`), declare the root drift (do not refresh the root install), and check the tests that pin these texts (including `tests/golden/**` fixtures only by reading: **do not modify `tests/golden/**`**; if a golden case pins the changed sentence, stop and report). *Acceptance:* the sentence is in both files and their projections; the registry and mirrors are regenerated; all gates and the suite pass; the scorecard and the evaluator hash show no drift.

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
