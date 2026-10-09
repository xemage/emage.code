# plan-113 — Tool scoping for `poc-security-engineer` (L4/X5)

**Created:** 2026-10-08
**Based on:** the user's instruction of 2026-10-08, "Continue with the next best step";
`docs/artifacts/poc-security-reviewer-blocking-v3.md` §12 X5; plan-099.
**Scopes:** `T602`, `T603`, `T604`.

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

## 5. T603 review and follow-up (2026-10-09)

- **Code review round 1: FAIL** (P-1 HIGH, P-2..P-4 MEDIUM, 8 LOW). The orchestrator tested the claims on git 2.43.0:
  P-1 did **not** reproduce, P-2 and P-3 did. The work went back for retry 1.
- **Round 2: CONDITIONAL_PASS.** P-1 was re-graded to LOW. Details are in
  `security-review-poc-security-audit-code-v1.md`.
- **Condition C-1 remediation plan.** The unquoted `KEY=value` rule gap and the untracked-`.env*` name check are
  owned by `@orchestrator`, with **T604** as the deadline. T604 must be done no later than the production handoff of
  any PoC that relies on the scanner.
- **Next:** T604 (backend-developer, P2) covers C-1, the LOW findings L-1, L-2 and L-7, and the extra token formats.
  The unquoted-rule false-positive trade-off goes to the user first.
- **User action remaining after T603 merges:** allow `mcp__poc-security-audit__*` in `.claude/settings.json`. That
  file is client-owned and is never auto-edited. Until then the tools are denied, which fails closed.

## 6. T604 (2026-10-09)

- **T604 closes condition C-1.** The unquoted-credential rule was added as the user decided ("Add it, tuned"), along
  with the untracked `.env*` name check, L-1, L-2, L-7 and the extra token formats.
- **Security Engineer review: PASS** (`security-review-poc-security-audit-code-v2.md`). 0 critical, 0 high, 0 medium
  and 6 low findings (SEV-1..SEV-6), which are tracked as technical debt.
- **Orchestrator checks.** All six real secret shapes hit and 11 of 12 harmless lines did not. `MAX_TOKENS=100000000`
  is a documented false positive. An 800 KB single line completes in 0.2 s. Adversarial keyword-dense lines time out
  at 60 s and fail closed. An ignored `.env` is reported by name. No secret value appears in any output.
- **Suite 978 OK.**
- **Parked (T605, not scheduled):** SEV-1..SEV-6 and three missing pins.
- **Still with the user:** allow `mcp__poc-security-audit__*` in `.claude/settings.json`. That file is client-owned and
  is never auto-edited.
