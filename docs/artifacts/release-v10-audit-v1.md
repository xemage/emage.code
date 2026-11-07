# Artifact: release-v10-audit-v1.md

> Immutable once produced; a revision is `release-v10-audit-v2.md`. Release-level audit of `v9.0.0..develop` for v10.0.0 (task T753, plan-145 wave 1). It feeds T757 (version markers) and T758 (`docs/releases/v10.0.0.md`), and every § 6.2 item is assigned in section 5.

**Based on:** `docs/tasks/task-T753.md`; `docs/plans/plan-145-release-v10.md` (§ Why MAJOR, § Task Decomposition); `docs/artifacts/tracked-debt-register-v11.md` (§ 6.2, § 6.3, § 7); `docs/artifacts/release-v9-audit-v1.md` (shape only); `docs/tasks/completed-tasks.md` rows T711 to T752; `git log v9.0.0..develop`; `git diff v9.0.0 develop`; § Outcome of plans 127, 128, 129 and 133 (read); plans 125 to 144 otherwise by grep.

**Author / mode:** Tech Lead, review mode (read-only). Only this file was written; no source, script, marker, ledger row or brief status changed. The throwaway targets lived in my own folder under the session scratchpad and are deleted.

**Code state audited:** worktree `agent/tech-lead/T753` at `16ea3418`, which is `develop` (`6d4abc1b`) plus the two plan-145 commits. `v9.0.0` (tag commit `e4c7e7d4`) is an ancestor of `develop`.

**Basis marker:** **(V)** verified (file or diff read, or command run; the evidence names which). **(I)** inferred (reason given). **(unverified)** not read, not run, or not checkable from here. How the throwaway installs ran is in section 8.

---

## 1. Answer: does MAJOR hold, and is T725 the only breaking change?

**MAJOR holds. T725's deletion is not the only breaking change.** The rule is skill `release-workflow` § Semantic Versioning: "Breaking changes to public API or contracts" (`implementation/knowledge/skills/release-workflow/SKILL.md:27`). Three tasks break something that works under v9.0.0 in an installed target, unless the adopter acts:

| Task | What stops working in a target | Who is hit | Evidence |
|---|---|---|---|
| T725 | `/prepare-release` is deleted on five platform paths, in every install mode. A renamed copy inside a platform tree is deleted too (section 3, M-1) | Any target that used the command | (V) v9 install, then `--update` from this tree |
| T722 | `context-retriever` stops reading a v9 index. `--projections-only` from v9 leaves the server unable to start (M-2). The Copilot agent loses its tool grant (M-4) | Any target that built an index, or defined its own server on Copilot | (V) same install; server process run |
| T714 | `security-audit` and `poc-security-audit` refuse a broad root, audits refuse an index set only in the environment, and child tools lose inherited credentials (M-3) | A target rooted at `$HOME`, or using an environment-only package index or credential | (V) functions called in the updated target |

Two more break only for someone working from an emage.code checkout: T726 (CWSO helper options, M-6) and T739 (the release gate needs a parser, M-7). The generator refusals of T722 and T725 hit a fork that authors its own knowledge (M-5).

**The version does not change, so this does not trigger plan-145's return to the user on version grounds.** The reason for it does: plan-145 § Why MAJOR and register v11 § 6.2 name only T725. Neither T714 nor T722 appears in § 6.2 as a migration item, so a release document written from § 6.2 alone would miss them.

## 2. Coverage and classification

### 2.1 Coverage

| Item | Value |
|---|---|
| Range | `v9.0.0..develop`: 43 commits, 21 non-merge (V, `git rev-list --count`, `git log --no-merges`) |
| Plus | `e18ac6c6` and `16ea3418` (plan-145 and briefs), not yet on `develop` (V) |
| Diff | 366 files, +18753 / -1145; outside platform mirrors and `docs/{tasks,plans,artifacts,checkpoints}`, 98 files (V) |
| Tasks in range | T711 (archive) and T713 to T752 (V, `completed-tasks.md`). T712 is in `v9.0.0` (V, `git log v9.0.0 --grep T712`) |
| What an update changes in a v9 target | 99 files: `.claude` 16, `.cline` 7, `.gemini` 17, `.github` 17, `.opencode` 17, `.pi` 17, `.mcp.json` 1, `implementation/runtime/` 7. **`docs/`, `AGENTS.md` and `CLAUDE.md`: none** (V, `git diff --name-only` in the target) |

