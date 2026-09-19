# Failure classification: `prepare-release-real-verdict-missing`

**Scheme:** `docs/artifacts/failure-taxonomy-v1.md`
**Source case:** `tests/golden/open/prepare-release-real-verdict-missing/`
**Command:** `/prepare-release`
**`known_failing_category` (T410 axis):** `tracked_defect`

## Axis classification

| Axis | Value |
|---|---|
| `cause` | `established-practice-drift` |
| `behavior` | `required-section-absent` |
| `mechanism` | `whole-block-absence` |

## Why

`implementation/knowledge/commands/prepare-release.md` step 7 requires a `## RELEASE VERDICT`
block with 11 structured fields. The fixture — a real release checkpoint,
`docs/checkpoints/checkpoint-release-v6.4.1.md` — has no such heading anywhere; it reports release
status via a `## Quality gates run this cycle` table and prose instead, and its own text even says
"See RELEASE VERDICT for how this factors into the release status" without ever including one.
The case's corpus survey (`grep -rl "## RELEASE VERDICT" docs/checkpoints/*.md`) returns zero
matches across all real release checkpoints in the repo.

- **`cause`**: `established-practice-drift` — declared block unambiguous, corpus of real release
  checkpoints consistently omits it in favor of a different convention.
- **`behavior`**: `required-section-absent` — the entire `## RELEASE VERDICT` heading and its
  fields are missing, not just renamed.
- **`mechanism`**: `whole-block-absence` — no partial trace of the block exists; the document's
  own prose gestures at the concept by name without ever instantiating the structure.
