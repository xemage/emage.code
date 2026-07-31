# Task T308 — Prepare release notes for the Claude Code tool-projection fix

**ID:** T308
**Owner:** release-manager
**Status:** pending
**Priority:** P0
**Depends on:** T301, T307, GATE 1 (make sync && make verify green, full test suite green)
**Created:** 2026-07-31
**Completed:** —
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
<filled during execution>