### 2.2 Classes

- **Breaking (target)**: something that worked in an installed target under v9.0.0 stops, unless the adopter acts (the class of `release-v9-audit-v1.md` § 1.2).
- **Breaking (checkout)**: the same, but only for someone running code from an emage.code checkout, which a target does not receive (section 4).
- **Behaviour (target)**: an installed project's tools or agent text change, and nothing stops working without a stated replacement.
- **Release author**: visible when writing or publishing a release from this repository. A target does not receive it.
- **Other repository**: CWSO.
- **Internal**: registers, rulings whose effect is in another task, tests, reviews.

**Counts (40 task ids): breaking (target) 3, breaking (checkout) 2, behaviour 5, release author 12, other repository 2, internal 16.**

### 2.3 Task classification

| Task | Commit | Class | What changed | Citation |
|---|---|---|---|---|
| T711 | `4a7e0aa8` | internal | v9.0.0 publish closed, checkpoint-040 | ledger row |
| T713 | `414d425b` | internal | Register v4 | ledger row |
| **T714** | `414d425b` | **breaking (target)** | Allowed-root refusal, child environment allowlist, index guard, more refused names; `check-gitlab-token.py --strict-storage`; `PREREQUISITES.md`; `SECURITY.md` § 4.2 | `runtime/security/executor.py`, `validation.py:117-127`, `audit_server.py:90`, `poc_audit_server.py:94`; M-3 |
| T715 | `82691e7f` | release author | Gate: fenced anchors, unparsed pointers, `--allow-newer-pointers` | `verify-release-docs.py --help` |
| T716 | `82691e7f` | release author | Release script: escaped changelog entries, entry below `[Unreleased]`, semantic previous tag; exact refs in the tag-tree check | ledger row; § 6.2 items 6, 7 |
| T717 | `82691e7f` | release author | `CONTRIBUTING.md`: hotfix during an open release, pre-release tags, retag | `CONTRIBUTING.md:401, 435, 478` |
| T718 | `63524f01` | internal | Rulings; effect in T720 | `plan-127` § Outcome |
| T719 | `63524f01` | behaviour | Agent and command text | M-8 |
| T720 | `63524f01` | behaviour | Release gate rules, ADR-011 | M-8 |
| T721 | `63524f01` | internal | Text pins | ledger row |
| **T722** | `4e71af62` | **breaking (target)** and breaking (checkout) | `--index-dir` dropped from every generated config; default index path; Copilot grant dropped; `mcp.outputFile` allowlist; denials honour `extraPlatforms` | `servers.yaml:197-199`; `context_retriever.py` `default_index_dir`; `server.py:112-114, 133`; `sync.mjs` `withEmittedMcpTools`, `assertMcpOutputFile`; M-2, M-4, M-5 |
| T723 | `4e71af62` | behaviour | Byte-wise `printable`, ledger fsync and no-clobber publish, Cursor notice lines | `install.sh`, `merge-task-docs.py`; M-8 |
| T724 | `4e71af62` | behaviour | `{env:NAME}` no longer gives a false "differs" note | `merge-mcp-json.py:112-114`; M-8 |
| **T725** | `4e71af62` | **breaking (target)** and breaking (checkout) | `audience:` required, `authoringOnly` manifest list, installer withholds | `install.sh` `withhold_authoring_only`; `sync.mjs` `commandAudience`; `plan-128` § Outcome; M-1, M-5 |
| T726 | `8ba4e774` | breaking (checkout) | CWSO helper options | `sia-executor.py`, `cwso-deploy-helper.sh`, `mint-cwso-jwt.py`, `cwso-proxmox-setup.sh`; M-6 |
| T727, T728 | CWSO `6630ecb` | other repository | CWSO server and CI | `plan-129` § Outcome; CWSO not read **(unverified)** |
| T729 | `a46ba7b6` | internal | Register v5 | ledger row |
| T730 | `913a8de7` | release author | Sigils escaped, URL tokens in code spans, exact refs in the drift check | § 6.2 item 7 |
| T731 | `913a8de7` | release author | More pointer forms fail; line separators refused | § 6.2 item 7 |
| T732 | `913a8de7` | internal | acorn in `unit-tests` (`ci/js/`) | ledger row; § 6.2 item 8 |
| T733 | `b33c9b35` | internal | Register v6 | ledger row |
| T734 | `d76a43f7` | internal | ADR-012; effect in T735 | `docs/decisions/ADR-012-medium-acceptance-record.md` |
| T735 | `d76a43f7` | behaviour | Release, hotfix and verdict text; `/prepare-release` mentions marked authoring-only | M-8; `plan-133` § Outcome |
| T736 | `d76a43f7` | internal | Text pins | ledger row |
| T737 | `bbfe5602` | internal | Register v7 | ledger row |
| T738 | `6e724383` | release author | `install.sh` line separators refused; pointer checks | § 6.2 item 7 |
| T739 | `9e43d135` | breaking (checkout) | The gate needs `markdown-it-py`; `ci/requirements-release.txt` | M-7; § 6.2 item 16 |
| T740 | `7fb165e9` | internal | Register v8 | ledger row |
| T741 | `41df4020` | release author | Strict UTF-8, pinned pipeline, no job on a tag outside the three tag jobs | § 6.2 items 15, 18, 19, 20 |
| T742 | `dcc9297a` | internal | Register v9 | ledger row |
| T743 | `7e02cba5` | release author | Refusals: front matter, CR in `install.sh`, long lines | § 6.2 item 7 |
| T744 | `7e02cba5` | release author | Exact pins, clone on the gates, strict child reads | § 6.2 items 20, 23 |
| T746 | `1822aae0` | internal | Register v10 | ledger row |
| T747 | `bae5c4df` | release author | Verdict check reads the parser's tokens | § 6.2 items 7, 30 |
| T748 | `bae5c4df` | internal | Security review | `security-review-t748-batch-t-v1.md` |
| T749 | `999e0ef0` | release author | HTML anywhere, size and nesting refused | § 6.2 items 22, 25 |
| T750 | `999e0ef0` | release author | `run-allowlisted.py` on every gate command, `timeout`, clone on `release` | § 6.2 items 14, 21, 26 |
| T751 | `999e0ef0` | internal | Security review | ledger row |
| T752 | `92eb72c3` | internal | Register v11 | ledger row |

