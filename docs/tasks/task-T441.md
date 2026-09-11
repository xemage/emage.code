# Task T441 — Static routing policy (tier -> model class)

**ID:** T441
**Owner:** tech-lead
**Status:** done
**Priority:** P1
**Tier:** standard
**Depends on:** T440 (done)
**Created:** 2026-09-11
**Completed:** 2026-09-11
**Based on:** `docs/plans/plan-035-roadmap-v7-ground-up.md` §2.4 (original T441 row, literal
wording quoted below); `docs/plans/plan-043-phase4-task-tier-routing-detailed-planning.md`
(per-task table T441 row, Finding 2's tool-grant note for this task specifically); `docs/
artifacts/task-tier-schema-v1.md` (T440's delivered tier vocabulary — the three tier names this
task's mapping routes from, and §5 "Not decided here," which explicitly names this task as the
next consumer of that vocabulary and states its owner needs both `edit` and `execute`)

## Objective

Define and publish a **static** routing policy mapping each of the three task tiers defined in
`docs/artifacts/task-tier-schema-v1.md` to a model class, as a new instruction document under
`implementation/knowledge/instructions/`. Quoted verbatim from `plan-035` §2.4's own T441 row —
this is the literal, complete scope, not a starting point for anything broader:

> "Routing policy in `implementation/knowledge/instructions/`: `mechanical` → economy model,
> `standard` → mid, `judgment` → frontier. Static mapping only. **No historical-success-rate
> learning in v6.16** — that requires volume this project does not yet have."

**Hard scope boundary — read before starting, do not expand:** this task publishes a fixed,
hand-authored `tier -> model class` table and nothing else. It does **not** implement, design, or
even sketch any of the following, all of which are explicitly out of scope for this version of the
roadmap per the quoted line above:
- Tracking historical success/failure rates per tier, per component, or per model
- Any mechanism that adjusts the mapping based on past outcomes (adaptive routing, bandit
  algorithms, confidence scores, feedback loops)
- Actually wiring any agent, orchestrator, or CI job to *read* and *enforce* this policy at
  dispatch time (that is plausibly a future task's job, not named or authorized here)
- Escalation mechanics on `mechanical`-tier failure (that is `T442`'s explicitly separate scope,
  per `plan-035` §2.4's own next row and `plan-043`'s task graph — this task's output is
  consumed by T442, not merged with it)

If, while doing this work, you find yourself wanting to add any of the above "to make the policy
actually useful," stop and report it as a `dependency`-type blocker (the right next step is a new,
separately-scoped and separately-approved task) rather than expanding this one's scope silently.

## Inputs

- `docs/plans/plan-035-roadmap-v7-ground-up.md` §2.4 (Phase 4 task table, T441 row, quoted above
  verbatim — re-read it yourself rather than trusting only the quotation in this brief)
- `docs/plans/plan-043-phase4-task-tier-routing-detailed-planning.md` (Finding 2's tool-grant note
  for T441 specifically, and the per-task table's T441 row)
- `docs/artifacts/task-tier-schema-v1.md` (the `mechanical`/`standard`/`judgment` vocabulary this
  policy maps from — §1 for the tier definitions, §5 "Not decided here" for this task's own
  boundary as T440's own authors already understood it)
- `implementation/knowledge/agents/tech-lead.md` (your own real tool grant — confirm it yourself
  at the start of your session rather than trusting this brief's citation of it)
- `implementation/knowledge/schemas/instruction.schema.json` (the frontmatter schema your new file
  must satisfy: `description` (string, min length 10), optional `applyTo`, `maturity` — one of
  `experimental`/`beta`/`stable`/`deprecated`)
- An existing instruction file under `implementation/knowledge/instructions/` (there are four; read
  any one directly in your own session to see the real frontmatter + `## Rails` shape in practice —
  this brief deliberately does not name any of them by id, see the self-referential-ledger-defect
  note in Constraints below)

## Why this lands under `implementation/knowledge/instructions/`, and what that requires

