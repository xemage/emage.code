# Artifact: maturity-promotion-criteria-v1.md

> Filename: `maturity-promotion-criteria-v1.md`. Immutable once produced; revisions bump `<N>`.

## Metadata
- **Producer agent**: tech-lead
- **Task**: T431
- **Created**: 2026-09-10
- **Based on**: `docs/tasks/task-T431.md`; `docs/plans/plan-041-phase3-maturity-ladder-detailed-planning.md`
  (T431 row); `docs/plans/plan-035-roadmap-v7-ground-up.md` §2.4 Phase 3 (T431's original nominal
  scope, its proposed five `stable` criteria); `docs/artifacts/maturity-levels-v1.md` (T430 — final
  enum names, mandatory-field policy — cited below, not re-derived).
- **Supersedes**: none (first version)

## Body

### 0. Basis (cited from T430, not re-derived)

Per `docs/artifacts/maturity-levels-v1.md`:
- Enum: `experimental` → `beta` → `stable` → `deprecated` (Decision 1).
- `maturity` is a **mandatory** frontmatter field on all 77 registry-eligible components (28
  `agent`, 19 `command`, 4 `instruction`, 26 `skill`); `generate-registry.py` hard-fails on a
  missing/invalid value (Decision 2).
- All 77 currently carry the explicit baseline value `experimental` (Decision 3) — none have been
  promoted yet, so every criterion below is a target state, not a current one, except where noted.

This task defines what mechanically moves a component between those four states, per category.

### 1. `plan-035`'s five proposed `stable` criteria — per-category applicability

`plan-035` §2.4 Phase 3, T431 row proposes, for `stable`: **(a)** ≥1 golden case exercising it,
**(b)** explicit rails (declared inputs / out-of-scope / failure mode), **(c)** referenced by ≥1
command or agent, **(d)** documented in the end-user tree, **(e)** no open P0/P1 defect.

