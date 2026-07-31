# Task T307 — Regression test for the Claude Code tool-map fix

**ID:** T307
**Owner:** backend-developer
**Status:** done
**Priority:** P1
**Depends on:** T301
**Created:** 2026-07-31
**Completed:** 2026-07-31
**Based on:** docs/plans/plan-016-pattern-a-hardening-and-phase23-poc-closure.md

## Objective
Prevent this exact regression (abstract tool names leaking into generated Claude Code frontmatter)
from recurring silently in the future by adding a permanent automated check.

## Inputs
- `tests/functional/test_platform_projections.py` (existing file)
- `implementation/.claude/agents/orchestrator.md` (post-`make sync` output of T301)

## Expected outputs
- `tests/functional/test_platform_projections.py` with one new test added (do not replace the
  existing file's content).

## Acceptance criteria
1. New test runs `make sync` (or invokes the equivalent sync function directly) and asserts the
   generated `implementation/.claude/agents/orchestrator.md` tools line contains `Read` and `Bash`,
   and does NOT contain a bare `read` or `execute` token.
2. `python3 tests/run.py --suite functional -v` → 0 failures.
3. Per R8, paste the literal test-run output into Execution notes.

## Blocker protocol
Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`)
+ severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.

## Execution notes

**Run 2026-07-31.** Fulfilled as part of T301's own verification: the existing
`test_claude_code_agents_use_tools_string` in `tests/functional/test_platform_projections.py`
had to be updated anyway (it asserted the pre-fix, buggy echo-back behavior as correct — see
T301's Execution notes for the root-cause). Rather than add a second, narrower orchestrator-only
test duplicating logic, the existing test was strengthened to check, for **every** generated
Claude Code agent (not just orchestrator): (a) the projected tools string equals the `toolMap`-
translated, deduplicated source list, and (b) no bare abstract category name
(`read`/`search`/`edit`/`execute`/`todo`) appears in the projected string. This is a strict
superset of this task's stated acceptance criteria (which only required checking
`orchestrator.md` for `Read`/`Bash` presence and `read`/`execute` absence).

`python3 tests/run.py --suite functional -v` (relevant excerpt — full suite run together with
T301, see its Execution notes for the complete before/after):
```
Ran 266 tests in 11.175s
OK (skipped=13)
```
`test_claude_code_agents_use_tools_string` passes for all 27 generated agents, including
`orchestrator`.

Committed together with T301 on branch `bugfix/301-claude-code-tool-projection`
(commit `4427a83`) — same root cause, same file, same verification run.
