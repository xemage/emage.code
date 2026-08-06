# Task T330 — CWSO overview -> deployment -> agent-usage narrative guide

**ID:** T330
**Owner:** technical-writer
**Status:** done
**Completed:** 2026-08-06
**Priority:** P2
**Depends on:** T327
**Created:** 2026-08-06
**Based on:** `docs/plans/plan-018-cwso-agent-knowledge-awareness.md`; `implementation/runtime/cwso/README.md`;
`docs/artifacts/role-mapping-cwso-v1.md`; `docs/deployment/README.md`; `docs/deployment/local-docker-desktop-guide.md`;
`docs/deployment/cwso-emage-orchestrator-connection-guide.md`; `implementation/knowledge/skills/cwso-awareness/SKILL.md`
(T327 output)

## Objective

The user's verbatim ask: "a complete guide showing me first an overview and goal, starting from pure
emage.code over deployment of CWSO to how does an agent use CWSO (do I need to update agent knowledge or
skills?)". Author ONE coherent narrative document answering, in order: (1) what CWSO is and why emage.code
integrates it (Pattern A concurrent multi-agent code editing); (2) how it's deployed locally — link the
existing three deployment docs, do not re-derive their content; (3) how it's actually invoked at runtime by
agent code — link `implementation/runtime/cwso/README.md` and summarize the role-split rule at a high level
(full detail stays in that README); (4) whether agent knowledge/skills needed updating — answer: yes, and it
was done, by T327 (link the new skill and the three updated agent files as evidence, don't just assert it).

## Inputs

- `implementation/runtime/cwso/README.md` (Pattern A usage guide, task T319)
- `docs/artifacts/role-mapping-cwso-v1.md` (task T211)
- `docs/deployment/README.md`, `docs/deployment/local-docker-desktop-guide.md`,
  `docs/deployment/cwso-emage-orchestrator-connection-guide.md` (existing, accurate, tested — link only)
- `implementation/knowledge/skills/cwso-awareness/SKILL.md` and the three edited agent files (T327 output)
- Evidence of validation history: task files `docs/tasks/task-T214.md`, `task-T304.md`, `task-T319.md` — cite
  these as the source of "previously validated via manual/live testing," do not present CWSO integration as new
  or unverified.

## Constraints

- File ownership: one new document only. Suggested path:
  `docs/deployment/cwso-overview-and-agent-integration-guide.md` (place alongside the other deployment docs
  since `docs/deployment/README.md` is the existing index page these link from — do not edit `README.md`
  itself; that's out of scope for this plan).
  If a more appropriate location is identified (e.g. under `docs/artifacts/` since this is more "how the whole
  system fits together" than "how to deploy to environment X"), the technical-writer may choose it but must
  report the chosen path clearly and justify the deviation from the suggested path in one sentence.
- Do NOT duplicate the full content of the three deployment docs or `implementation/runtime/cwso/README.md` —
  link + summarize in 1-3 sentences per linked doc, max.
- Do NOT invent a different role-mapping table — reference the one in T327's skill / the source artifact.
- Must be honest that CWSO integration (Pattern A, live server, JWT auth, 11-tool contract) was already
  validated through manual/live testing across T214, T304, T319, and the user's own 2026-08-06 manual
  validation — not a new or speculative integration.
- Do not touch `.vscode/mcp.json`, `deploy/local-dev/`, `docs/deployment/cwso-emage-orchestrator-connection-guide.md`,
  `scripts/mint-cwso-jwt.py`.

## Expected outputs

One new markdown document with (at minimum) these sections in this order:
1. **Overview and goal** — what CWSO is, why emage.code integrates it, what problem Pattern A solves.
2. **Deployment** — brief summary + links to the three existing deployment docs (which one to use when).
3. **Runtime usage** — brief summary + link to `implementation/runtime/cwso/README.md`; state the
   worker/orchestrator role-split rule exists and link for full detail, do not re-derive the full table here.
4. **Agent knowledge and skills** — answers "do I need to update agent knowledge or skills?" with: yes, and
   this was done — links to `implementation/knowledge/skills/cwso-awareness/SKILL.md` and the three updated
   agent files, plus a one-line note on how to verify the projection landed
   (`grep -rl -i cwso .claude/skills .claude/agents`).

## Acceptance criteria

1. The document exists at the reported path and covers all four sections above in order.
2. No section duplicates more than ~3 sentences of any linked document's content.
3. The document explicitly states CWSO was previously validated via manual/live testing (cites at least
   T214, T304, or T319), not framed as new/unverified.
4. All internal links resolve to real, existing files.

## Blocker protocol

Report blockers as: type + severity + proposed mitigation. Max 2 retries before escalating to the orchestrator.

## Execution notes

Created `docs/deployment/cwso-overview-and-agent-integration-guide.md` (suggested path used as-is) with the
four required sections in order: Overview and goal; Deployment (links to `README.md` and
`local-docker-desktop-guide.md`, no duplication); Runtime usage (links to
`implementation/runtime/cwso/README.md`, states the role-split fact at high level only); Agent knowledge and
skills (states "yes, already done," links to the `cwso-awareness` skill and the three updated agent files,
gives the verification grep command). Explicitly documents prior manual/live validation (T214, T304, T319,
and the user's own 2026-08-06 validation) rather than framing CWSO as new/unverified. All internal links
verified to resolve against real files on disk. Did not edit `docs/deployment/README.md` or any other
existing file. Committed as `docs(T330): CWSO overview -> deployment -> agent-usage narrative guide`.

Outcome: PASS.
