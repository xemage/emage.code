# Artifact: release-next-audit-v1.md

> Immutable once produced; revisions bump `<N>`.

# Release-level audit, `v11.0.0..develop`, for v12.0.0

- **Task:** T869 (plan-182 § Task Decomposition item 1). **Author:** tech-lead (read-only on source). **Date:** 2026-11-19.
- **Range:** `v11.0.0..9b9a31f0` (develop; tag `v11.0.0` on `3118924a`): 43 commits, 21 of them not merges, 22 merge requests (`!684` is the merge-back of `release/v11.0.0`, then `!686` to `!706`). 216 files (18479+, 1818-); outside `docs/`, `tests/` and the mirrors under `implementation/.<platform>/`, 50 files. The tree read is `2fec9af8` (`9b9a31f0` plus the plan-182 commit); `scripts/`, `implementation/` and `.gitlab-ci.yml` are identical in both (read here).
- **Based on:** `docs/tasks/task-T869.md`; `docs/plans/plan-182-next-release.md` (all, with Addendum 1); `docs/artifacts/release-v11-audit-v1.md` (structure); `docs/releases/v11.0.0.md`; `docs/artifacts/tracked-debt-register-v25.md` § 5, § 6.1 to § 6.3, § 7, and through it v17 to v24 § 6.2 and v17 § 5 (batch Q members); registers v13, v14, v16 by grep (SEC-T762-04, TL-T761-10); `CONTRIBUTING.md` § Versioning and § Cutting a release; skill `release-workflow` § Version Decision Flowchart; `docs/releases/_template.md` (headings); plans 163, 165, 167, 168, 173, 175, 177, 178, 180 § Outcome (by grep); `git diff -U0` of every changed file outside `docs/` and `tests/` except the generated agent files (two read in full: `tech-lead.md`, `security-engineer.md`, and the `task` map of `orchestrator.md`); `npm view` of `@modelcontextprotocol/server-filesystem` 1.0.0 and 2.4.0 (dependencies, engines; read 2026-11-19).
- **The user's words** (2026-11-19, verbatim): "release plan go"; plan "Approve (Recommended)"; version "v12.0.0, MAJOR (Recommended)"; probe tag "Yes, probe first (Recommended)".
- **Line numbers** are on `2fec9af8`. T872 bumps version markers on the release branch, so **T873 re-reads every cited line on `release/v12.0.0`** before writing it into the document (item 4).

## 1. Breaking and behaviour changes