Grounding check performed before adapting these (not assumed): read `tests/golden/README.md` and
every `case.yaml` under `tests/golden/{open,held-out}/**` (read-only, per this task's constraint).
Finding: the golden suite is **command-scoped by design** — its own README states it "checks
whether emage.code's five commands... produce output that respects their own declared contract...
It is not a live-capability benchmark." Every `case.yaml` has exactly one identifying field beyond
`id`/`status`/`tags`: `command: /<one-of-five-commands>` (`/code-review`, `/new-feature`, `/plan`,
`/security-audit`, `/prepare-release`). **No `case.yaml` field references an agent id, instruction
id, or skill id, structurally, today.** This changes the applicability analysis materially beyond
what the task brief's Objective section already flagged.

| # | Criterion (verbatim intent) | `agent` | `command` | `instruction` | `skill` |
|---|---|---|---|---|---|
| a | ≥1 golden case exercising it | **Partial substitute needed** — only the 4 agents that own a command (`agent:` frontmatter on a command file) inherit a golden case transitively; the other 24 have no structural path. Substitute below. | **Applies as-is**, but only 5/19 commands are structurally reachable today (the other 14 need golden cases written before they can ever satisfy this — expected, not a gap in the criterion itself). | **Does not transfer** — no `case.yaml` field can name an instruction; it is a passive, cross-cutting file, not something a case is "for." Full substitute below. | **Does not transfer** — no `case.yaml` field can name a skill either, and grep confirms only **1 of 26** existing skill ids (`release-workflow`) is referenced by name in real test code today. Full substitute below. |
| b | Explicit rails (inputs / out-of-scope / failure mode) | Applies as-is | Applies as-is | Applies as-is | Applies as-is |
| c | Referenced by ≥1 command or agent | Applies as-is (already grounded: `@<agent-id>` mentions, `agent:` frontmatter) | **Does not transfer as worded** — a command is *invoked* (by a user or another command), not typically "referenced by" an agent the way a skill/agent is. Direction-flipped substitute below. | Applies with grounding (see below) | Applies as-is (already grounded: AGENTS.md's mandatory-skill table, explicit "skill `<id>`" mentions) |
| d | Documented in the end-user tree | Applies as-is | Applies as-is | Applies as-is | Applies as-is |
| e | No open P0/P1 defect | Applies as-is | Applies as-is | Applies as-is | Applies as-is |

**Summary of what needed rewording or a substitute, and why:**
- **(a)** needs a real substitute for `agent` (24/28 have no structural path via `case.yaml`),
  `instruction` (0/4 tagged via the formal `# maturity-evidence:` convention — flagged in the
  brief), and `skill` (0/26 tagged via that same formal convention — found during this task, not
  flagged in the brief). Re-verified directly by grep (real test code only —
  `tests/functional/**`, `tests/unit/**`, `tests/performance/**`, `tests/eval/**`,
  `tests/_helpers/**`; `tests/golden/**` and `tests/fixtures/**` excluded as simulated content, not
  real assertions): `instruction` filenames are already referenced by path in real functional
  tests for **all 4/4** instructions (`test_platform_projections.py`,
  `test_install_agents_mapping.py`, `test_check_version_consistency.py`), whereas skill ids are
  referenced by path in real test code for only **1/26** (`release-workflow`, in
  `tests/functional/test_check_version_consistency.py:341`,
  `test_real_repo_excludes_illustrative_knowledge_examples`). (A second apparent hit,
  `code-review`, in `test_golden_held_out_isolation.py`, is a false positive — it names golden
  *command*-surface `/code-review` case IDs (deliberately not quoted here, as some are held-out
  cases and this artifact sits outside `tests/golden/held-out/`, which must not name held-out case
  IDs, per `test_golden_held_out_isolation.py`'s own Check B), not the `code-review` skill, and does
  not count.) So `skill` is not at "zero" real-world coverage, but its embryonic coverage (1/26,
  ~4%) remains substantially narrower than `instruction`'s (4/4, 100%) — the "harder starting point
  than `instruction`'s equivalent gap" characterization below still holds, just not because skill
  coverage is literally zero. For `command` and the 4 command-owning agents, the literal criterion
  is kept as-is because the mechanism genuinely exists and is checkable today.
- **(c)** needs a direction-flipped substitute for `command` only, exactly as the brief's Objective
  anticipated — commands don't get "referenced by" an agent, they *declare* their owning agent.
- **(b)**, **(d)**, **(e)** transfer cleanly to all four categories as worded (rephrased below only
  to make each one script-checkable, per Acceptance Criterion 2 — not because the underlying logic
  needed to change).

### 2. New conventions this artifact introduces (needed to make (a)/(c) checkable)

Two lightweight, additive conventions are introduced so `T432`'s `scripts/check-maturity.py` has
something real to grep for. Neither requires a `schema.json`/`*.schema.json` edit — both are plain
Markdown body content, so they are additive to existing frontmatter (`additionalProperties: false`
on frontmatter is unaffected).

1. **`## Rails` section** (criterion b, all categories). A component's Markdown body must contain a
   heading `## Rails` (or `### Rails` if nested) with three labeled, non-empty sub-items:
   - `**Inputs**:` — what this component consumes (arguments, files, upstream artifacts).
   - `**Out of scope**:` — what it explicitly does not do.
   - `**Failure mode**:` — what happens, and what is reported, when it cannot complete.
   Mechanically checkable: heading present, each of the three bold labels present under it, each
   followed by at least one non-whitespace character of prose on the same or next line.

2. **`# maturity-evidence: <category>/<id>` tag** (criterion a substitute, for `agent`,
   `instruction`, `skill`). A plain Python comment line, placed in a test file that a human has
   judged to genuinely exercise or enforce the named component — either a functional test
   (`tests/functional/**/*.py`) or a golden case's `expect.py`
   (`tests/golden/{open,held-out}/*/expect.py`, read-only path — adding a comment line to an
   *existing* case's `expect.py` during a future promotion wave is still an edit to a protected
   path per this suite's README and requires the same review care as any other change there; this
   artifact does not authorize bypassing that). Mechanically checkable: `grep -rn
   "# maturity-evidence: <category>/<id>"` across the two allowed directories returns ≥1 hit. The
   human judgment ("does this test really exercise the component") is made once, at tag-authoring
   time — identical in kind to how a human already decides what a golden case tests today; the
   script only verifies the tag's presence, not its truth.

3. **`## Deprecation Notice` section** (new, for the `deprecated` transition — see §4).

### 3. Per-category, per-transition criteria

All four categories share a common shape: `experimental` is today's uniform floor (already true —
no action needed to be at this level). Promotion is a **one-way, all-conditions-met** gate: a
component satisfies a tier only when every criterion for that tier (and every criterion for every
tier below it) holds simultaneously — a `stable` component must still satisfy `beta`'s bar, not
just `stable`'s incremental additions. `deprecated` is a separate, orthogonal state (§4), not a
"tier below `experimental`."

`plan-035` gives no explicit `experimental→beta` bar (only a `stable` bar) — filling that gap is
part of Acceptance Criterion 1's "at least the `experimental→beta` and `beta→stable` transitions"
requirement, not optional. The design choice made here: `beta` is a **self-contained, well-formed**
bar (the component honestly describes itself and hasn't broken anything), while `stable` is an
**externally-validated** bar (something outside the file itself attests to it). This also gives
`P0`/`P1` defect-freedom real teeth at two different strengths instead of only gating at `stable`.

#### 3.1 `agent`

**`experimental → beta`** — ALL of:
1. `maturity: beta` set; the file still passes `implementation/knowledge/schemas/agent.schema.json`
   and `tests/functional/test_schemas.py` (part of `tests/run.py`) with zero errors.
2. `## Rails` present per §2.1.
3. No open `P0` defect (see §3.5 for the shared defect-check definition).

**`beta → stable`** — ALL of the above, still holding, PLUS:
4. Golden/test evidence: **at least one** of —
   (i) ≥1 golden case (`open/` or `held-out/`) whose `case.yaml` `command:` value names a command
   whose own frontmatter `agent:` equals this agent's id (transitive command ownership — currently
   possible only for `orchestrator`, `poc-orchestrator`, `security-engineer`, `tech-lead`, the 4
   agents a command currently declares); or
   (ii) a `# maturity-evidence: agent/<id>` tag per §2.2; or
   (iii) ≥1 row in `docs/tasks/completed-tasks.md` with `Owner` == this agent's id whose
   `Outcome / artifact` column resolves to a real, existing file/MR reference (a completed, shipped
   unit of reviewed work attributable to this agent — the task-ledger analog of a golden case,
   used because the golden suite does not, and per its own README is not meant to, cover most
   agents directly).
5. Cross-referenced: this agent's id appears as ≥1 command's `agent:` frontmatter value, OR as an
   explicit `@<agent-id>` mention in the body of ≥1 other `agents/*.md` or `commands/*.md` file, OR
   in `docs/wiki/agents-overview.md`'s routing table (already true for all agents there today).
6. Documented: this agent's `name`/id appears in ≥1 file under `docs/wiki/**` with ≥1 full sentence
   (≥40 non-whitespace characters in the same row/bullet/section) of real description, not an
   incidental substring match.
7. No open `P0` or `P1` defect (stricter than beta's `P0`-only bar).

#### 3.2 `command`

**`experimental → beta`** — ALL of:
1. `maturity: beta` set; passes `command.schema.json` / `test_schemas.py`.
2. `## Rails` present.
3. No open `P0` defect.

**`beta → stable`** — ALL of the above, PLUS:
4. Golden evidence: ≥1 golden case (`open/` or `held-out/`) whose `case.yaml` `command:` ==
   `/<this-command-id>`. Kept as `plan-035` originally worded it — no substitute needed, the
   mechanism already exists (5/19 commands currently qualify structurally; the remaining 14 need
   cases authored, which is expected promotion work, not a defect in the criterion).
5. **Direction-flipped substitute for "referenced by ≥1 command or agent":** this command's
   frontmatter `agent:` field is present and its value resolves to a real, existing agent id in the
   registry (i.e., the command declares who executes it, rather than being "referenced by" one — a
   command is invoked, not referenced, so the checkable relationship runs the other way).
6. Documented: this command's id appears in ≥1 file under `docs/wiki/**` with ≥1 full sentence of
   real description (today only incidental; a dedicated commands-overview doc is expected promotion
   work, same caveat as agent §3.1.6).
7. No open `P0` or `P1` defect.

#### 3.3 `instruction`

**`experimental → beta`** — ALL of:
1. `maturity: beta` set; passes `instruction.schema.json` / `test_schemas.py`.
2. `## Rails` present — for an `instruction`, "inputs" reads as "what triggers `applyTo`
   scope/situation," "out of scope" as what this instruction deliberately does not mandate, and
   "failure mode" as what happens when a rule is violated (e.g., blocks merge, flags as debt) —
   same three labels, category-appropriate prose.
3. No open `P0` defect.

**`beta → stable`** — ALL of the above, PLUS:
4. **Full substitute for "≥1 golden case exercising it"** (does not transfer — instructions are
   passive, and no `case.yaml` field can name one): a `# maturity-evidence: instruction/<id>` tag
   per §2.2 in ≥1 functional test or golden `expect.py`. Grounding: `tests/functional/
   test_platform_projections.py`, `test_install_agents_mapping.py`, and
   `test_check_version_consistency.py` already reference instruction filenames today (confirmed by
   grep), so the mechanism this criterion depends on is not hypothetical — it already exists in
   embryonic form and only needs the `maturity-evidence` tag added during the promotion wave that
   claims this criterion.
5. Referenced: this instruction's id/filename is named explicitly in the body of ≥1 `agents/*.md`
   or `commands/*.md` file, OR listed in `AGENTS.md`'s "Code Standards"/"Security" routing tables
   (already true for all 4 instructions today, per direct grep of `AGENTS.md`).
6. Documented: appears in ≥1 file under `docs/wiki/**` with ≥1 full sentence of real description.
7. No open `P0` or `P1` defect.

#### 3.4 `skill`

**`experimental → beta`** — ALL of:
1. `maturity: beta` set; passes `skill.schema.json` / `test_schemas.py`.
2. `## Rails` present — "inputs" as the situation/trigger for using the skill, "out of scope" as
   what the skill deliberately excludes, "failure mode" as what the skill instructs when its own
   procedure cannot complete.
3. No open `P0` defect.

**`beta → stable`** — ALL of the above, PLUS:
4. **Full substitute for "≥1 golden case exercising it"** (does not transfer — no `case.yaml` field
   can name a skill): a `# maturity-evidence: skill/<id>` tag per §2.2 in ≥1 functional test or
   golden `expect.py`.

   *Coverage grounding (re-verified directly by grep of real test code — `tests/functional/**`,
   `tests/unit/**`, `tests/performance/**`, `tests/eval/**`, `tests/_helpers/**`; `tests/golden/**`
   and `tests/fixtures/**` excluded as simulated content, not real assertions):* no skill currently
   has the formal `# maturity-evidence:` tag (the convention is new, introduced by this artifact),
   but coverage is not literally zero — **1 of the 26** skill ids, `release-workflow`, is already
   referenced by path in real functional-test code:
   `tests/functional/test_check_version_consistency.py:341`, inside
   `test_real_repo_excludes_illustrative_knowledge_examples`, which asserts the CLI does not flag
   `implementation/knowledge/skills/release-workflow/SKILL.md`'s illustrative semver example. That
   reference is real and deliberate, but incidental to the test's actual purpose (a
   version-consistency exclusion check, not an assertion about the skill's behavior), so it does not
   itself satisfy this criterion — the formal `# maturity-evidence: skill/release-workflow` tag
   still needs to be added deliberately at promotion time. (One apparent second hit, `code-review`
   in `tests/functional/test_golden_held_out_isolation.py`, is a false positive: it names golden
   *command*-surface `/code-review` case IDs — not quoted here, since some are held-out cases and
   this artifact must not name held-out case IDs per that same test's Check B — not the
   `code-review` skill.) The other 25/26 skill ids have no test-code references of any kind, formal
   or incidental. This
   remains a harder starting point than `instruction`'s equivalent gap — `instruction` filenames are
   already referenced by real functional tests for **4/4** instructions (§3.3.4), vs. `skill`'s
   ~4% (1/26) — but "harder starting point" is the accurate framing, not "zero coverage." Since
   every skill (`release-workflow` included) still lacks the formal tag, every skill's first
   promotion to `stable` requires a wave (T433–T435) to author at least one such tag deliberately —
   flagged here so `T432`'s script doesn't get built assuming latent, already-tagged coverage that
   isn't there.
5. Referenced: this skill's id is named explicitly in `AGENTS.md`'s mandatory-skill workflow table
   (already true for `task-management`, `systematic-debugging`, `receiving-code-review`,
   `verification-before-completion`, `validation-gates`, `checkpoint-protocol` — 6/26 today), OR in
   the body of ≥1 `agents/*.md` or `commands/*.md` file as an explicit `skill \`<id>\`` mention.
6. Documented: appears in ≥1 file under `docs/wiki/**` with ≥1 full sentence of real description
   (today: **zero** skills are documented there — grep confirms no skill id appears in
   `docs/wiki/**` at all; a dedicated skills-overview doc is expected promotion work).
7. No open `P0` or `P1` defect.

#### 3.5 Shared defect-check definition (used by all four categories' criterion `e`)

"Open `P0`/`P1` defect against component `<category>/<id>`" means **either**:
- a row in `docs/tasks/active-tasks.md` with `Priority` ∈ {`P0`, `P1`} whose `Title` or linked
  `docs/tasks/task-<ID>.md` body explicitly names `<id>`, and whose `Status` is not `done` or
  `cancelled` (i.e., it is still on the active ledger — `active-tasks.md`'s own invariant per
  `AGENTS.md` guarantees terminal rows never linger there); **or**
- (for `command`, and transitively for the 4 command-owning agents) a `tests/golden/**/case.yaml`
  with `status: known_failing` and `known_failing_category: tracked_defect` whose `command:` value
  names this command (or a command owned by this agent), unresolved.
`P2` and untracked/anecdotal concerns do not block either tier — consistent with `AGENTS.md`'s own
task-priority vocabulary (`P0` critical path, `P1`, `P2`), reused here rather than inventing a
parallel severity scale.

### 4. `deprecated` — any tier → `deprecated`

`plan-035` T436 states: "anything that cannot reach `stable` in three waves is marked `experimental`
or `deprecated`. An accurate `experimental` label is worth more than an aspirational `beta` one" —
this implies a real distinction between "still experimental" (hasn't earned promotion yet, still
maintained/in use) and "deprecated" (actively being phased out), which `plan-035` names but does not
define. Acceptance Criterion 3 requires that distinction be made concrete here.

**Resolution: `deprecated` is not a demotion destination reached by simply failing to promote.** A
component only becomes `deprecated` when a human (per `plan-035`, `product-owner` for T436's pass,
or `solution-architect` for an architecture-driven removal) makes an explicit decision, recorded via
a required `## Deprecation Notice` section in the component's own file:

```
## Deprecation Notice
**Reason**: <why this is being retired — one or more sentences>
**Replacement**: <id of the component that replaces it>
```
or, if there is no replacement:
```
## Deprecation Notice
**Reason**: <why this is being retired>
**Removal target**: <a version string matching README.md's versioning convention, e.g. v6.16.0>
```

Mechanically checkable, both directions:
- `maturity: deprecated` ⇒ MUST have a `## Deprecation Notice` section containing a non-empty
  `**Reason**:` AND at least one of `**Replacement**:` (resolving to a real, existing component id)
  or `**Removal target**:` (a non-empty version-shaped string).
- `maturity` ∈ {`experimental`, `beta`, `stable`} ⇒ MUST NOT have a `## Deprecation Notice` section
  (mutual exclusivity — a component cannot be simultaneously "on the promotion ladder" and
  "scheduled for removal"; if it needs a notice, the field must say `deprecated`).

This applies identically across all four categories — nothing about the deprecation *decision* or
its *recording* is category-specific; only the promotion ladder above (§3) needed per-category
adaptation, not the exit path.

### 5. Consumed by

- **T432** (`scripts/check-maturity.py`) — implements every criterion in §3 and §4 as a real,
  non-subjective check. §2's two new conventions (`## Rails`, `# maturity-evidence:` tag) and §4's
  `## Deprecation Notice` are the concrete markers the script greps/parses for; §3.5 is the shared
  defect-check helper both `beta`- and `stable`-tier checks call.
- **T433–T435** (Wave 1–3 promotions) — use §3 as the literal checklist per component; §3.1.4(iii),
  §3.3.4, and §3.4.4/.5/.6 flag where a wave must *create* new evidence (task-ledger rows, evidence
  tags, wiki docs) rather than merely *discover* existing evidence, since several of those currently
  sit at zero coverage (documented above per category, not glossed over).
- **T436** (honest demotion pass) — uses §4's `## Deprecation Notice` requirement as the mechanical
  gate distinguishing an honest `experimental` label from an actual `deprecated` decision.
