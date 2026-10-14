# T633 — Release-level Security Engineer audit of the installer and the PoC scanner (audit C-6)

**ID:** T633
**Owner:** security-engineer
**Status:** pending
**Priority:** P1
**Tier:** judgment
**Depends on:** —
**Affects:** —
**Created:** 2026-10-14
**Completed:** —
**Based on:**
- `docs/plans/plan-121-release-v8-wave-2.md` (Task Decomposition item for T633)
- `docs/artifacts/release-v8-audit-v1.md` C-6 and §2.1; `scripts/install.sh` (765 changed lines since v7.0.1), `scripts/merge-mcp-json.py`, `scripts/merge-task-docs.py`, `scripts/render_installed_agents.py`, `scripts/publish-release.py`, `scripts/dry-run-publish-release.py`
- `implementation/runtime/security/` (`poc_scan.py`, `poc_audit_server.py`, `git_executor.py`) and the existing reviews `docs/artifacts/security-review-*.md`
- `AGENTS.md` and `.claude/rules/security-guidelines.md` (OWASP checklist, Security Review Workflow)
- The user's approval of plan-121 on 2026-10-14 (AskUserQuestion, verbatim option label): "Approve as written (Recommended)", together with the decisions quoted in `docs/plans/plan-121-release-v8-wave-2.md` (header).

## 1. What and why

Run the OWASP Top 10 checklist over the security-sensitive code that shipped since v7.0.1 and has had no release-level review: above all the installer (the rewritten copy engine, the `eval "$saved_shopt"` helpers, rsync and no-rsync paths, symlink and bind-mount handling, `--update` spares, path handling and permissions, handling of `.mcp.json` and settings merges, anything that copies runtime source into target projects) and the merge scripts; then confirm the PoC scanner stack against its existing reviews and the contract v6. Grade every finding `SECURITY:CRITICAL`/`HIGH`/`MEDIUM`/`LOW`; a `HIGH` or `CRITICAL` blocks the release. Verdict `PASS`/`CONDITIONAL_PASS`/`FAIL` with conditions (owner, fix, deadline). You are read-only; you have no write tool: return the review as your final report and the orchestrator records it as `docs/artifacts/security-review-release-v8-v1.md`. State what you could not verify (you cannot run code).

## 2. Output

Your report: scope covered, verdict, a findings table (ID, grade, concern, fix), conditions, OWASP coverage table, what you did not verify.

## 3. Constraints

- **Write access:** none. Read-only.
- Never open `tests/golden/held-out/` unless this brief explicitly authorizes it; never write a held-out case id anywhere (brief, report, commit message, branch name, ledger row, artifact); never write a golden case name unless that case has a `tests/golden/open/` directory. Run `python3 -m unittest tests.functional.test_golden_held_out_isolation` on every artifact before it is committed.
- No `.env*` or credential files; do not read the user's local `.claude/settings.json` or `.vscode/mcp.json`.
- Mark anything you did not re-read **(unverified)**.

## 4. Acceptance criteria

1. Every in-scope file is covered or listed as not covered with the reason.
2. Every finding has a grade, a concern and a fix.
3. No file is modified.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
