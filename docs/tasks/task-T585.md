# T585 — Apply the first ADR-008 rulings (P40 S2/S3 notes, P43)

**ID:** T585
**Owner:** backend-developer
**Status:** done
**Priority:** P2
**Tier:** mechanical
**Affects:** skill/validation-gates, skill/code-review, skill/testing-strategy, skill/rapid-prototyping, skill/poc-evaluation, agent/evaluation-agent
**Depends on:** T584
**Created:** 2026-10-07
**Based on:**
- `docs/artifacts/adr-008-rulings-p40-p43-v3.md`: **the single implementation input.** §2 holds the six edits with
  Before/After text, §3 the per-edit statements, and §4 the consolidated list with the expected hit counts.
- `docs/artifacts/security-review-adr-008-rulings-n1-v1.md` (Security Engineer phrase check: PASS)
- `docs/plans/plan-102-adr-008-rulings-p40-p43.md` §4
- The user's decisions of 2026-10-07: P43 "Evaluation decides, tighten-only (Recommended)"; P40 S2/S3 "Strictest
  applies (Recommended)"; notes "N1 + N2 + N3 (Recommended)".

## 1. What

Apply the six edits in v3 §2 **verbatim** to the knowledge sources under `implementation/knowledge/`:

| Edit | File |
|---|---|
| N1 | `skills/validation-gates/SKILL.md` (before `### Severity Definitions`) |
| N2 | `skills/code-review/SKILL.md` (before `### Artifact Version Awareness`) |
| N3 | `skills/testing-strategy/SKILL.md` (the line at `:233`) |
| P1 | `skills/rapid-prototyping/SKILL.md` (before `**Evidence items**`) |
| P2 | `skills/poc-evaluation/SKILL.md` (bullet appended after `:117`) |
| P3 | `agents/evaluation-agent.md` (after `:22`) |

**Do not change any wording.** If an anchor is missing or is not unique, or an edit cannot be applied exactly, stop and
report it as a blocker.

## 2. Then regenerate and declare

1. `node implementation/scripts/sync.mjs --root implementation` and
   `python3 implementation/scripts/generate-registry.py`.
2. **Root parity.** Do not refresh the repo root (that needs the user's approval). Instead, run
   `python3 -m tests.functional.test_root_install_parity --print-drift` and declare exactly the printed paths in
   `tests/_baselines/root-install-drift.json`, as earlier knowledge tasks did. Report the count.

## 3. Verification (report every result)

- **Content check per edit.** For each file, `old.replace(Before, After) == new`, with nothing else in the file changed.
  Do not use a "single -U0 hunk" check.
- **v3 §4 hit counts.** Run each `grep -c`, including the required **0 hits** for the superseded v2 wording ("None of
  them makes another less strict", "for two of the gates:").
- **Gates:**
  - `sync.mjs --check`;
  - `generate-registry.py --check`;
  - `python3 implementation/scripts/check-maturity.py --root implementation`;
  - `python3 scripts/scorecard.py --check`, which must be unchanged at 34 / 26 / 0;
  - `python3 docs/tasks/validate-tasks.py`.
- **Golden and evaluator hash.** No file under `tests/golden/` may change. The evaluator-hash tests must stay green
  against v16. `validate-workflow-gate-verdict-sources` keeps a frozen fixture of `validation-gates`; it lags the
  source by design, and its result does not change. Confirm this.
- **Suite.** Run `python3 tests/run.py`, redirecting output to a file (never pipe it to `tail`). Expect 904 tests with
  0 failures. Name any failure.

## 4. Constraints

- **Write scope:**
  - the six knowledge files;
  - the regenerated `implementation/.<platform>/` mirrors and `implementation/registry/index.json`;
  - `tests/_baselines/root-install-drift.json`;
  - this brief's `**Status:**` line.
- **Off limits:** no other file; nothing under `tests/golden/` (never open `tests/golden/held-out/`); not
  `scripts/scorecard.py` and not the evaluator-hash files.
- Do not read `.env*`, credential or key files.
- Work only in the assigned worktree. Commit locally as **one** Conventional Commit ending with the line
  `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. **Do not push. Never run `glab mr merge` or any
  merge/approve API, with no exception.** Hand back.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity
(`critical` | `major` | `minor`). Max 2 retries before escalating. Never silently fail.
