# Artifact: security-review-t812-v11-no-harness-fix-v1.md

> Immutable once produced; revisions bump `<N>`.

# Security Review T812: harness-fix confirmation for SEC-T660-01 and SEC-T665-01, release v11.0.0

- **Date:** 2026-11-13
- **Reviewer:** security-engineer (read-only; no shell, no write tool, no token use, no GitLab call)
- **Task:** T812 (plan-160). The user's word for this step, verbatim: "Continue with the next best step".
- **Purpose:** ADR-016 condition 4 and rows D1/D2: the Security Engineer's review confirms, before the user is asked, whether a harness fix exists. Under O-C this is a **new review for v11.0.0**, and it also says whether T756's finding still holds.
- **Based on** (worktree `/home/emage/Code/emage/worktrees/agent-orchestrator-T812`, branch `agent/orchestrator/T812`, develop `5de6fbb7` plus the plan commit; search was run on the primary checkout at develop `5de6fbb7`, because `grep_content` refuses a root outside it):
  - `docs/tasks/task-T812.md`; `docs/plans/plan-160-v11-confirmation-sec-t660-t665.md`
  - `docs/decisions/ADR-016-security-engineer-confirmation-as-validity-condition.md` § Decision, O-A to O-D, rows D1/D2
  - `implementation/knowledge/skills/validation-gates/SKILL.md:70` (§ Verdict Rules, the text after T805)
  - `docs/artifacts/security-review-t756-accepted-mediums-v1.md` lines 26, 27 (Part 1) and 74 (Q3)
  - `docs/plans/plan-155-v11-release-decisions.md:13` (§ User decisions 1), `:16`, `:42`
  - `docs/artifacts/tracked-debt-register-v16.md` § 2.3 (lines 94-108), § 6.1 (line 218), § 6.2 items 2 (lines 231, 233) and 40 (lines 237-242), the dates table (line 253)
  - `implementation/PREREQUISITES.md` lines 75, 89, 107, 127, 137, 155-161, 170, 177-187 ("What this does not protect"), 189-203 ("Server-side limits"), 216-218 (live checks)
  - `implementation/knowledge/mcp/servers.yaml:75-93` (the `gitlab` entry)
  - frontmatter `tools:` of the seven GitLab holders under `implementation/knowledge/agents/`
  - `AGENTS.md` § MCP Servers (GitLab grants paragraph, in context)

## Facts from the orchestrator (the orchestrator's statements, not checked by this review)

Since T756 the GitLab token setup is unchanged in kind: one GitLab personal access token, scope `api`, expiring 2027-01-28, kept in a gpg-encrypted store and unlocked into memory once per boot, exposed to the session as a token-file path. Six of the seven GitLab tool holders hold `execute`. The orchestrator did not read the token or the store. Plans 146 to 159 removed the Pi and Gemini platforms and changed CI. None of them changed the token handling.

## What this review verified by reading

- **Six of seven holders have `execute`.** Read in each file's frontmatter: orchestrator, poc-orchestrator, release-manager, qa-engineer, devops-engineer and poc-devops-engineer list `execute`. scrum-master does not. This matches the orchestrator's fact.
- **The `gitlab` entry is unchanged in kind.** `servers.yaml:75` pins `@zereight/mcp-gitlab@2.2.5`. Lines 90-91 keep `GITLAB_PERSONAL_ACCESS_TOKEN` (optional, empty default) and `GITLAB_PERSONAL_ACCESS_TOKEN_FILE`. Line 93 keeps `GITLAB_PERMISSION_MODE: modify`. The pin, the token variables and the mode are the same as described at T756.
- **The closure text is unchanged.** `PREREQUISITES.md:185` says: "**The only closure** is an isolated user, container or VM that holds only the scoped credential and no `glab` or git token; the harness cannot create it." T756 cited the same sentence at `:190`. The line moved, most likely through the Pi and Gemini removals; that cause is inferred **(unverified)**.
- **The other residuals are unchanged.** Lines 181-184 still state them: the same-user read of the token file, `glab`'s own stored copy, no mechanism on clients other than Claude Code, and `modify` not stopping a shell's direct API call (lines 191, 203).
- **I did not check that the history has no change.** Without a shell I could not diff plans 146 to 159. "None changed the token handling" rests on the orchestrator's statement plus the current state read above **(unverified as history)**.

## SEC-T660-01: the tool list is not a credential boundary (`SECURITY:MEDIUM`)

**Grade now: `SECURITY:MEDIUM`, unchanged.**
- An agent with `execute` runs as the user. It can read the token file, or `glab`'s or git's own credentials, and call the GitLab API directly. With an `api` token it can merge, tag, release or push wherever the token's role allows.
- The named-tool narrowing (T667) and `GITLAB_PERMISSION_MODE=modify` limit only the MCP path.
- Exploitation needs an agent acting outside its brief, for example through prompt injection, and protected branches stop direct pushes to `main` and `develop`. That keeps the grade at MEDIUM, not HIGH.
- I re-checked the Immutable Security Constraints:
  - Constraint 5 (privilege escalation): no permission is granted or changed. The capability exists because the token is the user's own identity. I agree with the earlier grades (T660, T665, T756).
  - Constraint 6 (unencrypted data at rest): the token is in memory and the store is gpg-encrypted, per the orchestrator. The swap residual belongs to SEC-T665-01.

