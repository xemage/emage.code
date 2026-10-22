# T674 — Documentation corrections (tracked debt)

**ID:** T674
**Owner:** technical-writer
**Status:** pending
**Priority:** P2
**Tier:** standard
**Depends on:** T671
**Affects:** —
**Created:** 2026-10-16
**Completed:** —
**Based on:**
- `docs/plans/plan-123-post-release-follow-ups.md` (Task Decomposition item for T674; the section "Grant G-2" for T668 and T669)
- `docs/checkpoints/checkpoint-038-release-v8.0.0.md` (section 3), `docs/releases/v8.0.0.md` (Known issues), the review artifacts named in the item
- The user's words of 2026-10-16: "I want to drop Cursor support completely" (T661, T662); "Regarding baseline v22: approving it" (T668 to T670); the approval of plan-123 (AskUserQuestion, verbatim option label): "Approve as written (Recommended)"

## 1. What and why

Documentation corrections (technical-writer; the orchestrator commits): SEC-T660-03 (list the operator controls `GITLAB_PERMISSION_MODE`, `GITLAB_DENIED_TOOLS_REGEX`, `GITLAB_ALLOWED_PROJECT_IDS`), SEC-T660-07 (the Pi omission and the default `core` toolset sentence), SEC-T655-09, SEC-T657-08, SEC-T658-03 and -04, TL-T649-10 (the `release-workflow` skill template title: a knowledge edit, so the projections change), the T634 severity-scale reference page `docs/wiki/severity-and-grade-scales.md`, stale component counts.

## 2. Output

As stated in section 1.

## 3. Constraints

- Work in your own worktree/branch; one Conventional Commit ending with `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`. Do not push; do not merge; never create, push or delete a tag or release; never use or print `WIKI_TOKEN`; do not edit `docs/tasks/active-tasks.md`, `completed-tasks.md` or any brief's Status line. Agents without a shell (solution-architect, technical-writer) write their artifact text for the orchestrator to commit.
- Gates for any change under `implementation/`, `scripts/` or `tests/`: `node implementation/scripts/sync.mjs --root implementation --check`, `python3 implementation/scripts/generate-registry.py --check`, `python3 implementation/scripts/check-maturity.py --root implementation`, `python3 scripts/scorecard.py --check`, `python3 docs/tasks/validate-tasks.py`, the evaluator hash (`check_evaluator_hash()`, no drift unless the brief says otherwise), `python3 -m unittest tests.functional.test_golden_held_out_isolation`, and the full suite `python3 tests/run.py > file` (summary lines). Declare root drift in `tests/_baselines/root-install-drift.json` (sorted `python3 -m tests.functional.test_root_install_parity --print-drift` paths plus one comment line starting `Declared <date> by <task> (`); do NOT refresh the root install.
- Never open `tests/golden/held-out/`; never write a held-out case id anywhere; only T668 may modify `tests/golden/**` (grant G-2). No `.env*` or credential files (the primary checkout has an untracked local `.env` that must not be read or grepped); do not read the user's local `.claude/settings*.json` or `.vscode/mcp.json`. Mark anything you did not verify **(unverified)**.

## 3a. Carried from the T665 and T672 reviews

- README and wiki: the config merge is done on `--update` AND on a plain install over an existing config (T672); document the new on-disk names (`.<name>.<random>.tmp`, `<ledger>.bak`, `<tree>.emage-new.<pid>` / `.emage-old.<pid>`) in the wiki.
- The full operator-controls text (SEC-T660-03) still owns `GITLAB_DENIED_TOOLS_REGEX` and `GITLAB_ALLOWED_PROJECT_IDS`; `GITLAB_PERMISSION_MODE=modify` is now generated (T665).
- Documentation tests (T673) read sentences with counts in `AGENTS.md`, `implementation/AGENTS.md`, the wiki and `PREREQUISITES.md`: keep the counts and holder lists in step with the agent sources.

## 4. Acceptance criteria

As stated in section 1.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
