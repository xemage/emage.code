# T602 — Rule L4/X5: replace `poc-security-engineer`'s `execute` tool with fixed-command scanning

**ID:** T602
**Owner:** solution-architect
**Status:** done
**Priority:** P2
**Tier:** judgment
**Affects:** —
**Depends on:** —
**Created:** 2026-10-08
**Based on:**
- `docs/plans/plan-113-poc-security-engineer-tool-scoping.md`
- `docs/artifacts/poc-security-reviewer-blocking-v3.md` §12 X5 (the origin: "replace `poc-security-engineer`'s
  `execute` tool with a fixed-command scanner"; parked as L4)
- `docs/artifacts/security-engineer-audit-server-design-v1.md` (the existing fixed-command audit server design)
- `docs/decisions/ADR-008-knowledge-document-authority.md` and `docs/decisions/ADR-007-command-contract-authority.md`
- The user's instruction of 2026-10-08: "Continue with the next best step".

## 1. What and why

`poc-security-engineer.md` (stable) grants `tools: [read, search, execute, web]`. `execute` is unrestricted command
execution. The production `security-engineer` instead has
`[read, search, mcp__security-audit__run_npm_audit, mcp__security-audit__run_pip_audit,
mcp__security-audit__run_dotnet_list_vulnerable, mcp__security-audit__grep_content, web, mcp__fetch]`: fixed-argv
tools, never a shell string. The PoC reviewer is the agent that finds exposed secrets and injection paths, so it
should not hold an arbitrary-execution tool.

**The complication.** Its Behavior requires reports that need more than the four audit tools provide. For an exposed
secret it must report "the file, line, commits, whether they were pushed, the credential's type and issuer" (around
`:24`). Commit and push status needs git history. Rule how to cover this without arbitrary execution.

Rule:
- **(a)** Whether the `execute` grant should go, and what replaces it. Candidate replacements to evaluate:
  - the four existing `mcp__security-audit__*` tools only;
  - those plus a new fixed-command git-history tool, whose design is for the user to decide (a new tool is
    implementation work under `implementation/runtime/security/`);
  - those plus `search`/`read`, with commit and push status delegated to an agent that holds git access.
- **(b)** Every statement in `poc-security-engineer.md` (and in `poc-orchestrator` § Security Findings) that assumes
  command execution. List them with line numbers. State which ones would break, and which edits (if any) fix them.
- **(c)** Whether a tool-grant change interacts with any contract test or projection. Check
  `tests/functional/test_platform_projections.py`, `test_agent_escalation_consistency.py`,
  `tests/performance/test_tool_use_complexity.py` and `test_audit_server.py`. Name which assert tool lists, and what
  they expect.
- **(d)** Maturity. `poc-security-engineer` is `stable`. State what a tool-grant change does to its maturity
  evidence. Maturity never ranks a conflict (ADR-008 P4); this is only about whether `check-maturity` stays green.

**Decision only.** Write exactly one file. Every option that changes the tool grant, adds a tool, or edits the
`stable` agent is a **user decision**, and a Security Engineer reviews every amendment. Do not design the new tool's
code; if one is recommended, describe its contract (inputs, fixed argv, validation) at the level of
`security-engineer-audit-server-design-v1.md`, and state that implementation is a separate task.

## 2. Output

`docs/artifacts/poc-security-engineer-tool-scoping-v1.md`, containing:

1. **D5 records** for (a)–(d). Each has verbatim clauses with file and line **on the commit your worktree is on**,
   the Step A analysis, the step that fired, the amendment or "held for the user", and a statement that maturity was
   not relied on.
2. **Constraints.** Nothing may weaken any security rule or Immutable Security Constraint. The agent must keep every
   blocking class it has today. No option may leave the agent unable to detect or report an exposed secret.
3. **One user question** covering the options in (a), designed so the user can answer it in one round: 2–4 options,
   each with its consequences (security gain, capability lost, new implementation work, test and projection impact,
   root-drift paths, golden impact), your recommendation, and the candidate edits held verbatim.
4. **Golden and test coupling.** No open golden case cites `poc-security-engineer` (the orchestrator checked, with
   held-out pruned). Confirm, and report the tests in (c) with exactly what they assert. **Never open
   `tests/golden/held-out/`. Never write a golden case name unless that case has a `tests/golden/open/` directory.**
5. **Hit counts** (lines and occurrences) and a summary table.

## 3. Constraints

- **Read access:** the whole repo, except `tests/golden/held-out/`, `.env*`, and any credential or key file.
- **Write access:** your artifact, plus this brief's `**Status:**` line (set it to `in_review`).
- You have no shell. Do not commit, push or merge.
- Quote verbatim, mark omissions with "…", and mark anything you did not re-read **(unverified)**.

## 4. Acceptance criteria

1. Exactly one file is written, with `Based on:`.
2. All four D5 records exist, and (b) lists every execution-dependent statement with line numbers.
3. The user question meets §2.3 and keeps every blocking class and the secret-reporting duty.
4. No amendment weakens a security rule. Every tool-grant or agent edit is a held, user-decided option.
5. No golden case name appears unless it has a `tests/golden/open/` directory.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity
(`critical` | `major` | `minor`). A P5 escalation is a ruling outcome, not a blocker.
