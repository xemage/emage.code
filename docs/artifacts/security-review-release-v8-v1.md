# Artifact: security-review-release-v8-v1.md

> Immutable once produced; revisions bump `<N>`.

## Metadata

- **Reviewer**: security-engineer (read-only; no execute tool; static review). Recorded by the orchestrator from the reviewer's report.
- **Task**: T633 (plan-121): release-level OWASP audit of the security-sensitive code that shipped since v7.0.1 and had no release-level review (release audit C-6).
- **Based on**: `docs/tasks/task-T633.md`, `docs/artifacts/release-v8-audit-v1.md` (C-6, §2.1), `docs/artifacts/poc-security-engineer-tool-scoping-v6.md`, `security-review-t611-scanner-residuals-v1.md`, `security-review-poc-security-audit-code-v2.md`.
- **Tree read**: develop `4c5b43e`. Date: 2026-10-14.
- **Scope**: `scripts/install.sh` (1091 lines), `merge-mcp-json.py`, `merge-task-docs.py`, `render_installed_agents.py`, `publish-release.py`, `dry-run-publish-release.py`, the `release` job in `.gitlab-ci.yml`, `implementation/runtime/security/{poc_scan,poc_audit_server,git_executor}.py`, the shipped `implementation/.mcp.json`, `.gemini/settings.json` and `.opencode/opencode.json` (heads), `requirements-mcp-server.txt`. **Not read**: `tests/**`, `scripts/sync-wiki.py`, `scripts/verify-release-docs.py`, `servers.yaml`, the other platform MCP projections.
- **Basis**: reading only (no shell); no `git diff v7.0.1..develop`; `grep_content` and `run_pip_audit` failed to run, so there is no automated A06 result.

## Verdict: CONDITIONAL_PASS

0 critical, 0 high, 3 medium, 12 low. No Immutable Security Constraint is breached; no secret is in any file read; no command injection or unsafe `eval` of external input was found in `install.sh`; the PoC scanner stack is consistent with its reviews and contract v6. Under `validation-gates` § Verdict Rules a medium security finding must be fixed before the release ships.

## Orchestrator verification and decisions (2026-10-14)

- **SEC-001: reproduced** on scratch directories: with `<target>/.claude` a symlink to an outside directory holding a canary file, `scripts/install.sh --target <target> --platform claude-code --update` deleted the canary in the outside directory and wrote the harness files there. The shipped `implementation/` tree contains no symlinks (`find implementation -type l`: 0). Decision (user, "Yes, fix before the release (Recommended)"): fix before the release (T636).
- **SEC-002: the four nonexistent package names pre-date v7.0.1**: `@anthropic/mcp-filesystem`, `@github/mcp-github`, `@modelcontextprotocol/mcp-git` and `@supabase/mcp` are all present in `v7.0.1:implementation/.mcp.json`; the only server added since v7.0.1 is `poc-security-audit` (a `python3` command). Decision (user, "Fix before the release (Recommended)"): verify the real package names and scope ownership first, then correct, pin and re-sync; the names and pins come back to the user before they are applied (T637 researches, a later task applies).
- **SEC-003: provisional on GitLab settings** the reviewer could not see. The user stated (AskUserQuestion, "I'll check; both are set (grade drops to LOW)") that `WIKI_TOKEN` is Protected and Masked and that the `v*` tag pattern is protected. The orchestrator has not verified these settings; the finding is therefore tracked as LOW (token in argv and a token named for the wiki job reused for releases) and stays as debt.

## Findings

