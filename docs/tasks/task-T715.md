# T715 — Batch B: release-docs gate and repository guards

**ID:** T715
**Owner:** devops-engineer
**Status:** done
**Priority:** P1
**Tier:** standard
**Depends on:** —
**Affects:** —
**Created:** 2026-11-01
**Completed:** 2026-11-01
**Based on:**
- `docs/plans/plan-126-batch-b-release-tooling.md` (task T715)
- The user's answer of 2026-11-01, verbatim: "B go"
- `docs/checkpoints/checkpoint-040-release-v9.0.0.md`; `docs/artifacts/tracked-debt-register-v4.md` (batch B rows)

## 1. What and why

(devops-engineer): the release-docs gate and the repository guards.
   - SEC-T703-01: `scripts/verify-release-docs.py:129-131,341-347`; the anchor check tests presence, not content, so an anchor inside a code fence or an HTML comment passes. Check the anchor outside fences and comments.
   - SEC-T703-02: `verify-release-docs.py:127,314-321`; a migration pointer in another form passes vacuously. Fail on a pointer-like line the pattern does not parse.
   - SEC-T703-03: `verify-release-docs.py:333-338,357-358`; a pointer to a newer version than the current one is skipped silently. Report it.
   - SEC-T677-02: no test pins the `check_section_requirements` call in `verify-release-docs.py` `main`, and none pins that the `SWAP_*` variables in the `install.sh` swap helper are set before the first rename. Add both tests.
   - SEC-T677-01: `tests/functional/test_function_size.py` misses some function shapes (Bash `function name {` and a brace on the next line; JS arrows, methods, nested functions; a column-0 `}` inside a heredoc; redefined Python names). Close what a line-based guard can close; report the rest with a reason.
   - TL-T708-04: `tests/functional/test_verify_release_docs.py:194-203` became weaker with the version bump. Make it independent of the current version.
   - TL-T708-05: `test_verify_release_docs.py:256-260` is always skipped. Make it run, or remove it and say why.
   - TL-T708-07: `scripts/check-version-consistency.py:68-82`; the exclusion is wider than its rationale (Proposed ADRs). Narrow it, or record why not (the reviewer found it acceptable as is).
   - SEC-T685-03, code part: the `verify-release-docs.py:15-17` docstring still says the main duty is enforced "within its grace window". Correct it.
   - *Acceptance:* each item is fixed with a test, or reported with a reason. A deliberately broken fixture shows each new check failing. All gates and the suite pass.

## 2. Output

The changes stated in section 1, on your own branch, and a closing report: per id, fixed (with the test or check that shows it) or not fixed (with the reason).

## 3. Constraints

- Work in your own worktree on branch `agent/<your-role>/<ID>`; Conventional Commits ending with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. Do not push; do not merge; never create, push or delete a tag or release; do not edit `docs/tasks/active-tasks.md`, `completed-tasks.md` or any brief's Status line.
- Gates for any change under `implementation/`, `scripts/` or `tests/`: `node implementation/scripts/sync.mjs --root implementation --check`, `python3 implementation/scripts/generate-registry.py --check`, `python3 implementation/scripts/check-maturity.py --root implementation`, `python3 scripts/scorecard.py --check`, `python3 docs/tasks/validate-tasks.py`, the evaluator hash (no drift), `python3 -m unittest tests.functional.test_golden_held_out_isolation`, and the full suite `python3 tests/run.py > file` (summary lines). Declare root drift in `tests/_baselines/root-install-drift.json`; do NOT refresh the root install.
- Never open `tests/golden/held-out/`; never write a held-out case id. Never read `/dev/shm/emage-secrets/`, `~/.config/secrets/`, any `.env*` or credential file, or the user's local `.claude/settings*.json` and `.vscode/mcp.json`; never print a secret value. Mark anything you did not verify **(unverified)**.

## 4. Acceptance criteria

Each item is fixed with a test, or reported with a reason. A deliberately broken fixture shows each new check failing. All gates and the suite pass.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
