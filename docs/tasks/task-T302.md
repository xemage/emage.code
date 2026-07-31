# Task T302 — Author the Phase 2/3 PoC debt scorecard

**ID:** T302
**Owner:** technical-writer
**Status:** done
**Priority:** P0
**Depends on:** T300
**Created:** 2026-07-31
**Completed:** 2026-07-31
**Based on:** docs/plans/plan-016-pattern-a-hardening-and-phase23-poc-closure.md

## Objective
Produce the formal, honest closure record for the Phase 2/3 self-improvement-loop work
(T220–T241), per `.claude/rules/poc-guidelines.md` § "Debt Scorecard". This document is the
historical record that replaces the fabricated "done"/"promoted" claims currently in
`docs/tasks/completed-tasks.md`.

## Inputs
- `.claude/rules/poc-guidelines.md`
- `implementation/scripts/sia-executor.py` (contains the literal `mock_delay`/"Simulates SIA
  execution" evidence)
- `docs/artifacts/t238-metrics-final.json` (zero-signal evidence)
- `docs/artifacts/t240-deployment-report-v1.md` ("Mock LLM provider" admission)
- `docs/plans/plan-016-pattern-a-hardening-and-phase23-poc-closure.md` §0 (findings table)

## Expected outputs
- `docs/artifacts/phase2-3-poc-debt-scorecard-v1.md` (new file)

## Acceptance criteria
1. Contains a `## Hypothesis` section restating what Phase 2/3 was actually testing (SIA
   generations captured by CWSO/Polar with a merge+eval reward, feeding a fine-tune of an
   improved coding model).
2. Contains `## Result` = **INVALIDATED** — do not soften this verdict.
3. Contains a `## Debt Inventory` table with at minimum the 4 rows specified in plan-016 Wave 2
   (sia-executor.py mock path; t238 zero-signal metrics; impossible v1-ft model claim; T233/T239/T241
   promotion claims resting on that same zero-signal data), each with a Production Effort estimate.
4. Contains a `## Summary` (counts) and a `## Recommendation` stating No-Go for production and that
   any future Pattern B/C attempt must start from a real (non-mocked) LLM call path, a real
   evaluator with non-degenerate scores, and a real open-weight model with accessible weights.
5. `test -f docs/artifacts/phase2-3-poc-debt-scorecard-v1.md` → OK.

## Blocker protocol
Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`)
+ severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.

## Execution notes
Delegated to technical-writer agent (2026-07-31). Verified all 5 acceptance criteria directly
against `docs/artifacts/phase2-3-poc-debt-scorecard-v1.md`:
1. `## Hypothesis` section present, restates SIA/CWSO-Polar/fine-tune/deploy claim — met.
2. `## Result` line reads exactly `INVALIDATED`, unsoftened — met.
3. `## Debt Inventory` table contains the 4 required rows (sia-executor.py mock_delay path;
   t238-metrics-final.json zero-signal; t240-deployment-report-v1.md impossible v1-ft claim;
   completed-tasks.md T233/T239/T241 promotion claims), each with Production Effort = L — met.
4. `## Summary` (4 total / 4 critical / 0 medium / 0 low) and `## Recommendation` (No-Go,
   real-LLM-path/real-evaluator/real-open-weight-model requirements) present — met.
5. `test -f docs/artifacts/phase2-3-poc-debt-scorecard-v1.md` → OK (confirmed).

Evidence the writer verified directly (re-confirmed by orchestrator via Read):
- `implementation/scripts/sia-executor.py` line 10 docstring: "Simulates SIA execution (mock LLM
  call — Phase 3.3 wires real harness)"; `mock_delay: float = 2.0` constructor param (line 128);
  `--mock-delay` CLI flag (lines 819-821).
- `docs/artifacts/t238-metrics-final.json`: baseline and v1-ft groups both mean_score/median_score
  = 0.0.
- `docs/artifacts/t240-deployment-report-v1.md` line 33: upstream named "Mock LLM provider" on
  port 18080.

`test -f docs/artifacts/phase2-3-poc-debt-scorecard-v1.md && echo OK` → OK
