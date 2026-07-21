# Objective: Structured Plan Summary (v1)

Produce a machine-readable plan summary that emage.code can validate before orchestration.

## Required output file

Write `solution.json` containing a single JSON object with the following top-level fields:

- `objective`: short objective statement
- `architecture_version`: versioned architecture reference (example: `architecture-v2.md`)
- `summary`: concise plan summary
- `tasks`: array of task objects
- `risks`: array of risk strings

Each task in `tasks` must contain:

- `id`: task id string (example: `T300`)
- `title`: short title
- `owner`: role or team owner
- `status`: one of `pending`, `in_progress`, `blocked`, `in_review`, `done`, `cancelled`
- `priority`: one of `P0`, `P1`, `P2`
- `acceptance_criteria`: non-empty array of strings
- `dependencies`: array of task ids

## Quality expectations

- Include at least 3 tasks.
- Include at least 1 risk.
- Dependency ids should reference ids present in `tasks`.
- Keep output deterministic and valid JSON.
