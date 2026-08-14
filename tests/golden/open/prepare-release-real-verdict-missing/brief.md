# Case: prepare-release-real-verdict-missing (known_failing / tracked_defect)

## Command under test
`/prepare-release`

## Brief (illustrative — not executed live)
Same underlying contract as `prepare-release-verdict-compliant`, applied to a real release
checkpoint already in this repo's history instead of a hand-authored one:
`docs/checkpoints/checkpoint-release-v6.4.1.md` (v6.4.1, a real patch release).

## What this checks
The identical contract as `prepare-release-verdict-compliant`:
`implementation/knowledge/commands/prepare-release.md` step 7's declared `## RELEASE VERDICT`
block with `Version`/`Status`/`Features included`/`Fixes included`/`Breaking changes`/`Open
blockers`/`Quality gates passed`/`Quality gates failed`/`Blocker IDs`/`Release manager`/
`Timestamp` fields.

## Why this is known_failing today
`checkpoint-release-v6.4.1.md` has no `## RELEASE VERDICT` heading anywhere. It reports release
status information via a different, real convention instead — a `## Quality gates run this
cycle` table listing individual gate pass/fail results, prose in `## Phase summary` and `## Key
decisions` explaining the version-bump rationale (patch, not minor/major), and a `## Blockers
(active)` table. Notably, its own text at the end of the quality-gates section says "See
RELEASE VERDICT for how this factors into the release status" — referencing the concept by name
without ever actually including the structured block the command declares. A corpus survey
(`grep -rl "## RELEASE VERDICT" docs/checkpoints/*.md`) confirms zero real release checkpoints
in this repo contain the block.

## Category
`tracked_defect` — the command's declared verdict block is unambiguous and its absence from
every real release checkpoint (including one whose own prose explicitly gestures at it) is a
concrete, trackable gap between declared contract and established practice.
