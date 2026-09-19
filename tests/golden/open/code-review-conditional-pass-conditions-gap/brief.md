# Case: code-review-conditional-pass-conditions-gap (known_failing / capability_gap)

## Command under test
`/code-review`

## Brief (illustrative — not executed live)
"Review the rate limiter changes against `rate-limiter-v2.1.md`." Reviewer is satisfied enough
to conditionally pass, with follow-up items mentioned only informally ("discussed in standup").

## What this checks
`implementation/knowledge/commands/code-review.md`: "If CONDITIONAL_PASS, list the conditions
that must be met before merge." This case asks: can a deterministic, structured check verify
that the conditions were actually *listed* (as opposed to merely alluded to in prose), given that
the command never specifies what a machine-checkable "conditions list" must look like (no
required field name, no required list format)?

## Pass condition (as specified — deliberately not met by the fixture)
When `Status: CONDITIONAL_PASS`, the document must contain a structured `**Conditions**:` field
or a `## Conditions` section with at least one list item.

## Why this is known_failing today, and why it's a capability_gap rather than a tracked_defect
`fixture/review.md` is `CONDITIONAL_PASS` with two `Should Fix` items and a prose mention of
follow-up ("discussed in standup ... tracked separately") but no structured `Conditions` field or
section anywhere — because the command definition itself never mandates one. This is not a
reviewer error against a clear rule; the command's own text ("list the conditions") gives no
schema for what "listing" means in a way `expect.py` (or any downstream tool) could check
generically. Until the command definition is extended with an explicit `**Conditions**:` field
convention (analogous to `**Blocker IDs**:` for FAIL), this is a structural gap in the contract,
not a mistake in this specific review.

## Category
`capability_gap`.
