# plan-066 — T515: contract authority for the tracked-defect golden cases

**Status: dispatched 2026-09-24.**
Based on: `docs/plans/plan-064-roadmap-v8-breadth-and-utility.md` (Phase 9), `docs/tasks/task-T514.md`.

## 0. Why this document exists

`plan-064` Decision **D2** fixes the execution order as Phase 10 → **Phase 9** → Phase 8 → Phase 11.
Phase 10 closed with `T514`. This is the first task of Phase 9, and it exists as a separate planning
note for two reasons: it departs from `plan-064` §2.8's written first step, and scoping it surfaced
a structural finding that changes what Phase 9's remaining work looks like.

## 1. Departure from §2.8, and why

§2.8 recommended starting Phase 9 with *"the protected-path exception request and the first two or
three golden cases"* — i.e. begin authoring new coverage. This task instead takes Phase 9's other
listed item, the tracked defects, first.

Three reasons:

1. **`T514` just produced fresh, precise diagnoses.** Its closure identified these six cases as the
   entire remaining distance from 25/3 to 28/0 in the agent category. That diagnosis is at its most
   useful now.
2. **The protected-path exception is not needed yet.** §2.8 assumed the first Phase 9 task would
   have to touch `tests/golden/**`. Scoping showed the *decision* can be made read-only, and should
   be — see §2. The exception moves to the follow-up implementation task, where it is genuinely
   required and can be scoped to named files.
3. **It is the cheaper question.** Deciding six existing conflicts is bounded; authoring fourteen
   new cases is not.

Authoring new coverage is not dropped — it is Phase 9's larger pole and follows this task.

## 2. The finding that reshaped the task

The original intent was a single task: fix the defects, then reclassify the cases. Reading the cases
showed that will not work.

**Each defect case is one half of a zero-sum pair.** Every affected command has both a defect case
whose fixture is a real repository artifact, and a sibling `expected_pass` case whose fixture is
hand-authored to the declared contract. Both siblings' `expect.py` files encode the *same* contract.
Amending a command to match the real corpus therefore makes the defect case pass and the paired
sibling fail. The naive fix relocates the failure rather than removing it.

That is a judgment problem — which artifact convention is authoritative, and why — not an
implementation problem. Bundling it with the edits would have had a dispatched agent discovering the
trap mid-task and improvising a resolution inside a change that also touches frozen files. Hence the
split:

- **`T515` (this task)** — decide, read-only, no protected-path authorization, output an ADR plus a
  resolution table.
- **follow-up** — implement the decided changes under an explicit, file-scoped protected-path
  authorization, once the decisions have been reviewed on their own.

## 3. Ownership and the conflict of interest

Owner: **Solution Architect**, which owns zero commands.

The agents that own the affected commands are also, three of them, the agents still at
`experimental` that a favourable resolution would promote. Asking any of them to rule on whether
their own command's contract should bend is a direct conflict. `T514` handled a milder version of
this (its implementer was one of the eight components it evaluated) by having the top-level session
independently re-verify the result against a script. Here there is no script: the outcome turns on
human-equivalent judgment, so the control has to be structural — a disinterested owner — rather than
after the fact.

The brief states the incentive explicitly and requires the promotion impact of each verdict to be
recorded, including verdicts that unblock nothing.

## 4. Priority

**P1**, and honestly so: this blocks Phase 9, the command category's first promotions, and three
agent promotions. Unlike `T514` — where `P2` was both true and convenient — there is no honest way
to call this nice-to-have.

The self-referential ledger trap (`§3.5`: an open P0/P1 row naming a component id blocks that
component's own promotion claim) is therefore handled by phrasing rather than by priority. The brief
uses display-name form for every `stable` component and refers to held-out cases positionally. This
was verified mechanically against `check-maturity.py` before dispatch, not reasoned about.

The three blocked agents *are* named in the brief, which is why this task does not promote them:
promotion happens after `T515` closes and its row archives, removing it from the active-row scan.

## 5. Scope boundary

`T515` produces two documents and modifies nothing else. Implementation, reclassification, the
fourteen uncovered commands, and the two capability gaps are all out of scope and follow.

## 6. A §3.5 matcher defect found while writing this brief

The `P1` decision in §4 was verified by running `check-maturity.py` against the drafted brief rather
than by reasoning about it. That surfaced a latent defect worth recording, because it will affect
every future `P0`/`P1` task and it is not this task's to fix.

`_ledger_defect()` matches a component id anywhere in a brief's free text, with
`(?<![\w-])<id>(?![\w-])`. It cannot distinguish *"this component has a defect"* from *"this
document is worth reading."* Two consequences, both hit on the first draft:

1. **The agent-worktree branch convention is self-blocking.** `git-workflow.md` mandates
   `agent/<agent-name>/<task-id>`. Written into a brief, `agent/solution-architect/T515` matches
   `solution-architect` — the slashes are not in `[\w-]`. So *any* `P0`/`P1` brief that spells out
   its own branch name per the mandated convention blocks its own owner's promotion claim. This has
   not surfaced before only because almost every agent was `experimental` until `T514`; it becomes
   routine now that 25 are `stable`.
2. **An instruction cannot be cited by filename.** Citing `.claude/rules/git-workflow.md` matches
   `instruction/git-workflow` (the trailing `.` is not in `[\w-]`), demoting a `stable` instruction
   for the offence of being referenced. The same applies to `coding-standards.md`,
   `security-guidelines.md`, and `poc-guidelines.md` — the four documents briefs most need to cite.

Both were worked around here by phrasing (branch name described rather than spelled; instruction
referred to by title). That is a workaround, not a fix: it degrades brief clarity, it is invisible
to whoever writes the next brief, and it will be rediscovered by trial and error each time.

The real fix is to narrow the signal — scan a declared field (an explicit `Affects:` list, or the
`Owner` column, which is already excluded) instead of the whole body — so that mentioning a
component is not the same as indicting it. That is a change to `check-maturity.py` and to §3.5 of
`maturity-promotion-criteria-v1.md`, and it should be its own task in Phase 9 rather than being
smuggled into a decision task. It is not urgent: the workaround holds, and the defect makes the gate
*over*-strict, never under-strict, so nothing is wrongly promoted in the meantime.