**What changed since T756.** Nothing that affects the finding:
- Removing Pi and Gemini leaves four platforms (claude-code, cline, github, opencode). The shell path is the same on each.
- The CI changes (plans 146 to 159, including plan-159's release-gate runner tag) concern the GitLab runner, not the local token.
- T756 already said this finding "is now the same exposure as SEC-T665-01". That still holds.

**Harness fixes considered.** None closes the finding:

| # | Fix considered (inside the repository, its generators, or the installed agent and platform configuration) | Closes it? | Why not |
|---|---|---|---|
| H1 | Remove `execute` from the six GitLab holders | No | Every other agent with `execute`, and the user's own session, also runs as the same user and can read the same file. Those six roles also need a shell for their work (tests, git, CI lint). |
| H2 | Set `GITLAB_PERMISSION_MODE=readonly` in the generated entry | No | The server enforces it only on the MCP path (`PREREQUISITES.md:191, 203`). A shell with the token still calls the API. It would also break the write roles (qa-engineer, scrum-master) and `create_merge_request`. |
| H3 | `GITLAB_DENIED_TOOLS_REGEX`, `GITLAB_TOOLS`, `GITLAB_ALLOWED_PROJECT_IDS` | No | These are server-side only and do not stop a shell (`:203`). Their syntax and reach are partly unverified (`:198`). |
| H4 | Narrower token: `read_api` or fine-grained | No | `read_api` breaks the write roles (`:89`, `:107`). The fine-grained token was not usable for those roles (live check 1, `:216`). The token is also the user's, not the harness's. |
| H5 | Claude Code Bash sandbox `denyRead` on the token file, `~/.config/glab-cli` and `~/.git-credentials`, matching `Read(...)` deny rules, `allowUnsandboxedCommands: false` (`:170`, `:181`) | No | (a) It lives in `.claude/settings.json`, which the installer treats as client-owned and the generator does not write, so it is a user-side setting, not a harness output. (b) It is documented but unverified live (live check 2 failed at its first step, `:217`). (c) It covers only one of the four platforms; on the other three "no mechanism exists" (`:181`). (d) It does not cover same-user processes outside the Bash sandbox, or the other same-user credentials (SSH keys, `~/.netrc`, `GITHUB_PERSONAL_ACCESS_TOKEN`). At best it is a client-specific mitigation, not a closure. |
| H6 | `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB=1` | No | With it the `gitlab` server does not connect (live check 2, `:170`, `:217`). File mode already keeps the token out of the environment (`:137`). |
| H7 | Run the `gitlab` server under another OS user or in a container through the generated `command` | No | Only isolation hides the secret from the agent: a separate OS user, container or VM that the user creates and owns on the host. The harness cannot create it (`:185`). A wrapper in the generated entry would only start a process. Containers are also not a usable route in this environment, because the configured Docker host is not local. |

**Who could close it outside the harness.** The user:
- Run the agents, or the `gitlab` MCP server, under an isolated OS user, container or VM that holds only the scoped credential and no `glab` or git token, so that agent shells cannot read the token (`PREREQUISITES.md:185`).
- Optionally, narrow the blast radius further by the token's role (the Reporter profile, `PREREQUISITES.md` § "Reporter profile", not opened in this review **(unverified)**) and by removing `glab`'s stored login (`:183`). These reduce the impact but do not close the finding.

**Review date 2027-01-28.** This is the plan's deadline under ADR-015 O1, and it is the token renewal date (A-13; register v16 line 253). It still fits as long as v11.0.0 ships before 2027-01-28.
- If the release slips to or past 2027-01-28, the deadline passes before shipping. Under § Verdict Rules that "counts as moved later" and needs the user's new acceptance.
- Renewal is also the natural point to re-check H5 and isolation.

**The old deadline has passed (ADR-015 Rule 2 / O5).** Confirmed: the deadline "the sprint after v8.0.0" (`docs/releases/v8.0.0.md:261, :300`, as T756 quotes them) has passed.
- T756 found no sprint date. At the latest it passed when v9.0.0 shipped on 2026-11-01. That date is T756's; I did not re-read `docs/releases/v9.0.0.md` **(unverified independently)**.
- The plan carrying that deadline was set at v8.0.0. The user then accepted the finding for v10.0.0 only (register v16 line 94).
- **For the orchestrator to settle in the Conditions line:**
  - The deadline that passed is the v8.0.0 plan's.
  - The plan shown at v10.0.0 (T756 Q3) already named the review on 2027-01-28, which has not passed. I did not read `docs/releases/v10.0.0.md` **(unverified)**.
  - The Conditions line should name the date (at the latest 2026-11-01) and the release the old acceptance was given for, without blending the two plans.

## SEC-T665-01: the residual after option D (`SECURITY:MEDIUM`)

**Grade now: `SECURITY:MEDIUM`, unchanged.**
- A same-user shell can read the token file, or call the API with it, and `modify` does not stop that.
- tmpfs can be swapped unless swap is encrypted, and a hibernation image holds it too (`:182`). Whether swap is encrypted on the user's host is **(unverified)**.
- One shared Developer-level token remains an accepted residual (DEC-T681-1, as T756 cites it).

**What changed since T756.** Nothing that affects the finding:
- File mode in memory, from a gpg-encrypted store, is unchanged in kind (orchestrator's fact; `PREREQUISITES.md:155` describes that setup as "the user's, since 2026-10-31").
- The `check-gitlab-token.py` behaviour described at `:161` is the same posture as at T756. The script itself was not opened **(unverified)**.

**Harness fixes considered.** The same rows H1 to H7 apply, and none closes the finding:
- The residual is exactly "a same-user process can read the same file" (`:155`, `:181`). Only H7, isolation outside the harness, addresses it.
- The harness already does what it can (file mode in memory by default, the at-rest warning, the empty defaults, the literal-value warning on update).
- No harness-side measure can stop swap from holding tmpfs pages; encrypted or disabled swap is a host setting.

**Who could close it outside the harness.** The user, the same way as SEC-T660-01:
- an isolated OS user, container or VM that holds only the scoped credential and no `glab` or git token (`:185`)
- encrypted or disabled swap and hibernation on the host, for the at-rest part of the residual

**Review date 2027-01-28.** It fits, as for SEC-T660-01, while v11.0.0 ships before that date. SEC-T665-01 never had an earlier deadline (T756 line 27), so the old-deadline duty does not apply to it.

## Dated statements for citation (ADR-016 condition 4, rows D1/D2)

| Id | Dated statement |
|---|---|
| **SEC-T660-01** | As of 2026-11-13, for release v11.0.0, no fix inside the harness exists for SEC-T660-01: an agent shell runs as the user and can read the GitLab token, or the user's other GitLab credentials, and call the API directly, which no tool list, server mode, generated configuration or token-scope choice available to the harness prevents. Only an isolated OS user, container or VM that the user sets up can close it. T756's finding that no harness fix exists still holds. |
| **SEC-T665-01** | As of 2026-11-13, for release v11.0.0, no fix inside the harness exists for SEC-T665-01: the residual is a same-user process reading the in-memory token file or calling the API with it, plus swap of tmpfs pages, and the harness can neither create the isolation (an isolated OS user, container or VM, held by the user) nor control the host's swap. T756's finding that no harness fix exists still holds. |

Both statements are given before the user is asked again (O-B). The question to the user must cite this review by name and date (O-A).

## Not verified

- That no commit in plans 146 to 159 changed the token handling: this rests on the orchestrator's fact plus the current state read above, with no history diff.
- The token's scope, expiry and storage on the user's machine (orchestrator's facts, not read, by constraint).
- Whether swap is encrypted on the user's host.
- The date v9.0.0 shipped (2026-11-01, T756's), and the contents of `docs/releases/v8.0.0.md`, `v9.0.0.md` and `v10.0.0.md` (not re-read).
- The Claude Code sandbox route H5, which is unverified live (as `PREREQUISITES.md` already says).
- `PREREQUISITES.md` § "Reporter profile" and `scripts/check-gitlab-token.py`, which were not opened.
- The cause of the line shift from `:190` to `:185`.

## Verdict for this review's purpose

| Id | Result |
|---|---|
| SEC-T660-01 | **CONFIRMED no harness fix** |
| SEC-T665-01 | **CONFIRMED no harness fix** |

This is a confirmation under ADR-016 condition 4, not an acceptance. Only the user accepts. Both findings stay `SECURITY:MEDIUM` and block the v11.0.0 Release gate until the user accepts them again for v11.0.0 on a valid plan, or they are fixed. No new finding was raised.

## Points that need the user's word

1. **The acceptance itself.** Re-accept SEC-T660-01 and SEC-T665-01 for v11.0.0 on the plan shown, or isolate first. The plan shown: owner the user (isolation) and devops-engineer (documentation); fix "none possible in the harness"; deadline: the review on 2027-01-28; this review cited.
2. **Optional, not required for validity: H5 hardening on Claude Code.** The user may choose to add the sandbox `denyRead` and `Read` deny rules for the token file and the `glab` and git credentials in their own `.claude/settings.json`. It is a mitigation on one client and is unverified live; it is not a fix, and it does not change the plan.
3. **For the orchestrator, not the user:** the SEC-T660-01 Conditions line should name the passed deadline ("the sprint after v8.0.0", at the latest 2026-11-01) and the release that acceptance was given for, separate from the v10.0.0 plan's 2027-01-28 review.

## Blockers

None.
