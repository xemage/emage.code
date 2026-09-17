# Task T458 — Live-execution harness for the golden suite (unblocks T456)

**ID:** T458
**Owner:** **Split, deliberately — see "Why ownership is split" below.**
- `devops-engineer` — owns turning the already-proven, currently entirely manual live-execution
  mechanism into real, committed, reusable, tested code (scratch-isolation helper, scoring/
  classification module, `scorecard.py`-pattern `expect.py` invocation, escalation/floor-tolerance
  logic). Does **not** dispatch live trials itself.
- Top-level session / orchestrator — continues to execute the actual live control/treatment
  dispatches through `devops-engineer`'s code, exactly as it already has for the 28 trials behind
  this brief's own evidence base (`T484`, `T487`–`T490`, `T493`–`T494`). This is **not new scope**
  for the orchestrator — it is the status quo, now being formalized into reusable code instead of
  ad hoc invocation.
**Status:** pending
**Re-scope note (2026-09-17):** this brief supersedes its original 2026-09-09 version (preserved in
git history) — not yet dispatched either version. See "What changed since the original brief" below.
**Priority:** P1 (blocks Phase 5's formal ship decision and Gate G3's closure; does **not** block
`@context-retriever`/the memory layer from being genuinely usable today — those are already done
and independently verified)
**Depends on:** None structurally (T454's `@context-retriever` agent it exercises is done; the
golden suite's `expect.py`/case format it reuses is frozen/done from Phase 1; the methodology it
formalizes — `k`/escalation/floor-tolerance policy — is already decided, see `plan-048`).
**Blocks:** T456 (cannot be genuinely re-attempted without this task's output)
**Created:** 2026-09-09
**Completed:** —
**Based on:**
- `docs/tasks/task-T456.md` — the blocker this task exists to resolve (golden suite has no
  live-agent execution path by deliberate Phase 1 design).
- `docs/plans/plan-040-t458-golden-live-harness-followup.md` — this task's original backing plan;
  its task-graph and rationale are unchanged, only the scope below is revised.
- `docs/plans/plan-044-t458-first-slice.md` — **read this in full before starting.** Its Finding 3
  is why ownership is split (see below): `implementation/knowledge/agents/devops-engineer.md`'s
  `tools:` grant (`[read, search, edit, execute, web, mcp__gitlab, mcp__fetch]`) has no `agent`
  tool, so it cannot dispatch live sessions the way the orchestrator's in-process `Agent` tool does.
  Its walking-skeleton design (one case, one trial per arm, scratch-directory isolation, real
  `expect.py` reuse via `importlib.util.spec_from_file_location`) is the exact mechanism already
  proven working by `T484` and reused unmodified by every trial since — this is the shape the code
  this task produces must formalize, not redesign.
- `docs/plans/plan-045-t458-scaling.md`, `plan-046-t458-tier1-dispatch.md`,
  `plan-047-t458-k-threshold-resolution.md`, `plan-048-t458-k-threshold-decision.md` — the full
  scaling/methodology arc. `plan-048` §7 is the authoritative, already-decided policy this task's
  code must implement, not re-derive:
  - Default `k=1`; escalate to `k≥3` on `k=1` arm disagreement; separately escalate any unanimous
    case whose treatment trial shows a category-3 finding, to retest reproducibility.
  - Classify every `k≥3` result into one of three named outcomes: confirmed coin-flip, confirmed
    persistent effect, or elevated-but-heterogeneous (open) — never forced into a binary call.
  - A floor miss is actionable only once its specific diagnosed cause recurs across ≥2 trials
    within the same case; a floor miss whose cause has occurred exactly once stays open.
  - The real, current base rate (2 of 11 classified treatment trials show traceable positive
    influence — 18%, or 14% conservatively including the 3 unclassified trials as non-category-3)
    — a data point this task's code should be able to reproduce from raw trial records, not a
    number to hardcode.
- `docs/tasks/task-T484.md`, `task-T487.md`–`task-T490.md`, `task-T493.md`, `task-T494.md` — the 28
  real trials already run using the exact mechanism this task must now formalize. Read at least
  `task-T484.md` (the walking skeleton) and `task-T493.md` (the most recent `k≥3` escalation, real
  arm-agnostic checker-brittleness finding) before designing the code's interfaces.
- `docs/artifacts/golden-suite-format-v1.md` — the case format/`expect.py` contract, reused
  unmodified (§2.2's own design note anticipating exactly this live-run reuse).
- `docs/artifacts/context-retriever-v1.md` — the `ContextRetriever.query()` / CLI surface the
  treatment arm wires in (a `Bash`/`execute` subprocess call, per `context-retriever-v1.md` §2.1's
  documented real invocation shape — not a nested `Agent` dispatch).

## Why ownership is split (read before objecting to either half)

This repo's own precedent for harness-building work is `devops-engineer` (T417/T418/T419's
Terminal-Bench harness). That precedent still holds for *this* task's actual deliverable — real,
committed, tested infrastructure code. What has changed since the original 2026-09-09 brief is that
`plan-044`'s Finding 3 already surfaced, and this session's decision confirms, that `devops-engineer`
structurally cannot be the sole owner of live-trial *execution*: it has no `Agent`-tool grant, and
this repo's own established discipline (T415/T418/T455 precedent) is to reassign or re-scope a task
rather than silently widen an agent's tool grant to route around a mismatch.

The alternative — routing live dispatches through a standalone `claude` CLI subprocess via
`devops-engineer`'s existing `execute` grant (`plan-044`'s other Finding-3 option) — is **explicitly
rejected for this task**, not merely deferred: the 28 trials this brief's methodology (`plan-048`)
is built on were all run via the in-process `Agent` tool. Switching the execution mechanism now
would mean validating that a fresh, separate `claude` CLI process produces trials equivalent to the
in-process ones before any new data from it could be trusted alongside the existing evidence base —
a real, currently unvalidated risk, for no disclosed benefit. **Do not implement or investigate the
CLI-subprocess path as part of this task.** If a future task wants to pursue it as a genuinely
separate execution mechanism, that is a new, explicitly scoped decision, not something to fold in
here.