| # | Change | Commit / MR | Citation | Reaches |
|---|---|---|---|---|
| B-1 | **Opencode agent files carry a `permission:` map instead of `tools:`.** Every generated `.opencode/agents/*.md` (28) now has `permission:` with `allow`/`deny` values; the generic `tools:` block (`read: true`, `execute: true`, …), which Opencode did not read as permissions, is gone. The MCP denies of T663 move into the same map. | `7d3d8b5a` (!693, plan-168, T836 to T844) | `implementation/platforms/opencode.json:14`; `implementation/platforms/_manifest.schema.json:51`; e.g. `.opencode/agents/security-engineer.md` frontmatter | Opencode targets at `--update` |
| B-2 | **Deny-only built-in keys.** An agent whose source does not hold the generic tool gets a deny: no `execute` → `bash: deny`; no `edit` → `edit: deny`; no `web` → `webfetch: deny`, `websearch: deny`; no `agent` → `task: deny`. These keys are never written as an allow. On v11.0.0 every generated agent had Opencode's defaults (shell, edit, web and delegation allowed). Counts (register v20 item 49, not re-counted here): 13 agents carry `bash: deny`, 26 `task: deny`. Fixes SEC-T840-01, which v11.0.0 shipped and nobody accepted (register v20 § 6.2 item 49). | `7d3d8b5a` (!693) | `implementation/platforms/opencode.json:18`; `implementation/scripts/sync.mjs` (deny-only keys, `validatePermissionKeys`) | Opencode targets |
| B-3 | **`task` allowlist for the two orchestrators.** `orchestrator` and `poc-orchestrator` get `task: {"*": deny, "<Name>": allow, …}`, 14 named subagents each, from their source `agents:` list. They can no longer launch Opencode's built-in agents (`build`, `plan`, `general`, `explore`, …) or an agent file of the user's own. The generator refuses built-in names, wildcards and any wider allow (SEC-T844-01). | `fca6018e` (!700, plan-175) | `implementation/platforms/opencode.json:19`; `implementation/scripts/sync.mjs:682` (`OPENCODE_BUILTIN_AGENTS`); `.opencode/agents/orchestrator.md` frontmatter | Opencode targets that delegate from an orchestrator |
| B-4 | **Token-directory denies for the 13 agents without `execute`:** `read` denied for `gitlab-mcp`, `gitlab-mcp/*`, `*/gitlab-mcp`, `*/gitlab-mcp/*` (T855, SEC-T842-02) and `external_directory` denied for `*/gitlab-mcp/*` (T861, SEC-T856-02). Not covered: a `grep` on a parent such as `/dev/shm`, a token at another name or path, a token linked or copied into a project (register v24 item 49 (d)). | `fca6018e` (!700), `f1378000` (!702) | `implementation/platforms/opencode.json:20-21` | Opencode targets; a non-default token path is not protected |
| B-5 | **Supported Opencode range: 1.0.224 to the latest 1.x, tested on 1.19.2; 2.x not supported.** 1.0.224 is the first release whose agent `permission` map takes wildcard keys and patterns. | `fca6018e` (!700, T855, SEC-T837-02) | `implementation/PREREQUISITES.md:66` | Opencode users on an older client |
| B-6 | **Manifest and generator contract (fork authors).** The manifest enum `tools` loses `object` and gains `permission`; five new Opencode-only keys (`permissionKeys`, `permissionDenyUnlessGranted`, `permissionTaskAllowFromAgents`, `permissionReadDenyUnlessGranted`, `permissionExternalDirectoryDenyUnlessGranted`); `sync.mjs` stops on a tool list that both grants and denies a key, a non-deny rule for a deny-only key, a `task` map other than `"*": deny` plus named allows, a built-in name or self in `agents:`, and `mcpAgentDenies` without `tools: "permission"`. A fork manifest with `tools: "object"` fails. | `7d3d8b5a`, `fca6018e`, `f1378000` | `implementation/platforms/_manifest.schema.json:51-58`; `implementation/scripts/sync.mjs` (the `throw new Error` lines added in the range) | fork authors |
| B-7 | **Brave pin 2.1.4 → 2.1.5** (SEC-T702-09 fixed; the first Brave release with SLSA provenance; seven high advisories of 2.1.4 retired). Stdio still forced. Reaches every generated MCP config (`.mcp.json`, `.vscode/mcp.json`, `.cline/mcp.json`, `.opencode/opencode.json`). | `1253084d` (!698, plan-173, T851) | `implementation/knowledge/mcp/servers.yaml:143` | targets using `brave` |
| B-8 | **`server-filesystem` pin 1.0.0 → 2.4.0** (SEC-T756-07; first line without `glob`, `minimatch` 11). By npm metadata, 2.4.0 depends on the MCP SDK v2 packages `@modelcontextprotocol/server ^2.3.1` and `@modelcontextprotocol/node ^2.1.1` instead of `@modelcontextprotocol/sdk ^1.31.0`, and **declares `engines.node >=24`**. The supported Node lines in `implementation/PREREQUISITES.md:4` and `:227` include Node 22. Whether `npx` runs it on Node 22 (npm warns on an engines mismatch unless `engine-strict` is set) is **(unverified)**; see TL-T869-01. Opt-in server; no agent holds it. | `9023641c` (!703, plan-177, T859) | `implementation/knowledge/mcp/servers.yaml:239-241`; `npm view @modelcontextprotocol/server-filesystem@2.4.0 dependencies engines` | targets using `filesystem` |
| B-9 | **CA-chain control hardened** (SEC-T768-01 to -03, T859): 14 compromised keys instead of 12 (the two rollover G3B keys); the fixtures are cross-checked before use (`sha256sum -c SHA256SUMS` in both jobs; counts of chains, roots and keys); the store scan reads every OpenSSL certificate PEM form and fails on any other `BEGIN` type; the node job also runs `--capath /etc/ssl/certs` when hashed entries exist. CI-only. | `9023641c` (!703) | `.gitlab-ci.yml:158-159`, `:175`, `:196`, `:203-209`; `scripts/check-ca-chains.sh` header | maintainers |
| B-10 | **`sync-wiki.py` refuses redirects** (SEC-T756-08): a 3xx is an `HTTPError` and the page counts as failed, so `PRIVATE-TOKEN` is never re-sent to another location. Repository tooling, not installed into targets (`install.sh` does not name it; grep). | `9023641c` (!703) | `scripts/sync-wiki.py:63-74`, `:85` | maintainers syncing the wiki |
| B-11 | **`install.sh` copies with `rsync --checksum`** (TD-T774-01, QA-T818-01 fixed): a changed file of equal size and same-second mtime is no longer skipped. Both copy paths. The cost is a checksum pass per tree. | `996fb2fc` (!688, plan-163, T828) | `scripts/install.sh:907-918` (comment), `:938`, `:988` | every target at `--update` |
| B-12 | **Memory build refuses more** (QA-T818-03, T828): `build.py` derives the id from the `origin` remote of `--own-repo-root` and exits 2 when `--project-id` is not exactly that id, or when there is no usable `origin` (any id is then refused). v11.0.0 refused only a malformed id. The install notice says so. | `996fb2fc` (!688) | `implementation/runtime/memory/build.py:64-85`, `:303-306`; `scripts/install.sh:1759-1760` | targets scripting the index build |
| B-13 | **context-retriever remote handling** (T831, T834, T835): a `git remote get-url` timeout (`_GIT_TIMEOUT_S`, 10 s) or any `SubprocessError` now yields `RemoteResolutionError` instead of an uncaught exception; a remote that is not valid UTF-8 is refused; an `@` in the derived `<org>/<repo>` is refused; error messages redact everything up to the last `@` and drop a query string or fragment; the slug is no longer repeated in its error. Effect: such a remote gives no project id, so the server does not start (default) or `retrieve` fails (`--index-dir`), as for other unusable remotes in v11.0.0 (`release-v11-audit-v1.md` B-6). | `8473bb26` (!690, plan-165), `48b95fac` (!692, plan-167) | `implementation/runtime/memory/context_retriever.py:110` (`_redacted`), `:141`, `:164` | targets using context-retriever |
| B-14 | **Pin-age rule** (SEC-T860-01, SEC-T867-01): an `npx` pin must be at least 7 days past its npm publication; `audit-mcp-pins.py age` (exit 1 for a young pin, exit 2 on a missing or unparseable time) with `--allow-young PACKAGE@VERSION:REASON`, which must name a current pin. Two recorded exceptions (B-7, B-8 pins). Release-author and maintainer rule; not installed into targets. | `9023641c` (!703), `8e11e14c` (!705, plan-180) | `scripts/audit-mcp-pins.py:98`, `:585`; `docs/wiki/mcp-pin-bump-checklist.md` § 1 (lines 13-15) | release author, pin bumpers |
| B-15 | **Release gate for the pins** (T852): the checklist § 4 gate runs `audit --audit-level high --signatures` and `provenance` with **no `--accept`**; a test requires every `--accept` to name a current pin. The Brave record v4 acceptance is history. | `1253084d` (!698) | `docs/wiki/mcp-pin-bump-checklist.md:42` (register v22 § 6.2) | release author |
| B-16 | **CI image review re-dated** `ci_images_reviewed_on: 2026-11-19` (fails from 2027-03-20); `python:3.12-alpine` pin not moved (amd64 manifest byte-identical); Alpine 3.24 ships `nodejs` 24.22.3-r0. No tag-job image change, so no `allowed_images` change. | `9023641c` (!703) | `.gitlab-ci.yml:20-25` | maintainers |
| B-17 | **Runner hardening steps** for the release-gate runner (`services_limit = 0`, lint, log, patching) in checklist § 3; the user applies them (SEC-T811-05, SEC-T860-02). | `9023641c`, `8e11e14c` | `docs/wiki/mcp-pin-bump-checklist.md:39` and after; register v25 § 7 | maintainers, the user |
| B-18 | **Shipped text:** `AGENTS.md` (GitLab grants paragraph, MCP paragraph: Opencode `bash: deny` since T841, `task: deny` since T843) and `implementation/PREREQUISITES.md` (Opencode range, token posture on Opencode). No file under `implementation/knowledge/agents/`, `skills/`, `commands/` or `rules/` changed in the range (diff stat). | `7d3d8b5a`, `fca6018e`, `f1378000` | `AGENTS.md`, `implementation/AGENTS.md`; `implementation/PREREQUISITES.md:66` and the token sections | targets (text) |

