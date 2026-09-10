# Task T436 — Honest demotion pass

**ID:** T436
**Owner:** Product Owner (matches `plan-035`/`plan-041`'s own assignment and explicit reasoning —
"a product-priorities call... not a technical one." **Deliberately spelled with its human display
name, not its lowercase-hyphenated registry id, throughout this brief** — this component is one of
Wave 2's 31 already-`stable` promotions; the literal id would trip the same whole-word
self-referential ledger-defect regression T434/T435's briefs found and fixed (a third variant:
the task's own required Owner field colliding with an already-`stable` component, unlike the
"unrelated incidental mention" variant those briefs fixed) — confirmed directly by the
orchestrator, `python3 tests/run.py` genuinely failed with the literal id present, fixed by this
rewrite, re-verified clean before dispatch. **Tool grant checked before dispatch and found to be a
deliberate, documented constraint, not an oversight to route around**: the agent definition file's
registered grant is `[read, search, web, todo]` — no `edit`, no `execute`, the only agent in Phase 3
so far with *neither*. The security-guidelines-topic instruction file's own Agent Permission
Classification section explicitly lists this role as "read-only at all times (can only
approve/reject requirements and priorities)" as a designed security boundary, not a gap (that
instruction file is also now `stable`, per Wave 3 — deliberately not naming its own id here either,
for the same reason). **Disposition: unlike every prior Phase 3 tool-grant gap (T430/T434/T435's
Bash-less `solution-architect` cases), this is NOT resolved by reassigning the whole task to a
write-capable agent — that would lose the real product-judgment intent `plan-041` explicitly calls
for.** Instead: the Product Owner performs the actual judgment/decision phase of this task (fully
achievable with `read`/`search`/`web` — it needs to review, not write); the orchestrator transcribes
its real, reasoned decision into a committed artifact (since it cannot write one itself); if the
decision calls for any component's `maturity:` field or content to actually change, that mechanical
implementation is a small, separate follow-up dispatched to a write-capable agent (the Tech Lead,
matching Phase 3's established owner), executing this task's decision, not making a new one of its
own.)
**Status:** done
**Priority:** P1
**Depends on:** T434 (done), T435 (done) — both required, per `plan-041`'s own note: "needs both
waves' actual promotion outcomes first, since 'cannot reach `stable` in three waves' is only
knowable once T434/T435 both report."
**Blocks:** T437
**Created:** 2026-09-10
**Completed:** 2026-09-10
**Based on:** `docs/plans/plan-041-phase3-maturity-ladder-detailed-planning.md` (approved, merged
MR !252) — specifically its T436 row; `docs/plans/plan-035-roadmap-v7-ground-up.md` §2.4 Phase 3
(T436's original nominal scope: "Demote honestly: anything that cannot reach `stable` in three
waves is marked `experimental` or `deprecated`. An accurate `experimental` label is worth more than
an aspirational `beta` one."); `docs/artifacts/phase3-wave1-promotion-v1.md`,
`phase3-wave2-promotion-v1.md`, `phase3-wave3-promotion-v1.md` (T433-T435's real, itemized findings
— the actual evidence base for this task's judgment, read these directly, do not re-derive or
re-summarize secondhand); `docs/artifacts/maturity-promotion-criteria-v1.md` (T431 — the `## 4.
deprecated` criteria: requires a `## Deprecation Notice` section with `**Reason**` +
`**Replacement**` or `**Removal target**`, mutually exclusive with `experimental`/`beta`/`stable`).

## A framing correction before you start — read this first

`plan-035`'s original T436 description ("mark `experimental` or `deprecated`... an accurate
`experimental` label is worth more than an aspirational `beta` one") was written before T430-T432
existed. **T432's `check-maturity.py` already mechanically prevents the specific failure mode T436
was originally worried about** — no component can falsely claim `beta` or `stable` without
genuinely satisfying T431's real criteria; this has been true and CI-enforced since T432 shipped,
and independently, adversarially verified multiple times across T433-T435. **Every one of the 77
components already carries an accurate label today** — 31 are genuinely `stable`, the remaining 46
are honestly `experimental` (the default, not a failure state). **T436's real remaining question is
narrower than its own original framing suggests: is there anything, among the 46 `experimental`
components, that should be marked `deprecated` instead** — i.e., something with a genuine, identified
dead end (superseded, redundant, or structurally unable to ever satisfy its promotion criteria) —
**or does the honest conclusion turn out to be that nothing currently warrants deprecation**, because
every non-`stable` component's gap is a live, trackable, fixable item (a missing golden case, an
open ledger defect, unattempted evidence work) rather than a genuine dead end? **Do not assume the
answer is "find things to deprecate" — a well-reasoned "nothing qualifies yet, here is why" is an
equally acceptable, honest outcome, and forcing a deprecation to make Phase 3 look complete would be
exactly the "aspirational" dishonesty this task exists to prevent, just in the opposite direction.**

