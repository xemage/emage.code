# T512 — Root self-install harness refresh to v7.0.0

**Status:** done
**Owner:** top-level session
**Priority:** P1
**Depends on:** none
**Completed:** 2026-09-19
**Based on:** the user's explicit instruction ("I updated the used version of emage.code in this repository. Summarize and commit the staged changes as update of the harness version.")

## Objective

Review and commit the staged output of the user's own `scripts/install.sh --update` run against
this repo's own root self-install (a dogfooding instance of the harness it produces), propagating
already-shipped v7.0.0 `implementation/` content into the root platform mirrors, which had drifted
stale.

## Inputs

- The user's own already-staged `git add -A` output (409 files, all under root platform directories
  plus `docs/tasks/active-tasks.md`).
- `implementation/` at its current, already-merged v7.0.0 state (unchanged by this task).

## Outputs

- All 7 platform self-install mirrors (`.claude/`, `.cursor/`, `.gemini/`, `.github/`, `.opencode/`,
  `.pi/`, `.cline/`, `.clinerules/`) refreshed to match `implementation/`'s current content.
- `.claude/settings.json` (local, non-harness config) restored after being incidentally deleted by
  the update.
- `docs/tasks/active-tasks.md`'s false "This ledger starts EMPTY... first real task is T001"
  scaffold text replaced with an accurate status note.

## Acceptance criteria

- [x] `sync.mjs --check` reports no drift (confirms root now genuinely matches `implementation/`'s
      canonical source)
- [x] No unrelated or incidental deletions committed as if intentional (`.claude/settings.json`
      caught and restored)
- [x] No false state claims committed into the task ledger (the scaffold-template text caught and
      corrected)
- [x] Full verification bar green: `tests/run.py`, `check-maturity.py`, `validate-tasks.py`

## Execution notes

See `docs/tasks/completed-tasks.md`'s T512 row for the full closure record, including a real
process mistake made and caught the same session (the active-tasks.md fix was initially lost in
flight due to a stage/edit ordering error, caught by diffing the actual merged commit rather than
assuming the edit had landed, and corrected in a same-day follow-up MR).
