# T806 — Security review of T805 against ADR-016

**ID:** T806
**Owner:** security-engineer
**Status:** done
**Priority:** P1
**Tier:** standard
**Depends on:** T805
**Affects:** —
**Created:** 2026-11-12
**Completed:** 2026-11-12
**Based on:**
- `docs/plans/plan-157-confirmation-as-validity-condition.md` (task T806)
- `docs/decisions/ADR-016-security-engineer-confirmation-as-validity-condition.md`

## 1. What and why

Review T805's diff: does the skill state ADR-016's fourth condition, its consequence and O-A to O-C as ruled, no more and no less; are W1 to W3 wording only; do the pins hold each element; did anything weaken ADR-011, ADR-012 or the rest of ADR-015.

## 2. Output

The text of `docs/artifacts/security-review-t806-adr-016-apply-v1.md`, returned to the orchestrator, who commits it. Verdict `PASS` | `CONDITIONAL_PASS` | `FAIL`; findings graded `SECURITY:*`.

## 3. Constraints

Read-only; no source is modified.

**Range under review:** `942ca923..946a2a9a` on `agent/solution-architect/T804` (`97e1c0b4` source and pins, `946a2a9a` mirrors, registry, drift declaration), read in the worktree `/home/emage/Code/emage/worktrees/agent-solution-architect-T804`.

**Evidence from the orchestrator's own verification (2026-11-12):** D1, D2, W1, W2 and W3 each occur exactly once in the skill source and once in ADR-016; D2 stands directly between D1's consequence sentence and "The review date is then the plan's deadline"; "It covers only the release" no longer occurs; the word diff of the skill source shows only those five changes; `MUTATIONS` 73 to 95; the pin test (30 tests), validate-tasks, link integrity, team health, scorecard, sync `--check` and registry `--check` exit 0; `--print-drift` lists exactly the four installed `validation-gates/SKILL.md` copies, as declared. The full suite is not yet run at this range. Never read secret paths or `tests/golden/held-out/`.

## 4. Acceptance criteria

Each finding has a file and line; each claim not verified is marked **(unverified)**.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
