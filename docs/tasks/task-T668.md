# T668 — Golden realignment B under grant G-2 (prepare-release and /skillify cases)

**ID:** T668
**Owner:** qa-engineer
**Status:** pending
**Priority:** P1
**Tier:** judgment
**Depends on:** —
**Affects:** —
**Created:** 2026-10-16
**Completed:** —
**Based on:**
- `docs/plans/plan-123-post-release-follow-ups.md` (Task Decomposition item for T668; the section "Grant G-2" for T668 and T669)
- `docs/checkpoints/checkpoint-038-release-v8.0.0.md` (section 3), `docs/releases/v8.0.0.md` (Known issues), the review artifacts named in the item
- The user's words of 2026-10-16: "I want to drop Cursor support completely" (T661, T662); "Regarding baseline v22: approving it" (T668 to T670); the approval of plan-123 (AskUserQuestion, verbatim option label): "Approve as written (Recommended)"

## 1. What and why

Golden realignment B under grant **G-2** (qa-engineer), approved by the user together with baseline v22 (see "Grant G-2" below). Items: (1) the open `prepare-release-real-verdict-missing` case: `status: expected_pass`, drop the two `known_failing_*` keys, replace its fixture `fixture/docs/releases/v7.0.1.md` by a byte-identical copy of the now-published `docs/releases/v8.0.0.md`, rewrite the brief's history sections; `expect.py` unchanged since G-1; (2) the open `skillify-skill-file-template-drift` case (item 11 of G-1, deferred): `status: expected_pass`, drop the two `known_failing_*` keys, replace the fixture by a byte-identical copy of the generated skill `implementation/knowledge/skills/gitlab-api-push-fallback/SKILL.md` at `fixture/implementation/knowledge/skills/gitlab-api-push-fallback/SKILL.md` (one of the declared skill roots of `expect.py`), delete the old fixture file, rewrite the brief's history sections; `expect.py` unchanged. Controls as in G-1: `check()` byte-identical, before/after results, discrimination probes on scratch copies, scorecard before (34 / 28 / 0) and after, the floor check, gates, held-out hygiene (no held-out id anywhere). *Acceptance:* the G-1 control list, reported item by item.

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
