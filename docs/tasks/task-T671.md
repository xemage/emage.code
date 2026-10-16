# T671 — Tracked-debt register

**ID:** T671
**Owner:** tech-lead
**Status:** pending
**Priority:** P1
**Tier:** judgment
**Depends on:** —
**Affects:** —
**Created:** 2026-10-16
**Completed:** —
**Based on:**
- `docs/plans/plan-123-post-release-follow-ups.md` (Task Decomposition item for T671; the section "Grant G-2" for T668 and T669)
- `docs/checkpoints/checkpoint-038-release-v8.0.0.md` (section 3), `docs/releases/v8.0.0.md` (Known issues), the review artifacts named in the item
- The user's words of 2026-10-16: "I want to drop Cursor support completely" (T661, T662); "Regarding baseline v22: approving it" (T668 to T670); the approval of plan-123 (AskUserQuestion, verbatim option label): "Approve as written (Recommended)"

## 1. What and why

Tracked-debt register (tech-lead): consolidate every tracked low-severity item scattered across the review artifacts and the release document into one register `docs/artifacts/tracked-debt-register-v1.md` (id, source artifact, grade, location, one-line description, proposed disposition: fix in T672 to T677, fix elsewhere, accept, close as obsolete). Sources include the T633 findings SEC-004 to SEC-015, T636 L6 and L7, T619 and T620 residuals (SEC-T619-05, the T620 JWT and scanner items), T635 SEC-T635-01 to -04, T640 SEC-T640-01 to -04, T646 SEC-T646-02 to -06, T650 SEC-T650-02 to -05, T655 SEC-T655-04 to -10, T657 SEC-T657-04, -07, -09, T658 SEC-T658-02 to -07, T660 SEC-T660-02 to -07, TL-T649-01 to -20, QA-T648-01 to -04, the T621 observations, the T634 severity-scale reference page that was never created, stale component counts in README and wiki, and the plan-112 parked notes. Items already fixed are marked closed with the evidence. *Acceptance:* the register; every id in the release document's K-18 appears in it.

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
