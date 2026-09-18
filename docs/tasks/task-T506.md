# Task T506 — Harness lineage document: what changed, which failure motivated it, before/after
scorecard (`plan-035` nominal `T465`)

**Owner:** Technical Writer
**Status:** in_progress
**Priority:** P1
**Depends on:** none hard (per `plan-055` §4's own sequencing note: "T465-equiv can be authored in
parallel with T464-equiv"). Soft, optional dependency: T505 (in progress — if its own live
validation exercise produces a real, disclosable MR before this task needs a worked example, this
task may cite it as one)
**Created:** 2026-09-18
**Based on:** `docs/plans/plan-055-phase6-closed-loop-rescoped-detailed-planning.md` §4's
`T465-equiv` row ("Harness lineage document per accepted change... Technical Writer... Note (not a
blocker): this repo's own ledger (T379/T380) shows Technical Writer sessions have twice lacked
Bash tool access and needed orchestrator assistance for mechanical steps... worth the orchestrator
budgeting a little of its own time for this task rather than assuming a fully autonomous
hand-off") and §5's artifact-flow diagram; `docs/plans/plan-059-t505-t506-dispatch-plan-coverage.md`
(this task's own minimal plan-coverage backing document); `docs/plans/
plan-035-roadmap-v7-ground-up.md` §2.4 Phase 6, T465 row, quoted verbatim below; `docs/tasks/
task-T505.md` (the sibling task this task's one real worked example, if any, would come from).

**`plan-035` §2.4 Phase 6, T465 row, quoted verbatim (the literal acceptance criterion this task
must implement exactly):** *"Harness lineage: `docs/harness-lineage/harness-v<N>.md` — what
changed, which failure motivated it, before/after scorecard."*

**Do not treat `plan-035` §2.4 Phase 6's own introductory prose (`implementation/sia/`,
`sia-executor.py`, reward shaping/harness capture/reward attachment "already exist") as a scoping
instruction for this task**, for the same reason `task-T503.md`/`task-T504.md`/`task-T505.md`
disclosed: that prose describes a different, invalidated RL/fine-tuning subsystem this task has no
dependency on.

## Why this task exists

Phase 6's closed loop (taxonomy → proposal → validation → human MR gate) needs a durable, readable
record of *what actually happened* each time a proposal is accepted and merged — not just the git
history of the harness-surface files themselves, but a human-readable narrative connecting a
specific accepted change back to the specific failure(s) that motivated it and the measured
before/after result. This is the literal acceptance criterion `plan-035` states for T465: "what
changed, which failure motivated it, before/after scorecard."

## What this task builds

1. **A template**, `docs/harness-lineage/_template.md` (this directory does not exist yet on
   `develop` — you are creating it), defining the structure every future
   `docs/harness-lineage/harness-v<N>.md` document must follow. At minimum, the template must have
   sections for:
   - **What changed** — the target file, and a summary of the actual diff (may embed or link to the
     real `diff_text()` output from the accepted `DiffProposal`).
   - **Which failure motivated it** — the triggering case id(s) (`DiffProposal.based_on`) and the
     cluster's axis triple (`cause`/`behavior`/`mechanism`, per `implementation/runtime/
     meta_improver.py`'s `FailureCluster`) — cite `docs/artifacts/failure-taxonomy-v1.md`'s scheme
     directly, do not reinvent a different taxonomy for this document.
   - **Before/after scorecard** — the real `PromotionResult` fields (`floor_met`,
     `no_critical_regression`, `evaluator_hash_unchanged`, and the underlying pass-rate numbers if
     available) from `implementation/runtime/golden_harness/promotion.py`'s T504 output, presented
     as a real before/after comparison, not just a pass/fail restatement.
   - **MR reference** — the real MR number/URL that carried the change (T505's mechanism), and the
     merge commit SHA once merged.
   - **Date and accepting reviewer** — who approved the merge (per `plan-035`'s own literal T464
     acceptance criterion: "no path exists by which a proposal reaches `develop` without human
     approval" — this document is part of that human-approval trail's own record, not a separate,
     independent claim).
2. **A real instance, `docs/harness-lineage/harness-v1.md`, IF AND ONLY IF a real, disclosable
   accepted change exists by the time you do this work.** Check directly with the orchestrator (or
   read `docs/tasks/task-T505.md`'s own status/closure notes and the real MR it references, if any)
   before deciding: if T505's live validation exercise has produced a real MR the orchestrator has
   disclosed as usable for this purpose, use it as this task's one real worked example, following
   the template exactly, and state explicitly in the document whether the referenced MR is merged or
   still open (do not claim it is merged if it is not). **If no such real example exists yet, do not
   fabricate one.** In that case, produce a clearly-labeled illustrative example instead — see next
   point.
3. **If no real example is available: a clearly-labeled illustrative/template-only example**, e.g.
   `docs/harness-lineage/_example-illustrative.md`, following the same template, populated with
   plausible-but-explicitly-fictional content, headed with an unambiguous disclosure banner (e.g.
   "**This is an illustrative example only. No real accepted change is recorded here — see
   `_template.md` for the structure a real instance must follow.**"). This must never be named
   `harness-v1.md` or any `harness-v<N>.md` pattern, since that naming is reserved for real accepted
   changes only — a future reader must never be able to mistake the illustrative file for a real
   lineage record.
4. **A short pointer/index note** (e.g. a `docs/harness-lineage/README.md`, or folded into the
   template's own header — your call) explaining the directory's purpose, the `harness-v<N>.md`
   naming convention (per `AGENTS.md`'s own "Artifact Versioning" convention: immutable, new
   versions never overwrite old ones), and pointing to `_template.md` for anyone about to author a
   new real instance.

## A known, disclosed friction — budget for it, do not assume full autonomy

This repo's own ledger (`docs/tasks/task-T379.md`/`task-T380.md`) records Technical Writer
sessions twice lacking Bash tool access and needing orchestrator assistance for mechanical git
steps (branch creation, commits, pushes, opening the MR). Confirm your own real tool grant directly
at the start of this task (do not assume); if you find yourself needing a git/Bash operation you
cannot perform, report it as a `dependency`-type blocker immediately rather than stalling silently —
the orchestrator has already budgeted time for this and will assist with the mechanical git steps
(branch creation, commit, push, MR open) if your tool grant does not include `execute`.

## Inputs

- `docs/artifacts/failure-taxonomy-v1.md` (T415) — the real `cause`/`behavior`/`mechanism` scheme
  this document's "which failure motivated it" section cites directly, not a reinvented scheme.
- `implementation/runtime/meta_improver.py` (T503, full) — `DiffProposal`, `FailureCluster` shapes.
- `implementation/runtime/golden_harness/promotion.py` (T504, full) — `PromotionResult` shape, the
  source of this document's "before/after scorecard" section.
- `docs/tasks/task-T505.md` (this dispatch's sibling task) — the human-MR-gate mechanism whose real
  or illustrative output this document records.
- `docs/artifacts/phase6-kill-switch-v1.md`, `docs/artifacts/meta-improver-v1.md`,
  `docs/artifacts/promotion-rule-v1.md` — style precedent for this task's own new documents.
- `AGENTS.md` "Artifact Versioning" section — the immutable-versioning convention this document's
  own naming scheme (`harness-v<N>.md`, never overwritten) must follow.

## Constraints

- Token budget: `medium` (per `plan-035`'s own original estimate, unchanged by `plan-055`) —
  recommendation, not a hard ceiling.
- File ownership: this task may only create/modify files under `docs/harness-lineage/**`, plus its
  own `docs/tasks/task-T506.md` status field.
- **Never present an illustrative example as a real accepted change.** If no real example exists at
  the time you do this work, disclose that plainly per point 3 above — do not imply completion of a
  real harness cycle that has not happened.
- Do not touch `.mcp.json`, `tests/golden/**`, `scripts/scorecard.py`,
  `docs/benchmarks/tb-subset.*`. Do not touch or branch from
  `feature/T475-codex-platform-integration` — unrelated, in-flight work.
- Do not build any part of T505's own mechanism (the MR-gate module/tests) — separate, parallel
  task; this task only documents its output.
- Commit your work normally to your own dedicated worktree/branch (already created off `develop`
  for this task, following this repo's standard per-agent-per-task naming convention). Push it and
  open a merge request against `develop`, then stop — do not
  merge it yourself. If you lack `execute`/Bash tool access to perform the git steps, report this
  immediately as a `dependency` blocker rather than stalling — the orchestrator will assist.

## Expected outputs

1. `docs/harness-lineage/_template.md` — the template.
2. `docs/harness-lineage/harness-v1.md` — a real instance, only if a real, disclosable accepted
   change exists (see point 2 above); otherwise omitted.
3. `docs/harness-lineage/_example-illustrative.md` — a clearly-labeled illustrative example,
   present if and only if point 2's real instance is not produced.
4. A short pointer/index note explaining the directory and naming convention.
5. A short completion report (in your final message back to the orchestrator) stating: exact file
   paths produced, and explicit confirmation of whether the worked example used is real (citing the
   real MR) or illustrative (explicitly disclosed as such).

## Acceptance criteria

- [ ] `docs/harness-lineage/_template.md` exists with sections for "what changed," "which failure
      motivated it" (citing the real taxonomy scheme), "before/after scorecard" (citing real
      `PromotionResult` fields), "MR reference," and "date and accepting reviewer."
- [ ] Exactly one of: a real `docs/harness-lineage/harness-v1.md` instance (only if a real
      disclosable accepted change exists, correctly stating whether the cited MR is merged or still
      open) OR a clearly-labeled illustrative example under a name that cannot be mistaken for a
      real `harness-v<N>.md` instance.
- [ ] No file outside `docs/harness-lineage/**` is modified (plus this task's own
      `docs/tasks/task-T506.md` status field).
- [ ] No real accepted change is fabricated or misrepresented as real.
- [ ] `python3 tests/run.py` passes with no new failures relative to the pre-task baseline on
      `develop`.

## Blocker protocol

Report blockers with type (`technical` | `dependency` | `unclear_requirements` | `external`) and
severity (`critical` | `major` | `minor`). If you cannot determine whether a real, disclosable
accepted change exists (e.g. T505's status is unclear from `docs/tasks/task-T505.md` alone), ask the
orchestrator directly rather than guessing — do not default to fabricating a "real" example out of
convenience. If you lack Bash/`execute` tool access for the mechanical git steps, report this
immediately as a `dependency` blocker (not `technical`) — this is a known, budgeted-for friction,
not a surprise, and the orchestrator will assist.
