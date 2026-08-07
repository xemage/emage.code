# Task T334 — Wire `main-develop-drift-check` and `main-develop-drift-gate` into `.gitlab-ci.yml`

**ID:** T334
**Owner:** devops-engineer
**Status:** pending
**Priority:** P0
**Depends on:** T332, T333
**Created:** 2026-08-07
**Completed:** —
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
<not yet picked up>
