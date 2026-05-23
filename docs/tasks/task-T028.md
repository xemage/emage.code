# Task T028 — Harden release documentation verification gate

## Objective
Strengthen release-stage CI checks so release publication is blocked unless required documentation is updated and content verification passes.

## Inputs
- `docs/tasks/task-T025.md`
- `.gitlab-ci.yml`
- `scripts/sync-wiki.py`
- updated docs from T026/T027

## Expected outputs
- updated `.gitlab-ci.yml` release gate logic
- documentation verification script(s) used by release gate

## Acceptance criteria
- Tag pipeline fails when required release docs checks fail.
- Tag pipeline passes when docs are updated and verification checks pass.
- Gate remains deterministic and produces actionable error output.

## Blocker protocol
If blocked, report blocker type and severity with one proposed mitigation.
