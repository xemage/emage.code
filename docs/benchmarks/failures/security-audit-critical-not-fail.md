# Failure classification: `security-audit-critical-not-fail`

**Scheme:** `docs/artifacts/failure-taxonomy-v1.md`
**Source case:** `tests/golden/open/security-audit-critical-not-fail/`
**Command:** `/security-audit`
**`known_failing_category` (T410 axis):** `tracked_defect`

## Axis classification

| Axis | Value |
|---|---|
| `cause` | `rule-violation-no-exception-clause` |
| `behavior` | `value-violates-invariant` |
| `mechanism` | `cross-field-invariant-violation` |

## Why

`implementation/knowledge/commands/security-audit.md` states unconditionally: "if any CRITICAL
findings exist, the verdict MUST be FAIL," with no compensating-control exception clause. The
fixture (hand-authored — no real historical `/security-audit` output exists to source it from) has
`**CRITICAL findings**: 1` and `**Status**: CONDITIONAL_PASS`, reasoning that a compensating
network-level control mitigates the finding. Both fields are individually well-formed and present
(unlike every other case in this taxonomy's `known_failing` set); the failure is purely in the
*relationship* between the two field values, which the command's stated rule forbids without
exception.

- **`cause`**: `rule-violation-no-exception-clause` — distinct from `established-practice-drift`
  because there is no real corpus of `/security-audit` outputs to survey (this is the one
  hand-authored, scenario-grounded case in the set); distinct from `undefined-structured-
  convention` because the rule and its fields are fully declared and structured, just violated.
- **`behavior`**: `value-violates-invariant` — the unique behavior value in the set that isn't
  about presence/absence/naming of structure at all.
- **`mechanism`**: `cross-field-invariant-violation` — `CRITICAL findings` and `Status` are each
  individually well-formed; only their combination breaks the declared rule.
