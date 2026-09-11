# Task T442 — Escalation on `mechanical`-tier failure + misclassification defect-opening

**ID:** T442
**Owner:** backend-developer
**Status:** done
**Priority:** P1
**Tier:** standard
**Depends on:** T441 (done)
**Created:** 2026-09-11
**Completed:** 2026-09-12
**Based on:** `docs/plans/plan-035-roadmap-v7-ground-up.md` §2.4 (original T442 row, literal
wording quoted below, and the Phase 4 acceptance-criteria block); `docs/plans/plan-043-phase4-task-
tier-routing-detailed-planning.md` (per-task table T442 row, Finding 2's tool-grant note for this
task specifically, and the task-graph note "Needs T441's policy to exist so 'escalate one tier' has
a concrete target to escalate to"); `implementation/knowledge/instructions/model-routing-policy.md`
(T441's delivered tier->model-class mapping — this task's escalation target — and its own explicit
"Escalation mechanics on `mechanical`-tier failure (a separately scoped, separately authorized
task)" out-of-scope line, which names this task); `docs/artifacts/task-tier-schema-v1.md` (T440's
tier vocabulary this task's escalation logic operates over)

## Objective

Define and publish a policy document stating two related rules, as a new instruction document
under `implementation/knowledge/instructions/` (see "Location determination" below for why, stated
explicitly so this is not discovered or guessed mid-task). Quoted verbatim from `plan-035` §2.4's
own T442 row — this is the literal scope this task starts from:

> "Escalation: on `mechanical` failure, escalate one tier and record the escalation. Two
> escalations on the same brief class = the brief is misclassified; open a defect against the
> brief, not the model."

Concretely, this task must state, in writing, in the new instruction document:

1. **The escalation rule.** When a task brief carrying `tier: mechanical` fails at the model class
   `model-routing-policy.md` routes `mechanical` to (`economy`, per that document's table), the
   correct response is to escalate **one tier**, not to fail the task outright and not to skip
   straight to the top tier. "One tier" means the task is retried at the model class the *next*
   tier up (`standard` -> `mid-tier`, per the same table) routes to — not `judgment` -> `frontier`.
   State this mapping explicitly rather than leaving "one tier" for a future reader to work out
   from two separate documents.
2. **The recording rule.** Every escalation must be recorded — this document must state *what*
   should be recorded (at minimum: the task id, the original tier, the model class escalated to,
   and the outcome after escalation) so a future consumer (concretely, `T443`'s scorecard-extension
   work, not yet dispatched) knows what shape of data to expect. Per "Hard scope boundary" below,
   this task states the recording *requirement*, it does not build a recording mechanism.
3. **The misclassification-defect rule.** If the same "brief class" (see "Defining 'brief class'"
   below — this task must propose and document a concrete, checkable definition; `plan-035` does
   not define the term) escalates **twice**, that is a signal the *tiering assignment itself* was
   wrong for that class of task, not that the model failed twice by chance. The document must state
   that the correct response is to open a defect against the brief/tiering-assignment process for
   that class — using this project's own existing defect-representation mechanism (a tracked task
   in `docs/tasks/active-tasks.md`, the same representation `implementation/scripts/
   check-maturity.py`'s ledger-defect check already recognizes as this project's defect model) —
   and explicitly *not* to just silently re-route the task again a third time.

## Hard scope boundary — read before starting, do not expand

**This is a mechanism/policy definition task, mirroring `T441`'s own explicit scope boundary.** It
states the escalation and misclassification-defect *policy* in writing. It does **not**:

- Implement any dispatch-time enforcement — no code, hook, or CI job that actually detects a
  `mechanical`-tier failure and re-dispatches the task at a higher model class. `model-routing-
  policy.md` itself already states "actually wiring any agent, orchestrator, or CI job to read and
  enforce this mapping at dispatch time... is left to future, separately scoped and separately
  authorized work" — this task inherits that same boundary for the escalation logic on top of it.
- Implement a live recording mechanism (a database, log format, or code path that actually writes
  an escalation record somewhere). It states what a future recording mechanism must capture; it
  does not build that mechanism. That is plausibly `T443`'s job (extending the scorecard), not
  authorized or scoped here.
- Implement live, automatic defect-opening (no code that actually creates a task row, a GitLab
  issue, or any other artifact when two escalations are detected). It states the rule in writing;
  a human or a future automation applies it.
- Assign a `tier` value to any specific existing task brief, or retroactively evaluate any past
  task against this rule. Out of scope, same as it was for `T440`/`T441`.

**This scope boundary reflects an orchestrator determination, not a word-for-word instruction found
in `plan-035` or `plan-043`.** `plan-035`'s Phase 4 acceptance criteria include "Marking a
`judgment` task as `mechanical` produces escalation, not silent degradation" — read at face value,
this could be argued to require a *working* mechanism by the time Phase 4 as a whole ships. This
task is deliberately scoped to the policy-definition half only, for three stated reasons: (a)
`plan-043`'s own per-task table lists this task's scope as `medium`, matching `T440`/`T441`, not
`large`, which working dispatch-time enforcement would plausibly require; (b) `T441`'s own text
explicitly named this task as the next step and scoped itself to policy-only, setting a direct,
adjacent precedent; (c) no dispatch-time routing mechanism exists yet for this policy to hook into
in the first place — `model-routing-policy.md` states plainly that nothing currently reads or
enforces its mapping. **If, while doing this work, you conclude the Phase 4 acceptance criterion
genuinely requires a working mechanism now, do not build it — stop and report a `dependency`-type
blocker** naming this exact tension so the orchestrator can decide whether a new, separately-scoped
task is needed, rather than silently expanding this one's scope in either direction.

## Defining "brief class" — a genuine open call this task must make, and document

`plan-035`'s literal text ("two escalations on the same brief class") does not define "brief
class" anywhere in this repository. This task must propose a concrete, checkable working
definition and state it explicitly in the document's own text — do not leave the term undefined
and hope a future reader infers it. A recommended starting point, offered here as guidance, not as
a instruction to copy verbatim: define "brief class" as *the combination of the task's declared
owning component and its declared tier* (e.g., two separate `mechanical`-tier tasks both owned by
the same agent/component, each independently escalating) — this reading is the most literal fit
for "the brief is misclassified" being a property of *how tasks for that owner/component are being
tiered*, not a property of any single task instance or of the model that happened to run it. You
are free to refine or replace this definition if you find a better-grounded one, but whichever
definition you choose, state it explicitly and explain why, the same way `task-tier-schema-v1.md`
stated explicit, checkable gate definitions rather than leaving them implicit.

## Location determination (orchestrator finding, stated explicitly per this dispatch's own
instruction — do not re-derive or guess)