**T745 has no ledger row** (V, grep of `docs/tasks/*.md`). It is the review id of plan-140 (`docs/plans/plan-140-batch-s-release-gate.md:70`, `security-review-t745-batch-s-v1.md`), named in T744's row. It is not counted above. A record gap only (TL-T753-07).

## 3. Migration items for `docs/releases/v10.0.0.md` (draft; the release manager owns the wording)

### M-1. `/prepare-release` is no longer installed (T725, TD-T671-P5). **Before `--update`** if you use it.

- Removed from a target on `.claude/commands/prepare-release.md`, `.gemini/commands/prepare-release.md`, `.opencode/commands/prepare-release.md`, `.pi/prompts/prepare-release.md`, `.github/prompts/prepare-release.prompt.md` (V, `authoringOnly` of each manifest; `.cline` lists none, and `.clinerules` has no manifest).
- All three modes delete an existing copy: `--update`, `--projections-only` and a plain install (V, each run). A dry run prints the `rm` (V).
- An authoring checkout, a directory holding `implementation/registry/index.json`, keeps it (V, by `tests.functional.test_install_command_audience`, 12 tests OK; not by my own install).
- `.generated-manifest.json` gains `authoringOnly` (V). Its `files` list still names the withheld path in a target (V; TL-T753-06).

