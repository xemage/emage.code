# Task T503 — `@meta-improver`: failure cluster → diff proposal, never an applied edit
(`plan-035` nominal `T462`)

**Owner:** backend-developer (build phase); **orchestrator** (live end-to-end validation phase —
see "Split ownership" below)
**Status:** in_progress
**Priority:** P0
**Depends on:** T501 (done — `implementation/runtime/golden_harness/failure_taxonomy.py`, the real
taxonomy-query module this task consumes)
**Created:** 2026-09-18
**Based on:** `docs/plans/plan-055-phase6-closed-loop-rescoped-detailed-planning.md` §4's
`T462-equiv` row ("consumes a failure cluster, emits the smallest viable harness change as a diff
proposal, never an applied edit... Genuinely greenfield — no existing code found anywhere in this
repo. Correctly stays 'large'") and §5's artifact-flow diagram (`T461-equiv (wiring) ──> T462-equiv
(build: proposal schema + @meta-improver)`, live dispatch orchestrator-executed); `docs/artifacts/
phase6-sia-readiness-audit-v1.md` §5 item 2 ("`@meta-improver` itself does not exist in any form...
genuinely greenfield work, correctly scoped 'large'") and §6 (the tool-grant split-ownership
reasoning this task's own dispatch applies); `implementation/runtime/golden_harness/
failure_taxonomy.py` (T501, real, merged, tested — `FailureTaxonomy.load()`, `all_records()`,
`get()`, `filter_by()`, the `FailureRecord` dataclass) — this task's real, concrete input.

**Do not treat `plan-035` §2.4 Phase 6's own introductory prose (`implementation/sia/`,
`sia-executor.py`, reward shaping/harness capture/reward attachment "already exist") as a scoping
instruction for this task.** Per the audit's primary finding, that prose describes a different,
invalidated RL/fine-tuning subsystem this task has no dependency on and must not import from,
reference, or reuse (including `reward_shaping.py`'s continuous blended-reward pattern — see
`plan-055` §6 risk table's explicit warning against pulling that pattern into a binary
promote/reject-shaped generator by convenience). This task's real dependency is
`implementation/runtime/golden_harness/failure_taxonomy.py` alone.

## Why this task exists, and why "never an applied edit" is the one property that matters most

Phase 6's eventual closed loop needs something that turns a cluster of related, already-classified
failures into a concrete, reviewable suggestion for how the harness (this repo's own agent
definitions, skills, commands, instructions — not application code) should change. This task builds
that generator. It does **not** build anything that applies the suggestion. T464-equiv (the human
MR gate) is the only path a proposal can ever take toward `develop`, and that task does not exist
yet — there is currently **no downstream consumer that could safely apply a proposal even if one
existed**, so this module must be architecturally incapable of doing so itself.

This is the safety-critical invariant of this entire task, and it must be a **proven property**,
not a documented intention: this module must be **architecturally incapable** of writing to any
real repository file, provable by a real, committed, adversarial test — mirroring the rigor T502's
kill switch applied to its own "cannot self-resume" guarantee. "The code doesn't currently call
`write_text`" is not sufficient; the test must actively try to make the generator write somewhere
it shouldn't (or apply a proposal to a real path) and confirm it cannot.

## Split ownership (applied pre-emptively, not discovered mid-task)

This repo has hit the same tool-grant gap at least 9 times (`T410/T415/T418/T420/T430/T440/T451/
T456/T458`, plus `T499`): an agent is asked to do live-dispatch work its own tool grant cannot
reach. `plan-055` §4 applies the fix in advance for this task:

- **`backend-developer`** (tool grant re-confirmed this dispatch: `Read, Edit, Write, Bash,
  WebFetch, WebSearch, mcp__fetch` — no `agent` tool) builds everything in this brief: the proposal
  schema, the clustering logic, the generation mechanism, and the adversarial "never writes" test
  suite.
- **The orchestrator**, not `backend-developer`, performs at least one real end-to-end validation
  cycle once the code exists: take a real failure record (or cluster) from T501's actual taxonomy
  data, run it through the built generator directly (a plain Python invocation — importing and
  calling the module, not spawning a nested agent session), and independently inspect the resulting
  `DiffProposal` for plausibility. Generating a proposal from already-classified failure data does
  not require an LLM-driven session in this task's own design (see "Generation mechanism" below) —
  if, once the real code exists, one plausible proposal genuinely turns out to require a live
  nested dispatch after all (e.g., to have an LLM draft actual diff prose), the orchestrator will
  make that call at review time rather than assuming it in advance either way, per the dispatch
  instruction this task itself was given.

## A scoping decision made here, not left ambiguous: `@meta-improver` is a Python module, not a
## new registered Claude subagent

`plan-055` §4 describes this task as matching "the `@context-retriever`/T454 precedent for building
a new agent + supporting code." T454 built a full 28th registered subagent: a new
`implementation/knowledge/agents/context-retriever.md` definition, projected across all 7 platforms
via `sync.mjs`, plus a `deploy/docker-compose-context-retriever.yml` manifest and a supporting
Python wrapper module. **This task deliberately does not follow that precedent in full**, and this
is a disclosed scoping decision, not an oversight:

A registered Claude subagent has a `tools:` grant. `context-retriever`'s own precedent is
deliberately read-only-safe by construction (a read-only wrapper). But registering `@meta-improver`
as a dispatchable subagent would put pressure toward giving it enough tool access to actually be
useful as an interactive LLM session (at minimum `Read`, likely `Edit`/`Write` if it is ever asked
to "just fix it" in a future session) — and that is exactly the shape of risk this task exists to
prevent. Proving "architecturally incapable of writing" is far more tractable for a plain Python
library (no tool grant to reason about at all — the question reduces to "does this module's own
source code ever call a filesystem-mutating function") than for a registered agent definition whose
safety depends on a `tools:` YAML line never being loosened later.

**Decision: `@meta-improver` is built as a Python module and query/generation API under
`implementation/runtime/`, callable directly (imported and invoked as a function call — by the
orchestrator today, and by a future T463-equiv/loop-runner later), not as a new
`implementation/knowledge/agents/meta-improver.md` registered subagent.** The `@meta-improver` name
from `plan-035`/`plan-055` is used here as this module's conceptual/documentary name (e.g. in its
own docstring and in `docs/artifacts/meta-improver-v1.md`), not as an instruction to run
`sync.mjs`/`generate-registry.py` or touch any platform-projection folder. If you (the implementer)
find during the build that a registered-subagent form is genuinely necessary for some reason this
scoping reasoning missed, stop and report it as an `unclear_requirements` blocker before building
one — do not silently add a 28th agent registration as a side effect of this task.

## Objective

Build a real, tested Python module, under your own choice of location inside
`implementation/runtime/**` (a reasonable default, mirroring T501's own placement, is a new
sibling module or package next to `golden_harness/`, e.g. `implementation/runtime/
meta_improver.py` or `implementation/runtime/meta_improver/` — document your choice), that:

1. **Defines a proposal schema** — a frozen, immutable dataclass (or small set of dataclasses)
   representing a "diff proposal" as pure, inert data: at minimum, the target file path, the
   target file's declared class (see point 2), a human-readable rationale, the actual proposed
   change (a real diff/patch representation, or a base-content + proposed-content pair — your
   call, document it, but it must be enough for a human reviewer to understand exactly what would
   change), and the triggering failure record(s) it is based on (by `case_id`, referencing
   `FailureRecord`/`FailureTaxonomy`, not duplicating their data). **This dataclass and every
   object graph it can produce must expose no method that performs a real filesystem write, `git`
   subprocess call, or any other repository-mutating operation.** It is data, not an action.
2. **Validates target-path eligibility at construction time, as a first layer of defense.** A
   proposal may only target files under: `implementation/knowledge/agents/*.md`,
   `implementation/knowledge/skills/*/SKILL.md`, `implementation/knowledge/commands/*.md`,
   `implementation/knowledge/instructions/*.md` — this repo's actual harness surface (agent
   definitions, skills, commands, instructions), not application code, and never
   `tests/golden/**` or `scripts/scorecard.py`. State explicitly, in the module's own docstring
   or the documentation artifact (point 5 below), which file classes may be targeted and why
   these four and no others. A proposal naming any other path (including the two explicitly
   protected ones) must be **rejected at construction time** (raise, do not silently accept) —
   this is a first layer only; full enforcement is T463-equiv's separate, not-yet-built job (see
   `docs/artifacts/protected-paths-v1.md` §2 item 2), but this module must not even be *capable*
   of producing a proposal naming a disallowed path.
3. **Forms failure clusters from `FailureTaxonomy` data.** Your own design decision (T461's brief
   deferred "clustering" as exactly this task's job to decide) — a reasonable minimal approach:
   group `taxonomy.all_records()` by shared `(cause, behavior, mechanism)` triple, since that is
   exactly the query `filter_by()` already supports. Document whichever approach you choose and
   why. A cluster of size 1 (a failure sharing no axis triple with any other) is a valid, expected
   output, not an error.
4. **Generates a `DiffProposal` for a given cluster — the "emits" mechanism.** This is the other
   major open design question this task decides. A reasonable default, given the constraints
   above (no live LLM dispatch required for this task, per "Split ownership"): a deterministic,
   rule-based/template generator that, given a cluster's axis values and triggering case IDs,
   selects a target file (document your target-selection heuristic explicitly — a simple,
   deterministic heuristic such as keyword/substring matching between the cluster's axis values
   and existing knowledge-base file titles/content is acceptable; it does not need to be
   sophisticated, it needs to be deterministic, documented, and testable) and proposes a small,
   concrete addition (e.g., a "Known failure pattern" note citing the cluster's `cause`/
   `behavior`/`mechanism` and the triggering case IDs) as the proposed diff content. If, once you
   have built the schema and clustering logic, you conclude a template-based generator cannot
   produce a genuinely plausible proposal and a live LLM dispatch is actually required to draft
   diff content, **stop and report this as a `technical` blocker** rather than either building a
   nested live-dispatch call yourself (you have no `agent` tool to do so safely) or silently
   shipping a low-quality generator — the orchestrator will decide how to proceed.
5. **Produces a short design-decision document**, `docs/artifacts/meta-improver-v1.md` (mirroring
   T502's `phase6-kill-switch-v1.md` precedent), stating: the proposal schema shape and why, the
   allowed target file classes and why, the clustering approach and why, the generation mechanism
   and its target-selection heuristic and why, and this task's own "Python module, not registered
   subagent" scoping decision reproduced from this brief's own section above (state it as your own
   documented decision, not merely as a citation back to this brief).

## The adversarial "never writes" test — the actual proof, not an assertion

A committed test suite must include, at minimum:

1. **A static/source-level scan** of the generator module's own source (e.g. via Python's `ast`
   module, walking every `Call` node) asserting **zero** occurrences of: `open(...)` with a
   write-capable mode (`"w"`, `"a"`, `"x"`, or any mode string containing those), `Path.write_text`/
   `Path.write_bytes`/`Path.unlink`, `os.remove`/`os.rename`/`os.replace`, any `shutil.*` call, and
   any `subprocess`/`os.system` invocation whose arguments could plausibly include `git apply`,
   `git commit`, or `git checkout`. This must scan the actual module file(s) this task adds, not a
   hypothetical/idealized version of them.
2. **A behavioral, real-filesystem test**: snapshot the repository's tracked-file state (e.g.
   `git status --porcelain` plus a content hash of every file the generator's target-eligibility
   allowlist could plausibly touch) before running the full pipeline (load T501's real taxonomy →
   cluster → generate proposals for every cluster) against the real on-disk
   `docs/benchmarks/failures/**` data, then re-snapshot after, and assert **byte-identical** —
   nothing on disk changed as a side effect of generating proposals.
3. **A rejection test proving the first-layer defense-in-depth control from Objective point 2**:
   construct (or attempt to construct) a proposal targeting `tests/golden/held-out/some-file.md`
   and separately one targeting `scripts/scorecard.py`, and confirm both are rejected (a raised
   exception, not a silently-produced proposal object) — this is the module's own test of its own
   guard, independent of and in addition to T463-equiv's future, separate enforcement layer.
4. **A real-data functional test**, following the `tests/functional/test_golden_harness_*.py`
   naming precedent, that loads the real T501 taxonomy from `docs/benchmarks/failures/**`, forms
   at least one real cluster, generates at least one real `DiffProposal` from it, and asserts
   specific, correct values (not a tautological "returns something non-empty" check) — the
   proposal's `based_on` case IDs match the real cluster's real case IDs, the target path is one
   of the four allowed classes, and the rationale/diff content references the real cluster's real
   axis values.

## Held-out isolation

Same discipline as every prior task touching this data: your new files only read already-redacted,
already-committed `docs/benchmarks/failures/**` content (via T501's module, which already handles
this correctly) and `implementation/runtime/golden_harness/failure_taxonomy.py`'s own public API.
Grep any new file you add for real held-out case identities (you don't need to know them —
`tests/functional/test_golden_held_out_isolation.py`'s own guard already does) and re-run that
guard after adding your files to confirm it still passes.

## Inputs

- `implementation/runtime/golden_harness/failure_taxonomy.py` (T501, full — this task's real,
  concrete, tested input; read the `FailureRecord`/`FailureTaxonomy` docstrings in full, including
  their own explicit scope-boundary notes).
- `implementation/runtime/golden_harness/{policy,scoring,schema}.py` and `tests/functional/
  test_golden_harness_failure_taxonomy.py` — style/testing precedent for this area of the codebase.
- `docs/artifacts/protected-paths-v1.md` (full) — style precedent for how this repo documents a
  standing safety control, and the authoritative source for exactly which two paths are protected
  and why (do not reinvent this list; reproduce it exactly).
- `docs/artifacts/phase6-kill-switch-v1.md` (T502, full) — style precedent for this task's own
  "prove the safety property with an adversarial test" documentation approach.
- `docs/plans/plan-055-phase6-closed-loop-rescoped-detailed-planning.md` §4 (T462-equiv row) and
  §5 (artifact-flow diagram) — full context for this task's place in the larger Phase 6 sequence.

## Constraints

- Token budget: this is explicitly scoped "large" per `plan-055` — do not force it into a `medium`
  budget. Report genuine progress if it runs long rather than rushing to a shallow "done."
- File ownership: this task may only create/modify files under `implementation/runtime/**`,
  `tests/functional/**` (and/or `tests/unit/**` if that better fits the adversarial static-scan
  test's own nature — your call), `docs/artifacts/**` (its own new `meta-improver-v1.md`), plus its
  own `docs/tasks/task-T503.md` status field.
- Protected paths — do not touch, no exceptions: `tests/golden/**`, `scripts/scorecard.py`,
  `.mcp.json`, `docs/benchmarks/tb-subset.*`. Do not touch or branch from the
  `feature/T475-codex-platform-integration` branch — it is unrelated, in-flight work.
- Do not run `sync.mjs` or `generate-registry.py`, and do not add any file under
  `implementation/knowledge/agents/`, any platform's agent-projection folder, or
  `implementation/registry/` — per this brief's own "Python module, not registered subagent"
  scoping decision above.
- Do not build any part of T463-equiv (the evaluator-hash tamper-evidence check, the promotion
  rule, or any live before/after golden-suite comparison run), T464-equiv (the MR gate), or
  T465-equiv (the lineage document) — all remain separate, not-yet-dispatched future tasks.
- Do not import, call, or reuse anything from `implementation/sia/`, `implementation/adapters/
  sia-target/` (including `reward_shaping.py`'s blended-reward pattern), or `implementation/
  scripts/sia-executor.py`.
- Commit your work normally to your own dedicated worktree/branch (`agent/backend-developer/T503`,
  already created off `develop`). Push it and open a merge request against `develop`, then stop —
  do not merge it yourself.
- No self-merge, no exceptions for content type: work only in your own dedicated worktree/branch.
  Do not merge anything, including into your own branch from elsewhere, and do not merge the MR you
  open. The orchestrator (top-level session) merges after independent review.

## Expected outputs

1. A new Python module (or package) under `implementation/runtime/**` implementing the proposal
   schema, target-path validation, clustering, and generation mechanism described above.
2. A new test file (or files) under `tests/functional/**`/`tests/unit/**` implementing the four
   required test categories above (static scan, behavioral no-write-side-effect, rejection,
   real-data functional).
3. `docs/artifacts/meta-improver-v1.md` documenting every design decision per the Objective
   section's point 5.
4. A short completion report (in your final message back to the orchestrator) stating: exact
   module/test/doc paths chosen, the generation-mechanism heuristic chosen and why, explicit
   confirmation the held-out isolation guard still passes, and explicit confirmation of the
   adversarial "never writes" test's actual pass result (not merely that it exists).

## Acceptance criteria

- [ ] A real, tested `DiffProposal`-shaped dataclass exists, exposing no filesystem-mutating
      method anywhere in its own definition or any helper it calls.
- [ ] Target-path validation rejects any proposal naming a path outside the four allowed harness
      file classes, proven by a real test including both explicitly-named protected paths
      (`tests/golden/**`, `scripts/scorecard.py`).
- [ ] A real, documented clustering function groups real T501 taxonomy records into failure
      clusters, proven by a real test against real on-disk data.
- [ ] A real, documented generation function produces at least one real, plausible `DiffProposal`
      from a real cluster of real taxonomy data, proven by a real functional test with specific
      (non-tautological) assertions.
- [ ] The static AST-scan test passes, finding zero filesystem-mutating calls in the new module(s).
- [ ] The behavioral before/after-snapshot test passes, proving zero real filesystem side effects
      from running the full generate pipeline.
- [ ] `tests/functional/test_golden_held_out_isolation.py` passes after this task's files are
      added (re-run fresh, not assumed).
- [ ] No file outside this task's declared file-ownership boundary is modified. Zero hits on any
      protected path. No new file under `implementation/knowledge/agents/`, any platform
      agent-projection folder, or `implementation/registry/`.
- [ ] `python3 tests/run.py` passes with no new failures relative to the pre-task baseline on
      `develop`.
- [ ] `docs/artifacts/meta-improver-v1.md` exists and documents every design decision listed in
      Objective point 5.

## Blocker protocol

Report blockers with type (`technical` | `dependency` | `unclear_requirements` | `external`) and
severity (`critical` | `major` | `minor`). If the "never an applied edit" guarantee turns out to be
harder to prove airtight than this brief anticipates, or you find a genuine ambiguity in what
counts as an acceptable proposal target, report it as a real blocker rather than picking an
interpretation and hoping it's right — this is the single most safety-relevant piece of Phase 6
built so far, per the orchestrator's own explicit instruction for this task. If you find any
existing partial diff-proposal/weakness-clustering mechanism already in this repo that this brief's
own research missed, report it as a `dependency` blocker before building a duplicate.
