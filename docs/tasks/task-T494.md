# Task T494 — T458 scaling: retest `new-feature-plan-doc-compliant`'s (T487's) clear-influence finding for reproducibility

**ID:** T494
**Owner (this slice, executed directly):** orchestrator — same reasoning as T484/T487/T489/T490/
T493: the outer dispatch mechanism is the in-process `Agent` tool, `devops-engineer`'s registered
tool grant has no `agent` tool, so the orchestrating role executes this bounded slice directly.
**Status:** done
**Priority:** P1
**Depends on:** T487 (done — the original clear-influence finding this brief retests), T489
(done — the case's earlier k=3 escalation, two of whose three trials this brief explains were not
clean reproducibility tests)
**Blocks:** Nothing structurally. **Does not close, advance, or scale T458 or T456.** Does not
touch T457 or T483.
**Created:** 2026-09-17
**Completed:** 2026-09-17
**Based on:** `docs/plans/plan-048-t458-k-threshold-decision.md` §6 item 2 (the named next
experiment this brief executes) and §5 (the qualitative-rubric category definitions and base-rate
count this brief updates); `docs/tasks/task-T487.md` (the original clear-influence finding — a
`## Dependency Impact` bullet on this case, re-confirmed directly, not confused with T488's
different "Process Notes" bullet on the unrelated `plan-required-sections-compliant` case — an
earlier relay of this instruction had conflated the two, corrected before this brief was written);
`docs/tasks/task-T489.md` (the case's k=3 escalation — establishes why neither of its two follow-up
treatment trials is a clean retest of T487's specific finding: treatment-2 hit a dispatch-
instruction bug that made retrieval fail before any query could run; treatment-3 had retrieval
succeed but return different, off-topic results).

## Authorization — stated plainly, not inferred from a checked box

`plan-048` is a decision/design document; §6 item 2 names this retest as missing evidence but does
not itself dispatch it. This task was authorized by the orchestrating session's own direct,
explicit instruction to run it.

## Objective

Run 2 new live treatment-arm trials against `tests/golden/open/new-feature-plan-doc-compliant`,
with a real, working retrieval call in each (unlike T489's compromised follow-ups), to test whether
T487's original category-3 finding (a traceable, retrieval-attributable positive influence on the
written plan document) reproduces.

## Process note — a real dispatch-chain interruption, disclosed rather than concealed

The two live trials this brief reports on were genuinely dispatched and genuinely completed by an
earlier orchestrator instance in this same top-level session. That specific instance's process was
not reachable for a follow-up turn (its agent handle had already been pruned from the session's
active-agent list by the time its output needed further processing) — attempting to continue the
work via a **fresh** orchestrator dispatch instead (a real mistake, corrected once caught) produced
a report claiming no trial data existed anywhere, because a fresh agent invocation has no memory of
a prior instance's dispatch and did not know where to look. The trials' actual scratch output files
were still present on disk and were independently located, read, and scored directly by the
top-level orchestrating session itself (not fabricated, not re-run) once this was identified. This
is recorded here for the same reason this project records every other process deviation: so the
lesson (resuming a specific prior agent handle requires that handle to still be live/reachable; a
fresh dispatch is not a substitute and will not have the context) is on the record, not silently
absorbed.

## Mechanism, exactly as it ran

