# Artifact: security-review-t689-token-placement-v1.md

> Immutable once produced; revisions bump `<N>`.

## Metadata

- **Reviewer**: security-engineer, read-only (no shell: no test, mutation, generator or `git show`; content search could not reach the worktree, so files were read directly; GitLab's access token scopes page fetched on 2026-10-31). Recorded by the orchestrator from the reviewer's report.
- **Gate**: security. **Date**: 2026-10-31.
- **Target**: T689, worktree `agent-devops-engineer-T689`, commit `29107505` (parent develop `35ed12f9`).
- **Based on**: `docs/tasks/task-T689.md` (objective; section 6 via the brief's summary); `docs/artifacts/security-review-t665-token-handling-v1.md` (SEC-T665-03); `docs/artifacts/security-review-t665-token-handling-v2.md`; `docs/artifacts/tracked-debt-register-v2.md` (D-3, SEC-T665-03).
- **Files read**: `scripts/check-gitlab-token.py` (all); `implementation/PREREQUISITES.md` 120-229; `AGENTS.md`:116 and `implementation/AGENTS.md`:116; `docs/wiki/mcp-servers.md` 40-71; `docs/wiki/quick-start.md` 78-102; `docs/wiki/cline-setup.md` 104-125; `implementation/SECURITY.md` 24-31; `docs/artifacts/security-review-t665-token-handling-v2.md`; `tests/functional/test_check_gitlab_token.py` (docstring).

## Verdict: PASS (0 critical, 0 high, 0 medium, 6 LOW)

No Immutable Security Constraint is breached, and no required control is removed or weakened.

- **Default placement**: every reviewed live document gives an in-memory default (PREREQUISITES "File mode" 139-159; quick-start 92, 98; mcp-servers 43, 67; SECURITY.md:28; both AGENTS.md:116). `$HOME/.config/gitlab-mcp/token` survives only as the persistent-disk option, acceptable on an encrypted disk only (PREREQUISITES:158).
- **Environment-mode caveat** (an export in a shell profile is plaintext at rest): PREREQUISITES:160, :186; mcp-servers:44, :67; quick-start:98; both AGENTS.md:116. Missing in Migration step 2 (SEC-T689-03).
- **The checker** (`scripts/check-gitlab-token.py`:177-239, 263-292): file-system lookup by the `fstat` device of the opened descriptor, path fallback only when that fails; messages name the variable, never the path; the file-system type is printed only after matching `FS_TYPE_RE`, otherwise `unrecognised` (treated as persistent); the mount table is size-capped, decoded with `errors="replace"`, `\NNN` escapes decoded; any `OSError`/`ValueError` gives "not determined" (fail soft); the token cannot reach the new output.
- **The creation snippet** (PREREQUISITES:146-148): refuses a symbolic link and a directory owned by someone else, runs under `umask 077`, `chmod 700`/`600` before the token is written with the `printf` builtin (not in argv). Under the sticky `/dev/shm`, no other user can replace a directory the victim owns or create entries in a 0700 directory, so a freshly created directory is race-free; residual: a pre-existing directory once writable by others (SEC-T689-01).
- **Stated limits** are accurate (tmpfs swap unless swap is encrypted; `$XDG_RUNTIME_DIR` removed when the last session ends without lingering; `/dev/shm` cleared at reboot; logout removal depends on `RemoveIPC`, labelled unverified in PREREQUISITES). The wiki and the v2 record drop that label (SEC-T689-02).
- `security-review-t665-token-handling-v2.md` claims no gate verdict (its lines 7 and 41 say "closed" is the change's claim).

## SEC-T665-03 disposition

**Closed by T689**: the documented default placement is in memory, not at rest, and the checker warns (exit 1) about a token file on a persistent file system. The closure no longer rests on the full-disk-encryption assumption the user rejected on 2026-10-24 (D-3). The user's own setup since 2026-10-31 complies (a 0600 file in a 0700 directory under `/dev/shm`, filled from a gpg store; PREREQUISITES:157).

Residuals (accepted or documented; none new): (1) same-user read access (SEC-T660-01, SEC-T665-01, re-accepted); (2) tmpfs swap and hibernation images unless swap is encrypted; (3) environment mode stays supported with the at-rest caveat (the user's decision; on an unencrypted disk the user's own accepted Constraint-6 exposure); (4) the at-rest check is skipped where no mount table can be read, e.g. macOS (SEC-T689-04); (5) `glab`'s own stored login (`~/.config/glab-cli/config.yml`, OAuth and refresh token) is a second credential at rest; documented (PREREQUISITES:187, mcp-servers:71). **Orchestrator note**: on the user's devcontainer this copy was already removed on 2026-10-30 (the stored values emptied, the OAuth authorization revoked; `glab` uses `GITLAB_TOKEN` from the environment). Recommendation: carry it as a user action for other installs in `tracked-debt-register-v3.md`.

## Findings

| Id | Grade | Location | Finding | Recommendation / disposition |
|---|---|---|---|---|
| SEC-T689-01 | LOW | `implementation/PREREQUISITES.md`:147 | `: > "$d/token"` and `chmod 600 "$d/token"` follow an existing symbolic link at `$d/token`. Relevant only if `$d` existed before and was once writable by another user, who could plant `token` as a link to a missing path; the token would land there as a victim-owned 0600 file, at rest and outside the intended place. The step-6 checker refuses the link (`O_NOFOLLOW`), but only after the write. A fresh directory under `umask 077` has no race. | Tracked debt: `rm -f -- "$d/token" &&` before `: >`, or require `[ ! -e "$d/token" ] \|\| { [ ! -L "$d/token" ] && [ -O "$d/token" ]; }`; optionally check `stat -c %a "$d"` = 700. |
| SEC-T689-02 | LOW | `docs/wiki/mcp-servers.md`:67; `docs/artifacts/security-review-t665-token-handling-v2.md`:23 | Both say the file "disappears at logout or reboot" for both directories; for `/dev/shm` logout removal depends on `RemoveIPC=yes` (unverified, PREREQUISITES:156), for `$XDG_RUNTIME_DIR` only when the last session ends without lingering (PREREQUISITES:155). Hibernation images are not named. | Tracked debt: add the qualifiers to the wiki; say "swap and hibernation images" wherever tmpfs swap is mentioned; correct v2 in a later version. |
| SEC-T689-03 | LOW | `implementation/PREREQUISITES.md`:213; `AGENTS.md`:116; `implementation/AGENTS.md`:116 | Migration step 2 ("Nothing breaks if you do nothing: the exported `GITLAB_PERSONAL_ACCESS_TOKEN` keeps working") omits the at-rest caveat. Both AGENTS.md copies still say "the setup instructions export `GITLAB_PERSONAL_ACCESS_TOKEN` into the environment that starts the assistant" (pre-existing, in the line T689 edited), which contradicts the file-mode default. | Tracked debt: add the caveat to step 2; rephrase the AGENTS sentence (one line kept; update `test_mcp_grant_pins.py` if it pins the old text). |
| SEC-T689-04 | LOW | `scripts/check-gitlab-token.py`:233-235, 486-490 | When no mount table can be read or nothing matches, the run ends `result: ok (…)` with exit 0; the skipped storage check appears only on an earlier info line, so a token file under `$HOME` on macOS without FileVault gets a clean result. Fail soft is what the brief asked for. | Tracked debt: add "storage not determined" to the result qualifier; optional `--strict-storage`; a pinning test. |
| SEC-T689-05 | LOW (informational) | `scripts/check-gitlab-token.py`:206-213, 222 | The path fallback resolves `os.path.realpath(path)` separately from the open descriptor (TOCTOU) and follows parent-directory links; only a same-user process (which can already read the token) can exploit it, so it weakens the advice only. The check reads the checker's own mount namespace, which can differ from the MCP server's (devcontainer). | Tracked debt: say at PREREQUISITES:163 that the result describes the file system as the checker sees it; optionally compare `os.stat(path).st_dev` with the descriptor's and report "not determined" on a mismatch. |
| SEC-T689-06 | LOW (informational) | `implementation/PREREQUISITES.md`:129 | The Git-over-HTTP sentence is attributed only to the user's report ("not re-read for T689"). The orchestrator read GitLab's scopes page on 2026-10-30 and the reviewer on 2026-10-31 (`docs.gitlab.com/security/tokens/access_token_scopes/`): for a personal access token, `api` "also grants complete read and write access to the registry and repository through Git-over-HTTP"; the footnote applies to personal tokens only, not to group or project access tokens (detail from the fetch summary, unverified verbatim). | Tracked debt: record the reading and the URL, state that the clause is for personal access tokens; keep group/project tokens unverified until checked. |

## Recommendations

1. The orchestrator issues `tracked-debt-register-v3.md`: D-3 rejected, SEC-T665-03 closed by T689, SEC-T689-01 to -06 as LOW debt, the `glab` stored-login copy as a user action for other installs.
2. SEC-T689-01 and SEC-T689-03 first (small edits in documents users copy from).
3. Run the full suite and the `StorageTests` mutation proofs on the merged tree before merging (the orchestrator's run is recorded in `docs/tasks/task-T689.md`).

## Unverified

- That the worktree state is commit `29107505`; changes outside the files read were not reviewed.
- The three test modules beyond the docstring; no test or mutation run by the reviewer.
- The `servers.yaml` comment change and `docs/tasks/task-T689.md` section 6 (facts from the brief).
- Whether systemd-logind `RemoveIPC=yes` removes a directory under `/dev/shm` at logout.
- The checker on real btrfs, overlay and container mount tables (fake mount tables only).
- Whether `api` on group or project access tokens grants Git over HTTP.
- That `fs.protected_symlinks` gives SEC-T689-01 no protection inside the user's 0700 directory (reasoned, not tested).

### OWASP Coverage
| Category | Reviewed | Findings |
|----------|----------|----------|
| A01 | Yes (ownership, mode) | 1 (01) |
| A02 | Yes (at rest, Constraint 6) | 3 (02, 03, 04) |
| A03 | Yes (mountinfo parsing, output cleaning) | 0 |
| A04 | Yes (fail-soft, TOCTOU) | 1 (05) |
| A05 | Yes | 0 |
| A06 | No (no dependency change) | 0 |
| A07 | Yes (token scope documentation) | 1 (06) |
| A08 | No (no CI or package change) | 0 |
| A09 | Yes (no path or token in output) | 0 |
| A10 | Yes (host pin and redirect refusal unchanged) | 0 |