**Correction to § 6.2 item 1 and `plan-128` § Outcome (TL-T753-01).** They say a target that used the command "keeps its own copy under another file name". **Inside a platform tree that fails:** I put `.claude/commands/my-prepare-release.md` in a target, and both `--update` and `--projections-only` deleted it, with no line naming it in the log (V). Only a plain install left it (V). This is the known `rsync -a --delete` of `AGENTS.md` § Knowledge Base; `commands/` is not a spared path. The item must say: keep the copy **outside** the platform trees, and copy it back after each `--update` or `--projections-only`.

### M-2. `context-retriever`: the index location now comes from the git remote (T722, TD-T671-K5). **After `--update`**, if you built an index.

- Every generated config drops `--index-dir implementation/runtime/memory/_index/em-age-emage.code` (V, `.mcp.json`, `.gemini/settings.json`, `.opencode/opencode.json`, `.pi/mcp.json`, `.cline/mcp.json`).
- The server now reads `implementation/runtime/memory/_index/<org>-<repo>`, lower case, from the workspace's git remote (V: `acme/widget` gave `_index/acme-widget`; `implementation/runtime/memory/README.md`).
- **A v9 target built its index in the old path,** because v9's installer note told it to match the `--index-dir` already in the config (V, v9 install log; the same words are at `scripts/install.sh:1749-1750`). After `--update` that index is not read, and the server does not start: the load fails with `FileNotFoundError` on `_index/acme-widget/manifest.json` (V, `ContextRetriever`, called from `build_server`, `server.py:79`). **Action:** rebuild with `--output-dir implementation/runtime/memory/_index/<org>-<repo>`. Moving the directory instead looks sufficient, because the directory name is not read from the manifest, but I built no index **(unverified)**.
- **With no git remote the server now fails at start** with `RemoteResolutionError` (V, `default_index_dir`), where v9 got past start with a given index directory and failed at the first query (I, `derive_requesting_context` runs per call).
- **A hand-set `--index-dir` under the generated name is replaced with no note** (V: a v9 entry edited to `custom/index`, then `--update --platform claude-code`, gave the generated `args`, and the log has no line about it). So the new `runtime/memory/README.md` sentence "Pass `--index-dir` to the server to use another location" holds only in an entry under a name the generator does not own (I, `AGENTS.md`: the merge keeps such names).
- **`--projections-only` must not be the step from v9 to v10 (TL-T753-02).** It refreshes the configs but not `implementation/runtime/`, so the v9 server, which still requires `--index-dir`, runs without it (V: after that mode, the process exits with `error: the following arguments are required: --index-dir`). **Action:** use `--update` for this step.

### M-3. `security-audit` and `poc-security-audit` refuse what they accepted (T714; SEV-T690-04, SEC-T714-01, -03). After `--update`; check before if one applies. `implementation/runtime/` is refreshed by `--update` and a plain install, not by `--projections-only`.

- **A broad root stops the start.** `allowed_root` of `/`, `$HOME` or an ancestor of `$HOME` raises `PathValidationError` (V, `HOME` set to the target and `validate_allowed_root('.')`). A project whose root is `$HOME` loses both servers. **Action:** launch from a workspace directory below it.
- **An index set only in the environment refuses the audit.** `run_pip_audit` refuses while `PIP_INDEX_URL`, `PIP_EXTRA_INDEX_URL` or `PIP_FIND_LINKS` (or a `PIP_AUDIT_` form) is set, and `run_npm_audit` while any `npm_config_*registry` is set (V, `index_override_error`, both). **Action:** move the setting into `pip.conf` or `.npmrc`, unset the variable and restart the server.
- **Child tools no longer inherit the server's environment** (V, `child_env`: `NODE_AUTH_TOKEN` and `GITLAB_PERSONAL_ACCESS_TOKEN` not passed; `executor.py` `CHILD_ENV_NAMES`). A registry credential held only in a variable is no longer seen; by the module's docstring a NuGet feed then fails with an authentication error, which I did not run **(unverified)**. Keep such credentials in the tool's own file.
- **`grep_content` refuses more names:** `.netrc`, `.npmrc`, `.pgpass`, `.git-credentials`, `.aws`, `*.p12`, `*.pfx`, `*.kdbx` (V, `validation.py` `SENSITIVE_NAME_GLOBS`). No action.
- No credential in a child's environment is the point of the change. Say so: this is a control tightened, not a regression.