## Objective

Review the real, itemized evidence from T433/T434/T435's closure artifacts — the 19 commands still
at `experimental` (blocked: 14 on a disclosed golden-case coverage gap, 3-5 on tracked golden-suite
defects), the 4 agents blocked on `T456`/`T457`, the 4 skills flagged with real, pre-existing
content defects (`blocker-escalation`, `cost-token-governance`, `dependency-graphing`,
`worktree-isolation`), and the 18 skills genuinely untouched by any wave — and make a real,
reasoned product-priorities judgment: for each category (not necessarily each of the 46 individual
components — group sensibly), does its current gap represent (a) legitimate, honest
`experimental` status with a live path forward (leave as-is, no action), or (b) a genuine dead end
warranting `deprecated` (name specifically which components, and why — what makes it a dead end
rather than "not yet done")?

## Inputs

- `docs/artifacts/phase3-wave1-promotion-v1.md`, `phase3-wave2-promotion-v1.md`,
  `phase3-wave3-promotion-v1.md` — read all three directly, they are the real evidentiary record
- `implementation/registry/summary.md` — current real maturity distribution
- `docs/tasks/completed-tasks.md`, `docs/tasks/active-tasks.md` — for `T456`/`T457`'s real current
  status and any other open items relevant to blocked components
- `docs/artifacts/maturity-promotion-criteria-v1.md` §4 — the real `deprecated` criteria your
  decision must satisfy if you recommend it for anything

## Expected output

**Your response to the orchestrator must contain a clear, itemized decision** (you cannot write a
file yourself — report your full reasoning in your final message, it will be transcribed into a
real, committed artifact by the orchestrator, attributed to your judgment, not paraphrased into
something you didn't actually conclude). For each category of currently-`experimental` component:
state your decision (leave as `experimental` / recommend `deprecated`) and your reasoning, citing
the specific evidence from T433-T435's artifacts that supports it — not generic reasoning. If you
recommend any component for `deprecated`, name it specifically and state what the `## Deprecation
Notice`'s `**Reason**` and `**Replacement**`/`**Removal target**` should say.

## Acceptance criteria

1. Every category of non-`stable` component from T433-T435's findings is explicitly addressed —
   none silently skipped.
2. Any `deprecated` recommendation is grounded in a genuine, cited dead-end finding, not merely
   "hasn't been promoted yet" (which is not a valid deprecation reason on its own — see the framing
   correction above).
3. If the honest conclusion is that nothing currently warrants deprecation, that is stated plainly
   as the decision, with reasoning — not treated as an incomplete or failed task.
4. Reasoning is specific and evidence-cited, not generic ("this seems less important") — mirrors the
   evidentiary rigor every other Phase 3 artifact this session has used.

## Constraints

- **No paid or recurring-cost API calls.**
- **Do not touch `.mcp.json`, anywhere. Do not touch the main checkout
  (`/home/emage/Code/emage/emage.code`).** (Moot for this dispatch specifically — you have no write
  tools — but stated for completeness/consistency with every other Phase 3 brief.)
- **Do not touch `tests/golden/**`, `scripts/scorecard.py`, `docs/benchmarks/tb-subset.json`/`.md`,
  `feature/T475-codex-platform-integration`.**
- This is a judgment task, not an implementation task — you have no `edit`/`execute` tools and are
  not expected to use any; do not attempt to work around this.

## Blocker protocol

Report blockers as: type/severity/mitigation. If you find the evidence in T433-T435's artifacts
insufficient to make a confident call on any specific component or category, say so explicitly
(`type: unclear_requirements`, `severity: minor`) rather than guessing — a stated "insufficient
evidence to decide, here's what's missing" is a valid, honest partial answer for that item.

## Execution notes

(To be filled in — not required for this dispatch shape.)

## Completion addendum (2026-09-10)

Decision: nothing among the 46 non-`stable` components currently warrants `deprecated` — every
category's gap is a live, trackable, fixable item, not a genuine dead end. Full itemized reasoning
in `docs/artifacts/phase3-maturity-demotion-decision-v1.md` and `completed-tasks.md`'s T436 row.
First dispatch attempt correctly refused to fabricate a decision when its assumed `git show`
fetch mechanism failed (no execute tool); redispatched with the real evidence embedded directly,
which worked cleanly. Implemented via MR !272 (dispatch, merge commit `1e0c028`); this closure
commit adds the decision artifact directly (no separate implementation MR, since the deliverable
is a decision record, not code).
