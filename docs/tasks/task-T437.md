# Task T437 — Regenerate registry summary + add maturity-distribution table to the release checkpoint template

**ID:** T437
**Owner:** Release Manager (matches `plan-035`/`plan-041`'s own assignment: "last in sequence since
it reports on the finished state of T430-T436." **Deliberately spelled with its human display name,
not its lowercase-hyphenated registry id, throughout this brief, including in file-path and
branch-name references (using a `<your-slug>` placeholder instead)** — this component is itself
one of Wave 2's `stable` promotions (confirmed directly: `implementation/knowledge/agents/
<your-slug>.md`'s own frontmatter already shows `maturity: stable`, where `<your-slug>` is this
role's own real registry id, which you already know); the literal id would trip the same whole-word
self-referential ledger-defect regression T434/T435/T436's briefs each found and fixed in their own
way — this is the fourth occurrence this phase, now checked proactively at brief-authoring time
rather than discovered via a failing test run, and the first occurrence where even a *file path*
(not just prose) triggered it, confirmed directly by the orchestrator (`python3 tests/run.py`
genuinely failed with the literal path/branch-name text present, before this rewrite). **Tool
grant checked before dispatch: the agent definition's registered grant is `[read, search, edit,
execute, web, mcp__gitlab]` — has both `edit` and `execute`, no reassignment needed, no gap this
time** (first Phase 3 task besides T431/T432 with a fully write-capable owner from the start).
**Status:** done
**Priority:** P2 (small, closes Phase 3 — does not block anything else in this repo currently)
**Depends on:** T436 (done — `docs/artifacts/phase3-maturity-demotion-decision-v1.md`, confirming
no components changed as a result of the demotion pass, so the current registry state is final for
Phase 3's purposes)
**Blocks:** none (Phase 3's own closure, not a blocker for other work)
**Created:** 2026-09-11
**Completed:** 2026-09-11
**Based on:** `docs/plans/plan-041-phase3-maturity-ladder-detailed-planning.md` (approved, merged
MR !252) — specifically its T437 row; `docs/plans/plan-035-roadmap-v7-ground-up.md` §2.4 Phase 3
(T437's original nominal scope: "Regenerate `implementation/registry/summary.md`; add a maturity
distribution table to the release checkpoint template"); `implementation/registry/summary.md` (the
file to regenerate); `docs/checkpoints/_template.md` (the one and only checkpoint template this
repo currently has — see the "Genuine ambiguity" note below); `implementation/knowledge/commands/
prepare-release.md` (the command that actually produces `docs/checkpoints/checkpoint-release-
v<version>.md` files — read its "Version Management" section directly, it currently has no maturity-
distribution step).

## A genuine, disclosed ambiguity — resolve and state your choice, do not silently pick

Neither `plan-035` nor `plan-041` names a file literally called "release-checkpoint template" — no
such file exists in this repo. Two real candidates, not mutually exclusive:

1. **`docs/checkpoints/_template.md`** — the one generic checkpoint template every checkpoint in
   this repo is based on (release checkpoints included, per `prepare-release.md`'s own step 6:
   "Create a release checkpoint: `docs/checkpoints/checkpoint-release-v<version>.md`" — no separate
   release-specific template file exists to create it from).
2. **`implementation/knowledge/commands/prepare-release.md`** itself — the command whose "Version
   Management" section is what actually instructs whoever runs `/prepare-release` to create that
   checkpoint file; adding a maturity-distribution step there would ensure every future release
   checkpoint actually includes the table, not just that the generic template has a slot for it.

**Do both, or pick one with disclosed reasoning — your call, document it in your completion
report.** A reasonable approach: add a `## Maturity Distribution` section to `_template.md` (so
every future checkpoint, not just release ones, has the slot available) AND add a step to
`prepare-release.md`'s "Version Management" section referencing it (so release checkpoints
specifically are instructed to fill it in) — but if you judge one alone is sufficient, say so and
why, rather than silently picking without disclosing the choice.

## Objective

1. Regenerate `implementation/registry/summary.md` via the real generator
   (`implementation/scripts/generate-registry.py`) so it reflects the current, real state (already
   correct as of `develop`'s current tip, but re-run it for real rather than assuming — confirm no
   drift, per acceptance criterion 3).
