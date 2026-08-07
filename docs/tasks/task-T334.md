# Task T334 — Wire `main-develop-drift-check` and `main-develop-drift-gate` into `.gitlab-ci.yml`

**ID:** T334
**Owner:** devops-engineer
**Status:** done
**Priority:** P0
**Depends on:** T332, T333
**Created:** 2026-08-07
**Completed:** 2026-08-07
**Based on:** `docs/plans/plan-019-main-develop-drift-detection.md` §3.3, `.gitlab-ci.yml` (current)

## Objective

Add two new CI jobs that invoke `scripts/check-main-develop-drift.py` (T332): a non-blocking
informational job on every `develop` push (existing `verify` stage), and a blocking gate at
release-tag time (existing `release` stage) that the `release` job's `needs:` must include, so a
new release cannot publish while `main` is more than one release behind `develop`. No new CI
stages are introduced — both jobs use stages that already exist.

## Inputs

- `.gitlab-ci.yml` (current file — read before editing to confirm no unrelated drift since this
  brief was written)
- `scripts/check-main-develop-drift.py` (T332)
- `docs/plans/plan-019-main-develop-drift-detection.md` §3.3 (full trigger-point rationale)

## Expected outputs

- `.gitlab-ci.yml`, modified in place (two new job blocks + one `needs:` edit)

## Exact edits

### Edit 1 — add `main-develop-drift-check` to the `verify` stage

Insert this job block immediately after the existing `validation-super-gate:` job block (i.e.
directly before the `sync-no-diff:` job block):

```yaml
main-develop-drift-check:
  stage: verify
  image: python:3.12-alpine
  variables:
    GIT_DEPTH: "1"
  before_script:
    - apk add --no-cache git
  script:
    - git fetch origin main develop --depth=1
    - git fetch origin 'refs/tags/*:refs/tags/*'
    - python3 scripts/check-main-develop-drift.py --main-ref origin/main --develop-ref origin/develop
  allow_failure: true
  rules:
    - if: '$CI_PIPELINE_SOURCE == "push" && $CI_COMMIT_BRANCH == "develop"'
```

### Edit 2 — add `main-develop-drift-gate` to the `release` stage

Insert this job block immediately after the existing `release-docs-gate:` job block (i.e. directly
before the `release:` job block):

```yaml
main-develop-drift-gate:
  stage: release
  image: python:3.12-alpine
  variables:
    GIT_DEPTH: "1"
  before_script:
    - apk add --no-cache git
  script:
    - git fetch origin main develop --depth=1
    - git fetch origin 'refs/tags/*:refs/tags/*'
    - python3 scripts/check-main-develop-drift.py --main-ref origin/main --develop-ref origin/develop
  rules:
    - if: '$CI_COMMIT_TAG =~ /^v[0-9]+\.[0-9]+\.[0-9]+(-[A-Za-z0-9.-]+)?$/'
```

Note: unlike Edit 1, this job has **no** `allow_failure: true` — it must block by default.

### Edit 3 — extend the `release:` job's `needs:`

Find the existing `release:` job block:

```yaml
release:
  stage: release
  needs: ["release-docs-gate"]
```

Change `needs:` to:

```yaml
release:
  stage: release
  needs: ["release-docs-gate", "main-develop-drift-gate"]
```

Do not change anything else in the `release:` job block.

## Acceptance criteria

1. `.gitlab-ci.yml` contains both new job blocks with the exact `stage:`, `rules:`, and `script:`
   content specified above (whitespace/indentation may be adjusted to match the file's existing
   2-space YAML style, but keys/values must match).
2. `python3 -c "import yaml; yaml.safe_load(open('.gitlab-ci.yml'))"` exits 0 (valid YAML) — if
   `pyyaml` is not installed, use `pip install --quiet pyyaml` first, or fall back to
   `python3 -c "import yaml"` failing gracefully and note in Execution notes if YAML validation
   had to be skipped.
3. `grep -c "main-develop-drift-check:" .gitlab-ci.yml` → 1
4. `grep -c "main-develop-drift-gate:" .gitlab-ci.yml` → 1
5. `grep -A2 "^release:" .gitlab-ci.yml | grep "main-develop-drift-gate"` → matches (confirms the
   `needs:` edit landed)
