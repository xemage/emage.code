# T730 — Batch G: release script and drift check

**ID:** T730
**Owner:** devops-engineer
**Status:** done
**Priority:** P1
**Tier:** standard
**Depends on:** —
**Affects:** —
**Created:** 2026-11-02
**Completed:** 2026-11-04
**Based on:**
- `docs/plans/plan-131-batch-g-release-tooling.md` (task T730)
- The user's answers of 2026-11-02, verbatim: "G go"; SEC-T677-01 "Add a JS parser"
- `docs/artifacts/tracked-debt-register-v5.md` (batch G); `docs/artifacts/security-review-t715-t716-batch-b-v1.md` § 3

## 1. What and why

(devops-engineer): the release script and the drift check.
   - **SEC-T716-01 (do first):** `scripts/check-main-develop-drift.py:50-51, 146-147` resolves `origin/main` and `origin/develop` by short name, so a tag with that name shadows the branch. Resolve the refs with `git show-ref --verify --hash refs/remotes/<ref>`, as `check-release-tag-tree.py:71-86` does, then read files by object id. Add a test with a shadowing tag.
   - **SEC-T716-02:** in `scripts/publish-release.py:76-80, 326-328`, the category test depends on the Unicode database of the Python that runs it. Add the reserved Default_Ignorable ranges explicitly (U+2065, U+FFF0-FFF8, U+E0000-E0FFF and the others in the Unicode list). Add a test that asserts `unicodedata.unidata_version` for the release image.
   - **SEC-T716-03:** in `publish-release.py:417-446`, bare URLs and GitLab references (`@user`, `#123`, `!12`, `~label`, `%milestone`) in a commit subject render as links. Neutralise `://` and these sigils outside code spans, with tests. If neutralising breaks a legitimate changelog form, document the residual risk instead and give the reason.
   - **SEC-T716-04:** in `publish-release.py:532-539`, `ApiCredential` is a NamedTuple, so `tuple()`, `_asdict()`, `%`-formatting and pickling expose the token. Use a non-iterable type (a frozen dataclass with `field(repr=False)`, or a `__slots__` class). Add a test that none of these forms exposes the token.
   - **SEC-T716-05:** `tests/functional/test_publish_release_t716.py` skips its CommonMark rendering test without saying so when markdown-it-py is missing. Add markdown-it-py to `ci/requirements-ci.in`, regenerate `ci/requirements-ci.txt` with hashes, and make the test fail, not skip, when `CI` is set.
   - **SEC-T676-14:** handle it in the same lock regeneration. Set `--exclude-newer` to at least seven days before the generation day, so it works as a cooldown, and state that in the header comment.
   - *Acceptance:* each item is fixed with a test, or reported with a reason. All gates and the suite pass.

## 2. Output

The changes stated in section 1, on your own branch, and a closing report: per id, fixed (with the test that shows it) or not fixed (with the reason).

## 3. Constraints

- Work in your own worktree on branch `agent/<your-role>/<ID>`; Conventional Commits ending with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. Do not push; do not merge; never create, push or delete a tag or release; do not edit `docs/tasks/active-tasks.md`, `completed-tasks.md` or any brief's Status line.
- Gates for any change under `implementation/`, `scripts/` or `tests/`: `node implementation/scripts/sync.mjs --root implementation --check`, `python3 implementation/scripts/generate-registry.py --check`, `python3 implementation/scripts/check-maturity.py --root implementation`, `python3 scripts/scorecard.py --check`, `python3 docs/tasks/validate-tasks.py`, the evaluator hash (no drift), `python3 -m unittest tests.functional.test_golden_held_out_isolation`, and the full suite `python3 tests/run.py > file` (summary lines). Declare root drift in `tests/_baselines/root-install-drift.json`; do NOT refresh the root install.
- Never open `tests/golden/held-out/`; never write a held-out case id. Never read `/dev/shm/emage-secrets/`, `~/.config/secrets/`, any `.env*` or credential file, or the user's local `.claude/settings*.json` and `.vscode/mcp.json`; never print a secret value. Mark anything you did not verify **(unverified)**.

## 4. Acceptance criteria

Each item is fixed with a test, or reported with a reason. All gates and the suite pass.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
