# Case: prepare-release-real-verdict-missing (expected_pass)

## Command under test
`/prepare-release`

## Brief (illustrative — not executed live)
Same underlying contract as `prepare-release-verdict-compliant`, applied to a real release
notes document already in this repo's history instead of a hand-authored one:
`docs/releases/v8.0.0.md` (v8.0.0, the first release notes document to carry the block).

## What this checks
The identical contract as `prepare-release-verdict-compliant`:
`implementation/knowledge/commands/prepare-release.md` step 7's declared `## RELEASE VERDICT`
block with `Version`/`Status`/`Features included`/`Fixes included`/`Breaking changes`/`Open
blockers`/`Quality gates passed`/`Quality gates failed`/`Blocker IDs`/`Release manager`/
`Timestamp` fields.

Step 7 puts the block in the release notes document from step 5 (`docs/releases/v<version>.md`)
as a top-level `## RELEASE VERDICT` section, and says that document is the block's home, "not the
release checkpoint from step 6". The fixture is therefore a release notes document, at
`fixture/docs/releases/v8.0.0.md`.

## Provenance of the current fixture
The current fixture, `fixture/docs/releases/v8.0.0.md`, is a byte-identical copy (`cmp`) of the
real `docs/releases/v8.0.0.md`: the published release notes of v8.0.0. It is the working document
of a real release, not a document written for this case. Its `## RELEASE VERDICT` section is the
first real emission of the block, issued by the release manager under step 7 of
`/prepare-release` after the QA, Tech Lead and security gates of that release, and it carries all
11 declared fields (`Version: v8.0.0`, `Status: CONDITIONAL_PASS`, and the nine others). It was
committed through the normal merge request flow, and published, independently of this case.
`expect.py` is byte-identical to the file it has had since grant G-1, so the check is exactly as
strong as before; only the example moved.

## History: formerly known_failing / tracked_defect
Until baseline v22 this case was `known_failing` with `known_failing_category: tracked_defect`.
Its fixture was then `docs/releases/v7.0.1.md`, a real patch release whose headings were
`## Install`, `## Highlights` (with `### Fixed` and `### Internal`), `## Breaking changes` and
`## Internal (task references)`: release content, but no `## RELEASE VERDICT` heading anywhere. A
corpus survey (`grep -rl "## RELEASE VERDICT" docs/releases/`) found the heading only in
`docs/releases/_template.md`, which carries the slot, so no shipped release notes document
contained the block. The command's contract was unambiguous and the shipped notes omitted it,
which is `ADR-007` branch 3b (omission: fix the corpus, not the check).

The exit was the one `ADR-007` § 3b prescribes, and the one named at the time this case was
retargeted: a genuine release notes document that carries the block, re-fixtured byte-identically.
`docs/releases/v8.0.0.md` is that document, the check is unchanged, and the case moved from
`known_failing` to `expected_pass` under `docs/tasks/task-T668.md` (grant G-2 of
`docs/plans/plan-123-post-release-follow-ups.md`; stage 2 / S8 of
`docs/artifacts/promotion-and-golden-realignment-plan-v1.md` § 6.4). The old fixture file was a
copy; the shipped `docs/releases/v7.0.1.md` is untouched, and the earlier retarget (below) is
unchanged history.

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
`docs/releases/v7.0.1.md` (replaced at grant G-2 by the v8.0.0 copy). `REQUIRED_FIELDS` (11 names),
`ALLOWED_STATUS`, `VERSION_RE`, `_verdict_section` and the `check()` logic are byte-identical to
the pre-retarget file. The result
stayed `False` at that point: against the right artifact class the shipped notes still omitted the
block, so the defect was real. (`expect.py`'s docstring still describes the case as
`known_failing` and says it is expected to return `False`; that text predates this change and was
not edited, because `expect.py` is outside the grant. The source of truth for the status is
`case.yaml`.)

Realigned under `docs/artifacts/promotion-and-golden-realignment-plan-v1.md` § 6.3 (grant G-1,
items 2 to 6).
