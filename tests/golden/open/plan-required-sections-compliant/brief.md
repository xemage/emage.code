# Case: plan-required-sections-compliant

## Command under test
`/plan`

## Brief (illustrative — not executed live)
"Plan a background sync job that reconciles local widget state with the remote inventory
service." A user or agent runs `/plan` against this request.

## What this checks
`implementation/knowledge/commands/plan.md` step 5 requires the plan document saved to
`docs/plans/<slug>-plan.md` to use exactly this structure: **Goal**, **Task Decomposition**,
**Dependency Graph** (rendered as a Mermaid diagram per step 2), **Resource Assignments**,
**Risk Assessment**, **Open Questions**.

## Pass condition
Exactly one file matches `fixture/docs/plans/*-plan.md`, and its content contains all six
required `##` headers, in the declared order, with a fenced ` ```mermaid ` block appearing
somewhere under the Dependency Graph section.

## Provenance
Hand-authored to the command's declared contract. See `plan-real-doc-header-drift` (known_failing)
for the same check run against a real plan document from this repo's history — none of this
repo's 34 real `docs/plans/*.md` files (surveyed via `grep -l "Task Decomposition"
docs/plans/*.md` and equivalents for the other five required headers, all zero matches for
`Task Decomposition` and `Resource Assignments` across the entire corpus) satisfy this contract
verbatim, which is why this case's fixture had to be hand-authored rather than sourced from real
history.
