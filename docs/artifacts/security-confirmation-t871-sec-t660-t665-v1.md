# Artifact: security-confirmation-t871-sec-t660-t665-v1.md

> Immutable once produced; revisions bump `<N>`.

# Security Confirmation T871: no harness fix for SEC-T660-01 and SEC-T665-01, release v12.0.0

- **Date:** 2026-11-19
- **Reviewer:** security-engineer. The review was read-only: no shell, no write tool, no token use and no GitLab call. Search was done with `grep_content` on the main checkout.
- **Task:** T871 (plan-182, wave 1). The user's words, verbatim: "release plan go", "Approve (Recommended)" and "v12.0.0, MAJOR (Recommended)".
- **Purpose:** to meet ADR-016 condition 4 and its row D2 (O-C) for v12.0.0. It is a dated statement, made before the user is asked (O-B), on whether the T812 confirmation still holds. It was re-checked against today's tree.
- **Based on** (main checkout `/home/emage/Code/emage/emage.code`, develop `9b9a31f0`):
  - `docs/artifacts/security-review-t812-v11-no-harness-fix-v1.md`, read in full.
  - `docs/decisions/ADR-016-security-engineer-confirmation-as-validity-condition.md`, read in full.
  - `docs/releases/v11.0.0.md`, lines 42, 208, 219, 221, 226, 227, 318, 322 and 323.
  - `docs/artifacts/tracked-debt-register-v25.md` § 6.1, § 6.2 and § 6.3 (lines 167-186).
  - `docs/artifacts/tracked-debt-register-v24.md` § 6.2, item 49 (lines 197-207). v25 § 6.2 says that v24 § 6.2 "stands, unchanged", so this is where item 49 stands today.
  - Registers v20 to v24, by grep for item 49, K-23 and SEC-T844-01.
  - `implementation/PREREQUISITES.md`, lines 89, 110, 123, 127, 144, 153-157, 161, 166-173, 181, 182, 185 and 216.
  - `implementation/knowledge/mcp/servers.yaml`, lines 75, 78-79, 86, 90, 91 and 93.
  - The frontmatter `tools:` line of every agent under `implementation/knowledge/agents/`, by grep for `execute`.
  - `.opencode/agents/scrum-master.md`, the frontmatter of one generated agent without `execute`.

## Facts from the orchestrator (not checked by this review)

- The plan-182 brief makes these statements, and this review did not check them:
  - The token setup is unchanged in kind since T812: one GitLab personal access token, scope `api`, expiring 2027-01-28. It is kept in a gpg-encrypted store, unlocked into memory, and exposed to the session as a token-file path.
  - Since T812 the scope has narrowed only on Opencode (T844, T856, T862; register item 49).
  - Claude Code, Cline and GitHub are unchanged since T812, as far as the range shows.
- I did not open the plan at `agent/tech-lead/T869` (`plan-182-next-release.md`). Its contents are taken from the brief only **(unverified)**.

## What this review verified by reading

- **The `gitlab` entry is unchanged in kind.** These lines of `servers.yaml` are the same as T812 cited them:
  - `:75` pins `@zereight/mcp-gitlab@2.2.5`.
  - `:90` keeps `GITLAB_PERSONAL_ACCESS_TOKEN` (optional, empty default).
  - `:91` keeps `GITLAB_PERSONAL_ACCESS_TOKEN_FILE`.
  - `:93` keeps `GITLAB_PERMISSION_MODE: modify`.
- **The closure text and the residuals are unchanged.**
  - `PREREQUISITES.md:185` still reads: "**The only closure** is an isolated user, container or VM that holds only the scoped credential and no `glab` or git token; the harness cannot create it." This is the same line number T812 cited.
  - `:181` still says that a shell runs as the user and can read the token file and `~/.config/glab-cli`, `~/.git-credentials`, `~/.netrc`, SSH keys and `GITHUB_PERSONAL_ACCESS_TOKEN`. It also still says: "On every other client no mechanism exists".
  - `:182` still states the swap and hibernation residual.
