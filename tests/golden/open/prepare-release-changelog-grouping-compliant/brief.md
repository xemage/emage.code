# Case: prepare-release-changelog-grouping-compliant

## Command under test
`/prepare-release`

## Brief (illustrative — not executed live)
"Prepare a minor release, v6.9.0." Changelog generated from `completed-tasks.md` entries since
the last release.

## What this checks
`implementation/knowledge/commands/prepare-release.md` §"Release Steps" step 2: "Generate
changelog from completed tasks — Group by: Features, Fixes, Breaking Changes, Internal —
Include task IDs and artifact version references."

## Pass condition
`fixture/changelog.md` contains `## Features`, `## Fixes`, `## Breaking Changes`, and
`## Internal` section headers, and at least one `T<digits>` task-ID reference appears under
each of `Features` and `Fixes`.

## Provenance
Hand-authored. No real changelog artifact grouped this exact way (`Features`/`Fixes`/`Breaking
Changes`/`Internal`) exists in this repo's history — real release checkpoints
(`docs/checkpoints/checkpoint-release-v*.md`) use a flat "Completed work (this cycle)" commit
table instead (see `prepare-release-real-verdict-missing` for that real convention checked
against a different part of this same command's contract).
