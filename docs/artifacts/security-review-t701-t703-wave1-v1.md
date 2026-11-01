# Artifact: security-review-t701-t703-wave1-v1.md

> Immutable once produced; revisions bump `<N>`.

## Metadata

- **Reviewer**: security-engineer. Read-only: no shell; the diffs were read from files the orchestrator exported (`git diff origin/develop..b49f61b5`). Recorded by the orchestrator from the reviewer's report.
- **Gate**: security. **Date**: 2026-11-01.
- **Target**: branch `chore/plan-124-wave-1` at `b49f61b5`: T701 (token-docs batch, `468501f0`) and T703 (release-gate check of the migration pointer, `22d2bfcc`, `7f3dbd51`).
- **Based on**: `docs/tasks/task-T701.md`, `task-T703.md`; `implementation/PREREQUISITES.md` (138-167), `scripts/verify-release-docs.py`, `docs/releases/_template.md`, `scripts/install.sh` and `.gitlab-ci.yml` (develop `b1e7d91e`, unchanged by the diff); `security-review-t689-token-placement-v1.md`, `security-review-t697-t699-debt-checkpoint-refresh-v1.md`, `tracked-debt-register-v3.md`, `security-review-t662-cursor-removal-v1.md`.

## Verdict: PASS (T701 PASS, T703 PASS)

0 critical, 0 high, 0 medium, 6 LOW (tracked as debt under the LOW policy of 2026-10-23; this artifact is the record).

- **T701.** The token-file snippet (`PREREQUISITES.md:146-148`) is safe against other local users: a foreign or symlinked `$d` fails `[ ! -L ]`/`[ -O ]`; after `chmod 700` no other user can create an entry; `rm -f --` removes a planted name without following it, a planted directory aborts the chain; `: >` under `umask 077` creates 0600 and the later `printf >` only truncates. No wording is weaker than before; "acceptable only on a disk that you have encrypted" is consistent with the TD-T697-08 ruling and Constraint 6.
- **T703.** The gate is fail-closed (missing `install.sh`, unparsable tag, missing document, missing `## Migration Guide`, read errors), collected paths cannot leave `docs/releases/` (`POINTER_RE` has no `/` in the filename class), the regexes are linear, a pre-release tag enforces its pointer, and the `release` job needs `release-docs-gate` on the same tag pattern (`.gitlab-ci.yml:197, 217, 233`). The SEC-T662-01 requirement that the gate checks the pointer target is met.

## Findings

| Id | Grade | Location | Finding | Recommendation | Status |
|---|---|---|---|---|---|
| SEC-T701-01 | LOW | `implementation/PREREQUISITES.md:155, 156`; `security-review-t665-token-handling-v2.md:23` | SEC-T689-02 only partly done: hibernation images not named at :155/:156; the immutable T665 v2 record ("disappears at logout or reboot") not corrected by a later version. | Add the hibernation note at :155/:156; issue a T665 v3 or erratum. | tracked-LOW; devops-engineer with technical-writer; next token-docs change |
| SEC-T701-02 | LOW | `PREREQUISITES.md:213`, `:160` | "a `.env` file that your shell reads" is called acceptable on an encrypted disk without saying where it may live; a project `.env` is exposed to commits (Constraint 1) and to the `filesystem` server. | Add "outside every project directory, never committed", or drop `.env` and point to file mode. | tracked-LOW; same |
| SEC-T701-03 | LOW (informational) | `PREREQUISITES.md:157` | The keyring/gpg variant does not restate the new `rm -f --` step; swapping the redirect in without it reopens the SEC-T689-01 symlink-follow. | Show the full chain with `rm -f -- "$d/token"` for this variant. | tracked-LOW; same |
| SEC-T703-01 | LOW | `scripts/verify-release-docs.py:129-131, 341-347` | The anchor checks presence, not content; an empty `### Cursor` heading or an anchor inside a `~~~` fence or an HTML comment passes. | Strip `~~~` fences and comments; optionally require `--force-prune-keys` and `v8.0.0` in the item. **Condition for v9.0.0:** the T705 review and T709 check the Cursor item's content by hand before SEC-T662-01 is closed. | tracked-LOW; devops-engineer; content check in T705/T709 |
| SEC-T703-02 | LOW | `scripts/verify-release-docs.py:127, 314-321` | Pointers are collected only in the literal `docs/releases/vX.Y.Z.md` form; another form makes the gate pass vacuously (only a tree-pinned unit test guards it). | Fail when an `install.sh` line names `docs/releases/` and `POINTER_RE` cannot parse it, or keep the pointer in one variable the gate reads. | tracked-LOW; devops-engineer; before the next release after v9.0.0 |
| SEC-T703-03 | LOW | `scripts/verify-release-docs.py:333-338, 357-358` | A pointer to a version newer than the verified tag is skipped silently; on a real tag pipeline that is always a defect (a dead pointer). | Fail or warn on a newer pointer for a release tag; keep the skip behind an explicit flag for develop tests. | tracked-LOW; same |

## Register status

| Id | Status |
|---|---|
| SEC-T689-01 | closed (residual SEC-T701-03) |
| SEC-T689-02 | partly closed (rest is SEC-T701-01) |
| SEC-T689-03 | closed (residual SEC-T701-02) |
| SEC-T689-06 | closed |
| SEC-T699-01 | closed |
| SEC-T662-01, second half (the gate checks the pointer target) | closed by T703; the first half (`docs/releases/v9.0.0.md` with the Cursor item) stays open (MEDIUM) until T705 and its content review |

## Unverified

- The snippet was not run; race-freedom relies on the sticky bit of `/dev/shm`; POSIX default ACLs on tmpfs not tested.
- `RemoveIPC=yes` behaviour; the GitLab scopes-page footnote (not re-fetched).
- Whether the CI `test` stage runs `tests/functional/test_verify_release_docs.py` on MRs and has PyYAML; whether the `release` job has `allow_failure`.
- Root drift and registry for the edited `implementation/` files (the orchestrator's gate run covers it).