### M-4. Copilot: the `context-retriever` agent loses `context-retriever/retrieve` (T722, SEV-T690-06). After `--update`, silently.

`tools:` becomes `[read, search]` in `.github/agents/context-retriever.agent.md` (V). Copilot's generated config has no such server, so the grant could be met only by a server the user defined. Such a user loses the tool until an agent file of theirs grants it, and an edit to the generated file does not survive `--update`. It is the only agent token dropped on any platform (V, target diff). Whether the agent is useful without it on Copilot **(unverified)**.

### M-5. Generator, for a fork that authors its own knowledge (T722, T725; SEC-T684-02).

- `sync.mjs` stops on a command without `audience: authoring | target | both` (V, `commandAudience`; `test_generator_rejects_unknown_or_missing_audience`).
- `mcp.outputFile` must lie under the manifest's `outputDir`, or be exactly `.mcp.json` or `.vscode/mcp.json` at the root; an MCP file may not lie in another manifest's removal tree (V, `assertMcpOutputFile`, `assertMcpFilesApart`).
- An `mcp__<server>__` token of a server that `servers.yaml` defines but a platform does not carry is left out of that platform's agent (V, `withEmittedMcpTools`).

### M-6. CWSO helper scripts, from a checkout (T726). A target does not receive them (section 4).

- `implementation/scripts/sia-executor.py`: `--jwt-secret` is removed; use `--jwt-secret-file <path>` or `CWSO_JWT_SECRET`; no abbreviation (V, diff).
- `scripts/cwso-deploy-helper.sh`: `export --secret-file <path>` now also needs `--print-secret` and refuses a terminal; `verify`'s `--workspace` and `--diag` default to a new `mktemp -d` directory, not `/tmp/cwso-credcheck*`; `--parquet-store` is new (V, diff).
- `scripts/deploy/cwso-proxmox-setup.sh`: Docker Engine 29.9.2 and compose v5.6.1 pinned and sha256-checked; a `.env` value with a backslash is refused (V, ledger row, diff).
- Still open: `implementation/scripts/dispatch-test-sia.py` accepts `--jwt-secret` on argv (TD-T726-01, `plan-129` § Outcome).
- CWSO's own redeploy conditions are user action A-16 (register v11 § 7), separate from this release.

### M-7. Release authors of this repository (§ 6.2 items 3, 7, 16, 20, 22, 25, 27, 30). Not for a target.

The document's release-author section can point to `CONTRIBUTING.md` § Releasing. The break is T739: **no parser, no gate** (`verify-release-docs.py:174-180`; `CONTRIBUTING.md:164-167`). The rest is refusals, listed under the § 6.2 items in section 5.

### M-8. Behaviour changes to brief your team on (no action).

- **Release gate (T720, T735; ADR-011, ADR-012):** a user-accepted `SECURITY:MEDIUM` covers one release only, and the next release gate lists each one until it is fixed or accepted again (`validation-gates/SKILL.md`, Release Gate inputs, new lines 119-120). `release-manager` issues no PASS or CONDITIONAL_PASS on its own release files without an independent check row (`agents/release-manager.md:46`). The verdict gains `Issued at commit` and `Independent check`, and the Conditions block `grade=` and `release=` (`:183`).
- **Hotfix (T735):** eligibility is graded on the issue's own scale, or is a breach or weakened control that `@security-engineer` confirms; a fix with design impact does not take the fast track (`release-workflow/SKILL.md:171, 202`).
- **Text (T719, T720):** `qa-engineer` bug priority is `P0 | P1 | P2`, no `P3`; `scrum-master` adds `Critical`; `dependency-graphing` swaps `in_progress` (yellow) and `in_review` (blue); `/batch` states its slug rule; `plan-approve-execute` maps `/new-project`'s three answers; `/discover-skills` loses the optional packaging step; `/validate-tasks` and `/validate-workflow` no longer imply `/prepare-release` in a target (V, diffs).
- **Installer (T723, T724):** `printable` is byte-wise, so a non-ASCII name prints with `?`; `merge-task-docs.py` refuses a backup or seed name taken after planning, and a dry run creates nothing; the Cursor notice has one line per case; an unedited Opencode entry no longer draws a false "differs" note (V, diffs; the refusal not run).
- **Docs (T714):** `SECURITY.md` § 4.2: the scanner lives in the workspace it scans; put `implementation/runtime/` under code-owner review. `PREREQUISITES.md`: hibernation, `.env` location, the gpg chain. `check-gitlab-token.py --strict-storage`, run from a checkout (V, diffs).

