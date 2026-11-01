# Artifact: release-v9-audit-v1.md

> Immutable once produced; a revision is `release-v9-audit-v2.md`. Release-level audit of `v8.0.0..origin/develop` for v9.0.0 (task T700, plan-124 wave 1). It feeds T704 (version markers and stale lines) and T705 (`docs/releases/v9.0.0.md`).

**Based on:** `docs/tasks/task-T700.md`; `docs/plans/plan-124-release-v9.md` (approved by the user on 2026-11-01); `docs/decisions/ADR-010-drop-cursor-platform-support.md` (Appendix A); `docs/tasks/task-T679.md` section 3a; `docs/artifacts/tracked-debt-register-v3.md` (sections 3.2 to 3.6, 5, 6 and 7; decision D-13); `docs/releases/v8.0.0.md` (Install, Migration Guide M-1 to M-9, Known Issues K-1 to K-21); `docs/releases/_template.md`; `docs/artifacts/release-v8-audit-v2.md` (format model); `docs/checkpoints/checkpoint-039-post-v8-follow-ups-complete.md`; `docs/tasks/completed-tasks.md` rows T652 and T661 to T699; `git log v8.0.0..origin/develop`.

**Author / mode:** Tech Lead, review mode (read-only). Only this file was written. No source, script, version marker, CHANGELOG, ledger row or brief status line was changed. Commands run were read-only (`git`, `grep`, `check-version-consistency.py`, `check-maturity.py`, `scorecard.py --check`) plus one scratch copy (a `git archive` of this worktree's HEAD with `tests/golden/held-out` excluded) in the session scratchpad, used only to simulate the version bump.

**Code state audited:** worktree `agent/tech-lead/T700` at `3394229a` (plan-124 commit) on top of `origin/develop` = `8cc091d3`. `v8.0.0` (tag commit `6630dd0e`) is an ancestor of `origin/develop`; `origin/main` (`8f829a6b`) has the same tree as the tag and one merge commit not in `develop`.

**Basis marker:** **(V)** verified (file read, diff read or command run; the evidence names which). **(I)** inferred (reason given). **(unverified)** not read, not run, or not checkable from here.

---

## 1. Coverage and classification

### 1.1 Coverage

| Item | Value |
|---|---|
| Range | `v8.0.0..origin/develop`: 78 commits, 40 non-merge, 38 merges (V, `git rev-list --count`, `git log --no-merges`) |
| Plus | `3394229a` (plan-124 and the briefs T700 to T711), not yet on `develop`; `v8.0.0..HEAD` is 41 non-merge commits (V) |
| Tasks closed in range | T652 (archived only) and T661 to T699: 40 task ids, each with a row in `completed-tasks.md` (V, loop over T661..T699) |
| Tasks closed before the tag | T650, T651 and T653 to T660 are in `v8.0.0` (V, `git log v8.0.0 --grep`); not classified here |
| Active ledger | 12 rows (T700 to T711, created by `3394229a`) (V) |

### 1.2 Classes

- **Breaking**: something that worked under v8.0.0 stops working, or is removed, unless the adopter acts.
- **Behaviour**: what an installed project does or what its agents are told changes, but nothing that worked stops working without a stated replacement.
- **Internal**: repository-only (tests, CI, release tooling, decisions, artifacts, ledger, documentation corrections, root refresh) or another repository.

**Counts (by task id): breaking 8, behaviour 9, internal 23 (40).**

### 1.3 Task classification

| Task | Commit(s) | Class | What changed for an adopter | Evidence |
|---|---|---|---|---|
| T652 | `13b813f7` | internal | Archive of the v8.0.0 publish row, checkpoint-038 | ledger only (V) |
| T661 | `57f98f89` | internal | ADR-010 decision (effect through T662, T678, T679) | `docs/decisions/ADR-010-drop-cursor-platform-support.md` (V) |
| **T662** | `81f7db11` | **breaking** | Cursor removed: `--platform cursor` exits 1 before writing; `--platform all` no longer writes `.cursor/`; MCP format value `cursor` renamed `pi`; pack schema lists six platforms | `scripts/install.sh:20` (`SUPPORTED_PLATFORMS`), `:190-196` (error, exit 1), `:1285-1301` (notice); `implementation/scripts/sync.mjs:843` (`Unknown MCP format`); `implementation/registry/package.schema.json:23` (enum without `cursor`) (V) |
| **T663** | `ad377d86` | **breaking** (Opencode only) | Every generated Opencode agent file gets `false` entries: the six unsafe Playwright tools for every agent, and `<server>_*: false` for each non-exempt server the agent holds no tool of; `filesystem`, `git`, `supabase` are denied to every generated agent | `implementation/.opencode/agents/backend-developer.md:10,12,23`; `implementation/knowledge/mcp/servers.yaml:49,79,117` (`denyUnlessGranted`); `AGENTS.md:118` (V) |
| T664 | `57f98f89` | internal | Token-scope design and the user's option D (implemented by T665) | ledger row T664 (V) |
| **T665** | `3fd16315` | **breaking** (narrow) | `gitlab` entry: `GITLAB_PERMISSION_MODE=modify` (delete and teardown tools refused for every client session, the user's own included), `GITLAB_PERSONAL_ACCESS_TOKEN_FILE` file mode, `${VAR:-}` on Claude Code, Gemini placeholder `${env:VAR}` to `${VAR}`; new `scripts/check-gitlab-token.py` | `implementation/knowledge/mcp/servers.yaml:98-101`; `implementation/PREREQUISITES.md:196,210-215` (V) |
| **T666** | `58149964` | **breaking** | `orchestrator` (16) and `poc-orchestrator` (8) hold named GitLab tools instead of the whole server: no merge, approve, tag, release, pipeline control | `implementation/knowledge/agents/orchestrator.md:4`, `poc-orchestrator.md:4` (V; v8.0.0 had `mcp__gitlab`) |
| **T667** | `58149964` | **breaking** | `devops-engineer` (11), `release-manager` (17), `poc-devops-engineer` (6) likewise; no agent holds the whole `gitlab` server | `devops-engineer.md:4`, `release-manager.md:4`, `poc-devops-engineer.md:4` under `implementation/knowledge/agents/` (V, counted) |
| T668 | `bc412c88` | internal | Golden realignment under grant G-2 (two `tracked_defect` cases now pass) | `scorecard.py --check`: 34 cases, 30 pass, 0 regressions (V) |
| T669 | `bc412c88` | internal | Evaluator baseline v22 | ledger row T669 (V) |
| T670 | `bc412c88` | internal | `orchestrator` promoted to `stable` (metadata; closes v8 K-1) | `implementation/knowledge/agents/orchestrator.md:6`; `check-maturity.py`: 80 components, agents 28 stable (V) |
| T671 | `57f98f89` | internal | Tracked-debt register v1 | artifact (V) |
| T672 | `03a1c572` | behaviour | A plain install over an existing MCP config MERGES (as `--update`); JSON validated before any write; atomic writes; swap-based tree replacement; `--dry-run` writes nothing; ledger merge keeps a `.bak` | `scripts/install.sh:1334-1345` (validate first), `:1395-1397` (merge in every mode); `scripts/merge-mcp-json.py:322`, `:481-484` (no-sidecar note); `scripts/merge-task-docs.py:188-192` (V) |
| T673 | `5369c41b` | internal | Grant-pin and doc-anchor tests | tests only (V, `git show --stat`) |
| T674 | `f90c6e5d` | internal | Documentation corrections; new `docs/wiki/severity-and-grade-scales.md` (closes v8 K-11) | file exists (V) |
| T675 | `acd26112` | behaviour | Installed `security-audit` runtime refuses secret-bearing paths (`.env*`, keys, credential files, `.git`) and accepts git worktree roots; CI images digest-pinned; release tooling hardened; changelog entry placed below the intro (closes v8 K-12) | `implementation/runtime/security/validation.py:30` (`SENSITIVE_NAME_GLOBS`), `:49-69`, `:102`; `scripts/publish-release.py:402-403` (V) |
| **T676** | `44c15b49` | **breaking** | The `github` MCP server (GitHub container, `GITHUB_PERSONAL_ACCESS_TOKEN`) removed from `servers.yaml` and every generated config; Docker no longer launches any shipped server; Playwright `--blocked-origins` 22 to 39 entries; hash locks for the two Python MCP runtimes; CI Python hash-locked; `scripts/audit-mcp-pins.py` | `servers.yaml` has no `github` server (V, 16 servers listed); `docs/wiki/mcp-servers.md:317` (item 8); `implementation/runtime/security/requirements-mcp-server.txt` (httpx2 floor, lock file named); blocked-origins counted in `servers.yaml` at `v8.0.0` and now (V) |
| T677 | `3e2fbfbe` | internal | Function-size refactor, no behaviour change (generated files hash-identical per the row) | ledger row T677 (V); hash identity (unverified, from the row) |
| T678 | `c7a6cfc0` | internal | Documentation half of ADR-010: Cursor removed from live docs, knowledge text and templates; README one-line notice | `README.md:64`; `docs/releases/_template.md:21-29` (no Cursor row) (V) |
| T679 | `ee6adf18` | internal | Root refresh after the Cursor removal (S3) | ledger row T679 (V) |
| **T680** | `a8f3734c` | **breaking** (Pi only) | `.pi/mcp.json`: `${env:X}` to `${X}`; the optional GitLab token variables left out (read from Pi's environment); `hindsight` and `cwso` no longer generated for Pi and pruned by the update; a literal credential is kept with a WARNING; retired `${env:` keys dropped with a note | `servers.yaml:162,170` (`skipFormats: [pi]`), `:98-99` (`optional: true`); `scripts/install.sh:1535` (`--drop-env-form`); `scripts/merge-mcp-json.py:347-348,360`; `implementation/PREREQUISITES.md:212` (V) |
| T681 | `25c749a6` | internal | Decision DEC-T681-1 (option A: shared Developer-level token, exposure sentence, Reporter profile) | ledger row T681 (V) |
| T682 | `58c38c8e` | behaviour | Installer residuals: a stale `<tree>.emage-old.<pid>` / `.emage-new.<pid>` sibling stops the next run with a restore hint (nothing written); overlap and `extras.from` checks | `scripts/install.sh:572-596` (V) |
| T683 | `cf46f222` | internal | Doc-assertion tests | tests only (V) |
| T684 | `f662bb4e` | behaviour | Stale-swap hint shown byte-safe; case-folded overlap check; `merge-task-docs.py` plan-then-write | `scripts/install.sh:566-571` (comment), `:581-584` (V) |
| T685 | `eec8a1cc` | internal | Brave acceptance scoped to `package@version` (`brave-audit-acceptance-v2.md`); `scripts/check-release-tag-tree.py` in the tag pipeline; GitHub-removal sentences | `.gitlab-ci.yml:211`; `docs/artifacts/brave-audit-acceptance-v2.md:11` (V) |
| T686 | `9d47b384` | internal (maintainers) | Release job authenticates with `CI_JOB_TOKEN` (`JOB-TOKEN` header); `WIKI_TOKEN` only for `wiki-sync`; allowlisted child environment | `.gitlab-ci.yml:222,227`; `scripts/publish-release.py:92-95,206`; `CONTRIBUTING.md:234-279` (V) |
| T687 | `8dd665d5` | internal | Tracked-debt register v2 | artifact (V) |
| **T688** | `d89f75f2` | **breaking** (narrow) | `qa-engineer` loses `get_pipeline_job_output` (20 to 19 GitLab tools) and must not read raw CI traces by any route | `implementation/knowledge/agents/qa-engineer.md:4` (19 counted), `:77`, `:213` (V) |
| T689 | `f2b1e9ef` | behaviour | Documented default token file in memory (`$XDG_RUNTIME_DIR`, else `/dev/shm`); a persistent-disk file only when encrypted; `check-gitlab-token.py` warns (exit 1) on a token file on a persistent file system | `implementation/PREREQUISITES.md:139-165`; `scripts/check-gitlab-token.py:21-26,234,238` (V) |
| T690 | `b2c7170b` | behaviour | GitHub Copilot `.vscode/mcp.json` gains `security-audit` and `poc-security-audit` (`python3 -m implementation.runtime.security...`, `cwd: ${workspaceFolder}`); closes v8 K-3 | `implementation/.vscode/mcp.json:64,72`; `servers.yaml:209-211,226-229`; `docs/wiki/mcp-servers.md:251-255` (V; v8.0.0 had 7 Copilot servers, now 9) |
| T691 | `6c61c5e3` | internal | Ruling on P112-P41-O1 (option A+) | artifact (V) |
| T692 | `d03bee97` | behaviour | `TECHNICAL-DEBT.md` lives in the PoC root next to `POC-DEBT-SCORECARD.md` | `implementation/knowledge/instructions/poc-guidelines.md:154-155` (V) |
| T693 | `300fd1ed` | behaviour | `release-manager` Release Gate Policy item 5: an independent check of the self-authored release document, recorded with its commit; later edits other than the verdict make it stale | `implementation/knowledge/agents/release-manager.md:46` (V) |
| T694 | `529fc7ff` | behaviour (repository scripts, not installed) | CWSO scripts and `implementation/runtime/cwso/mcp_client.py` take the JWT secret from `CWSO_JWT_SECRET` or an explicit file only; no fallback to a sibling secret file | `git show 529fc7ff -- implementation/runtime/cwso/mcp_client.py` (V); `runtime/cwso` and `implementation/scripts/` are not copied into targets: `scripts/install.sh:1484-1500` copies `runtime/memory`, `runtime/security`, `runtime/handoff` (V) |
| T695 | (none in this repo) | internal | CWSO repository work; only its review artifact is here (`529fc7ff`) | ledger row T695 (V) |
| T696 | `d60c6e1d` (brief) | internal | CWSO repository work | ledger row T696 (V) |
| T697 | `d4f1af17` | internal | Tracked-debt register v3 | artifact (V) |
| T698 | `7e1bdd96` | internal | Checkpoint 039 | checkpoint (V) |
| T699 | `ff4684c9` | internal | Root refresh 21 | ledger row T699 (V) |

### 1.4 Commits without a task of their own (all internal)

`c5bc9e42` (plan-123), `d20fa703` (T661 to T677 briefs), `8f512713` (T689 to T692 briefs), `f23f0204` and `d60c6e1d` (T694 to T696 briefs, T689 live-check results), `d2b77fd7` (T697 to T699 briefs), `d8ffe41c` (security review of T697 to T699). All touch only `docs/tasks/`, `docs/plans/`, `docs/checkpoints/` or `docs/artifacts/` (V, `git show --stat`).

---

## 2. Migration items for `docs/releases/v9.0.0.md` (draft; the release manager owns the wording)

Order for adopters: read M-1 to M-4 **before** running `scripts/install.sh --update` (M-2 and M-4 need action first); M-5 to M-10 apply after it. Items for maintainers of the source repository are in M-11.

**Coverage check.** task-T679 §3a: SEC-T678-03 and SEC-T662-01 in M-1, T676 in M-2, T672 in M-3, T680 in M-4. D-13: T689 in M-5, T688 in M-6, T690 (SEV-T690-07) in M-8, T693 in M-9. Added by this audit: T665 (permission mode) in M-5, T666/T667 in M-6, T663 in M-7.

### M-1. Cursor is no longer supported (ADR-010, T662, T678, T679; SEC-T662-01, SEC-T678-03). Any time; nothing is required before `--update`.

- What changed: `scripts/install.sh --platform cursor` exits 1 before writing anything and names this item (`scripts/install.sh:190-196`); `--platform all` no longer installs `.cursor/`. The `cursor` platform manifest, the generated `.cursor/` tree and the `cursor` MCP format value are removed. `--update` and `--projections-only` no longer touch `.cursor/`: files you added there are no longer deleted (before, they were).
- The installer prints a warning when it finds a harness-generated `.cursor/` **during `--update` or `--projections-only`** (both set the update flag: `scripts/install.sh:365`, `:1306-1307`). A plain install prints nothing about it (V, code reading). Appendix A says "while it finds"; say "on `--update`".
- A leftover `.cursor/` is frozen (SEC-T678-03): it is no longer updated, pruned or checked, its MCP versions are not bumped, its Playwright hardening is not updated, and **its agents are not tool-restricted: every agent there can call every tool of every configured server**.
- If you do not use Cursor with this harness: if you added nothing of your own to `.cursor/`, delete the folder (`rm -r .cursor`). Otherwise delete the paths listed under `files` in `.cursor/.generated-manifest.json` except `mcp.json`, then the manifest and any empty folders; in `.cursor/mcp.json` remove the server entries named under `generatorOwnedKeys` in `.cursor/mcp.json.provenance.json` and keep your own (or delete the file if nothing in it is yours); then delete the sidecar.
- If you keep the folder, **remove these entries now** if present: `filesystem` when it runs `npx -y @anthropic/mcp-filesystem` (v5.0.0 to v7.0.1 installs; v8.0.0 release notes M-9), and the keys `e2b`, `redis`, `figma` and `notion` (v5.0.0 to v6.9.0 installs). Edit `.cursor/mcp.json` by hand.
- `--force-prune-keys`: the option belongs to `scripts/merge-mcp-json.py` and still exists in v9.0.0 (`scripts/merge-mcp-json.py:418`); what exists only at the `v8.0.0` tag is the generated Cursor source file `implementation/.cursor/mcp.json` that the v8.0.0 M-8/M-9 commands name as `--source`. Recommend hand editing: a run with the v8.0.0 Cursor file as `--source` also merges every v8.0.0 Cursor entry (including `github`) into your file, and `--force-prune-keys filesystem` is refused because `filesystem` is in that source (`scripts/merge-mcp-json.py:455-469`: only dest-only keys; (I) from code reading, not run). See TL-T700-01 and TL-T700-02.
- Cursor reads a root `AGENTS.md` (Cursor documentation, checked 2026-10-16 per ADR-010; not re-checked); the installer still writes `AGENTS.md`. No Cursor-specific agents, commands, rules or skills ship.
- Automation: a script running `--platform cursor` fails with exit 1; one that runs `--platform all` and reads `.cursor/` must change.
- Rollback: the v8.x installer with `--update` recreates `.cursor/` and replaces it wholesale (your files in it are deleted by that older installer).
- Pack authors: `supportedPlatforms` in `pack.json` no longer accepts `cursor` (`implementation/registry/package.schema.json:23`). Maintainers: a platform manifest with `mcp.format: "cursor"` now fails with `Unknown MCP format` (`implementation/scripts/sync.mjs:843`); Pi uses `pi`.
- Known Issue to add: "A Cursor install left in a project is frozen and is not pruned (M-1)."

### M-2. The `github` MCP server is removed (T676, T685; SEC-T676-13). **Before `--update`** if you use it.

- What changed: the shipped `github` entry (container `ghcr.io/github/github-mcp-server`, `GITHUB_PERSONAL_ACCESS_TOKEN`) is gone from `servers.yaml` and every generated config; Docker no longer launches any shipped server (the Docker prerequisite was removed from `implementation/PREREQUISITES.md` in `44c15b49`).
- Before `--update`: copy the `github` entry from your installed config under your own server name (for example `github-mine`). The update prunes the generator-owned name `github` through the provenance sidecar.
- Without a sidecar nothing is pruned and the entry stays: delete it by hand, or run once per file `python3 scripts/merge-mcp-json.py --source <generated file> --dest <your file> --force-prune-keys github` (generated files as in the v8.0.0 M-8 list, minus Cursor) (`docs/wiki/mcp-servers.md:317`).
- Required sentences (T685): "A GitHub server that you keep under your own name is outside every generated denial on Opencode and Gemini CLI (those denials name the generated servers only), so give it a fine-grained, read-only token. If you no longer use a GitHub server, revoke or unset `GITHUB_PERSONAL_ACCESS_TOKEN`."
- The harness ships no GitHub tooling any more; your own session keeps what you configured.

### M-3. A plain install merges existing configs; new file names and refusals (T672, T682, T684; SEC-T672-06).

- What changed: `scripts/install.sh` without `--update` over an existing MCP or settings config now MERGES it (as `--update` does) instead of overwriting it (`scripts/install.sh:1395-1397`). Every existing config is validated as JSON before the first write; an invalid one stops the run, naming the file, with nothing written (`:1334-1345`). Before, a plain install overwrote it.
- With no provenance sidecar the merge prints (`scripts/merge-mcp-json.py:481-484`): `merge-mcp-json: note: <dest>: there is no provenance sidecar at <old-sidecar>, so no retired generator entry could be pruned; kept your server(s) a, b, which the generated config does not contain. If one is a retired generator entry, remove it by hand or run scripts/merge-mcp-json.py with --force-prune-keys <name>.`
- New on-disk names: `.<name>.<random>.tmp` (atomic writes, `scripts/merge-mcp-json.py:322`, `scripts/merge-task-docs.py:172`), `<ledger>.bak` then `.bak.2`, `.bak.3` (`merge-task-docs.py:188-192`), `<tree>.emage-new.<pid>` and `<tree>.emage-old.<pid>` (tree swap, `scripts/install.sh:1117-1118`).
- A leftover `.emage-old.<pid>` or `.emage-new.<pid>` from an interrupted run stops the next run with `error: a previous update of this target was interrupted ...` and a restore hint; nothing is written or removed (`scripts/install.sh:572-596`). If the managed folder is missing, the `.emage-old` sibling is your only copy: restore it with the printed `mv` line.
- An option value that starts with `-` (for example `--target -x`) is refused; write `./-x` (`scripts/install.sh:156-158`). `--dry-run` creates nothing (T672 row; not re-run).

### M-4. Pi: placeholder form, GitLab variables, `hindsight` and `cwso` (T680). **Before `--update`** if you edited `hindsight` or `cwso` in `.pi/mcp.json`.

- Before `--update`: copy a hand-edited `hindsight` or `cwso` entry to another name; the update removes those two names from `.pi/mcp.json` ("pruned the retired generator server"). Pi 1.x rejects a templated URL, so add your own entry with a literal URL if you need them (`servers.yaml:162,170`; `implementation/PREREQUISITES.md:212`).
- After: every placeholder changes from `${env:X}` to `${X}` (Pi 0.99.0 to 1.4.0 kept `${env:X}` as literal text, so those entries never worked); the `gitlab` entry no longer carries `GITLAB_PERSONAL_ACCESS_TOKEN` or `GITLAB_PERSONAL_ACCESS_TOKEN_FILE`: export the one you use in Pi's environment (Pi fails the whole server on an unset or empty variable).
- The update drops retired `${env:` keys with a note ("dropped the retired `${env:` entry") and keeps any other key of yours. A key with a credential-like name and a literal value prints `WARNING: ... holds a literal value; remove it from the file and revoke the token` (names only, `scripts/merge-mcp-json.py:360`): remove it and revoke that token.

### M-5. GitLab entry: permission mode, token file in memory (T665, T689). After `--update`.

- The generated `gitlab` entry sets `GITLAB_PERMISSION_MODE=modify` (`servers.yaml:101`): the pinned server refuses every delete tool and teardown tools such as `cancel_pipeline` **in every session of that client, your own included** (`implementation/PREREQUISITES.md:196`; the teardown list is from the server README on main, not matched to 2.2.5 (unverified)). To lift it, edit your client config; `--update` writes the generated value back.
- The entry gains `GITLAB_PERSONAL_ACCESS_TOKEN_FILE`; on Claude Code both token placeholders become `${VAR:-}` (leave them); on Gemini CLI placeholders change from `${env:VAR}` to `${VAR}`. Claude Code asks you to approve the changed project server again (`PREREQUISITES.md:212`).
- Nothing breaks if you do nothing: an exported `GITLAB_PERSONAL_ACCESS_TOKEN` keeps working (`PREREQUISITES.md:213`). It is a plaintext secret at rest if it sits in a shell profile or `.env` file (`PREREQUISITES.md:160`); the wording of migration step 2 is being corrected by T701 (SEC-T689-03), and decision D-11 on environment mode is open (section 6).
- To adopt file mode (recommended): write the token to a mode 0600 file **in memory** (`$XDG_RUNTIME_DIR`, else `/dev/shm`, or filled from a keyring or encrypted store), outside every project; export the path in `GITLAB_PERSONAL_ACCESS_TOKEN_FILE`; remove the old export; run `python3 scripts/check-gitlab-token.py` from an emage.code checkout; revoke the old, broader token (`PREREQUISITES.md:139-165,214`). A persistent-disk file is acceptable only on a disk you encrypted.
- `check-gitlab-token.py` now exits 1 with a warning for a token file on a persistent file system (`scripts/check-gitlab-token.py:238`): automation that treats exit 1 as failure fails for a disk-resident file. Without a readable mount table it skips that check and does not warn (SEC-T689-04).
- After changing the token or the file, restart the client; on VS Code Remote SSH or dev containers restart the VS Code server (`PREREQUISITES.md:164`; observed on Claude Code in VS Code Remote SSH only).
- If you use `GITLAB_TOKEN` with `glab`: empty `glab`'s own stored login and revoke its OAuth authorization (user action A-10, register v3 6.1).

### M-6. GitLab grants of the seven holder roles (T666, T667, T688). After `--update`.

- No agent holds the whole `gitlab` server. The named sets: `scrum-master` 24, `qa-engineer` 19 (was 20), `orchestrator` 16, `release-manager` 17, `devops-engineer` 11, `poc-orchestrator` 8, `poc-devops-engineer` 6 (`implementation/knowledge/agents/<role>.md:4`, counted (V)). `create_merge_request` is the only write of the three that hold it; no agent holds merge, approve, push, file write, delete, branch, tag or release creation, pipeline trigger, retry or cancel, CI variables or raw job output.
- `orchestrator`, `poc-orchestrator`, `devops-engineer`, `release-manager` and `poc-devops-engineer` held the whole server in v8.0.0. A workflow in which one of them merged, tagged, released or ran pipelines through MCP must move to the top-level session or the user.
- `qa-engineer` loses `get_pipeline_job_output` and must not fetch raw CI job traces by any route (MCP, `glab ci trace`, `curl`, a `/raw` URL, the browser); bug reports carry a user-checked log excerpt (`qa-engineer.md:77,213`).
- This narrows tool lists; it is not a credential boundary: six of the seven roles hold `execute`, and a shell holding the token can call the API (`AGENTS.md:116`). Existing installs keep the old grants until `--update`.

### M-7. Opencode: per-agent denies in the generated agent files (T663). After `--update`.

- Each generated `.opencode/agents/*.md` gets `false` entries: the six unsafe Playwright tools for every agent, and `<server>_*: false` for each server marked `denyUnlessGranted` that the agent holds no tool of (`gitlab`, `playwright`, `memory`, `sequential-thinking`, `security-audit`, `poc-security-audit`, `context-retriever`, `filesystem`, `git`, `supabase`). No agent lists `filesystem`, `git` or `supabase`, so generated agents can no longer call them on Opencode. Exempt and still reachable: `brave`, `context7`, `hindsight`, `cwso`, `hf-mcp-server`, `toolradar` (`implementation/.opencode/agents/backend-developer.md:10,12,23`; `AGENTS.md:118`).
- Not covered (user decision 2026-10-16, "No, document the gap only"): Opencode's built-in agents and agent files of your own.
- A global `ask` or `deny` of yours on a tool that an agent holds is overridden for that agent; only `OPENCODE_CONFIG_CONTENT` (observed) or a managed configuration (source reading) is applied later (`AGENTS.md:118`).
- `.opencode/agents/` is replaced as a tree by `--update`; edits there are lost.

### M-8. GitHub Copilot: two code-launching servers added (T690; SEV-T690-07, D-13). After `--update`, silently.

- `--update` adds `security-audit` and `poc-security-audit` to `.vscode/mcp.json`: `python3 -m implementation.runtime.security.audit_server` and `... poc_audit_server --allowed-root .`, each with `"cwd": "${workspaceFolder}"`, no env, no secret (`implementation/.vscode/mcp.json:64,72`). The installer prints nothing about it (SEV-T690-07).
- They run Python code from the workspace (`implementation/runtime/security/`, copied by the installer); a hostile branch can change that code (SEV-T690-02, the same exposure as on the other five platforms). They need `mcp==2.2.0` in the `python3` VS Code starts (`pip install --require-hashes -r implementation/runtime/security/requirements-mcp-server.lock.txt` in a virtual environment).
- VS Code's Workspace Trust and tool-approval prompts were not observed (unverified, `docs/wiki/mcp-servers.md:253`). Both names are generator-owned: a hand removal is undone by the next update, and an entry of your own with one of these names is overwritten in place (I, from the provenance merge rules, not run).
- The Copilot agents `security-engineer` and `poc-security-engineer` already held the tools; the PoC security scan can now complete on Copilot (v8 K-3 closed).

### M-9. Release gate input (T693). For teams that use `release-manager`.

- A `PASS` or `CONDITIONAL_PASS` release verdict now needs a row in the Gate Inputs table naming who checked the release document independently (the `tech-lead` review by area or the top-level session) and the commit covered. After that check only the `## RELEASE VERDICT` section and the `Release:` line under `## Gate Verdicts` may change; any other change makes it stale and the same party re-runs it (`implementation/knowledge/agents/release-manager.md:46`).

### M-10. Behaviour changes to brief your team on (no action)

- `security-audit` tools refuse paths with a secret-bearing component (`.env`, `.env.example`, `.envs/`, `prod.env`, private keys, certificates, credential files, `.git`), deny by default, so a legitimate `monkey.key` is refused too (`implementation/runtime/security/validation.py:24-31`; T675).
- The shipped `playwright` entry blocks 39 origins (was 22; T676); `playwright-local` is unchanged.
- PoC: `TECHNICAL-DEBT.md` lives in the PoC root next to `POC-DEBT-SCORECARD.md` (`poc-guidelines.md:155`; T692).
- All 28 agents are `stable` (T670).
- Hash-locked requirements exist for the two Python MCP runtimes: `implementation/runtime/{memory,security}/requirements-mcp-server.lock.txt` (`pip install --require-hashes -r ...`); the plain `requirements-mcp-server.txt` adds `httpx2>=2.12.0` (T676, SEC-T646-04).

### M-11. For maintainers of the source repository

- Release job on `CI_JOB_TOKEN` (T686): the pusher of the tag needs at least Developer on the project and the right to create the tag; protect `v*` tags for Maintainers; `WIKI_TOKEN` is used only by `wiki-sync` (protected and masked); keep the `glab release create` fallback until a real tag pipeline confirms the job token (`CONTRIBUTING.md:234-279`).
- `scripts/publish-release.py --token` (argv) warns; use `--token-env` (T675). The tag pipeline also runs `scripts/check-release-tag-tree.py` (tag tree equals `origin/main` tree) in `main-develop-drift-gate` (T685, `.gitlab-ci.yml:211`).
- CI images are digest-pinned and CI Python is hash-locked (`ci/requirements-*.txt`); pin bumps follow `docs/wiki/mcp-pin-bump-checklist.md` and `scripts/audit-mcp-pins.py` (T675, T676).
- CWSO scripts in this repository (`scripts/mint-cwso-jwt.py`, `scripts/cwso-deploy-helper.sh`, `scripts/deploy/*`, `implementation/scripts/sia-executor.py`, `implementation/runtime/cwso/mcp_client.py`) read the JWT secret only from `CWSO_JWT_SECRET` or an explicit secret-file option; the old fallback to a sibling secret file is gone (T694).
- `mcp.format: "cursor"` in a platform manifest is an error (M-1).

---

## 3. Known issues (draft for `docs/releases/v9.0.0.md`)

### 3.1 The v8.0.0 K-items now

| v8 item | Status in v9.0.0 | Evidence and draft change |
|---|---|---|
| K-1 `orchestrator` experimental | **Closed** (T670) | Maturity: agents 28 stable; commands 14 stable / 5 experimental; instructions 4 / 2; skills 7 / 20; 80 components, 0 failing (V, `check-maturity.py`) |
| K-2 Golden suite | **Changed** | 34 cases, 30 pass, 4 `known_failing` (all `capability_gap`), 0 regressions (V, `scorecard.py --check`). Open: `security-audit-critical-not-fail`, `code-review-conditional-pass-conditions-gap`, `prepare-release-conditional-pass-conditions-gap`, plus one in the held-out set (counts only). The four stay `known_failing` by the user's decision "D-6 a" (K-2b). The scorecard file name still says `v6.12.0` |
| K-3 Copilot lacks the security servers | **Closed** (T690); replaced by M-8 and new K-25 | |
| K-4 `poc-security-audit` limits | Still true | `poc_scan.py` and `poc_audit_server.py` unchanged since v8.0.0 (V, `git diff --stat v8.0.0 -- implementation/runtime`) |
| K-5 hard-coded index directory | Still true | `servers.yaml:198` (V); TD-T671-K5 |
| K-6 `/prepare-release` installed everywhere | Still true | TD-T671-P5 (`audience:` unimplemented), register v3 theme 1 |
| K-7 old `validate-tasks.py` and templates kept | Still true (I) | `--update` merges `docs/` preserving existing files (`scripts/install.sh:1433-1447`); not re-run |
| K-8 parked items | **Changed** | RO621-N-1 accepted ("D-5"), N-2 ruled (T692), N-3 open (tracked-LOW), N-4, N-5, O1-b and O5-c accepted; P112-P41-O1 ruled and applied (T691, T693); older parked remarks not re-read (TD-T671-legacy, unverified) |
| K-9 | Keep the id (closed) | |
| K-10 `CHANGELOG.md` | **Changed** | The file still holds only `[Unreleased]` and the job artifact is regenerated. The v7.0.1 range quirk is gone: `v8.0.0` is an ancestor of `develop` and `main` has the tag's tree (V). `git log --no-merges --oneline v8.0.0..HEAD` is 41 at `3394229a`; the release-branch commits add to it |
| K-11 no single scale page | **Closed** (T674) | `docs/wiki/severity-and-grade-scales.md` |
| K-12 changelog placement | **Closed** (T675) | `scripts/publish-release.py:402-403`. The API half of the release job is still unexercised: new K-26 |
| K-13 MCP pins | **Changed** | The `github` container is gone (T676). npm transitive dependencies still float; the Python runtimes have hash locks. `SUPABASE_ACCESS_TOKEN` is account-wide; `@zereight/mcp-gitlab` and `toolradar-mcp` have single maintainers; no bump scheduler. `@brave/brave-search-mcp-server@2.1.4` has two HIGH audit findings accepted until 2026-11-21 or the next Brave release (SEC-T676-02, `brave-audit-acceptance-v2.md:11`): **the release document must restate that they block the tag if the acceptance lapses** (plan-124 T705; T702 result to be inserted) |
| K-14 symlink-guard window | Still true | Accepted residual T636-L6/L7 (register v3 7.2) |
| K-15 Playwright | **Restate without Cursor** | Narrowing in force on Claude Code, Copilot (documentation) and Pi with `pi --tools`; on Opencode **generated agents** now also carry per-agent denies (T663, M-7); on Gemini CLI an agent's list still does not restrict MCP tools, and every agent can call every other tool of every configured server, GitLab writes included. The server-level six-tool denial on Opencode and Gemini stays. Built-in Opencode agents and own agent files: K-23. SEC-T658-01 stays user-accepted (register v3 7.1). Delete the Cursor sentences |
| K-16 GitLab write tools | **Restate** | All seven holders named (M-6); SEC-T660-01 accepted residual "mitigated, not closed" (same-user read access to the token file; tmpfs can be swapped unless swap is encrypted); one shared Developer-level token (SEC-T665-07, DEC-T681-1); `GITLAB_PERMISSION_MODE=modify` binds the user's own session too; a shell with the token can still merge, tag or push |
| K-17 dependency audit | **Changed** | `scripts/audit-mcp-pins.py` exists (T676); the httpx2 range is closed by the floor and lock (SEC-T646-04). Insert the T702 result (plan-124) |
| K-18 tracked debt by reference | **Replace** | Refer to `docs/artifacts/tracked-debt-register-v3.md`: 398 ids, 4 open, 77 tracked-LOW, 39 accepted; none open is `SECURITY:HIGH` or `CRITICAL`; the one open MEDIUM, SEC-T662-01, is closed by this release |
| K-19 installs without a sidecar | Still true; **extend** | Add `github` (M-2) and, on Pi, `hindsight` and `cwso` (M-4): without a usable sidecar they are not pruned |
| K-20 not observed live | Still true; **extend** | Add: the Opencode per-agent denies (T663, not observed in a live tool call), the Copilot behaviour of the two new servers (T690). Pi placeholder forms were verified on Pi 0.99.0, 1.0.0, 1.3.0, 1.4.0 (T680); Pi list handling still not observed. User action A-7 |
| K-21 rollback to v7.0.1 | **Replace** | Rollback to v8.0.0 with `--update`: recreates `.cursor/` (wholesale replacement), restores the `github` entry, the whole-server GitLab grant of five roles and `qa-engineer`'s job-output tool, Pi `${env:X}` placeholders (which do not work on Pi), `GITLAB_PERMISSION_MODE` unset (server default `full`, per the README (unverified)), and removes the two Copilot security servers and the Opencode per-agent denies (I, from the v8.0.0 sources; not run) |

### 3.2 New items an adopter must know

- **K-22** A Cursor install left in a project is frozen and is not pruned (M-1); its agents are not tool-restricted (SEC-T678-03).
- **K-23** Opencode built-in agents (build, plan, general, explore, ...) and agent files of your own get no per-agent deny and no global GitLab deny; only the server-level six-tool Playwright denial applies to them (user decision 2026-10-16; `AGENTS.md:118`).
- **K-24** GitLab token at rest and in memory: environment mode (an exported token in a profile or `.env`) is a plaintext secret at rest on an unencrypted disk, and no user decision records it as accepted (TD-T697-08, decision D-11 open); a token file in tmpfs can be swapped unless swap is encrypted, and any same-user process can read it (SEC-T660-01 residuals, accepted). `check-gitlab-token.py` cannot see disk encryption and does not check the role in the usual case.
- **K-25** GitHub Copilot: `context-retriever/retrieve` is listed in agent tool lines but the server is not generated for Copilot (fail-closed, SEV-T690-06); the security servers' code is workspace-resident (SEV-T690-02); the executor passes the full inherited environment to child tools (SEV-T690-04).
- **K-26** The release job on `CI_JOB_TOKEN` is unproven until the first real tag pipeline (section 5). For maintainers only.
- **K-27** Live checks still open (A-2 remainder): whether a Developer-level token can merge into a protected branch limited to Maintainers; unset-variable behaviour in VS Code and Cline (`implementation/PREREQUISITES.md:225`).

---

## 4. Version markers and stale lines for T704

Measured by simulation: README marker set to `v9.0.0` in a scratch copy, then `python3 scripts/check-version-consistency.py --root <copy>` (V). The script reads `Latest release: vX.Y.Z` from `README.md` and fails on any older `vX.Y.Z` near "current release", "latest release", "current state" or "release:", or in a path or link to `docs/releases/vX.Y.Z.md`, outside `docs/releases/`, `docs/checkpoints/`, `docs/archiv/`, `docs/tasks/`, `docs/plans/`, `docs/artifacts/`, `tests/golden/` and `CHANGELOG.md` (`scripts/check-version-consistency.py:66-75`). On today's tree it passes for v8.0.0 (V).

### 4.1 Markers to bump (v8.0.0 to v9.0.0)

| File:line | Text now |
|---|---|
| `README.md:14` | `Latest release: v8.0.0` (canonical marker; also read by `verify-release-docs.py` and `check-main-develop-drift.py`) |
| `README.md:222` | `Per-release install steps live in [docs/releases/v8.0.0.md](...)` |
| `docs/wiki/README.md:6` | `Latest release: v8.0.0` (a `MARKER_FILES` entry of `verify-release-docs.py:30-34`) |
| `docs/wiki/home.md:5` | `Latest release: v8.0.0` (a `MARKER_FILES` entry) |
| `docs/wiki/implementation-guide.md:5` | `(current release: v8.0.0)` |
| `docs/wiki/implementation-guide.md:41` | link to `docs/releases/v8.0.0.md` (two hits on the line) |
| `implementation/README.md:4` | `(**v8.0.0**)` |
| `implementation/README.md:6` | `Latest release: v8.0.0` |
| `implementation/README.md:61` | `Per-release notes: [docs/releases/v8.0.0.md](...)` |

No version marker exists in a JSON, YAML or script file (V, `git grep '8\.0\.0'` outside the historical folders: only prose, tests, CI comments and `scripts/install.sh:1299-1300`, which name the v8.0.0 notes on purpose).

### 4.2 Lines the gate flags that are not markers

| File:line | Why flagged | Action |
|---|---|---|
| `docs/decisions/ADR-010-drop-cursor-platform-support.md:10,45,126,141,213` | Path `docs/releases/v8.0.0.md` in an accepted, immutable ADR | Cannot be edited. Needs decision D-T700-1 (section 6) |
| `docs/wiki/severity-and-grade-scales.md:13` | Path `docs/releases/v8.0.0.md` in a sentence that is a dated reference on purpose | Reword without the path form (for example "the v8.0.0 release document"); no test pins the sentence (V, grep of `tests/functional`) |

### 4.3 Stale lines and counts (not caught by the gate)

- `scripts/install.sh:1300`: "`--force-prune-keys exists only in the v8.0.0 installer.`" is inaccurate (TL-T700-01): the option belongs to `scripts/merge-mcp-json.py` and exists in v9.0.0 (`:418`); only the generated Cursor source file is v8.0.0-only. Pinned verbatim by `tests/functional/test_install_cursor_removal.py:41-42`, so a fix changes both. Suggested text: "The generated Cursor file that `--force-prune-keys` needs as `--source` exists only at the v8.0.0 tag; edit the file by hand."
- `AGENTS.md:116` and `implementation/AGENTS.md:116`: "the setup instructions export `GITLAB_PERSONAL_ACCESS_TOKEN`" (SEC-T689-03); owned by T701, not T704.
- `docs/wiki/mcp-servers.md:306`: the heading "Migrating an existing install from v7.x" now carries the v9.0.0 item 8 (optional retitle; check anchors first).
- Counts re-checked and correct: 28 agents (`README.md:309`, `docs/wiki/home.md:17`), 19 commands (`README.md:307`), 16 MCP servers (7 core, 9 extended; `AGENTS.md` lists them), six platforms (`scripts/install.sh:20`, `docs/releases/_template.md:21-29`), "the other five platforms" (`implementation/knowledge/commands/skillify.md:50`), 21 agents without a GitLab tool and seven named holders (`AGENTS.md:116`) (V).
- Leftover Cursor mentions in live docs are deliberate: `README.md:64` (removal notice) and the "recorded before Cursor was removed" notes (`AGENTS.md:118`, `docs/wiki/mcp-servers.md:124,149`, `implementation/PREREQUISITES.md:44-45`) (V).

---

## 5. Release-job readiness on `CI_JOB_TOKEN`

**State.** The `release` job (`.gitlab-ci.yml:215-233`) needs `release-docs-gate` and `main-develop-drift-gate`, uses the digest-pinned `python:3.12-alpine`, clones with `GIT_DEPTH: "0"`, installs `git~=2.54` with an allowlisted environment (`:222`) and runs `publish-release.py --token-env CI_JOB_TOKEN --token-header JOB-TOKEN` (`:227`). The script runs `git fetch --tags --force` always (`scripts/publish-release.py:529`) and `fetch --unshallow --tags origin` only for a shallow clone (`:236-240`), both with `child_environment()` (`:206`): allowlisted names (`:92-95`, including `GIT_ASKPASS`, `GIT_CONFIG_COUNT` and `GIT_CONFIG_KEY_n`/`VALUE_n`) and no variable whose value contains the job token or `WIKI_TOKEN`. `main-develop-drift-gate` fetches without that filter. No real tag pipeline has run this job (T686 row; register v3 A-5).

**SEC-T686-03 (job-token masking; register status "fixed" as documentation).** Whether `CI_JOB_TOKEN` is masked in job logs is unverified; the script never prints it. It is an item of the first-tag checklist (`CONTRIBUTING.md:270-279`).

**SEC-T686-06 (clone method; tracked-LOW, availability, fail-closed; "settle before the first real tag").** If the runner gives git the clone credential through the environment (for example a `GIT_CONFIG_VALUE_n` or askpass variable whose value holds the job token) rather than through `.git/config`, the value filter removes it and the fetch at `publish-release.py:529` fails before any API call. The runner's clone method and version cannot be read by an agent (unverified). T706 rehearses the job with `--skip-api` in a scratch clone and cannot exercise the runner's credential (I), so the first real tag pipeline is the first test. If it fails there: re-run the job after a fix or use the `glab release create` fallback; never move or re-tag (plan-124 risk table; `CONTRIBUTING.md:259-261`).

**What the first real tag pipeline (`v9.0.0`) must confirm, recorded in checkpoint-040:**

1. `release-docs-gate` passes (`verify-release-docs.py --tag v9.0.0`).
2. `main-develop-drift-gate` passes, including `check-release-tag-tree.py` (the tag tree equals `origin/main`), so the tag goes on the verified `main` tip after both merges.
3. Both git fetches in `release` succeed with the filtered environment (SEC-T686-06); on failure, the log line is reported and the allowlist is not widened to the token.
4. The Releases API accepts the `JOB-TOKEN` header (status code recorded); the pusher holds Developer or higher; the job-token permission and allowlist settings of the project do not deny it (unverified until run).
5. The GitLab Release body equals `docs/releases/v9.0.0.md` byte for byte, and the `CHANGELOG.md` artifact lists the `v8.0.0..v9.0.0` non-merge subjects.
6. No job-token value appears in the logs of `release` and `release-docs-gate` (SEC-T686-03).
7. Whether job tokens work in tag pipelines on protected tags here (T686 unverified point).

Other preconditions: `v*` tags protected for Maintainers (A-4, the user's report; re-checked by the orchestrator through the read-only API per register v3); `apk add git~=2.54` resolves in the pinned image's Alpine branch at tag time (I: a later Alpine `git` minor version in that branch would fail the bootstrap; not checked).

---

## 6. Decisions for the release manager or the user

| # | Decision | Options | Recommendation | Who |
|---|---|---|---|---|
| D-T700-1 | The version gate flags five lines of the immutable ADR-010 after the bump (4.2) | (a) Add `docs/decisions/` to `EXCLUDED_PREFIXES` of `scripts/check-version-consistency.py`, with a test and a rationale note (the script comment requires the task-T400 rationale to be updated; precedent: `tests/golden/` added by T642 on the user's decision); (b) a superseding ADR only to change paths (disproportionate) | (a): accepted ADRs are historical records like `docs/plans/` and `docs/artifacts/`. Needed before T704 can pass | user (as for T642); implemented in T704 or a small devops task |
| D-T700-2 | `scripts/install.sh:1300` wording (TL-T700-01) | (a) fix in T704 together with `test_install_cursor_removal.py:41-42`; (b) leave it, record as LOW debt, and state the accurate fact in M-1 | (a) if T704 runs the gates anyway; else (b) | orchestrator, release manager |
| D-T700-3 | The Cursor cleanup recipe in M-1 (TL-T700-02) | (a) hand editing only; (b) give the merge-script recipe with the v8.0.0 Cursor file, with its side effects | (a) | release manager |
| D-T700-4 | D-11 (TD-T697-08): environment mode and Immutable Security Constraint 6 | as in register v3 6.2 | Decide before T705 writes M-5 and K-24, so the release document states the decided position | user, with security-engineer |
| D-T700-5 | SEV-T690-07: a stderr note on `--update` as well as the release notes | (a) release notes only (D-13); (b) also an installer note | (a) for v9.0.0; the note stays LOW debt | orchestrator |
| D-T700-6 | The Brave HIGH findings (A-6, plan question 3) | already set: "Decide after T702 (Recommended)" | none here | user, after T702 |

---

## 7. Findings of this audit

| Id | Grade | Location | Finding |
|---|---|---|---|
| TL-T700-01 | LOW (accuracy of adopter text) | `scripts/install.sh:1300`; pinned by `tests/functional/test_install_cursor_removal.py:41-42` | "`--force-prune-keys exists only in the v8.0.0 installer`": the option was never an installer option and still exists in `scripts/merge-mcp-json.py:418`; only the generated Cursor source file is v8.0.0-only (ADR-010 Appendix A says it correctly) |
| TL-T700-02 | LOW (migration text) | M-1; `scripts/merge-mcp-json.py:455-469` | With the v8.0.0 Cursor file as `--source`, `--force-prune-keys filesystem` is refused (the key is in that source) and the run merges all v8.0.0 Cursor entries, `github` included, into the user's file (I, code reading; not run) |
| TL-T700-03 | INFO | `scripts/install.sh:1304-1307` | The Cursor notice is printed on `--update` and `--projections-only` only, not on a plain install; Appendix A's "while it finds" should say so |
| TL-T700-04 | INFO | `docs/decisions/ADR-010-...md` | The version gate will fail after the bump on an immutable file (D-T700-1) |

None is a security finding graded `SECURITY:MEDIUM` or higher.

---

## 8. What I did not verify

- The full test suite, the golden contract and the evaluator hash were not run (no code changed); the suite count 2188 is from plan-124.
- `--dry-run` creating nothing, the leading-dash refusal and hash identity after T677: read from the ledger and code, not run.
- TL-T700-02 and the rollback effects in K-21: inferred from code and the v8.0.0 sources, not run.
- The `GITLAB_PERMISSION_MODE` teardown list and server default: from the server README on main, not matched to 2.2.5 (as `PREREQUISITES.md` says).
- The runner's clone method, job-token masking, the Releases API with `JOB-TOKEN` and the project's job-token settings (section 5).
- VS Code behaviour of the two new Copilot servers; Opencode per-agent denies in a live tool call; Gemini CLI denials (K-20, A-7).
- Cursor still reading a root `AGENTS.md`: taken from ADR-010, not re-checked.
- K-7: install behaviour for an existing `validate-tasks.py` was read in code, not run.
- No remote state was read after the fetch of 2026-11-01; a later commit on `origin/develop` is not covered.

## 9. Review mode and references

Read-only. Artifacts referenced: `ADR-010` (Appendix A), `task-T679.md` 3a, `tracked-debt-register-v3.md`, `docs/releases/v8.0.0.md`, `release-v8-audit-v2.md`, `security-review-t686-release-job-token-v1.md` (by its register rows), `brave-audit-acceptance-v2.md`, `checkpoint-039`. Decision ids: ADR-010, D-11, D-12, D-13 (register v3), DEC-T664-3, DEC-T681-1, D-6 a, D-5.
