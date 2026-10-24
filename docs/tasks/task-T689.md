# T689 — GitLab token placement: no full-disk-encryption assumption (SEC-T665-03, D-3)

**ID:** T689
**Owner:** devops-engineer
**Status:** pending
**Priority:** P2
**Tier:** standard
**Depends on:** T687
**Affects:** —
**Created:** 2026-10-24
**Completed:** —
**Based on:**
- `docs/plans/plan-123-post-release-follow-ups.md` (Addendum of 2026-10-24: T689)
- The user's decisions of 2026-10-24 (replies to the decision list of `docs/artifacts/tracked-debt-register-v2.md` section 5.2): "D-3 reject (disk encryption: no)"
- `docs/artifacts/tracked-debt-register-v2.md` (D-3, SEC-T665-03), `docs/artifacts/security-review-t665-token-handling-v1.md`, `implementation/PREREQUISITES.md` ("GitLab token", "File mode")

## 1. What and why

The user rejected the position that a plaintext token file at rest does not breach Immutable Security Constraint 6 ("No unencrypted sensitive data at rest"): the workstation has no full-disk encryption, and the documented file mode assumed it. Make the documented default placement one that is not at rest on disk: a file under `$XDG_RUNTIME_DIR` (tmpfs), or `/dev/shm` when `$XDG_RUNTIME_DIR` does not exist (state its limits: a world-traversable directory, tmpfs can be swapped unless swap is encrypted, the file disappears at logout or reboot), or a file filled from a keyring at login (with the same-user caveat); a file on a persistent disk is documented only as acceptable when the user has encrypted the disk, and the documents say that the harness no longer assumes it. Update `implementation/PREREQUISITES.md` ("File mode", the posture table, "What this does not protect"), the wiki bullet, `AGENTS.md` and `implementation/AGENTS.md` token sentences (each GitLab-grants paragraph stays one line), `implementation/SECURITY.md` if it cites file mode, and the pinned documentation tests (`tests/functional/test_gitlab_token_handling.py`, `test_gitlab_exposure_docs.py`, `test_mcp_grant_pins.py`: update the expectations, do not weaken them). `scripts/check-gitlab-token.py`: warn (exit 1, name only, no path content) when the token file is on a persistent file system rather than tmpfs/ramfs (detect via `/proc/self/mountinfo` or `/proc/mounts` and `os.stat`, fail soft where unavailable, e.g. non-Linux), with tests and mutation proofs; also document that an exported token variable defined in a shell profile file is a plaintext secret at rest too (the environment mode stays supported, with that caveat). SEC-T665-03 (MEDIUM) is closed by this change, not by the earlier assumption; record the user's rejection in the review artifact. **Start only after the user has reported the results of the live checks 1 to 3 of T665** (they may change the same sections: merge them in, do not overwrite them). Root drift: declare it, do not refresh the root install. *Acceptance:* the default placement is not at rest on disk in every live document; the checker warns on a persistent-disk token file; all gates and the suite pass; a Security Engineer review follows.

## 2. Output

As stated in section 1.

## 3. Constraints

- Work in your own worktree/branch; one Conventional Commit ending with `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`. Do not push; do not merge; never create, push or delete a tag or release; never use or print `WIKI_TOKEN`; do not edit `docs/tasks/active-tasks.md`, `completed-tasks.md` or any brief's Status line. Agents without a shell (solution-architect, technical-writer) write their artifact text for the orchestrator to commit.
- Gates for any change under `implementation/`, `scripts/` or `tests/`: `node implementation/scripts/sync.mjs --root implementation --check`, `python3 implementation/scripts/generate-registry.py --check`, `python3 implementation/scripts/check-maturity.py --root implementation`, `python3 scripts/scorecard.py --check`, `python3 docs/tasks/validate-tasks.py`, the evaluator hash (`check_evaluator_hash()`, no drift unless the brief says otherwise), `python3 -m unittest tests.functional.test_golden_held_out_isolation`, and the full suite `python3 tests/run.py > file` (summary lines). Declare root drift in `tests/_baselines/root-install-drift.json` (sorted `python3 -m tests.functional.test_root_install_parity --print-drift` paths plus one comment line starting `Declared <date> by <task> (`); do NOT refresh the root install.
- Never open `tests/golden/held-out/`; never write a held-out case id anywhere; only T668 may modify `tests/golden/**` (grant G-2). No `.env*` or credential files (the primary checkout has an untracked local `.env` that must not be read or grepped); do not read the user's local `.claude/settings*.json` or `.vscode/mcp.json`. Mark anything you did not verify **(unverified)**.

## 4. Acceptance criteria

As stated in section 1.

## 5. Blocker protocol


Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