| ID | Grade | OWASP | Concern | Location | Fix |
|---|---|---|---|---|---|
| SEC-001 | **MEDIUM** | A01/A05 | The installer follows symlinks at managed target paths; it writes, and under `--update` deletes, outside the target (rsync `-a`, `rsync --delete`, `cp -rn`, `cp`, and the Python `write_text` calls). | `install.sh` 556-567, 605-617, 698-700, 818, 860-863, 945-947, 1002; `merge-mcp-json.py` 150-153; `merge-task-docs.py` 138-149; `render_installed_agents.py` 173-174 | Refuse any managed path that is a symlink or resolves outside the physical target, before the first write, covering ancestors (`docs`, `implementation`, `implementation/runtime`, `.vscode`); in Python, check `is_symlink()` or open with `O_NOFOLLOW`. |
| SEC-002 | **MEDIUM** (provisional; LOW if all four npm scopes are vendor-owned, HIGH if an unclaimed scope can be registered) | A08/A06 | Shipped MCP configs launch unpinned `npx -y` packages; four of them (above) return 404 on the npm registry. Some of these servers receive tokens. | `implementation/.mcp.json` 17, 105, 112, 119, 126 and the same entries in the other projections | Correct or remove the four names in `servers.yaml`, pin exact versions for every npx entry, re-run both generators. |
| SEC-003 | MEDIUM provisional, now LOW per the user's statement | A02/A05/A07 | The release job passes the token in argv (`--token "${WIKI_TOKEN}"`), reuses a token named for the wiki job, and runs the tagged commit's script with it; the stdlib redirect handler re-sends custom headers; `api_v4_url` is not validated. | `.gitlab-ci.yml` 202; `publish-release.py` 236-288 | `CI_JOB_TOKEN` (if the Releases API accepts it) or a dedicated protected, masked token read from the environment; disable redirects or pin the host. |
| SEC-004 | LOW | A04 | The no-rsync `--update` fallback has no cleanup or rollback (user settings only in `/tmp` between `rm -rf` and restore). | `install.sh` 333-345, 500, 650-670 | A `trap`, or build in a sibling directory and swap. |
| SEC-005 | LOW | A05 | `rsync -a` copies source permission bits verbatim (runtime Python can land group/world writable). | `install.sh` 558, 607, 687 | `--chmod=go-w`. |
| SEC-006 | LOW | A08/A04 | Merge scripts write non-atomically; `merge-mcp-json.py` writes before it validates the sidecar; ledger rows are dropped with no backup. | `merge-mcp-json.py` 122-153; `merge-task-docs.py` 54-58, 139-145 | Parse first, write a temp file, `os.replace`; keep a `.bak` of ledgers. |
| SEC-007 | LOW | A08 | The MCP merge keeps dest-only keys inside generator-owned server objects (`env`, `headers`); gemini `hooks` arrays are replaced wholesale. | `merge-mcp-json.py` 31-42, 126-130 | Replace whole generator-owned server objects; warn on dest-only `env`/`headers` keys. |
| SEC-008 | LOW | A04 | A plain install overwrites existing MCP configs and `CLAUDE.md`; `--dry-run` has side effects (`mkdir -p`, temp backups); `--platform` is validated late. | `install.sh` 818, 650-656, 860-863, 1002, 1011-1033 | Merge or refuse; put every write behind `run`; validate `--platform` up front. |
| SEC-009 | LOW | A03 | Copy-paste hints print unquoted, unsanitised paths from the target tree (`find` over all of `runtime/`). | `install.sh` 1059-1072 | `printf '%q'`; search only the three shipped runtime directories. |
| SEC-010 | LOW (hygiene) | A03 | `eval "$saved_shopt"` (fixed builtin output; not exploitable). | `install.sh` 364-367, 412-415 | Explicit `shopt -q` save and restore, or a subshell. |
| SEC-011 | LOW | A03 | `re.match` with `$` accepts a trailing newline in the ref, range, commit and oid validators (fails closed in git). | `poc_scan.py` 335-338, 785, 820 | `fullmatch`. |
| SEC-012 | LOW (unmeasured) | A04 | Python-`re` credential rules run on attacker-controlled file and ref names with no time bound. | `poc_scan.py` 380-389, 246-247 | Cap the raw name before matching; add a timing test. |
| SEC-013 | LOW | A05 | Undocumented scanner limits: submodules are not scanned; `--allowed-root .` depends on the client's launch directory. | `poc_scan.py` 554-566; `poc_audit_server.py` 83-93; `.mcp.json` 97-99 | Document both; prefer an absolute `--allowed-root`. |
| SEC-014 | LOW | A08 | No hash pinning of `mcp==2.2.0`; no integrity check of the installer source; `python3 -m implementation...` puts the project directory first on `sys.path`. | `requirements-mcp-server.txt` 23; `install.sh` 1071 | Document `--require-hashes` and `git tag -v`. |
| SEC-015 | LOW | A10/A09 | Release-script hygiene: unvalidated `api_v4_url` and `project_id`, un-sanitised commit subjects in release text, `re.subn` string replacement, `python3 -c` without `-I`, leading-dash `--target` unguarded. | `publish-release.py` 236-278, 130-165; `install.sh` 67; `render_installed_agents.py` 57-61 | See the report. |

## Conditions

| ID | Owner | Fix | Deadline |
|---|---|---|---|
| SEC-001 | backend-developer | Symlink and containment guard on all managed paths (shell and the three Python scripts) with tests for a symlinked `.claude`, `docs` and `.mcp.json`. | Before the v8.0.0 tag (task T636). |
| SEC-002 | devops-engineer | Verify the four npm scopes, correct or remove the four names, pin versions, `make sync` and the registry generator. | Before the v8.0.0 tag (task T637 researches; the application follows the user's approval of the names and pins). |
| SEC-003 | devops-engineer | Token via environment or `CI_JOB_TOKEN`; confirm the protected-tag pattern and variable flags (the user states both are set). | Debt; before the v8.0.0 tag if the flags turn out not to be set. |
| SEC-004..SEC-015 | per area | Track as technical debt. | Next sprint. |

## Verified as sound (reading only)

`install.sh` quoting and arrays (NUL-delimited `find -print0`, `read -d ''`, bash arrays, `set -u` idiom); the repository-root and inside-repository refusals use `-ef` (inode equality) and run before any write; the exclude mechanism (`check_exclude_names`); temp files via `mktemp` (0600/0700, no predictable names); no secrets in argv or logs in the installer or merge scripts; `merge-mcp-json.py` reads no environment variables and `merge-task-docs.py` regexes are linear; `git_executor.py` (`shell=False`, closed stdin, stderr to `/dev/null`, minimal environment, hardening prefix, bounded stdout, aggregate deadline, process-group kill guarded against pid reuse); scanner results never include matched text, stderr or argv, and `HIT_KEYS`, label validation and `path_altered` are enforced in `add_hit`; `resolve_root` resolves symlinks and defeats a hostile `core.worktree`; contract v6 matches the code (`RULES_VERSION` `2026-10-09.5`, the `jwt` pattern string).

## What the reviewer could not verify

Nothing was run. Reasoned from source or documented behaviour: GNU `cp -r` and rsync symlink semantics, bash behaviour on versions older than 4.4, BSD/busybox differences, the cp/rsync parity claims in `install.sh` comments. No diff since `v7.0.1` (so SEC-002's age was checked by the orchestrator, above). No test run. CI settings (flags, tag protection, token scope, whether the Releases API accepts `CI_JOB_TOKEN`). npm scope ownership for `@anthropic`. No automated dependency audit. Python-`re` timings on hostile names (SEC-012). Behaviour with a low `RE_DUP_MAX`, git older than 2.40, a SHA-256 repository or an unusual locale. Platform consumption of merged keys and approval of project-scoped servers. Files not read are listed under Scope.