`plan-043`'s artifact-flow section names this task's target only loosely: "`implementation/
knowledge/...` escalation mechanism + defect-opening hook (T442)" — it does not commit to a
specific subdirectory. This brief resolves that ambiguity, on the orchestrator's own reasoning, as
follows: **this task's deliverable lands under `implementation/knowledge/instructions/`, as a new
file, the same registry-governed category and directory `T441`'s `model-routing-policy.md` already
lands in.** Reasoning: (a) this task's content is a written policy/procedure statement, not a
step-by-step invocable workflow — the same character as the four other files already in that
directory, not the character of anything under `implementation/knowledge/skills/`; (b) this task is
a direct, explicit continuation of `T441`'s policy (it extends "what happens when the routed model
class fails," a natural sibling to "what model class to route to"), and `model-routing-policy.md`'s
own "Out of scope" section explicitly frames escalation mechanics as a *separate task*, not a
separate *kind* of artifact; (c) `plan-043`'s Finding 2 already checked this task's owner
(`backend-developer`) against the expectation that this task, like `T441`, needs both `edit` and
`execute` — consistent with landing in a registry-governed directory requiring the same
`generate-registry.py`/`sync.mjs` regeneration workflow `T441` needed, not with a lighter-weight
location. **If you find affirmative evidence this determination is wrong before you start writing
(for example, a location this brief did not consider that fits the file's content better), report
it as an `unclear_requirements` blocker rather than silently picking a different location** — this
determination is the orchestrator's own reasoned call, not something either plan pins down with
certainty, so it is worth a second, and it is not to be reversed without disclosure.

**Recommended filename:** `mechanical-tier-escalation-policy.md`, not a shorter `escalation-
policy.md` — this project's own vocabulary already uses "escalation" for a distinct, existing
concept (the `docs/tasks/task-<ID>.md` "Blocker protocol" section's blocker-escalation mechanism,
used by every task brief including this one). A shorter, generic filename risks being confused with
that unrelated concept in a future search or reference. You may choose a different filename if you
have a better-grounded reason, but state your reasoning if you deviate from this recommendation.

## Inputs

- `docs/plans/plan-035-roadmap-v7-ground-up.md` §2.4 (Phase 4 task table, T442 row, quoted above
  verbatim, and the Phase 4 "Acceptance criteria" block immediately below that table — re-read both
  yourself rather than trusting only the quotations in this brief)
- `docs/plans/plan-043-phase4-task-tier-routing-detailed-planning.md` (Finding 2's tool-grant note,
  the per-task table's T442 row, and the task-graph's T442 node)
- `implementation/knowledge/instructions/model-routing-policy.md` (read this file directly and in
  full — it is this task's immediate predecessor and the document this task's new file must be
  consistent with, not duplicate; its `## Rails` and "Explicit scope boundary" sections show the
  shape this project's policy documents use)
