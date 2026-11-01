# Artifact: security-review-t714-batch-c-v1.md

> Immutable once produced; revisions bump `<N>`.

## Metadata

- **Reviewer**: security-engineer. Read-only: no shell; the diffs were read from files the orchestrator exported. Recorded by the orchestrator from the reviewer's two reports.
- **Gate**: security. **Date**: 2026-11-01.
- **Target**: T714 (batch C, plan-125) on `docs/plan-125-post-v9`: first review at `a54e42b1` (`dfcccddb`, `91a6e358`, `acf9a25d`), re-check of the fixes `5fa9629c`, `7a7c6b8b`, `b26f6ebe` merged at `37e7ef76`.
- **Based on**: `docs/tasks/task-T714.md`; `docs/plans/plan-125-post-v9-follow-ups.md`; `security-review-t701-t703-wave1-v1.md`, `security-review-t689-token-placement-v1.md`, `security-review-t690-copilot-security-servers-v1.md`; `security-review-t697-t699-debt-checkpoint-refresh-v1.md` (TD-T697-08); `implementation/runtime/security/executor.py`, `validation.py`, `audit_server.py`, `poc_audit_server.py`, `commands.py`; `scripts/check-gitlab-token.py`; `implementation/PREREQUISITES.md`, `implementation/SECURITY.md`, `docs/wiki/mcp-servers.md`.

## Verdict: PASS (after the re-check)

The first review was CONDITIONAL_PASS with one MEDIUM (SEC-T714-01); the fixes close it. 0 critical, 0 high; no Immutable Security Constraint breached; no control weakened. The PASS holds with SEC-T714-02, -04, -06 and -08 tracked as LOW debt (this artifact is the record; owner devops-engineer; next sprint; for the next register version).

| Severity | Count | Resolved | Remaining |
|---|---|---|---|
| CRITICAL | 0 | 0 | 0 |
| HIGH | 0 | 0 | 0 |
| MEDIUM | 1 | 1 (SEC-T714-01) | 0 |
| LOW | 7 | 3 (-03, -05, -07) | 4 (-02, -04, -06, -08, tracked) |

## Rulings on the changes

