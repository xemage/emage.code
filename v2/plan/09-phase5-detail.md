# 09 — Phase 5 detail: Validation gates

> Backfill of the v1 Phase-5 placeholder.

## Goal
Validation gates produce structured, auditable verdicts at every quality checkpoint. Reviewers do not modify code; orchestrator routes failures into fix tasks.

## Verdicts

| Verdict | Meaning | Orchestrator action |
|---------|---------|---------------------|
| `PASS` | Meets all acceptance criteria | Advance to next phase |
| `CONDITIONAL_PASS` | Meets criteria with caveats | Advance + add follow-up tasks for each condition |
| `FAIL` | Does not meet ≥1 critical criterion | Block phase; create fix tasks; re-route to producer |

## Gate types

| Gate | Reviewer | Inputs | Output artifact |
|------|----------|--------|-----------------|
| Architecture review | tech-lead | requirements, architecture | `architecture-review-vN.md` |
| Code review | tech-lead | implementation diff | `code-review-vN.md` |
| QA validation | qa-engineer | implementation + test plan | `test-report-vN.md` |
| Security audit | security-engineer | implementation + threat model | `security-report-vN.md` |
| Release sign-off | release-manager | full release artifacts | `release-checklist-vN.md` |

## Verdict report shape

```markdown
# <Gate name> — <verdict>

- **Subject**: <artifact-vN>
- **Reviewer**: <agent>
- **Date**: YYYY-MM-DD
- **Verdict**: PASS | CONDITIONAL_PASS | FAIL

## Findings
| ID | Severity | Description | Location |
|----|----------|-------------|----------|
|    |          |             |          |

## Conditions (CONDITIONAL_PASS only)
- [ ] T0xx — <description>

## Required fixes (FAIL only)
- [ ] T0xx — <description>
```

## Acceptance criteria
- [ ] Skill `validation-gates/SKILL.md` documents the verdict format and routing rules.
- [ ] Each reviewer agent (tech-lead, qa-engineer, security-engineer, release-manager) references the skill.
- [ ] Orchestrator's task-management skill includes "FAIL → fix tasks" routing.
