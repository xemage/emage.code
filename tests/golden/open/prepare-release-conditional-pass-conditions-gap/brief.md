# Case: prepare-release-conditional-pass-conditions-gap (known_failing / capability_gap)

## Command under test
`/prepare-release`

## Brief (illustrative — not executed live)
"Prepare a patch release, v6.9.1." Release manager conditionally passes pending a final
smoke-test sign-off, mentioned only informally ("tracked in the release channel").

## What this checks
`implementation/knowledge/commands/prepare-release.md` §"Release Steps" step 9: "If
CONDITIONAL_PASS, list conditions that must be met before deployment." This case asks: can a
deterministic, structured check verify the conditions were actually *listed* (as opposed to
merely alluded to in prose), given that neither step 9 nor the step 7 `## RELEASE VERDICT`
template declares a required field name or list format for them (unlike, e.g., `**Blocker
IDs**:`, which the template does declare explicitly for the FAIL case)?

## Pass condition (as specified — deliberately not met by the fixture)
When `**Status**: CONDITIONAL_PASS`, the document must contain a structured `**Conditions**:`
field or a `## Conditions` section with at least one list item.

## Why this is known_failing today, and why it's a capability_gap rather than a tracked_defect
`fixture/release-notes.md` is `CONDITIONAL_PASS` with a prose mention of the pending condition
("pending final smoke-test sign-off ... tracked informally") but no structured `Conditions`
field or section — because the command definition's own `## RELEASE VERDICT` template (step 7)
never includes one, unlike its explicit `**Blocker IDs**:` field for the FAIL path. This
mirrors `code-review-conditional-pass-conditions-gap`'s identical structural gap in a sibling
command; both commands say "list conditions"/"list the conditions" without ever defining what a
machine-checkable list looks like.

## Category
`capability_gap` — until the `## RELEASE VERDICT` template is extended with an explicit
`**Conditions**:` field convention, this is a structural gap in the contract itself, not a
mistake in this specific release.
