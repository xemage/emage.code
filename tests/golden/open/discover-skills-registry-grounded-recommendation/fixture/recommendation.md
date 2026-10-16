## Recommended skills for: implementing T525's golden cases and marking the task done

### Mandatory

| Skill | Why | Mandatory? |
|-------|-----|------------|
| `verification-before-completion` | Implementation work ending in a done claim — run the gate before reporting complete. | yes |
| `systematic-debugging` | A check returned red; investigate before changing the check. | yes |

### Suggested

| Skill | Why | Mandatory? |
|-------|-----|------------|
| `testing-strategy` | Choosing what each golden case should assert and at which layer. | no |
| `validation-gates` | The case authoring feeds a PASS/CONDITIONAL_PASS/FAIL gate verdict. | no |
| `worktree-isolation` | The task runs in an isolated agent worktree off `develop`. | no |

### Next command
`/validate-tasks`, or load the `verification-before-completion` skill
