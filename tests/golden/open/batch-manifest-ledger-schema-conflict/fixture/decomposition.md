# Batch decomposition — replace ad-hoc `print()` diagnostics with the shared structured logger

**Status: approved by the user 2026-09-26.** Three units, no cross-unit dependencies.

| Unit ID | Description | Assigned agent | Branch | Status |
|---------|-------------|----------------|--------|--------|
| U1 | Migrate `implementation/runtime/memory/` diagnostics to the structured logger | backend-developer | `batch/structured-logging/1-runtime-memory` | pending |
| U2 | Migrate `implementation/runtime/handoff/` diagnostics to the structured logger | backend-developer | `batch/structured-logging/2-runtime-handoff` | pending |
| U3 | Migrate `scripts/` diagnostics to the structured logger | devops-engineer | `batch/structured-logging/3-scripts` | pending |

## Independence

Each unit touches a disjoint directory tree and imports the shared logger, which already exists and
is not modified by any unit. No unit's acceptance criteria reference another unit's output.

| Unit ID | Depends on |
|---------|------------|
| U1 | — |
| U2 | — |
| U3 | — |

## Merge order

Any order. A final integration test run (`python3 tests/run.py`) is recommended after all three
merge, because the three together change the log format the suite's log-assertion helpers read.