- **15 generated agents hold `execute`.** In source frontmatter these are:
  - the six GitLab holders: orchestrator, poc-orchestrator, release-manager, qa-engineer, devops-engineer and poc-devops-engineer;
  - nine others: backend-developer, frontend-developer, database-engineer, integration-agent, scaffolding-agent, tech-lead, feasibility-agent, data-mockup-agent and poc-qa-engineer.

  scrum-master does not hold `execute`. Six of the seven GitLab holders hold a shell, as at T812. The total of 15 matches item 49 (a).
- **The narrowing for agents without `execute` is in the generated output.** `.opencode/agents/scrum-master.md` lines 45-54 carry:
  - `bash: deny` and `task: deny`;
  - `read` denies for `gitlab-mcp`, `gitlab-mcp/*`, `*/gitlab-mcp` and `*/gitlab-mcp/*`;
  - `external_directory: "*/gitlab-mcp/*": deny`.

  This matches item 49 (d) and `PREREQUISITES.md:110`. I read one of the 13 files. The other 12 rest on register v20's count **(unverified here)**: `grep_content` searches no hidden directories, so a search under `.opencode/` returned nothing.
- **The client posture table is unchanged in substance** (`PREREQUISITES.md:168-173`):
  - Claude Code: the scrub cannot be used with the `gitlab` entry (live check 2). The sandbox `denyRead` is documented but not verified live.
  - GitHub Copilot / VS Code: `${env:VAR}`, with no mechanism that keeps the token out of the agent's shell.
  - Cline: "no mechanism", and no agent files.
  - Opencode: generated agents are partly covered, and built-in agents and the user's own agent files are not (K-23).
- **I did not diff the history.** Without a shell I could not run `git log v11.0.0..9b9a31f0`. "Nothing in the range changed the token handling on Claude Code, Cline or GitHub" rests on the current state read above and on registers v20 to v25. Those registers record only Opencode changes to SEC-T660-01 (item 49), and v24 line 108 says "SEC-T665-01 is not changed by any source in the range". This is **(unverified as history)**.

## SEC-T660-01: the tool list is not a credential boundary (`SECURITY:MEDIUM`)

**Today's finding.** An agent with a shell runs as the user. It can read the GitLab token file, or the user's `glab` and git credentials, and call the GitLab API directly. With an `api` token it can merge, tag, release or push wherever the token's role allows. The named-tool lists (T667) and `GITLAB_PERMISSION_MODE=modify` limit only the MCP path.

**Grade: `SECURITY:MEDIUM`, unchanged.** Exploitation needs an agent acting outside its brief, for example through prompt injection, and protected branches stop direct pushes to `main` and `develop`. The Immutable Security Constraints were re-checked as T812 did:
- Constraint 5 (privilege escalation): no permission is granted. The token is the user's own identity.
- Constraint 6 (unencrypted data at rest): the token is in memory and the store is encrypted, per the orchestrator. The swap residual belongs to SEC-T665-01.

**Does anything in the range close it? No.** The range narrows the Opencode scope only:
- T841: `bash: deny`.
- T843: `task: deny`.
- T855: map-valued `task` for the orchestrators, and `read` denies on `gitlab-mcp`.
- T861: the `external_directory` deny.

None of these touches the generated agents that hold a shell, the built-in agents, the user's own agents, or the other three clients.

**Scope per platform, as of 2026-11-19:**

