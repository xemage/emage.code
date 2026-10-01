# Case: validate-workflow-gate-verdict-sources (known_failing / tracked_defect)

## Command under test
`/validate-workflow`

## Brief (illustrative — not executed live)
"Validate the workflow (`all`)." The part of the run this case reproduces is step 6's per-gate
verification, performed against the gate definitions this repository actually ships.

## What this checks
`implementation/knowledge/commands/validate-workflow.md` `## Validation Gate References` steps 5 and
6, verbatim:

> 5. **Check all validation gates.** Gate types, executors and the VERDICT format are defined in the `validation-gates` skill (§ Gate Types, § Verdict Format); the orchestrator's invocation points are in the `orchestrator` agent's § Validation Gates. Each gate below names where it is defined:
>    - Plan approval gate — `plan-approve-execute` skill § The Three Phases › Phase 2: Approve
>    - Architecture briefing gate — `orchestrator` agent § Core Workflow › Phase 3: Development, step 1
>    - Integration checkpoint gate — `validation-gates` skill § Gate Types, **Integration**
>    - Code review gate — `validation-gates` skill § Gate Types, **Implementation**
>    - Security audit gate — `validation-gates` skill § Gate Types, **Security**
>    - Release gate — `validation-gates` skill § Gate Types, **Release**
>
>    The first two are workflow steps, not among the `validation-gates` skill's five gate types.
> 6. For each gate, verify:
>    - Gate is reachable in workflow
>    - Gate produces a VERDICT
>    - Gate blocks progression on FAIL
>    - Gate escalation path is defined

together with the command's `## Rails` Failure mode, verbatim:

> **Failure mode**: If any gate is unreachable, doesn't produce a VERDICT, doesn't block on FAIL, or lacks an escalation path, the overall VERDICT is FAIL with that gate named in the remediation backlog.

and the `## WORKFLOW VALIDATION VERDICT` template's declared value space,
`- **Status**: PASS | CONDITIONAL_PASS | FAIL`.

**The assertion is that step 6's second verification can succeed for every gate step 5 lists** —
i.e. that `Status: PASS`, which the template declares as a possible outcome, is reachable at all.
`check()` performs that verification deterministically, gate by gate, against byte-identical copies of
the three files step 5 cites. A gate *produces a VERDICT* iff its cited definition:

- **(a)** is a row of the `validation-gates` skill's § Gate Types table whose kind is admitted by that
  skill's § Verdict Format — the format step 5 itself names — which opens "Every gate MUST produce a
  verdict in this format" and pins `**Gate:** architecture | implementation | integration | security |
  release`; or
- **(b)** itself declares a VERDICT (the word appears in the cited definition).

### Result: 4 of 6 — and the two that fail are the two step 5 says are not gates
| Gate | Cited definition | Produces a VERDICT? |
|---|---|---|
| Plan approval | `plan-approve-execute` § Phase 2: Approve | **No** — its declared outcomes are **Approve / Revise / Reject**, and "verdict" appears nowhere in the section |
| Architecture briefing | `orchestrator` § Phase 3, step 1 | **No** — "Run Architecture Briefing: … confirm API boundaries and ownership"; no output is declared |
| Integration checkpoint | `validation-gates` § Gate Types, Integration | Yes, by (a) |
| Code review | `validation-gates` § Gate Types, Implementation | Yes, by (a) |
| Security audit | `validation-gates` § Gate Types, Security | Yes, by (a) |
| Release | `validation-gates` § Gate Types, Release | Yes, by (a) |

So, by the command's own Failure mode, every faithful `/validate-workflow` run against this repository
returns `FAIL`, naming the plan approval and architecture briefing gates — regardless of the workflow's
actual health. **This is parked item P9 (`plan-084` §4), confirmed.** The command's text half-knows it:
step 5's closing sentence concedes the first two "are workflow steps, not among the `validation-gates`
skill's five gate types", and the Verdict Format's `**Gate:**` field gives a verdict for either of them
no admissible value — then step 6 requires one from each.

### Why `tracked_defect`, and why this case does not resolve it
`ADR-007` branch 1 asks whether a clause contradicts "another clause of the same command file"; step
6's universal "For each gate … produces a VERDICT", applied to step 5's own list, contradicts step 5's
closing sentence. That is a defect awaiting adjudication, not a capability the surface was never meant
to have, so `capability_gap` would mis-describe it. Plausible exits exist in both directions — step 6
could scope the VERDICT requirement to the four verdict gates; step 5 could cite the orchestrator's
**ARCHITECTURE GATE** (§ Validation Gates, which does "Produce VERDICT") instead of the briefing; or the
two workflow steps could be given verdicts — and choosing among them is the adjudicating task's job, not
this case's (`T561` §7: no command file is edited). `ADR-007` §5 forbids the other exit, relaxing this
check.

### Why the case has no hand-authored report
Every hand-authored `/validate-workflow` report would decide this case by its author's choice: a report
claiming `PASS` would fail and one honestly claiming `FAIL` would pass, so the outcome would measure the
fixture, not the command (`sprint-status-dag-ledger-grounded/brief.md` declines the same move in the
other direction). Here every byte `check()` reads is real and the result follows from the shipped
definitions alone. A green case built on an honest-`FAIL` report was considered and rejected: it would
pass only while P9 persists, and turn red the moment P9 is fixed — encoding the defect as the
expected behaviour.

### Readings deliberately not asserted
- **Step 6's other three verifications** (reachability, blocking on FAIL, escalation path). They are
  properties of the workflow's behaviour rather than of a cited definition's text; asserting them by
  keyword would be guessing. The VERDICT verification is the one step 5 makes checkable by naming the
  format.
- **The report's own `## WORKFLOW VALIDATION VERDICT` block shape** — see above; there is no real
  report and an authored one would decide the case.
- **(b) is lenient on purpose**: any mention of a verdict in the cited definition counts, so the case
  cannot be accused of failing a gate on wording. Both failing gates fail even under that leniency.

## Pass condition
For each of the six gates step 5 lists, the definition it cites resolves in the fixture copy of the
cited file (fence-aware heading path, then table row or numbered step) and produces a VERDICT by (a) or
(b). **Today two do not, so `check()` returns `False`.**

## Discrimination (demonstrated at authoring, on temp copies)
`check()` is `False` on the fixture, and becomes `True` when — and only when — **both** workflow-step
definitions are given a VERDICT (`Produce VERDICT.` appended to the Phase 2: Approve opening line and to
Phase 3 step 1). With that fix applied, it returns `False` again if: only the plan approval gate is
fixed; `release` is removed from the Verdict Format's `**Gate:**` field; "Every gate MUST produce a
verdict" is removed; the Release row is deleted from § Gate Types; or the VERDICT is added to Phase 3
step 2 instead of step 1 (the selector resolves the cited step, not its neighbourhood).

## Provenance
**Fully real.** `fixture/implementation/knowledge/skills/validation-gates/SKILL.md`,
`fixture/implementation/knowledge/skills/plan-approve-execute/SKILL.md` and
`fixture/implementation/knowledge/agents/orchestrator.md` are byte-identical copies of the three source
files step 5 cites, at `develop` `8fd1f5f`; `cmp` against `implementation/knowledge/` to confirm. They
are frozen here: if a later task amends any of them, this fixture does not follow, and re-fixturing is
the exit (`ADR-007` branch 3b's procedure applied to inputs).

There is no `/validate-workflow` output to use instead:

```
grep -rl 'WORKFLOW VALIDATION VERDICT' --include=*.md . | grep -vE '/commands/|/prompts/|/skills/|/agents/|/workflows/'  ->  0 matches
```