- `docs/artifacts/task-tier-schema-v1.md` (the `mechanical`/`standard`/`judgment` vocabulary and
  the mechanical-tier gating rule this escalation logic assumes)
- `implementation/knowledge/agents/backend-developer.md` (your own real tool grant — confirm it
  yourself at the start of your session rather than trusting this brief's citation of it)
- `implementation/knowledge/schemas/instruction.schema.json` (the frontmatter schema your new file
  must satisfy: `description` (string, min length 10), optional `applyTo`, `maturity` — one of
  `experimental`/`beta`/`stable`/`deprecated`)
- `implementation/knowledge/instructions/model-routing-policy.md` also doubles as your best
  reference for the real frontmatter + `## Rails` shape other instruction files in this project use
  in practice (this brief deliberately does not name any *already-`stable`* instruction file by id
  as a reference — see the self-referential-ledger-defect note in Constraints below)

## Why this lands under `implementation/knowledge/instructions/`, and what that requires

Same registry-governed directory, same requirements `T441` already had to satisfy — restated here
rather than assumed to transfer silently:

1. `implementation/knowledge/instructions/` is walked by `implementation/scripts/
   generate-registry.py`, which produces `implementation/registry/index.json` and
   `implementation/registry/summary.md`. Adding a new file there without regenerating the registry
   leaves those two files stale, and CI's `validation-super-gate` job runs `generate-registry.py
   --root implementation --check` internally and will fail with "registry: generation drift
   detected" if the committed registry does not match a fresh generation.
2. The same directory is walked by `implementation/scripts/sync.mjs`, which projects every
   instruction file into every supported platform's own instruction folder. CI's `sync-no-diff` job
   runs `node implementation/scripts/sync.mjs --root implementation` for real (not `--check`) and
   fails if that produces any uncommitted diff. Your new file must be projected and the resulting
   platform-folder files committed alongside it.
3. Concrete required workflow, in order: (a) write the new instruction file with schema-valid
   frontmatter; (b) run `python3 implementation/scripts/generate-registry.py --root implementation`
   (no `--check` — regenerates `index.json`/`summary.md` for real) and stage the result; (c) run
   `node implementation/scripts/sync.mjs --root implementation` and stage every resulting
   platform-projection file; (d) run the verification commands in Acceptance Criteria below and
   confirm all pass clean; (e) commit everything together.
4. Your real tool grant, per `implementation/knowledge/agents/backend-developer.md` (re-checked
   directly by the orchestrator immediately before this dispatch: `[read, search, edit, execute,
   web, mcp__fetch]`) — has both `edit` and `execute`, matching `plan-043`'s Finding 2 expectation
   of no reassignment needed. **Confirm this empirically yourself at the start of your session**
   (actually run `python3 implementation/scripts/generate-registry.py --help` and `node
   implementation/scripts/sync.mjs --help` successfully) rather than assuming the grant is
   sufficient just because this brief says so — if either script genuinely fails for a tool-access
   reason (not a content bug), stop and report a `technical` blocker immediately.

## Expected outputs

- One new file, `implementation/knowledge/instructions/mechanical-tier-escalation-policy.md` (or
  your chosen, disclosed alternative filename) — schema-valid frontmatter (`description`,
  `applyTo`, `maturity: experimental` — brand-new component, zero evidence history, do not
  backdate its maturity), a `## Rails` section matching the shape `model-routing-policy.md` uses
  (Inputs / Out of scope / Failure mode), and the actual policy content: the escalation rule, the
  recording rule, and the misclassification-defect rule, each stated explicitly per "Objective"
  above, including your documented "brief class" definition per the dedicated section above.
- `implementation/registry/index.json` and `implementation/registry/summary.md` — regenerated for
  real via `generate-registry.py` (not hand-edited), reflecting the new component.
- Every platform-projection file `node implementation/scripts/sync.mjs --root implementation`
  produces or updates as a result of the new file — commit whatever the tool actually produces, do
  not hand-pick a subset.

## Constraints

- Token budget: medium scope, matching `plan-043`'s disposition for T440-T442.
- Do not touch `feature/T475-codex-platform-integration` in any way.
- Do not edit `tests/golden/**`, `scripts/scorecard.py`, or `docs/benchmarks/tb-subset.json`/`.md`
  — all three remain protected/frozen; this task has no legitimate reason to touch any of them.
- No paid/metered API calls of any kind.
- Do not edit `docs/tasks/active-tasks.md` or `docs/tasks/completed-tasks.md` — ledger transitions
  are orchestrator-only per this project's own standing protocol. Report completion back to the
  orchestrator; do not archive your own task row.
- Do not run `glab mr merge` (or any equivalent) on the merge request you open. Open it, leave it
  open, and stop. This is a standing instruction for every dispatch in this session, not specific
  to you.
- **Self-referential ledger-defect avoidance (this exact class of mistake has recurred repeatedly
  in this project's history — T433, T434/T435, T436, T437, T483, T440, and T441 have all had to
  check for it).** `implementation/scripts/check-maturity.py` flags any open, non-`done`/
  non-`cancelled` `P0` or `P1` task whose title or brief text names a component's real registry id
  by exact, whole-word text — and this task's own row is open at `P1` while you work. Before you
  consider your work done: independently re-derive the current, real list of components holding
  this project's top maturity tier yourself (`python3 implementation/scripts/check-maturity.py
  --root implementation --verbose`, or read `implementation/registry/summary.md` directly — do not
  trust a count or list quoted in this brief or in any plan document without re-checking it against
  the live repo state), then grep your own new/edited file (and this brief, if you touch it)
  against every one of those ids. If you find a hit, fix it (generic phrasing or a placeholder, not
  the literal id) before reporting completion. This brief itself was swept against that same live
  list (31 ids: 20 agents, 4 instructions, 7 skills, 0 commands, independently re-derived from
  `implementation/registry/summary.md` before this brief was written) and named none of them by
  literal id — keep it that way. (`backend-developer` is not on that list — it currently holds
  `experimental` maturity — so naming it as this task's owner is not itself a self-referential hit.)

## Acceptance criteria

1. `implementation/knowledge/instructions/mechanical-tier-escalation-policy.md` (or your disclosed
   alternative filename) exists, has schema-valid frontmatter, and states all three rules from
   "Objective" above explicitly in its own text: the one-tier escalation rule (with the concrete
   `mechanical`->`standard` model-class mapping spelled out, not left implicit), the recording
   requirement (with the minimum fields to capture named), and the misclassification-defect rule
   (with your documented "brief class" definition).
2. The document explicitly states, in its own "Out of scope" or equivalent section, that it does
   not implement dispatch-time enforcement, a live recording mechanism, or live automatic
   defect-opening — mirroring `model-routing-policy.md`'s own scope-boundary disclosure.
3. `python3 implementation/scripts/generate-registry.py --root implementation --check` passes
   (no drift) after your commit.
4. `node implementation/scripts/sync.mjs --root implementation` produces a clean `git diff`
   (nothing left uncommitted) after your commit.
5. `python3 implementation/scripts/check.py --root implementation --required --schemas
   --cookbooks --handoff-security --hook-policy --telemetry --benchmarks --registry --maturity
   --packaging --triggers --adapters` passes clean (the literal CI `validation-super-gate` command
   — run it yourself, do not assume).
6. `python3 implementation/scripts/check-maturity.py --root implementation --verbose` still reports
   `0 failing`, with the real component count incremented by exactly one new `experimental` entry
   for this new file, and the existing top-maturity-tier pool otherwise unchanged.
7. `python3 docs/tasks/validate-tasks.py` still passes.
8. `python3 tests/run.py` passes with no new failures (report the exact before/after test count and
   skip count you observed — expect a possible hardcoded-count-assertion fix in
   `tests/functional/test_check_maturity.py`, the same class of change `T441` needed, if the same
   test asserts an exact real component count; only touch it if your own run actually requires it,
   do not pre-emptively edit it).
9. Zero literal, exact, hyphenated registry-id mentions of any currently-top-maturity-tier
   component anywhere in your new/edited files (self-checked per the Constraints section above).
10. `git diff --stat` against `origin/develop` shows only the new instruction file, the regenerated
    registry files, genuine `sync.mjs`-produced platform-projection files, and (only if genuinely
    required per item 8) the one disclosed test-assertion fix — nothing under `tests/golden/**`,
    `scripts/scorecard.py`, `docs/benchmarks/tb-subset.*`, `docs/tasks/active-tasks.md`, `docs/
    tasks/completed-tasks.md`, or `feature/T475-codex-platform-integration`.
11. A merge request is opened from your branch (`agent/backend-developer/T442`) to `develop`,
    referencing `T442` in its title or description, left **unmerged**.

## Blocker protocol

Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`) +
severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries before
escalating back to the orchestrator. In particular: if you conclude the Phase 4 acceptance
criterion ("Marking a `judgment` task as `mechanical` produces escalation, not silent degradation")
genuinely requires working enforcement now rather than a policy statement, or if you find the
"Location determination" section's reasoning wrong before you start, stop and report rather than
silently resolving either question yourself in a direction this brief did not disclose.

## Execution notes

Delivered: `implementation/knowledge/instructions/mechanical-tier-escalation-policy.md` (new,
schema-valid frontmatter, `maturity: experimental`), stating all three rules from the "Objective"
section explicitly — the one-tier escalation mapping (`mechanical`/economy -> `standard`/mid-tier,
spelled out, not left implicit), the recording requirement (task id, original tier, escalated-to
model class, outcome after escalation), and the misclassification-defect rule with a documented
"brief class" definition (owner `Owner:` field + declared `tier`, chosen over owner-alone,
tier-alone, or title/acceptance-criteria-shape alternatives, with reasoning given for the choice).
An explicit "Out of scope" subsection under `## Rails` states the document does not implement
dispatch-time enforcement, a live recording mechanism, or live automatic defect-opening, mirroring
`model-routing-policy.md`'s own scope-boundary disclosure. `implementation/registry/{index.json,
summary.md}` regenerated for real via `generate-registry.py`. Seven platform-projection files
(`.claude`, `.clinerules`, `.cursor`, `.gemini`, `.github`, `.opencode`, `.pi`) produced via
`sync.mjs` — no `.codex` projection, correctly, since Codex platform support has not yet merged to
`develop` (it exists only on the separate, unmerged `feature/T475-codex-platform-integration`
branch this task correctly left untouched). One minimal, disclosed fix to the pre-existing
hardcoded component-count assertion in `tests/functional/test_check_maturity.py` (78->79, plus one
new `instruction/experimental: 2 pass, 0 fail` line), required because the new legitimate
component shifted the real count that test asserts against. The implementer correctly did not
touch `docs/tasks/active-tasks.md` or `docs/tasks/completed-tasks.md` (ledger transitions are
orchestrator-only per this task's own Constraints section) — its commit (`b7c6c0e`) contains
exactly the 18 files listed above; the dispatch commit (`88f854e`) separately carries the 2 ledger
files.

**Orchestrator independent verification before this closure** (not accepted on the implementer's
self-report alone): re-checked out the pushed branch fresh (`origin/agent/backend-developer/T442`,
confirmed identical to the local worktree HEAD, `b7c6c0e`, no drift). `git diff --stat
origin/develop origin/agent/backend-developer/T442` matched the implementer's claimed 20 files
exactly (verified via `--name-status`, and per-commit via `git show --stat` on each of `88f854e`
and `b7c6c0e` separately); zero hits confirmed directly against `tests/golden/**`,
`scripts/scorecard.py`, `docs/benchmarks/tb-subset.*`, and `.mcp.json`; confirmed no overlap with
`feature/T475-codex-platform-integration` (a local-only, unpushed branch, not touched by this
branch's history). Read the new policy file in full: confirmed the quoted rule text is verbatim
against `plan-035-roadmap-v7-ground-up.md` §2.4's real T442 row; confirmed it correctly cites and
is consistent with both `docs/artifacts/task-tier-schema-v1.md` (T440) and
`implementation/knowledge/instructions/model-routing-policy.md` (T441) without contradicting
either (both read in full for this check) — it correctly identifies itself as the direct
continuation of the "escalation mechanics... a separately scoped, separately authorized task" line
`model-routing-policy.md` itself states as out of scope. Re-ran, fresh, independently:
`generate-registry.py --root implementation --check` -> "registry is up to date"; a real
`node implementation/scripts/sync.mjs` run (577 files written) -> clean `git status`/`git diff`
afterward, zero drift; `check-maturity.py --root implementation --verbose` -> 79 components
checked, 0 failing, stable pool unchanged at 31 (`agent/stable: 20`, `instruction/stable: 4`,
`skill/stable: 7`), exactly one new `instruction/experimental` (2 pass total, up from 1);
`python3 docs/tasks/validate-tasks.py` -> `TASK LEDGER: PASS`; `python3 tests/run.py` -> 514
tests, `OK`, `skipped=24`, unchanged from baseline. All independently matched the implementer's
self-reported numbers exactly. Self-referential ledger-defect sweep re-run independently: grepped
the new policy file, and the isolated new `active-tasks.md` dispatch-note block, against the real,
freshly re-derived 31-id top-maturity-tier list (re-extracted directly from `summary.md`, not
copied) — zero hits in either. Real GitLab CI independently polled to completion on the actual
pushed SHA (`b7c6c0e`, pipeline `2842157383`) — 5/5 jobs green (`sync-no-diff`,
`validation-super-gate`, `verify-knowledge-drift`, `unit-tests`, `markdown-links`), not assumed.
MR !286 confirmed via API: source `agent/backend-developer/T442` -> target `develop`, not a
draft, `merge_status: mergeable`, SHA matches HEAD exactly.

**"Brief class" definition assessed for future usability, per this closure's own remit**: the
policy's "Defining 'brief class'" section states a concrete, checkable definition (owning
component's `Owner:` field + declared `tier`, both already present on every task brief header) and
explains why it was chosen over three named alternatives (owner alone, tier alone, title-text or
acceptance-criteria-shape keying) — a future task-tier reassignment or defect-opening decision can
apply it directly from a brief's own header fields without re-deriving what "brief class" means.
Not flagged as vague.

**Ledger-closure sequencing, disclosed explicitly, mirroring `T441`'s own precedent**: this status
update and the corresponding `active-tasks.md` -> `completed-tasks.md` row move are committed
directly onto this same branch (`agent/backend-developer/T442`), as a further commit after the
implementer's own commit, added only after the independent verification above passed — not a
separate ledger-only branch or MR. MR !286 now carries the implementation and its own ledger
closure in one mergeable unit. Left unmerged per this session's standing no-self-merge
instruction — handed back to the top-level session for merging.
