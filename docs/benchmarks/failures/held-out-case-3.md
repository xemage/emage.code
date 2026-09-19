# Failure classification: `held-out-case-3` (redacted identity)

**Scheme:** `docs/artifacts/failure-taxonomy-v1.md`
**Source case:** `tests/golden/held-out/<redacted>` — real ID intentionally withheld per
`tests/functional/test_golden_held_out_isolation.py` Check B; label assigned deterministically by
sorted real case ID, mirroring `scripts/scorecard.py`'s `redact_held_out_identities()`.
**Command:** `/new-feature`
**`known_failing_category` (T410 axis):** `tracked_defect`

## Axis classification

| Axis | Value |
|---|---|
| `cause` | `established-practice-drift` |
| `behavior` | `naming-or-format-drift` |
| `mechanism` | `naming-convention-drift` |

## Why (redacted)

This case's specific fixture content, and the detailed reasoning that led to each axis value
above, are withheld together with the case's identity — consistent with the protection scope of
`tests/functional/test_golden_held_out_isolation.py`. Only the categorical axis values in the
table above are disclosed here. For the general, case-independent definition of each axis value,
see `docs/artifacts/failure-taxonomy-v1.md` §3.