2. Add a maturity-distribution table (or equivalent section) to the checkpoint template(s), per the
   disclosed resolution above — a template section, not a one-time snapshot of today's specific
   numbers (the template must remain reusable for every future release, whatever the distribution
   looks like then).

## Genuine collision-avoidance reminder, given this phase's own pattern

Four Phase 3 tasks in a row have now hit variants of the same self-referential/incidental-mention
regression against `check-maturity.py`'s ledger-defect check (T433: self-naming; T434/T435:
incidental mention of an unrelated already-`stable` component; T436: the task's own Owner field).
**If you need to give any real, concrete example in your own prose (in this task's own body, or in
any file you edit) — e.g. illustrating what a filled-in maturity-distribution table might look
like — do not use any of the 31 currently-`stable` component's real ids as your example.** Use a
generic placeholder (`<component-id>`) or a clearly-fictional example name instead. This applies to
`_template.md`/`prepare-release.md` specifically: those files are not scanned by the ledger-defect
check while you're working (they're not `docs/tasks/task-<ID>.md` files), so editing them is safe
regardless — this reminder is about your own task's *closure report/artifact*, if you produce one
that becomes part of an open ledger row before this task closes.

## Expected outputs

1. `implementation/registry/summary.md` — regenerated, confirmed matching real current state.
2. `docs/checkpoints/_template.md` and/or `implementation/knowledge/commands/prepare-release.md` —
   updated per your disclosed resolution of the ambiguity above.

## Acceptance criteria

1. `implementation/registry/summary.md` reflects the real, current maturity distribution (31
   `stable` / 46 `experimental` / 0 `deprecated` as of this task's dispatch — confirm this exact
   split independently before reporting, don't assume it's unchanged from the brief's own numbers).
2. A maturity-distribution table/section exists in the checkpoint template(s) you chose to edit,
   structured as a reusable template (category × maturity-level counts), not a hardcoded snapshot
   of today's specific numbers.
3. `python3 implementation/scripts/generate-registry.py --root implementation --check` reports "up
   to date" after your regeneration.
4. `python3 tests/run.py` passes with no regressions.
5. `node implementation/scripts/sync.mjs --root implementation --check` reports no drift (only
   relevant if you touch anything under `implementation/knowledge/**` — `prepare-release.md` is
   under that tree, so this applies if you edit it).
6. Your ambiguity resolution (which template file(s) you edited and why) is stated explicitly in
   your completion report.
7. Coding standards and Conventional Commits followed; branch pushed, MR opened against `develop`,
   not self-merged.

## Constraints

- **No paid or recurring-cost API calls.**
- **Do not touch `.mcp.json`, anywhere. Do not touch the main checkout
  (`/home/emage/Code/emage/emage.code`).**
- **Do not touch `tests/golden/**`, `scripts/scorecard.py`, `docs/benchmarks/tb-subset.json`/`.md`,
  `feature/T475-codex-platform-integration`.**
- **Confirm your own tool grant before starting** — re-check `implementation/knowledge/agents/
  <your-slug>.md` directly (your own real registry id, per the note above).
- **Work in your own worktree/branch** (`agent/<your-slug>/T437`, using your own real registry id
  for `<your-slug>`, per this repo's branch-naming convention), created from `develop`.
  Commit as you go; run the full test suite before reporting completion. **Do not self-merge.**

## Blocker protocol

Report blockers as: type/severity/mitigation. If the "which template file" ambiguity above turns
out to have a real technical blocker you didn't anticipate (e.g. a CI check that validates
`_template.md`'s exact structure and would break with an added section), report it rather than
forcing the edit through.

## Execution notes

(To be filled in by the implementing agent during work, if useful — not required.)

## Completion addendum (2026-09-11)

Both candidate template files edited (resolving the disclosed ambiguity): `docs/checkpoints/
_template.md` (new reusable `## Maturity distribution` table) and `implementation/knowledge/
commands/prepare-release.md` (instructs populating it from the regenerated registry). Real,
independently-confirmed current distribution: 31 `stable` / 46 `experimental` / 0 `deprecated`.
This closes Phase 3 (T430-T437) in full. Implemented on MR !276 (`agent/release-manager/T437` →
`develop`, merge commit `8ebf472`); this brief itself was dispatched via MR !275.
