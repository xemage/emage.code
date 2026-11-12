# T793 — plan-151 root refresh

**ID:** T793
**Owner:** orchestrator
**Status:** done
**Priority:** P1
**Tier:** standard
**Depends on:** T790
**Affects:** —
**Created:** 2026-11-12
**Completed:** 2026-11-12
**Based on:**
- `docs/plans/plan-151-context-retriever-code-residue.md` (§ Task Decomposition item 4, § Outcome "Open")
- The user's approval of 2026-11-12, verbatim: "refresh"

## 1. What and why

Refresh the root self-install so that the two paths T790 declared (`.cline/mcp.json`, `.opencode/opencode.json`) match a fresh install, and empty the drift baseline.

## 2. Output

`scripts/install.sh --target <worktree> --platform all --projections-only` from develop `4aaf8d33`: only the two declared files changed, one line each (`--platform-root` `.cline` and `.opencode`); `--print-drift` gives `[]`; `tests/_baselines/root-install-drift.json` emptied with a note.

## 3. Constraints

As plan-151 § Constraints. No `docker` command. Root refreshes need the user's approval at that moment (given above).

## 4. Acceptance criteria

- `python3 -m tests.functional.test_root_install_parity --print-drift` prints `[]`.
- No root file other than the two declared paths changes.
- The full suite and the MR pipeline pass.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
