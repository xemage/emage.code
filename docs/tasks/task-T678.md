# T678 — Cursor removal step S2: live docs, knowledge text and templates (ADR-010)

**ID:** T678
**Owner:** technical-writer
**Status:** pending
**Priority:** P1
**Tier:** standard
**Depends on:** T662
**Affects:** —
**Created:** 2026-10-16
**Completed:** —
**Based on:**
- `docs/plans/plan-123-post-release-follow-ups.md` (Addendum of 2026-10-16: T678)
- `docs/decisions/ADR-010-drop-cursor-platform-support.md` (accepted 2026-10-16), `docs/artifacts/cursor-removal-inventory-v1.md`
- The user's decisions of 2026-10-16 (AskUserQuestion, verbatim option labels): "v9.0.0 (MAJOR), no deprecation release (Recommended)", "B: error plus read-only notice, never delete (Recommended)", "Yes, delete both trees (Recommended)", "Accept all four defaults (Recommended)"

## 1. What and why

Step S2 of ADR-010: edit the live docs, the seven knowledge files and their generated mirrors (regenerate with sync.mjs and the registry script; the technical-writer has no shell, so the orchestrator commits and runs the generators), `docs/releases/_template.md` (row 23 removed), the `.gitlab` templates, `CONTRIBUTING.md` and the platform-count words (ADR-010 D1 and V16, including `skillify.md` lines 50-53), per the ADR's allow-list; keep the draft migration text of Appendix A for the v9.0.0 release document; historical records stay untouched. Declare the root drift. Acceptance: the ADR's allow-list grep shows no Cursor reference outside historical records and the migration text; all gates and the suite pass; a Security Engineer read of the changed security statements.

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
