# T515 — Decide contract authority for the six tracked-defect golden cases

**Status:** pending
**Owner:** Solution Architect
**Priority:** P1
**Depends on:** —
**Affects:** command/plan, command/new-feature, command/prepare-release
**Plan:** `docs/plans/plan-066-t515-command-contract-authority.md` (`plan-064` Phase 9)

## 1. Objective

Six golden cases carry `status: known_failing` with `known_failing_category: tracked_defect`.
They are the entire remaining blocker on criteria 3 and 7 for the three agents still at
`experimental`, and they also block their own commands' promotion. Each one records a conflict
between a command's *declared* contract and the repository's *actual* artifact convention.

**This task decides which side of each conflict is authoritative. It does not implement the
decision.** The output is a decision record plus a resolution table precise enough that a
follow-up implementation task can be written mechanically from it.

The split is deliberate: §3 below documents a structural trap that makes the naive fix wrong in
every case, and that trap is a judgment problem, not a coding problem. Settling it in a
read-only task keeps the judgment reviewable on its own merits, and keeps it out of the same
change that touches frozen files.

## 2. Why you, and what that means

You own **zero commands**. The four agents with a stake in the outcome — the ones that own the
affected commands, three of which are still `experimental` and would be promoted by a favourable
resolution — are exactly the wrong parties to decide whether their own commands' contracts should
bend. Your disinterest is the reason this is assigned to you.

Concretely: **a resolution that happens to unblock a promotion is not thereby a good resolution.**
If the honest answer for a given case is "the command is right, the corpus is wrong, this case
stays failing," say that. "All six resolve cleanly" is a suspicious result, not a target. State in
your record how many of the three blocked agents each resolution would and would not unblock, so
the reader can see the incentive you were working against.

## 3. The structural trap — read this before forming any opinion

Each defect case has a **paired sibling case for the same command, with the opposite fixture**:

| Command | Defect case (real artifact, currently failing) | Paired sibling (hand-authored, currently passing) |
|---|---|---|
| `/plan` | `plan-real-doc-header-drift` | `plan-required-sections-compliant` |
| `/new-feature` | `new-feature-real-checkpoint-format-drift` | `new-feature-checkpoint-line-compliant` |
| `/prepare-release` | `prepare-release-real-verdict-missing` | a sibling that is **held out** |

The sibling's `expect.py` encodes the *same* contract. So the obvious fix — "0 of 34 real plan
documents use the declared headers, therefore amend the command to match reality" — **makes the
paired sibling fail.** The failure moves; it does not go away. Any resolution you propose must
state explicitly what happens to the paired sibling, and a resolution that silently breaks one is
not a resolution.

The remaining two defect cases live under `tests/golden/held-out/`. Enumerate them yourself by
scanning for `known_failing_category: tracked_defect`; they are in scope and must be decided too.

## 4. Inputs

- `tests/golden/` — the six defect cases and their siblings. Each case is
  `case.yaml` + `brief.md` + `fixture/` + `expect.py`; `expect.py` holds the real contract check.
  Read `tests/golden/README.md` first for the case contract and the two `known_failing` flavours.
- `implementation/knowledge/commands/` — the declared contracts. The relevant clauses are cited by
  file and step in each case's `known_failing_reason`.
- `AGENTS.md` and `docs/checkpoints/`, `docs/plans/` — the real corpus the drift is measured
  against.
- `docs/artifacts/maturity-promotion-criteria-v1.md` §3.5 — the defect-check definition that makes
  these cases block promotion.
- `docs/decisions/_template.md`.

## 5. Constraints

1. **Read-only outside your two output files.** Do not edit any command file, any file under
   `tests/golden/`, or any `expect.py`. You are deciding, not implementing.
2. **`tests/golden/**` is a protected path** (`docs/artifacts/protected-paths-v1.md`). This task is
   *not* authorized to modify it — reading is fine, writing is not. The follow-up implementation
   task will carry that authorization explicitly; this one deliberately does not need it.
3. **Held-out discipline.** Case IDs under `tests/golden/held-out/` must never appear in any file
   outside that directory — enforced by `tests/functional/test_golden_held_out_isolation.py`. In
   your outputs refer to them positionally ("the held-out defect case for the release command"),
   never by ID, and do not name which command the second one belongs to if that would identify it.
4. Do not weaken a case to make it pass. "Relax the check until the fixture conforms" is the
   failure mode this whole exercise exists to catch.
5. Verdicts must be one of: **amend the contract** (the corpus is right), **fix the corpus** (the
   contract is right — then say concretely what would have to change and whether the frozen
   historical fixture could ever pass), **widen the contract to admit both forms** (then say why
   both are legitimate, not merely why it is convenient), or **reclassify the case** (e.g. this is
   a `capability_gap`, not a `tracked_defect` — then justify against README's definitions).

## 6. Expected outputs

1. `docs/decisions/ADR-007-command-contract-authority.md`, from `_template.md`. It must state a
   general principle for resolving contract-vs-corpus conflicts — the six cases are the evidence
   that forces the principle, not six independent judgment calls — and then apply it.
2. `docs/artifacts/command-contract-resolution-v1.md`: one row per defect case with the verdict,
   the exact command clause at issue, the effect on the paired sibling, the files a follow-up task
   would have to touch, and the promotion impact.

Both under `docs/`. Do not create or transition task rows — that is the orchestrator's job.

## 7. Acceptance criteria

- [ ] All six `tracked_defect` cases are enumerated by your own scan and each has a verdict.
- [ ] Every verdict names the paired sibling's fate explicitly, or states that no sibling exists.
- [ ] The ADR states a general principle and shows each case following from it.
- [ ] Promotion impact is stated per case, including cases that unblock nothing.
- [ ] No file under `tests/golden/`, no command file, and no `expect.py` is modified —
      `git status` in your worktree shows only your two new documents.
- [ ] No held-out case ID appears in either output.
- [ ] Corpus claims you rely on are re-verified by running the survey yourself, not copied from
      `known_failing_reason`. Those reasons were written at authoring time and may have drifted;
      if a figure is now wrong, say so — that is a finding, not a nuisance.

## 8. Working agreement

Branch from `develop` in a worktree — name it per the agent-worktree convention in the Git Workflow
rules under `.claude/rules/`, i.e. `agent/<your-agent-slug>/<task-id>`, using this task's ID. Do not
work in the primary checkout. Conventional Commits. Do not merge your own branch and do not push to
`develop` or `main` — hand the branch back and the orchestrator opens the MR.

Use the convention as stated — spelling out your own branch name is fine. An earlier version of
this brief avoided doing so, because the §3.5 defect check used to free-text-scan brief bodies for
component ids and would have read the slug in `agent/<slug>/<id>` as an indictment, blocking the
owner's own promotion claim. `T516` fixed that: defects are now declared in the `**Affects:**` field
above, and a mention is no longer an accusation. Background in
`docs/plans/plan-066-t515-command-contract-authority.md` §6 and
`docs/plans/plan-067-t516-defect-check-declared-field.md`.

## 9. Blocker protocol

Report blockers as `technical` | `dependency` | `unclear_requirements` | `external`, with severity
`critical` | `major` | `minor`. Max 2 retries, then escalate. Do not silently narrow scope: if a
case resists a clean verdict, report it as an open question with the options and their
consequences rather than forcing a call to fill the table.
