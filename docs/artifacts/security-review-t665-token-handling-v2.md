# Artifact: security-review-t665-token-handling-v2.md

> Immutable once produced; revisions bump `<N>`. Continues `security-review-t665-token-handling-v1.md`, which stays unchanged.

## Metadata

- **Kind**: a record, not a new review. It records the user's rejection of the position on SEC-T665-03 that v1 left "for the user to confirm", and the change that closes the finding instead. It was written by devops-engineer at the instruction of the T689 brief (section 1: "record the user's rejection in the review artifact"); v1 is immutable, so the record is this new version. No Security Engineer has reviewed T689 yet; the review that the brief requires follows.
- **Task**: T689 (plan-123, addendum of 2026-10-24). **Date**: 2026-10-31.
- **Based on**: `docs/artifacts/security-review-t665-token-handling-v1.md` (SEC-T665-03); `docs/tasks/task-T689.md` (sections 1 and 6); `docs/plans/plan-123-post-release-follow-ups.md` (addendum of 2026-10-24, item 28); `docs/artifacts/tracked-debt-register-v2.md` (SEC-T665-03, decision D-3).

## What v1 said

SEC-T665-03 (MEDIUM, plaintext token file at rest, an Immutable Security Constraint 6 judgement) was marked "fixed; closed" because the documentation stated that full-disk encryption is assumed and offered `$XDG_RUNTIME_DIR` (tmpfs) and keyring-fed placements as better options. The orchestrator's position that Constraint 6 is not breached was "for the user to confirm", and it held only through the full-disk-encryption assumption.

## The user's decision

On 2026-10-24 the user answered the decision list of `tracked-debt-register-v2.md` section 5.2: "D-3 reject (disk encryption: no)". The workstation has no full-disk encryption, so the assumption does not hold and a plaintext token file on a persistent disk breaches Constraint 6 ("No unencrypted sensitive data at rest"). **The v1 closure of SEC-T665-03 is withdrawn**: the finding was open from that decision until the T689 change.

## How T689 closes SEC-T665-03 (pending the Security Engineer review)

| Item | Change |
|---|---|
| Default placement | `implementation/PREREQUISITES.md` "File mode": the documented default is a file in memory, under `$XDG_RUNTIME_DIR`, else `/dev/shm` (limits stated: a world-traversable directory, swap unless encrypted, the file disappears at logout or reboot), or filled there from a keyring or an encrypted store at login (same-user caveat). The creation snippet refuses a directory that is not the user's or is a symbolic link. A file on a persistent disk is documented as acceptable only on a disk the user has encrypted; the documents say that the harness no longer assumes disk encryption. |
| Environment mode | Stays supported; the documents state that an exported token in a shell profile file (or a `.env` file) is a plaintext secret at rest too. |
| Checker | `scripts/check-gitlab-token.py` warns (exit 1; the message names the variable, never the path) when the token file is on a file system other than `tmpfs` or `ramfs`, read from `/proc/self/mountinfo`; it fails soft (an information line, no warning) where no mount table can be read or none matches. Tests and mutation proofs: `tests/functional/test_check_gitlab_token.py`, class `StorageTests`. |
| Live documents | The wiki (`docs/wiki/mcp-servers.md`, `docs/wiki/quick-start.md`), `AGENTS.md` and `implementation/AGENTS.md` (the GitLab-grants paragraph, still one line), `implementation/SECURITY.md`; pinned by `tests/functional/test_gitlab_token_handling.py` and `tests/functional/test_mcp_grant_pins.py`. |

Residual, unchanged from v1 and still re-accepted (SEC-T660-01, SEC-T665-01): a same-user process can read a file in memory as well as one on disk, and tmpfs can be swapped unless swap is encrypted. The checker cannot see disk encryption, so on an encrypted disk its warning stays and is the user's to accept.

## Live-check results that bear on v1's "Open and unverified"

Recorded from `docs/tasks/task-T689.md` section 6 (the user's reports, 2026-10-24 to 2026-10-31); merged into `PREREQUISITES.md` by T689:

- Live check 1: the fine-grained personal access token is not usable for `qa-engineer` and `scrum-master` (no Create permission for Issue, Milestone or Issue link); the legacy `api` token stays the default.
- Live check 2: with `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB=1` the `gitlab` MCP server does not connect (cause unverified); the Bash-side parts of the check were not established.
- Live check 3: token-file mode works with the variable unset; the empty-variable case and the reverse direction were not reported (unverified).
- `glab` reads `GITLAB_TOKEN` from the environment ahead of its config file, and its own stored login is a second plaintext copy at rest (an OAuth token and a refresh token, not `glpat-` tokens).

## Not verified

- The Security Engineer review of T689 has not happened; "closed" above is the change's claim, not a gate verdict **(unverified)**.
- The checker's storage detection was run on one Linux host only (an ext4 `/tmp` and a tmpfs `$XDG_RUNTIME_DIR`); btrfs subvolumes, overlay and container mount tables are covered by fake mount tables in the tests, not by real hosts **(unverified)**.
- Whether systemd-logind's `RemoveIPC=yes` also removes a directory under `/dev/shm` at logout **(unverified)**.
- `tracked-debt-register-v2.md` still lists D-3 and SEC-T665-03 as they were; a later register version is the orchestrator's.