| Platform | Who can still read the token | Changed since T812? |
|---|---|---|
| Opencode | (a) the 15 generated agents with `execute`, through their shell; (b) Opencode's built-in agents (`build` has a shell) and the user's own agent files (K-23); (c) the two orchestrators, indirectly, through the shell-holding subagents on their named `agents:` list. They can no longer launch `general` or `build`: this is shown in the resolved rule lists, and a live launch was not observed (K-20). (d) The 13 generated agents without `execute`: the default `gitlab-mcp` directory is covered (`read` and `external_directory` denied). Not covered: a `grep` on a parent directory such as `/dev/shm` or `/run/user/<uid>`, guarded only by that directory's `external_directory` rule (`ask` by default, `allow` under a broad user rule; SEC-T856-02); a token at a non-default name or path; a token linked or copied into a project. | Narrowed in (c) and (d); the finding is not closed |
| Claude Code | All 15 `execute` agents and the user's own session, through Bash. The sandbox `denyRead` and `Read` deny route is client-owned, not verified live, and does not cover same-user processes outside the sandbox | Unchanged (current state read; history not diffed) |
| GitHub Copilot / VS Code | All 15 `execute` agents and the user's session; no mechanism exists | Unchanged (as above) |
| Cline | The whole session (no agent files); no mechanism exists | Unchanged (as above) |

**Is there a harness fix now? No.** T812's rows H1 to H7 were re-checked against today's tree, and none closes the finding:

| # | Fix considered | Closes it? | Why not |
|---|---|---|---|
| H1 | Remove `execute` from the holders | No | The agents' work needs a shell, and the user's own session, Opencode's built-in agents (K-23) and every client without a per-agent mechanism still run as the same user. |
| H2 | `GITLAB_PERMISSION_MODE=readonly` | No | It is enforced only on the MCP path. |
| H3 | Server-side limits | No | They do not stop a shell. |
| H4 | `read_api` or a fine-grained token | No | The roles break, and live check 1 found the fine-grained token not usable (`PREREQUISITES.md:216`). |
| H5 | Claude Code sandbox | No | It is client-owned, covers one client, and is not verified live. |
| H6 | `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB=1` | No | The `gitlab` server does not connect with it. |
| H7 | Isolation through the generated `command` | No | Only an isolated OS user, container or VM owned by the user hides the secret (`:185`). |

The Opencode denies of T855 and T861 are defense in depth for the agents without a shell. They do not close the finding: `PREREQUISITES.md:110` says "These denies are defense in depth, not a boundary".

**Who can close it outside the harness:**
- **The user:** run the agents, or the `gitlab` MCP server, under an isolated OS user, container or VM that holds only the scoped credential and no `glab` or git token (`PREREQUISITES.md:185`). This is the only closure. Narrowing the token's role (Reporter profile, `:123`) and removing `glab`'s stored login reduce the impact but do not close the finding.
- **GitLab:** a token form that is usable for the write roles and scoped per role or per project. Live check 1 found that the fine-grained form offers no Create permission for Issue, Milestone or Issue link. If GitLab adds those, per-role tokens would narrow the blast radius. Even then a shell could read whichever token is present, so this would mitigate the finding, not close it.
- **The client vendors** (Anthropic, Opencode, GitHub and Microsoft, Cline): per-agent credential scoping, meaning secrets that are not readable from an agent's shell, a verified per-agent file deny, or a sandbox per subagent. None exists today on Cline or GitHub (`:181`). On Claude Code it exists only as an unverified, client-owned sandbox, and on Opencode only for agents without a shell.

**Plain statement:** no fix inside the harness exists for SEC-T660-01.

**Review date.** I propose keeping **2027-01-28**, the token renewal date:
- It is the plan's deadline under ADR-015 O1 and is still ahead today.
- The renewal forces a new token setup, which is the natural point to re-check isolation, H5 and any new GitLab token form.
- v12.0.0 must ship before 2027-01-28. If it slips to that date or later, the deadline passes before shipping and the finding needs the user's new acceptance (§ Verdict Rules).
- If the user wants more slack for v12.0.0, a later date needs the user's word. It would also need a new token expiry, which only the user controls.

