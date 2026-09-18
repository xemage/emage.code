# Checkpoint 033 — Phase 4 and Phase 5 complete; Gate G3 closes; Phase 6 unblocked

> Written by the top-level session immediately after T499's merge and ledger closeout. No
> checkpoint was written for Phase 4 (T440–T443) or Phase 5 (T450–T499) as each completed —
> `checkpoint-032` (Phase 3) is the last one on record, and real progress since then was tracked
> only through the task ledger and individual task briefs, not through a checkpoint. This document
> closes that gap in one pass rather than reconstructing it piecemeal later. Future agents planning
> Phase 6 need this checkpoint plus `docs/benchmarks/baseline-v6.17.0-retrieval-v2.md` plus
> `docs/decisions/ADR-005-memory-layer-design.md`, not the full T440–T499 execution history.

## Summary

**Phase 4 (`plan-035` T440–T443, "Task-Tier Routing") and Phase 5 (T450–T499, "Persistent
Memory / RAG") are both fully done and genuinely merged to `develop`.** Phase 5's own formal ship
gate — Gate G3 — is now closed for real, on an honest, independently re-verified measurement, not
asserted. This is the direct result of a long, continuous arc across many sessions: build the
memory layer (T450–T455), discover the golden suite had no live-execution path to measure it with
(T456, first attempt, correctly declared `blocked`), design and build a scoped tool-execution
primitive for two agents along the way (T457, T495–T497, a parallel side-quest triggered by MR
review), build the real live-execution harness (T458, via an eight-task investigative arc
T484–T494 that established real methodology first), re-attempt the ship-gate measurement for real
(T456 re-dispatch: **NO-SHIP**, honestly measured, root-caused to one checker-brittleness bug),
fix the diagnosed bugs under an explicit protected-path exception (T498), and re-measure
(**T499: SHIP**). Every step in this chain was independently re-verified by the top-level session
before merging — diffs read in full, arithmetic recomputed by hand, tests re-run fresh — not
accepted on any agent's self-report alone, consistent with this project's standing discipline.

## Real, independently-verified final state (not assumed)

- `python3 docs/tasks/validate-tasks.py`: PASS (0 active, 298 completed)
- `python3 tests/run.py`: 596 tests, OK, skipped=38
- `python3 implementation/scripts/check-maturity.py --verbose`: 79 components, 0 failing their
  claimed level
- `node implementation/scripts/sync.mjs --root implementation --check`: no drift, 577 files
- `docs/tasks/active-tasks.md` is genuinely empty — every task this project has ever opened is
  either `done` or was folded into a closed task's own record.

## Phase 4 — Task-Tier Routing (T440–T443), summary

Defined the `mechanical`/`standard`/`judgment` task-tier vocabulary and its three-gate
`mechanical`-eligibility rule (T440); published a static tier→model-class routing policy under
`implementation/knowledge/instructions/` (T441); defined escalation-on-`mechanical`-failure and
the misclassification-defect rule (T442); extended `scripts/scorecard.py` to record model tier and
outcome per golden case (T443, under an explicit, narrow, reviewed protected-path exception). All
four independently verified and merged in prior sessions. This checkpoint does not re-verify
Phase 4's own historical work — it is cited here only to close the "no checkpoint was ever written"
gap, not because anything about it changed this session.

## Phase 5 — Persistent Memory / RAG (T450–T499), summary

- **T450–T455 (memory layer, done long before this session's final arc)**: `ADR-005` (SoloMD
  decision, read-only default), the three-scope model, the indexing pipeline, hybrid retrieval,
  the read-only `@context-retriever` agent, and its own retrieval-quality eval sub-suite. All
  independently verified and usable as of their own closure — unaffected by anything in this
  checkpoint.
- **T456, first attempt (2026-09-09)**: correctly found the golden suite has no live-agent
  execution path by deliberate Phase 1 design (`golden-suite-format-v1.md` §2.2/§4.2) — declared
  honestly `blocked`, not faked. Opened `T457` (below) and `T458` (the real follow-up) rather than
  routing around the gap.
- **T457 / T495–T497 (tool-scoping side-quest, found during T456's own MR review, resolved this
  session)**: `@security-engineer` and `@context-retriever` both carried an `execute`→`Bash`
  unrestricted-shell tool grant undermining their own declared read-only/audit-only posture. `T495`
  gave `@context-retriever` a dedicated single-tool `stdio` MCP server. `T496`/`T497` gave
  `@security-engineer` a fixed 4-tool audit-command MCP server (Option C, user-selected over two
  narrower alternatives). Both backed by real, independently-re-run adversarial subprocess-over-
  stdio tests proving fabricated write/execute/shell tool calls are genuinely rejected, not merely
  asserted safe. `T457` (the tracking task) and `T496` closed once `T497`'s real implementation
  made their own stated blocking conditions false.
- **T458 (the real harness, via an eight-task investigative arc T484–T494, then formalized)**:
  `T484`–`T494` proved the live-execution mechanism works, built the first real memory-vault index,
  populated it with real content, and — critically — found that neither of the two ever-observed
  "clear positive influence" findings reproduced on retest (0 of 4 reproducibility attempts),
  converging evidence against treating a single observed retrieval influence as a stable property.
  Set a real, evidence-grounded k/escalation/floor-tolerance policy (`plan-048`). `T458` itself then
  turned that entirely-manual, by-hand methodology into real, committed, tested code
  (`implementation/runtime/golden_harness/`), with ownership deliberately split between
  `devops-engineer` (code) and the orchestrator (live-trial execution — `devops-engineer` has no
  `Agent`-tool grant and cannot dispatch live sessions itself, the same structural gap found for
  `evaluation-agent` later).
- **T456, re-dispatch (2026-09-17)**: used `T458`'s harness for a real measurement across 19 of the
  golden suite's 20 cases (1 excluded, disclosed, not reproducible by a fresh session). Pre-
  registered threshold (reused `plan-048`'s floor-tolerance policy) committed before any trial ran.
  **Result: control 20/29 (68.97%), treatment 19/31 (61.29%), verdict NO-SHIP** — honestly reported,
  not softened. Root-caused the entire deficit to one already-diagnosed (`T493`), arm-agnostic
  checker-brittleness bug plus three newly-found ones, none retrieval-caused (18 of 19 cases showed
  byte-identical control/treatment outcomes).
- **T498 (checker fixes, protected-path exception)**: fixed the four diagnosed bugs across exactly
  five `expect.py` files under `docs/artifacts/protected-paths-v1.md` §5's explicit exception
  process (an authorized task brief, not an incidental edit). Each fix minimal and targeted — a
  declared-count ceiling relaxed from strict equality to an inequality, a fenced-code-block
  heading-boundary skip, a table-cell regex widened to whole-word-anywhere-in-cell, and a `Status`
  field search scoped to the real `## VERDICT` block. Phase-1 baseline parity independently
  re-confirmed unchanged for all five cases.
- **T499 (re-measurement)**: re-measured only the five affected cases (mechanically confirmed via
  diff that no other `expect.py` changed) — four re-scored against their original T456 candidate
  text unmodified (isolating the checker-fix effect from any live-session non-determinism
  entirely), one given a fresh live k=1 trial. All five flip to passing in both arms.
  **New aggregate: control 21/25 (84.00%), treatment 23/27 (85.19%), `floor_met()` = `True`, no
  case classified a retrieval-attributable persistent effect. Verdict: SHIP.**

## Gate status

- **Gate G3 is now closed.** Per `plan-035` §2.4 Phase 5's literal, pre-registered ship-gate rule,
  applied honestly on real measured data (`docs/benchmarks/baseline-v6.17.0-retrieval-v2.md`), not
  asserted or softened. This is a genuine change from `checkpoint-032`'s own recorded state ("Gate
  G3 remains open").
- **Gate G0/G1/G2** remain closed, unchanged (`checkpoint-016`/`checkpoint-021`/`ADR-006`
  respectively).
- **Gate G4** remains ungated-but-unclosed — its evaluator-protection precondition closed with G1
  (per `checkpoint-032`), but the rest of its own phase's conditions (Phase 6, below) haven't been
  reached. Unchanged this session.

## Phase 6 — Closed Loop (v7.0.0) — now genuinely available, not started

Per `plan-035`'s own phase graph (`P3 --> P6`, `G3 --> P6`, `G4 --> P6` — three incoming edges, not
G3 alone), Phase 6's remaining precondition was Gate G3; Phase 3 (`P3`) already closed at
`checkpoint-032`. **Phase 6 is therefore now reachable at the gate level.** It has **not** been
planned to execution-ready detail and is **not started** — per this project's own Plan-Approve-
Execute protocol and the precedent every other phase transition in this project has followed
(`plan-037`/`plan-038`/`plan-041`/`plan-043`'s own dedicated per-phase detailed-planning passes),
this is available to start on request, not started proactively. `plan-035` §2.4's own Phase 6 task
table (T460–T466) is a first-draft sketch, not an execution-ready plan — the same gap Phase 3/4/5
each closed with their own detailed-planning document before any task was dispatched.

**One explicit, disclosed prerequisite named directly in `plan-035`'s own Phase 6 section**: T460
("audit existing SIA components... **no new module until this audit is complete**") must read
`docs/artifacts/phase2-3-poc-debt-scorecard-v1.md` first — the existing `implementation/sia/`
scaffolding is confirmed PoC-grade, not validated. Not investigated or acted on this checkpoint.

## Process notes worth carrying forward

- **Every real measurement in this arc that returned a negative or blocked result was reported
  honestly and closed as such (`done` with a genuine negative outcome, not left open or forced
  positive)** — T456's original `blocked` finding, T456's re-dispatch NO-SHIP verdict, and every
  intermediate reproducibility-test failure in `T484`–`T494`. This discipline is what makes T499's
  eventual SHIP verdict trustworthy: it was earned by a real fix to a real, previously-honestly-
  reported problem, not by a threshold quietly loosened until something passed.
- **The self-referential ledger-defect regression (`check-maturity.py`'s `_ledger_defect()`
  whole-word-matching a stable component's literal id inside an open P0/P1 brief) recurred multiple
  times across this arc**, including twice within `T498` alone (once in the dispatch commit, once
  independently on the implementation branch that had forked before the first fix landed). This
  class of bug is now well-understood but keeps recurring because each new task brief re-introduces
  it fresh — worth checking any future brief against the current `stable`-id list before dispatch,
  not assumed safe by analogy to a prior fix.
- **The split-ownership pattern (an agent builds code, the orchestrator executes live dispatches
  the agent's own tool grant can't reach) recurred twice this arc** (`T458`/`devops-engineer`,
  `T456`&`T499`/`evaluation-agent`) and is now a named, reusable precedent rather than something to
  re-discover per task — check an agent's real tool grant against what a task actually requires
  before assuming its nominal ownership is executable as written.
- **Re-scoring original candidate text against a fixed checker, when recoverable, is more rigorous
  than a fresh re-dispatch** (`T499`'s own finding) — it isolates a checker fix's effect completely
  from live-session non-determinism. Worth deliberately preserving trial candidate text in a
  recoverable location for any future measurement expected to need a fix-and-reverify cycle, rather
  than relying on it happening to still be present in an active session's scratch directory.

## Token metrics

Not separately tracked against a phase budget across this arc.

## Next steps

- **Phase 6 (Closed Loop, v7.0.0) is unblocked at the gate level** but not planned to execution-
  ready detail and not started — available to start on request, per this project's own protocol,
  not started proactively this checkpoint.
- `plan-048` §6 items 3/4 (a harder, vault-dependent golden case; scaling to 30–50 trials for a
  numeric qualitative-rubric threshold) remain separate, disclosed, not-yet-dispatched follow-ups —
  unrelated to Gate G3's own binary pass/fail criterion, which is now met regardless.
- **`feature/T475-codex-platform-integration`** remains exactly as prior checkpoints left it: a
  real, unpushed local branch ~2 real commits of genuine, `CONDITIONAL_PASS`-gated work (OpenAI
  Codex platform support, T475–T481), now roughly 210+ commits behind `develop`, never merged. Not
  touched this session. A user decision (revive/rebase vs. shelve) remains outstanding.
