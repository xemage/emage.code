# T587 — Apply the security-gate alignment ruling (FU-6, FU-7)

**ID:** T587
**Owner:** backend-developer
**Status:** pending
**Priority:** P2
**Tier:** mechanical
**Affects:** agent/security-engineer, skill/validation-gates, skill/receiving-code-review
**Depends on:** T586
**Created:** 2026-10-08
**Based on:**
- `docs/artifacts/security-gate-alignment-v2.md`: **the single implementation input.** §3 holds the seven edits with
  full Before/After text, and §7 the implementation checks and hit counts.
- `docs/artifacts/security-review-security-gate-alignment-v1.md`. Its conditions C1 and C2 are satisfied by applying
  v2 verbatim; the orchestrator verifies this before merge.
- `docs/plans/plan-103-security-gate-alignment.md` §4

## 1. What

Apply the seven edits in v2 §3 **verbatim** to `implementation/knowledge/`:

| Edit | File |
|---|---|
| FA1, FC1, FC3, FC2 | `agents/security-engineer.md` |
| FB1, FD1 | `skills/validation-gates/SKILL.md` |
| F7 | `skills/receiving-code-review/SKILL.md` |

Use exact Python string replacement. Assert that each Before occurs exactly once and that each file changes. Never
reword. If an anchor is missing or not unique, stop and report it as a blocker.

## 2. Then regenerate and declare

1. Run `node implementation/scripts/sync.mjs --root implementation` and
   `python3 implementation/scripts/generate-registry.py`.
2. Run `python3 -m tests.functional.test_root_install_parity --print-drift` and declare exactly the printed paths in
   `tests/_baselines/root-install-drift.json`. Do not refresh the repo root. Report the count.

## 3. Verification (report every result)

- **Per edit:** `old.replace(Before, After) == new`, with nothing else in the file changed.
- **Hit counts:** every v2 §7 count, giving both the line count and the occurrence count. That includes the rows that
  must read 0 afterwards, and `grep -cxF '2. The assignee addresses all critical and high findings.'` returning 0.
- **Gates:**
  - `sync.mjs --check`
  - `generate-registry.py --check`
  - `check-maturity.py --root implementation`
  - `scripts/scorecard.py --check` (must stay 34 / 26 / 0)
  - `docs/tasks/validate-tasks.py`
- **Golden:** no file under `tests/golden/` changes, and the evaluator-hash tests stay green against v16.
- **Suite:** run `python3 tests/run.py`, redirecting output to a file (never `| tail`). Expect 904 tests and 0
  failures.

## 4. Constraints

- **Write scope:**
  - the three knowledge files;
  - the regenerated `implementation/.<platform>/` mirrors and `implementation/registry/index.json`;
  - `tests/_baselines/root-install-drift.json`;
  - this brief's `**Status:**` line.
- **Do not touch** anything under `tests/golden/`; never open `tests/golden/held-out/`. Also leave
  `scripts/scorecard.py` and the evaluator-hash files alone, and never read `.env*`, credential or key files.
- **Commit:** work only in the assigned worktree and commit locally as one Conventional Commit ending with
  `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. **Do not push. Never run `glab mr merge` or any
  merge/approve API, with no exception.**

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity
(`critical` | `major` | `minor`). Allow at most 2 retries before escalating. Never fail silently.