Unlike `T440` (deliberately scoped to stay out of the registry-governed tree specifically because
its owner lacked `execute`), this task's output is a **new file** under `implementation/knowledge/
instructions/`, which **is** registry-governed. This is flagged explicitly, up front, so it is not
discovered mid-task the way an earlier task in this same roadmap discovered it the hard way:

1. `implementation/knowledge/instructions/` is walked by `implementation/scripts/
   generate-registry.py`, which produces `implementation/registry/index.json` and
   `implementation/registry/summary.md`. Adding a new file there without regenerating the registry
   leaves those two files stale, and CI's `validation-super-gate` job (`python3 implementation/
   scripts/check.py --root implementation ... --registry ...`) runs `generate-registry.py --root
   implementation --check` internally and will fail with "registry: generation drift detected" if
   the committed registry does not match a fresh generation.
2. The same directory is also walked by `implementation/scripts/sync.mjs`, which projects every
   instruction file into every supported platform's own instruction folder (there are nine —
   `.github/`, `.cursor/`, `.gemini/`, `.opencode/`, `.pi/`, `.clinerules/`, `.cline/`, `.codex/`,
   `.agents/`). CI's `sync-no-diff` job runs `node implementation/scripts/sync.mjs --root
   implementation` for real (not `--check`) and fails if that produces any uncommitted diff. This
   means your new file must be projected and the resulting platform-folder files committed
   alongside it, not left for CI to generate.
3. Concretely, your workflow must be, in this order: (a) write the new instruction file with
   schema-valid frontmatter; (b) run `python3 implementation/scripts/generate-registry.py --root
   implementation` (no `--check` — this regenerates `index.json`/`summary.md` for real) and stage
   the result; (c) run `node implementation/scripts/sync.mjs --root implementation` and stage every
   resulting platform-projection file; (d) run the verification commands in Acceptance Criteria
   below and confirm all pass clean; (e) commit everything together.
4. Your real tool grant (`implementation/knowledge/agents/tech-lead.md`, checked at dispatch time:
   `[read, search, edit, execute, web, mcp__fetch]`) includes both `edit` and `execute` — this was
   flagged in `plan-043`'s Finding 2 as unlikely to need reassignment, unlike the immediately
   preceding task in this same sequence, whose nominal owner had `edit` but no `execute` and could
   not run these same two scripts itself. **Confirm this empirically at the start of your own
   session** (actually run `python3 implementation/scripts/generate-registry.py --help` and `node
   implementation/scripts/sync.mjs --help` successfully) rather than assuming the grant is
   sufficient just because this brief says so — if either script genuinely fails for a tool-access
   reason (not a content bug), stop and report a `technical` blocker immediately rather than working
   around it.

## Expected outputs

- One new file, `implementation/knowledge/instructions/model-routing-policy.md` — schema-valid
  frontmatter (`description`, `applyTo`, `maturity: experimental` — this is a brand-new component
  with zero evidence history, it cannot legitimately claim anything higher; do not backdate its
  maturity), a `## Rails` section (Inputs / Out of scope / Failure mode, matching the shape used by
  this project's other instruction files, even though `experimental` does not require it to pass
  `check-maturity.py` — write it anyway, it is good practice and costs nothing at this size), and
  the actual policy content: the three-row `tier -> model class` table quoted in Objective above,
  each row naming the class in general terms (`economy`, `mid-tier`, `frontier`) rather than a
  specific vendor/model identifier that would go stale the moment a vendor renames or retires a
  model — state this reasoning explicitly in the file itself as a documented decision, not silently.
  Include the "static mapping only, no historical-success-rate learning in this version" boundary
  verbatim or near-verbatim in the file's own text, so a future reader of the policy (not just this
  brief) understands the boundary without having to find this task's brief first.
- `implementation/registry/index.json` and `implementation/registry/summary.md` — regenerated for
  real via `generate-registry.py` (not hand-edited), reflecting the new component.
