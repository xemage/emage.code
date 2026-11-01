# Artifact: gitlab-per-role-token-design-v1.md

> Immutable once produced; revisions bump `<N>`.

## Metadata

- **Author**: solution-architect (T681). No shell, no live client run, no token used or read. Decision artifact only: no code, no existing document, no agent file was changed. The user decides (section 9).
- **Date**: 2026-10-22. **Status**: PROPOSED.
- **Based on**: `docs/tasks/task-T681.md`; `docs/plans/plan-123-post-release-follow-ups.md` (Addendum of 2026-10-22: T681; named by the task brief, not re-read); `docs/artifacts/security-review-t665-token-handling-v1.md` (SEC-T665-01, SEC-T665-07); `docs/artifacts/gitlab-token-handling-design-v1.md` (option D, DEC-T664-1 to -6); `implementation/PREREQUISITES.md` ("GitLab token"); `implementation/knowledge/mcp/servers.yaml` (the single `gitlab` entry); `implementation/scripts/sync.mjs` (`emitMcp`, `agentMcpDenials`, `MCP_TOOL_NAME_STYLES`, `parseServersYaml`, `validateDenyTools`); `implementation/platforms/{opencode,pi,gemini}.json`; the seven GitLab-holder agent files in `implementation/knowledge/agents/`; `AGENTS.md` ("GitLab grants"); `tests/functional/test_mcp_package_pins.py` (first 150 lines); `scripts/check-gitlab-token.py` (first 120 lines). Vendor sources: section 11.
- **Evidence labels**: **[V]** = read during this task in a file of this repository or in vendor documentation (a documentation statement, not a test result). **(unverified)** = not read or not run. Nothing here was observed in a live run of any client or of GitLab.
- **Decision references**: DEC-T681-1 to DEC-T681-3 (section 9). No ADR is written by this task; if the user chooses option B, C or D the orchestrator writes the ADR (next free number).
- **No `requirements-vN.md` applies.**

## 1. Summary

1. **The threat is real but narrower than "every shell role holds a Developer token".** Only the three merge-request roles (`orchestrator`, `poc-orchestrator`, `release-manager`) hold `create_merge_request`, the one tool that forces Developer. Every other GitLab tool of the seven holders works with Planner or Reporter. The shared token is Developer-level only because one `gitlab` entry serves all seven.
2. **A second server entry is cheap for the generator and weak as a control.** `sync.mjs` already renders any number of server entries, derives tool names per server and writes the per-agent Opencode denies per server, so option B needs data changes only (section 5.2). But both tokens live on the same disk of the same user, and every agent with `execute` (most of which hold no GitLab tool at all; 6 of the 7 GitLab holders, per AGENTS.md) can read both. B changes what the *MCP surface* can do on clients that do not enforce tool lists; it does not change what a shell can do.
3. **Recommendation: A now, plus a documented "Reporter profile" (docs only); defer B; do not do D.** The Developer-level CI/runner sentence goes into the `PREREQUISITES.md` scope table now, whichever option the user picks (section 8). C (the harness holds no Developer credential at all) is the only option that removes a credential rather than splitting it; choose it if the user wants that, and accept the workflow cost.

## 2. The threat and the residual, restated

### 2.1 What a Developer-level `api` token can do (the exposure the docs understate)

From the GitLab permissions page, fetched 2026-10-22 **[V]** (the page was flattened by the fetch tool; two rows are marked "inferred" by that tool):

- "Push to non-protected branches": Developer. Reporters cannot push code.
- "Run, rerun, or retry CI/CD pipeline or job": Developer. On a protected branch only if the user may merge or push there.
- "Create Git tags" and "Delete Git tags": Developer (inferred from the table). "Manage protected tags": Maintainer, so a tag name no protected-tag rule covers can be created by a Developer.
- "Create, delete and stop environments": Developer. "Cancel jobs": Developer (inferred).
- "Manage project CI/CD variables" and "manage project runners": Maintainer. A Developer token cannot read or change variables through the API.

From the CI/CD variables page **[V]**: a protected variable is "available only to pipelines that run on protected branches or protected tags" (merge request pipelines can optionally receive them); the page does not state which refs receive an unprotected variable, but by contrast every pipeline on an unprotected ref does.

