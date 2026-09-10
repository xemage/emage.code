# Instructions Overview

This page documents the 4 passive, cross-cutting `instruction` components,
filling a documentation gap noted directly in
`docs/artifacts/maturity-promotion-criteria-v1.md`: instructions previously
had no dedicated overview page under `docs/wiki/**`, unlike agents (see
[Agents Overview](agents-overview)) or commands/skills (see
[Commands and Skills Overview](commands-and-skills-overview)). Unlike a
command or skill, an instruction is never invoked directly — it is projected
into every supported platform's own rule/instruction mechanism (`.github/
instructions/*.instructions.md`, `.cursor/rules/*.mdc`, `.claude/rules/*.md`,
and so on) and applies automatically whenever its `applyTo` glob matches the
file or situation an agent is working in.

A dedicated page for instructions, separate from `commands-and-skills-
overview.md`, is deliberate: instructions are not "referenced by ≥1 command
or agent" the way a skill or agent is (see `maturity-promotion-criteria-
v1.md` §1) — they are consumed passively across every platform's automatic
rule-application mechanism, a structurally different relationship than a
skill being invoked by id or a command declaring its owning agent. Mixing
the two into one page would blur that distinction rather than clarify it.

## Instructions

| Instruction | `applyTo` | Role |
|-------------|-----------|------|
| `coding-standards` | `**/*.{ts,js,py,java,cs,go,rs,rb,php,swift,kt}` | Naming conventions, function-design limits (max 50 lines, max 4 parameters, early returns), error-handling patterns, baseline security hygiene, code organization, and the `<type>-vN.md` artifact-versioning convention every other knowledge-base component's own filename follows. |
| `git-workflow` | `**` | GitFlow branching strategy, the "no direct commits to `main`/`develop`, ever" protected-branch rule (including for docs-only or ledger-only changes), agent worktree lifecycle, and Conventional Commits format. |
| `poc-guidelines` | `**` | Hypothesis-first validation for PoC workstreams, mandatory `POC-DEBT` shortcut tagging, and the Debt Scorecard a PoC cannot be marked complete without. |
| `security-guidelines` | `**` | OWASP Top 10 prevention patterns, agent permission classification (write-capable vs. read-only vs. conditional), and the Immutable Security Constraints that no agent or PoC time pressure may override. |

`coding-standards` and `security-guidelines` are the two instructions
`AGENTS.md` names explicitly, in its "Code Standards" and "Security"
sections respectively, listing every platform's own projected path for each
(`.github/instructions/coding-standards.instructions.md`,
`.cursor/rules/security-guidelines.mdc`, and so on) — the routing table a
developer or agent follows to find the platform-native copy of the rule
that's actually active in their current environment.

`git-workflow` is the instruction `release-manager.md`'s own "Git Flow for
Releases" section builds on: a release branch's stabilization flow is a
specialization of the same protected-branch and MR-only rules this
instruction defines project-wide, not an exception to them.

`poc-guidelines` is the instruction `poc-orchestrator.md`'s "Mandatory Debt
Tracking" section defers to for the full tagging convention and Debt
Scorecard format — the agent's own summary is deliberately short precisely
because the authoritative rules live here, in the instruction, not
duplicated across every PoC-track agent file that needs them.