## 4. What the release document must not assume (§ 6.2 item 13, settled)

**Targets receive neither `scripts/verify-release-docs.py` nor `docs/releases/_template.md`.** (V, install from this tree into an empty directory, all platforms, and `--update` over a v9 target.) This closes the **(unverified)** of § 6.2 item 13.

- A fresh target holds `.claude .cline .clinerules .gemini .github .mcp.json .mcp.json.provenance.json .opencode .pi .vscode AGENTS.md CLAUDE.md docs implementation`.
- **Not present:** `scripts/`, `docs/releases/`, `ci/`, `.gitlab-ci.yml`, `CONTRIBUTING.md`, `CHANGELOG.md`, `implementation/scripts/`, `implementation/registry/`.
- `implementation/` holds only `__init__.py` and `runtime/` (`handoff`, `memory`, `security`). `docs/wiki/` holds only `README.md` and `home.md`.

So the document must not:

1. tell a target to run a `scripts/` command as if it were there (`check-gitlab-token.py`, `merge-mcp-json.py`, the gate): each runs from an emage.code checkout;
2. link to a sibling `docs/releases/` path as if it were in the target. `install.sh:187` and `:1297-1301` name `docs/releases/v8.0.0.md` and `v9.0.0.md`; those are in the emage.code repository;
3. promise that a v9 target keeps a working `context-retriever` or `/prepare-release` through `--update` (M-1, M-2);
4. treat `--projections-only` as enough for v9 to v10 (M-2);
5. state that `CHANGELOG.md` changed in the range: it did not (V, empty diff). Its entry is the release job's, unobserved (§ 6.2 item 6).

**Shipped text that names what a target lacks (TL-T753-05, pre-existing):** `.claude/skills/verification-before-completion/SKILL.md:85`, `.claude/agents/orchestrator.md:130, 133, 134`, and the seeded `docs/wiki/home.md:24`, `docs/wiki/README.md:15` tell the reader to run `scripts/verify-release-docs.py` (V, fresh target). The same script name is in v9's generated tree (V, `orchestrator.md` and `verification-before-completion`). Not new; a Known Issue or a tracked item, and no reason to hold the release.

## 5. Next-release checklist, register v11 § 6.2: who handles each item

