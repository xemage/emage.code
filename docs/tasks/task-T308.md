# Task T308 — Prepare release notes for the Claude Code tool-projection fix

**ID:** T308
**Owner:** release-manager
**Status:** done
**Priority:** P0
**Depends on:** T301, T307, GATE 1 (make sync && make verify green, full test suite green)
**Created:** 2026-07-31
**Completed:** 2026-07-31
**Based on:** docs/plans/plan-016-pattern-a-hardening-and-phase23-poc-closure.md

## Objective
Ship the T301 fix as its own release before any other Plan 016 work proceeds, so the broken
Claude Code subagent tool-projection defect is resolved for any concurrent user of this platform
as soon as possible, independent of the Phase 2/3 ledger correction or Pattern A hardening work.

## Inputs
- `git tag --sort=-v:refname` (to confirm the true current latest tag — do not assume)
- `docs/releases/v6.4.0.md` (style/shape reference)
- T301 / T307 diffs

## Expected outputs
- `docs/releases/v<X.Y.Z>.md` (new file; `<X.Y.Z>` determined from the actual latest tag, patch-bumped)

## Acceptance criteria
1. Confirmed current latest tag via `git tag --sort=-v:refname | head -5` before choosing the next
   version — do not hardcode a guess.
2. `docs/releases/v<X.Y.Z>.md` contains: "Latest release: v<X.Y.Z>"; a "## Highlights" section
   plainly stating that Claude Code subagents were generated with a broken `tools:` frontmatter
   (abstract categories instead of real tool identifiers) leaving them unable to use
   Read/Bash/Edit/Write/Agent, and that this is now fixed; a "## Install" section with valid
   instructions.
3. `python3 scripts/verify-release-docs.py --tag v<X.Y.Z>` exits 0.
4. Per R8, paste the verify command's literal output into Execution notes.

## Blocker protocol
Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`)
+ severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.

## Execution notes

**Run 2026-07-31.**

`git tag --sort=-v:refname | head -5`:
```
v6.4.1
v6.4.0
v6.3.0
v6.2.0
v6.1.0
```
Current latest is `v6.4.1`. This is a bug fix to already-shipped platform-projection code
(the Claude Code platform, shipped v6.4.0), so the next version is the patch bump `v6.4.2`.

Created `docs/releases/v6.4.2.md` (Install + Highlights sections, describing the tool-projection
bug and its fix) and updated the `Latest release:` marker in `README.md`, `docs/wiki/README.md`,
`docs/wiki/home.md` from `v6.4.1` to `v6.4.2`.

`python3 scripts/verify-release-docs.py --tag v6.4.2`:
```
release-docs-verify: all documentation checks passed
release-docs-verify: verified marker 'Latest release: v6.4.2'
```
Exit 0.

Note on sequencing: this was first drafted directly on `develop` before T301/T307's fix had
actually been merged there (a process misstep — T309 requires the fix to be merged to develop
first). Safely stashed, then reapplied cleanly on `release/v6.4.2` (branched from `develop` after
the bugfix MR !80 was merged). Re-ran the verify command above on the release branch — same
clean result.

**Second bug found and fixed (T309's CI run, not part of the original brief):** MR !81's pipeline
failed on `unit-tests` — `tests/performance/test_team_health.py::TestShippedTaskValidator::test_shipped_validator_passes`
reported `FAIL C8: task-T308.md says done but T308 is not in completed-tasks.md`. Root cause: this
task's own header was set to `Status: done` without actually performing the atomic 4-step ledger
completion (append to `completed-tasks.md`, remove from `active-tasks.md`) — an oversight on my
part, caught by the exact shipped validator this repo built under plan-014 for precisely this
failure mode. Fixed: appended T308's row to `completed-tasks.md`, removed it from
`active-tasks.md`. Re-ran locally: `python3 docs/tasks/validate-tasks.py` → `TASK LEDGER: PASS (8
active, 143 completed)`; `python3 -m pytest tests/performance/test_team_health.py -q` → `9 passed`;
full suite `python3 tests/run.py -v` → `Ran 266 tests ... OK (skipped=13)`.
