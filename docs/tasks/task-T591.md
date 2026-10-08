# T591 — Apply the O1 ruling: higher of the two grade definition sets under /security-audit

**ID:** T591
**Owner:** backend-developer
**Status:** in_review
**Priority:** P2
**Tier:** mechanical
**Affects:** command/security-audit, agent/security-engineer
**Depends on:** T589, T590
**Created:** 2026-10-08
**Based on:**
- `docs/artifacts/security-grade-definitions-v2.md`: **the single implementation input.** Its two four-backtick fences
  hold E-O1a and E-O1b. It also holds the hit-count table.
- `docs/artifacts/security-review-security-grade-definitions-v1.md`. Conditions C1–C3 are satisfied by applying v2
  verbatim.
- `docs/plans/plan-105-security-grade-definitions-o1.md` §4.
- The user's decision of 2026-10-08: Q-O1 "Higher of the two (Recommended)". The command amendment rests on this
  decision.

## 1. What

**Sequencing guard (check first):** `grep -cF 'No grade so given is lower than a minimum grade set elsewhere'
implementation/knowledge/skills/validation-gates/SKILL.md` must return 1. If it does not, stop and report a blocker.

Apply both edits **verbatim**, or neither:

| Edit | File |
|---|---|
| E-O1a | `implementation/knowledge/commands/security-audit.md`: after the `:46` line, keeping its three-space indent |
| E-O1b | `implementation/knowledge/agents/security-engineer.md`: a new paragraph before `## Security Review Report Format` |

Extract each Before/After pair from the v2 fences with a script; do not retype it. Apply it with exact Python string
replacement. Assert that each Before occurs exactly once and that each file changes. Never reword.

## 2. Then regenerate and declare

1. Run `node implementation/scripts/sync.mjs --root implementation`, then
   `python3 implementation/scripts/generate-registry.py`.
2. Run `python3 -m tests.functional.test_root_install_parity --print-drift`. Declare exactly the printed paths in
   `tests/_baselines/root-install-drift.json`, keeping the paths already declared. Do not refresh the repo root.

## 3. Verification (report every result)

- **Per file:** base + edits == new, and nothing else changed.
- **Step 9:** `/security-audit` step 9 (the four definition lines) is byte-identical. Step 10 and the Failure mode are
  untouched.
- **Hit counts:** every v2 count, as both a line count and an occurrence count.
- **Gates:**
  - `sync.mjs --check`;
  - `generate-registry.py --check`;
  - `check-maturity.py --root implementation`;
  - `scripts/scorecard.py --check` (must be 34 / 26 / 0);
  - `validate-tasks.py`.
- **Golden:** no file under `tests/golden/` changes. The evaluator-hash tests stay green against v16. The three
  `security-audit-*` open cases keep their results.
- **Suite:** run `python3 tests/run.py` with its output redirected to a file. Expect 904 tests and 0 failures.

## 4. Constraints

- **Write scope:** the two knowledge files, the regenerated mirrors and registry, the drift baseline, and this brief's
  `**Status:**` line.
- **Off limits:** nothing under `tests/golden/`; never open `tests/golden/held-out/`. Also leave
  `scripts/scorecard.py` and the evaluator-hash files alone, and never read `.env*`, credential or key files.
- **Commit:** one Conventional Commit, ending with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- **Do not push. Never run `glab mr merge` or any merge or approve API, with no exception.**

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity
(`critical` | `major` | `minor`).
