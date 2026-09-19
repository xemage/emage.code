# Artifact: phase3-wave1-promotion-v1.md

> Filename: `phase3-wave1-promotion-v1.md`. Immutable once produced; revisions bump `<N>`.

## Metadata
- **Producer agent**: tech-lead
- **Task**: T433
- **Created**: 2026-09-10
- **Based on**: `docs/tasks/task-T433.md`; `docs/decisions/ADR-006-gate-g2-routing-target-classes-interpretation.md`;
  `docs/artifacts/maturity-promotion-criteria-v1.md` (T431 — the real per-category `beta→stable`
  criteria this task must satisfy, verbatim); `docs/artifacts/maturity-levels-v1.md` (T430);
  `implementation/scripts/check-maturity.py` (T432 — the real verifier this artifact's every claim
  is checked against directly, not estimated).
- **Supersedes**: none (first version)

## Body

### 0. Outcome summary — read this first

**Zero of the 9 candidate artifacts (8 named components, `code-review` counted twice per the
disclosed ambiguity resolution below) are promoted to `maturity: stable` in this MR.** Every
component's frontmatter is unchanged at `maturity: experimental`. This is not a failure to do the
promotion work — the promotion *evidence* (Rails sections, evidence tags + real tests, dedicated
wiki documentation, cross-references) was genuinely authored for all 9 and is real, substantive,
and independently verified against `check-maturity.py` (§2 below). It is a disclosed, empirically-
proven finding that **no commit this agent can produce, while `T433` itself remains an open ledger
row, can make `check-maturity.py` report `PASS` for any of the 9 claimed-`stable` components** —
and that, independent of that first blocker, **5 of the 9 have their own, separate, real defects**
that will keep blocking them even after the first blocker is resolved. Both are reported as
blockers in §4, with proposed mitigations. See §1 for the disclosed `code-review` resolution, §2
for the real evidence and verifier output per component, §3 for the two blockers' full mechanics
and proof.

### 1. `code-review` identifier ambiguity — disclosed resolution

`code-review` exists as both a `skill` id (`implementation/knowledge/skills/code-review/SKILL.md`)
and a `command` id (`implementation/knowledge/commands/code-review.md`), with no textual basis in
`plan-035` to prefer one. **Resolution: both are treated as in-scope and both received full,
genuine promotion evidence.** Reasoning: "the 8 highest-traffic components" plausibly refers to the
*code-review workflow* as a whole, not one specific artifact type, and the two are tightly coupled
(the command is the invocable surface for the skill's own checklist and verdict format — see
`docs/wiki/commands-and-skills-overview.md`). Treating both as candidates is the more conservative
reading (produces strictly more real evidence, narrows nothing) and is one of the three resolutions
`task-T433.md` itself lists as acceptable. This is disclosed here and in the completion report, not
silently picked.

### 2. Evidence produced per component, and the real verifier's per-component result

All entries below reflect `python3 implementation/scripts/check-maturity.py --root implementation
--verbose`, run for real, against the actual state committed in this branch. In that real,
committed state, `maturity:` is `experimental` for all 9 (§0), so every one of them reports `PASS`
(they only need to satisfy `experimental`'s own bar, which requires nothing beyond a schema-valid
declaration — no `## Rails`, no evidence, is required to justify staying at `experimental`).
**The evidence below is what has been verified, via a separate, uncommitted, before/after
simulation (§3.1), to make `experimental->beta` and `beta->stable` criteria 1/2/4/5/6 pass for
every one of the 9** — i.e., it proves the evidence itself is sufficient, isolating that question
from the two ledger/defect blockers in §3, which are independent of evidence quality.