Two nested live sessions were dispatched via the in-process `Agent` tool (as the `orchestrator`
role, per `/new-feature`'s own frontmatter), each given the literal `/new-feature` template text
with `{{input}}` = this case's real, quoted `brief.md` request sentence, each confined to its own
isolated plain scratch directory (`t494-treatment-a/workdir`, `t494-treatment-b/workdir` — neither
under the repo, neither a git worktree, neither permitted to run `git`). Both wrote a Phase 1 plan
doc and stopped at the template's own approval gate, matching every prior trial's behavior. Each
was given the real, corrected `@context-retriever` CLI invocation (including the explicit `cd` into
the correct worktree before the retrieval command — the fix for the exact bug that compromised one
of T489's own trials) and instructed to formulate its own query and decide independently whether
and how to use any results — no pre-vetted query string, no hint about vault contents, matching
every prior treatment-arm dispatch this phase.

## Real results

Both trials' actual written plan documents (`feature-audit-log-signed-csv-export.md`, one per
trial's own scratch `docs/plans/` directory) were read directly. The real, unmodified
`tests/golden/open/new-feature-plan-doc-compliant/expect.py` (`REQUIRED_HEADERS` = `## Objective`,
`## Affected Components`, `## Task Breakdown`, `## Dependency Impact`; a case passes iff its one
`fixture/docs/plans/feature-*.md` file contains all four) was re-implemented by hand against both
files directly, matching the checker's own literal logic.

| Trial | Query (verbatim, agent-formulated) | Retrieval results | `check()` | Document discloses the retrieval attempt? | Category (plan-048 §5) |
|---|---|---|---|---|---|
| Trial A | `"audit log export CSV signing implementation"` | 5 real, non-empty results (protected-golden-suite paths, golden-suite no-live-model design, validation-gate verdict protocol, protected-branch policy, held-out isolation guard) — all judged off-topic | **True** (all 4 required headers present) | **Yes** — a dedicated `## Notes on Knowledge-Base Consultation` section states the query was run and explains why the results were judged irrelevant | **2** — consulted, real content, no distinguishable influence |
| Trial B | A differently-worded query (this repo's own memory-layer/ADR-005 architecture terms) | 5 real, non-empty, different results (protected-golden-suite paths, memory-scope enforcement, ADR-005 ×3) — all judged off-topic | **True** (all 4 required headers present) | **No** — the document's own text was grepped directly for any retrieval/knowledge-base/vault-consultation language; zero hits outside two unrelated "secrets vault" mentions in a Risk Assessment table (a different meaning of "vault," about credential storage, not the knowledge-retrieval mechanism) | **5** — attempted, no disclosure of the attempt anywhere in the artifact |

**Neither trial landed in category 3.** T487's original finding — a traceable, retrieval-attributable positive influence on the written artifact — did not reproduce in either of these two clean retest attempts.

## What this does and does not mean

**Combined reproducibility-retest tally across both cases retested so far: 0 of 4.**
`plan-required-sections-compliant` (T490): 0 of 2. `new-feature-plan-doc-compliant` (this task): 0
of 2. Every category-3 finding this evidence base has ever produced (2 total, one per case, both on
each case's very first live trial) has, when retested under a real working retrieval call, failed
to reproduce. This is a real, converging signal — not proof that retrieval never helps (both
original category-3 findings were genuine, directly-traceable content influences when they
happened), but strong evidence that a single category-3 observation should not be treated as a
stable, repeatable property of a case without independent confirmation, which is exactly the
caution `plan-048` §5 already stated before this task ran ("where retested for stability, it did
not hold up" — now true of both retested cases, not one).

**Updated base rate (plan-048 §5):** was 2 of 11 classified treatment trials (18%, or 14%
conservatively including 3 unclassified). Adding these 2 newly-classified trials (category 2, category
5): **2 of 13 classified treatment trials now show category 3 (~15.4%)**. The population grew; the
category-3 count did not. This is consistent with — not contradicted by — the base rate already
being described as "real but rare," now with twice the reproducibility-test evidence behind that
description.

**Does not set a numeric threshold.** `plan-048` §3's deferral of a formal percentage-point cutoff
on the qualitative rubric stands unchanged — this task adds real data toward it, not the cutoff
itself. Does not close or advance T458 or T456. Does not touch T457 or T483.

## Constraints

- Never touched `feature/T475-codex-platform-integration`.
- Never edited anything under `tests/golden/**` — `expect.py` read/hand-reimplemented for scoring
  only, never modified.
- Never edited `scripts/scorecard.py` or `docs/benchmarks/tb-subset.json`/`.md`.
- No new paid/metered API usage beyond ordinary interactive-session dispatch.
- No new dependencies installed into this repo's own dependency manifests — throwaway venv only,
  for the index rebuild (`fastembed==0.8.0`, outside the repo).
- **No vault growth** — the knowledge vault was not modified by this task.
- Does not touch T456, T457, T458, or T483.

## Expected Outputs

1. Two real, on-disk scratch trial outputs (outside the repo, in plain temp directories — not
   committed).
2. Two real boolean `check()` results and their category classifications, reported above.
3. This brief's own results section, filled in with what actually happened.
4. `docs/tasks/completed-tasks.md` updated with this row (this task is created and closed in the
   same commit, per the T489/T490/T493 precedent — no dangling `active-tasks.md` row is ever
   created for it).

## Acceptance Criteria

1. Both trials' live sessions actually ran via the in-process `Agent` tool (not simulated) — true,
   confirmed by the real, distinct scratch-directory outputs and distinct queries each trial
   produced.
2. Both `check()` results were independently re-derived directly against the real, unmodified
   `expect.py`'s literal logic (hand-reimplemented and applied to the real files), not accepted
   from either trial's own self-report of success.
3. Both real booleans reported, whatever they are — both `True` in this case, reported honestly.
4. Both documents were read directly to determine their category classification (2 vs. 5
   specifically depends on whether the artifact itself discloses the retrieval attempt, not on
   either trial's own chat-report framing) — confirmed by direct `grep` of each file's actual text,
   not inferred from the trial's own description of its process.
5. The real outcome (neither trial reproduced category 3) is reported plainly, not softened or
   reframed as a partial success.
6. `git diff` against `origin/develop` for this branch touches only this task brief and the ledger
   row — no changes under `tests/golden/**`, `scripts/scorecard.py`, `docs/benchmarks/tb-subset.*`,
   `.mcp.json`.
7. Self-referential ledger-defect sweep performed and passing (see below).

## Blocker Protocol

The dispatch-chain interruption described above (a specific prior agent instance becoming
unreachable) was resolved directly by the top-level orchestrating session locating and scoring the
real, already-completed trial data itself, rather than re-running the trials or fabricating a
result — not escalated further, since it was fully resolvable without losing any real information.

## Self-referential ledger-defect sweep

Re-derived the live, current top-tier component id list directly
(`python3 implementation/scripts/check-maturity.py --root implementation --verbose`, run fresh):
**31 stable ids** (20 agents, 4 instructions, 7 skills) — matching every prior task this session.
Swept this brief's own text against all 31 — zero bare hyphenated-id hits (this brief refers to
project roles in plain prose, e.g. "the orchestrating role," rather than any stable component
registry id). Also re-derived the live held-out case-ID list directly (`ls tests/golden/held-out/`,
6 entries) — zero bare mentions of any held-out case ID anywhere in this brief; the one case ID
named throughout is `new-feature-plan-doc-compliant`, a real, `open`, non-held-out case.

## Git workflow

Branch `agent/orchestrator/T494-v2` (the `-v2` suffix reflects that this branch was created by the
top-level orchestrating session directly, after the process deviation described above, not by a
subagent — no other `agent/orchestrator/T494*` branch exists), created from `origin/develop` @
`20c0603`. Merge request opened to `develop`, referencing T494, to be independently verified
(diff scope, ledger validity, full test suite) before merge, by the same top-level session that
authored this brief — since it authored the brief directly, the usual "hand back to me unmerged"
step collapses into "verify before merging," matching this project's own established practice for
the rare cases where the top-level session performs a fix or closure directly (e.g. T440's
ledger-sequencing fix, T492's allowlist review).
