# T604 — Close the T603 review residuals: unquoted-secret rule, untracked secret files, LOW findings

**ID:** T604
**Owner:** backend-developer
**Status:** pending
**Priority:** P2
**Tier:** standard
**Affects:** —
**Depends on:** T603
**Created:** 2026-10-09
**Based on:**
- `docs/artifacts/security-review-poc-security-audit-code-v1.md` (condition C-1 and findings L-1..L-8)
- `docs/plans/plan-113-poc-security-engineer-tool-scoping.md` §5
- `docs/artifacts/poc-security-engineer-tool-scoping-v2.md` (the contract)

## 1. What and why

This is the deadline task for the C-1 remediation plan. It must be done no later than the production handoff of any
PoC that relies on the scanner.

**Before dispatch, the orchestrator puts one question to the user:** whether to add an unquoted-assignment rule
(`KEY=value` / `key: value`), given its false-positive cost (`TOKEN_TTL=3600`, `key: value` in YAML). The user's answer
decides the scope of item 1.

1. **Unquoted-assignment rule** (only as the user decides). Add it with a tuned pattern, a sample per rule, and tests
   for the false-positive cases. Bump `RULES_VERSION`.
2. **Untracked secret files by name** (about 10 lines, no content read). For `scope == "worktree"`, after the grep, run
   `ls-files -z --others` without `--exclude-standard`, so ignored files are included. Feed the names through the same
   `TRACKED_NAME_PATTERNS` loop as `scan_tracked_names`. Report a hit as a redacted name, never content.
3. **L-1:** add `-o` to `git grep` and dedupe `(path, line)` per rule, so a huge single line cannot blow the byte cap.
4. **L-2:** keep `git_failed` from `rev-parse` unless the exit was a genuine "not a repository", so old git and
   SHA-256 repositories are reported correctly.
5. **L-7:** make the process-death test treat a zombie as dead (read `/proc/<pid>/stat` state `Z`).
6. **Extra token formats:** npm (`npm_…`), SendGrid (`SG.…`), JWT (`eyJ…`), each with a sample and a placeholder test.
7. **Document** L-4, L-5 and L-6 as limits in the module docstring and in the result documentation. L-3 (the
   placeholder heuristic) is a decision for the user; do not change it.

## 2. Controls

- **Review.** A Security Engineer reviews the code before merge.
- **Gates.** `sync.mjs --check`, `generate-registry.py --check`, `check-maturity.py --root implementation`,
  `scorecard.py --check` (34 / 26 / 0), `validate-tasks.py`, and the evaluator hash green against **v20**.
- **Tests.** Run `python3 tests/run.py`, redirected to a file. Every existing test passes, and each new behaviour has a
  test that can fail.

## 3. Constraints

- **Write scope:** `implementation/runtime/security/` (the three new modules only), their tests, the regenerated
  mirrors and registry (if the rule table is exposed there), the drift baseline, and this brief's `**Status:**` line.
- **Forbidden:**
  - `tests/golden/` (never open held-out);
  - `scripts/`;
  - `.claude/settings.json` and any other client-owned settings;
  - `.env*`, credential or key files.
- **Commit:** one Conventional Commit, ending with `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`.
  **Do not push. Never run `glab mr merge` or any merge or approve API, with no exception.**

## 4. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity
(`critical` | `major` | `minor`).
