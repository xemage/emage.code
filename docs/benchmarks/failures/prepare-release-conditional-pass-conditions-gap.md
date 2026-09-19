# Failure classification: `prepare-release-conditional-pass-conditions-gap`

**Scheme:** `docs/artifacts/failure-taxonomy-v1.md`
**Source case:** `tests/golden/open/prepare-release-conditional-pass-conditions-gap/`
**Command:** `/prepare-release`
**`known_failing_category` (T410 axis):** `capability_gap`

## Axis classification

| Axis | Value |
|---|---|
| `cause` | `undefined-structured-convention` |
| `behavior` | `required-section-absent` |
| `mechanism` | `field-level-absence-within-declared-block` |

## Why

`implementation/knowledge/commands/prepare-release.md` step 9 requires "if CONDITIONAL_PASS, list
conditions that must be met before deployment," but the declared `## RELEASE VERDICT` template
(step 7) has no `**Conditions**:` field or equivalent slot for them — unlike the FAIL path, which
does declare `**Blocker IDs**:` explicitly. The fixture (`**Status**: CONDITIONAL_PASS`, prose-only
mention "pending final smoke-test sign-off ... tracked informally") has no structured conditions
field, but there is no schema declared for it to conform to. Structurally identical gap to
`code-review-conditional-pass-conditions-gap` in a sibling command.

- **`cause`**: `undefined-structured-convention` — the template itself never includes the field.
- **`behavior`**: `required-section-absent` — no `Conditions` field/section anywhere in the
  fixture.
- **`mechanism`**: `field-level-absence-within-declared-block` — the surrounding `## RELEASE
  VERDICT` block does exist (`**Status**:` is present); only the undeclared `Conditions` sub-field
  is missing from within it.
