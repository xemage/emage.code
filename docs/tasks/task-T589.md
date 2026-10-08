# T589 — Apply the security-finding grading and per-MR OWASP ruling (SEC-T586-07)

**ID:** T589
**Owner:** backend-developer
**Status:** done
**Priority:** P2
**Tier:** mechanical
**Affects:** skill/validation-gates, skill/code-review, agent/tech-lead
**Depends on:** T588
**Created:** 2026-10-08
**Based on:**
- `docs/artifacts/security-finding-grading-and-owasp-run-v2.md`, **the single implementation input**. Its four-backtick
  fences hold the three edits, each with its full Before/After text. It also holds the hit-count table.
- `docs/artifacts/security-review-security-finding-grading-v1.md`. Its condition C1 is satisfied by applying v2
  verbatim.
- `docs/plans/plan-104-security-finding-grading-and-owasp-run.md` §4
- The user's decisions of 2026-10-08: Q-a "Pointer (Recommended)"; Q-b "Tech Lead per MR (Recommended)".

## 1. What

Apply the three edits in v2 **verbatim**:

| Edit | File |
|---|---|
| E-A1 | `skills/validation-gates/SKILL.md` |
| E-B1a | `skills/code-review/SKILL.md` |
| E-B1b | `agents/tech-lead.md` |

All three files are under `implementation/knowledge/`.

- Extract each Before/After pair from the v2 fences with a script. Do not retype them.
- Apply each pair with exact Python string replacement. Assert that each Before occurs exactly once and that each
  file changes.
- Never reword anything. If an anchor is missing or not unique, stop and report it as a blocker.

## 2. Then regenerate and declare

1. Run `node implementation/scripts/sync.mjs --root implementation`, then
   `python3 implementation/scripts/generate-registry.py`.
2. Run `python3 -m tests.functional.test_root_install_parity --print-drift`. Declare exactly the printed paths in
   `tests/_baselines/root-install-drift.json`. Do not refresh the repo root.

## 3. Verification (report every result)

- **Per file:** the base file with the edits applied equals the new file, and nothing else changed.
- **Hit counts:** every v2 count, giving both the line count and the occurrence count.
- **Gates:**
  - `sync.mjs --check`
  - `generate-registry.py --check`
  - `check-maturity.py --root implementation`
  - `scripts/scorecard.py --check` (must stay at 34 / 26 / 0)
  - `validate-tasks.py`
- **Golden:** no file under `tests/golden/` changes, and the evaluator-hash tests stay green against v16.
- **Suite:** run `python3 tests/run.py` with its output redirected to a file. Expect 904 tests and 0 failures.

## 4. Constraints

- **Write scope:**
  - the three knowledge files;
  - the regenerated mirrors and registry;
  - the drift baseline;
  - this brief's `**Status:**` line.
- **Do not touch:** nothing under `tests/golden/`; never open `tests/golden/held-out/`. Do not touch
  `scripts/scorecard.py` or the evaluator-hash files. Do not read `.env*`, credential or key files.
- **Commit:** make one Conventional Commit, ending with
  `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- **Do not push. Never run `glab mr merge` or any merge or approve API, with no exception.**

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity
(`critical` | `major` | `minor`).
