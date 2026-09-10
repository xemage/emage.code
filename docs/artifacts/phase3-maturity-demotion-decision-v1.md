# Artifact: phase3-maturity-demotion-decision-v1.md

> Filename: `phase3-maturity-demotion-decision-v1.md`. Immutable once produced; revisions bump `<N>`.

## Metadata
- **Producer agent**: Product Owner (decision); transcribed into this committed artifact by the
  orchestrator, since Product Owner's real tool grant (`[read, search, web, todo]`) has neither
  `edit` nor `execute` — a deliberate security boundary per `implementation/knowledge/instructions/
  security-guidelines.md`'s Agent Permission Classification, not an oversight. This artifact
  reproduces the Product Owner's actual reasoning as delivered, not a paraphrase.
- **Task**: T436
- **Created**: 2026-09-10
- **Based on**: `docs/tasks/task-T436.md`; `docs/artifacts/phase3-wave1-promotion-v1.md`,
  `phase3-wave2-promotion-v1.md`, `phase3-wave3-promotion-v1.md` (T433-T435 — the evidentiary
  record this decision is grounded in); `docs/artifacts/maturity-promotion-criteria-v1.md` §4 (the
  real `deprecated` criteria); `docs/tasks/active-tasks.md` (T456/T457/T458's real current status);
  `AGENTS.md` (Blocker Protocol severities, task ledger schema — cited directly by the decision
  below, independently verified accurate by the orchestrator before this artifact was committed).
- **Supersedes**: none (first version)

## Body

### Overall decision (stated up front, matching the task brief's own framing)

**Nothing among the 46 `experimental` components currently warrants `deprecated`.** Every gap
surfaced by Waves 1-3 is a live, trackable, fixable item with either a concrete proposed
remediation path, an already-open ledger task, or simply an absence of survey — none is a genuine
dead end (superseded, redundant, or structurally incapable of ever meeting its promotion criteria,
per `maturity-promotion-criteria-v1.md` §4). Forcing a deprecation here to make Phase 3 look
"complete" would reproduce the exact aspirational-labeling problem T436 exists to prevent, just
pointed the other direction — this is treated as an equally valid, and here the correct, outcome,
not an incomplete task.

### Category 1: 14 commands blocked solely on golden-case coverage gap

`batch`, `bug-report`, `consolidate-memory`, `discover-skills`, `evaluate-poc`, `handoff`,
`new-poc`, `new-project`, `poc-demo`, `skillify` (command), `sprint-status`, `team-status`,
`validate-tasks`, `validate-workflow`

**Decision: leave `experimental`. No deprecation.**

**Reasoning:** Per Wave 2 (`phase3-wave2-promotion-v1.md`), for all 14, Rails/agent-resolution/wiki
documentation are already evidence-complete; the sole remaining gap is zero `tests/golden/**`
coverage, and the reason is procedural (golden is a protected path requiring an explicit exception
request T434's scope did not make), not a discovered defect in the commands themselves. Wave 2's
own authors already proposed a concrete three-step remediation (request the exception, author 14
representative cases with the same review rigor as the existing 5-command suite, re-run
`check-maturity.py --verbose`). A category whose own finding already carries a scoped remediation
plan is definitionally a live path forward, not a dead end.

### Category 2: 3 commands blocked on tracked golden-suite defects

`new-feature`, `prepare-release`, `security-audit`

**Decision: leave `experimental`. No deprecation.**

**Reasoning:** These already have golden coverage; the blocker is a verdict-format/header drift
between what the command declares and what historical usage shows. This is not a novel problem —
Wave 1 found the identical failure pattern for two other commands and explicitly recommended them
"as follow-up candidates, not as deprecation candidates," direct precedent within this same Phase 3
body of work. A format/documentation drift defect is a correction task, not evidence the underlying
capability (e.g. `security-audit`, still clearly needed per `AGENTS.md`'s own OWASP/security-review
workflow) is obsolete or redundant.

### Category 3: 4 agents blocked on T456/T457

`context-retriever`, `devops-engineer`, `evaluation-agent`, `solution-architect`

**Decision: leave `experimental`. No deprecation.** The least ambiguous category in this review.

**Reasoning:** These four are already evidence-complete — Wave 2 states the blocker is "a genuine
infrastructure gap, not a defect in any specific agent." Confirmed against `active-tasks.md`: T456
(P0, owner `evaluation-agent`) is blocked only on T458 (pending, P1, `devops-engineer`) reaching
done; T457 (P1, owner `solution-architect`) is pending, not yet dispatched — both real, actively
tracked, P0/P1 rows with named owners, the maximum degree of "live path forward" evidence available
in this system. `context-retriever`/`solution-architect`/`devops-engineer` are flagged only because
T456/T457's own briefs name them as scope/assignees — an artifact of the ledger-defect check's
mechanism, not a finding about those agents' quality. Deprecating any of these four foundational
roles (architecture, devops, evaluation, context-retrieval) on the basis of an unresolved
infrastructure-sequencing dependency would itself be a product-priorities error.

### Category 4: 4 skills with real, pre-existing content defects

`blocker-escalation`, `cost-token-governance`, `dependency-graphing`, `worktree-isolation`

**Decision: leave all 4 `experimental`. No deprecation.**

**Reasoning, per skill:**
- **`blocker-escalation`** — severity vocabulary mismatch against `AGENTS.md`'s own Blocker
  Protocol (`critical`/`major`/`minor`, independently verified present in `AGENTS.md` line 48). A
  document-reconciliation fix, not evidence the subject matter is obsolete — `AGENTS.md` itself
  still mandates a Blocker Protocol today.
- **`cost-token-governance`** — an internal budget-table mismatch within the skill's own document
  (not even cross-document) — the narrowest possible defect, a self-consistency edit. Token
  governance remains an active concern per `AGENTS.md`'s own Token Governance table.
- **`dependency-graphing`** — assumes `Blocks`/`BlockedBy` ledger columns that do not exist in the
  real `active-tasks.md` schema (independently verified: the real schema is `ID | Title | Owner |
  Status | Priority | Depends on | Last update` — `Depends on` only). A spec/implementation
  mismatch with two available fixes (rewrite the skill to derive graphs from `Depends on`, or
  extend the ledger schema) — flagged as needing an explicit "which side do we fix" scoping
  decision in a follow-up, not a deprecation trigger; the underlying need (visualizing task
  dependencies) is not dead.
- **`worktree-isolation`** — documents a direct-merge-to-`main` procedure that contradicts
  `git-workflow.md` (now `stable`, promoted in this same Wave 3 pass), which explicitly forbids
  direct commits to `main`/`develop` and documents a recovery procedure for two real historical
  incidents of exactly this mistake. **Considered the strongest deprecation candidate of the four**
  — explicitly weighed and rejected: the evidence names one specific contradictory clause (the
  merge step), not a finding that the skill's entire content (worktree creation, parallel-agent
  isolation, cleanup) is redundant with `git-workflow.md`. Recommending deprecation would require
  asserting the whole skill is subsumed, which the evidence doesn't support — only that one
  procedure section needs correcting to reference the real branch-to-MR-to-review-to-merge flow.

All four match Wave 3's own characterization: "real, pre-existing content defects found
incidentally while surveying candidates," recommended to "be fixed (a separate, non-promotion
task) before a future wave attempts their promotion evidence" — treated by Wave 3's own authors as
correctable, not terminal, and concurred with here based on the evidence.

### Category 5: 14 genuinely untouched skills

`api-design`, `ci-cd-pipeline`, `context-window-management`, `cwso-awareness`,
`gitlab-management`, `memory-management`, `plan-approve-execute`, `poc-evaluation`,
`project-planning`, `rapid-prototyping`, `release-workflow`, `skillify` (skill, distinct from the
command of the same name), `technical-debt-tracking`, `technology-scouting`

**Decision: leave all 14 `experimental`. No deprecation.**

**Reasoning:** Per Wave 3, these are "genuinely untouched — no evidence collected either way, no
defects found, simply not yet surveyed by any wave due to time/scope limits, not because anything
is wrong with them." The clearest possible case against deprecation: zero negative evidence exists.
Deprecating on an absence of survey would be the purest form of the aspirational-dishonesty-in-
reverse the task brief explicitly warns against.

### Summary table

| Category | Components | Decision | Basis |
|---|---|---|---|
| Commands — golden-case gap | 14 | Leave `experimental` | Procedural scope gap, not a defect; Wave 2 has a concrete remediation plan |
| Commands — tracked format defect | 3 (`new-feature`, `prepare-release`, `security-audit`) | Leave `experimental` | Identical pattern already precedented as fixable by Wave 1 |
| Agents — T456/T457 blocked | 4 (`context-retriever`, `devops-engineer`, `evaluation-agent`, `solution-architect`) | Leave `experimental` | Already evidence-complete; blocked by actively tracked, owned ledger tasks, not agent quality |
| Skills — content defects | 4 (`blocker-escalation`, `cost-token-governance`, `dependency-graphing`, `worktree-isolation`) | Leave `experimental` | Each a scoped, self-contained content correction; none shown redundant in full |
| Skills — unsurveyed | 14 | Leave `experimental` | Zero evidence of any kind, positive or negative |

**No `## Deprecation Notice` is recommended for any component in this pass.**

### Recommended follow-up items surfaced during this review (not T436's to schedule)

1. The `tests/golden` protected-path exception request + 14-case authoring effort Wave 2 already
   scoped.
2. The format-drift fix for the 3 Wave-1/Wave-2-precedented commands.
3. A consolidated content-correction pass for the 4 flagged skills, including an explicit
   schema-vs-skill decision for `dependency-graphing`.
4. No action needed for the 14 unsurveyed skills beyond a future wave's normal cadence.

None of these are opened as new tasks by this decision — flagged for future prioritization.

### Orchestrator's independent verification before committing this artifact

Not accepted on the Product Owner's self-report alone: independently grepped `AGENTS.md` for the
two specific factual citations the decision relies on (`critical`/`major`/`minor` severities;
`active-tasks.md`'s real column schema, `Depends on` only, no `Blocks`/`BlockedBy`) — both
confirmed accurate, exact matches. Confirmed the decision engaged critically with its own strongest
candidate case (`worktree-isolation`) rather than uniformly waving every component through with
generic reasoning — it was explicitly named as "the strongest deprecation candidate" and rejected
for a specific, evidence-grounded reason (a partial defect, not a finding of total redundancy), not
dismissed by default. No file changes result from this decision — no follow-up technical dispatch
is required this round.
