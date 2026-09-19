# Failure classification: `plan-real-doc-header-drift`

**Scheme:** `docs/artifacts/failure-taxonomy-v1.md`
**Source case:** `tests/golden/open/plan-real-doc-header-drift/`
**Command:** `/plan`
**`known_failing_category` (T410 axis):** `tracked_defect`

## Axis classification

| Axis | Value |
|---|---|
| `cause` | `established-practice-drift` |
| `behavior` | `naming-or-format-drift` |
| `mechanism` | `naming-convention-drift` |

## Why

`implementation/knowledge/commands/plan.md` step 5 requires six verbatim headers (Goal, Task
Decomposition, Dependency Graph, Resource Assignments, Risk Assessment, Open Questions). The
fixture — a real plan doc, `docs/plans/plan-030-mcp-remote-transport-alignment.md` — uses
`## Objective`, `## Task Breakdown`, `## Agent Assignments`, `## Risks & Mitigations` instead of
four of the six (only `## Dependency Graph` and `## Open Questions` match verbatim). The case's
corpus survey (`grep -rl "Task Decomposition"` / `"Resource Assignments"` across all 34 real
`docs/plans/*.md` files, zero matches for either) shows this is systemic, not specific to
plan-030.

- **`cause`**: `established-practice-drift` — declared contract unambiguous, real corpus (all 34
  plan docs) consistently diverges.
- **`behavior`**: `naming-or-format-drift` — the conceptual sections (goal, tasks, risks, etc.)
  are all present; only the header text differs from the declared names.
- **`mechanism`**: `naming-convention-drift` — content structurally present under different
  names, not missing.
