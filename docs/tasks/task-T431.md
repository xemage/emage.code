# Task T431 — Promotion criteria per category

**ID:** T431
**Owner:** tech-lead (matches `plan-041`'s own reasoning — this repo's existing pattern of
`tech-lead` owning standards/criteria work; tool grant checked before dispatch, see below, no
reassignment needed)
**Status:** done
**Priority:** P1 (blocks T432, which cannot be written until these criteria are concrete and
machine-checkable)
**Depends on:** T430 (done — `docs/artifacts/maturity-levels-v1.md`, `implementation/registry/
schema.json`'s reconciled enum)
**Blocks:** T432
**Created:** 2026-09-10
**Completed:** 2026-09-10
**Based on:** `docs/plans/plan-041-phase3-maturity-ladder-detailed-planning.md` (approved, merged
MR !252) — specifically its T431 row; `docs/plans/plan-035-roadmap-v7-ground-up.md` §2.4 Phase 3
(T431's original nominal scope, the five proposed promotion-criteria bullets); `docs/artifacts/
maturity-levels-v1.md` (T430's design artifact — the final enum names and the mandatory-field
policy this task must build on, not re-derive).

## Objective

Define concrete, machine-checkable promotion criteria for each of the four component categories
(`agent`, `command`, `instruction`, `skill`) governing the transitions in the enum
`docs/artifacts/maturity-levels-v1.md` established (`experimental → beta → stable → deprecated`).
`plan-035` §2.4 proposes five criteria for reaching `stable`: (a) ≥1 golden case exercising it,
(b) explicit rails — declared inputs, declared out-of-scope, declared failure mode, (c) referenced
by ≥1 command or agent, (d) documented in the end-user tree, (e) no open P0/P1 defect. **Do not
apply these five uniformly across all four categories without checking whether each one is even
meaningful for that category** — e.g. "referenced by ≥1 command or agent" describes how an
*agent/skill* gets invoked, but a *command* being "referenced by" something is a different
relationship (a command is invoked by a user or another command, not typically "referenced by an
agent" in the same sense); "≥1 golden case exercising it" is well-defined for the workflows the
existing golden suite already covers (`code-review`, `plan`, `prepare-release`, `security-audit`,
`new-feature` — checked in `plan-041`'s own risk table) but it is not yet confirmed whether a
golden case can meaningfully "exercise" an `instruction` (a passive knowledge file, not something
directly invoked) the same way it exercises an `agent` or `command`. Resolve these per-category
gaps explicitly in your output — do not force a uniform rule where the source text's own logic
doesn't actually transfer.

## Inputs

- `docs/plans/plan-035-roadmap-v7-ground-up.md` §2.4 Phase 3 (T431's proposed five criteria)
- `docs/artifacts/maturity-levels-v1.md` (T430 — final enum, mandatory-field policy)
- `implementation/registry/summary.md` (current state — all 77 components at `experimental`)
- `tests/golden/**` (READ-ONLY — see Constraints; use only to check what the existing golden suite
  already covers, to ground your `stable`-tier golden-case criterion in what's actually achievable)

## Expected outputs

- A design artifact (e.g. `docs/artifacts/maturity-promotion-criteria-v1.md`) stating, per category
  (`agent`/`command`/`instruction`/`skill`) and per transition (`experimental→beta`,
  `beta→stable`, any-tier`→deprecated`), the concrete, checkable conditions — worded precisely
  enough that `T432`'s `scripts/check-maturity.py` (the next task) can implement each one as a
  real, non-subjective check, not a criterion requiring human judgment at CI time.
- Explicit resolution (not silence) for each of the two per-category gaps named in the Objective
  above, and any others you find while doing this work.

## Acceptance criteria

1. Every one of the four categories has a complete, stated set of promotion criteria for at least
   the `experimental→beta` and `beta→stable` transitions — no category is left with plan-035's raw
   five bullets un-adapted if any bullet doesn't transfer cleanly.
2. Every stated criterion is phrased as something a script could mechanically evaluate (e.g. "has
   at least one file under `tests/golden/**` whose `brief.md` references this component's id" is
   checkable; "is well-documented" alone is not — sharpen anything like the latter into a checkable
   form, e.g. "has a non-empty `## Responsibilities`/equivalent section and a README/wiki page
   referencing it").
3. The `deprecated` transition's criteria are also stated (`plan-035`'s T436 needs this — "anything
   that cannot reach `stable` in three waves is marked `experimental` or `deprecated`" implies a
   real distinction between the two, not just "not stable").
4. Cites `docs/artifacts/maturity-levels-v1.md` for the enum names/mandatory-field policy rather
   than re-deriving them.
5. `python3 tests/run.py` passes with no regressions (this task is docs/artifact-only in expected
   scope, but confirm no accidental edits elsewhere broke anything).
6. Coding standards (if any code/scripts are written — none expected, but if you add example
   validation snippets, they still apply) and Conventional Commits followed; branch pushed, MR
   opened against `develop`, not self-merged.

## Constraints

- **No paid or recurring-cost API calls.**
- **Do not touch `.mcp.json`, anywhere, for any reason. Do not touch the main checkout
  (`/home/emage/Code/emage/emage.code`).**
- **Do not touch `tests/golden/**`, `scripts/scorecard.py`, `docs/benchmarks/tb-subset.json`/`.md`**
  — read-only reference only, per this task's own Objective/Inputs sections above. If you find you
  need something more than read access to ground a criterion, that is a `type: unclear_requirements`
  blocker to report, not license to edit those paths.
- **Do not touch `feature/T475-codex-platform-integration`. Do not start T432 or any later Phase 3
  task — T432 is a separate dispatch, not part of this task's scope even if it seems natural to
  sketch `scripts/check-maturity.py` while these criteria are fresh in mind.**
- **Confirm your own tool grant before starting** — `implementation/knowledge/agents/
  tech-lead.md`'s registered grant is `[read, search, edit, execute, web, mcp__fetch]`; verify this
  is still accurate before beginning and report immediately as a `type: technical` blocker if it
  has changed or proves insufficient.
- **Work in your own worktree/branch** (`agent/tech-lead/T431`), created from `develop`. Commit as
  you go; run the full test suite before reporting completion. **Do not self-merge** — push and
  open a merge request, then stop.

## Blocker protocol

Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`) +
severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries before
escalating to the orchestrator. If a criterion from `plan-035`'s original five genuinely does not
apply to a category (rather than just needing rewording), say so explicitly and propose what
replaces it — do not silently drop it without a substitute and without flagging the deviation from
`plan-035`'s original text.

## Execution notes

(To be filled in by the implementing agent during work, if useful — not required.)

## Completion addendum (2026-09-10)

All acceptance criteria met, but not on the first delivered draft without correction — see below.
Full record in `docs/artifacts/maturity-promotion-criteria-v1.md` and `completed-tasks.md`'s T431
row. **One real factual error was found during the orchestrator's independent pre-merge review and
corrected before merging:** the first version claimed "zero existing tests reference any of the 26
skill ids by name," load-bearing for the `skill` category's design — false, per direct evidence
(`tests/functional/test_check_version_consistency.py:341` genuinely references `implementation/
knowledge/skills/release-workflow/SKILL.md`). Corrected by the same implementing agent (continued
on the same branch) to the real count (1/26, not 0/26), with the `instruction` comparison
cross-checked for consistency (4/4). The underlying design conclusion was unaffected — only its
stated grounding was. Implemented on MR !257 (`agent/tech-lead/T431` → `develop`, feat commit
`cfd89c1`, correction commit `f583230`, squashed commit `62a13f7`, merge commit `8cf217c`); this
brief itself was dispatched via MR !256 (merge commit `9886a39`).
