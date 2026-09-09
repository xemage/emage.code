# Task T430 — Maturity levels in implementation/registry/schema.json

**ID:** T430
**Owner:** backend-developer (**reassigned from `plan-041`/`plan-035`'s nominal
`solution-architect`** — `implementation/knowledge/agents/solution-architect.md`'s real tool
grant is `[read, search, edit, web, todo, mcp__sequential-thinking, mcp__fetch]`, no `execute`;
this task requires running `implementation/scripts/generate-registry.py` and the test suite to
verify ~84 file edits, which needs Bash. Matches this repo's own established disposition
(T415/T418/T421/T455 precedent: reassign the owner, leave the nominal agent's tool grant
unchanged, do not widen it) — checked before dispatch, not discovered mid-task.)
**Status:** pending
**Priority:** P1 (first task in Phase 3's approved sequence; T431-T437 depend on it directly or
transitively)
**Depends on:** Phase 3 start condition (Gate G1 + Phase 2, both closed — see `plan-041`'s
"Re-confirmed state")
**Blocks:** T431
**Created:** 2026-09-09
**Completed:** —
**Based on:** `docs/plans/plan-041-phase3-maturity-ladder-detailed-planning.md` (approved, merged
MR !252) — specifically its Finding 2 and the T430 row of its per-task summary table;
`docs/plans/plan-035-roadmap-v7-ground-up.md` §2.4 Phase 3 (T430's original nominal scope);
`implementation/registry/schema.json` (the enum this task edits); `implementation/scripts/
generate-registry.py` (the generator whose `_maturity()` function this task's finding concerns).

## Corrected premise — read this before starting, do not re-derive from plan-041 alone

`plan-041`'s Finding 2 correctly identified that `implementation/registry/schema.json` already
has a `maturity` enum (`["draft", "beta", "ga", "deprecated"]`) distinct from `plan-035`'s proposed
`experimental → beta → stable → deprecated`, and that `implementation/registry/summary.md` shows
all 77 components at `beta`. **What `plan-041` did not check, and this task's pre-dispatch
verification found: none of that is real per-component classification data.** Grepped every file
under `implementation/knowledge/` (84 markdown files) for an explicit `^maturity:` or
`^stability:` frontmatter field — **zero matches, in any file.** Read `generate-registry.py`
directly: its `_maturity()` function is `frontmatter.get("maturity") or frontmatter.get
("stability") or "beta"` — a hardcoded fallback, not a read of real declared data. Grepped
`implementation/scripts/check.py` for `maturity` — zero matches, so nothing currently validates or
enforces the field either. **The uniform "beta" in `summary.md`/`index.json` is the generator's
default value applied because the field is absent everywhere, not because every component was
actually classified `beta`.**

This changes T430's real scope from a pure rename (swap `ga`→`stable`, `draft`→`experimental`
across already-tagged files) to a genuine first-population task: there is nothing to rename in any
component file, only the unused schema enum and the generator's fallback default. This task must
therefore make three decisions and document them (in `docs/artifacts/maturity-levels-v1.md` or
equivalent — your choice of filename, state it), not silently assume any of them:

1. **Final enum values.** `plan-035` proposed `experimental/beta/stable/deprecated`; the existing
   unused schema enum is `draft/beta/ga/deprecated`. Per `plan-041`'s own delegation ("the exact
   target names are `solution-architect`'s call at dispatch, not pre-decided here" — this
   delegation carries to whichever agent is actually dispatched, unchanged in substance by the
   owner reassignment above), pick and justify one set (or a reconciled third set) in the design
   artifact. Do not pick silently in a commit message only.
2. **Whether the field becomes mandatory going forward**, i.e. whether `generate-registry.py`'s
   silent `or "beta"` fallback should be removed once every component has a real explicit value
   (recommended, since T432's next task is to "mechanically verify a claimed level" — a fallback
   default undermines that if a component can still validly have no explicit claim at all — but
   this is your call to make and document, not this brief's to pre-decide).
3. **What the honest baseline value is for a component with no golden case, no declared rails, and
   no promotion work yet done** — i.e. what every one of the 84 files should be explicitly set to
   as their starting value before Phase 3's Wave 1-3 (T433-T435) promote any of them. This is not
   "beta" by `plan-035`'s own framing ("end the state where 76 of 76 components are beta" — a
   uniform `beta` is exactly the problem Phase 3 exists to fix, so re-asserting it explicitly for
   all 84 would misrepresent the untouched baseline as more mature than it is). The lowest level in
   whichever enum you pick (decision 1) is the expected honest default; state your reasoning if you
   choose otherwise.

