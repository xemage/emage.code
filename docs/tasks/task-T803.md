# T803 — plan-156 root refresh

**ID:** T803
**Owner:** orchestrator
**Status:** done
**Priority:** P1
**Tier:** standard
**Depends on:** T801
**Affects:** —
**Created:** 2026-11-12
**Completed:** 2026-11-12
**Based on:**
- `docs/plans/plan-156-apply-adr-015.md` (§ Outcome "Root drift declared", § Addendum)
- The user's approval of 2026-11-12, verbatim: "Root refresh approved"

## 1. What and why

Refresh the root self-install so that the 7 paths T801 declared (the `validation-gates` skill under `.claude`, `.cline`, `.github` and `.opencode`; the release-manager agent under `.claude`, `.github` and `.opencode`) match a fresh install, and empty the drift baseline.

## 2. Output

`scripts/install.sh --target <worktree> --platform all --projections-only` from develop `babddbd0`: only the 7 declared files changed, one line each (ADR-015 rows C1 and C2); `--print-drift` gives `[]`; `tests/_baselines/root-install-drift.json` emptied with a note.

## 3. Constraints

No `docker` command. Root refreshes need the user's approval at that moment (given above). The user's own settings files are not touched.

## 4. Acceptance criteria

- `python3 -m tests.functional.test_root_install_parity --print-drift` prints `[]`.
- No root file other than the 7 declared paths changes.
- The full suite and the MR pipeline pass.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