**Not reaching a target or author:** the registers v17 to v25, the evidence runs (plan-170, plan-178: `docs/artifacts/mcp-agent-denials-evidence-*`), the Brave upstream report draft (plan-172, `74b0dca8`), checkpoint-043 (`e3019a12`), tests.

## 2. Version finding

**v12.0.0 (MAJOR) is right.** By the flowchart of skill `release-workflow` ("Has any public API or contract changed in a breaking way? Yes → MAJOR"), each of these alone is a breaking contract change:
- **B-2, B-3:** a generated Opencode agent that could run a shell, edit, use the web or launch any agent in v11.0.0 can no longer do so, and the user cannot re-grant it from the project or global config (the agent's own rules come last; `AGENTS.md`, MCP paragraph). The orchestrators lose the built-in agents.
- **B-5:** Opencode clients below 1.0.224 are no longer supported.
- **B-6:** a fork manifest valid in v11.0.0 (`tools: "object"`) fails the schema and the generator.
- **B-12:** a `build.py` invocation that v11.0.0 accepted (a well-formed other id, or no `origin` remote) now exits 2.
- **B-8:** the filesystem server's declared Node floor rises to 24 (**(unverified)** in effect, TL-T869-01).

That B-2 to B-4 are security fixes does not make them backward compatible; semver as `CONTRIBUTING.md` and the skill state it has no exception for fixes that remove a capability. The precedent is v8.0.0 to v11.0.0 (MAJOR for removed capabilities). **No finding argues for MINOR.** Nothing differs from the user's choice, so no return to the user is needed on the version.

## 3. Migration items for the release document

| # | Item | Source | What a target keeps / must do |
|---|---|---|---|
| MI-1 | **Opencode: generated agents' permissions** (first, plan-182 T873) | B-1 to B-4; SEC-T840-01, SEC-T844-01, SEC-T842-02, SEC-T856-02; register v24 item 49 | After `--update`, `.opencode/agents/` is replaced as a tree (`AGENTS.md`: "replaces `.opencode/agents/` as a tree (agent files are not merged)"): every generated agent carries a `permission:` map. Agents without the grant lose shell, edit, web and `task`; the orchestrators can launch only their 14 named subagents. **Automation or habits that relied on, for example, a reviewer agent running a shell, or an orchestrator launching `general`/`build`, must change**: use a generated agent that holds the tool, or the user's own session. A global or project `permission` rule of the user (`allow` or `ask`) does not override an agent's own deny; only a source Opencode loads after the agent files can (`OPENCODE_CONFIG_CONTENT`, observed on 1.19.2; managed config by source reading) (`AGENTS.md`). Rollback is the v11.x installer, which writes the `tools:` form back. |
| MI-2 | **Opencode: the user's own agent files and the built-in agents (K-23 unchanged)** | K-23 (`docs/releases/v11.0.0.md:271`); B-3 | Unchanged: built-in agents (`build`, `plan`, `general`, `explore`, …) and agent files of the user's own get **none** of the new denies, no per-agent MCP deny and no global GitLab deny; only the server-level six Playwright denies apply. `build` keeps a shell and so the GitLab token (item 49 (b)). Changed: the generated orchestrators can no longer launch them (B-3); the user still can. An agent file of the user's own placed inside `.opencode/agents/` is removed by `--update` (tree replacement, `AGENTS.md`; existing behaviour, not new, but worth restating); keep own files where the installer does not write **(the location the document should name is unverified here)**. |
| MI-3 | **Opencode client version** | B-5 | Use opencode-ai 1.0.224 or later, 1.x; tested on 1.19.2; 2.x not supported. Below 1.0.224 the wildcard keys of the new map are not understood **(behaviour of an older client unverified)**. |
| MI-4 | **Fork authors of knowledge** | B-6 | Change `tools: "object"` to `tools: "permission"` in an own Opencode-like manifest; an agent source that both grants and denies a key, a `task` map other than `"*": deny` plus named allows, or a built-in or own name in `agents:` stops `sync.mjs`. |
| MI-5 | **MCP pins: Brave 2.1.5, `server-filesystem` 2.4.0** | B-7, B-8; SEC-T702-09, SEC-T756-07 | Nothing to do beyond `--update`: generated entries move; a user-owned entry of the same server is not touched (merge keeps user names). K-28 (Brave advisories) closes. For `filesystem`: 2.4.0 is built on the MCP SDK v2 and declares Node ≥ 24; **until T870 or the orchestrator settles TL-T869-01, the document must not claim it runs on Node 22**. |
| MI-6 | **Installer copy fixed; drop K-39 and M-6's check and `touch` workaround** | B-11; register v18 § 6.2 (item 45 retired); plan-163 § Outcome | The v12.0.0 installer, run from the new clone, already copies with `--checksum`, so the first `--update` repairs a stale equal-size file. K-39 closes; M-6's `grep`/`touch` workaround is dropped. The cost note (a checksum pass) may go in Changelog. |
| MI-7 | **Memory index build** | B-12; QA-T818-03 | A build script must pass exactly the id derived from `origin` of `--own-repo-root` (lower-case `<org>/<repo>`), and the repository must have an `origin` remote; otherwise exit 2. |
| MI-8 | **context-retriever remotes** | B-13; SEC-T829-01/-02, SEC-T832-01/-02, SEC-T835-01/-02 | No action for normal remotes. A remote with non-UTF-8 bytes, an `@` in its path, or a hanging `git` now gives a clean refusal (server does not start, or `retrieve` fails with `--index-dir`). Messages no longer show userinfo, query or fragment. |
| MI-9 | **Release authors and maintainers of this repository** (not for a target) | B-9, B-10, B-14 to B-17; items 35, 44, 46 | Both CA jobs pass on the release commit; the pin-age check and the no-`--accept` gate; `sync-wiki.py` fails on a redirect; runner steps of checklist § 3 (user). |

## 4. Register v25 § 6.2: the 33 numbers

Status: **due** (an action in a plan-182 task), **rule** (holds; checked in the named task), **open** (not closable in this release), **watch**. Text of the 26 rule items as `release-v11-audit-v1.md` § 3 lists (sources v11 to v16); items 43 to 49 from v17 to v24.

| # | Item (short) | Status | Who, task |
|---|---|---|---|
| 3 | `Issued at commit`, `Independent check` fields (`_template.md`) | due | release-manager T878 |
| 4 | TD-T723-01: cite current `install.sh` lines (re-read on the release branch; `:938`, `:988`, `:1759` moved by B-11, B-12) | due | release-manager T873; tech-lead T876 |
| 6 | D-T710-2 `CHANGELOG.md` under `[Unreleased]` | rule (`scripts/publish-release.py` has no diff in the range) | release-manager T873 |
| 7 | Gate rules of batches G, S, T (`verify-release-docs.py` has no diff) | rule | release-manager T873 |
| 9 | Conditions block (`release-manager.md:183`) | due | release-manager T873, T878 |
| 10 | SEC-T735-09: drop the template pointer sentence from `v12.0.0.md` before the independent check | due | release-manager T873/T878 |
| 11 | Independent checker `@tech-lead` | due | tech-lead, within T878 |
| 12 | Closed list after the check; hotfix eligibility | due | release-manager T878 |
| 14 | Watch `release-docs-gate` at the tag (`.gitlab-ci.yml` lines moved again by B-16/B-9: re-read) | watch | orchestrator T879; T874 probe |
| 15 | Tag jobs without `allow_failure` | rule | tech-lead T876 |
| 16 | A local gate run needs the parser | rule | release-manager T873; qa-engineer T875 |
| 17 | `ci/requirements-ci.txt` regeneration | n/a (`ci/` no diff) | — |
| 18 | A new CI job needs a `NOT_TAG_CONDITIONS` `if` (no new job in the range: the CA jobs gained steps, not jobs) | rule | tech-lead T876 |
| 19 | Digest bump vs `apk`/Python minor; header recipe | n/a unless T870 leads to a bump | devops-engineer, only if a bump task is created |
| 20 | UTF-8; strict `check-version-consistency.py` | due | release-manager T872; qa-engineer T875 |
| 21 | Allowlisted gate commands | watch | orchestrator T879 |
| 22 | No HTML other than comments in the document | due | release-manager T873 |
| 23 | Release script edit needs `RELEASE_COMMAND` | n/a (no change to the line) | — |
| 24 | A probe tag proves the gates only | rule (T874 within its limits) | orchestrator T874 |
| 25 | Gate limits (131072 chars, nesting 20) | due | release-manager T873 |
| 26 | `run-allowlisted.py` has no pin | n/a (no diff) | — |
| 27 | Placeholders | due | release-manager T873 |
| 28 | First-tag watch list `CONTRIBUTING.md`; `main` does not move between tag and tree check; plan-159 runner checks (TL-T819-03) | due | orchestrator T879 |
| 29 | No `docker` in briefs | rule | orchestrator, all tasks |
| 30 | No second verdict heading | due | release-manager T873/T878 |
| 35 | Both CA-chain jobs pass on the release commit | due | qa-engineer T875 reads; orchestrator T879 |
| 8 | npm step in a tag pipeline; musl lock | open **(unverified)**, watch | orchestrator T879 |
| 43 | **The acceptances end at each release:** SEC-T660-01 and SEC-T665-01 (accepted for v11.0.0 only) need a fix or a new acceptance for v12.0.0. Before the question: the Security Engineer's new dated review for v12.0.0 (ADR-016 D1/D2, O-B, O-C; T812 does not serve). Ask as SEC-T735-08 says: name v12.0.0, show the plan and a deadline ahead. If 2027-01-28 has passed at the tag, the document says so with date and release. The Conditions line attributes the swap and hibernation clause to the confirming review (TL-T821-01). SEC-T702-09 left the item (fixed, B-7). | due | security-engineer T871; then the orchestrator asks the user; release-manager T873 (Conditions lines); security-engineer T877; release-manager T878 |
| 44 | Release-gate runner: `allowed_images` changes with any tag-job digest (none in the range, B-16); every `v*` tag pipeline shows runner #59129270 for all three jobs, or SEC-T741-17 reopens | due | orchestrator T874 (probe), T879 |
| 46 | Probe tags (QA-T818-04; `publish-release.py` unchanged, so it still applies): delete `v12.0.0-gate.1` remote and local, or push only `refs/tags/<tag>`; `git ls-remote --tags origin` shows no `gate` ref before and after the tag push | due | orchestrator T874; the user deletes; orchestrator T879 checks |
| 47 | Dates (section 7); each acceptance shown to the user has its deadline ahead at the tag | due | orchestrator (question after T871); T879 date check |
| 48 | K-15 reopen condition (K-20, A-7, SEC-T658-02): stays in the document | due | release-manager T873; security-engineer T877 |
| 49 | **SEC-T660-01's Opencode scope** for the acceptance question: (a) the 15 agents with `execute`; (b) built-in agents and own agent files (K-23); (c) the orchestrators, through their named shell-holding subagents; (d) the 13 others covered for `read`/`grep`/`glob` on the default token directory, not for a parent-directory `grep`, a non-default path, or a token linked into a project. No harness fix for (a), (b). The question should say the v11.0.0 acceptance predated SEC-T840-01 (shipped in v11.0.0, never accepted, now fixed); I suggest the document names SEC-T840-01 as shipped-and-fixed | due | security-engineer T871 restates; orchestrator asks; release-manager T873; security-engineer T877 |

**Counts:** 26 rule items (3, 4, 6, 7, 9, 10, 11, 12, 14 to 30, 35), of which 5 are n/a in this range (17, 19, 23, 26 and, as a rule only, 24); item 8 open; items 43, 44, 46, 47, 48, 49 due. Total 33. **SEC-T665-01** has no Opencode-scope item; its line follows item 43 only.

## 5. Batch Q (5 ids): route in this release

Members (register v17 § 5, carried unchanged to v25): TD-T723-01, SEC-T735-08, SEC-T735-09, TL-T780-09, TL-T821-01.

| Id | Route |
|---|---|
| TD-T723-01 | T873 cites current `install.sh` lines, re-read on `release/v12.0.0` (item 4); T876 checks. Stays tracked (recurs). |
| SEC-T735-08 | The orchestrator's acceptance question after T871 names v12.0.0, shows the plan and a deadline ahead (item 43); T873 records it; T877 confirms. Stays tracked (register v17 ruling). |
| SEC-T735-09 | T873 drops the pointer sentence from `v12.0.0.md` before T878's independent check (item 10). |
| TL-T780-09 | T876 reviews the migration items by hand: the gate checks migration items only on `install.sh` lines with "Cursor", so MI-1 to MI-8 are unchecked by any script. No check is added (plan-182 § Not in scope). |
| TL-T821-01 | T873: SEC-T665-01's (and SEC-T660-01's) Conditions line attributes the swap and hibernation clause to the T871 review, not to "the plan as shown"; T878 checks. |

