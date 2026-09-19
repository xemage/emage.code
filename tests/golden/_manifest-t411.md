# T411 Golden Suite Manifest

Convenience index of all 20 golden cases authored for T411, for T413 (`scripts/scorecard.py`),
T414 (baseline publication), and T415 (failure taxonomy). Not part of the format contract itself
(see `docs/artifacts/golden-suite-format-v1.md` for that) — this is a flat listing generated at
authoring time; re-derive it from `case.yaml` files directly if it ever drifts.

Excludes `_example-scaffold/` (not a real case, per format spec §3).

**T412 addendum (2026-08-13):** all 20 cases moved from flat `tests/golden/<case-id>/` into
`tests/golden/open/<case-id>/` (14 cases) or `tests/golden/held-out/<case-id>/` (6 cases) as a
pure directory move — zero content change (verified by blob-hash comparison against this
manifest's authoring commit `90f1f26`). The table below now shows each case's `open`/`held-out`
location. See `tests/golden/README.md` §"open/ vs held-out/" and
`tests/functional/test_golden_held_out_isolation.py`'s module docstring for the held-out split
rationale and the isolation guard's design.

| # | Case ID | Location | Command | Status | Known-failing category |
|---|---------|----------|---------|--------|-------------------------|
| 1 | code-review-conditional-pass-conditions-gap | `open/` | `/code-review` | known_failing | capability_gap |
| 2 | code-review-fail-blocker-details | `open/` | `/code-review` | expected_pass | — |
| 3 | code-review-real-verdict-format-drift | `held-out/` | `/code-review` | known_failing | tracked_defect |
| 4 | code-review-verdict-compliant | `held-out/` | `/code-review` | expected_pass | — |
| 5 | new-feature-checkpoint-line-compliant | `open/` | `/new-feature` | expected_pass | — |
| 6 | new-feature-plan-doc-compliant | `open/` | `/new-feature` | expected_pass | — |
| 7 | new-feature-real-artifact-versioning-drift | `held-out/` | `/new-feature` | known_failing | tracked_defect |
| 8 | new-feature-real-checkpoint-format-drift | `open/` | `/new-feature` | known_failing | tracked_defect |
| 9 | plan-approval-marker-gap | `held-out/` | `/plan` | known_failing | capability_gap |
| 10 | plan-real-doc-header-drift | `open/` | `/plan` | known_failing | tracked_defect |
| 11 | plan-required-sections-compliant | `open/` | `/plan` | expected_pass | — |
| 12 | plan-task-creation-precondition-real | `open/` | `/plan` | expected_pass | — |
| 13 | prepare-release-changelog-grouping-compliant | `open/` | `/prepare-release` | expected_pass | — |
| 14 | prepare-release-conditional-pass-conditions-gap | `open/` | `/prepare-release` | known_failing | capability_gap |
| 15 | prepare-release-real-verdict-missing | `open/` | `/prepare-release` | known_failing | tracked_defect |
| 16 | prepare-release-verdict-compliant | `held-out/` | `/prepare-release` | expected_pass | — |
| 17 | security-audit-coverage-consistency | `open/` | `/security-audit` | expected_pass | — |
| 18 | security-audit-critical-not-fail | `open/` | `/security-audit` | known_failing | tracked_defect |
| 19 | security-audit-owasp-matrix-compliant | `held-out/` | `/security-audit` | expected_pass | — |
| 20 | security-audit-verdict-fields-compliant | `open/` | `/security-audit` | expected_pass | — |

## `open`/`held-out` split (T412)

- **Held-out (6 cases, 30%):** `code-review-verdict-compliant`,
  `code-review-real-verdict-format-drift`, `new-feature-real-artifact-versioning-drift`,
  `plan-approval-marker-gap`, `prepare-release-verdict-compliant`,
  `security-audit-owasp-matrix-compliant`.
- **Open (14 cases, 70%):** everything else.
- **Reasoning:** the held-out set spans all 5 command surfaces (2 `/code-review`, 1 each of
  `/new-feature`, `/plan`, `/prepare-release`, `/security-audit` — not concentrated in one
  surface), is balanced 3 `expected_pass` / 3 `known_failing` (satisfying the "not 100%
  `expected_pass`" requirement with margin), and covers both `known_failing_category` values
  (`tracked_defect`: `code-review-real-verdict-format-drift`,
  `new-feature-real-artifact-versioning-drift`; `capability_gap`: `plan-approval-marker-gap`) so a
  future improvement can't game only one failure flavor. It also mixes real-artifact-grounded
  cases (`code-review-real-verdict-format-drift`, `new-feature-real-artifact-versioning-drift`,
  `plan-approval-marker-gap`) with hand-authored ones (`code-review-verdict-compliant`,
  `prepare-release-verdict-compliant`, `security-audit-owasp-matrix-compliant`), so the held-out
  set isn't skewed toward either provenance. Each surface keeps at least 2 cases in `open/`
  (`/code-review` keeps 2, all others keep 3), leaving every surface's `open/` subset large enough
  to remain useful for iterative improvement work.

## Summary

- Total cases: 20 (excluding `_example-scaffold/`)
- Per surface: `/code-review` 4, `/new-feature` 4, `/plan` 4, `/prepare-release` 4,
  `/security-audit` 4
- `expected_pass`: 11
- `known_failing`: 9 — 6 `tracked_defect`, 3 `capability_gap`
  (`code-review-real-verdict-format-drift`, `new-feature-real-artifact-versioning-drift`,
  `new-feature-real-checkpoint-format-drift`, `plan-real-doc-header-drift`,
  `prepare-release-real-verdict-missing`, `security-audit-critical-not-fail` are
  `tracked_defect`; `code-review-conditional-pass-conditions-gap`, `plan-approval-marker-gap`,
  `prepare-release-conditional-pass-conditions-gap` are `capability_gap`)

## Real-artifact-grounded cases

Cases whose `fixture/` is a verbatim (or minimally, transparently redacted — see each case's
`brief.md`) copy of a real artifact already in this repo's history, rather than hand-authored:

- `code-review-real-verdict-format-drift` — `docs/tasks/task-T365.md`
- `new-feature-real-artifact-versioning-drift` — `docs/artifacts/adapter-evaluation-v1.md`,
  `docs/artifacts/benchmark-report-v1.md`
- `new-feature-real-checkpoint-format-drift` —
  `docs/checkpoints/checkpoint-017-t417-harbor-oracle-smoke-complete.md`
- `plan-approval-marker-gap`, `plan-real-doc-header-drift`, `plan-task-creation-precondition-real`
  — `docs/plans/plan-030-mcp-remote-transport-alignment.md`
- `prepare-release-real-verdict-missing` — `docs/checkpoints/checkpoint-release-v6.4.1.md`

All other cases (`/security-audit`'s three matrix/verdict cases, `code-review-verdict-compliant`,
`code-review-fail-blocker-details`, both `/new-feature` compliant cases, both `/prepare-release`
compliant cases, both conditional-pass capability-gap cases) are hand-authored — either because
no real precedent of that exact structured output exists anywhere in this repo's history (a
corpus survey is documented in each such case's `brief.md`), or because the case demonstrates a
genuine capability gap that by definition has no clean real-world instance.
