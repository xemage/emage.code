# T732 — Batch G: JS parser for the function-size guard (SEC-T677-01)

**ID:** T732
**Owner:** devops-engineer
**Status:** done
**Priority:** P2
**Tier:** standard
**Depends on:** —
**Affects:** —
**Created:** 2026-11-02
**Completed:** 2026-11-04
**Based on:**
- `docs/plans/plan-131-batch-g-release-tooling.md` (task T732)
- The user's answers of 2026-11-02, verbatim: "G go"; SEC-T677-01 "Add a JS parser"
- `docs/artifacts/tracked-debt-register-v5.md` (batch G); `docs/artifacts/security-review-t715-t716-batch-b-v1.md` § 3

## 1. What and why

(devops-engineer), **SEC-T677-01**: the user's decision is "Add a JS parser". Make `tests/functional/test_function_size.py` measure JavaScript functions with a real parser instead of line heuristics. This closes the residual shapes listed in the guard's docstring: a `}` inside a multi-line template literal, methods with multi-line parameters, and anonymous callbacks.
   - Use a parser dependency such as `acorn`, pinned to an exact version at least two weeks old.
   - Add a lockfile with integrity hashes in a dedicated directory, for example `ci/js/package.json` and `package-lock.json`. Install with `npm ci --ignore-scripts` in the CI job that runs the suite.
   - When the parser is missing and `CI` is set, the test must fail rather than skip. Locally it may skip, but it must say so.
   - Also record the dependency and its update rule where the repo documents CI dependencies.
   - *Acceptance:*
     - the residual shapes are measured, with fixtures;
     - all real `.mjs` and `.js` files stay within 50 lines;
     - the lockfile carries integrity hashes;
     - CI installs the parser with `--ignore-scripts`;
     - all gates and the suite pass;
     - the CI lint is valid.

## 2. Output

The changes stated in section 1, on your own branch, and a closing report: per id, fixed (with the test that shows it) or not fixed (with the reason).

## 3. Constraints

- Work in your own worktree on branch `agent/<your-role>/<ID>`; Conventional Commits ending with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. Do not push; do not merge; never create, push or delete a tag or release; do not edit `docs/tasks/active-tasks.md`, `completed-tasks.md` or any brief's Status line.
- Gates for any change under `implementation/`, `scripts/` or `tests/`: `node implementation/scripts/sync.mjs --root implementation --check`, `python3 implementation/scripts/generate-registry.py --check`, `python3 implementation/scripts/check-maturity.py --root implementation`, `python3 scripts/scorecard.py --check`, `python3 docs/tasks/validate-tasks.py`, the evaluator hash (no drift), `python3 -m unittest tests.functional.test_golden_held_out_isolation`, and the full suite `python3 tests/run.py > file` (summary lines). Declare root drift in `tests/_baselines/root-install-drift.json`; do NOT refresh the root install.
- Never open `tests/golden/held-out/`; never write a held-out case id. Never read `/dev/shm/emage-secrets/`, `~/.config/secrets/`, any `.env*` or credential file, or the user's local `.claude/settings*.json` and `.vscode/mcp.json`; never print a secret value. Mark anything you did not verify **(unverified)**.

## 4. Acceptance criteria

- the residual shapes are measured, with fixtures;
     - all real `.mjs` and `.js` files stay within 50 lines;
     - the lockfile carries integrity hashes;
     - CI installs the parser with `--ignore-scripts`;
     - all gates and the suite pass;
     - the CI lint is valid.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
