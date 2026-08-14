# Phase 1 Golden Suite Baseline — v6.12.0

**Status:** FROZEN — this is the Phase 1 baseline.
**Task:** T414. **Based on:** `docs/benchmarks/scorecard-v6.12.0.json` /
`docs/benchmarks/scorecard-v6.12.0.md` (T413), `tests/golden/` (T410/T411), the
`open`/`held-out` split and isolation guard (T412, `tests/functional/test_golden_held_out_isolation.py`).
**Published:** 2026-08-13.

## What this document is

This is the formal, human-facing publication of the golden suite scorecard as the
**frozen Phase 1 reference point**. It is not a new measurement — every number below is
sourced directly from `docs/benchmarks/scorecard-v6.12.0.json`'s `content.summary` (as
rendered in `docs/benchmarks/scorecard-v6.12.0.md`), cross-checked against that file at
publication time. This document exists to formally close the "no optimization before the
baseline exists" gate; it does not restate or recompute the scorecard from memory.

Per `docs/plans/plan-035-roadmap-v7-ground-up.md`, Phase 1 §2.4, Layer 1 table, row T414:

> Publish `docs/benchmarks/baseline-v6.12.0.md`. **Do not optimise anything before this
> file exists.**

That instruction is now satisfied: this file exists. **No improvement/optimization work
against the golden suite may begin before this file existed, and all future improvement
work's golden-suite results are compared against the numbers below.**

## Headline numbers (source: `scorecard-v6.12.0.json` `content.summary`, generated
`2026-08-13T20:40:53Z`)

| Metric | Count |
|---|---|
| Total cases | 20 |
| Pass | 11 |
| Fail (regression + known_failing) | 9 |
| **Regressions** (expected_pass, now failing) | 0 |
| Known-failing (expected) | 9 |
| — tracked_defect | 6 |
| — capability_gap | 3 |
| Unexpected pass (known_failing now passing) | 0 |

### Open / held-out breakdown

| Location | Total | Pass | Regressions | Known-failing | tracked_defect | capability_gap | Unexpected pass |
|---|---|---|---|---|---|---|---|
| open | 14 | 8 | 0 | 6 | 4 | 2 | 0 |
| held-out | 6 | 3 | 0 | 3 | 2 | 1 | 0 |

For the full per-case table (open cases only, by real ID), see
`docs/benchmarks/scorecard-v6.12.0.md`. This document intentionally does not repeat the
per-case table — see "Held-out case identities" below for why held-out rows are excluded
from per-identity reproduction here, and "How to reproduce" for the authoritative source.

## "Reject a too-easy baseline" check — performed and passed

Per plan-035's risk table: *"Golden suite is authored too easy, baseline reads 20/20 |
Medium | High | T411 mandates ≥5 known-failing cases; **T414 rejects a perfect
baseline**."* This check was performed as part of publishing this document, not assumed:

- `content.summary.known_failing` in `docs/benchmarks/scorecard-v6.12.0.json` was read
  directly and is **9** (6 `tracked_defect` + 3 `capability_gap`), against **11** pass, 0
  regressions, 20 total cases.
- 9 clears T411's mandated floor of ≥5 known-failing cases with margin (9 ≥ 5).
- The known-failing set is not concentrated in a single command surface or a single
  category: it spans `tracked_defect` (6) and `capability_gap` (3), and is present in
  both the `open` (6 of 14) and `held-out` (3 of 6) subsets — i.e. held-out is not merely
  an easy rubber-stamp subset with 100% pass.
- **Verdict: this is not a 20/20 or near-perfect result. The baseline is a healthy,
  meaningful signal and is safe to publish as the Phase 1 reference point.**

## Held-out case identities — deliberately not named here

This document does not enumerate which specific case IDs are `held-out` beyond the
aggregate counts above, mirroring T413's own redaction reasoning in
`scripts/scorecard.py` (see its "Held-out case-ID redaction in output artifacts" module
docstring section). The concern the isolation guard (T412,
`tests/functional/test_golden_held_out_isolation.py`) protects against is the held-out
set leaking into improvement-task material — any agent/skill/doc/script file outside
`tests/golden/` that names a real held-out case ID as a whole token is flagged by that
guard's Check B. This baseline document lives under `docs/benchmarks/`, well outside
`tests/golden/`, and is exactly the kind of improvement-adjacent file that check exists
to cover — so it carries held-out *aggregate* health (counts, pass/fail split,
tracked_defect/capability_gap split) only, never held-out case *identity*, exactly as
`scorecard-v6.12.0.json`/`.md` already do via `redact_held_out_identities()`.

This was verified, not assumed: this document was `grep`-checked against all six real
held-out case IDs listed in `tests/golden/_manifest-t411.md`'s "`open`/`held-out` split
(T412)" section, with zero matches, and
`tests/functional/test_golden_held_out_isolation.py` was re-run after writing this file
and still passes with it present.

## How to reproduce

`python3 scripts/scorecard.py` regenerates `docs/benchmarks/scorecard-v6.12.0.json` and
`docs/benchmarks/scorecard-v6.12.0.md` from the current on-disk state of `tests/golden/`.
Unlike those two files, **this baseline document is not regenerated automatically** — it
is a point-in-time snapshot/publication of the v6.12.0 scorecard, frozen at the moment
Phase 1 began comparing improvement work against it. If the golden suite or its results
change in the future, that produces a *new* scorecard and, if formally re-baselined, a
new baseline document (e.g. `baseline-v6.13.0.md`) — this file is never edited in place
to reflect later runs.