6. `git fetch origin main develop --depth=1 && git fetch origin 'refs/tags/*:refs/tags/*'` then
   `python3 scripts/check-main-develop-drift.py --main-ref origin/main --develop-ref origin/develop`
   still exits 0 or 1 with a coherent verdict (same command as T332 acceptance criterion 3 — must
   still work unchanged, this task does not modify the script).
7. Full test suite still green: `python3 tests/run.py` → exit 0.

## Blocker protocol

Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`)
+ severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.

## Execution notes

Executed 2026-08-07 by devops-engineer. Read `.gitlab-ci.yml` before editing — no unrelated
drift since brief was written. Applied the 3 exact edits verbatim (content unchanged, only
existing 2-space indentation preserved): inserted `main-develop-drift-check:` into the `verify`
stage directly after `validation-super-gate:` / before `sync-no-diff:`; inserted
`main-develop-drift-gate:` into the `release` stage directly after `release-docs-gate:` / before
`release:`; extended `release:`'s `needs:` to `["release-docs-gate", "main-develop-drift-gate"]`.
No other lines in `.gitlab-ci.yml` changed. No files other than `.gitlab-ci.yml` and this brief
were modified.

### AC1 — visual diff check (both new job blocks present, correct stage/rules/script)

`git --no-pager diff .gitlab-ci.yml`:

```diff
@@ -111,6 +111,21 @@ validation-super-gate:
     - if: $CI_PIPELINE_SOURCE == "merge_request_event"
     - if: $CI_COMMIT_BRANCH
 
+main-develop-drift-check:
+  stage: verify
+  image: python:3.12-alpine
+  variables:
+    GIT_DEPTH: "1"
+  before_script:
+    - apk add --no-cache git
+  script:
+    - git fetch origin main develop --depth=1
+    - git fetch origin 'refs/tags/*:refs/tags/*'
+    - python3 scripts/check-main-develop-drift.py --main-ref origin/main --develop-ref origin/develop
+  allow_failure: true
+  rules:
+    - if: '$CI_PIPELINE_SOURCE == "push" && $CI_COMMIT_BRANCH == "develop"'
+
 sync-no-diff:
   stage: sync
   needs: ["verify-knowledge-drift", "validation-super-gate"]
@@ -161,9 +176,23 @@ release-docs-gate:
   rules:
     - if: '$CI_COMMIT_TAG =~ /^v[0-9]+\.[0-9]+\.[0-9]+(-[A-Za-z0-9.-]+)?$/'
 
+main-develop-drift-gate:
+  stage: release
+  image: python:3.12-alpine
+  variables:
+    GIT_DEPTH: "1"
+  before_script:
+    - apk add --no-cache git
+  script:
+    - git fetch origin main develop --depth=1
+    - git fetch origin 'refs/tags/*:refs/tags/*'
+    - python3 scripts/check-main-develop-drift.py --main-ref origin/main --develop-ref origin/develop
+  rules:
+    - if: '$CI_COMMIT_TAG =~ /^v[0-9]+\.[0-9]+\.[0-9]+(-[A-Za-z0-9.-]+)?$/'
+
 release:
   stage: release
-  needs: ["release-docs-gate"]
+  needs: ["release-docs-gate", "main-develop-drift-gate"]
   image: python:3.12-alpine
   variables:
     GIT_DEPTH: "0"
```

Result: PASS — both job blocks present with exact `stage:`, `rules:`, and `script:` content
specified in the brief; `main-develop-drift-gate` correctly omits `allow_failure: true`
(blocks by default) while `main-develop-drift-check` retains it (informational only).

### AC2 — YAML validity

`python3 -c "import yaml; yaml.safe_load(open('.gitlab-ci.yml'))"; echo "EXIT_CODE=$?"`

```
EXIT_CODE=0
```

`pyyaml` was already installed in the environment; no `pip install` was required.

### AC3 — `main-develop-drift-check:` occurs exactly once

`grep -c "main-develop-drift-check:" .gitlab-ci.yml`

```
1
```

Result: PASS.

### AC4 — `main-develop-drift-gate:` occurs exactly once

`grep -c "main-develop-drift-gate:" .gitlab-ci.yml`

```
1
```

Result: PASS.

### AC5 — `release:` job's `needs:` includes the new gate

`grep -A2 "^release:" .gitlab-ci.yml | grep "main-develop-drift-gate"`

```
  needs: ["release-docs-gate", "main-develop-drift-gate"]
