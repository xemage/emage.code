# T723 — Batch A: installer and merge-task-docs

**ID:** T723
**Owner:** devops-engineer
**Status:** done
**Priority:** P2
**Tier:** standard
**Depends on:** —
**Affects:** —
**Created:** 2026-11-02
**Completed:** 2026-11-02
**Based on:**
- `docs/plans/plan-128-batch-a-installer-generator.md` (task T723)
- The user's answer of 2026-11-02, verbatim: "A go"
- `docs/checkpoints/checkpoint-040-release-v9.0.0.md`; `docs/artifacts/tracked-debt-register-v4.md` (batch A rows; descriptions in v1 to v3)

## 1. What and why

(devops-engineer): the installer and `merge-task-docs.py`.
   - **SEC-T684-03**: `install.sh:279-281`, `printable`, depends on the locale; U+202E passes `[:print:]`. Fix: `printable() { ascii_printable "$1"; }`, with a test.
   - **SEC-T684-04**: `_atomic_write_bytes` in `merge-task-docs.py` does not `fsync` the temp file or the directory. Add both.
   - **SEC-T684-05**: in `merge-task-docs.py`, seeds published with `os.replace` can overwrite a file created between planning and writing, and `dest_dir.mkdir` runs before the dry-run guard. Use `os.link` or an exclusive create, and move the `mkdir` after the guard, with tests.
   - **SEC-T684-06**: tests. T04j is not strictly equivalent; there is no non-UTF-8 name test; bash 3.2 `%q` is unverified; one mode assertion cannot fail. Add the 41-link test and a non-UTF-8 name test, and use a ledger mode other than 0600.
   - **SEC-T677-03**: `install.sh` `usage` is allowlisted as "no logic" in the function-size guard but holds one command substitution. Remove the substitution, or correct the allowlist reason.
   - **TL-T708-03**: `install.sh:1300` puts two cases in one sentence, and a test pins it. Split the sentence and update the pin. T715 also checks this line for release-document pointers (SEC-T715-02), so keep a parsed `docs/releases/vX.Y.Z.md` path form, and run `verify-release-docs.py --tag v9.0.0`.
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
