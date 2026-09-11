# Artifact: task-tier-schema-v1.md

> Filename: `task-tier-schema-v1.md`. Immutable once produced; revisions bump `<N>`.

## Metadata
- **Producer agent**: Solution Architect
- **Task**: T440
- **Created**: 2026-09-11
- **Based on**: `docs/plans/plan-035-roadmap-v7-ground-up.md` §2.4 Phase 4 task table (T440 row,
  the source of the `tier` vocabulary and the literal mechanical-tier gating language quoted
  below); `docs/plans/plan-043-phase4-task-tier-routing-detailed-planning.md` Finding 1 (the real
  routing-candidate pool and the four-role exclusion, re-verified directly in this task rather than
  copied); `implementation/registry/summary.md`, read fresh this session (2026-09-11);
  `docs/tasks/active-tasks.md`, read fresh this session (2026-09-11), for the current status of the
  open tasks cited in §4.
- **Supersedes**: none (first version)
- **Consumed by (future)**: the routing-policy task that is next in `plan-035`'s Phase 4 sequence
  (static tier-to-model-class mapping, to be landed under
  `implementation/knowledge/instructions/` by an owner with both `edit` and `execute` — out of
  scope for this artifact and for T440; see "Not decided here" below).

## Body

### 1. The three tiers

- **`mechanical`** — Work that is fully specified before dispatch: the owning component already
  has proven, test-backed behavior, the task's acceptance criteria are binary and mechanically
  checkable (not a judgment call about quality or design), and there is no open question the
  assignee needs to resolve beyond following the brief. This is the tier eligible for routing to
  an economy-class model once a routing policy exists (a later task's job, not this one's).
- **`standard`** — Work with clear acceptance criteria but real, non-mechanical decision-making
  inside the brief's boundaries: choosing between two reasonable implementation approaches,
  synthesizing information from multiple sources, or working against a component that is proven
  but whose task shape is less rigidly test-backed than `mechanical` requires. This is the default
  tier for most task briefs in this project today.
- **`judgment`** — Work whose correctness cannot be reduced to a checklist: architecture decisions,
  product-priority tradeoffs, security risk acceptance, anything requiring escalation or
  interpretation of ambiguous or conflicting requirements. Everything this project currently routes
  to a judgment-heavy design, priority, or risk-acceptance role defaults here unless a specific
  task instance genuinely meets the `mechanical` bar above.

### 2. The mechanical-tier gating rule

Quoted verbatim from `plan-035` §2.4's T440 row: **"`mechanical` requires stable component +
declared rails + test-backed acceptance criteria."** Restated as three independent, real,
checkable gates — a task brief may declare `tier: mechanical` only if **all three** hold:

1. **Stable component.** The task's owning component (the agent, command, instruction, or skill
   the brief assigns as owner) currently holds this project's top maturity tier, `stable`, as
   mechanically verified by `implementation/scripts/check-maturity.py` and reflected in
   `implementation/registry/summary.md`. A component that merely claims `stable` in its own
   frontmatter without passing that check does not satisfy this gate — `check-maturity.py` is the
   authority, not the declaration.
2. **Declared rails.** The owning component's definition contains an explicit `## Rails` section
   (or equivalent declared-scope section) stating its real inputs, its explicit out-of-scope
   boundary, and its failure mode — the same rails criterion `check-maturity.py` already enforces
   as part of reaching `stable` in gate 1. This gate is listed separately from gate 1 because a
   future maturity-ladder change could in principle decouple them; today, in practice, satisfying
   gate 1 already implies this one.
