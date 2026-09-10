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
| `@database-engineer` | write | Designs schemas, writes reversible migrations, and optimizes slow queries using EXPLAIN/ANALYZE and index strategy documents. |
| `@devops-engineer` | write | Builds GitLab CI/CD pipelines, Dockerfiles, and infrastructure-as-code, and owns deployment automation from staging through production. |
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
| `@feasibility-agent` | Stress-tests critical assumptions early and produces a Red/Yellow/Green risk rating with a Go/No-Go recommendation before implementation effort is spent. |
| `@technology-scout` | Evaluate APIs, SDKs, platforms |
| `@integration-agent` | Wires third-party APIs and SDKs into a PoC quickly, documenting required environment variables and failure-mode notes for each integration. |
| `@scaffolding-agent` | Creates a minimal, runnable project skeleton with basic dependency setup, avoiding overengineering and non-essential tooling for a PoC timeline. |
| `@data-mockup-agent` | Generates realistic, deterministic synthetic demo data (seed scripts, fixtures, example payloads) when real production data is unavailable or inappropriate. |
| `@evaluation-agent` | Determines whether a PoC actually validated its hypothesis, tying its Validated/Invalidated/Inconclusive verdict directly to observable evidence. |
| `@demo-agent` | Demo preparation & walkthroughs |
| `@technical-debt-narrator` | Documents every PoC shortcut in a Technical Debt Scorecard with severity, remediation effort, and ownership, so production teams inherit an explicit backlog. |
| `@poc-devops-engineer` | Sets up the minimal local-first run loop (clone, configure, run within minutes) for a PoC, adding containerization only if it speeds up adoption. |
| `@poc-qa-engineer` | Validates only the happy-path demo flow and core hypothesis checks for a PoC, explicitly skipping full regression suites and performance certification. |
| `@poc-security-engineer` | Performs a pragmatic PoC security scan that flags obvious secrets exposure and injection/auth risks without blocking rapid hypothesis validation. |
| `@poc-technical-writer` | Writes lean PoC documentation covering how to run the build, required environment variables, and known limitations for rapid handoff. |

## Platform / Infrastructure

| Agent | Role |
|-------|------|
| `@context-retriever` | Read-only knowledge-retrieval subagent that answers "find prior knowledge relevant to `<query>`" requests against the persistent memory vault's hybrid semantic+lexical+structural index, scoped to the calling session's own project and platform. |

## Permission boundaries

- **Write-capable** agents may modify code in their assigned worktree only.
- **Read-only** agents (Tech Lead during review, Security Engineer during audit, Product Owner always) can flag issues, annotate, and request changes — never edit.
- **Conditional** permissions (QA, Architect) restrict write access to specific file types.

Permission violations are logged and tasks rejected. See [Security Guidelines](https://gitlab.com/em-age/emage.code/-/blob/main/.github/instructions/security-guidelines.instructions.md).

## v3 note

The permission model stays the same in v3. What changes is the surrounding
workflow contract: use the stricter v3 validation gates for cookbook manifests,
trigger policies, package install/update/uninstall, and adapter smoke tests.
