# Task T222 - Wrap an emage.code agent as SIA target + author `evaluate.py`

## Objective
Express one emage.code agent task as a SIA task (target agent + evaluation), so the SIA loop can improve it
and produce a measurable reward signal.

## Inputs
- SIA task layout + eval contract: `sia/EVALUATION_GUIDE.md`, `sia/sia/orchestrator.py`
- The chosen emage.code agent + a representative task with ground truth
- SIA target adapter (T220)

## Expected outputs
- A SIA task directory: `tasks/<name>/data/public/{task.md,evaluate.py}` and private ground truth
- `evaluate(submission)→dict` writing `results.json` with a primary metric

## Acceptance criteria
- `python tasks/<name>/data/public/evaluate.py --gen-dir <dir>` produces `results.json`.
- Metric reflects the real objective; ground truth kept under `data/private/`.
- One reference target agent runs and is evaluable end-to-end (no proxy required for this task).

## Blocker protocol
If blocked, report blocker type and severity with one proposed mitigation.