3. **Test-backed acceptance criteria.** The task brief's own `## Acceptance criteria` section
   consists of criteria a script or test can evaluate as pass/fail (for example: a named test file
   passes, a named golden case passes, a command's output matches a specified check) — not
   criteria that require a human or model to render a subjective judgment ("looks reasonable,"
   "matches intent," "reads well"). If even one acceptance criterion in the brief requires a
   judgment call, the whole task fails this gate and is not eligible for `mechanical`, regardless
   of how the other criteria read.

A task must clear all three gates to legitimately carry `tier: mechanical`. Failing any one gate
means the task is at most `standard` (or `judgment`, per §1's definitions).

### 3. The real, current eligible pool (gate 1 only)

Gate 1 by itself is checkable today; gates 2 and 3 depend on the shape of an individual task
brief, which is not assessed by this artifact (see "Not decided here" below). The pool of
components that currently pass gate 1 — i.e., that currently hold this project's `stable` maturity
tier — was re-derived fresh this session by reading `implementation/registry/summary.md` directly
(the same authoritative source `implementation/scripts/check-maturity.py --root implementation
--verbose` populates; both reflect one registry regenerated together and, per this project's own
recurring practice, are not expected to diverge).

**The real `stable` pool today is 31 components, broken down as: 20 agents, 4 instructions, 7
skills, 0 commands.** No command currently holds `stable`, so no command-owned task can pass gate 1
today. Per the self-referential ledger-defect-avoidance constraint on this task, the individual
`stable` component ids are not enumerated here — see `implementation/registry/summary.md` for the
full, current, per-component list and per-component maturity value.

This figure was independently re-derived by category-counting `summary.md`'s own `| ID | Category
| Maturity | Path |` table this session, not copied from `plan-043`'s prose — it matches
`plan-043`'s Finding 1 count exactly (20/4/7/0 across the same four categories), which is
consistent with no promotion or demotion activity having landed between `plan-043`'s session and
this one.

### 4. Four originally-expected roles that do not currently qualify

`plan-035`'s original Wave-1 naming (§2.4 Phase 3, T433 row) treated four production
coding/review roles as among the highest-traffic components and implicitly the earliest
`mechanical`-tier candidates this roadmap anticipated. As of this session, none of the four
currently hold `stable`, so none currently pass gate 1 above — each for its own real, already-
tracked reason, re-verified directly against `implementation/registry/summary.md` (maturity value)
and `docs/tasks/active-tasks.md` (open blocking task status) this session, not copied uncritically
from any prior planning document:

- **The orchestrator role** — currently `experimental` (`summary.md`, confirmed this session).
  Blocked by tracked golden-suite format-drift/tracked-defect cases inherited from its own owned
  commands (including a `plan`-command header-format drift against real historical plan documents,
  and a held-out review-verdict-format-drift defect on another owned command), recorded in the
  `T433` closure entry of `docs/tasks/completed-tasks.md` as open, unresolved defects at the time
  of that closure and not superseded by any later completed task found in
  `active-tasks.md`/`completed-tasks.md` this session.
- **The tech-lead role** — currently `experimental` (`summary.md`, confirmed this session).
  Blocked by the same held-out review-verdict-format-drift tracked defect cited above (inherited
  via the same `T433` closure record), still unresolved as of this session.
- **The backend-developer role** — currently `experimental` (`summary.md`, confirmed this
  session). Blocked by a confirmed false-positive trip of the project's self-referential
  ledger-defect check: this role's id appears inside open task `T457`'s own brief text as a
  forward-looking possible-assignee note, not as a defect report against this role — the `T433`
  closure record in `completed-tasks.md` explicitly identifies this as a genuine false positive
  that "does not resolve on its own." `T457` is confirmed still open (`pending`, `P1`) in
  `docs/tasks/active-tasks.md` as of this session, so the false-positive mention has not yet been
  removed from that brief and this role's promotion path remains blocked by it in practice.
- **The security-engineer role** — currently `experimental` (`summary.md`, confirmed this
  session). Blocked directly by open task `T457` (confirmed `pending`, `P1`, owner
  `solution-architect`, in `docs/tasks/active-tasks.md` as of this session) — the same
  scoped-execution/read-primitive gap this artifact's own owning task's dependency graph already
  tracks: this role's `tools:` grant includes `execute`, which on at least one supported platform
  maps to effectively unrestricted shell access, so its "read-only" posture is currently enforced
  only by prose instruction, not by a technical tool-scoping control — a real, disclosed,
  unresolved defect, not a false positive.

Because gate 1 (stable component) is a hard precondition for `mechanical`, none of these four roles
can carry `tier: mechanical` on any task today, regardless of how well-specified an individual
task's acceptance criteria might otherwise be. This is expected to change only once the cited
defects/tasks (the format-drift defects behind the first two, and `T457` behind the last two) are
actually resolved and each role's registry entry independently passes `check-maturity.py`'s
`stable` check.

### 5. Not decided here

This artifact defines the `tier` vocabulary and the mechanical-tier gate. It deliberately does
**not**:

- Assign a `tier` value to any specific existing task brief, in `docs/tasks/active-tasks.md`,
  `docs/tasks/completed-tasks.md`, or anywhere else. Per-task tier assignment is future work, left
  to a later step this artifact does not perform.
- Publish a tier-to-model-class routing policy (which model class each tier should route to, or
  the mechanics of escalation on `mechanical` failure). That is explicitly the scope of the next
  task in `plan-035`'s Phase 4 sequence, to be landed under
  `implementation/knowledge/instructions/` by an owner whose tool grant includes `execute` — not
  this task's scope, and not a file this task's owner (`solution-architect`, tool grant
  `[read, search, edit, web, todo, mcp__sequential-thinking, mcp__fetch]`, no `execute`) is
  positioned to land under that directory without triggering a registry-regeneration/
  platform-projection-sync step it cannot perform.
- Re-derive gates 2 and 3 (declared rails, test-backed acceptance criteria) against any specific
  task brief — those two gates are properties of an individual brief's own content, assessable only
  when that brief is written or reviewed, not properties of the component pool this artifact
  characterizes in §3.
- Change `implementation/registry/schema.json`, `implementation/scripts/generate-registry.py`, or
  any file under `implementation/knowledge/**` — all out of this task's declared scope.
