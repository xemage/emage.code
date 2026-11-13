# T807 — plan-157 root refresh

**ID:** T807
**Owner:** orchestrator
**Status:** done
**Priority:** P1
**Tier:** standard
**Depends on:** T805
**Affects:** —
**Created:** 2026-11-13
**Completed:** 2026-11-13
**Based on:**
- `docs/plans/plan-157-confirmation-as-validity-condition.md` (§ Outcome "Root drift declared", § Addendum)
- The user's approval of 2026-11-13, verbatim: "Approving root refresh"

## 1. What and why

Refresh the root self-install so that the 4 paths T805 declared (the `validation-gates` skill under `.claude`, `.cline`, `.github` and `.opencode`) match a fresh install, and empty the drift baseline.

## 2. Output

`scripts/install.sh --target <worktree> --platform all --projections-only` from develop `b8dba5dc`: only the 4 declared files changed, two lines each (ADR-016 rows D1, D2, W1, W2 and W3); `--print-drift` gives `[]`; `tests/_baselines/root-install-drift.json` emptied with a note.

## 3. Constraints

No `docker` command. Root refreshes need the user's approval at that moment (given above). The user's own settings files are not touched.

## 4. Acceptance criteria

- `python3 -m tests.functional.test_root_install_parity --print-drift` prints `[]`.
- No root file other than the 4 declared paths changes.
- The full suite and the MR pipeline pass.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