| # | Item | Handler | Task | Note from this audit |
|---|---|---|---|---|
| 1 | T725 migration item | release-manager | **T758**; shown by qa-engineer in T760 | Facts (V). **Change the "another file name" advice** (M-1, TL-T753-01) |
| 2 | ADR-011 re-acceptances (four, and how to ask) | security-engineer states them; orchestrator asks; user decides; release-manager records | **T756**, then the user; **T763** | Deadlines not read here; T756's acceptance requires it |
| 3 | `Issued at commit`, `Independent check` | release-manager | **T763** | `_template.md:87-88`, re-read (V) |
| 4 | TD-T723-01, current `install.sh` citations | release-manager | **T758** | Today the advice is `:1297-1300`, the pointer `:1301` (V); add `:187`, which also names the v9 document. T757 must not shift them unnoticed |
| 5 | Brave date and version | devops-engineer; orchestrator re-checks before the tag | **T755**; **T764** | 2026-11-06 is before 2027-01-30 (V). Newest Brave version is T755's (not read here) |
| 6 | `CHANGELOG.md` below `[Unreleased]` | devops-engineer rehearses; orchestrator and user observe | **T759**; **T764** | No change to the file in range (V) |
| 7 | Visible changes of batches G, S, T | release-manager; devops-engineer rehearses the escaped references | **T758**; **T759**; **T761** reads | Goes in M-7 |
| 8 | Unverified live: rendering, npm step, musl lock | orchestrator and user | **T764** | Rendering partly in T759. Reduced, not closed |
| 9 | Conditions block | release-manager, from T756 and the user's words | **T763** | `agents/release-manager.md:183`, re-read (V) |
| 10 | Template pointer sentence | release-manager, before the check | **T758** | `_template.md:90`, re-read (V) |
| 11 | Independent checker | orchestrator dispatches; `@tech-lead` | **T763** (check), reusing **T761** if current | This audit edited no release file, so it does not itself disqualify a Tech Lead checker (`agents/release-manager.md:46`) |
| 12 | Closed list after the check; hotfix eligibility | release-manager | **T763**; T758 carries the hotfix text as M-8 | No text outside the closed list after the check |
| 13 | Do targets receive the gate and template? | **settled here: no** (section 4); release-manager applies it | **T753**; **T758**; T760 confirms on the release tree | (V) |
| 14 | Watch `release-docs-gate` at the tag | orchestrator; user approves each step | **T764** | Timeout, removal path and `release` still unobserved |
| 15 | No `allow_failure` on tag jobs | test holds it; reviewer reads | **T761**; **T764** if PyPI is down | No change planned |
| 16 | A local gate run needs the parser | release-manager, qa-engineer | **T758**, **T760** | **The local parser here is 3.0.0, the lock 4.2.0** (V). T758's acceptance says "on the locked parser": use a venv |
| 17 | Regenerating `ci/requirements-ci.txt` needs the release lock too | devops-engineer, only if regenerated | **T755**, if it regenerates; none planned | Fact |
| 18 | New CI job needs an `if` from `NOT_TAG_CONDITIONS` | reviewer | **T761** | No new job planned (T754 and T757 add none); fact |
| 19 | Digest bump passes; `apk` or Python minor needs a constant edit | devops-engineer, only if bumped | **T755**; **T761** | Fact. The header gap is unscheduled |
| 20 | Checked file must be valid UTF-8 | release-manager; qa-engineer | **T758**, **T760** | Child check also strict (ran on this tree, PASS at v9 marker) |
| 21 | CI variables stay out of gate commands | reviewer; orchestrator watches | **T761**; **T764** | No new variable planned. No test reads project variables, so `GIT_STRATEGY` and `CI_PROJECT_DIR` are for T764 |
| 22 | No HTML other than comments in the document | release-manager; gate | **T758**, **T760** | |
| 23 | Release script line needs `RELEASE_COMMAND` | devops-engineer if changed; reviewer | **T759** (read only); **T761** | No change planned |
| 24 | A release candidate is a full release | orchestrator | none: plan-145 has no candidate and no probe tag | Reopens only if the user asks |
| 25 | Size and nesting limits | release-manager; gate | **T758**, **T760** | 131072 characters; 20 levels |
| 26 | `run-allowlisted.py` has no pin; code review | tech-lead; security-engineer | **T761**; **T762** | |
| 27 | Placeholders: replace, not code span | release-manager; a reader must check the rest | **T758**; **T761** | Gate does not read others (SEC-T751-09) |
| 28 | First real tag pipeline's watch list | user runs; orchestrator reports | **T764** | `CONTRIBUTING.md:279-292`, re-read (V) |
| 29 | No `docker` unless approved | orchestrator, in each brief | all; **T759** only, as approved in plan-145 | This audit ran none |
| 30 | Verdict section heading rule | release-manager; gate | **T763**, **T760** | |

## 6. Version markers for T757 (simulated, not bumped)

On a scratch `git archive` without `tests/` and without the platform trees, I changed `README.md`'s marker to `v10.0.0` and ran `scripts/check-version-consistency.py` (V). It names exactly: `README.md:222`, `docs/wiki/README.md:6`, `docs/wiki/home.md:5`, `docs/wiki/implementation-guide.md:5, 41`, `implementation/README.md:4, 6, 61`, plus `README.md:14` (the marker changed). `implementation/knowledge` holds no `v9.0.0` (V, `git grep`). No non-marker line was flagged, unlike the v9 audit's § 4.2. Unmodified, it passes at `v9.0.0` (V).

## 7. Findings of this audit, and what they ask of the plan

