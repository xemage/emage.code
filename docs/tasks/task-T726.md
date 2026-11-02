# T726 — Batch E: CWSO helper scripts in emage.code

**ID:** T726
**Owner:** devops-engineer
**Status:** done
**Priority:** P2
**Tier:** standard
**Depends on:** —
**Affects:** —
**Created:** 2026-11-02
**Completed:** 2026-11-02
**Based on:**
- `docs/plans/plan-129-batch-e-cwso-hardening.md` (task T726)
- The user's answer of 2026-11-02, verbatim: "E go"
- `docs/artifacts/tracked-debt-register-v4.md` (batch E rows) and v3; the T694 to T696 security reviews

## 1. What and why

(devops-engineer, emage.code): the CWSO helper scripts.
   - SEC-T694-04: `implementation/scripts/sia-executor.py` takes `--jwt-secret` on argv, and argparse's `allow_abbrev` echoes values. Read the secret from a file or the environment, remove the argv form or warn on it, and set `allow_abbrev=False`.
   - SEC-T694-05: error messages in `scripts/cwso-deploy-helper.sh` and `scripts/mint-cwso-jwt.py` can echo values or paths. Name variables only.
   - SEC-T694-06: `cwso-deploy-helper.sh export --secret-file` prints the secret to stdout by design. Require an explicit flag or a non-tty check, and document it.
   - SEC-T694-07: the helper and the minter parse the secret file differently. Use one rule.
   - SEC-T694-08: `scripts/deploy/cwso-proxmox-setup.sh` writes the raw value into the `.env` line that compose reads. Fix the quoting, and keep the value at rest with mode 600; document it.
   - SEC-T694-09: in `tests/functional/test_cwso_jwt_secret_source.py`, add the missing cases: `--secret=VALUE`, an unknown argument that echoes, and checks on literal text.
   - SEC-T694-11: `cwso-proxmox-setup.sh` and `cwso-deploy-helper.sh` download `get.docker.com` and `releases/latest` unpinned and without checksum, and use fixed `/tmp` paths. Pin a version, verify a checksum, and use `mktemp`. Any download that cannot be pinned is reported with a reason.
   - *Acceptance:* each item is fixed with a test or reported with a reason. No secret value appears in any test output. All gates and the suite pass.

## 2. Output

The changes stated in section 1, on your own branch, and a closing report: per id, fixed (with the test or check that shows it) or not fixed (with the reason).

## 3. Constraints

- Work in your own worktree on branch `agent/<your-role>/<ID>`; Conventional Commits ending with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. Do not push; do not merge; never create, push or delete a tag or release; do not edit `docs/tasks/active-tasks.md`, `completed-tasks.md` or any brief's Status line.
- Gates for any change under `implementation/`, `scripts/` or `tests/`: `node implementation/scripts/sync.mjs --root implementation --check`, `python3 implementation/scripts/generate-registry.py --check`, `python3 implementation/scripts/check-maturity.py --root implementation`, `python3 scripts/scorecard.py --check`, `python3 docs/tasks/validate-tasks.py`, the evaluator hash (no drift), `python3 -m unittest tests.functional.test_golden_held_out_isolation`, and the full suite `python3 tests/run.py > file` (summary lines). Declare root drift in `tests/_baselines/root-install-drift.json`; do NOT refresh the root install.
- Never open `tests/golden/held-out/`; never write a held-out case id. Never read `/dev/shm/emage-secrets/`, `~/.config/secrets/`, any `.env*` or credential file, or the user's local `.claude/settings*.json` and `.vscode/mcp.json`; never print a secret value. Mark anything you did not verify **(unverified)**.

## 4. Acceptance criteria

Each item is fixed with a test or reported with a reason. No secret value appears in any test output. All gates and the suite pass.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
