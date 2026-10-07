# Case: validate-workflow-gate-verdict-sources (expected_pass)

## Command under test
`/validate-workflow`

## Brief (illustrative — not executed live)
"Validate the workflow (`all`)." The part of the run this case reproduces is step 6's per-gate
verification, performed against the gate definitions this repository actually ships, together with
two structural properties of step 5's list itself.

## What this checks
`implementation/knowledge/commands/validate-workflow.md` `## Validation Gate References` steps 5 and
6, as amended by `T567`, verbatim:

> 5. **Check all validation gates.** Gate types, executors and the VERDICT format are defined in the `validation-gates` skill (§ Gate Types, § Verdict Format); the orchestrator's invocation points are in the `orchestrator` agent's § Validation Gates. Each gate below names where it is defined:
>    - Architecture review gate — `validation-gates` skill § Gate Types, **Architecture**
>    - Code review gate — `validation-gates` skill § Gate Types, **Implementation**
>    - Integration checkpoint gate — `validation-gates` skill § Gate Types, **Integration**
>    - Security audit gate — `validation-gates` skill § Gate Types, **Security**
>    - Release gate — `validation-gates` skill § Gate Types, **Release**
>
>    These are the skill's five gate types, in the order of its § Procedures › 4. Gate Pipeline for a Release. Plan approval (`plan-approve-execute` skill § The Three Phases › Phase 2: Approve, a user decision: Approve / Revise / Reject) and the architecture briefing (`orchestrator` agent § Core Workflow › Phase 3: Development, step 1) are workflow steps, not validation gates, and are not checked here.
> 6. For each gate, verify:
>    - Gate is reachable in workflow
>    - Gate produces a VERDICT
>    - Gate blocks progression on FAIL
>    - Gate escalation path is defined

together with the command's `## Rails` Failure mode, unchanged, verbatim:

> **Failure mode**: If any gate is unreachable, doesn't produce a VERDICT, doesn't block on FAIL, or lacks an escalation path, the overall VERDICT is FAIL with that gate named in the remediation backlog.

and the `## WORKFLOW VALIDATION VERDICT` template's declared value space, also unchanged,
`- **Status**: PASS | CONDITIONAL_PASS | FAIL`.

**The assertion is that step 6's second verification can succeed for every gate step 5 lists, that
the list is the complete set of gate kinds the cited Verdict Format admits, and that this check's
mirror of the list is the command's list, in order.** Together these say that `Status: PASS`, which
the template declares as a possible outcome, is reachable against the shipped definitions, and that
the list step 6 iterates over is the one step 5's "Check all validation gates" promises.

`check()` is the AND of three predicates, evaluated against byte-identical copies of the command file
and of the one file its step 5 now cites.

**1. Per-gate (unchanged from the pre-`T568` check, byte for byte).** A gate *produces a VERDICT* iff
its cited definition:

- **(a)** is a row of the `validation-gates` skill's § Gate Types table whose kind is admitted by that
  skill's § Verdict Format — the format step 5 itself names — which opens "Every gate MUST produce a
  verdict in this format" and pins `**Gate:** architecture | implementation | integration | security |
  release`; or
- **(b)** itself declares a VERDICT (the word appears in the cited definition).

**2. Completeness (new).** The set of § Gate Types kinds `check()` cites (lower-cased) must **equal**
the set the Verdict Format's `**Gate:**` field admits, and that set must be non-empty. A step 5 that
omits any admitted gate kind fails. This is the omission the pre-`T568` check could not see: the old
list cited four of the five kinds and left out Architecture.

**3. Ordered list fidelity (new).** In the fixture copy of the command, take the first unfenced line
starting with `5. **Check all validation gates.**`, collect each following line matching
`^   - (.+?) — ` (the separator is U+2014 EM DASH) until the first line matching `^\d+\. `, and
require the captured names to **equal** `check()`'s own gate list, in order. A step 5 whose list drifts
from the check's mirror fails, and so does a step 5 that re-adds a workflow step as a gate.

### Result: 5 of 5, complete, and in order
| Gate | Cited definition | Produces a VERDICT? |
|---|---|---|
| Architecture review | `validation-gates` § Gate Types, Architecture | Yes, by (a) |
| Code review | `validation-gates` § Gate Types, Implementation | Yes, by (a) |
| Integration checkpoint | `validation-gates` § Gate Types, Integration | Yes, by (a) |
| Security audit | `validation-gates` § Gate Types, Security | Yes, by (a) |
| Release | `validation-gates` § Gate Types, Release | Yes, by (a) |

| Predicate | Result |
|---|---|
| Completeness: cited kinds `{architecture, implementation, integration, security, release}` equal the `**Gate:**` field's kinds | Yes |
| Ordered list fidelity: step 5 lists Architecture review, Code review, Integration checkpoint, Security audit, Release, which is the check's list in order | Yes |

So a faithful `/validate-workflow` run against this repository can return `PASS`: no listed gate is
forced to fail step 6's VERDICT verification by its definition alone.

### Resolution
Before `T567`, step 5 listed six gates. Two of them, the plan approval gate (`plan-approve-execute`
§ Phase 2: Approve, which declares Approve / Revise / Reject) and the architecture briefing gate
(`orchestrator` § Core Workflow › Phase 3, step 1, which declares no output), could not produce a
VERDICT, and step 5's own closing sentence said they were "workflow steps, not among the
`validation-gates` skill's five gate types". The command's Failure mode therefore made every faithful
run `FAIL` regardless of the workflow's health. This was parked item P9 (`plan-084` §4), which this
case confirmed while `known_failing` (`tracked_defect`).

`docs/artifacts/validate-workflow-gate-resolution-v1.md` resolved it under `ADR-007` branch 1, the
same-file prong ("A command file may also not contradict itself — where it does, the clause the rest
of the file and the corpus both disagree with is the defective one"), on two quoted contradictions:

- **C1:** step 5's first two bullets against its own opening, its closing sentence, step 6, the Failure
  mode and step 11's `PASS`.
- **C2:** step 5's "Check all validation gates" against a list that omitted the Architecture gate.

`T567` amended step 5 to the skill's five gate types in pipeline order (MR !453), with step 6, the
Failure mode and step 11 unchanged. This case was realigned to that amended contract by `T568`. No
predicate was relaxed (`ADR-007` §5):

- **Validation 1.** The per-gate predicate and its value constraints are byte-identical. The check
  goes from six per-gate entries to five, but the two removed entries were structurally
  unsatisfiable against the shipped definitions. They could only fail, regardless of the workflow's
  actual health, so they measured nothing about the workflow. In their place the check gains
  completeness and ordered list fidelity, which the old check lacked. The number of
  verdict-producing gates checked rises from four to five. The orchestrator ruled this not a
  weakening, on condition that both new predicates are added and demonstrated (artifact §9.2); the
  Discrimination section below demonstrates them.
- **Validation 2.** The only scorecard transition is this case moving from `known_failing` to
  `expected_pass`.

Whether `/validate-workflow` should check plan approval as a non-gate is a separate scope question,
parked as P36. It is not asserted here.

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

*Note added by `T568`:* the "two failing gates" in the last bullet are the pre-`T568` plan approval
and architecture briefing entries, which are no longer in step 5. All five current rows pass by (a),
so the (b) path is unused today. It is kept so that the per-gate predicate stays byte-identical to the
one it replaces.

## Pass condition
For each of the five gates step 5 lists, the definition it cites resolves in the fixture copy of the
`validation-gates` skill (fence-aware heading path, then table row) and produces a VERDICT by (a) or
(b). The cited kinds equal the Verdict Format's admitted kinds, and the fixture command's step 5 list
equals the check's list in order. **Today all three hold, so `check()` returns `True`.**

## Discrimination (re-derived by `T568`, on temp copies outside `tests/golden/`)
`check()` returns `True` on an unmodified copy (control). Each perturbation below was applied to a
fresh copy of the case directory. Every substitution was asserted to match exactly once, and the copy's
content digest was confirmed to differ from the unmodified case before its result was read. Each copy was
then discarded. `check()` returns `False` for every one:

| # | Perturbation | Predicate that fails | `check()` |
|---|---|---|---|
| 1 | The old `Plan approval gate — …` bullet re-inserted into the fixture command's step 5 | fidelity (6 names vs 5) | `False` |
| 2 | The Code review and Integration checkpoint bullets swapped in the fixture command | ordered fidelity | `False` |
| 3 | The `Architecture review gate` entry removed from `GATES` in a temp `expect.py`, and the matching bullet removed from the fixture command | completeness (fidelity holds, all four remaining per-gate entries hold) | `False` |
| 4 | `architecture` removed from the skill's `**Gate:**` field | per-gate (Architecture review) and completeness | `False` |
| 5 | The Architecture row deleted from § Gate Types | per-gate (Architecture review) | `False` |
| 6 | "Every gate MUST produce a verdict" removed | per-gate (all five) and completeness | `False` |
| 7 | The Release row deleted from § Gate Types | per-gate (Release) | `False` |

Contrast: the pre-`T568` `check()` (six gates, per-gate only), run on the new fixture, returns
`False`. Its plan approval and architecture briefing entries cite files the fixture no longer carries.

## Provenance
**Fully real.** Two fixture files, each a byte-identical copy of its source at the `develop` commit
named below; `cmp` against that commit's `implementation/knowledge/` to confirm:

- `fixture/implementation/knowledge/commands/validate-workflow.md` — the amended command, added by
  `T568`, copied at `develop` `a6be6b0` (the merge of `T567`, MR !453). The list-fidelity predicate
  reads it. The source has since changed only in its frontmatter (`maturity: experimental` →
  `stable`, `T569`), which `check()` does not read; this copy was not refreshed.
- `fixture/implementation/knowledge/skills/validation-gates/SKILL.md` — the one file step 5 now cites.
  First copied at `a6be6b0`; re-copied by `T583` at `develop` `7be9926`, after `T582` (MR !483)
  amended, within § Verdict Format, the verdict template's Conditions line, § Verdict Rules and
  § Severity Definitions, and § Procedures › 3. Handle a CONDITIONAL_PASS Verdict. `cmp` confirmed
  the re-copy identical to source. `check()` reads only § Gate Types and, from § Verdict Format,
  the `**Gate:**` field and "Every gate MUST produce a verdict", none of which `T582` changed.

`T568` removed the copies of `skills/plan-approve-execute/SKILL.md` and `agents/orchestrator.md`. After
`T567`, no step 5 bullet cites them and `check()` reads neither. Keeping them would have made the
statement "copies of the files step 5 cites" false. The copies are frozen here: if a later task amends
either source, this fixture does not follow, and re-fixturing is the exit (`ADR-007` branch 3b's
procedure applied to inputs).

There is no `/validate-workflow` output to use instead. The grep this section previously gave did not
return 0 matches as it claimed: it returned 2, the resolution artifact and this `brief.md`, both of
which only *mention* the block (artifact §9.1). It is restated here with `tests/golden/` and
`docs/artifacts/` pruned before traversal, which also keeps it out of `tests/golden/held-out/`:

```
find . \( -path ./tests/golden -o -path ./docs/artifacts \) -prune -o -type f -name '*.md' -print0 | xargs -0 grep -l 'WORKFLOW VALIDATION VERDICT' | grep -vE '/commands/|/prompts/|/skills/|/agents/|/workflows/'  ->  0 matches (at develop a6be6b0 plus this change)
```