What follows for the harness (my inference, **(unverified)** as a live chain, not run): a holder of the token can push a commit to a new unprotected branch that changes `.gitlab-ci.yml`, start a pipeline on it, and so run arbitrary code on the project's runners. That code sees every unprotected CI/CD variable and the job token, and can reach whatever the runner reaches (network, a shared runner's other jobs, deploy credentials stored as unprotected variables). It does not need `merge`, `create_pipeline` or `push_files` in any agent's tool list: the token is enough. Branch protection stops a merge into `main` or `develop`; it does not stop this. Only protected variables, protected environments and runners limited to protected refs do, and they are the adopter's configuration, outside the harness.

The same capability is **not** reachable through the MCP tools of the shipped roles: no role holds a push, branch, tag or pipeline-trigger tool (PREREQUISITES, "Rules that follow from the table"). The exposure is the token itself, read from a file or the environment by a shell, then used with `curl`.

### 2.2 Who is exposed

| Group | Agents | Holds GitLab MCP tools | Holds `execute` (a shell) | Needs Developer |
|---|---|---|---|---|
| MR roles | orchestrator, poc-orchestrator, release-manager | yes, incl. `create_merge_request` | yes | yes |
| Read and issue roles | qa-engineer (20 tools incl. `create_issue`, job output), devops-engineer, poc-devops-engineer | yes, no MR creation | yes | no |
| Issue writer without shell | scrum-master | yes (24 tools) | **no**: its tool line is `read, search, todo, web` plus GitLab tools **[V]** | no |
| Everyone else | backend-developer, frontend-developer, database-engineer, tech-lead, security-engineer and others | none | yes (most) | n/a |

The task brief names scrum-master among the shell-holding roles; its agent file shows no `execute`. The shell-holding GitLab roles that do not need Developer are therefore qa-engineer, devops-engineer and poc-devops-engineer, and the shell exposure of the token is wider than the seven: every agent with `execute` runs as the user in the same client environment, whether or not it holds a GitLab tool (design v1, section 2.3, AP-1 to AP-5). A per-role token inside one client environment cannot hide anything from those agents.

### 2.3 The residual, precisely

- SEC-T665-01 (MEDIUM) is the same-user residual that the user re-accepted on 2026-10-16. SEC-T665-07 (LOW) is its sharper form: the one credential that every agent shell can reach is sized for the three roles that need most.
- Splitting the credential reduces it only if the stronger half is unreachable from the shell. In this harness it is not: both halves are files or variables of the same user, in the same client session. The only closure remains an isolated user, container or VM (design v1, DEC-T664-1).
- A second, usually stronger credential is already reachable on a maintainer's machine: `~/.config/glab-cli` and `~/.git-credentials` (AP-4; this project's own skill `gitlab-api-push-fallback` uses `glab`). For such an adopter the harness's Developer token is not the strongest credential on disk. For an adopter without `glab`, it is.

## 3. What the generator and the clients do today (facts used by the options)

