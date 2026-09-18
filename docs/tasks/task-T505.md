# Task T505 — Human gate: proposals open a merge request against `develop`; no auto-merge path
(`plan-035` nominal `T464`)

**Owner:** Release Manager (build phase); **orchestrator** (live end-to-end validation exercise —
see "Orchestrator-owned live validation" below)
**Status:** done
**Closure note (2026-09-18):** all 9 acceptance criteria independently re-verified by the
top-level session before this closure (not accepted on the implementer's self-report alone),
including personally re-running the AST scanner and adversarial tests and personally performing
the live end-to-end validation (real MR !341, opened, reviewed, then closed without merging).
This closes Phase 6's original six-task table in full. See `docs/tasks/completed-tasks.md`'s
`T505` row for the full closure record.
**Priority:** P0
**Depends on:** T504 (done, merged `d405c4e` — `implementation/runtime/golden_harness/promotion.py`,
`PromotionResult`/`evaluate_promotion`, this task's real, concrete required input); T503 (done,
merged — `implementation/runtime/meta_improver.py`, `DiffProposal`, the object whose content this
task's MR carries)
**Created:** 2026-09-18
**Based on:** `docs/plans/plan-055-phase6-closed-loop-rescoped-detailed-planning.md` §4's
`T464-equiv` row ("Human gate: proposals open an MR against `develop`; no auto-merge path...
Release Manager... Unchanged from `plan-035` — tool grant confirmed sufficient, no live-dispatch
requirement, ordinary MR flow already used throughout this repo") and §5's artifact-flow diagram;
`docs/plans/plan-059-t505-t506-dispatch-plan-coverage.md` (this task's own minimal plan-coverage
backing document); `docs/plans/plan-035-roadmap-v7-ground-up.md` §2.4 Phase 6, T464 row, quoted
verbatim below; `implementation/runtime/meta_improver.py` (T503, real, merged, read in full) and
`implementation/runtime/golden_harness/promotion.py` (T504, real, merged, read in full) — this
task's real, concrete inputs; this project's own Git Workflow conventions document (this repo's
real git/GitLab branch-naming and MR conventions, to be reused, not reinvented).

**`plan-035` §2.4 Phase 6, T464 row, quoted verbatim (the literal acceptance criterion this task
must implement exactly):** *"Human gate: accepted proposals open a merge request against `develop`.
No path exists by which a proposal reaches `develop` without human approval."*

**Do not treat `plan-035` §2.4 Phase 6's own introductory prose (`implementation/sia/`,
`sia-executor.py`, reward shaping/harness capture/reward attachment "already exist") as a scoping
instruction for this task**, for the same reason `task-T503.md`/`task-T504.md` disclosed: that
prose describes a different, invalidated RL/fine-tuning subsystem this task has no dependency on.
This task's real dependency is `meta_improver.py` (T503) and `golden_harness/promotion.py` (T504)
alone.

## Why this task exists, and why it is the highest-stakes piece of Phase 6 so far

Every piece of Phase 6 built before this task (`T501`'s taxonomy wiring, `T503`'s `@meta-improver`
generator, `T504`'s validation/promotion rule) was **deliberately, architecturally incapable of
writing to any real, tracked repository file** — `meta_improver.py`'s module docstring states this
as its "one property that matters most," and `promotion.py`'s `apply_proposal_to_scratch` only ever
writes to an isolated scratch directory with a defensive guard against ever resolving to the real
repo tree. **This task is the first point in the entire closed-loop pipeline where a proposal's
content is ever allowed to touch a real, tracked repository file.** Apply the exact same rigor
`T502`/`T503`/`T504` applied to their own safety-critical guarantees — see "The 'no auto-merge
path' property" below, the section that matters most in this brief.

## What this task builds

A function/CLI (your call on the exact shape — a plain importable module mirroring
`meta_improver.py`'s/`promotion.py`'s own "plain Python module, not a registered subagent" pattern
is the natural continuation of this codebase's existing convention, but document whichever choice
you make and why) that:

1. **Takes a `PromotionResult` (T504's real dataclass, `implementation.runtime.golden_harness.
   promotion.PromotionResult`) as an explicit, required input.** Refuses — raises, never silently
   proceeds — if `promotion_result.promote is not True`. A rejected or unevaluated proposal must
   never produce a branch or MR under any code path.
2. **Also takes the `DiffProposal` (T503's real dataclass) the `PromotionResult` was computed for**,
   since the `PromotionResult` itself carries no reference back to the proposal it evaluated
   (confirm this directly by reading `promotion.py` — it does not) and this task needs
   `proposal.target_path`, `proposal.proposed_content`, `proposal.rationale`, `proposal.diff_text()`,
   and `proposal.based_on` to build the branch/commit/MR content. Your function signature should
   accept both explicitly (e.g. `open_promotion_mr(proposal: DiffProposal, promotion_result:
   PromotionResult, ...) -> MrGateResult`), not attempt to smuggle the proposal inside the
   `PromotionResult` or vice versa — keep the two objects' real, already-established shapes intact.
3. **Creates a real branch** off `develop`, following this repo's own real convention
   (this project's own Git Workflow document, "Agent Worktree Branch Naming":
   `agent/<agent-name>/<task-id>`).
   Adapt sensibly for an automatically-generated proposal, since there is no human agent name or
   task ID here — your own call, but document the adapted scheme explicitly in the design doc (a
   reasonable choice: `meta-improver/<proposal-derived-slug>`, deterministic from the proposal's
   `target_path` and first `based_on` case id, so re-running against the same proposal produces a
   recognizable, stable branch name rather than a random one — but this is a suggestion, not a
   mandate; pick what you judge cleanest and justify it).
4. **Commits the proposal's `proposed_content` to its real `target_path`**, and only that path — no
   other file in the branch's diff — using a real Conventional Commit message
   (this project's own Git Workflow document, "Commit Messages") citing the triggering failure case ids
   (`proposal.based_on`) and the rationale (`proposal.rationale`), so the commit message alone
   carries enough context to understand *why* without needing the MR description.
5. **Pushes the branch** to the real remote.
6. **Opens a real merge request against `develop`** (via `glab mr create` or the `mcp__gitlab`
   MCP server — your call, document which and why; `glab mr create` is this repo's own
   already-established real convention, see `docs/tasks/task-T341.md`/`task-T343.md`/`task-T347.md`
   for real prior usage) whose description includes the proposal's own `rationale` and
   `diff_text()` output verbatim, so a human reviewer has everything needed to evaluate it without
   re-deriving context from the taxonomy or the promotion decision.
7. **Then stops.** No further action of any kind on the MR after it is opened.

## The "no auto-merge path" property — the section that matters most in this brief

This is not a documentation requirement. **This property must be architectural, mechanically
provable, and adversarially tested** — mirror `T503`'s own two-independent-proofs discipline for
its "never writes to a real repo file" guarantee exactly:

1. **A static AST scan of this task's own module source**, proving it contains **no call of any
   kind** that merges, approves, or auto-accepts a merge request, and no call that pushes directly
   to `develop`/`main` or merges locally. At minimum, the scanner must detect (and the source must
   contain zero of):
   - `glab mr merge` (any `subprocess`/`os.system` invocation whose argument list contains both
     `"mr"` and `"merge"`, or the literal substring `"mr merge"`)
   - `glab mr approve`
   - Any GitLab REST/GraphQL API call shape that merges or approves an MR (e.g. a request whose URL
     path contains `merge_requests` and either a `/merge` suffix, an `/approve` suffix, or an HTTP
     method (`PUT`/`POST`/`PATCH`) combined with a merge/approve endpoint — whatever shape the
     `mcp__gitlab` MCP server's own merge/approve tool calls take, if you use that server instead of
     `glab`; scan for those call names directly)
     - `git merge` (any `subprocess`/`os.system` call whose argument list contains `"merge"` as a
       `git` subcommand)
     - `git push` with a target ref of `develop` or `main` (a direct push to either protected branch,
       bypassing the MR flow entirely) — this task's own push call must always target its own new
       branch, never `develop`/`main` directly; the scanner should confirm no push call's ref
       argument is a bare `develop`/`main` literal
     - `git push --force`/`git push -f` to any ref
   - Mirror `T503`'s `find_filesystem_mutation_calls`-style scanner shape (parse the module's AST,
     walk `Call` nodes, match against these banned shapes) — this is a proven, precedented pattern
     in this exact codebase, reuse its structure rather than inventing a new one.
2. **Adversarial tests proving the scanner is a real detector, not a no-op that always reports
   clean** — one synthetic violation snippet per banned shape above (mirror
   `test_meta_improver.py`'s `TestNoFilesystemMutation.test_static_scan_detects_a_synthetic_
   violation`'s per-shape-snippet pattern exactly), plus a no-false-positive test against the
   legitimate calls this module *does* need to make (`glab mr create`, `git push <own-branch>`,
   `git commit`, `git checkout -b`) to prove the scanner isn't so broad it would also flag this
   module's own legitimate operations.
3. **A real, load-bearing guard in the function itself**, independent of (and in addition to) the
   AST-scan proof: the `promote is not True` refusal (point 1 above) is the first, most important
   runtime guard, but also confirm your implementation contains no code path — no flag, no
   parameter, no environment variable — that could cause it to merge, approve, or push directly to
   `develop`/`main` even if called with unexpected arguments. If you find yourself needing any such
   parameter for a legitimate reason, stop and report it as a blocker rather than adding it — this
   guarantee must have zero exceptions.

**If you are not confident this guarantee is airtight once implemented — report it as a real
blocker (`technical`, `critical` severity) rather than shipping something you are not sure about.**
This is the explicit standing instruction for this task; do not resolve genuine uncertainty here
unilaterally.

## `PromotionResult` refusal — concrete test requirement

Write a real, specific test proving the refusal is not merely asserted: construct a
`PromotionResult` with `promote=False` (any real, valid combination of the other fields — e.g.
`floor_met=False`) and confirm calling your MR-gate function raises (not merely returns an error
value) **before** any git or GitLab call is attempted — assert via mocking/spying that zero
subprocess/API calls happened in that path, not just that the return value looks like a failure.

## Orchestrator-owned live validation (not part of Release Manager's own completion)

Per this dispatch's own explicit instruction: once this task's code exists and is independently
reviewed, **the orchestrator personally exercises this mechanism for real** — not merely trusts its
unit tests, mirroring the discipline already applied to `T503`/`T504`. Concretely:

1. Generate one real proposal (`meta_improver.generate_proposal`, reusing T503's own real
   `naming-convention-drift` cluster example or a freshly generated one — orchestrator's call at
   execution time).
2. Construct a `PromotionResult` for it — either a real one via `T504`'s `evaluate_promotion`
   against real or clearly-synthetic trial data (disclosed either way), or a hand-built one with
   `promote=True` if that proves cleaner at execution time — orchestrator's own call, to be
   documented in the closure record either way.
3. Run it through this task's real mechanism.
4. Confirm a real branch and a real MR against `develop` are actually produced.
5. **Leave that MR open and unmerged.** Report its number/URL back to the user. The user will
   independently review its actual content and decide whether to merge it as a real (if minor)
   harness improvement, or close it having served its purpose as a validation exercise — that
   decision belongs explicitly to the user, not to Release Manager and not to the orchestrator.

Release Manager's own task does not include performing this validation itself — build the
mechanism, write its own test suite (including the refusal test and the AST-scan/adversarial-test
suite above), open its own build-phase MR against `develop` for the *code*, and stop there.

## Inputs

- `implementation/runtime/meta_improver.py` (T503, full, including `DiffProposal.diff_text()`,
  `DiffProposal.rationale`, `DiffProposal.based_on`).
- `implementation/runtime/golden_harness/promotion.py` (T504, full, including `PromotionResult`'s
  exact field set — note again: it does not reference the `DiffProposal` it was computed for).
- `tests/functional/test_meta_improver.py`'s `TestNoFilesystemMutation` class (T503) — the AST-scan
  + adversarial-test pattern this task's own "no auto-merge path" proof must mirror.
- This project's own Git Workflow conventions document (full) — branch naming, commit message
  format, MR rules; reuse this repo's own real conventions, do not invent a new scheme.
- `docs/tasks/task-T341.md`, `task-T343.md`, `task-T347.md` — real prior examples of `glab mr
  create` usage in this exact repo.
- `docs/artifacts/phase6-kill-switch-v1.md` (T502) and `docs/artifacts/promotion-rule-v1.md` (T504)
  — style precedent for this task's own new design doc.

## Constraints

- Token budget: `medium` (per `plan-035`'s own original estimate, unchanged by `plan-055`) —
  recommendation, not a hard ceiling; report genuine progress honestly if real scope exceeds it.
- File ownership: this task may only create/modify files under `implementation/runtime/
  golden_harness/**` (or a new sibling module if you judge that cleaner — document the choice),
  `tests/functional/**` and/or `tests/unit/**`, `docs/artifacts/**` (its own new file(s) only), plus
  its own `docs/tasks/task-T505.md` status field.
- **Never merge, approve, or auto-accept any MR — including your own build-phase MR.** Open it and
  stop. No self-merge, no exceptions for content type.
- Do not touch `.mcp.json`, `tests/golden/**`, `scripts/scorecard.py`,
  `docs/benchmarks/tb-subset.*`. Do not touch or branch from
  `feature/T475-codex-platform-integration` — unrelated, in-flight work.
- Do not import, call, or reuse anything from `implementation/sia/`, `implementation/adapters/
  sia-target/`, or `implementation/scripts/sia-executor.py`.
- Do not build T506 (the lineage document) — separate, parallel task.
- Do not perform the live validation exercise yourself — that is explicitly the orchestrator's own
  job per "Orchestrator-owned live validation" above; build the mechanism and its own test suite,
  then stop.
- Commit your work normally to your own dedicated worktree/branch (already created off `develop`
  for this task, following this repo's standard per-agent-per-task naming convention). Push it and
  open a merge request against `develop`, then stop — do not merge it yourself, and do not merge
  anything else either.

## Expected outputs

1. The MR-gate module (path and exact shape your own documented call — e.g.
   `implementation/runtime/golden_harness/mr_gate.py`).
2. A design doc (e.g. `docs/artifacts/mr-gate-v1.md`, mirroring `phase6-kill-switch-v1.md`'s
   structure): what it declares, the branch-naming scheme adapted for an automated proposal and why,
   the commit-message format, the MR-description content, the "no auto-merge path" guarantee's full
   proof (both the AST-scan detector shape and the adversarial test list), and what this module does
   not do (scope boundary — e.g. it does not decide promote/reject itself, it does not retry a
   failed push, etc.).
3. New test file(s) covering: the `promote is not True` refusal (with the zero-git/API-calls
   assertion above), the AST scanner's real-source-clean result, the AST scanner's per-banned-shape
   synthetic-violation detection, the AST scanner's no-false-positive result against this module's
   own legitimate calls, and (mocking the actual git/`glab`/GitLab-API calls, since a real test
   suite must not open real MRs on every CI run) a test proving the branch/commit/MR content is
   built correctly from a given `DiffProposal`/`PromotionResult` pair (branch name, commit message
   citing `based_on` and `rationale`, MR description containing both `rationale` and `diff_text()`
   output).
4. A short completion report (in your final message back to the orchestrator) stating: exact
   module/test/doc paths chosen, the exact banned-call-shape list your AST scanner checks for, and
   explicit confirmation of each test category's real pass result.

## Acceptance criteria

- [ ] A real, tested function/CLI exists that takes a `PromotionResult` and its corresponding
      `DiffProposal` as explicit inputs and refuses (raises, before any git/API call) if
      `promotion_result.promote is not True`.
- [ ] When given a promoted result, it produces a real branch (off `develop`, following this repo's
      adapted `agent/<...>`-style convention, documented), a real commit (Conventional Commit format,
      citing `based_on` case ids and `rationale`, touching only `proposal.target_path`), a real
      push, and a real MR against `develop` whose description includes `rationale` and
      `diff_text()`.
- [ ] A static AST scan of the module's own source finds zero call shapes that merge, approve, or
      auto-accept an MR, or that push/merge directly to `develop`/`main`.
- [ ] The AST scanner is proven a real detector via synthetic per-banned-shape violation tests (one
      per shape) and proven not to false-positive against this module's own legitimate calls.
- [ ] `docs/artifacts/mr-gate-v1.md` exists and documents every decision listed in this brief,
      including the full "no auto-merge path" proof.
- [ ] No file outside this task's declared file-ownership boundary is modified. Zero edits to
      `tests/golden/**`, `scripts/scorecard.py`. Zero hits on `implementation/sia/`,
      `implementation/adapters/sia-target/`, `implementation/scripts/sia-executor.py`.
- [ ] `python3 tests/run.py` passes with no new failures relative to the pre-task baseline on
      `develop`.
- [ ] `tests/functional/test_golden_held_out_isolation.py` passes after this task's files are added
      (re-run fresh, not assumed).
- [ ] (Orchestrator-owned, not part of Release Manager's own completion) At least one real,
      end-to-end live validation cycle is independently performed, producing a real, open, unmerged
      MR against `develop`, per "Orchestrator-owned live validation" above.

## Blocker protocol

Report blockers with type (`technical` | `dependency` | `unclear_requirements` | `external`) and
severity (`critical` | `major` | `minor`). **If the "no auto-merge path" guarantee turns out harder
to prove airtight than expected, or you are not confident a given MR-opening mechanism is genuinely
incapable of ever merging on its own, report it as a real blocker rather than shipping something you
are not sure about** — this is the highest-stakes safety property in all of Phase 6 so far, since
this is the first piece that can genuinely alter the real repository if it goes wrong. Do not
resolve that class of uncertainty unilaterally.
