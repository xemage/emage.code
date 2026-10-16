# T611 — Clean up the PoC scanner residuals: SEV-1..SEV-6 with three pins (old T605) and T609-10..T609-13

**ID:** T611
**Owner:** backend-developer
**Status:** done
**Priority:** P2
**Tier:** standard
**Depends on:** —
**Affects:** —
**Created:** 2026-10-09
**Completed:** —
**Based on:**
- `docs/plans/plan-115-poc-scanner-residual-cleanup.md`
- `docs/artifacts/security-review-poc-security-audit-code-v2.md` (SEV-1..SEV-6) and `-v1.md`
- `docs/artifacts/security-review-t609-template-label-v1.md` (T609-10..T609-13)
- `docs/artifacts/poc-security-engineer-tool-scoping-v3.md` (contract v3; v2 and v1 are immutable)
- `implementation/runtime/security/poc_scan.py`, `poc_audit_server.py`, `tests/functional/test_poc_audit_server.py`
- The user's instruction of 2026-10-09: "Continue as suggested".

## 1. What

Fix the LOW residuals below in one pass. Every item fails closed today; the point is accuracy and robustness, not a new
feature. Do not weaken any rule, label condition or fail-closed path. Keep F-8, E1-b, E1-c and both tool lists byte-identical.

**From the T604 code review (old "T605"):**

- **SEV-1** (quadratic cost on keyword-dense and `eyJ`-dense single lines). Measured: `"password"*100000` and `"eyJ"*266000` on one line run to the 60 s deadline and fail closed. Add a timing test (both lines, expecting completion within about 10 s). If slow, bound the name run in `_not_ending` and the credential rules (for example `[A-Za-z0-9_-]{0,64}`). Check regex size and compile time first, because bounded repeats duplicate nested nodes. A bound creates a new blind spot (a credential name longer than the bound): document it in the contract and in the agent blind-spot bullet, and keep it fail-closed otherwise.
- **SEV-2** the Python `_name_scan` loop is not bound by the deadline (a multi-second stall at about 2M names): check the deadline every ~4096 names and stop with `timeout` / `complete: false`.
- **SEV-3** returned file names are verbatim and can carry hostile text into the reviewing agent's context: strip control characters and cap the returned length (about 200), without changing the redaction rules.
- **SEV-4** the name-exclusion suffix lacks a separator boundary (`SECURITY_PROFILE=` is excluded by accident): require the ending to follow `_` or `-`. Tests: `SECRET_PROFILE=abcdefgh1234` must be reported; `SECRET_FILE=abcdefgh1234` must not.
- **SEV-5** pin and document the known false positives: type annotations like `password: Optional[str] = None`, `MAX_TOKENS=100000000` and `args.password`. Do NOT add an all-digits rule and do NOT add a `tokens` exclusion (`API_TOKENS=<a>,<b>` is a plausible real secret list).
- **SEV-6** JWT fixtures (the jwt.io sample, an unsigned token) are flagged: document it.

**From the T609 code review:**

- **T609-10** with several matches on one line only the last is anchored; text between two shape matches that no rule matches and line continuation (YAML plain scalar, trailing backslash) are not judged. Add the limits to contract v3 §5 and the module docstring; optionally label only single-match lines (if you do, say so in the contract and keep the tests).
- **T609-11** align the `scan_secrets` tool description with the contract (both label rules, the end-of-line condition, the same-shape requirement); replace the `assert` in `_anchored` with an explicit check that raises or fails closed (it disappears under `python -O`); validate `value_shape` and `template_shape` against the fixed sets in `add_hit`.
- **T609-12** state in contract §5 that a missing label may mean the anchored check degraded, and that the scan assumes a quiescent tree.
- **T609-13** correct the wording "a URL whose scheme is 32 or more characters long": it is not a blind spot (the pattern is unanchored on the left, so a longer scheme still matches its last 32 characters); only an upper-case scheme is. Fix it in the contract, the docstring and the agent blind-spot bullet (`implementation/knowledge/agents/poc-security-engineer.md`; this projects, so declare the root drift).

If a rule regex changes (SEV-1, SEV-4), bump `RULES_VERSION` (currently `2026-10-09.4`) and update its pin. Contract changes go into a NEW immutable artifact `docs/artifacts/poc-security-engineer-tool-scoping-v4.md` (a delta on v3; do not edit v3).

## 2. Constraints

- **Read access:** the whole repo, except `tests/golden/held-out/`, `.env*`, and any credential or key file. Never open `tests/golden/held-out/`; never write a golden case name unless that case has a `tests/golden/open/` directory. Run `python3 -m unittest tests.functional.test_golden_held_out_isolation` before committing.
- Work in your own worktree/branch; one Conventional Commit ending with `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`. Do not push; do not merge; do not edit `.claude/` (outside the generated `implementation/.claude` mirror), `.github/` or other derived top-level folders, `docs/tasks/active-tasks.md`, `completed-tasks.md`, or any brief's Status line.
- Regenerate with `node implementation/scripts/sync.mjs --root implementation` and `python3 implementation/scripts/generate-registry.py`. Declare any root drift in `tests/_baselines/root-install-drift.json` (the baseline is empty now; sorted paths plus one comment line "Declared 2026-10-09 by T611 (...)"). Do NOT refresh the root install.
- Gates to report: `sync.mjs --check`, `generate-registry.py --check`, `check-maturity.py --root implementation`, `scorecard.py --check` (34/26/0), `validate-tasks.py`, the evaluator hash via `implementation/runtime/golden_harness/evaluator_hash.py` (baseline v20 unchanged), the held-out isolation test, and the full suite `python3 tests/run.py` redirected to a file.

## 3. Outputs

Scanner and server changes, tests for each item, contract v4 (new artifact), the agent blind-spot wording fix with regenerated mirrors and registry, a report with the gate results, suite summary line, drift paths and every deviation.

## 4. Acceptance criteria

1. Every item above is fixed, documented or explicitly deferred with a reason; none weakens a rule, label condition or fail-closed path.
2. New tests: the SEV-1 timing test, SEV-2 deadline test, SEV-3 control-character test, SEV-4 pair, SEV-5 pins, T609-11 value validation and the `assert` replacement; existing tests stay green except legitimate pin updates (`RULES_VERSION`).
3. All gates and the full suite pass; no root refresh.
4. A Security Engineer code-reviews the change before merge (the orchestrator dispatches it).

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