- **Child environment** (`executor.py`): the allowlist is close to minimal; nothing token-bearing passes except the proxy variables (documented). After the fix the non-secret pointer variables pass (`PIP_CONFIG_FILE`, `XDG_CONFIG_HOME`, `XDG_CACHE_HOME`, `NPM_CONFIG_USERCONFIG`, `NPM_CONFIG_GLOBALCONFIG` and the lowercase npm forms, `NUGET_PACKAGES`), `DOTNET_CLI_TELEMETRY_OPTOUT=1` and `DOTNET_NOLOGO=1` are always set, and `index_override_error` at the top of `run_fixed_argv` refuses pip-audit when a `PIP_(AUDIT_)?(INDEX_URL|EXTRA_INDEX_URL|FIND_LINKS)` variable is set and npm when an `npm_config_*registry` variable is set (case-insensitive; the error names variables only, never values). `PIP_CONFIG_FILE` and `NPM_CONFIG_USERCONFIG` restore pre-T714 behaviour and are operator-set, not a regression. The argv is fixed, so `--index-url` cannot be injected; index lines inside a requirements file remain pip-audit's documented model (SEV-T690-02). The NuGet decision (no guard; sources come from `NuGet.Config`, dropped credentials fail authentication rather than switch sources) is sound; whether `dotnet list --vulnerable` ever restores with an environment-only `RestoreSources` is unverified and not a finding.
- **`validate_allowed_root`** (`validation.py:106-126`, called by `audit_server.py:90` and, after the fix, `poc_audit_server.py:94`): refuses `/`, `$HOME` and its ancestors including through a symlink, a trailing slash, a relative path and an unset `HOME`; fails closed at start.
- **Sensitive names** (`validation.py:33-37`): case-blind; refusing `.aws` as a whole directory is right; every name of the `security-guidelines.md` "do not read" list is covered.
- **`check-gitlab-token.py`**: the open-to-check TOCTOU is closed (the descriptor's own path, no second name resolution); the token cannot reach output; exit 0 with the undetermined-storage qualifier and `--strict-storage` for exit 1 is acceptable for an advisory tool, and the docstring now says so.
- **Docs**: the hibernation note, the full gpg/`secret-tool` chain with `rm -f --` under `umask 077`, the `.env` location rule (strictly stronger; consistent with Constraints 1 and 6 and the TD-T697-08 ruling) and `SECURITY.md` § 4.2 are accurate.

## Findings

| Id | Grade | Location | Finding | Status |
|---|---|---|---|---|
| SEC-T714-01 | MEDIUM | `executor.py` `CHILD_ENV_NAMES` | The allowlist silently dropped package-index settings: an index set only in the environment fell back to public PyPI or npm (dependency confusion); the dotnet telemetry opt-out was dropped. | fixed (`5fa9629c`; `PackageIndexSettingsTests` with a mutation proof) |
| SEC-T714-02 | LOW | `validation.py:106-126` | `validate_allowed_root` trusts `$HOME`: an empty or overridden `HOME` lets the real home pass; broad non-ancestors (`/etc`, `/tmp`, `/dev/shm`, other homes, `~/.config`) are accepted. | tracked-LOW: also refuse the passwd home and its ancestors and an empty `HOME`; optionally `~/.config`, `/dev/shm`, `$XDG_RUNTIME_DIR` |
| SEC-T714-03 | LOW | `poc_audit_server.py:92` | The PoC server's `--allowed-root` lacked the broad-root check. | fixed (`7a7c6b8b`; `BroadAllowedRootTests`) |
| SEC-T714-04 | LOW | `validation.py:33-37` | Missing names: `.ssh` (or `id_ecdsa*`, `id_dsa*`, `*.ppk`), `.docker`, `.kube`, `.gnupg`, `.pypirc`, `.vault-token`, `*.jks`, `*.keystore`, `*.tfstate`, `credentials.tfrc.json`, and MCP configs that may hold a pasted token (`.claude/settings.local.json`, `.vscode/mcp.json`, `.pi/mcp.json`). On Copilot the list is not a boundary (SEV-T690-04 (d)). | tracked-LOW |
| SEC-T714-05 | LOW | `check-gitlab-token.py:13`; `PREREQUISITES.md` step 6 | The docstring said every warning means exit 1 while the storage qualifier keeps exit 0. | fixed (`b26f6ebe`; `--strict-storage` recommended for automated use and macOS) |
| SEC-T714-06 | LOW (informational) | `executor.py` | Proxy URLs may carry credentials and `HOME` exposes `~/.npmrc`/`pip.conf` indirectly; tool stdout/stderr reach the agent verbatim. | tracked-LOW: redact `scheme://user:pass@` in `run_fixed_argv` output; state the residual in the wiki |
| SEC-T714-07 | LOW | `PREREQUISITES.md:213` | Two different "step 3" references in one sentence. | fixed (`b26f6ebe`) |
| SEC-T714-08 | LOW (new in the re-check) | `executor.py` `_PIP_INDEX_RE`, `CHILD_ENV_NAMES` | pip hardening settings made in the environment (`PIP_NO_INDEX`, `PIP_ONLY_BINARY`/`PIP_NO_BINARY`, `PIP_REQUIRE_HASHES`, `PIP_CONSTRAINT`) are dropped without the guard noticing: `PIP_NO_INDEX=1` with `find-links` in `pip.conf` reopens the public index; a dropped `PIP_ONLY_BINARY=:all:` lets source builds run. | tracked-LOW: refuse on every `PIP_*`/`PIP_AUDIT_*` variable except `PIP_CONFIG_FILE`, with a subtest |

## Disposition of earlier ids

| Id | Status |
|---|---|
| SEC-T701-01 | closed (hibernation note at `PREREQUISITES.md:155-156`; the erratum `security-review-t665-token-handling-v3.md`) |
| SEC-T701-02, SEC-T701-03 | closed |
| SEC-T689-02 (rest) | closed |
| SEC-T689-04 | closed (wording residual SEC-T714-05, fixed) |
| SEC-T689-05 | closed (descriptor path; mount-namespace limit documented) |
| SEV-T690-02 | partly closed: the trust-boundary paragraph and CODEOWNERS guidance are in `SECURITY.md` § 4.2; the pinned runtime package stays tracked |
| SEV-T690-04 | partly closed: (a) environment, (b) `allowed_root`, (c) names done with residuals SEC-T714-02, -04, -06, -08; (d) the Copilot security agents hold `read`/`search`, so the server's denials are not a boundary there: still open |

## Unverified

- Whether pip-audit's internal `pip install` reads `PIP_*` variables and `PIP_CONFIG_FILE` (inferred from pip and pip-audit's documented model).
- Whether npm, pip, pip-audit or dotnet print proxy or registry URLs with credentials in errors; whether `dotnet list --vulnerable` restores.
- Whether `rg --iglob '!**/.aws'` stops descent (assumed by analogy with `.git`).
- The reviewer ran no tests; the orchestrator ran the touched test modules and the full suite.