- **Generator, entries.** `parseServersYaml` accepts any key matching `[A-Za-z0-9._-]+`; `emitMcp` loops over all entries of a tag set and renders each per platform; `denyUnlessGranted` and `denyTools` are per server; the provenance sidecar records every generator-owned key **[V]** (`sync.mjs` read in full). A second entry needs no change to `sync.mjs`.
- **Generator, tool names.** An agent token `mcp__<server>__<tool>` is rendered per platform: Claude Code verbatim; Copilot `slash` (`gitlab-mr/create_merge_request`); Opencode `underscore` (`gitlab-mr_create_merge_request`; characters outside `[A-Za-z0-9_-]` become `_`, a hyphen is kept); Pi `mcp__gitlab_mr__create_merge_request` (a hyphen becomes `_`); Gemini drops the `tools` line (`"tools": "drop"`), so a Gemini agent has no per-agent MCP list at all **[V]**. Cline has no agent files (design v1, section 5).
- **Generator, Opencode denies.** `agentMcpDenials` writes, per `denyUnlessGranted` server, `<server>_*: false` after the allows for an agent that holds nothing of the server and before the allows for an agent that holds only named tools of it **[V]**. With two servers each MR role would get a leading wildcard deny for both, followed by its named allows. `AGENTS.md` records that `gitlab_*` does not match a server named `gitlab-ee`, so `gitlab-mr` is not covered by the `gitlab` wildcard and needs its own `denyUnlessGranted: true`. Avoid the name `gitlab_mr` (it would be matched by `gitlab_*`).
- **Who enforces a tool list.** Claude Code, Copilot/VS Code (by documentation), and Pi (when the file reaches `pi --tools`) enforce; Opencode enforces through the T663 per-agent denies (documented and read from vendor source, not observed live); Gemini CLI and Cline do not, and Opencode's built-in agents are not covered (`AGENTS.md`, "GitLab grants").
- **Token file mode (T665).** The server reads `GITLAB_PERSONAL_ACCESS_TOKEN_FILE` once at start; a non-empty `GITLAB_PERSONAL_ACCESS_TOKEN` wins (design v1, section 5). The generator's `fromEnv` decouples the name the server sees from the name the client reads, so a second entry can read `GITLAB_MR_PERSONAL_ACCESS_TOKEN_FILE` and hand it to the server as `GITLAB_PERSONAL_ACCESS_TOKEN_FILE` **[V]** (`servers.yaml` syntax).
- **Pinned server controls.** `GITLAB_TOOLS` is "an explicit list [that] replaces the default `core` toolset; it does not merge" **[V]** (README 2.2.5, fetched 2026-10-22). What is **not** in the README: whether a tool outside `core` (`create_merge_request` is in the `merge_requests` category, which `discover_tools` can activate) is registered by `GITLAB_TOOLS`, whether `discover_tools` is still registered when `GITLAB_TOOLS` is set, the behaviour of `GITLAB_DENIED_TOOLS_REGEX`, and what the server does at start without a token **(unverified)**.
- **Pi.** An unset variable in a Pi `env` value throws (source read on Pi main, T665 review; follow-up T680). Every additional unset variable in a generated entry would add to that gap **[V]** (documented in `PREREQUISITES.md`).

## 4. Options

### Option A. Status quo plus the documentation sentence

- **What**: no structural change. Add the Developer-level CI/runner sentence to the scope table (section 8). Add a "Reporter profile" paragraph: an adopter who does not use the three MR roles through MCP creates a Planner or Reporter token (already stated as "Planner or Reporter otherwise"); an adopter who uses them accepts a Developer token and is told what it reaches.
- **Generator**: nothing. **Clients**: nothing new.
- **Adopter cost**: none beyond reading one more paragraph.
- **Tests and counts**: one documentation assertion (SEC-T658-06 style, anchored to the paragraph) in the existing docs tests; no server, agent or projection count changes.
- **Residual**: unchanged. Every shell reads the one token; a Developer token reaches section 2.1.
- **Size**: S (documentation task, already routed).

### Option B. Two server entries

- **What**: keep `gitlab` for the read and issue tools with a Planner or Reporter token; add `gitlab-mr` (name to be chosen; avoid `gitlab_mr`) with a Developer token, started with `GITLAB_TOOLS=create_merge_request` so the server itself registers only that tool **(unverified: section 3)**, `GITLAB_PERMISSION_MODE=modify`, and its own variables `GITLAB_MR_PERSONAL_ACCESS_TOKEN` / `GITLAB_MR_PERSONAL_ACCESS_TOKEN_FILE`. The three MR roles keep every read tool on `mcp__gitlab__*` and replace only `mcp__gitlab__create_merge_request` with `mcp__gitlab-mr__create_merge_request`.
- **Generator**: no code change (section 3). Data: one `servers.yaml` entry (about 12 lines with comments), three agent files edited. Regenerate six platform projections, the Opencode and other agent copies of the three agents, `registry/index.json` checksums; declare root drift in `tests/_baselines/root-install-drift.json` (do not refresh the root install). `scripts/merge-mcp-json.py` adds the new key by itself; on a rollback to v8.x the provenance sidecar lets the old file prune it.
- **Clients (what each does with it)**:

