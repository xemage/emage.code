# Checkpoint 035 — T507-T511 arc complete: closed loop proven and hardened; v7.0 release readiness reassessed

> Written by the top-level session immediately after T511's merge. Closes out the arc that began
> with `plan-060`'s review (`docs/plans/plan-060-v7-release-readiness-and-closure.md`) and continued
> through the user's own explicit, sequential instructions ("Scope the promotion.py hardening" →
> "build A + C first" → "Build B"). Mirrors `checkpoint-033`/`034`'s own precedent for a real
> phase/arc boundary.

## Summary

**The v7.0 closed-improvement-loop mechanism has now been run for real, found wanting once, and
hardened against the specific failure mode that surfaced — three times over, each independently
re-verified before merging.** `T507` ran the loop end-to-end for the first time and got a
`promote=True` result on a proposal that was almost certainly not a genuine improvement. `T509`
diagnosed why (real, code-level findings, not speculation). `T510` and `T511` built all three of
`T509`'s scoped hardening options. `promotion.py`'s `evaluate_promotion()` went from a three-conjunct
to a six-conjunct decision across this arc, every addition independently re-verified against real,
current source and re-run fresh before merging — never accepted on any implementer's self-report
alone.

## Real, independently-verified final state (not assumed)

- `python3 docs/tasks/validate-tasks.py`: PASS (0 active, 310 completed)
- `python3 tests/run.py`: 734 tests, `OK`, `skipped=38`
- `python3 implementation/scripts/check-maturity.py --verbose`: 79 components, 0 failing
- `node implementation/scripts/sync.mjs --root implementation --check`: no drift, 577 files
- Held-out isolation guard: 8/8 pass
- `docs/plans/plan-035-roadmap-v7-ground-up.md`'s six phase status headers: all accurate,
  checkpoint-cited, none stale (fixed by `T508`)

## The arc, task by task