- Every platform-projection file `node implementation/scripts/sync.mjs --root implementation`
  produces or updates as a result of the new file (expect this to touch all nine platform folders'
  instruction projections, plus their respective MCP/manifest indexes if `sync.mjs` regenerates
  those as a side effect of adding a new instruction — commit whatever the tool actually produces,
  do not hand-pick a subset).

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
  in this project's history — T433, T434/T435, T436, T437, T483, and T440 already hit it once for
  this same tier-schema work).** `implementation/scripts/check-maturity.py` flags any open,
  non-`done`/non-`cancelled` `P0` or `P1` task whose title or brief text names a component's real
  registry id by exact, whole-word text — and this task's own row is open at `P1` while you work.
  Before you consider your work done: independently re-derive the current, real list of components
  holding this project's top maturity tier yourself (`python3 implementation/scripts/
  check-maturity.py --root implementation --verbose`, or read `implementation/registry/summary.md`
  directly — do not trust a count or list quoted in this brief or in any plan document without
  re-checking it against the live repo state), then grep your own new/edited file (and this brief,
  if you touch it) against every one of those ids. If you find a hit, fix it (generic phrasing or a
  placeholder, not the literal id) before reporting completion. This brief itself was swept against
  that same live list before being written and named none of them — keep it that way.

## Acceptance criteria

1. `implementation/knowledge/instructions/model-routing-policy.md` exists, has schema-valid
   frontmatter, states the three-tier mapping exactly as quoted in Objective (or a clear
   equivalent — `mechanical`→economy, `standard`→mid, `judgment`→frontier), and explicitly states
   the "static mapping only, no historical-success-rate learning" boundary in its own text.
2. `python3 implementation/scripts/generate-registry.py --root implementation --check` passes
   (no drift) after your commit.
3. `node implementation/scripts/sync.mjs --root implementation` produces a clean `git diff`
   (nothing left uncommitted) after your commit — i.e., what you committed already matches a fresh
   sync run.
4. `python3 implementation/scripts/check.py --root implementation --required --schemas
   --cookbooks --handoff-security --hook-policy --telemetry --benchmarks --registry --maturity
   --packaging --triggers --adapters` passes clean (this is the literal CI `validation-super-gate`
   command — run it yourself before reporting completion, do not assume).
5. `python3 implementation/scripts/check-maturity.py --root implementation --verbose` still
   reports `0 failing` and the same real component count it reported before your change, plus
   exactly one new `experimental` entry for the new file (the pool of components holding the top
   maturity tier must be unchanged by this task — you are adding a new, unproven component, not
   promoting or demoting anything else).
6. `python3 docs/tasks/validate-tasks.py` still passes (you are not editing the ledger, so this
   should be unaffected either way — run it anyway as a sanity check).
7. `python3 tests/run.py` passes with no new failures (report the exact before/after test count and
   skip count you observed).
8. Zero literal, exact, hyphenated registry-id mentions of any currently-top-maturity-tier
   component anywhere in your new/edited files (self-checked per the Constraints section above).
9. `git diff --stat` against `origin/develop` shows only the new instruction file, the regenerated
   registry files, and genuine `sync.mjs`-produced platform-projection files — nothing under
   `tests/golden/**`, `scripts/scorecard.py`, `docs/benchmarks/tb-subset.*`, `docs/tasks/
   active-tasks.md`, `docs/tasks/completed-tasks.md`, or `feature/T475-codex-platform-integration`.
10. A merge request is opened from your branch (`agent/tech-lead/T441`) to `develop`, referencing
    `T441` in its title or description, left **unmerged**.

## Blocker protocol

Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`) +
severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries before
escalating back to the orchestrator. In particular: if `generate-registry.py` or `sync.mjs` fail
for a reason that is not a straightforward content fix in your own new file (a genuine tool-access
problem, or a pre-existing drift unrelated to your change), stop and report rather than trying to
force a workaround — the orchestrator will independently re-verify your work before it can merge,
so a reported, disclosed blocker is strictly better than a silently-patched-over one.

## Execution notes

Delivered: `implementation/knowledge/instructions/model-routing-policy.md` (new — static
`mechanical`→economy / `standard`→mid-tier / `judgment`→frontier mapping, with an explicit
"no historical-success-rate learning" boundary stated in the file's own text, and the general
model-class-not-vendor-identifier reasoning disclosed inline); `implementation/registry/
index.json` + `implementation/registry/summary.md` (regenerated for real via `generate-registry.py`,
not hand-edited); one new instruction file projected into all seven currently-supported platform
instruction folders via `sync.mjs` (the two remaining platforms in this project's full platform
list do not project a separate instructions tree — `sync.mjs`'s own manifest config, not an
omission); one minimal, disclosed content fix to `tests/functional/test_check_maturity.py`'s
pre-existing hardcoded real-repo component-count assertion (77→78, plus one new `instruction/
experimental: 1 pass, 0 fail` line), required because the new, legitimate component shifted the
real registry count this test asserts against. Merged via MR !285 (`agent/tech-lead/T441`,
commits `095097b`/`c39698f`/`a237d37`) — left unmerged per this session's standing no-self-merge
instruction; hand back to the top-level session for merging.

**Orchestrator independent verification before this status update** (not accepted on the
implementer's self-report alone): re-checked out the pushed branch fresh into a separate,
detached-HEAD worktree (not the implementer's own working copy) and independently re-ran every
verification command named in Acceptance Criteria above: `generate-registry.py --root
implementation --check` → "registry is up to date"; `node implementation/scripts/sync.mjs --root
implementation` (real run, not `--check`) → 570 files written, `git status --short` empty
afterward; `check.py` validation-super-gate (the literal CI command) → "OK - 254 checks passed, 0
errors"; `check-maturity.py --root implementation --verbose` → 78 components, 0 failing, stable
pool unchanged (`agent/stable: 20 pass, 0 fail`, `instruction/stable: 4 pass, 0 fail`, `skill/
stable: 7 pass, 0 fail`), exactly one new `instruction/experimental: 1 pass, 0 fail`; `python3
docs/tasks/validate-tasks.py` → PASS; `python3 tests/run.py` → 514 tests, `OK`, `skipped=24`,
unchanged from baseline. All six independently matched the implementer's self-reported numbers
exactly. `git diff --stat origin/develop` confirmed to touch only the files named above plus this
brief/ledger row — zero protected-path hits (`tests/golden/**`, `scripts/scorecard.py`, `docs/
benchmarks/tb-subset.*` all confirmed untouched via a direct diff against each path). Real GitLab
CI independently polled on the actual pushed SHA (`a237d37`) — 5/5 jobs green (`sync-no-diff`,
`validation-super-gate`, `verify-knowledge-drift`, `unit-tests`, `markdown-links`), not assumed
from the implementer's report.

**Self-referential ledger-defect sweep, re-run independently before this closure**: grepped this
brief and the new instruction file against the real, freshly re-derived 31-id top-maturity-tier
list — zero hits in either. (A broader, non-authoritative sweep across every changed file,
including `implementation/registry/index.json`/`summary.md`, the platform-projection
`.generated-manifest.json` files, and `tests/functional/test_check_maturity.py`, does surface
many of those same ids — expected and not a defect, since those files legitimately enumerate every
registered component by design and are not `docs/tasks/task-<ID>.md` briefs or ledger row titles,
the only two file classes `check-maturity.py`'s actual defect-check scans. The empirically observed
`0 failing` result from `check-maturity.py` itself is the authoritative confirmation, not the
naive grep.)

**Ledger-closure sequencing, disclosed explicitly**: this status update and the corresponding
`active-tasks.md`→`completed-tasks.md` row move are committed directly onto this same branch
(`agent/tech-lead/T441`), as a further commit after the implementer's own commits, rather than as
a separate ledger-only branch or MR — per this dispatch's own stated intent (see the "T441
dispatched" note originally recorded in `active-tasks.md`) to avoid the exact
pending-row-survives-after-merge ledger-sequencing gap found during T440's own dispatch. As a
direct consequence, MR !285 now carries both the implementation and its own ledger closure in one
mergeable unit — there is no valid merge order concern for the top-level session merging this MR;
it is atomic by construction.
