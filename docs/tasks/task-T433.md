# Task T433 — Wave 1 promotion (8 highest-traffic components) to `stable`

**ID:** T433
**Owner:** tech-lead (matches `plan-035`/`plan-041`'s own assignment; tool grant checked before
dispatch — `implementation/knowledge/agents/tech-lead.md`'s registered grant is `[read, search,
edit, execute, web, mcp__fetch]`, has `execute`)
**Status:** pending
**Priority:** P0 (closes Gate G2 per `ADR-006`; blocks T434/T435, which both depend on T433's
outcome)
**Depends on:** T432 (done — `implementation/scripts/check-maturity.py`, the real, CI-enforced
verifier this task's promotions must actually pass, not just declare)
**Blocks:** T434, T435
**Created:** 2026-09-10
**Completed:** —
**Based on:** `docs/plans/plan-041-phase3-maturity-ladder-detailed-planning.md` (approved, merged
MR !252) — specifically its T433 row and Finding 1; `docs/plans/plan-035-roadmap-v7-ground-up.md`
§2.4 Phase 3 (T433's original nominal scope, the 8 named components); `docs/decisions/
ADR-006-gate-g2-routing-target-classes-interpretation.md` (the user-approved resolution of Finding
1's "routing target classes" ambiguity — read this before starting, it changes what this task does
and does not need to produce); `docs/artifacts/maturity-promotion-criteria-v1.md` (T431 — the real
per-category `beta→stable` criteria every promotion in this task must satisfy); `docs/artifacts/
maturity-levels-v1.md` (T430 — enum, mandatory-field policy); `implementation/scripts/
check-maturity.py` (T432 — run this against every claimed promotion before reporting it as done,
it is the actual acceptance mechanism, not a formality).

## Gate G2 disposition — read this before starting

Per `ADR-006` (accepted, this session): **this task does not need to identify, rank, or reserve
any subset of its 8 components as "routing target classes."** That question — which task classes
are candidates for Phase 4's cost-tier routing — is explicitly deferred to Phase 4's own future
planning pass, once Phase 4's `T440` defines a real tier schema (`mechanical`/`standard`/
`judgment`) to judge against. Gate G2 closes on this task's completion under the
infrastructure-precondition reading: once these 8 components have genuinely, mechanically-verified
`stable` status (via T432's real checker, not a status-field flip), the *general* precondition G2's
own gate-table row states ("target task class has a stable brief with rails and tests") is
satisfied in substance. **Do not attempt Phase 4-style routing-candidate analysis in this task** —
it is out of scope and was deliberately excluded by `ADR-006`, not merely unaddressed.

## Objective

Genuinely promote each of the following 8 named components (per `plan-035` §2.4's literal list) to
`stable`, satisfying every one of `docs/artifacts/maturity-promotion-criteria-v1.md`'s real
`beta→stable` criteria for its category — not a `maturity:` field edit alone. Where a component is
missing required evidence (a golden case, a `# maturity-evidence:` tag, a `## Rails` section, a
`docs/wiki/**` entry, a cross-reference), **produce that evidence for real** — author the golden
case, add the tag to a real test, write the Rails section with real content, write the wiki entry —
then verify the promotion actually passes `python3 implementation/scripts/check-maturity.py --root
implementation --verbose` before reporting it as done.

**The 8 named components** (`agent` unless noted): `orchestrator`, `tech-lead`,
`backend-developer`, `qa-engineer`, `security-engineer` (5 agents); `validation-gates` (`skill` —
only id match; no command of that name exists); `plan` (`command` — only id match; the skill with
similar scope is named `plan-approve-execute`, a different id, not part of this list).

**Known identifier ambiguity — resolve and disclose, do not silently pick:** `code-review` exists
as *both* a `skill` id (`implementation/knowledge/skills/code-review/SKILL.md`) and a `command` id
(`implementation/knowledge/commands/code-review.md`), with no basis in `plan-035`'s text to prefer
one over the other. State your resolution explicitly in your completion report and in the design
artifact below (promote both, since "the 8 highest-traffic components" plausibly means the
*workflow* rather than one specific artifact type; promote only one with justification for which;
or treat this as a `type: unclear_requirements` blocker if you judge it genuinely needs the
orchestrator's input — any of these is an acceptable outcome, silent, undisclosed selection of one
is not).

## Scope warning — read before estimating

Per `plan-041`'s own explicit flag: **this is Phase 3's largest single task and the one most likely
to need the same kind of mid-task re-scoping T407/T417-T419 and T458 needed.** 8 components × up to
7 real criteria each (agent/skill categories need real golden-case-or-evidence-tag authorship,
real Rails content, real wiki documentation — none of which currently exists for most of these
components, confirmed by `maturity-promotion-criteria-v1.md`'s own coverage grounding: e.g. **zero**
skills are documented in `docs/wiki/**` today, and no skill has the formal `# maturity-evidence:`
tag yet). **Do not treat this as a "large, but one dispatch" task by default** — if, once you've
surveyed the real gap per component, the total real authorship work (new golden cases, new wiki
pages, etc.) clearly exceeds what one task/branch can responsibly absorb, report this as a
`type: technical`, `severity: major` blocker with your own proposed re-scoping (e.g. splitting by
component, or by criterion-type across all 8) — this is an expected, not a failed, outcome for a
task of this shape, mirroring `task-T458.md`'s identical disclosed expectation.