**Passed deadline (ADR-015 Rule 2, the user's Q2 ruling).**
- The deadline that passed for SEC-T660-01 was the v8.0.0 plan's, "the sprint after v8.0.0". It passed at the latest on 2026-11-01. That acceptance was given for v8.0.0 ("Accept the risk, plan after the release (Recommended)", 2026-10-15). The user's new acceptance for v11.0.0 on 2026-11-13 cured it, and `docs/releases/v11.0.0.md:226` and `:322` say so.
- The v11.0.0 plan's deadline, the review on 2027-01-28, has **not** passed as of 2026-11-19.
- **No new passed deadline exists for v12.0.0.** Whether the v12.0.0 release document must still repeat the old v8.0.0 one, which was already cured at v11.0.0, depends on ADR-015 Rule 2's exact wording. I did not open ADR-015 for this **(unverified)**. My recommendation is one history clause in the Conditions line: "the v8.0.0 plan's deadline passed at the latest on 2026-11-01 and was cured by the v11.0.0 acceptance of 2026-11-13; no deadline has passed since". It costs nothing and is accurate.

## SEC-T665-01: the residual after option D (`SECURITY:MEDIUM`)

**Today's finding.** The token is kept in memory as a mode-0600 file under `/dev/shm` or `$XDG_RUNTIME_DIR`, written from a gpg-encrypted store (`PREREQUISITES.md:155`). Even so, a same-user process can read the file or run the same lookup and call the API with the token, and `modify` does not stop it. tmpfs pages can be swapped, and a hibernation image holds the token, unless swap is encrypted (`:153`, `:182`). One shared Developer-level token remains (DEC-T681-1, as T812 cites it).

**Grade: `SECURITY:MEDIUM`, unchanged.**

**Does anything in the range close it? No.** Register v24 line 108 says "SEC-T665-01 is not changed by any source in the range". v25 records no change. The Opencode `gitlab-mcp` denies reduce which generated agents can read the default file path. They do not touch the same-user residual for shell holders, built-in agents, other clients or the swap part.

**Scope per platform:** the same as SEC-T660-01 for the read residual. The swap and hibernation part is a host property and is the same on every platform.

**Is there a harness fix now? No.** The same rows H1 to H7 apply. The harness already does what it can:
- file mode in memory by default;
- the at-rest warning in `check-gitlab-token.py` (`:161`);
- empty defaults;
- the Opencode denies.

No harness measure can keep tmpfs pages out of swap.

**Who can close it outside the harness:**
- **The user:** an isolated OS user, container or VM that holds only the scoped credential and no `glab` or git token (`:185`), together with encrypted or disabled swap and hibernation on the host for the at-rest part.
- **GitLab and the client vendors:** as for SEC-T660-01. Their work would mitigate the finding, not close it.

**Plain statement:** no fix inside the harness exists for SEC-T665-01.

**Review date:** I propose **2027-01-28**, for the same reasons as SEC-T660-01.

**Passed deadline:** none. SEC-T665-01 never had an earlier deadline (T812; `docs/releases/v11.0.0.md:227`), and its v11.0.0 plan's deadline has not passed.

## Dated statements for citation (ADR-016 condition 4, rows D1 and D2, O-C)

| Id | Dated statement |
|---|---|
| **SEC-T660-01** | As of 2026-11-19, for release v12.0.0, re-checked against develop `9b9a31f0`, the Security Engineer's review T812 (`security-review-t812-v11-no-harness-fix-v1.md`, 2026-11-13) still holds: no fix inside the harness exists for SEC-T660-01. An agent shell runs as the user and can read the GitLab token, or the user's other GitLab credentials, and call the API directly, which no tool list, server mode, generated configuration, Opencode permission rule or token-scope choice available to the harness prevents. Since T812 its scope has narrowed on Opencode only (register item 49: the 13 agents without `execute` are covered for the default `gitlab-mcp` directory; the 15 with `execute`, the built-in agents and the user's own agents (K-23), and the orchestrators through their shell-holding subagents still reach it). Claude Code, Cline and GitHub are unchanged in the current tree. Only an isolated OS user, container or VM that the user sets up can close it. |
| **SEC-T665-01** | As of 2026-11-19, for release v12.0.0, re-checked against develop `9b9a31f0`, the Security Engineer's review T812 (`security-review-t812-v11-no-harness-fix-v1.md`, 2026-11-13) still holds: no fix inside the harness exists for SEC-T665-01. The residual is a same-user process reading the in-memory token file or calling the API with it, plus swap and hibernation of tmpfs pages. The harness can neither create the isolation (an isolated OS user, container or VM, held by the user) nor control the host's swap. No source in `v11.0.0..9b9a31f0` changes it, according to registers v20 to v25. |

Both statements are given before the user is asked for v12.0.0 (O-B). The question to the user must cite this artifact by name and date (O-A).

## Not verified

- The history `v11.0.0..9b9a31f0`. No shell was available, so "Claude Code, Cline and GitHub unchanged" rests on the current state and on registers v20 to v25.
- The other 12 generated Opencode agents without `execute` (one file read), and the 15/13 split in the generated Opencode files. The source frontmatter count of 15 was verified.
- The plan-182 text, ADR-011 and ADR-015 (Rule 2's exact wording on repeating an already-cured deadline). They were not opened.
- The security reviews T844, T856 and T862, which were not opened. Their conclusions are taken from register item 49 (v24) and the v20 to v23 summaries.
- The token's scope, expiry and storage on the user's machine, which are the orchestrator's facts. Whether swap is encrypted on the host.
- Opencode behaviour in a live refused call (K-20), and the Claude Code sandbox route H5 live.
- Whether GitLab or any client vendor has shipped per-role tokens or per-agent credential scoping since 2026-10-24. No web search was made. I treat it as absent **(unverified)**.

## Verdict for this purpose

| Id | Result |
|---|---|
| SEC-T660-01 | **CONFIRMED: no harness fix (T812 still holds; scope narrowed on Opencode, not closed)** |
| SEC-T665-01 | **CONFIRMED: no harness fix (T812 still holds; unchanged)** |

This is a confirmation under ADR-016 condition 4 and row D2. It is not an acceptance, and only the user accepts. Both findings stay `SECURITY:MEDIUM`. They block the v12.0.0 Release gate until the user accepts them for v12.0.0 on a valid plan, or they are fixed. A shipped accepted MEDIUM allows CONDITIONAL_PASS at best. No new finding was raised.

## Points that need the user's word

1. **The acceptance for v12.0.0.** Accept SEC-T660-01 and SEC-T665-01 for v12.0.0, or isolate first, which closes both. The plan to show:
   - Owner: the user (isolation) and devops-engineer (documentation).
   - Fix: "none possible in the harness".
   - Who could close it outside the harness: the user, by an isolated OS user, container or VM holding only the scoped credential and no `glab` or git token. For SEC-T665-01, also encrypted or disabled swap and hibernation. GitLab and the client vendors could mitigate it, but not close it.
   - Deadline: the review on 2027-01-28.
   - This artifact cited, dated 2026-11-19.
   - The Opencode scope from item 49, stated in the question.
2. **The review date.** Keep 2027-01-28 (recommended). v12.0.0 must then ship before it, and a slip to that date or later needs a new acceptance. Any later date needs the user's word and a new token expiry.
3. **Optional, not required for validity:** H5 hardening on Claude Code in the user's own `.claude/settings.json`, and answering "no" to Opencode `external_directory` prompts for parent directories such as `/dev/shm`. These are mitigations, not fixes.
4. **For the orchestrator, not the user:** in SEC-T660-01's Conditions line, say that no deadline has passed since v11.0.0. As history, add that the v8.0.0 plan's deadline passed at the latest on 2026-11-01 and was cured on 2026-11-13. Check ADR-015 Rule 2 for whether that history clause is required or only advisable.

## Blockers

None.