| Client | Second entry starts | Per-role tool list for `gitlab-mr` | Evidence |
|---|---|---|---|
| Claude Code | yes; a new project-scoped server asks for approval again (M-2); with `${VAR:-}` an unset token variable renders empty | enforced (`mcp__gitlab-mr__create_merge_request`) | documented; hyphenated server names are shown for `playwright-local` in PREREQUISITES; not run |
| Copilot / VS Code | yes | `gitlab-mr/create_merge_request`; enforced by documentation | documented; not run |
| Opencode | yes | `gitlab-mr_create_merge_request` plus per-agent denies; the built-in agents are not covered | documented and read from vendor source; not observed |
| Pi | yes if the variable is set; an unset variable throws (T680), so an adopter without MR roles must still set it, which defeats the point | `mcp__gitlab_mr__create_merge_request` | source read, not run |
| Gemini CLI | yes; every agent can call it (tools dropped); `GITLAB_TOOLS` is the only cap on the surface | none | documented; not run |
| Cline | yes; global config, no agents | none | documented; not run |

- **Adopter cost**: a second token to create (Developer, ideally a project access token with 30 to 90 days expiry), store (a second 0600 file), rotate and revoke; one more server process (`npx`) per client session; one more approval prompt. An adopter who uses no MR role gets a second server that starts without a token: whether it exits with an error is **(unverified)**, but the client will list a failing server. The generator has no "optional entry" concept (`tags` select per platform, not per adopter).
- **Interplay with T665 file mode**: two path variables, two files. `scripts/check-gitlab-token.py` takes the variable names as flags (the docstring says the variable name is a flag; the flag names were not read **(unverified)**) and has one ceiling constant, `MAX_ROLE_LEVEL = 30` (Developer); the default entry would want a Reporter ceiling (20).
- **Tests and counts** (test files other than `test_mcp_package_pins.py` were not read **(unverified)**): `APPROVED_NPX_PINS` must gain a `gitlab-mr` key because the test asserts that the set of npx entry keys equals the dict (one line, verified in the file); the grant-set tests (`GitLabGrantSetTests`) that pin which agents hold `create_merge_request` change their expected token name; platform-projection tests that assert server key sets or counts change; documentation assertions anchored to "seven named holders" and to the Opencode enumeration of `denyUnlessGranted` servers change. Docs: `AGENTS.md` (MCP table, "GitLab grants", which says "no agent holds the whole `gitlab` server" and lists tool counts per role), `PREREQUISITES.md` (scope table, file mode steps twice, per-client table, the long Opencode paragraph that enumerates the servers), `docs/wiki/mcp-servers.md`, the release notes. The core-server count rises by one in every projection and in the AGENTS.md table. My estimate, not measured: 15 to 30 new or edited tests on top of the current 1617 (skipped 23).
- **Residual**: the same-user shell reads both files. On a client that enforces tool lists, the MCP path is already closed for the non-MR roles under A, so B adds nothing there. On Gemini and Opencode built-ins B limits the *MCP* surface of the default entry to the Reporter ceiling (enforced by GitLab) and of the second entry to one tool (enforced by the server, if the `GITLAB_TOOLS` behaviour holds). Against an attacker with a shell (Gemini agents all have one) the gain is nil.
- **Size**: M (devops-engineer for entry, agents, tests and checker; technical-writer for four documents; Security Engineer review because a credential path is added).

### Option C. One entry; the MR roles stop using MCP to open merge requests

- **What**: remove `create_merge_request` from `orchestrator`, `poc-orchestrator` and `release-manager`. The shared token drops to Planner or Reporter for everyone, and the harness holds no Developer credential. Merge requests are opened by the top-level session or the maintainer (already the policy for merge, tag and release in `AGENTS.md`), with the maintainer's own credential (`glab`).
- **Generator**: nothing. Three agent files, the "GitLab grants" text, the orchestrator and release-manager workflow text, `git-workflow.md` wording on who opens merge requests, the T667 grant-set tests.
- **Clients**: nothing new; the agents simply lack the tool everywhere.
- **Adopter cost**: lowest credential burden (one token, Reporter); a workflow change: subagent branches are pushed, the top-level session opens the merge request. An agent with `execute` can still run `glab mr create` if a `glab` credential exists, so C removes the harness-issued Developer credential, not the capability on a maintainer's machine.
- **Interplay with file mode**: none; one file as today.
- **Residual**: the harness-held credential reaches no more than Reporter or Planner. The maintainer's `glab` credential (AP-4) is untouched and is stronger than the removed token. Net effect for a `glab` user: smaller, not closed.
- **Tests and counts**: grant-set tests lose `create_merge_request` from three expectations; the `AGENTS.md` per-role tool counts (16, 8, 17) drop by one each; `gitlab_create_merge_request` disappears from the Opencode "global ask overridden" example in the docs.
- **Size**: S to M, but it reverses a function T666 and T667 added on purpose (**(unverified)**: their rationale was not re-read), so it needs the user's ruling on the workflow, not just on the security trade.