| Component | Category | Rails added | Evidence (criterion a/4) | Cross-ref/referenced (criterion c/5) | Documented (criterion d/6) |
|---|---|---|---|---|---|
| `orchestrator` | agent | New — Inputs/Out of scope/Failure mode | Already existing: owns `/plan` (`plan-required-sections-compliant` etc.) | Already existing: `agents-overview.md` + owns multiple commands | Already existing: `agents-overview.md` row |
| `tech-lead` | agent | New | Already existing: owns `/code-review` | Already existing | Already existing |
| `backend-developer` | agent | New | Already existing: `completed-tasks.md` rows with MR refs (e.g. T049 `!23`, T212 `!42`) | Already existing: `@backend-developer` mention in `orchestrator.md` Phase 3 | Already existing: `agents-overview.md` row |
| `qa-engineer` | agent | New | Already existing: `completed-tasks.md` rows with MR refs (e.g. T305 `MR !91`) | Already existing: `@qa-engineer` mention in `orchestrator.md` Phase 4 | Already existing: `agents-overview.md` row |
| `security-engineer` | agent | New | Already existing: owns `/security-audit` | Already existing: owns `/security-audit`, `agents-overview.md` | Already existing |
| `validation-gates` | skill | New | **Newly authored**: `tests/functional/test_validation_gates_skill_contract.py` (`# maturity-evidence: skill/validation-gates`) | Already existing: `AGENTS.md` Skill Workflow table | **Newly authored**: `docs/wiki/commands-and-skills-overview.md` |
| `code-review` | skill | New | **Newly authored**: `tests/functional/test_code_review_skill_contract.py` (`# maturity-evidence: skill/code-review`) | **Newly authored**: `skill \`code-review\`` mention added to `tech-lead.md`'s Code Review section | **Newly authored**: `docs/wiki/commands-and-skills-overview.md` |
| `plan` | command | New | Already existing: `plan-required-sections-compliant` etc. | Already existing: `agent: "orchestrator"` frontmatter | Already existing (incidental `cline-setup.md` "Plan mode" line — real prose, not engineered) |
| `code-review` | command | New | Already existing: `code-review-fail-blocker-details` etc. | Already existing: `agent: "tech-lead"` frontmatter | **Newly authored**: `docs/wiki/commands-and-skills-overview.md` |

New test files (`tests/functional/test_validation_gates_skill_contract.py`,
`tests/functional/test_code_review_skill_contract.py`) make real, substantive assertions —
cross-consistency checks between each skill's documented contract and the rest of the knowledge
base (e.g., every named gate executor in `validation-gates`' Gate Types table must resolve to a
real registered agent id; the `code-review` skill's severity guide and VERDICT vocabulary must
match `tech-lead.md`'s and `commands/code-review.md`'s own sections) — not placeholder assertions
engineered only to contain the required tag string. Both files pass on their own (`pytest
tests/functional/test_validation_gates_skill_contract.py tests/functional/test_code_review_skill_contract.py`
→ 5 passed).

`docs/wiki/commands-and-skills-overview.md` is a new, dedicated overview page (mirroring
`agents-overview.md`'s existing pattern) documenting `/plan`, `/code-review`, `validation-gates`,
and `code-review` with real, multi-sentence descriptions — not a single padded line engineered to
clear `check-maturity.py`'s `_looks_like_real_description()` heuristic (the exact gaming pattern
T432's own adversarial review already found and closed once; this artifact deliberately does not
retry it).

### 3. The two independent blockers (full mechanics)

#### 3.1 Blocker A — T433's own open ledger row makes `check-maturity.py` unsatisfiable for any of its own claimed promotions, by construction

`maturity-promotion-criteria-v1.md` §3.5's shared defect-check definition counts, as an "open
P0/P1 defect against `<category>/<id>`," any row in `docs/tasks/active-tasks.md` with `Priority` ∈
`{P0, P1}` and `Status` not `done`/`cancelled`, **whose linked `docs/tasks/task-<ID>.md` body
mentions `<id>` as a whole word** — with no distinction between "this task reports a defect in
`<id>`" and "this task's own subject matter is `<id>`" (e.g., a promotion task for `<id>` that must,
to describe its own scope, name `<id>`).

`task-T433.md` (P0, `in_progress`, the only status this task can honestly carry while an agent
without archival authority is actively working it) necessarily and correctly names all 9 candidate
identifiers in its own body (`orchestrator`, `tech-lead`, `backend-developer`, `qa-engineer`,
`security-engineer`, `validation-gates`, `plan`, `code-review`) — it is the task that defines them
as its own subject. Verified directly (not estimated):