| ID | Severity | Finding | Asks of the plan |
|---|---|---|---|
| TL-T753-01 | Important | The "keep a copy under another file name" advice fails inside a platform tree (M-1) | T758 uses M-1's wording, not § 6.2 item 1's |
| TL-T753-02 | Important | `--projections-only` from v9 leaves `context-retriever` unable to start (M-2) | T758 states it; T760 may show it. A code fix is not proposed: the old runtime cannot be changed from here, and a warning in the installer would be new scope |
| TL-T753-03 | Important | T714 and T722 breaks are in neither § 6.2 nor plan-145 § Why MAJOR | T758 takes M-2 to M-6 from here. The orchestrator tells the user the reason widened, though the version does not |
| TL-T753-04 | Minor | **New stale note:** `scripts/install.sh:1749-1750` still says to match the `--index-dir` "already set in the generated mcp.json". There is none since T722 (V, printed by this tree's install). No test pins the sentence (V, `git grep`) | **Decision for the orchestrator:** a one-line fix in wave 1 before T757, or a Known Issue. I recommend the fix: every install prints it, and it is the same instruction that caused M-2. `build.py:12`'s example has the same old path |
| TL-T753-05 | Minor | Shipped text names scripts a target lacks (section 4) | Known Issue or tracked |
| TL-T753-06 | Minor | `files` in a target's manifest names the withheld command. No reader of `files` found in `scripts/`, `sync.mjs` or the retriever (V, grep) | Tracked |
| TL-T753-07 | Minor | T745 has a review, no ledger row | Register v12; no action for the release |

**Nothing here blocks the release.** Security findings are for T756 and T762; I graded none, and found no control weakened in this range's target-facing code (T714 and T722 tighten). That is a code reviewer's reading, not T762's re-check.

Known Issues: I did not derive the list. T758 takes it from register v11 (§ 5, § 6.1, § 7) and T756; plan-128's SEC-T663-02, `plan-129`'s TD-T726-01 and A-19's two probe tags are the ones this audit met. The v9 K-items were not re-read **(unverified)**.

## 8. Method and what I did not verify

**Method.** A v9 tree from `git archive v9.0.0` installed into a throwaway target with `origin` `https://example.invalid/acme/widget.git` (rc 0), committed there, then `--update --dry-run`, `--update` (rc 0), with variants restored from that commit: hand-set `--index-dir`, `--projections-only` (claude-code), renamed copy in all three modes, a plain install over a stale copy. A separate fresh install from this tree (rc 0). Python functions imported from the updated target. All deleted. `tests.functional.test_install_command_audience` passed (12 tests).

**(unverified), each named where it arises:**

1. Moving an old index instead of rebuilding (M-2); no index was built, so a v10 retrieval was not run.
2. Any live client: no assistant started a server. M-2's start failures are from the server process and its loader; M-3's from the functions, not an MCP call.
3. A NuGet or private npm feed failing after T714 (M-3); the guards ran, the audits did not.
4. Copilot's `context-retriever` agent without the tool (M-4).
5. T727, T728 and A-16 in CWSO; that repository was not read.
6. The `merge-task-docs.py` refusal (M-8), read and not run. T723's other items are from its ledger row and the diff.
7. Plans 125 to 144 were not read in full. Outcomes of 127, 128, 129 and 133 were read; the register plans (130, 132, 134, 137, 139, 141, 144) only through their ledger rows; the gate plans through § 6.2's text, which I did not re-derive except where section 5 says "re-read".
8. Knowledge text: added lines read in the diff, long lines cut at about 400 to 500 characters.
9. The version simulation left out `tests/` and the platform trees (section 6), so T757 still runs the real check.
10. All tag-pipeline behaviour: nothing was published, and no CI job ran.

## 9. Review mode and references

Read-only; the artifact is the only output. No `docker`, push, merge, tag or release; no mutation or full suite; `tests/golden/held-out/` not opened; no `.env*`, credential or local settings file read; CWSO not read. Decision references: ADR-010, ADR-011, ADR-012. Requirements references: plan-145; no `requirements-vN.md` applies to this release audit.
