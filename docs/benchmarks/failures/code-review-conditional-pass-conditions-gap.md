# Failure classification: `code-review-conditional-pass-conditions-gap`

**Scheme:** `docs/artifacts/failure-taxonomy-v1.md`
**Source case:** `tests/golden/open/code-review-conditional-pass-conditions-gap/`
**Command:** `/code-review`
**`known_failing_category` (T410 axis):** `capability_gap`

## Axis classification

| Axis | Value |
|---|---|
| `cause` | `undefined-structured-convention` |
| `behavior` | `required-section-absent` |
| `mechanism` | `field-level-absence-within-declared-block` |

## Why

`implementation/knowledge/commands/code-review.md` requires "if CONDITIONAL_PASS, list the
conditions that must be met before merge," but never defines a structured field/section
convention for it (no `**Conditions**:` field, no `## Conditions` heading declared anywhere in
the command spec) — unlike the FAIL path, which does declare an explicit `**Blocker IDs**:`
field. The fixture (`Status: CONDITIONAL_PASS`, two `Should Fix` items, and a prose-only mention
"discussed in standup ... tracked separately") has no structured conditions field, but this is
not the reviewer's mistake — there is no schema to conform to.

- **`cause`**: `undefined-structured-convention`, because the gap is in the command's own
  declared contract, not in how the fixture document was written.
- **`behavior`**: `required-section-absent` — no `Conditions` field/section appears anywhere in
  the fixture.
- **`mechanism`**: `field-level-absence-within-declared-block` (not `whole-block-absence`) —
  the fixture's overall `## VERDICT`-style block *does* exist (`Status: CONDITIONAL_PASS` and the
  `Should Fix` counts are present); only the specific, undeclared `Conditions` sub-field is
  missing from within it.
