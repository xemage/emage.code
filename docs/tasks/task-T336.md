# Task T336 — GATE: end-to-end verification of the drift-detection mechanism

**ID:** T336
**Owner:** qa-engineer
**Status:** pending
**Priority:** P0
**Depends on:** T332, T333, T334, T335
**Created:** 2026-08-07
**Completed:** —
**Based on:** `docs/plans/plan-019-main-develop-drift-detection.md` (full plan)

## Objective

Verify, with real command output (not asserted), that T332-T335 together form a working,
consistent drift-detection mechanism: the script behaves correctly standalone, the CI YAML is
valid and wires the script in at both trigger points, the full test suite (including T333's new
tests) is green, and the documentation update is present and consistent. Produce a VERDICT
(`PASS` / `CONDITIONAL_PASS` / `FAIL`) per this repo's Validation Gates convention. This task does
not modify any file besides its own Execution notes.

## Inputs

- `scripts/check-main-develop-drift.py` (T332)
- `tests/functional/test_check_main_develop_drift.py` (T333)
- `.gitlab-ci.yml` (T334)
- `CONTRIBUTING.md` (T335)
- `docs/plans/plan-019-main-develop-drift-detection.md`

## Expected outputs

- This task brief's own Execution notes, containing the VERDICT and all literal command evidence
  below.

## Acceptance criteria — run each command, paste literal output into Execution notes

1. Script standalone, real repo state:
   ```bash
   git fetch origin main develop --depth=1
   git fetch origin 'refs/tags/*:refs/tags/*'
   python3 scripts/check-main-develop-drift.py --main-ref origin/main --develop-ref origin/develop
   echo "EXIT_CODE=$?"
   ```
   Must print a `MAIN-DEVELOP DRIFT: PASS` or `FAIL` line and a matching `EXIT_CODE` (0 for PASS,
   1 for FAIL) — either is an acceptable *result*, but the command must run without a Python
   traceback or non-0/1 exit code.

2. Full test suite:
   ```bash
   python3 tests/run.py
   echo "EXIT_CODE=$?"
   ```
   Must show `EXIT_CODE=0` and the total test count must include T333's new test file (compare
   against the pre-T332 baseline test count, e.g. from `docs/tasks/task-T264.md` or the most
   recent full-suite run recorded in a checkpoint, to confirm the count increased by the expected
   14 new tests — note both counts in Execution notes).

3. CI YAML validity and content:
   ```bash
   python3 -c "import yaml; yaml.safe_load(open('.gitlab-ci.yml'))" && echo "YAML_VALID=true"
   grep -c "main-develop-drift-check:" .gitlab-ci.yml
   grep -c "main-develop-drift-gate:" .gitlab-ci.yml
   grep -A2 "^release:" .gitlab-ci.yml | grep -c "main-develop-drift-gate"
   ```
   Expected: `YAML_VALID=true`, `1`, `1`, `1` (in order).

4. Markdown link / lint check for the whole repo (matches the `markdown-links` CI job's own logic
   — run it locally if feasible, otherwise state that this criterion is deferred to the actual
   MR pipeline and note that explicitly rather than fabricating a result):
   ```bash
   grep -c "### Drift detection" CONTRIBUTING.md
   grep -c "check-main-develop-drift.py" CONTRIBUTING.md
   ```
   Expected: `1`, `1` or more.

5. Task ledger still valid after T332-T335 are moved to `done` (this task's own execution should
   include moving T332-T335 to `docs/tasks/completed-tasks.md` per this repo's atomic
   archive-on-completion convention, then running):
   ```bash
   python3 docs/tasks/validate-tasks.py
   echo "EXIT_CODE=$?"
   ```
   Expected: `TASK LEDGER: PASS (...)`, `EXIT_CODE=0`.

## Verdict rubric

- **PASS** — all 5 criteria produce the expected results with no fabricated/assumed output.
- **CONDITIONAL_PASS** — criterion 4 (markdown lint) was deferred to the MR pipeline per its own
  fallback instruction, but criteria 1/2/3/5 all pass — track "confirm markdown-links CI job is
  green on the MR" as an explicit condition in `docs/tasks/active-tasks.md` / the MR description.
- **FAIL** — any of criteria 1/2/3/5 do not produce the expected result. Do not silently patch the
  underlying file to force a pass; file a fix task instead and report the blocker.

## Blocker protocol

Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`)
+ severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.

## Execution notes
<not yet picked up>
