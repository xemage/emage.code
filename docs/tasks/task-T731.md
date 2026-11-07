# T731 — Batch G: release-docs gate

**ID:** T731
**Owner:** devops-engineer
**Status:** done
**Priority:** P1
**Tier:** standard
**Depends on:** —
**Affects:** —
**Created:** 2026-11-02
**Completed:** 2026-11-04
**Based on:**
- `docs/plans/plan-131-batch-g-release-tooling.md` (task T731)
- The user's answers of 2026-11-02, verbatim: "G go"; SEC-T677-01 "Add a JS parser"
- `docs/artifacts/tracked-debt-register-v5.md` (batch G); `docs/artifacts/security-review-t715-t716-batch-b-v1.md` § 3

## 1. What and why

(devops-engineer): the release-docs gate, `scripts/verify-release-docs.py`.
   - **SEC-T715-01** (lines 134, 357-366): pointer forms without the keywords still pass unchecked, for example `v9.0.0.md`, `release-notes`, `doc/releases`, `"$REL_DOC"` or a wiki URL. Widen `POINTER_LIKE_RE` to catch these forms, with a broken fixture for each.
   - **SEC-T715-02** (lines 352-353): a prose pointer on a line that names Cursor is checked only for existence. Check it for the Cursor item, or report it as unparsed. T723 reworded `install.sh:1300`; confirm that the current `install.sh` passes.
   - **SEC-T715-03** (lines 386-414): an anchor inside a raw HTML block still counts. Blank CommonMark HTML blocks as well, with a fixture.
   - **SEC-T715-04** (lines 427-430, and 221): the gate prints an `install.sh` line to the CI log without stripping control or bidi characters. Pass printed lines through an `UNSAFE_RE.sub("?", ...)` like the one in `check-release-tag-tree.py:48`, with a test.
   - *Acceptance:* each item is fixed with a test, and every new check fails on a broken fixture. `verify-release-docs.py --tag v9.0.0` still passes. All gates and the suite pass.

## 2. Output

The changes stated in section 1, on your own branch, and a closing report: per id, fixed (with the test that shows it) or not fixed (with the reason).

## 3. Constraints

- Work in your own worktree on branch `agent/<your-role>/<ID>`; Conventional Commits ending with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. Do not push; do not merge; never create, push or delete a tag or release; do not edit `docs/tasks/active-tasks.md`, `completed-tasks.md` or any brief's Status line.
- Gates for any change under `implementation/`, `scripts/` or `tests/`: `node implementation/scripts/sync.mjs --root implementation --check`, `python3 implementation/scripts/generate-registry.py --check`, `python3 implementation/scripts/check-maturity.py --root implementation`, `python3 scripts/scorecard.py --check`, `python3 docs/tasks/validate-tasks.py`, the evaluator hash (no drift), `python3 -m unittest tests.functional.test_golden_held_out_isolation`, and the full suite `python3 tests/run.py > file` (summary lines). Declare root drift in `tests/_baselines/root-install-drift.json`; do NOT refresh the root install.
- Never open `tests/golden/held-out/`; never write a held-out case id. Never read `/dev/shm/emage-secrets/`, `~/.config/secrets/`, any `.env*` or credential file, or the user's local `.claude/settings*.json` and `.vscode/mcp.json`; never print a secret value. Mark anything you did not verify **(unverified)**.

## 4. Acceptance criteria

Each item is fixed with a test, and every new check fails on a broken fixture. `verify-release-docs.py --tag v9.0.0` still passes. All gates and the suite pass.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
