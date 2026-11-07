# T714 — Batch C: token docs and security runtime LOW items

**ID:** T714
**Owner:** devops-engineer
**Status:** done
**Priority:** P1
**Tier:** standard
**Depends on:** —
**Affects:** —
**Created:** 2026-11-01
**Completed:** 2026-11-01
**Based on:**
- `docs/plans/plan-125-post-v9-follow-ups.md` (task T714)
- The user's answer of 2026-11-01, verbatim: "v4 + C go"
- `docs/checkpoints/checkpoint-040-release-v9.0.0.md`; `docs/artifacts/tracked-debt-register-v3.md`

## 1. What and why

(devops-engineer): batch C. SEC-T701-01 (hibernation note at `implementation/PREREQUISITES.md:155-156`), SEC-T701-02 (where an environment-mode `.env` may live: outside every project directory, never committed, or drop `.env`), SEC-T701-03 (the gpg/keyring variant shows the full chain with `rm -f --`), SEC-T689-04 (`scripts/check-gitlab-token.py` must not end "ok" when the storage check could not run), SEC-T689-05 (path resolution vs the open descriptor; mount-namespace note), SEV-T690-02 (a trust-boundary paragraph in `implementation/SECURITY.md`), SEV-T690-04 (`implementation/runtime/security/executor.py`: an allowlisted child environment, `root_is_too_broad` for `allowed_root`, the missing credential-file names). *Acceptance:* every item fixed or reported with a reason; tests for the code changes; all gates and the suite pass; a Security Engineer review follows.

## 2. Output

As stated in section 1.

## 3. Constraints

- Work in your own worktree on branch `agent/<your-role>/<ID>`; Conventional Commits ending with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. Do not push; do not merge; never create, push or delete a tag or release; do not edit `docs/tasks/active-tasks.md`, `completed-tasks.md` or any brief's Status line.
- Gates for any change under `implementation/`, `scripts/` or `tests/`: `node implementation/scripts/sync.mjs --root implementation --check`, `python3 implementation/scripts/generate-registry.py --check`, `python3 implementation/scripts/check-maturity.py --root implementation`, `python3 scripts/scorecard.py --check`, `python3 docs/tasks/validate-tasks.py`, the evaluator hash (no drift), `python3 -m unittest tests.functional.test_golden_held_out_isolation`, and the full suite `python3 tests/run.py > file` (summary lines). Declare root drift in `tests/_baselines/root-install-drift.json`; do NOT refresh the root install.
- Never open `tests/golden/held-out/`; never write a held-out case id. Never read `/dev/shm/emage-secrets/`, `~/.config/secrets/`, any `.env*` or credential file, or the user's local `.claude/settings*.json` and `.vscode/mcp.json`; never print a secret value. Mark anything you did not verify **(unverified)**.

## 4. Acceptance criteria

As stated in section 1.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