Concretely: `devops-engineer` builds and tests the harness's non-dispatch logic in isolation (using
recorded/synthetic trial data, not live sessions, for its own test suite — see Expected Outputs
item 4). The orchestrator continues to be the one that actually runs `/new-feature <brief>` (or
whichever command a case names) as a live control/treatment pair, now calling `devops-engineer`'s
code to do the scratch-isolation setup and `expect.py` scoring instead of repeating that logic by
hand each time.

## What changed since the original brief (2026-09-09 → 2026-09-17)

The original brief (preserved in git history) scoped this task as inventing the live-execution
mechanism from scratch, with the two-arm design, scratch isolation, and `expect.py`-reuse pattern
all still open questions, and no ownership-model gap yet identified. Since then, an eight-task
investigative arc (`T484`, `T485`, `T486`, `T487`, `T488`, `T489`, `T490`, `T493`, `T494` — all
`done`) ran directly by the orchestrator:

- Proved the mechanism works end-to-end (`T484`, one case, one trial per arm).
- Built the first real memory-vault index and populated it with real content (`T485`, `T486`) —
  before this, `@context-retriever`'s treatment arm had nothing real to retrieve.
- Found and reproduced-tested two "clear positive influence" cases, with a real, disclosed negative
  finding: neither reproduced on retest (0 of 4 reproducibility attempts) — a genuine signal against
  treating a single observed influence as a stable property (`T487`, `T489`, `T494`).
- Ran a 5-case, k=1 breadth expansion (`T488`) and a targeted k≥3 escalation on the two cases that
  showed real spread (`T490`), then a further k=5 escalation on the one case k≥3 couldn't yet
  resolve (`T493`) — which confirmed a real, arm-agnostic checker/template brittleness bug, not a
  retrieval effect.
- Set the k/escalation/floor-tolerance policy this task's code must now implement (`plan-048`,
  summarized above).

**None of this produced committed, reusable code.** Every trial ran by hand: scratch directories
under a session's own `/tmp` scratchpad, `expect.py` loaded ad hoc via `importlib` each time,
classification and floor-tolerance judgment applied by the orchestrator reading raw output, not by
any checked-in logic. That gap — real methodology, zero reusable infrastructure — is this task's
actual, narrowed scope now.

## Objective

Turn the already-proven, currently entirely manual live-execution mechanism into real, committed,
tested code that the orchestrator can call instead of repeating the same by-hand steps for every
future trial or every future golden-suite case. Concretely:

