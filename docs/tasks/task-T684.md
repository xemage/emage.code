# T684 — Residual hardening of the T682 review (SEC-T682-03, -04, -06)

**ID:** T684
**Owner:** devops-engineer
**Status:** done
**Priority:** P2
**Tier:** standard
**Depends on:** T682
**Affects:** —
**Created:** 2026-10-22
**Completed:** 2026-10-22
**Based on:**
- `docs/plans/plan-123-post-release-follow-ups.md` (Addendum of 2026-10-22: T684)
- `docs/artifacts/security-review-t682-installer-residuals-v1.md` (SEC-T682-03, -04, -06)

## 1. What and why

Fix the three LOW findings of the T682 review that were deferred (`docs/artifacts/security-review-t682-installer-residuals-v1.md`): SEC-T682-03 (`guard_stale_swap_siblings` display and hint: use the byte-wise `ascii_printable` for the two display lines, print the `%q` token under `LC_ALL=C` so non-ASCII bytes become octal, change the hint to `[ ! -e DEST ] && mv -- OLD DEST`, add a test that runs the hint through `bash -c` for a hostile name (`;`, `$()`, space, newline, a bidi character) and checks that no side effect occurs, add a `%q` mutation), SEC-T682-04 (`sync.mjs`: compare the resolved `mcp.outputFile` and its `.provenance.json` with the generator inputs; resolve with `fs.realpath` of the nearest existing ancestor and compare case-folded forms, or document the limitation in the function comment if accepted), SEC-T682-06 (`merge-task-docs.py`: compute all merged texts first (decode, merge, backup names) and write afterwards; soften the message to "each ledger is either unchanged or fully replaced"; write `.bak` and seeds through the atomic helper). Every fix gets a test and a mutation proof. *Acceptance:* the three findings closed; all gates and the suite pass; a Security Engineer delta review follows.

## 2. Output

As stated in section 1.

## 3. Constraints

- Work in your own worktree/branch; one Conventional Commit ending with `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`. Do not push; do not merge; never create, push or delete a tag or release; never use or print `WIKI_TOKEN`; do not edit `docs/tasks/active-tasks.md`, `completed-tasks.md` or any brief\'s Status line.
- Gates for any change under `implementation/`, `scripts/` or `tests/`: `node implementation/scripts/sync.mjs --root implementation --check`, `python3 implementation/scripts/generate-registry.py --check`, `python3 implementation/scripts/check-maturity.py --root implementation`, `python3 scripts/scorecard.py --check`, `python3 docs/tasks/validate-tasks.py`, the evaluator hash (`check_evaluator_hash()`, no drift), `python3 -m unittest tests.functional.test_golden_held_out_isolation`, and the full suite `python3 tests/run.py > file` (summary lines). Declare root drift in `tests/_baselines/root-install-drift.json`; do NOT refresh the root install.
- Never open `tests/golden/held-out/`; never write a held-out case id anywhere; do not modify `tests/golden/**`. No `.env*` or credential files; do not read the user\'s local `.claude/settings*.json` or `.vscode/mcp.json`. Mark anything you did not verify **(unverified)**.

## 4. Acceptance criteria

As stated in section 1.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
