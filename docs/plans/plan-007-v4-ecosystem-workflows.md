# Plan 007 — v4.0.0 Ecosystem Workflows

Based on: `docs/artifacts/research-agents-skills-ecosystem-v1.md`

## Objective

Close the highest-value gaps vs Superpowers and Awesome OpenCode by adding
mandatory workflow skills, agent safety guards, session handoff, background-agent
triggers, and registry-driven skill discovery — without changing the v3
schema-first architecture.

## Scope (v4.0.0)

| Item | Deliverable | Priority |
|------|-------------|----------|
| Systematic debugging | `knowledge/skills/systematic-debugging/SKILL.md` | P1 |
| Receiving code review | `knowledge/skills/receiving-code-review/SKILL.md` | P1 |
| Verification before completion | `knowledge/skills/verification-before-completion/SKILL.md` | P1 |
| Agent safety guards | `knowledge/instructions/security-guidelines.md` section | P1 |
| Session handoff | `/handoff` command + `triggers/examples/handoff-resume.json` | P1 |
| Background agents | `triggers/examples/background-agent-delegate.json` | P2 |
| Skill discovery | `/discover-skills` command + registry integration | P2 |
| Skills bootstrap | `AGENTS.md` mandatory skill workflow section | P1 |

## Out of scope (v4.x follow-up)

- Pi extension bridge (TypeScript)
- Plan annotation UI
- OPA/Rego policy layer (Cupcake-style)

## Acceptance criteria

- [ ] Three new skills in canonical knowledge; projected to all 5 platforms
- [ ] Two new slash commands; projected to all platforms
- [ ] Two new trigger examples validated by `check-v3.py --triggers`
- [ ] Security guidelines include destructive-command and secret-file guards
- [ ] `AGENTS.md` documents mandatory skill check before implementation
- [ ] `node sync-v3.mjs` + `verify-v3.mjs` pass with no drift
- [ ] Registry regenerated with new entries
- [ ] `docs/releases/v4.0.0.md` with Install + Highlights
- [ ] 78+ tests pass

## Release path

1. `feature/v4-ecosystem-workflows` → `develop` (MR)
2. `release/v4.0.0` → `main` (MR + tag)
3. Back-merge `main` → `develop`