1. **A scratch-isolation helper**: given a case's `brief.md` and a `control`/`treatment` label,
   create an isolated plain scratch directory (never a git worktree, never the main checkout — same
   as every trial run so far) and return its path, ready for a live session to be dispatched into.
2. **A scoring module** that, given a scratch directory and the real, unmodified case `expect.py`,
   loads it via `importlib.util.spec_from_file_location` (exact `scripts/scorecard.py` pattern,
   reused not reinvented) and returns a real boolean — the same call shape every trial so far has
   used by hand.
3. **A trial-record schema and store** (e.g. structured JSON per trial: case ID, arm, `k`-index,
   boolean result, category classification if applicable, diagnosed cause if a floor miss) — turning
   the 28 existing trials' worth of informal notes (scattered across `task-T484.md` through
   `task-T494.md`'s prose) into a queryable, reusable format going forward. **Do not attempt to
   retroactively re-encode all 28 historical trials as a precondition of this task** — that is
   optional, disclosed scope if time allows, not required; the schema and store must work for new
   trials regardless.
4. **An implementation of `plan-048`'s decided policy** (k=1 default, escalation triggers,
   three-outcome `k≥3` classification, floor-tolerance recurrence rule) as real, testable functions
   operating on the trial-record schema — not reprising the numbers as documentation, but as code a
   future trial batch can actually run through to get a classification, the same judgment the
   orchestrator has been applying by hand.
5. **Wiring the orchestrator's next live dispatch through this code** — at minimum one real,
   observed trial (reusing an already-run case, e.g. re-confirming `T484`'s own control/treatment
   pair) to prove the new code path produces the same result the by-hand mechanism already did, not
   a divergent one. This is a regression check on the *code*, not a new methodology question.

**This task does not need to run new trials to expand the evidence base.** `plan-048` §6 names two
genuinely separate follow-up items still open (a harder, vault-dependent golden case; scaling to
30-50 trials for a numeric ship-gate threshold) — **both are explicitly out of scope for this task**,
to be separately dispatched once this harness code exists, using it.

## Constraints

