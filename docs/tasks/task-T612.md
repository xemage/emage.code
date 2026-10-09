# T612 — Make altered-path hits unflaggable and add the regex-library self-test (T611-2, T611-3)

**ID:** T612
**Owner:** backend-developer
**Status:** done
**Priority:** P2
**Tier:** standard
**Depends on:** —
**Affects:** —
**Created:** 2026-10-09
**Completed:** —
**Based on:**
- `docs/plans/plan-116-poc-scanner-path-flags-and-regex-selftest.md`
- `docs/artifacts/security-review-t611-scanner-residuals-v1.md` (T611-2, T611-3)
- `docs/artifacts/poc-security-engineer-tool-scoping-v4.md` (§12 open residuals) and `-v3.md`; v1-v4 are immutable
- `docs/artifacts/placeholder-flag-ruling-v3.md` (flag semantics) and `security-review-t608-placeholder-flag-text-v1.md`
- `implementation/runtime/security/poc_scan.py`, `poc_audit_server.py`, `git_executor.py`, `tests/functional/test_poc_audit_server.py`, `test_placeholder_flag_text.py`
- The user's instruction of 2026-10-09: "Continue with the next best step".

## 1. What

**T611-2 (altered paths).** `safe_name` strips control/format/separator characters and caps names at 200 characters, so the
returned `path_or_redacted` of such a file is no longer the real git path. The agent's flag logic keys on that value and on a
"paths modified since `flag_commit`" list built from real paths, so a later change to the file never voids its flag, and
colliding displayed names merge their `hit_count`. Fix: when `safe_name` changed a name, mark the hit (for example
`path_altered: true`, added to `HIT_KEYS` and validated in `add_hit`), and state in the agent text
(`poc-security-engineer.md`, `poc-orchestrator.md`) that a hit with an altered path cannot be flagged and stays unresolved
(fail closed). Pin the new key, the contract v5 delta and the agent phrases. Redaction behaviour (T611-1) must not change.

**T611-3 (regex-library portability).** The bounded repeats `{7,1024}`, `{1024}` and `{10,512}` exceed `RE_DUP_MAX` 255 on some
regex libraries; `git grep -E` then fails to compile and every scan ends `git_failed` without a reason. Fix: a startup
self-test that compiles the largest rule through `git grep` (through `git_executor` only, same hardening, aggregate deadline, no
new subprocess surface) and reports a clear error code (for example `regex_unsupported`, `complete: false`, no hits dropped, no
secret-free claim) instead of a bare `git_failed`; document the regex-library requirement (`RE_DUP_MAX` of at least 1024) in the
contract. The self-test must fail closed, must not slow a normal scan noticeably, and must not hide a scan result.

**R-1** stays documented only.

Contract changes go into a NEW immutable artifact `docs/artifacts/poc-security-engineer-tool-scoping-v5.md` (a delta on v4).
Bump `RULES_VERSION` only if a rule pattern changes (it should not).

## 2. Constraints

- **Read access:** the whole repo, except `tests/golden/held-out/`, `.env*`, and any credential or key file. Never open `tests/golden/held-out/`; never write a golden case name unless that case has a `tests/golden/open/` directory. Run `python3 -m unittest tests.functional.test_golden_held_out_isolation` before committing.
- Work in your own worktree/branch; one Conventional Commit ending with `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`. Do not push; do not merge; do not edit `.claude/` (outside the generated `implementation/.claude` mirror), `.github/` or other derived top-level folders, `docs/tasks/active-tasks.md`, `completed-tasks.md`, or any brief's Status line.
- Keep every rule, label condition and fail-closed path unchanged. F-8, E1-b, E1-c and both tool lists stay byte-identical. No matched text in any result or log.
- Regenerate with `node implementation/scripts/sync.mjs --root implementation` and `python3 implementation/scripts/generate-registry.py`. Declare any root drift in `tests/_baselines/root-install-drift.json` (currently empty; sorted paths plus one comment line "Declared 2026-10-09 by T612 (...)"). Do NOT refresh the root install.
- Gates to report: `sync.mjs --check`, `generate-registry.py --check`, `check-maturity.py --root implementation`, `scorecard.py --check` (34/26/0), `validate-tasks.py`, the evaluator hash via `implementation/runtime/golden_harness/evaluator_hash.py` (baseline v20 unchanged), the held-out isolation test, and the full suite `python3 tests/run.py` redirected to a file.

## 3. Outputs

Scanner and server changes, tests (altered path via stripped control character and via a 250-character name, collisions, the self-test passing and the failure path simulated through the executor, fail-closed behaviour), contract v5, agent text with regenerated mirrors and registry, a report with the gate results, suite summary line, drift paths and every deviation.

## 4. Acceptance criteria

1. A hit whose path was altered carries the marker, the agent text makes it unflaggable and unresolved, and unaltered paths are unchanged.
2. The self-test reports a clear error code on a simulated compile failure, never turns it into a clean result, and costs one cheap call on a normal scan.
3. All gates and the full suite pass; no root refresh.
4. A Security Engineer code-reviews the change before merge (the orchestrator dispatches it).

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
