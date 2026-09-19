# Artifact: maturity-levels-v1.md

> Filename: `maturity-levels-v1.md`. Immutable once produced; revisions bump `<N>`.

## Metadata
- **Producer agent**: backend-developer
- **Task**: T430
- **Created**: 2026-09-09
- **Based on**: `docs/tasks/task-T430.md`; `docs/plans/plan-041-phase3-maturity-ladder-detailed-planning.md`
  (Finding 2, T430 row); `docs/plans/plan-035-roadmap-v7-ground-up.md` §2.4 Phase 3 (T430, T431,
  T432, T436, T440 rows); `implementation/registry/schema.json` (pre-edit state);
  `implementation/scripts/generate-registry.py` (pre-edit state).
- **Supersedes**: none (first version)

## Body

### Decision 1 — Final enum values: `experimental / beta / stable / deprecated`

`plan-035` (the original, already-approved roadmap) proposed `experimental → beta → stable →
deprecated`. The schema currently carries a different, unused enum: `draft / beta / ga /
deprecated`. This task had to pick one set, or a reconciled third.

**Chosen: `experimental`, `beta`, `stable`, `deprecated`** — `plan-035`'s original naming, not the
schema's stale enum.

Reasoning:
1. **Downstream task text already depends on this exact vocabulary, verbatim, in already-approved
   documents.** `plan-035`'s own rows for T431 ("Proposed for `stable`: (a) ≥1 golden case...");
   T432 ("A component may not *declare* `stable`; it must *satisfy* it" and "`scripts/check-
   maturity.py` fails on a component claiming `stable` without a golden case"); T436 ("anything
   that cannot reach `stable` in three waves is marked `experimental` or `deprecated`. An accurate
   `experimental` label is worth more than an aspirational `beta` one."); and T440 ("`mechanical`
   requires stable component...") all use `stable`/`experimental` as load-bearing words in their
   acceptance-criteria language, not just as color commentary. T431 is T430's direct blocked
   successor. Keeping the schema's stale `draft/ga` words would force every one of those already-
   written task descriptions to be silently re-translated by whichever agent implements them next
   — a translation burden and a consistency risk this task can eliminate now, for free, since
   nothing in the repo has ever actually used the `draft/ga` enum (see Decision 2 and the "Corrected
   premise" section of `task-T430.md`).
2. **Readability for this specific artifact class.** These are agent/command/instruction/skill
   *definitions* — internal developer-tooling config, not a customer-facing SaaS product. `ga`
   ("general availability") is enterprise/product-release jargon that reads oddly applied to, say,
   a skill file. `stable` communicates the same idea in plainer language. Likewise `draft` reads as
   "in-progress edit," which collides with normal git/PR workflow language, whereas `experimental`
   unambiguously means "usable but unproven," which is the actual intended semantics per `plan-035`.
3. **No compatibility cost.** Zero of the 84 files under `implementation/knowledge/` had any
   `maturity`/`stability` value before this task (verified: `grep -rlE '^(maturity|stability):'` →
   no matches). The old `draft/beta/ga/deprecated` enum in `schema.json` was declared but never
   read by any real data — nothing to migrate, no existing classified value to preserve.

Alternative considered and rejected: keep `draft/beta/ga/deprecated` (the schema's pre-existing,
unused enum) and rewrite `plan-035`'s T431/T432/T436/T440 wording to match at whatever future point
those tasks are dispatched. Rejected because it defers, rather than avoids, the translation cost,
and because the schema's enum has zero real usage today to protect by leaving it untouched.

### Decision 2 — The field is mandatory; the generator's silent fallback is removed

`implementation/scripts/generate-registry.py`'s `_maturity()` previously computed
`frontmatter.get("maturity") or frontmatter.get("stability") or "beta"` — any component with no
explicit value silently became `"beta"`, indistinguishable in the generated registry from a
component that was genuinely, deliberately classified `beta`.

**Chosen: make `maturity` a required frontmatter field.** `_maturity()` now raises `ValueError`
(file path + expected values included in the message) if the field is missing, empty, or not one
of the four canonical values — the registry generator now hard-fails instead of guessing.

Reasoning: T432's stated purpose (`plan-035`) is "mechanically verify a claimed level... A
component may not *declare* `stable`; it must *satisfy* it" — that check only means something if
"no claim" and "claim of `experimental`" are different, verifiable states. A silent default
collapses that distinction: an unclassified component and a specifically-triaged-and-marked-
`beta` component would be identical in the registry, and T432's future enforcement script would
have no way to tell "never reviewed" apart from "reviewed and still low-tier." Making the field
mandatory closes that gap once (this task), rather than leaving it open for T432 to rediscover.
Every one of the 77 registry-eligible files (see the scope note below) now carries an explicit
value, so the "mandatory" requirement costs nothing today and only bites a future new file that
forgets to set it — which is the intended, desired failure mode (loud, at generation time, not
silent forever).

The per-category JSON Schemas under `implementation/knowledge/schemas/{agent,command,skill,
instruction}.schema.json` were updated to add `maturity` as a `required` property with the same
four-value `enum`, and `tests/functional/test_schemas.py`'s hardcoded instruction allow/required
sets were updated to match — both are direct, necessary consequences of "mandatory," not a
separate scope decision (see "Unplanned but necessary companion fixes" below for why these needed
touching at all).

### Decision 3 — Honest baseline: `experimental`, uniformly, no exceptions found

Every one of the 77 registry-eligible components is set to `experimental` — the new enum's lowest
level — as its explicit baseline value.

Reasoning: `plan-035` frames Phase 3's very reason for existing as ending "the state where 76 of 76
components are beta" — i.e., a uniform `beta` stamp today would be re-asserting the exact
mis-classification Phase 3 exists to correct, just spelled with an explicit field instead of an
implicit fallback. The task brief's own promotion bar (`plan-035`'s proposed `stable` criteria:
"(a) ≥1 golden case exercising it, (b) explicit rails ..., (c) referenced by ≥1 command or agent,
(d) documented in the end-user tree, (e) no open P0/P1 defect") is not yet formally defined — that
is literally `T431`'s job, not this task's — so nothing can be certified above the floor today
without inventing an un-approved promotion bar. I checked `tests/golden/` (read-only, per this
task's constraint not to modify it) for any existing per-component evidence that might justify an
exception; it contains Terminal-Bench-style `held-out`/`open` suites, not a per-component mapping
to any of the 77 agent/command/instruction/skill files, so there is no existing golden-case
evidence to point to for any specific file today. **No file was found that warrants a
higher-than-baseline value; the baseline is applied uniformly to all 77.**

### Scope clarification — 77 registry-eligible files vs. the brief's "84 files" framing

The task brief (`task-T430.md`) and `plan-041` both say "84 files" / "grepped every file under
`implementation/knowledge/` (84 markdown files)." That count is accurate for *files on disk* under
`implementation/knowledge/**/*.md`, but it is not the same as the set of files
`generate-registry.py` actually turns into registry **entries**. Of the 84:

- **77 are real registry components**: 28 `agents/*.md`, 19 `commands/*.md`, 4 `instructions/*.md`,
  26 `skills/*/SKILL.md`. `generate-registry.py`'s `_collect_entries()` only ever reads these four
  patterns — this is also why `summary.md` pre-existed showing "77 components," matching `plan-041`
  Finding 2's own count, not 84.
- **7 are non-component supporting documentation, never read by the generator**: two top-level
  `README.md` files (`implementation/knowledge/README.md`,
  `implementation/knowledge/memory/README.md`) describing the knowledge folder itself, and five
  `skills/*/references/*.md` template/reference docs used *by* a skill (e.g.
  `skills/project-planning/references/milestone-roadmap.md`) but not themselves a skill. None of
  the 7 currently have any YAML frontmatter block at all.

**Resolution: `maturity` was added only to the 77 real registry components, not the 7 supporting
docs.** Adding a `maturity:` frontmatter field to a plain README or a fill-in-the-blank template
doc would (a) not affect the registry at all, since the generator never reads those paths, and (b)
not be semantically meaningful — a maturity *lifecycle* classification doesn't apply to a
reference template the way it applies to a versioned, invokable component. This is flagged here per
`task-T430.md`'s blocker-protocol instruction to "document the reconsideration... rather than
silently picking one" — this is not one of the three headline decisions, but it is a real deviation
from the brief's literal "84 files" wording that a reviewer should be able to see and check.

### Unplanned but necessary companion fixes discovered during implementation

1. **`generate-registry.py`'s `FRONTMATTER_RE` regex was broken and silently matched nothing, for
   every file, before this task.** The pattern was written as
   `r"^---\\s*\\n(.*?\\n)---\\s*\\n"` — inside a raw string, `\\s`/`\\n` are two literal backslash
   characters followed by a letter, not an escaped whitespace/newline class. `_parse_frontmatter()`
   therefore always returned `{}` for every file, regardless of real content, which is why the
   generator's "beta" fallback fired for 100% of components even before this task's frontmatter
   additions — not only because no file *declared* a value, but because the parser could never have
   read one even if a file had one. This is a genuine pre-existing bug, not introduced by this task,
   but it directly blocked this task's core acceptance criterion (real declared values reaching the
   regenerated registry) and had to be fixed to make `maturity` (or anything else in frontmatter)
   readable at all. Fixed to `r"^---\s*\n(.*?\n)---\s*\n"`. Side effect (verified, not incidental
   noise): registry entries' `name` field for the 28 agents now correctly shows the human-readable
   frontmatter `name:` value (e.g. `"Backend Developer"`) instead of the path-stem slug
   (`"backend-developer"`) it silently fell back to before. `id` values are unaffected (no file sets
   an explicit `id:` frontmatter key, checked directly). Commands/instructions have no `name:`
   field, so they are unaffected. Skills' `name:` values were already checked to equal their
   directory slug in every case, so skill entries are also unaffected in practice.
2. **`tests/functional/test_schemas.py` and the four `implementation/knowledge/schemas/*.schema.json`
   files hard-code the exact allowed frontmatter key set per category with `additionalProperties:
   false`.** Adding the new mandatory `maturity` key without updating these would fail every
   agent/skill/command/instruction frontmatter test (confirmed: this is exactly what happened on
   first `python3 tests/run.py` run after the frontmatter edits — 4 failures + 73 errors, all in
   `tests.functional.test_schemas`). Updated all four schemas to add `maturity` as a required
   enum-constrained property, and updated the instruction test's hardcoded
   `INSTRUCTION_REQUIRED`/`INSTRUCTION_ALLOWED` sets to match (the `instruction.schema.json` file
   itself is not currently loaded by any code path — confirmed via repo-wide grep — but was updated
   anyway for consistency with the other three, in case that changes later).

## Consumed by

- **T431** (promotion criteria per category) — cites the final enum names (`experimental / beta /
  stable / deprecated`) and the mandatory-field policy from this artifact; must define what
  specifically moves a component from `experimental` to `beta`/`stable`.
- **T432** (`scripts/check-maturity.py`, CI-enforced verification) — relies on the mandatory-field
  decision (Decision 2): a component with no explicit `maturity` is now a hard generation error, not
  a silently-defaulted `beta`, which is the precondition T432's "declare vs. satisfy" enforcement
  needs.
- **T436** (honest demotion pass) — will operate against the `experimental` baseline this task set
  for all 77 components; T436's later comparison ("cannot reach `stable` in three waves") is only
  meaningful because this task did not pre-emptively over-classify anything.
