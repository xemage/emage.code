# Artifact: security-review-t620-jwt-cost-v1.md

> Immutable once produced; revisions bump `<N>`.

## Metadata

- **Reviewer**: security-engineer (read-only; no execute tool; static review). Recorded by the orchestrator from the reviewer's report.
- **Task**: T620 (plan-120), R-1: the cost of the `jwt` rule on aperiodic `eyJ`-dense input. Reviewed commit `b7f913e`; the developer fixed the four LOW items in one round (`48db57a`, rebased as `5dc0289`), which the orchestrator verified but the reviewer did not re-read.
- **Date**: 2026-10-14.
- **Orchestrator checks**: the worst shape J (170 `eyJ` starts sharing a dot-free payload that itself holds a start every 3 characters) re-measured at 2 MB: 4.6 s, complete, no hit (the developer measured 4.3 s); `T620Tests` 8 tests OK; the scanner diff is a docstring note only.

## Verdict: PASS

0 critical, 0 high, 0 medium, 4 low. No pattern changed, so no rule, label condition or fail-closed path is weakened. The cost is linear (about 2 microseconds per byte on git 2.43.0 with glibc under `LC_ALL=C`), the 60 s deadline is reached only at roughly 30 MB for one file in the index or worktree scope, and a timeout fails closed (`timeout`, `complete: false`). Accepting that as a documented blind spot is sound: any cap on starts per payload would hide a real token behind a dense prefix.

The reviewer could not construct a super-linear shape: every start costs at most about 513 steps, each start belongs to exactly one dot, at most about 170 starts precede one dot within the 512-character header window, and failing payload runs of different dots are disjoint, giving at most about 341 steps per byte in total.

| ID | Grade | Concern | Disposition |
|---|---|---|---|
| T620-1 | LOW | Contract v6 gave a wrong reason for shape A's cost (the 170-fold rescan is real). | Fixed: the step model plus the disjointness step. |
| T620-2 | LOW | The 30 MB figure applies to one file only; history and stashes multiply it (tips up to 200, stashes up to 50, `git log -G` has no commit cap); on timeout the later rules do not run. | Fixed in v6 §4, the docstring and the unverified list; one history-scope timing test added. |
| T620-3 | LOW | Test margin 10 s against about 2.6 s (flake risk); the real-token test asserted only the whole token. | Fixed: bound 20 s (deadline stays 40 s); token fragments asserted absent. |
| T620-4 | LOW | Wording: R-1 "closed" (it is an accepted fail-closed residual); a mis-cited measurement; process noise; the `LC_ALL=C` and glibc caveat. | Fixed. |

Residuals that remain documented: the measurements are for git 2.43.0 with glibc under `LC_ALL=C`; another locale or regex library was not measured; the 30 MB figure is extrapolated.