```
$ python3 -c "
import re
text = open('docs/tasks/task-T433.md', encoding='utf-8').read()
def mentions(t, ident):
    return re.search(r'(?<![\w-])' + re.escape(ident) + r'(?![\w-])', t) is not None
for ident in ['orchestrator','tech-lead','backend-developer','qa-engineer',
              'security-engineer','validation-gates','plan','code-review']:
    print(ident, mentions(text, ident))
"
orchestrator True
tech-lead True
backend-developer True
qa-engineer True
security-engineer True
validation-gates True
plan True
code-review True
```

Empirically confirmed against the real checker (single-component reproduction, `orchestrator` given
a real `## Rails` section and `maturity: stable`, everything else unchanged):

```
FAIL agent/orchestrator claims stable:
  - experimental->beta #3 (no open P0 defect): open P0 task T433 names it in its brief
  - beta->stable #7 (no open P0 or P1 defect): open P0 task T433 names it in its brief
```

**This is not fixable by producing more or better evidence** — it is a structural property of
`check-maturity.py`'s own text-matching defect check interacting with the task ledger's lifecycle,
independent of evidence quality. It also cannot be fixed by this agent directly: `AGENTS.md`'s Task
Protocol states plainly "Only orchestrators create/transition tasks... Archival is orchestrator-only
and immediate" — moving `T433`'s own row from `active-tasks.md` to `completed-tasks.md` is outside
this agent's authority, and self-archiving one's own P0 task would itself violate the same
check-and-balance the invariant exists to enforce.

**Proof the blocker resolves cleanly once `T433` archives, with zero further evidence work**,
performed via an uncommitted, uncomitted-to-git, disposable full-worktree copy (never part of any
commit in this branch — reverted/deleted immediately after each check): with `T433`'s row removed
from `active-tasks.md` (simulating its closure) and all 9 components' frontmatter flipped to
`maturity: stable`, `qa-engineer` (agent), `code-review` (skill), and `validation-gates` (skill)
report a clean `PASS` — no further evidence gap of any kind. The other 6 candidates do **not**
cleanly resolve even after this simulated archival — see Blocker B.

#### 3.2 Blocker B — 5 (soon 6, see below) of the 9 candidates have their own, independent, real defects unrelated to T433

With Blocker A's condition simulated away (§3.1), the real verifier surfaces genuine, pre-existing
issues that were previously invisible only because Blocker A's failure reason was returned first
and masked them:

