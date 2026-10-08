# T599 — Apply the P33 ruling (PoC root, Debt Inventory severity, narrative register, debt-ledger security rule)

**ID:** T599
**Owner:** backend-developer
**Status:** in_review
**Priority:** P2
**Tier:** mechanical
**Affects:** instruction/poc-guidelines, agent/poc-orchestrator, agent/technical-debt-narrator, skill/technical-debt-tracking
**Depends on:** T598
**Created:** 2026-10-08
**Based on:**
- `docs/artifacts/poc-guidelines-owner-items-v2.md`: **the single implementation input.** It holds eight
  four-backtick fences, each a `Before:`/`After:` pair, plus the hit-count table.
- `docs/artifacts/security-review-poc-guidelines-owner-items-v1.md`. Applying v2 verbatim satisfies its conditions
  SEC-001 and SEC-002.
- `docs/plans/plan-110-poc-guidelines-owner-items.md` §4
- The user's decisions of 2026-10-08:
  - Q-A "PoC's own top dir (Recommended)"
  - Q-B "Add Severity column (Recommended)"
  - Q-C "Required, by narrator (Recommended)"

## 1. What

Apply all eight v2 edits **verbatim**:

| Edit | File (`implementation/knowledge/…`) |
|---|---|
| E-A2, E-B1-table, E-B1-rule, E-C1 | `instructions/poc-guidelines.md` (stable tier 1; user-decided) |
| E-A2-b | `agents/poc-orchestrator.md` |
| E-B1-b, E-O3 | `skills/technical-debt-tracking/SKILL.md` |
| E-D1 | `agents/technical-debt-narrator.md` |

- Extract each pair from the v2 fences with a script. Do not retype any text.
- Apply each pair with exact Python string replacement.
- Assert that each Before occurs exactly once and that each file changes.
- Never reword. If an anchor is missing or not unique, stop and report it as a blocker.

## 2. Then regenerate and declare

1. Run `node implementation/scripts/sync.mjs --root implementation`, then
   `python3 implementation/scripts/generate-registry.py`.
2. Run `python3 -m tests.functional.test_root_install_parity --print-drift`. Declare exactly the paths it prints in
   `tests/_baselines/root-install-drift.json`. Do not refresh the repo root.

## 3. Verification (report every result)

- **Per file:** the base file with the edits applied equals the new file, and nothing else changed.
- **Hit counts:** every v2 count, as both lines and occurrences.
- **Gates:**
  - `sync.mjs --check`
  - `generate-registry.py --check`
  - `check-maturity.py --root implementation`
  - `scripts/scorecard.py --check` (must report 34 / 26 / 0)
  - `validate-tasks.py`
- **Golden:** no file under `tests/golden/` changes, and the evaluator-hash tests stay green against **v18**.
- **Suite:** run `python3 tests/run.py`, redirected to a file. Expect 904 tests and 0 failures.

## 4. Constraints

- **Write scope:**
  - the four knowledge files;
  - the regenerated mirrors and registry;
  - the drift baseline;
  - this brief's `**Status:**` line.
- **Forbidden:**
  - anything under `tests/golden/`; never open `tests/golden/held-out/`;
  - `scripts/` and the evaluator-hash files;
  - reading `.env*`, credential or key files.
- **Commit:** one Conventional Commit, ending with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- **Do not push. Never run `glab mr merge` or any merge/approve API, with no exception.**

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity
(`critical` | `major` | `minor`).
