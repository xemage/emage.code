# Plan 055 — Phase 6 ("Closed Loop") re-scoped detailed planning pass

> Filename: `plan-055-phase6-closed-loop-rescoped-detailed-planning.md`

**Status: proposed — not approved for task-brief authoring or execution.**

This document does not open, dispatch, or author a task brief for any Phase 6 implementation task.
It is a planning pass only, mirroring the precedent set by `plan-037-phase2-phase5-sequencing.md`
(Phase 2), `plan-038-phase5-detailed-planning.md` (Phase 5), `plan-041-phase3-maturity-ladder-
detailed-planning.md` (Phase 3), and `plan-043-phase4-task-tier-routing-detailed-planning.md`
(Phase 4): each phase sat at `plan-035`'s own `"Status: proposed — not approved..."` header until a
dedicated planning pass existed, before any individual `task-T4xx.md`/`task-T5xx.md` brief was
authored.

**Based on:** `docs/artifacts/phase6-sia-readiness-audit-v1.md` (this task's own companion audit,
authored immediately before this document, in the same session — its §§2–6 findings are the direct
basis for every re-scoping decision below and are not re-derived here); `docs/plans/
plan-035-roadmap-v7-ground-up.md` §2.4 Phase 6 (the original task table, T460–T466, unchanged as a
naming reference — see §1 below for why this document does not renumber it); `docs/checkpoints/
checkpoint-033-phase4-phase5-complete-gate-g3-closed.md` (gate status: G3 closed, G4's
evaluator-protection precondition closed with G1, Phase 6 gate-reachable but not execution-ready);
`docs/artifacts/protected-paths-v1.md` (the still-missing T463 evaluator-hash check, confirmed by
direct read); `docs/tasks/task-T415.md` (the real, reusable failure-taxonomy artifact); `docs/
plans/plan-016-pattern-a-hardening-and-phase23-poc-closure.md` (the Pattern A/B/C descoping
decision this plan's §2 routes around); `implementation/knowledge/agents/{solution-architect,
backend-developer,evaluation-agent,devops-engineer,release-manager,technical-writer}.md` (real tool
grants, re-checked directly this session, not assumed from `plan-035`'s nominal owner column, per
this task's own explicit instruction and the repo's own repeated T410/T415/T418/T420/T430/T440/
T451/T456/T458 precedent for that exact gap).

## Goal

Produce the same kind of dispatch-ready decomposition for Phase 6 (`plan-035`'s nominal T460–T466,
"Closed Loop") that the four prior per-phase planning passes produced for Phases 2–5: a
re-confirmed start-condition check, a corrected dependency graph (per the audit's primary finding —
Phase 6 depends on the golden-harness/failure-taxonomy infrastructure, not on the invalidated
SIA/CWSO RL subsystem), a concrete per-task sequencing/agent-assignment table with tool-grant checks
done *before* dispatch, an artifact flow, and risks. **This plan does not itself author any
`task-T5xx.md` brief and does not dispatch any agent.**

## 1. On task numbering — a disclosed gap, not silently resolved

The audit (`phase6-sia-readiness-audit-v1.md` §0) found that this task's own dispatch described an
"ID-renumbering note" in `plan-035` translating its nominal `T460` to the real ledger ID `T500` —
and that no such note actually exists in the document. This plan is itself the direct descendant of
`plan-035`'s nominal `T461`–`T466` row (the rest of the Phase 6 task table). **This document does
not invent new task IDs for those six rows.** The next real, free ledger ID at the time this plan
was authored is unknown to this plan with certainty — `docs/tasks/active-tasks.md` shows 0 active
rows and the highest completed ID on record at audit time was `T499`, with this task itself
occupying `T500` — but per this repo's own repeated practice (e.g. `plan-043` deliberately did not
invent new numbers for T440–T443 because those were still the real free IDs at that plan's own
authoring time), **actual task-ID assignment is the orchestrator's job at dispatch-approval time,
not this planning pass's job.** Below, tasks are referred to by their `plan-035` nominal names
(`T461-equiv`, etc.) with an explicit instruction that the orchestrator must re-verify the true
next-free ID immediately before authoring each brief, exactly as the audit's §0 recommends doing
for this task's own ID before treating any Phase 6 artifact as fully anchored.

## 2. Re-confirmed state

- Gate status re-confirmed directly from `checkpoint-033`, not assumed: **G3 closed**, **G0/G1/G2**
  closed and unchanged, **G4**'s evaluator-protection precondition closed with G1, the rest of G4
  governs Phase 6 itself and is not yet met (no closed loop exists to evaluate).
- Per `plan-035`'s own phase graph (`P3 --> P6`, `G3 --> P6`, `G4 --> P6`), Phase 6's incoming
  preconditions (P3 done, G3 closed) are both met. **Phase 6 is gate-reachable.**
- `docs/tasks/task-T500.md` (this audit task's own brief) does not exist on disk — see the audit's
  §0. This plan's own authoring does not depend on that file's existence, but the orchestrator
  should create it (or its equivalent record) before this plan is treated as approved, so the ledger
  trail is complete.
- The `implementation/runtime/golden_harness/` module (built across T458/T456/T499, independently
  re-verified multiple times this arc per `checkpoint-033`) is real, tested, and already exposes the
  exact primitives T463-equiv needs: `scoring.score_scratch_dir()`, `policy.floor_met()`,
  `policy.pass_rate()`, `policy.classify_k_plus_outcome()`. This is a genuine, previously
  undocumented scope reduction for T463-equiv relative to `plan-035`'s original "large" estimate —
  see §4.

## 3. Finding — Phase 6's real dependency graph, corrected

`plan-035` §2.4 Phase 6's own introductory prose names `implementation/sia/`, `sia-executor.py`,
and the T223/T224/T225 reward pipeline as "already exist[ing]" scaffolding Phase 6 should wire into
a closed loop. The audit (§4) found this is inconsistent with the six tasks' own literal scope: none
of T461–T466 require a reward signal, trajectory capture, or a fine-tuned model. **This plan adopts
the corrected reading**: Phase 6's real dependency graph runs through —

1. `docs/artifacts/failure-taxonomy-v1.md` + `docs/benchmarks/failures/` (T415, real, tested,
   already classifies the 9 `known_failing` golden cases along `cause × behavior × mechanism`) —
   feeds T461-equiv.
2. `implementation/runtime/golden_harness/{scoring,policy}.py` (T458, real, tested) — feeds
   T463-equiv's before/after comparison.
3. `docs/artifacts/protected-paths-v1.md` + `tests/functional/test_golden_held_out_isolation.py`
   (T412/T416, real, enforced) — feeds T463-equiv's automatic-rejection requirement ("a proposal
   that touches `tests/golden/**` or `scripts/scorecard.py` is rejected automatically").
4. Nothing under `implementation/sia/` or `implementation/adapters/sia-target/` is a dependency of
   any Phase-6 task as literally scoped. **An executing agent must not be handed `plan-035`'s
   original Phase 6 introductory prose as a scoping instruction without this correction attached** —
   doing so risks silently resurrecting the Pattern B/C RL loop `plan-016` explicitly killed.

This does not delete or deprecate the SIA/CWSO code — per the audit, most of it is real and some of
it (`reward_attachment.py`, `reward_shaping.py`, `trainer_bridge.py`, `release_gate.py`) is
genuinely well-built. It simply is not Phase 6's dependency, and whether it is ever revived for a
future RL-training phase is an explicit, separate, not-yet-made decision (`plan-035` §2.7's own
deferral: "GRPO / LoRA fine-tuning at scale... After Gate G4 and sustained trajectory volume").

## 4. Re-scoped task sequencing table

| Nominal ID | Task (unchanged objective from `plan-035` §2.4) | Owner (re-verified tool grant) | Re-scoped notes vs. `plan-035`'s original sketch |
|---|---|---|---|
| T461-equiv | Wire weakness mining to the Phase 1 failure taxonomy (T415) — reuse, do not reimplement | `backend-developer` (`[read, search, edit, execute, web, mcp__fetch]`) | Unchanged owner. **New, disclosed open design question this task's own brief must resolve** (audit §5 item 1): how do failures beyond the 9 static `known_failing` cases flow into the same taxonomy on an ongoing basis (future golden-suite runs? the Terminal-Bench delta harness, T417–T419?). `plan-035`'s original sketch did not anticipate this as open. |
| T462-equiv | `@meta-improver`: failure cluster → diff proposal, never an applied edit | Split: **build** phase owned by `backend-developer` (same tool grant as above, matches the `@context-retriever`/T454 precedent for building a new agent + supporting code); **live-dispatch validation** (at least one real end-to-end cycle against a real failure) owned by **orchestrator, executed directly** — mirrors the `checkpoint-033`-documented split-ownership pattern (`T458`/`devops-engineer`, `T456`&`T499`/`evaluation-agent`), applied here pre-emptively rather than discovered mid-task as it was those four prior times. Neither `backend-developer` nor any other Phase-6 candidate agent has the `agent` tool needed to dispatch a live nested session. | Genuinely greenfield — no existing code found anywhere in this repo (audit §5 item 2). Correctly stays "large." |
| T463-equiv | Validation: proposal vs. failing case + open suite + held-out suite + baseline; promotion rule | `backend-developer` builds the **new** evaluator-hash tamper-evidence check (confirmed missing, `protected-paths-v1.md` §2 item 2) and the promotion-rule glue code around the **already-real** `golden_harness.scoring`/`golden_harness.policy` primitives; **orchestrator executes** the actual live comparison runs, same split-ownership reasoning as T462-equiv and the same structural reason `evaluation-agent` (`[read, search, web]`, no `execute`, no `agent` tool) cannot be this task's sole owner despite being `plan-035`'s implicit natural fit by name. | **Real scope reduction from `plan-035`'s original "large" estimate**: the before/after comparison machinery already exists and is tested (audit §5 item 3); only the evaluator-hash check and the promotion-rule wiring are net-new. Recommend re-estimating as "medium" once a real brief is drafted, pending the orchestrator's own token-budget judgment. |
| T464-equiv | Human gate: proposals open an MR against `develop`; no auto-merge path | `release-manager` (`[read, search, edit, execute, web, mcp__gitlab]`) | Unchanged from `plan-035` — tool grant confirmed sufficient, no live-dispatch requirement, ordinary MR flow already used throughout this repo. |
| T465-equiv | Harness lineage document per accepted change | `technical-writer` | Unchanged from `plan-035`. Note (not a blocker): this repo's own ledger (T379/T380) shows `technical-writer` sessions have twice lacked Bash tool access and needed orchestrator assistance for mechanical steps (branch state confirmation, sanctioned regeneration commands) — worth the orchestrator budgeting a little of its own time for this task rather than assuming a fully autonomous hand-off, though this is a minor friction, not a structural gap like T462/T463's. |
| T466-equiv | Kill switch: one documented command halts the loop; cannot self-resume | `devops-engineer` (`[read, search, edit, execute, web, mcp__gitlab, mcp__fetch]`) | Unchanged from `plan-035` — this is a local implementation-and-test task with no live-dispatch requirement, squarely within `devops-engineer`'s real tool grant despite its own lack of the `agent` tool (irrelevant here, unlike for T462/T463). |

**Sequencing**: T461-equiv and T466-equiv have no dependency on each other or on T462/T463 and can
run in parallel once dispatched. T462-equiv (build half) can start once T461-equiv's taxonomy-feed
mechanism is defined (needs a real failure-cluster shape to design the proposal schema against).
T463-equiv depends on T462-equiv's proposal schema existing (even in draft form) to know what it is
validating. T464-equiv depends on T463-equiv's promotion rule existing. T465-equiv can be authored
in parallel with T464-equiv (documents the *mechanism*, not a specific accepted change, until the
first real cycle completes). This mirrors `plan-035`'s own original sequencing intent; nothing in
the audit's findings changes the *order*, only the *owners* and *scope estimates* for T462/T463.

## 5. Artifact flow

```
T415 (existing) ──> T461-equiv (wiring) ──> T462-equiv (build: proposal schema + @meta-improver)
                                                    │
protected-paths-v1.md (existing) ──┐               │ (live dispatch, orchestrator-executed)
golden_harness/{scoring,policy}.py ┼──> T463-equiv (build: evaluator-hash check + promotion glue)
   (existing, T458)                │         │ (live dispatch, orchestrator-executed)
                                    └─────────┼──> T464-equiv (MR gate) ──> T465-equiv (lineage doc)
                                              │
                                    T466-equiv (kill switch, independent)
```

## 6. Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| A future task brief is drafted from `plan-035`'s original Phase 6 prose without this plan's §3 correction attached, and silently wires the loop through `implementation/sia/`. | Medium | Critical (would resurrect a `plan-016`-killed pattern) | Any Phase 6 task brief must cite this plan (`plan-055-*.md`) and the audit (`phase6-sia-readiness-audit-v1.md`) as its `Based on:`, not `plan-035` §2.4 alone. |
| T462-equiv or T463-equiv's brief assigns the live-dispatch half to an agent lacking the `agent` tool, repeating the gap this repo has now hit at least 9 times. | Medium (this class of gap has recurred repeatedly despite being well-documented) | Medium (caught late costs a re-scope cycle, not a false ship) | This plan's §4 table states the split explicitly, in advance, so the orchestrator does not need to rediscover it mid-task. |
| T463-equiv's evaluator-hash check duplicates or conflicts with `protected-paths-v1.md`'s existing three-control model instead of becoming its literal "control 2." | Low | Medium | T463-equiv's own future brief should quote `protected-paths-v1.md` §2 verbatim and implement exactly the control described there, not a reinvented variant. |
| Estimating T463-equiv as "medium" instead of `plan-035`'s original "large" proves optimistic once a real brief is drafted (the evaluator-hash check's actual design is still undetermined). | Medium | Low | Treat §4's re-estimate as a planning-pass judgment, not a commitment; the orchestrator should re-confirm scope when T463-equiv's actual brief is written, per this repo's own token-governance discipline. |
| `@meta-improver` (T462-equiv), once built, is tempted to reuse `reward_shaping.py`'s ±1/eval-blend pattern for scoring proposals, pulling Pattern B/C's reward-shaping logic back into scope by convenience rather than necessity. | Low | Medium | T462-equiv/T463-equiv briefs should score proposals via `golden_harness.policy`'s pass/fail and regression-classification primitives (already the tool this repo's own ship-gate measurements use), not via `reward_shaping.py`'s continuous blended reward, which was designed for RL training signal, not for a binary promote/reject gate. |

## 7. Explicit non-actions of this plan

- No `task-T5xx.md` brief is authored by this plan.
- No agent is dispatched by this plan.
- `docs/tasks/active-tasks.md` is not modified by this plan.
- This plan does not resolve whether the SIA/CWSO RL subsystem is ever revived for a future phase —
  that remains `plan-035` §2.7's own explicitly deferred item, untouched here.
- This plan does not fix T221's dangling ledger citation (`run_agent_openhands` no longer exists) or
  clean up `sia-executor.py`'s vestigial `mock_delay` parameter/docstring — both are disclosed in the
  companion audit (§2 rows T221/T235) as small, real, separately-dispatchable follow-ups, not
  addressed here since they are documentation-hygiene items unrelated to Phase 6's own critical path.
