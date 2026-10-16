# T662 — Implement the ADR-010 outcome: remove Cursor support

**ID:** T662
**Owner:** devops-engineer
**Status:** done
**Priority:** P1
**Tier:** judgment
**Depends on:** T661
**Affects:** —
**Created:** 2026-10-16
**Completed:** 2026-10-16
**Based on:**
- `docs/plans/plan-123-post-release-follow-ups.md` (Task Decomposition item for T662; the section "Grant G-2" for T668 and T669)
- `docs/checkpoints/checkpoint-038-release-v8.0.0.md` (section 3), `docs/releases/v8.0.0.md` (Known issues), the review artifacts named in the item
- The user's words of 2026-10-16: "I want to drop Cursor support completely" (T661, T662); "Regarding baseline v22: approving it" (T668 to T670); the approval of plan-123 (AskUserQuestion, verbatim option label): "Approve as written (Recommended)"

## 1. What and why

**Step S1 of `docs/decisions/ADR-010-drop-cursor-platform-support.md` (accepted 2026-10-16: v9.0.0, adopter behaviour B, delete both trees, Pi format value `pi`, pack schema with the six current platforms, no golden edit).** Follow the ADR's task breakdown for S1 and its decisions D1 to D9; commit 1 is the Pi format rename, commit 2 the removal (manifest, both `.cursor` trees via `git rm -r`, installer and renderer per D3 with early `--platform` validation and the read-only notice, registry and pack schema, tests per D6 with an orphan-tree guard), plus the end-to-end scenario against a real `git archive v8.0.0` install. S2 (T678, docs) and S3 (T679, root refresh) are separate rows. Original scope text:

Implement the ADR-010 outcome (devops-engineer, with technical-writer for the docs): remove Cursor from the source tree, generators, installer, tests, docs, registry and root install per the inventory; regenerate; declare the root drift. *Acceptance:* no Cursor references remain outside historical records and the migration note; all gates and the suite pass; a Security Engineer review follows. Depends on T661. If the inventory shows `tests/golden/**` edits are needed, T662 stops at that point and the orchestrator brings a grant (G-3) to the user; those goldens are then folded into a later baseline.

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