## Inputs

- `docs/artifacts/maturity-promotion-criteria-v1.md` §3.1 (`agent`), §3.2 (`command`), §3.4
  (`skill`), §3.5 (shared defect check) — the real criteria this task must satisfy, verbatim
- `docs/decisions/ADR-006-gate-g2-routing-target-classes-interpretation.md`
- `implementation/scripts/check-maturity.py` (T432 — the real verifier; run it, don't guess at
  whether a promotion would pass)
- `tests/golden/**` (READ-ONLY reference — to check existing coverage before assuming a new case is
  needed; e.g. golden cases already exist referencing `/code-review` and `/plan` command surfaces —
  check whether any already structurally qualify under §3.2 criterion 4 before authoring new ones)
- `docs/tasks/completed-tasks.md` (for agents' §3.1 criterion 4(iii) fallback — real, attributable
  completed work)

## Expected outputs

1. Real evidence artifacts per component as needed to satisfy each unmet criterion: new/extended
   golden cases (respecting the read-only constraint on `tests/golden/**` below — see Constraints
   for the exception process if a genuinely new case must be added there), `# maturity-evidence:`
   tags added to real functional tests or `expect.py` files, `## Rails` sections with real content
   in each promoted component's own file, `docs/wiki/**` entries documenting each promoted
   component.
2. `maturity: stable` set in each genuinely-qualifying component's frontmatter (not before the
   evidence above exists and is verified).
3. `implementation/registry/{index.json,summary.md}` regenerated via `generate-registry.py` after
   the frontmatter changes.
4. A design/closure artifact (e.g. `docs/artifacts/phase3-wave1-promotion-v1.md`) recording, per
   component: what evidence was already present vs. newly authored, the real
   `check-maturity.py --verbose` output confirming the `stable` claim passes, and your disclosed
   resolution of the `code-review` identifier ambiguity.

## Acceptance criteria

1. Running `python3 implementation/scripts/check-maturity.py --root implementation --verbose`
   after this task's changes shows every genuinely-promoted component passing at `stable` — not
   merely that the frontmatter says `stable` (a promotion whose evidence is fabricated or
   insufficient must show as `FAIL` when actually checked, and must not be shipped as `PASS` by
   construction).
2. Every piece of evidence produced (golden cases, evidence tags, Rails content, wiki entries) is
   real and substantive — not a copy-paste placeholder engineered only to satisfy `check-maturity.py`'s
   own heuristics (mirrors this project's own adversarial-review standard already applied to T432
   itself; expect the orchestrator to adversarially attempt to find a component that passes without
   genuinely satisfying its criteria, the same way T432's own docs-padding gap was found).
3. The `code-review` identifier ambiguity is explicitly resolved and disclosed, not silently picked.
4. No routing-target-class identification, ranking, or Phase-4-style analysis is performed — per
   `ADR-006`, this is explicitly out of scope for this task.
5. `python3 tests/run.py` passes with no regressions.
6. `node implementation/scripts/sync.mjs --root implementation --check` reports no drift.
7. Coding standards and Conventional Commits followed; branch pushed, MR opened against `develop`,
   not self-merged.

## Constraints

- **No paid or recurring-cost API calls.**
- **Do not touch `.mcp.json`, anywhere, for any reason. Do not touch the main checkout
  (`/home/emage/Code/emage/emage.code`).**
- **`tests/golden/**` and `scripts/scorecard.py` are protected paths.** If genuine new golden-case
  authorship is required to satisfy a criterion (e.g. a component with no structural golden
  coverage today), that is expected promotion work per `maturity-promotion-criteria-v1.md`'s own
  framing ("the remaining 14 need cases authored, which is expected promotion work, not a defect")
  — but adding a **new** case under `tests/golden/open/` or `held-out/` is still an edit to a
  protected path and requires an explicit, disclosed exception request to the orchestrator before
  the edit, per `protected-paths-v1.md`'s documented exception process. Do not add golden cases
  unilaterally; report the need and proposed case content as a blocker first. Do not touch
  `docs/benchmarks/tb-subset.json`/`.md` at all.
- **Do not touch `feature/T475-codex-platform-integration`. Do not start T434, T435, or any Phase 4
  work.**
- **Confirm your own tool grant before starting** — re-check `implementation/knowledge/agents/
  tech-lead.md` directly.
- **Work in your own worktree/branch** (`agent/tech-lead/T433`), created from `develop`. Commit as
  you go; run the full test suite before reporting completion. **Do not self-merge** — push and
  open a merge request, then stop.

## Blocker protocol

Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`) +
severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries before
escalating to the orchestrator. Specifically anticipated:

- Scope exceeding one task (see "Scope warning" above) — `type: technical`, `severity: major`,
  with your own proposed re-scoping. Expected, not a failure.
- Needing a new golden case under a protected path — `type: unclear_requirements`, `severity:
  major`, with the proposed case content, per the Constraints section's exception process.
- The `code-review` identifier ambiguity, if you judge it needs orchestrator input rather than your
  own disclosed resolution — `type: unclear_requirements`, `severity: minor`.

## Execution notes

(To be filled in by the implementing agent during work, if useful — not required.)
