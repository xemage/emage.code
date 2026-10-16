# T606 — Rule how a scanner finding can be flagged as a placeholder without weakening the secret check (L-3)

**ID:** T606
**Owner:** solution-architect
**Status:** done
**Priority:** P2
**Tier:** judgment
**Depends on:** —
**Affects:** —
**Created:** 2026-10-09
**Completed:** —
**Based on:**
- `docs/plans/plan-114-placeholder-flag-and-naming-rulings.md`
- `docs/artifacts/security-review-poc-security-audit-code-v1.md` (L-3) and `-v2.md`
- `docs/artifacts/poc-security-engineer-tool-scoping-v2.md` (contract F-1..F-11; incomplete scan is FAIL, never PASS)
- `implementation/runtime/security/poc_scan.py`, `poc_audit_server.py`; `implementation/knowledge/agents/poc-security-engineer.md`
- The user's decision of 2026-10-09: "A - it must be possible though to flag a finding as placeholder, so it does not block".

## 1. What and why

The scanner (`poc-security-audit`) reports every candidate secret and stays strict: `password=changeme` is a hit. A real PoC
has placeholders (`changeme`, `<your-key>`, `xxxx`) that should not block. The user wants a way to **flag a finding as a
placeholder so it does not block**. The earlier heuristic (skip values starting with `$`, `<`, `{` or a space) was rejected
because it hides real secrets (L-3).

Rule:
- **(a)** Where the flag lives. Candidates: (1) a reviewer-side annotation in the review record, made by the agent or a
  human, naming the finding by file, line and rule; (2) a committed allowlist file read by the scanner (a repo-reviewed
  list of path, line and rule); (3) an inline marker in the scanned source. Evaluate each against: can a hostile commit
  use it to hide a real secret; who may set it; is it reviewed; does it survive line moves and history scans.
- **(b)** What "does not block" means. The finding must still appear in the output, marked as placeholder, never vanish.
  State how it is counted in the verdict, and how an incomplete scan is still FAIL (F-8).
- **(c)** The authority. Who may flag (the reviewer agent alone, the orchestrator, only the user), and whether a flag
  needs a written reason.
- **(d)** Which files an implementation touches (scanner, server, agent text, tests), the contract tests that pin tool
  lists, and whether projections or root drift change. Maturity of `poc-security-engineer` (`stable`) must not be relied on.

**Decision only.** Write exactly one file. Do not write code. Every option that changes the agent or scanner is a held
user decision. A Security Engineer reviews it afterwards.

## 2. Output

`docs/artifacts/placeholder-flag-ruling-v1.md`, containing:

1. Records for (a)–(d), with verbatim clauses and file:line on the commit your worktree is on, marking anything not re-read **(unverified)**.
2. **Constraints.** No option may lower the no-secrets rule (Immutable Security Constraint 1), may let a flag hide a
   finding from the output, or may make an incomplete scan pass.
3. **One user question** with 2–4 options, each with its consequences (what a hostile commit can do, new implementation
   work, tests and root-drift paths), your recommendation, and the candidate edits held verbatim.
4. A summary table.

## 3. Constraints

- **Read access:** the whole repo, except `tests/golden/held-out/`, `.env*`, and any credential or key file.
  Never open `tests/golden/held-out/`. Never write a golden case name unless that case has a `tests/golden/open/` directory.
- **Write access:** your artifact, plus this brief's `**Status:**` line (set it to `in_review`).
- You have no shell. Do not commit, push or merge.

## 4. Acceptance criteria

1. Exactly one file is written, with `Based on:`.
2. (a)–(d) are all answered, and the user question meets §2.3.
3. No option lets a flag hide a finding or lets an incomplete scan pass.
4. No golden case name appears unless it has a `tests/golden/open/` directory.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity
(`critical` | `major` | `minor`).
