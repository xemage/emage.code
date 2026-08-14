# Case: prepare-release-verdict-compliant

## Command under test
`/prepare-release`

## Brief (illustrative — not executed live)
"Prepare a minor release, v6.9.0." All quality gates pass, no breaking changes.

## What this checks
`implementation/knowledge/commands/prepare-release.md` §"Release Gate Verdict" step 7: a
`## RELEASE VERDICT` block with `Version`, `Status`, `Features included`, `Fixes included`,
`Breaking changes`, `Open blockers`, `Quality gates passed`, `Quality gates failed`,
`Blocker IDs`, `Release manager`, `Timestamp` fields.

## Pass condition
`fixture/release-notes.md` contains a `## RELEASE VERDICT` section with all 11 required fields,
`Status` in `{PASS, CONDITIONAL_PASS, FAIL}`, and `Version` matching `v<major>.<minor>.<patch>`.

## Provenance
Hand-authored. See `prepare-release-real-verdict-missing` for a real release checkpoint from
this repo's own history checked against this identical contract — it has no such block at all,
which is why this compliant case must be hand-authored rather than sourced.
