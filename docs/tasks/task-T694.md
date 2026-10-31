# T694 — CWSO JWT secret out of emage.code

**ID:** T694
**Owner:** devops-engineer
**Status:** pending
**Priority:** P1
**Tier:** standard
**Depends on:** —
**Affects:** —
**Created:** 2026-10-31
**Completed:** —
**Based on:**
- `docs/plans/plan-123-post-release-follow-ups.md` (Addendum of 2026-10-31: T694)
- The user's decision of 2026-10-31: "T694 go"
- Immutable Security Constraint 1 (no secrets in source control); `implementation/SECURITY.md`

## 1. What and why

A scan of the user's files on 2026-10-30 found the CWSO JWT secret committed in this public repository, in `implementation/scripts/test-jwt-registration.py` and `docs/tasks/task-T344.md`. The secret was rotated on 2026-10-31: the committed copies hold a dead value, and the git history keeps it (no history rewrite).

1. **Secret source.** These scripts read the secret from a file by default (`../CWSO/.env.jwt.dev`, or `/home/emage/Code/emage/CWSO/.env.jwt.dev`): `scripts/mint-cwso-jwt.py`, `scripts/cwso-deploy-helper.sh`, `implementation/scripts/sia-executor.py`, `implementation/scripts/test-phase3.1.py`, and `scripts/deploy/cwso-docker-desktop.sh` / `scripts/deploy/cwso-proxmox-setup.sh` where they read the secret. Make them take it from the environment variable `CWSO_JWT_SECRET` only, with no file fallback. An explicit `--secret-file` option may stay if it is explicit, never a default. When the variable is missing, fail with a clear message that names the variable and never prints a value.
2. **Remove the dead value** from `implementation/scripts/test-jwt-registration.py` (read `CWSO_JWT_SECRET`) and from `docs/tasks/task-T344.md` (replace it with `<redacted 2026-10-31, rotated>`). Search every tracked file for the dead value without printing it. Take the value from the file at HEAD (`git show HEAD:implementation/scripts/test-jwt-registration.py`), keep it only in a pattern file under `/dev/shm` (mode 600), use `git grep -lF -f`, and delete the pattern file afterwards. Report file names only.
3. **Tests:** update or add the functional tests for the changed scripts. One test asserts that no script under `scripts/` or `implementation/scripts/` names `.env.jwt.dev` as a default.

## 2. Output

As stated in section 1.

## 3. Constraints

- Work in your own worktree/branch; one Conventional Commit ending with `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`. Do not push; do not merge; never create, push or delete a tag or release; never use or print `WIKI_TOKEN`; do not edit `docs/tasks/active-tasks.md`, `completed-tasks.md` or any brief's Status line. Agents without a shell (solution-architect, technical-writer) write their artifact text for the orchestrator to commit.
- Gates for any change under `implementation/`, `scripts/` or `tests/`: `node implementation/scripts/sync.mjs --root implementation --check`, `python3 implementation/scripts/generate-registry.py --check`, `python3 implementation/scripts/check-maturity.py --root implementation`, `python3 scripts/scorecard.py --check`, `python3 docs/tasks/validate-tasks.py`, the evaluator hash (`check_evaluator_hash()`, no drift unless the brief says otherwise), `python3 -m unittest tests.functional.test_golden_held_out_isolation`, and the full suite `python3 tests/run.py > file` (summary lines). Declare root drift in `tests/_baselines/root-install-drift.json` (sorted `python3 -m tests.functional.test_root_install_parity --print-drift` paths plus one comment line starting `Declared <date> by <task> (`); do NOT refresh the root install.
- Never open `tests/golden/held-out/`; never write a held-out case id anywhere; only T668 may modify `tests/golden/**` (grant G-2). No `.env*` or credential files (the primary checkout has an untracked local `.env` that must not be read or grepped); do not read the user's local `.claude/settings*.json` or `.vscode/mcp.json`. Mark anything you did not verify **(unverified)**.
- **Never print, log or commit a secret value, dead or live.** Never read `/dev/shm/emage-secrets/`, `~/.config/secrets/` or any `.env*` file. The only permitted access to the dead value is the pattern-file procedure of section 1.2.

## 4. Acceptance criteria

- The dead value occurs in no tracked file; the orchestrator verifies this independently.
- No script falls back to a secret file.
- All gates and the full suite pass.
- A Security Engineer review follows.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