**User rulings needed from batch Q: none.** The brief and plan-182 § User actions name SEC-T762-04 and TL-T761-10 as needing the user's ruling. **That is stale:** both were ruled by the user on 2026-11-12 (ADR-015, plan-155), applied by T801 and **fixed** in register v16 (`tracked-debt-register-v16.md:22`, `:82`); they left batch Q then and are not in v17 to v25 § 5. The only user decision this release needs on findings is the SEC-T660-01/SEC-T665-01 acceptance (item 43), already in plan-182 after T871. The user action SEC-T811-05 (runner log check) is in batch X, not Q.

## 6. Findings of this audit

- **TL-T869-01 (LOW, tracked; needs routing before T873):** `@modelcontextprotocol/server-filesystem@2.4.0` declares `engines.node >=24` (npm metadata, 2026-11-19), while `implementation/PREREQUISITES.md:4` supports Node 22.23.5 and later. Route: T870 records the engines field of every `npx` pin; the orchestrator decides between a `PREREQUISITES.md`/document note ("the `filesystem` server needs Node 24") and nothing, if T870 shows it runs on 22. It is not a blocker: the server is opt-in and no agent holds it.
- **TL-T869-02 (info):** plan-182 § User actions and the T869 brief treat SEC-T762-04 and TL-T761-10 as open for the user; they are fixed (section 5). The orchestrator may drop that user action.
- **No change found blocks the release.**

