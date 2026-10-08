# plan-113 — Tool scoping for `poc-security-engineer` (L4/X5)

**Created:** 2026-10-08
**Based on:** the user's instruction of 2026-10-08, "Continue with the next best step";
`docs/artifacts/poc-security-reviewer-blocking-v3.md` §12 X5; plan-099.
**Scopes:** `T602`, `T603`.

## 1. Why now

Every substantive rule item is closed. What remains of real value is a hardening item: the PoC security reviewer holds
an unrestricted `execute` tool, while the production `security-engineer` holds only fixed-argv audit tools.

## 2. Sequence

1. **T602** (solution-architect, decision only): D5 records, the list of execution-dependent statements, the test
   coupling, and one user question.
2. Orchestrator verification, then a Security Engineer review of every amendment.
3. The user decides the tool grant.
4. Implementation as a separate task. It may include new runtime code (a fixed-command git-history tool) only if the
   user chooses it.

## 3. Not in scope

The notes in plan-112 §2, and the other X-items (X1–X4, X6–X8).

## 4. Outcome (2026-10-09)

- **T602 ruling** (`poc-security-engineer-tool-scoping-v1.md` → `-v2.md`). The orchestrator verified it: the quotes,
  that no live golden case cites the agent, and the claim that `grep_content` prints matched text, so the four
  existing tools cannot meet the agent's "redacted output" duty.
- **User decisions** (2026-10-09, verbatim option labels):
  - Tool grant: **"New 2-tool server (Recommended)"**.
  - `grep_content`: **"Keep, record residual (Recommended)"**.
- **Security Engineer review: CONDITIONAL_PASS** (`security-review-poc-security-engineer-tool-scoping-v1.md`): 8
  medium and 4 low findings, all adopted in v2.
- **Orchestrator reproduction.** A planted `core.fsmonitor` command runs under a plain `git grep` and is blocked by
  the hardened invocation. Git's `-z -n` layout is `path NUL line NUL text`.
- **Next: T603** (backend-developer, P2) implements v2: the new `poc-security-audit` server with two tools, its
  tests, the registrations, and then the grant swap and held edits.
