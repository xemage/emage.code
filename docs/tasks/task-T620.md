# T620 — Bound the aperiodic-input cost of the JWT rule (R-1)

**ID:** T620
**Owner:** backend-developer
**Status:** pending
**Priority:** P1
**Tier:** standard
**Depends on:** —
**Affects:** —
**Created:** 2026-10-09
**Completed:** —
**Based on:**
- `docs/plans/plan-120-release-v8-readiness.md`
- `docs/artifacts/security-review-t611-scanner-residuals-v1.md` (R-1) and `docs/artifacts/poc-security-engineer-tool-scoping-v4.md` / `-v5.md` (contract; v1-v5 immutable)
- `implementation/runtime/security/poc_scan.py`, `poc_audit_server.py`, `tests/functional/test_poc_audit_server.py`
- The user's decisions of 2026-10-09 on the release-readiness question (verbatim): "1. A  2. A  3. A  4. approving baseline v21 - plan re-evaluation and steps to bring them out of experimental  5. C  6 B" (point numbers refer to the orchestrator's message listing six open points: 1 breaking changes and migration notes = release-level audit and Migration section; 2 release-level gates and sign-offs = the full sequence; 3 CI release job's third release-notes.md = fix first; 4 maturity = the user authorizes evaluator baseline v21 and asks for a re-evaluation plan and the steps to bring `orchestrator` and `tech-lead` out of `experimental`; 5 known residuals = fix all first; 6 plumbing = API fallback plan for branch and tag steps).

## 1. What and why

R-1: with `eyJ` repeated inside the 512-character JWT header window, up to about 170 match starts share one dot and one dot-free payload; the cost is a multiplier of up to ~170 on the line length (not quadratic), measured only on periodic input. It fails closed at the 60 s deadline. Measure first: build aperiodic adversarial lines (random-ish `eyJ` placement, mixed with base64url characters and dots, lengths 100 KB to 2 MB, single line and many lines), report timings before and after. If any plausible line exceeds ~10 s, bound the work (for example limit the number of starts per payload or restructure the pattern) without creating a false negative beyond a documented blind spot, and without weakening any rule, label condition or fail-closed path. If all timings are acceptable, record the measurements in a new contract delta and add a regression timing test instead of changing the rule. Contract changes go into a NEW immutable artifact `docs/artifacts/poc-security-engineer-tool-scoping-v6.md` (a delta on v5); bump `RULES_VERSION` (currently `2026-10-09.5`) only if a pattern changes. Keep F-8, E1-b, E1-c and both tool lists byte-identical; no matched text in any result or log.

## 2. Output

Tests (timing regression with a generous margin, not flaky), the optional pattern change, contract v6, regenerated mirrors only if an agent text changed (it should not), and a report with the before/after timings, the gate results and the suite summary line.

## 3. Constraints

- **Read access:** the whole repo, except `tests/golden/held-out/`, `.env*`, and any credential or key file. Never open `tests/golden/held-out/`; never write a golden case name unless that case has a `tests/golden/open/` directory.
- Work in your own worktree/branch; one Conventional Commit ending with `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`. Do not push; do not merge; do not edit `.claude/` (outside the generated `implementation/.claude` mirror), `.github/` or other derived top-level folders, `docs/tasks/active-tasks.md`, `completed-tasks.md`, or any brief's Status line. No `.env*` or credential files.
- Regenerate with `node implementation/scripts/sync.mjs --root implementation` and `python3 implementation/scripts/generate-registry.py` when a projected file changes; declare any root drift in `tests/_baselines/root-install-drift.json` (sorted paths plus one comment line); do NOT refresh the root install.
- Gates to report: `sync.mjs --check`, `generate-registry.py --check`, `check-maturity.py --root implementation`, `scorecard.py --check` (34/26/0), `validate-tasks.py`, the evaluator hash via `implementation/runtime/golden_harness/evaluator_hash.py` (baseline v20 unchanged), the held-out isolation test, and the full suite `python3 tests/run.py` redirected to a file.
- Quote verbatim, mark omissions with "…", and mark anything you did not re-read **(unverified)**.

## 4. Acceptance criteria

1. Timings for the aperiodic cases are recorded; the worst plausible case completes within a fixed bound or is documented as a fail-closed blind spot.
2. No rule, label condition or fail-closed path is weakened; all tests and gates pass.
3. A Security Engineer code-reviews the change before merge (the orchestrator dispatches it).

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
