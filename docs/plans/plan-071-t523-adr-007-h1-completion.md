# plan-071 — T523: completing ADR-007 verdict H-1

**Status: scoped 2026-09-25, awaiting approval to dispatch.**
Based on: `docs/decisions/ADR-007-command-contract-authority.md` branch 1,
`docs/artifacts/command-contract-resolution-v1.md` §H-1,
`docs/artifacts/command-promotion-readiness-v1.md`,
`docs/plans/plan-070-t520-t521-adr-007-execution.md`,
`docs/plans/plan-064-roadmap-v8-breadth-and-utility.md` Phase 9.

## 0. Why now

`plan-070` assigned H-1 to `T520`. `T520` delivered A, B and D and **deliberately left H-1
incomplete**, correctly: the file it needed was not in its §1 authorization table, and
`protected-paths-v1.md` §5.1 forbids the holding agent from extending its own grant. That refusal is
the reason this plan exists — it is the intended behaviour of the control, not a failure.

This plan finishes the one verdict `plan-070` scoped but could not close.

## 1. What `plan-070` got wrong about H-1, and what this plan corrects

`plan-070` folded H-1 into `T520` on the theory that it needed only a `case.yaml` status flip.
`command-contract-resolution-v1.md` says H-1 "flips with no fixture change". That claim is **correct
about the fixture and wrong about the checker**: the case's `expect.py` compiles the
*pre-amendment* pattern, so the case could not have flipped whatever `T520` did to the command.

The correction is recorded rather than quietly fixed, because it is a recurring failure mode — a
resolution artifact describing what *should* follow from a decision, without anyone having executed
it, is a prediction. `T520` was the first thing to test this one, and it failed.

## 2. Scope

One task, `T523`, `P2`, `mechanical` tier, owner **Backend Developer** (the same owner as `T520`,
which has the context and owns zero commands).

| In scope | Out of scope |
|---|---|
| the H-1 case's `expect.py` version regex + docstring | the fixture — see §4 |
| the H-1 case's `case.yaml` status and `known_failing_*` keys | `scripts/scorecard.py` |
| the H-1 case's `brief.md` expected-outcome sentence | any `tests/golden/open/` case |
| — | any other held-out case |
| — | **promoting `command/new-feature`** — see §5 |

`P2` is deliberate, for the reason `T514` and `T522` were `P2`: a `P0`/`P1` row declaring
`Affects: command/new-feature` re-enters criteria 3/7's open-defect scan. Here that is harmless
because this task promotes nothing, but the habit is worth keeping consistent.

## 3. Why the authorization is file-scoped, again

`plan-070` §1 argued that a narrower grant is a better grant, and split C out of `T520` on exactly
that basis. The same reasoning applies here with more force, because this grant touches
`tests/golden/held-out/` — the set three independent controls exist to protect (plan-035's risk
table: this static guard, the evaluator-hash check, and the write-scope exclusion).

So the grant names three files in one directory, and the brief states plainly that the agent may not
widen it and must report a blocker instead. `T520` demonstrated that this instruction is obeyed.

## 4. The trap, stated once so it is not rediscovered

Two edits make this case pass. Only one is correct.

- **Align the checker** — the contract was amended to the single-integer form under branch 1
  (`AGENTS.md` § Artifact Versioning outranks the command). Pointing the checker at the contract now
  in force is the verdict.
- **Rename a fixture file** — also turns the case green, and **inverts it**. The fixture holds two
  real artifacts copied verbatim from this repo's `docs/artifacts/`; the case's own
  `known_failing_reason` records that zero of 43 real artifacts used the two-part form. Renaming
  them would make the suite assert the form `AGENTS.md` does *not* declare, and `T520` would have to
  be reverted.

Verified before dispatch, not assumed: with the regex aligned and the fixture untouched, both
fixture filenames match and `check()` returns `True`.

`ADR-007` §5 — *never resolve by relaxing a check* — also binds. Making the regex accept **both**
forms would pass the case and is out of scope; it is relaxation, not alignment.

## 5. What this does and does not unblock

`T523` **promotes nothing.** Once it merges and the row archives, `command/new-feature` becomes
measurably promotable — a separate component-state change, per `T514`'s and `T522`'s precedent.

It also does not move any agent. `command-promotion-readiness-v1.md` §5 records the correction:
`orchestrator` and `tech-lead` are blocked by verdicts **A** and **H-2**, both branch-3b outcomes
that stay red until the corpus is fixed. H-1 unblocks a command only.

## 6. Where this leaves Phase 9

`command-promotion-readiness-v1.md` measures the remainder. After `T523`:

| Item | Blocked on | Size |
|---|---|---|
| 14 golden cases for uncovered commands | nothing — pure authoring | **the bulk** |
| verdict C (`T521`) | scoped, not dispatched | small |
| verdicts A and H-2 | real corpus fixes | medium |
| promoting `command/new-feature` | `T523` archiving | trivial |

The 14 are the phase's remaining pole and are blocked by an absence rather than a defect — each
fails criterion 4 and nothing else, so one case per command is sufficient. That is the natural next
plan after this one.