- **T507** — ran one real (not hand-built) end-to-end closed-loop cycle: a real failure cluster, a
  real `meta_improver` proposal, real trial scores, a real `promote=True` decision, a real MR (!346).
  Independent review found two reasons that MR had to stay unmerged: the implementer's own disclosed
  causal confound (the "improvement" was almost certainly dispatch non-determinism, not the
  proposal's content) and a genuine, previously-undiscovered bug the top-level session found itself
  (`mr_gate.py` never regenerated per-platform projections after editing the canonical knowledge
  source, so the MR's own CI failed). This satisfied Phase 6's literal AC1 ("one cycle runs
  end-to-end and produces a merge request") and proved the human gate works — catching a real false
  positive before it could land, exactly what Gate G4 exists to demonstrate.
- **T508** — fixed `plan-035`'s six stale, never-updated phase status headers (Phases 1-6), each
  now citing the real checkpoint that closed it. The implementer independently caught and corrected
  a real error in its own dispatching brief (a wrong line→phase mapping) rather than following it
  blindly.
- **T509** — design-only pass (dispatched per the user's "Scope the promotion.py hardening"),
  diagnosing `T507`'s root cause precisely: `floor_met()` pools trial evidence across every case in
  a comparison rather than requiring real per-case replication, and the regression conjunct's own
  extra rigor only applies once a case is escalated to k>=3 — nothing previously required escalation
  before a promotion could fire. Three options scoped (A: per-case minimum-evidence gate; B: a
  symmetric qualitative classification; C: provenance-homogeneity check), each independently shown
  to have blocked `T507`'s actual promotion. No code touched, no option decided — reserved for the
  user.
- **T510** — built Options A and C (per the user's "build A + C first"). `check_minimum_evidence()`
  requires `MIN_ESCALATED_K` per case in both arms before any promotion; `check_provenance_
  homogeneity()` fails closed on mixed or unknown trial-data provenance across arms.
  `TrialRecord.provenance` added, fully backward-compatible with every already-persisted record.
- **T511** — built Option B (per the user's "Build B"). `classify_k_plus_improvement_outcome()`
  requires a floor-met case to also show a real, recurring (category-3, `>=2` treatment trials)
  qualitative signal before it counts as `CONFIRMED_POSITIVE_EFFECT` — wired in as a required,
  conservative conjunct, a disclosed judgment call this task's own brief made (not `T509`'s original
  design, which left it open). Completes all three hardening options.

## What this proves and what it does not

- **Proven**: the mechanism runs end-to-end for real; the human MR gate genuinely catches a false
  positive before it can land; the specific failure mode `T507` exposed (thin, pooled, cross-case
  evidence and provenance-confounded comparisons producing a spurious "promote") is now closed by
  three independent, tested, code-level controls, not merely documented as a known risk.
- **Not proven, and not provable by construction**: that the loop will ever produce a *real*,
  genuinely accepted improvement. The hardening built this arc is deliberately conservative — per
  `T509`'s own disclosed trade-off, few real proposals will clear `CONFIRMED_POSITIVE_EFFECT` today,
  since consistent qualitative categorization at dispatch time is not yet an established process
  discipline. No real accepted change has ever gone through this loop. Phase 6's AC2 ("improvement is
  measurable on the held-out suite") and AC5 ("lineage document exists for every accepted change")
  remain genuinely open — not because anything is broken, but because both are, by definition, only
  satisfiable by a real accepted change actually happening, and this arc's entire point was to make
  sure the loop does *not* manufacture one prematurely.

## v7.0 release readiness, reassessed

`plan-060`'s own review identified exactly two remaining items before `/prepare-release major` could
cut `v7.0.0`: `T507` and `T508`. Both are done. This arc's three follow-up tasks (`T509`-`T511`) were
not part of that original list — they exist because `T507`'s own real result surfaced a genuine gap,
and the user chose to close it rather than ship past it. That gap is now closed.

**Recommendation: v7.0.0 is ready to release.** The two literal blockers `plan-060` named are done;
the follow-up finding they surfaced is also now closed, to the same independent-verification standard
as everything else this arc. Phase 6's AC2/AC5 remaining open is not a release blocker in the way
`T507`/`T508` were — it describes an ongoing operational characteristic of a now-correctly-cautious
system (it has not yet promoted anything, on purpose, because nothing has yet cleared a genuinely high
bar), not an unfinished piece of infrastructure. Forcing a real promotion before release, to close
AC2/AC5 on paper, would be exactly the mistake this whole arc worked to prevent.

This is the top-level session's assessment, not a decision — per this project's Plan-Approve-Execute
discipline, whether and when to actually run `/prepare-release major` remains the user's call.

## Process notes worth carrying forward

- **A real, non-decreasing date-order invariant** in `docs/tasks/completed-tasks.md` (validator check
  C9) was hit for the first time this arc, on `T510`'s closure: new rows must be appended at the true
  end of the file (or wherever keeps dates non-decreasing top-to-bottom), not simply inserted
  above the most recently seen row — the file's real physical order is oldest-row-last (a LIFO stack
  from this whole session's own edit history), not strictly chronological-by-position. Caught by
  `validate-tasks.py` before pushing, not discovered via a failed CI run.
- **A transient `glab auth git-credential "erase"` push failure**, distinct from this session's usual
  stale-token false positive, occurred once during `T510`'s dispatch commit. `glab api user` confirmed
  the credential bridge was fine; a direct retry of the identical push succeeded immediately. No
  configuration touched. Worth noting as a new, if rare, member of the "transient push hiccup, retry
  before investigating" family, distinct from the already-documented stale-`$GITLAB_PERSONAL_ACCESS_TOKEN`
  pattern.
- **Every task this arc was independently re-verified beyond the implementer's own test suite**,
  consistent with this entire session's discipline: real diffs read in full, real checkpoint/data
  citations re-checked against source, real test files re-run in isolation, the full verification bar
  re-run fresh before every merge. Two implementers this arc found and disclosed real refinements to
  their own dispatching briefs rather than following them blindly (`T509`'s pooled-vs-per-case
  correction; `T511`'s `count_category_occurrences` failing-trials-restriction deviation) — both
  independently confirmed accurate by the top-level session before being trusted.

## Token metrics

Not separately tracked against a phase budget across this arc.

## Next steps

- **User decision pending**: whether to run `/prepare-release major` now to cut `v7.0.0`, given this
  checkpoint's own recommendation that it is ready.
- **`plan-035` §2.7's deferred SIA/CWSO revival decision** remains untouched and unresolved, exactly
  as `checkpoint-034` left it — no change this arc.
- **`feature/T475-codex-platform-integration`** remains exactly as `plan-054` left it, untouched this
  arc, further behind `develop` and growing.
- **Not scoped or requested**: any further hardening of the closed loop, or an attempt to actually
  produce a real accepted promotion. Both would be new work requiring their own explicit user
  instruction, per this project's established discipline.
