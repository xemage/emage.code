# Agents Overview

emage.code ships with **27 specialist agents** organised by role. Only orchestrators are user-invocable.

The implementation stream keeps the same roster while providing a schema-first runtime model with managed cookbooks, triggers, packaging, and adapter validation.

## Orchestration

| Agent | Role |
|-------|------|
| `@orchestrator` | Production orchestrator — coordinates the full Plan-Approve-Execute lifecycle |
| `@poc-orchestrator` | PoC orchestrator — hypothesis-first validation with debt tracking |

## Engineering

| Agent | Permissions | Role |
|-------|-------------|------|
| `@backend-developer` | write | API endpoints, business logic, services |
| `@frontend-developer` | write | UI components, pages, client-side logic |
| `@database-engineer` | write | Schema, migrations, complex queries |
| `@devops-engineer` | write | CI/CD, Docker, infra-as-code |
| `@solution-architect` | write (architecture only) | Architecture, ADRs, design docs |
| `@tech-lead` | read-only during review | Code review, technical guidance |

## Quality & Security

| Agent | Permissions | Role |
|-------|-------------|------|
| `@qa-engineer` | write (tests only) | Test plans, automated tests, bug reports |
| `@security-engineer` | read-only | OWASP audits, security findings |

## Product & Process

| Agent | Permissions | Role |
|-------|-------------|------|
| `@product-owner` | read-only | Requirements, priorities, approvals |
| `@scrum-master` | write (process docs) | Sprint plans, GitLab issue breakdown |
| `@release-manager` | write (release docs) | Versioning, changelog, release prep |
| `@technical-writer` | write (docs only) | API docs, user guides |
| `@ux-designer` | write (design docs) | User flows, wireframes |

## Specialist / PoC

| Agent | Role |
|-------|------|
| `@feasibility-agent` | Quick feasibility studies |
| `@technology-scout` | Evaluate APIs, SDKs, platforms |
| `@integration-agent` | External system integration |
| `@scaffolding-agent` | Project bootstrap |
| `@data-mockup-agent` | Synthetic test data |
| `@evaluation-agent` | PoC outcome assessment |
| `@demo-agent` | Demo preparation & walkthroughs |
| `@technical-debt-narrator` | Debt scorecards |
| `@poc-devops-engineer` | PoC infra (lighter than production) |
| `@poc-qa-engineer` | PoC happy-path testing |
| `@poc-security-engineer` | PoC threat modelling |
| `@poc-technical-writer` | PoC documentation |

## Permission boundaries

- **Write-capable** agents may modify code in their assigned worktree only.
- **Read-only** agents (Tech Lead during review, Security Engineer during audit, Product Owner always) can flag issues, annotate, and request changes — never edit.
- **Conditional** permissions (QA, Architect) restrict write access to specific file types.

Permission violations are logged and tasks rejected. See [Security Guidelines](https://gitlab.com/em-age/emage.code/-/blob/main/.github/instructions/security-guidelines.instructions.md).

## v3 note

The permission model stays the same in v3. What changes is the surrounding
workflow contract: use the stricter v3 validation gates for cookbook manifests,
trigger policies, package install/update/uninstall, and adapter smoke tests.
