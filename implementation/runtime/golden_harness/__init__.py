"""Golden-suite live-execution harness (T458) — non-dispatch half.

Turns the manual mechanism proven by 28 real trials (`task-T484.md` through
`task-T494.md`, run entirely by hand by the orchestrator) into real, committed,
tested code. This package owns exactly the non-dispatch pieces named in
`docs/tasks/task-T458.md`'s Objective items 1-4:

- `scratch` — the scratch-isolation helper (Objective #1).
- `scoring` — the `expect.py`-reuse scoring module (Objective #2), mirroring
  `scripts/scorecard.py`'s own `load_expect_module()` pattern verbatim rather
  than reinventing it.
- `schema` / `trial_store` — the trial-record schema and JSONL store
  (Objective #3).
- `policy` — `plan-048-t458-k-threshold-decision.md` §7's decided
  k/escalation/floor-tolerance policy as callable functions (Objective #4).

This package deliberately contains **no dispatch mechanism of any kind** — no
`Agent`-tool call, no `claude` CLI subprocess. Launching a live control/treatment
session remains the orchestrator's job (Objective #5), using the entry points
this package exposes. See `docs/artifacts/golden-live-harness-v1.md` for the
full design writeup and the policy-statement-to-function mapping.
"""
from __future__ import annotations