```

Result: PASS.

### AC6 — drift-check script still works unchanged

`git fetch origin main develop --depth=1 && git fetch origin 'refs/tags/*:refs/tags/*' && python3 scripts/check-main-develop-drift.py --main-ref origin/main --develop-ref origin/develop; echo "EXIT_CODE=$?"`

```
From https://gitlab.com/em-age/emage.code
 * branch            main       -> FETCH_HEAD
 * branch            develop    -> FETCH_HEAD
drift-check: main=v6.5.0 develop=v6.5.0 releases_behind=0
drift-check: PASS — main is within the allowed 1-release grace window
MAIN-DEVELOP DRIFT: PASS
EXIT_CODE=0
```

Result: PASS — script unchanged, coherent verdict, exit 0.

### AC7 — full test suite

`python3 tests/run.py; echo "EXIT_CODE=$?"`

```
Ran 286 tests in 12.332s
FAILED (failures=1, skipped=17)
EXIT_CODE=1
```

The single failure is `test_shipped_validator_passes`
(`tests/performance/test_team_health.py`), reporting:

```
FAIL C8: completed ID T332 has brief status 'pending' (expected done or cancelled)
FAIL C8: completed ID T333 has brief status 'pending' (expected done or cancelled)
FAIL C8: completed ID T335 has brief status 'pending' (expected done or cancelled)
TASK LEDGER: FAIL (3 violations)
```

**Root-cause verification (pre-existing, unrelated to this task's edit):** reproduced with the
`.gitlab-ci.yml` change stashed out (`git stash` / re-run / `git stash pop`) — identical failure,
identical 3 violations, on the unmodified branch tip (commit `0061e9a`):

```
FAIL C8: completed ID T332 has brief status 'pending' (expected done or cancelled)
FAIL C8: completed ID T333 has brief status 'pending' (expected done or cancelled)
FAIL C8: completed ID T335 has brief status 'pending' (expected done or cancelled)
TASK LEDGER: FAIL (3 violations)
Ran 286 tests in 11.825s
FAILED (failures=1, skipped=17)
```

Cause: `docs/tasks/task-T332.md`, `docs/tasks/task-T333.md`, `docs/tasks/task-T335.md` each still
show `**Status:** pending` in their brief header even though all three are already rows in
`docs/tasks/completed-tasks.md`. This is a task-ledger consistency issue, not a defect in
`.gitlab-ci.yml` or in `scripts/check-main-develop-drift.py`. Per AGENTS.md, "Only orchestrators
create/transition tasks" — updating brief `Status:` fields is out of this task's ownership
boundary (constrained to `.gitlab-ci.yml` and this brief's Execution notes only), so it was not
fixed here.

Result: **CONDITIONAL** — all CI-wiring-specific criteria (AC1–AC6) pass. AC7's full-suite gate
is red, but the one failure is proven pre-existing and outside this task's scope. Flagging as a
blocker for the orchestrator rather than silently reporting green.

### Blocker

- **Type:** dependency
- **Severity:** minor
- **Description:** `tests/run.py` full suite fails (`exit 1`, 1/286 failures) because
  `docs/tasks/task-T332.md`, `task-T333.md`, `task-T335.md` still carry `Status: pending` while
  already archived as `done` in `docs/tasks/completed-tasks.md`. Confirmed pre-existing (present
  before this task's `.gitlab-ci.yml` edit, on commit `0061e9a`) and unrelated to CI wiring.
- **Proposed mitigation:** Orchestrator (or a task-management-owning agent) updates the `Status:`
  line in `docs/tasks/task-T332.md`, `docs/tasks/task-T333.md`, `docs/tasks/task-T335.md` to
  `done`, matching their already-archived rows in `completed-tasks.md`. This is a one-line edit
  per file and outside devops-engineer's file-ownership boundary for T334 (`.gitlab-ci.yml` +
  this brief only).

**Blocker resolution (orchestrator, 2026-08-07):** Updated `Status:`/`Completed:` headers in
`docs/tasks/task-T332.md`, `task-T333.md`, `task-T335.md` to `done`/`2026-08-07` (commit
`150d4f8`). Re-ran all 7 acceptance criteria fresh: AC1-AC6 unchanged/PASS, AC7 now
`python3 tests/run.py` -> `Ran 286 tests ... OK`, exit 0. **Final verdict: PASS (all 7 criteria
green).**