## Objective

Reconcile `plan-035`'s proposed maturity-level naming with the schema/generator state actually
found in the repo (see "Corrected premise" above), then populate all 84 `implementation/
knowledge/**/*.md` files with an explicit, honest baseline maturity value in frontmatter — not
leave them on the generator's silent default. Update `implementation/registry/schema.json`'s enum
to the final chosen values. Regenerate the registry (`implementation/scripts/generate-registry.py`)
and confirm `summary.md`/`index.json` reflect the real explicit values, not the old fallback.

## Inputs

- `implementation/registry/schema.json`
- `implementation/scripts/generate-registry.py`
- `implementation/knowledge/{agents,commands,instructions,skills}/*.md` (84 files)
- `docs/plans/plan-041-phase3-maturity-ladder-detailed-planning.md`

## Expected outputs

1. `implementation/registry/schema.json` — `maturity` enum updated to the chosen final values.
2. All 84 `implementation/knowledge/**/*.md` files — explicit `maturity:` (or `stability:`, your
   naming call, but be consistent — do not leave both field names in use) frontmatter field added,
   set to the honest baseline value (decision 3 above), unless a specific file's real current state
   genuinely warrants a higher one — if you find one, name it and justify it explicitly rather than
   uniformly stamping every file without looking.
3. `implementation/scripts/generate-registry.py` — updated if decision 2 above removes or changes
   the fallback behavior.
4. `implementation/registry/summary.md` + `implementation/registry/index.json` — regenerated via
   the actual script (not hand-edited) and committed.
5. `docs/artifacts/maturity-levels-v1.md` (or your chosen filename, state it) — documents the three
   decisions above with reasoning, for `T431` (promotion criteria) and future Phase 3 tasks to cite.

## Acceptance criteria

1. `implementation/registry/schema.json`'s `maturity` enum reflects a deliberate, documented
   decision — not left as the stale `draft/beta/ga/deprecated` values untouched, and not silently
   swapped without the design artifact explaining why.
2. Every one of the 84 `implementation/knowledge/**/*.md` files has an explicit maturity field
   matching the final enum — re-running `generate-registry.py` and grepping the regenerated
   `summary.md`/`index.json` shows real values, not a uniform artifact of the old fallback.
3. The honest-baseline decision (item 3 above) is stated and justified in the design artifact —
   if the chosen baseline is anything other than the enum's lowest level, that deviation is
   explained, not implicit.
4. `python3 tests/run.py` passes with no regressions.
5. `node implementation/scripts/sync.mjs --check` (or the project's current equivalent) reports no
   drift introduced by this task's edits, if the frontmatter change interacts with platform
   projection — verify this rather than assume maturity is projection-inert.
6. Coding standards and Conventional Commits followed; branch pushed, MR opened against `develop`,
   not self-merged.

## Constraints

- **No paid or recurring-cost API calls.** This task is pure repo-local editing and scripting.
- **Do not touch `.mcp.json`, anywhere, for any reason. Do not touch the main checkout.**
- **Do not touch `tests/golden/**`, `scripts/scorecard.py`, `docs/benchmarks/tb-subset.json`/`.md`**
  — this task is unrelated to the golden suite; if you find any interaction, treat it as a
  `type: unclear_requirements` blocker, do not edit those paths to resolve it.
- **Do not touch `feature/T475-codex-platform-integration`. Do not start T431 or any later Phase 3
  task.**
- **Confirm your own tool grant before starting** — `implementation/knowledge/agents/
  backend-developer.md`'s registered grant is `[read, search, edit, execute, web, mcp__fetch]`;
  verify this is still accurate before beginning and report immediately as a `type: technical`
  blocker if it has changed or proves insufficient.
- **Work in your own worktree/branch** (`agent/backend-developer/T430`), created from `develop`.
  Commit as you go; run the full test suite before reporting completion. **Do not self-merge** —
  push and open a merge request, then stop.

## Blocker protocol

Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`) +
severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries before
escalating to the orchestrator. If any of the three delegated decisions (enum names, mandatory-
field policy, honest baseline) turns out to have a materially better answer than what you initially
pick, document the reconsideration in the design artifact rather than silently picking one without
recording the alternative you rejected and why.

## Execution notes

(To be filled in by the implementing agent during work, if useful — not required.)
