# Case: prepare-release-real-verdict-missing (known_failing / tracked_defect)

## Command under test
`/prepare-release`

## Brief (illustrative — not executed live)
Same underlying contract as `prepare-release-verdict-compliant`, applied to a real release
notes document already in this repo's history instead of a hand-authored one:
`docs/releases/v7.0.1.md` (v7.0.1, a real patch release).

## What this checks
The identical contract as `prepare-release-verdict-compliant`:
`implementation/knowledge/commands/prepare-release.md` step 7's declared `## RELEASE VERDICT`
block with `Version`/`Status`/`Features included`/`Fixes included`/`Breaking changes`/`Open
blockers`/`Quality gates passed`/`Quality gates failed`/`Blocker IDs`/`Release manager`/
`Timestamp` fields.

Step 7 puts the block in the release notes document from step 5 (`docs/releases/v<version>.md`)
as a top-level `## RELEASE VERDICT` section, and says that document is the block's home, "not the
release checkpoint from step 6". The fixture is therefore a release notes document, at
`fixture/docs/releases/v7.0.1.md`.

## Why this is known_failing today
`docs/releases/v7.0.1.md` has no `## RELEASE VERDICT` heading anywhere. Its headings are
`## Install`, `## Highlights` (with `### Fixed` and `### Internal`), `## Breaking changes` and
`## Internal (task references)`: release content, but not the structured gate verdict the command
declares. A corpus survey (`grep -rl "## RELEASE VERDICT" docs/releases/`) finds the heading only
in `docs/releases/_template.md`, which carries the slot; no shipped release notes document
contains the block. The command's contract is unambiguous and the shipped notes omit it, which is
`ADR-007` branch 3b (omission: fix the corpus, not the check).

## Category
`tracked_defect` — the command's declared verdict block is unambiguous and its absence from the
shipped release notes is a concrete, trackable gap between declared contract and established
practice. The exit, per `ADR-007` § 3b, is a genuine release notes document that carries the
block, re-fixtured byte-identically; it is not an edit to the check or to the old fixture.

## History: why the fixture is a release notes document (O3)
This case was first authored against the wrong artifact class. Its original fixture was
`docs/checkpoints/checkpoint-release-v6.4.1.md` (a real release checkpoint, copied verbatim apart
from dropping the leading `v` of its other version tokens, so that
`scripts/check-version-consistency.py` would not flag the copy), and `expect.py` read
`fixture/docs/checkpoints/`. That checkpoint reported release status through a `## Quality gates
run this cycle` table and prose, and its own text referred to "RELEASE VERDICT" by name without
ever including the block.

When `prepare-release.md` step 7 was amended to make the release notes document the block's
home, the case no longer measured the clause it cites: it applied `/prepare-release`'s contract
to an artifact class the clause does not govern. That is `ADR-007` branch 2
(`docs/artifacts/remaining-verdict-renderings-v1.md` § 8.4 O3). The fix re-targeted the case; it
did not amend the command and did not weaken the check. In `expect.py` only the docstring and the
fixture-directory path lines changed (`fixture/docs/checkpoints` became `fixture/docs/releases`,
with the variable renamed), and the fixture became a byte-identical copy of the real
`docs/releases/v7.0.1.md`. `REQUIRED_FIELDS` (11 names), `ALLOWED_STATUS`, `VERSION_RE`,
`_verdict_section` and the `check()` logic are byte-identical to the pre-retarget file. The result
stayed `False`: against the right artifact class the shipped notes still omit the block, so the
defect is real.

Realigned under `docs/artifacts/promotion-and-golden-realignment-plan-v1.md` § 6.3 (grant G-1,
items 2 to 6).