### Option D. Project or group access tokens per role

- **What**: one token per role or per tier, each a bot user (project or group access token, role chosen at creation). A token is per server process, so per-role tokens mean per-role server entries: at least three tiers (read-only: devops-engineer and poc-devops-engineer, scope `read_api` if the CI lint calls accept it **(unverified)**; issue writers: qa-engineer and scrum-master, `api`, Planner or Reporter; MR roles, `api`, Developer), at most seven entries.
- **Generator**: as B, repeated; every role's tool line is renamed; every per-platform tool-name mapping and every Opencode deny map is multiplied.
- **Clients**: as B, with more processes (each entry is an `npx` process) and more approval prompts; Pi's unset-variable gap multiplies.
- **Adopter cost**: three to seven tokens; GitLab.com requires Premium or Ultimate for project access tokens (design v1, section 4); each needs rotation. Rotation of bot tokens is the adopter's script.
- **Residual**: as B. The gain over B is one tier (`read_api` for the two DevOps roles), which a shell attacker does not need to care about, since the stronger tokens are on the same disk.
- **Size**: L. **Not recommended**.

### Comparison

| Option | Developer credential exists | Shell can reach it | Non-enforcing client MCP surface | Adopter tokens | Generator code change | Size |
|---|---|---|---|---|---|---|
| A status quo plus sentence | yes (if MR roles used) | yes | Developer-wide | 1 | none | S |
| B two entries | yes (if MR roles used) | yes (second file) | Reporter on `gitlab`, one tool on `gitlab-mr` (if `GITLAB_TOOLS` holds) | 2 | none (data only) | M |
| C no MCP MR creation | **no** | n/a (the maintainer's `glab` remains) | Reporter | 1 | none | S to M, workflow change |
| D per role | yes (if MR roles used) | yes | tiered | 3 to 7 | none (data only), large data | L |

## 5. Mechanics worth knowing before deciding

### 5.1 Why B protects less than it appears to

An attacker needs a path to a token. The paths are the shell (environment, `/proc`, file, history: AP-1 to AP-5 of design v1) and the MCP tool list (AP-6). B closes AP-6 more tightly on the two clients that do not enforce tool lists, and nothing else. On Gemini every agent has a shell anyway. On Claude Code, the one client where a posture (`CLAUDE_CODE_SUBPROCESS_ENV_SCRUB`, sandbox `denyRead`) is documented, the posture is per session, not per agent: a sandboxed Bash for `qa-engineer` has the same rules as one for `orchestrator`, so denying the MR token file to one and not the other is impossible **(unverified in a live run; documentation says the sandbox settings are session settings)**.

### 5.2 What a future per-role split would need that does not exist

A control that does separate roles needs the credential to be reachable only by the process that needs it: an MCP server process started with the Developer token in its own environment under another OS user, or a launcher that reads the token from a source the agent shell cannot use. That is the "(b) require more" branch of DEC-T664-1, which the user declined on 2026-10-16.

### 5.3 Reopening conditions for B

Reopen B (as a new task, with this artifact as input) if any of these becomes true: a client supports per-agent environment or per-agent sandbox settings; the project decides to drop shell access from the read and issue roles (`qa-engineer` and DevOps would then be MCP-only and B would bind them); the project ships a first-class Gemini profile whose MCP surface it wants to cap server-side; or the live checks show that `GITLAB_TOOLS=create_merge_request` yields a server that exposes exactly one tool.

## 6. Migration paths

- **A**: none. Existing installs are unchanged.
- **Reporter profile (docs, part of A)**: the adopter replaces the shared token with a Planner or Reporter token (the PREREQUISITES migration steps 1 to 3 apply as written) and accepts that the MR roles' `create_merge_request` calls then fail with an authorization error; the orchestrator hands the merge request to the top-level session. Nothing is installed or regenerated.
- **B**: `install.sh --update` adds the `gitlab-mr` key and rewrites the three agent files; Claude Code asks for approval of the new server; the adopter creates the second token and file and exports two path variables; the old token is rotated down to Planner or Reporter and re-checked with `scripts/check-gitlab-token.py` (new ceiling); Pi adopters must set the second variable (T680). A user who does nothing finds `create_merge_request` failing in the three MR roles, so the release notes must say so. Rollback restores the v8.x files; the provenance sidecar prunes `gitlab-mr` automatically, and the second token file is unused.
- **C**: `--update` rewrites the three agent files; the adopter lowers the shared token to Planner or Reporter at their pace; nothing else breaks.

## 7. Consequences for task sizing (plan-123 follow-ups)

| If the user chooses | Tasks | Owners | Gates |
|---|---|---|---|
| A (recommended) | T-doc: scope-table sentence and Reporter-profile paragraph (section 8) plus one anchored docs assertion | technical-writer; devops-engineer for the test | the standard `implementation/` gates; no root refresh |
| A, then C later | T-agents: remove the tool from three agent files, adjust grant-set tests, `AGENTS.md`, workflow text | devops-engineer or a developer role; technical-writer; Security Engineer short review | as above; user ruling on the workflow first |
| B | T-entry (servers.yaml, agent files, tests, checker ceiling, drift declaration), T-docs (four documents), Security Engineer review, two live checks by the user (section 9) | devops-engineer, technical-writer, security-engineer | as above; after T680 if Pi adopters are in scope |
| D | B times three plus an ADR | as B | as B |

## 8. The documentation sentence belongs in the scope table now (whichever option is chosen)

The current PREREQUISITES table lists "Create a merge request, a branch, a tag" and "Trigger, retry or cancel a pipeline" as Developer rows, and the rules paragraph says one shared token "needs Developer if you use those three roles". It does not say what Developer reaches beyond the named tools. The orchestrator should route this to the documentation task now. Suggested wording for the row "Create a merge request, a branch, a tag" (or a note under the table):

> A Developer-level `api` token is more than a merge-request token. It can push commits to branches that are not protected, create tags that no protected-tag rule covers, and start pipelines on those branches. A pipeline on a branch the token holder controls runs that branch's `.gitlab-ci.yml` on your runners, with every unprotected CI/CD variable and the job token, whatever the agents' tool lists say. Branch protection on `main` and `develop` does not stop this. Limit it with protected variables, protected environments, runners restricted to protected refs and a dedicated low-privilege project. These rows are the GitLab permissions page of 2026-10-22; the chain as a whole was not run.

Also state in the rules paragraph that scrum-master holds no shell and that every agent with `execute` can read the token file regardless of its own tool list (already in "What this does not protect"; link to it).

## 9. Decisions and questions for the user

All are PENDING.

- **DEC-T681-1. Which option.** (a) A: status quo plus the documentation sentence and the Reporter profile (recommended); (b) B: two entries now; (c) C: remove `create_merge_request` from the three MR roles; (d) D: per-role or per-tier entries. Consequence of (a): SEC-T665-07 stays open as LOW with an accurate description, and the exposure is a stated, accepted residual of SEC-T665-01. Consequence of (c): a workflow change you must rule on.
- **DEC-T681-2. Is the harness's Developer token a credential you want to exist?** Do you use `glab` with a stronger token on the machines where the harness runs? If yes, the harness's Developer token is not the strongest credential on disk and B's gain is smaller still; if the maintainer or an adopter has no `glab` credential, the Developer token is the strongest and option C removes it. Please state which describes the machines you care about.
- **DEC-T681-3. Live check, only if B is chosen.** Run once with a throwaway project access token: start the pinned server with `GITLAB_TOOLS=create_merge_request` and list its tools (does it register exactly one, does it register `discover_tools`?), and confirm a Reporter-level token on the default entry gets an authorization error from `create_merge_request`. Agents cannot run it.

Questions in the order the user should answer them: (1) A, B, C or D? (2) Do you want the Reporter profile documented as a supported mode in which the MR roles hand the merge request to the top-level session? (3) Does the answer to DEC-T681-2 change your choice? (4) If B: do you accept the two live checks and the Pi dependency on T680?

## 10. Not verified

- No live run of any client, of the pinned server or of GitLab. The CI/runner chain in section 2.1 is a reading of two GitLab pages through a fetch tool (which flattened tables and marked two rows "inferred"), not an exercise.
- The behaviour of `GITLAB_TOOLS` for a tool outside `core`; whether `discover_tools` remains registered with an explicit list; `GITLAB_DENIED_TOOLS_REGEX` syntax; what the pinned server does when started without a token (all absent from the 2.2.5 README as fetched; the source was not read in this task).
- Per-client tool-name forms for a hyphenated server name are derived from `sync.mjs` rendering rules and from `PREREQUISITES.md`'s `playwright-local` note; `docs/artifacts/mcp-tool-name-mapping-v1.md` and the per-platform vendor behaviour for a hyphenated name were not re-read.
- Test files other than the first 150 lines of `test_mcp_package_pins.py`, the `check-gitlab-token.py` flag names, `docs/plans/plan-123-post-release-follow-ups.md`, `docs/wiki/mcp-servers.md` and `docs/artifacts/mcp-tool-name-mapping-v1.md` were not read; the test-count estimate for B is an estimate.
- Whether `validate_ci_lint` and `validate_project_ci_lint` work with a `read_api` token (relevant only to D).
- The rationale behind T666 and T667 granting `create_merge_request` to the three MR roles (relevant to C).
- The user's local settings, `.env*` files, credentials and `tests/golden/held-out/` were not opened.

## 11. Sources

- GitLab permissions: https://docs.gitlab.com/user/permissions/ (fetched 2026-10-22). CI/CD variables: https://docs.gitlab.com/ci/variables/ (fetched 2026-10-22).
- Pinned server README: https://unpkg.com/@zereight/mcp-gitlab@2.2.5/README.md (fetched 2026-10-22).
- Repository files listed in "Based on". Client facts: `docs/artifacts/gitlab-token-handling-design-v1.md`, section 5 and section 12.

## 12. Handoff context package (for the task the user's choice creates)

- **task_id**: to be assigned by the orchestrator (A: documentation task; B, C, D: as section 7).
- **definition**: implement the option the user chooses in DEC-T681-1; for A, add the section 8 wording to `implementation/PREREQUISITES.md` (scope table and rules paragraph), mirror it where `docs/wiki/mcp-servers.md` points to the table, and add one anchored documentation assertion.
- **constraints**: no token is created, read, printed or used by any agent; no `.env*`, credential files, user `.claude/settings*.json` or `.vscode/mcp.json`; never open `tests/golden/held-out/`; do not modify `tests/golden/**`; do not refresh the root install, declare drift; keep the pinned launcher form of `@zereight/mcp-gitlab@2.2.5`; label every unverified statement; one Conventional Commit ending with `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`; no push, no merge, no tag.
- **depends_on**: the user's decision on DEC-T681-1 to -3; T680 for option B if Pi adopters are in scope.
- **input_artifacts**: this file, `security-review-t665-token-handling-v1.md`, `gitlab-token-handling-design-v1.md`, `implementation/PREREQUISITES.md`, `implementation/knowledge/mcp/servers.yaml`, `implementation/scripts/sync.mjs`, `tests/functional/test_mcp_package_pins.py`.
- **expected_outputs**: A: the edited PREREQUISITES text and one test; B: servers.yaml entry, three agent files, regenerated projections and registry, drift declaration, tests, four documents, Security Engineer review; C: three agent files, tests, `AGENTS.md`, workflow text.
- **blocker_policy**: report with type and severity (`technical` | `dependency` | `unclear_requirements` | `external`; `critical` | `major` | `minor`). A live check that only the user can run is `external`: `minor` for code, `major` for any documentation claim that depends on it; ship the claim labelled unverified.
