# `docs/benchmarks/failures/` — golden-suite failure classification index

Scheme definition (axis meanings, why they're distinct, full case-by-case table): see
`docs/artifacts/failure-taxonomy-v1.md` (T415). This directory holds one auditable classification
file per `known_failing` golden case — which case, which `cause`/`behavior`/`mechanism` axis
value, and why — mirroring the golden suite's own per-case-directory convention
(`docs/artifacts/golden-suite-format-v1.md` §3).

**Scope:** only the `known_failing` bucket (9 cases, per
`docs/benchmarks/scorecard-v6.12.0.json`'s `content.summary.known_failing: 9`, re-verified at
authoring time). `regression` and `unexpected_pass` cases are out of scope — see
`failure-taxonomy-v1.md` §6.

**Held-out cases:** 3 of the 9 are held-out; per the isolation discipline carried forward from
T412/T413/T414, their files use a redacted identity (`held-out-case-<n>`, same numbering as
`docs/benchmarks/scorecard-v6.12.0.json`) and never name their real case ID, path, or fixture
content. See `failure-taxonomy-v1.md` §5.

## Index

| File | Case | Location | `known_failing_category` | `cause` | `behavior` | `mechanism` |
|---|---|---|---|---|---|---|
| `code-review-conditional-pass-conditions-gap.md` | `code-review-conditional-pass-conditions-gap` | open | capability_gap | undefined-structured-convention | required-section-absent | field-level-absence-within-declared-block |
| `new-feature-real-checkpoint-format-drift.md` | `new-feature-real-checkpoint-format-drift` | open | tracked_defect | established-practice-drift | required-marker-line-absent | whole-block-absence |
| `plan-real-doc-header-drift.md` | `plan-real-doc-header-drift` | open | tracked_defect | established-practice-drift | naming-or-format-drift | naming-convention-drift |
| `prepare-release-conditional-pass-conditions-gap.md` | `prepare-release-conditional-pass-conditions-gap` | open | capability_gap | undefined-structured-convention | required-section-absent | field-level-absence-within-declared-block |
| `prepare-release-real-verdict-missing.md` | `prepare-release-real-verdict-missing` | open | tracked_defect | established-practice-drift | required-section-absent | whole-block-absence |
| `security-audit-critical-not-fail.md` | `security-audit-critical-not-fail` | open | tracked_defect | rule-violation-no-exception-clause | value-violates-invariant | cross-field-invariant-violation |
| `held-out-case-1.md` | `held-out-case-1` (redacted) | held-out | tracked_defect | established-practice-drift | naming-or-format-drift | naming-convention-drift |
| `held-out-case-3.md` | `held-out-case-3` (redacted) | held-out | tracked_defect | established-practice-drift | naming-or-format-drift | naming-convention-drift |
| `held-out-case-4.md` | `held-out-case-4` (redacted) | held-out | capability_gap | undefined-structured-convention | required-section-absent | whole-block-absence |

9 files, 9 cases — matches `docs/benchmarks/scorecard-v6.12.0.json`'s `known_failing: 9`.