- **Live dispatches remain the orchestrator's, via the in-process `Agent` tool — unchanged from
  every trial run so far.** Do not widen `devops-engineer`'s tool grant to include `agent`. Do not
  implement or investigate the standalone-`claude`-CLI-subprocess alternative (see "Why ownership is
  split" above) — that is a rejected, not deferred, option for this task specifically.
- **No paid or recurring-cost API calls.** The mechanism this task formalizes already runs entirely
  through this repo's existing in-process agent-dispatch mechanism, at zero incremental metered
  cost — this task must not introduce one. If your design genuinely requires a metered API call of
  any kind, that is a `type: external`, `severity: critical` blocker requiring explicit user
  cost-authorization before any such call.
- **Do not touch `.mcp.json`, anywhere, for any reason. Do not touch the main checkout.**
- **Do not touch `tests/golden/**`, `scripts/scorecard.py`, `docs/benchmarks/tb-subset.json`/`.md`**
  — reuse `expect.py`'s contract by importing/calling it exactly as `scripts/scorecard.py` and every
  trial so far already does, never by editing it. If you find you must add a small, additive,
  non-invasive extension point, that itself requires an explicit, disclosed exception request to the
  orchestrator before any such edit, per `docs/artifacts/protected-paths-v1.md`'s documented
  exception process — do not silently work around this by copying/forking `expect.py`'s logic.
- **Do not touch `feature/T475-codex-platform-integration`. Do not start any Phase 3 work.**
- **Confirm your own tool grant before starting** — check
  `implementation/knowledge/agents/devops-engineer.md` directly (`tools: [read, search, edit,
  execute, web, mcp__gitlab, mcp__fetch]` as of this brief's writing) and report immediately as a
  `type: technical` blocker if it has changed and is now insufficient for the *non-dispatch* scope
  this brief actually assigns you, rather than discovering it mid-task.
- **Work in your own worktree/branch**, created from `develop`. Commit as you go; run the full test
  suite (`python3 tests/run.py`) and confirm no regressions before reporting completion. **Do not
  self-merge** — push and open a merge request, then stop.
- Follow this repo's coding standards (max 50-line functions, max 4 parameters, early returns) and
  Conventional Commits.

## Expected Outputs

1. Harness code (natural location `scripts/` or a new `implementation/runtime/` module — state your
   actual choice) implementing the scratch-isolation helper, scoring module, trial-record
   schema/store, and `plan-048` policy functions described in the Objective.
2. A design/methodology artifact (e.g. `docs/artifacts/golden-live-harness-v1.md`) documenting: how
   trial isolation works, the trial-record schema, and an explicit mapping from each `plan-048` §7
   policy statement to the function/module that implements it (so a future reader can verify the
   code matches the decided policy without re-deriving it).
3. At least one real, live-dispatched trial run through the new code (Objective item 5), with its
   result compared explicitly against the equivalent already-recorded historical trial — report
   agreement or divergence honestly; a divergence is a real, disclosable finding about the new code
   or about live-session non-determinism, not something to paper over.
4. Tests proving the harness's own non-dispatch logic (scratch-isolation setup, scoring, trial-record
   schema, `plan-048` policy classification/escalation functions) is correct, using recorded/
   synthetic trial data — not live agent sessions — wired into `python3 tests/run.py`'s default
   tier. Any test that genuinely requires a live dispatch should be opt-in/gated, mirroring this
   repo's established `EMAGE_*`-env-var-gated pattern, and is expected to be rare given item 3's
   scope.

## Acceptance Criteria

1. Real, committed code exists for the scratch-isolation helper, the `expect.py`-reuse scoring
   module, the trial-record schema/store, and `plan-048`'s decided k/escalation/floor-tolerance
   policy as callable functions — not restated as documentation only.
2. `devops-engineer`'s tool grant is unchanged by this task, and no live trial in this task's own
   deliverable was dispatched via any mechanism other than the orchestrator's existing in-process
   `Agent` tool.
3. `tests/golden/**` and `scripts/scorecard.py` are untouched; if any exception was genuinely
   required, it was disclosed and explicitly approved before the edit, not applied unilaterally.
4. At least one live trial was run through the new code and its result compared against an existing
   historical trial for the same case/arm, with agreement or divergence reported honestly.
5. No paid/recurring-cost API call was made without explicit prior authorization.
6. `python3 tests/run.py` passes with no regressions.
7. Your completion report states plainly that this task does not itself expand the evidence base
   (`plan-048` §6 items remain separately, not-yet-dispatched follow-ups) and does not itself
   perform T456's ship/no-ship measurement — that remains T456's own re-dispatch, now able to use
   this task's code instead of by-hand execution.
8. Coding standards and Conventional Commits followed; branch pushed, MR opened against `develop`,
   not self-merged.

## Blocker Protocol

Report any blocker with `type` (`technical` | `dependency` | `unclear_requirements` | `external`)
and `severity` (`critical` | `major` | `minor`) per `AGENTS.md`'s Blocker Protocol. Max 2 retries
before escalating to the orchestrator. Specific cases already anticipated:

- If `expect.py`'s existing contract genuinely cannot be pointed at a scratch directory without a
  protected-path edit: report `type: unclear_requirements`, `severity: major`, with the smallest
  possible proposed exception — do not silently fork or copy the logic instead. (Not expected: every
  trial so far has used this exact pattern successfully without needing one.)
- If reproducing `plan-048`'s stated base rate (2 of 11, 18%) from the historical trials' informal
  records proves genuinely ambiguous (e.g. a trial's category classification was judgment-based and
  not cleanly re-derivable from what was recorded): report `type: unclear_requirements`,
  `severity: minor` and propose your best-justified reading rather than blocking — this is expected
  to be imperfect given the records were prose, not structured data, which is exactly the gap this
  task's trial-record schema exists to close going forward.
- If, once you've read `devops-engineer.md`'s actual current tool grant, the non-dispatch scope this
  brief assigns still doesn't fit (e.g. a genuinely necessary capability beyond `read, search, edit,
  execute, web` that this brief did not anticipate): report `type: technical`, `severity: major` —
  do not request an `agent`-tool widening as the proposed fix; propose a narrower, scoped addition
  instead, or flag that the split-ownership model itself needs revisiting.

## Execution notes

(To be filled in by the implementing agent during work, if useful — not required.)