## 7. Dates

- **2027-01-28:** review of SEC-T660-01 and SEC-T665-01 and the GitLab token's renewal. The deadline shown in the acceptance question must still be ahead at the tag; **the tag must come before it**, or the user decides again and the document states the passed date (item 43, 47).
- **2027-01-29:** TD-T697-07 ends (MEDIUM, not shipped, not accepted). The document does not list it as accepted.
- **2027-03-20:** the CI image review fails (`ci_images_reviewed_on: 2026-11-19`, `.gitlab-ci.yml:25`; 2027-03-19 the last passing day). A tag pipeline on or after that date fails `test_ci_hash_pins`.
- **Young-pin exceptions:** Brave 2.1.5 (published 2026-11-17) is 7 days old about **2026-11-24**; `server-filesystem` 2.4.0 (published 2026-11-18) about **2026-11-25**. From then `age` passes with no `--allow-young`. Caveat SEC-T867-02: the check counts UTC calendar days, so it may pass up to almost a day early. T870 runs `age` without exceptions if it runs after both dates, else with the two recorded ones; any pin bump voids its exception.

## 8. What the release document must not assume

1. That the Opencode denies are observed refusing a live call: the resolved rule lists are observed on 1.19.2 (evidence v2 to v4), a refused call and a refused launch are not (K-20); the mapping of `bash`/`edit`/`webfetch`/`websearch`/`task` at call time and the 23 agents not run rest on the generator **(unverified live)**.
2. That the new denies reach Opencode's built-in agents or the user's own agent files (they do not; K-23), or that the token directory is protected at a non-default path or against a parent-directory `grep` (item 49 (d)).
3. That a user's global or project rule can re-grant a denied tool to a generated agent (it cannot; only `OPENCODE_CONFIG_CONTENT` or managed config).
4. That Opencode below 1.0.224 or 2.x works.
5. That `server-filesystem` 2.4.0 runs on Node 22 (TL-T869-01), or that any Node minimum is enforced by the installer **(unverified; nothing in the range checks it)**.
6. That targets receive `scripts/audit-mcp-pins.py`, `scripts/sync-wiki.py`, `scripts/check-ca-chains.sh`, `.gitlab-ci.yml`, `docs/wiki/` or `docs/releases/_template.md` (none is named in `install.sh`; grep, not an install).
7. That SEC-T660-01/SEC-T665-01 are carried over from v11.0.0 (each needs the new acceptance after T871), or that SEC-T762-04/TL-T761-10 are open.
8. That the hardened runner config (`services_limit = 0`) has run a tag job: only T874 and the real tag show it; SEC-T811-05's log check rests on the user's report.
9. That `main` is an ancestor of `develop` (it is not: plan-182 § State at writing).
10. That `install.sh`'s Pi/Gemini pointers name the new document: they still name `docs/releases/v11.0.0.md`, correctly.

## 9. Method and limits

- Read: the inputs above, by section; diffs by `git diff -U0`; line numbers by `grep -n` on `2fec9af8`. Not read: the 28 generated agent files beyond the three named, the mirrors, `tests/`, `docs/wiki/mcp-servers.md` diff, the full plan bodies (Outcomes by grep). No test, install or pipeline was run beyond the three acceptance checks. The agent counts (13/15/26) are register v20's, not re-counted.
- MR numbers from the merge commits' bodies in the range.
- Review mode: read-only; no source modified; only this artifact created.
