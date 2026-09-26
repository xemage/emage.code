# Batch decomposition — replace ad-hoc `print()` diagnostics with the shared structured logger

**Status: approved by the user 2026-09-26.** Three units, no cross-unit dependencies.

## Batch Manifest

| Task ID | Description | Assigned agent | Branch |
|---------|-------------|----------------|--------|
| T534 | Migrate `implementation/runtime/memory/` diagnostics to the structured logger | backend-developer | `agent/backend-developer/T534` |
| T535 | Migrate `implementation/runtime/handoff/` diagnostics to the structured logger | backend-developer | `agent/backend-developer/T535` |
| T536 | Migrate `scripts/` diagnostics to the structured logger | devops-engineer | `agent/devops-engineer/T536` |

Each `Branch` cell equals `agent/<Assigned agent>/<Task ID>`, so the manifest cannot drift from the
ledger row it describes. There is no `Status` column here: `docs/tasks/active-tasks.md` is
authoritative for status and this manifest is not a second status record.

## Independence

Each unit touches a disjoint directory tree and imports the shared logger, which already exists and
is not modified by any unit. No unit's acceptance criteria reference another unit's output.

The per-unit record of that independence is each unit's `Depends on` cell in
`docs/tasks/active-tasks.md` — `—` for all three — which is where step 5 puts it and what
`validate-tasks.py`'s `C12`/`C13`/`C14` validate. A dependency on a task outside the batch would be
permitted there; one naming another unit of this batch would not.

## Merge order

Any order. A final integration test run (`python3 tests/run.py`) is recommended after all three
merge, because the three together change the log format the suite's log-assertion helpers read.
