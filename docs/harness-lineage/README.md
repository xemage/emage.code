# Harness Lineage

**Based on:** `docs/tasks/task-T506.md` (`plan-035-roadmap-v7-ground-up.md`'s nominal `T465`,
`docs/plans/plan-055-phase6-closed-loop-rescoped-detailed-planning.md` §4's `T465-equiv` row);
`AGENTS.md` "Artifact Versioning" section (the immutable-versioning convention this directory's
own naming scheme follows).

## Purpose

This directory holds a durable, human-readable record of *what actually happened* each time a
`@meta-improver`-generated harness-change proposal (a `DiffProposal`, per
`implementation/runtime/meta_improver.py`) is accepted and merged via Phase 6's human MR gate
(T505/`T464-equiv`). It is not a substitute for git history of the harness-surface files
themselves — it exists to connect a specific accepted change back to:

1. the specific failure(s) that motivated it (`docs/artifacts/failure-taxonomy-v1.md`'s
   `cause`/`behavior`/`mechanism` scheme), and
2. the measured before/after result
   (`implementation/runtime/golden_harness/promotion.py`'s `PromotionResult`).

This is the literal acceptance criterion `plan-035` §2.4 Phase 6 states for `T465`: *"Harness
lineage: `docs/harness-lineage/harness-v<N>.md` — what changed, which failure motivated it,
before/after scorecard."*

## Files in this directory

| File | Purpose |
|---|---|
| `_template.md` | The structural template every real `harness-v<N>.md` document must follow. Start here when authoring a new real instance. |
| `_example-illustrative.md` | A clearly-labeled, entirely fictional worked example demonstrating the template's shape. **Never a real record — see its own disclosure banner.** |
| `harness-v<N>.md` (none yet) | Real instances, one per accepted change. See naming convention below. Does not exist yet as of this directory's creation (2026-09-18) — no real, disclosable accepted change has occurred yet; see `docs/tasks/task-T506.md`'s completion report for the current status. |

## Naming and versioning convention

Real instances are named `docs/harness-lineage/harness-v<N>.md`, `<N>` a strictly increasing
integer starting at `1`, one file per accepted change (not per proposal — only proposals that are
actually accepted and merged via the human MR gate get a real instance).

Per `AGENTS.md`'s "Artifact Versioning" section, these are **immutable artifacts**: once
`harness-v<N>.md` is written, it is never edited or overwritten. If a later correction is needed
(e.g. an MR initially recorded as merged is later reverted, or a reviewer name was wrong), author a
new `harness-v<N+1>.md` that documents the correction and explicitly references the prior version
it supersedes — do not edit the prior file in place.

Files prefixed with `_` (`_template.md`, `_example-illustrative.md`) are not versioned instances —
the leading underscore is a deliberate naming signal that these are structural/reference files, not
real lineage records, and they fall outside the `harness-v<N>.md` glob pattern any future tooling
or human reader scanning this directory for real instances should use.

## Authoring a new real instance

1. Confirm a real, disclosable accepted change exists: a `DiffProposal` (from
   `implementation/runtime/meta_improver.py`) has been approved and merged via T505's human MR gate
   mechanism.
2. Copy the structure of `_template.md` into a new `harness-v<N>.md`, where `<N>` is one greater
   than the highest existing real instance's `<N>` (or `1` if none exist yet).
3. Populate every section with real values only — the real `DiffProposal` fields, the real
   `docs/artifacts/failure-taxonomy-v1.md` case id(s) and axis triple, the real `PromotionResult`
   fields, the real MR number/URL and merge status, and the real approving reviewer.
4. State explicitly whether the referenced MR is merged or still open — never imply a merge that
   has not happened.
5. Never copy fictional content from `_example-illustrative.md` into a real instance.