| Component | Real, independent blocker | Nature |
|---|---|---|
| `command/plan` | `golden case plan-real-doc-header-drift is a known_failing tracked_defect for /plan` | **Real product defect.** This golden case (`status: known_failing`, `known_failing_category: tracked_defect`) documents that real historical plan docs use different section headers than `commands/plan.md` step 5 declares. Genuinely unresolved. |
| `command/code-review` | a held-out golden case is a `known_failing`/`tracked_defect` case for `/code-review` (case ID deliberately not quoted here — it lives under `tests/golden/held-out/`, and this artifact sits outside that directory, per `tests/functional/test_golden_held_out_isolation.py`'s own held-out-isolation guard, the same convention `maturity-promotion-criteria-v1.md` already follows) | **Real product defect.** Real historical review docs use a different VERDICT format than `commands/code-review.md` declares. Genuinely unresolved. |
| `agent/tech-lead` | same `/code-review` tracked defect (agents inherit their owned commands' defect status per §3.5) | Same real defect, inherited. |
| `agent/orchestrator` | same defect mechanism via `/plan`, plus tracked defects on `/new-feature` and `/prepare-release` (both also orchestrator-owned) | **3 independent real defects**, any one of which alone would block this agent. |
| `agent/security-engineer` | `golden case security-audit-critical-not-fail is a known_failing tracked_defect for /security-audit`, **plus** `open P1 task T457 names it in its Title` | The golden-case defect is real (an OWASP-rule violation in a fixture). The `T457` hit is **also a genuine, already-disclosed defect**, not a false positive: `T457`'s own title names `@security-engineer` because it tracks a real tool-grant overclaim (`security-engineer.md`'s "read-only mode" is prose-only, not technically enforced — see `completed-tasks.md`'s T454 closure addendum). |
| `agent/backend-developer` | `open P1 task T457 names it in its brief` | **False positive**, checked directly: `task-T457.md`'s only `backend-developer` mention is "`and/or `backend-developer`` for the scoped-tool mechanism itself — to be assigned once the design [is made]" — a forward-looking possible-assignee note, not a defect report against `backend-developer`. Same class of mechanical over-match as Blocker A, just against a different, longer-lived open task. Does **not** resolve when `T433` archives. |

Net effect: **only 3 of the 9 candidates (`qa-engineer`, `validation-gates` skill, `code-review`
skill) are genuinely, fully evidence-complete and blocked solely by Blocker A.** The other 6 need
either a real defect fixed (verdict/header-format drift in `commands/plan.md` /
`commands/code-review.md` against real historical usage, or `security-engineer.md`'s tool-scoping
prose-vs-enforcement gap already tracked at `T457`) or `T457`'s own resolution (for
`backend-developer`'s false-positive mention) before they can honestly reach `stable` — none of
which is in scope for a maturity-promotion task per `maturity-promotion-criteria-v1.md`'s own
design (the P0/P1-defect gate exists specifically to prevent promoting components with known,
unresolved defects to `stable`).

### 4. Blockers filed

**Blocker 1 — type: `technical`, severity: `major`.** `check-maturity.py`'s defect-check
(`maturity-promotion-criteria-v1.md` §3.5) cannot be satisfied, for any component, by a commit
authored while the promoting task's own ledger row remains open and P0/P1, because the task's own
brief must name the components it promotes. Proposed mitigation: once this MR is reviewed and
ready, the orchestrator archives `T433` (moves its row to `completed-tasks.md`) as part of, or
immediately after, merging it; a small, immediate follow-up (a few `maturity: stable` field flips —
no new evidence needed) then genuinely promotes `qa-engineer`, `validation-gates` (skill), and
`code-review` (skill), with `check-maturity.py --verbose` re-run to confirm real `PASS` at that
point. This artifact and the evidence in §2 are ready for that follow-up to consume directly.

**Blocker 2 — type: `technical`, severity: `major`.** 6 of the 9 candidates have real, independent,
pre-existing defects (§3.2) that will continue to block `stable` promotion even after Blocker 1
resolves. Proposed mitigation: these are product-defect-resolution tasks, not promotion-evidence
tasks, and are out of this task's scope per `maturity-promotion-criteria-v1.md`'s own design.
Recommend three follow-up tasks (or one task per defect, at the orchestrator's discretion): (a) fix
`commands/plan.md` / real plan docs' header drift (or reconcile the declared contract with real
usage) and resolve the open-bucket `plan-real-doc-header-drift` tracked defect; (b) fix
`commands/code-review.md` / real review docs' verdict-format drift and resolve the held-out-bucket
`/code-review` tracked defect described in §3.2's table (case ID intentionally not repeated here,
per the held-out-isolation convention); (c) resolve `T457` (security-engineer/context-retriever
tool-scoping gap) and, once resolved, re-check whether its now-closed status also clears
`backend-developer`'s incidental mention. `security-audit`'s `security-audit-critical-not-fail`
tracked defect (open bucket) is a fourth, separate real defect (OWASP-rule compensating-control
handling) not previously named in any open follow-up task found during this review — flagging it
here since it was not visible until Blocker 1 was simulated away.

### 5. Consumed by

- **Orchestrator** — to archive `T433` and dispatch the two blockers above as new tasks, per
  Blocker 1/2's proposed mitigations.
- **A future, small follow-up task** (post-`T433`-archival) — flips `maturity: stable` for
  `qa-engineer`, `validation-gates`, and `code-review` (skill) only, using the evidence already
  authored in this MR, and re-confirms via `check-maturity.py --verbose`.
- **T434/T435 (Wave 2/3)** — should read this artifact's §3 before assuming any component's
  ledger-defect check will pass cleanly; the same two blocker classes apply to any future wave.
