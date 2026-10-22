# emage.code v3 — Workspace Conventions

## Team Model
- Two orchestration tracks: Production (`@orchestrator`) and PoC (`@poc-orchestrator`)
- Only orchestrators are user-invocable. All other agents are subagents.
- Orchestrators delegate via structured briefs. Agents do not self-activate.

## Lifecycle States
```
pending → in_progress → blocked → in_review → done | cancelled
```

## Task Protocol
- Task list: `docs/tasks/active-tasks.md` — columns: `ID | Title | Owner | Status | Priority | Depends on | Last update`
- **INVARIANT:** `active-tasks.md` MUST NEVER hold a `done` or `cancelled` row. Terminal rows move to `docs/tasks/completed-tasks.md` (columns: `ID | Title | Owner | Done on | Outcome / artifact`) in the same edit.
- Archival is orchestrator-only and immediate. See skill `task-management` § "Complete a Task".
- Task briefs: `docs/tasks/task-<ID>.md` (objective, inputs, outputs, acceptance criteria)
- Only orchestrators create/transition tasks. Agents report completion and blockers.
- Sequential IDs: `T001`, `T002`, … Priorities: `P0` (critical path), `P1`, `P2`.

## Artifact Versioning
- Immutable artifacts: `<type>-v<N>.md` (e.g. `requirements-v1.md`, `architecture-v1.md`)
- Every artifact references its inputs: `Based on: requirements-v1.md`
- Revisions create new versions, never overwrite.

## Checkpoint Protocol
- Checkpoints: `docs/checkpoints/checkpoint-<SEQ>-<phase>.md`
- Written at every phase boundary by the orchestrator.
- Include: completed tasks, key decisions, blockers, token metrics, next steps.
- Agents receive latest checkpoint + task brief (not full history).

## Decision Log
- ADRs: `docs/decisions/ADR-<NNN>-<slug>.md`
- Each decision references requirements and task IDs.
- Immutable once accepted; superseded decisions link to replacement.

## Delegation Brief
1. **Objective** — clear, one-paragraph description
2. **Context** — current phase + latest checkpoint reference
3. **Inputs** — specific artifact versions to reference
4. **Constraints** — token budget, file ownership boundaries, technology constraints
5. **Expected Outputs** — artifact names and format
6. **Acceptance Criteria** — specific, testable conditions
7. **Blocker Protocol** — reminder to report blockers with type and severity

## Blocker Protocol
- Types: `technical` | `dependency` | `unclear_requirements` | `external`
- Severities: `critical` | `major` | `minor`
- Max 2 retries before user escalation. Agents MUST NOT silently fail.

## Validation Gates
- VERDICTS: `PASS` | `CONDITIONAL_PASS` | `FAIL`
- Review agents (Tech Lead, QA, Security) MUST NOT modify code during review.
- `FAIL` blocks progression. Orchestrator creates fix tasks and re-routes.
- `CONDITIONAL_PASS` proceeds with tracked conditions added to the task list.

## Skill Workflow (mandatory)

Before implementation, debugging, review response, or completion claims, agents
MUST check applicable skills in the active platform projection (`.github/skills/`, `.gemini/skills/`, `.opencode/skills/`, `.pi/skills/`, `.claude/skills/`, `.cline/skills/`) (or invoke `/discover-skills`).

| Situation | Required skill |
|-----------|----------------|
| Any bug, test failure, unexpected behavior | `systematic-debugging` |
| Code review feedback to implement | `receiving-code-review` |
| Marking work done, commit, MR, release | `verification-before-completion` |
| Phase or validation transition | `validation-gates`, `checkpoint-protocol` |
| Before any checkpoint, release, or after `install --update` | run `/validate-tasks` |

Skipping a mandatory skill requires orchestrator approval and a logged exception
in the task brief or checkpoint.

## Code Standards
- See platform instruction projections: `.github/instructions/coding-standards.instructions.md`, `.gemini/instructions/coding-standards.md`, `.opencode/instructions/coding-standards.md`, `.pi/instructions/coding-standards.md`, `.claude/rules/coding-standards.md`, `.clinerules/coding-standards.md`.
- Max 50-line functions, max 4 parameters, early returns.
- Conventional Commits: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`.
- GitFlow: `main`, `develop`, `feature/*`, `bugfix/*`, `release/*`, `hotfix/*`.

## Security
- See platform security instruction projections: `.github/instructions/security-guidelines.instructions.md`, `.gemini/instructions/security-guidelines.md`, `.opencode/instructions/security-guidelines.md`, `.pi/instructions/security-guidelines.md`, `.claude/rules/security-guidelines.md`, `.clinerules/security-guidelines.md`, and `implementation/SECURITY.md`.
- OWASP Top 10 compliance required.
- No secrets in code — use environment variables or vault. **Never commit live API keys.**
- Parameterized queries only.
- Input validation at all system boundaries.

## Knowledge Base
- Source knowledge lives in the emage.code repository under `implementation/knowledge/`; this target uses installed platform projections.
- **Every** per-platform folder is **derived**, not authored — `.github/`, `.gemini/`, `.opencode/`, `.pi/`, `.claude/`, `.cline/` and `.clinerules/`, with no exceptions and `.claude/` explicitly included. Each is owned by a generator and an installer, never by the author, so **do not hand-edit any of them**: author in the emage.code repository's `implementation/knowledge/` and regenerate. Both generators are required:
  - `node implementation/scripts/sync.mjs --root implementation` (`make sync`) writes the platform mirrors **under `implementation/.<platform>/`** — *not* to the top-level folders. There is no `scripts/sync.mjs`; that path fails with `Cannot find module`.
  - `python3 implementation/scripts/generate-registry.py` refreshes `implementation/registry/index.json`, whose per-entry `checksum` any source edit invalidates — running `sync.mjs` alone leaves the registry stale.
  - The **top-level** folders are written by `scripts/install.sh`, and `--update` replaces each of them wholesale with `rsync -a --delete`: a hand-written file there is **deleted, not merged**. The installer warns about this itself — "`--update` replaces `$TARGET/<folder>` entirely (rsync --delete)… Other local edits there will be lost." Only client-owned paths are spared (`.claude/settings.json`, `.claude/settings.local.json`, and `.github/workflows/`, `ISSUE_TEMPLATE/`, `PULL_REQUEST_TEMPLATE*`, `CODEOWNERS`, `dependabot.y*ml`, `FUNDING.yml`, `copilot-instructions.md`); `agents/`, `skills/`, `commands/`, `rules/` and the whole of `.clinerules/` are not.
  - Read-only drift gates, safe to run at any time: `node implementation/scripts/sync.mjs --root implementation --check` (`make verify`) and `python3 implementation/scripts/generate-registry.py --check`.
- Use the installed platform folders (`.github/`, `.gemini/`, `.opencode/`, `.pi/`, `.claude/`, `.cline/`, `.clinerules/`) as runtime references in this target project.
- Cline auto-detects the root `AGENTS.md` natively — no projection is needed for that file itself, it already works as-is. Cline users should also check `.clinerules/` for path-scoped project rules.

## MCP Servers
Declared in platform MCP configs (`.vscode/mcp.json`, `.gemini/settings.json`, `.opencode/opencode.json`, `.pi/mcp.json`, `.mcp.json`, `.cline/mcp.json`). Each server is tagged:

| Tag | Emitted to |
|-----|-----------|
| `core` | every platform |
| `extended` | platforms whose manifest opts in (all except `github`: `gemini`, `opencode`, `pi`, `claude-code`, `cline`) |

### Core servers (always available)

| Server | Purpose | Used By |
|--------|---------|---------|
| `gitlab` | Repository, issues, MRs, pipelines | Named tools only (no agent holds the whole server): Orchestrator, PoC Orchestrator, Scrum Master, QA Engineer, DevOps, Release Manager, PoC DevOps |
| `playwright` | Browser automation (hardened; blocks local-app URLs, see below) | Named tools only: QA, Frontend, Demo Agent, PoC QA |
| `memory` | Persistent knowledge graph | Orchestrator, PoC Orchestrator (team memory) |
| `sequential-thinking` | Complex problem decomposition | Solution Architect, Orchestrator, PoC Orchestrator |
| `brave` | Technology discovery | No agent lists its tools (Technology Scout and Feasibility hold no token); available to the session |
| `context7` | Framework/API documentation | No agent lists its tools (Technology Scout and Integration hold no token); available to the session |
| `hindsight` | Remote memory-layer endpoint (`HINDSIGHT_MCP_URL`) | No agent lists its tools; available to the session |

GitLab grants: no agent holds the whole `gitlab` server any more (T667). At `@zereight/mcp-gitlab@2.2.5` the server registers 275 tools (the raw `gitlab_api_request` tool among them is opt-in through `GITLAB_TOOLSETS=api` only), including merge, push, delete and branch/tag/release creation; seven agents hold named tools only. scrum-master (24 tools: issues, notes, labels, milestones, read-only merge request lookups), qa-engineer (20 tools: bug issues and notes, read-only merge request, pipeline and job lookups), orchestrator (16 tools: read-only issue, merge request, pipeline and branch lookups, and `create_merge_request`), poc-orchestrator (8 tools: merge request lookups, `create_merge_request`, pipeline lookups), devops-engineer (11 tools: read-only pipeline, job, merge request and test report summary lookups and the two CI lint tools `validate_ci_lint` and `validate_project_ci_lint`, which validate YAML and change nothing), release-manager (17 tools: read-only merge request, approval state, pipeline, issue, branch, tag and release lookups, and `create_merge_request`) and poc-devops-engineer (6 tools: pipeline lookups and the two CI lint tools) hold none that merges, approves, pushes, writes files, deletes, creates branches, tags or releases, triggers, retries or cancels pipelines, reads CI variables, environments or deployments, or sends a raw API request; only qa-engineer reads raw job output (T660 for qa-engineer and scrum-master, T666 for the two orchestrators, T667 for the other three; SEC-T657-02, SEC-T660-04). By policy the top-level session merges after its own verification and creates the tag and the release with the user's approval; release-manager opens the release merge requests and reads the result. This is a tool-list narrowing and a policy, not an enforcement. Six of the seven roles hold `execute`, and the setup instructions export `GITLAB_PERSONAL_ACCESS_TOKEN` into the environment that starts the assistant, so a shell in those roles can merge, tag, release or push with that token. Use a least-privilege token (scope `api`, limited by role) and, preferably, the token file `GITLAB_PERSONAL_ACCESS_TOKEN_FILE` (T665, SEC-T660-01: mitigated, not closed; scope and role table, per-client posture and live checks: `implementation/PREREQUISITES.md`, "GitLab token"); the generated entry also sets `GITLAB_PERMISSION_MODE=modify`. The pinned server reads further operator controls that the generated entry does not set and that you can add to the `env` of your own `gitlab` entry (a key you add there is kept by `install.sh --update`; Opencode names that map `environment`): `GITLAB_DENIED_TOOLS_REGEX` (a deny-list by pattern; the server's README gives no syntax or matching rules), `GITLAB_ALLOWED_PROJECT_IDS` (a project allow-list that the README says is "checked only for `/projects/:id` paths"; that endpoints such as `/search`, `/users` and `/groups/:id` are therefore not constrained is from the README on main, not matched to 2.2.5, unverified; whether it constrains the named tools of these roles is unverified), and `GITLAB_TOOLS` and `GITLAB_TOOLSETS` (which tools the server registers; an explicit `GITLAB_TOOLS` list replaces the default `core` toolset and does not merge with it). `GITLAB_PERMISSION_MODE` takes `readonly`, `modify` or `full` (per the README; unverified, see PREREQUISITES). None of them stops a shell that holds the token from calling the API; details and the unverified points: `implementation/PREREQUISITES.md`, "Server-side limits". `create_merge_request` can target any project and branch the token reaches and can start merge request pipelines; the CI lint tools with `dry_run` resolve `include:` entries server-side. The user's own main session and Opencode's built-in agents are not agents of this set and are unaffected. By default the server exposes only its `core` toolset until `discover_tools` activates the others (`milestones`, `labels`, `pipelines`, `issues`, `merge_requests`, `ci`, `tags`, `releases`); `discover_tools` cannot widen the seven roles' allowlist on a platform that enforces one, but it changes the visible toolset for the whole session. All seven lists include `discover_tools`, which the server needs to expose the non-default toolsets (`milestones`, `labels`, `pipelines`, `issues`, `ci`, `tags`, `releases`). This holds on Claude Code and, according to the vendor documentation (not observed in a live run), on GitHub Copilot/VS Code, and on Pi for an agent whose file is passed to `pi --tools` with an `mcp__` entry (vendor documentation and source; other consumers of the agent files are unverified; not observed in a live run); on Gemini CLI the agent tool list does not restrict MCP tools, so every agent can still call every GitLab tool there. On Opencode the generator writes per-agent `<server>_*: false` entries for every non-exempt server an agent holds no token of, so the 21 agents without a GitLab tool cannot call one, and the seven named holders (`gitlab_*: false` before their named allows) can call only their named GitLab tools there (per-agent, T663; documented and read from vendor source, not observed in a live tool call; `docs/artifacts/mcp-agent-denials-v1.md`).

The `fetch` server was removed in v8.0.0 (audit SEC-T646-01): it followed redirects blindly. Agents read web pages with the platform `web` tool. The `playwright` entry is hardened but is not a security boundary; see `docs/wiki/mcp-servers.md`. Its `--blocked-origins` list denies `localhost`, `127.*`, `*.localhost`, `10.*`, `192.168.*` and `172.16`-`172.31`, so E2E testing of a local dev server with the shipped entry fails with `ERR_BLOCKED_BY_CLIENT`. For local apps add a user-owned second entry named `playwright-local` (unrestricted, with the warning in `implementation/PREREQUISITES.md`); `install.sh --update` keeps it because the merge keeps names the generator does not own. Installed projects should add `.playwright-mcp/` to their `.gitignore`. The four Playwright agents (QA, Frontend, Demo Agent, PoC QA) hold named, non-`unsafe` Playwright tools, not the whole server; the tool-name form differs per platform. The narrowing is in force on Claude Code, on GitHub Copilot/VS Code (by documentation) and on Pi for an agent that lists an `mcp__` tool. On Opencode and Gemini CLI an agent's tool list does not restrict MCP tools, so since T658 the generator denies exactly six Playwright tools server-wide where the platform documents a mechanism: `browser_run_code_unsafe`, `browser_evaluate`, `browser_file_upload`, `browser_drag`, `browser_drop` and `browser_network_request` (one list, `denyTools` of the `playwright` entry in `servers.yaml`). Opencode: top-level `permission` entries `playwright_<tool>: deny` in `.opencode/opencode.json`; Gemini CLI: `excludeTools` on the `playwright` entry of `.gemini/settings.json`. Both are documented and read from vendor source, not observed in a live run. On Opencode the last matching rule wins and an agent's own rules come after the global ones, so an agent file of your own that allows one of these names (or `playwright_*`) overrides the denial. The denial is last only inside the one file the installer writes: Opencode merges several configuration sources, so an allow for one of these names in another configuration source, in `OPENCODE_CONFIG_CONTENT` or in a managed policy that Opencode applies later can override it too. On Gemini CLI every agent can still call the other tools of every configured server, including the GitLab write tools. Since T663 the Opencode generator also writes per-agent `false` entries into every agent file (per-agent): the six Playwright names for every agent, and `<server>_*: false` for every server that the agent holds no token of and that is not exempt (`denyUnlessGranted: true` on gitlab, playwright, memory, sequential-thinking, security-audit, poc-security-audit, context-retriever, filesystem, git and supabase), after its allows; an agent that holds only named tools of a server (all seven GitLab holders for `gitlab`: qa-engineer, scrum-master, orchestrator, poc-orchestrator, devops-engineer, release-manager and poc-devops-engineer; the Playwright agents, the security agents, context-retriever) gets that server's wildcard first, so it can call only its named tools. The read/search and memory-layer servers brave, context7, hindsight, cwso, hf-mcp-server and toolradar are exempt (`denyUnlessGranted: false`, user decision of 2026-10-16), so generated agents, including a primary orchestrator, keep them; a non-exempt server that no agent lists (filesystem, git, supabase) is denied in every generated agent file, as on Claude Code, where a subagent without the token cannot call it; the entries are documented and read from vendor source, not observed in a live tool call (`docs/artifacts/mcp-agent-denials-v1.md`, `docs/artifacts/mcp-agent-denials-evidence-v1.md`). On Opencode the `true` entries an agent holds come after your global config, so your own global `ask` or `deny` on a tool an agent holds is silently overridden for that agent; for example a global `ask` on `gitlab_create_merge_request` is overridden for the three agents that hold it (orchestrator, poc-orchestrator, release-manager). Since T667 no agent holds the whole `gitlab` server, so every `true` entry is a named tool and you can still override only the tools an agent holds; a tool that no agent holds, such as `gitlab_merge_merge_request`, stays denied in every generated agent file whatever your global rule says (`gitlab_*: false` comes first in each holder's map). No supported way through the generated files or through your project or global configuration keeps a prompt there (an `agent.<name>.permission` entry in your project config is also placed before the agent's own rules); only a source that Opencode loads after the agent files can, the environment variable `OPENCODE_CONFIG_CONTENT` (observed on opencode-ai 1.19.2) and, by source reading only, the managed configuration (SEC-T657-04, SEC-T663-03; `docs/artifacts/mcp-agent-denials-evidence-v1.md`). The `<server>_*` wildcards also match a user-owned server whose cleaned name starts with that prefix and an underscore (a server `gitlab_ee` is matched by `gitlab_*`, `gitlab-ee` is not); for an agent without the server that fails closed. Saved "always" approvals do not undo a deny: the legacy runtime hides a tool whose last matching rule is a deny, and the current core tests `denied()` before it adds saved approvals (source reading; an approval saved before the deny existed is unverified). Opencode's built-in agents (build, plan, general, explore, ...) and agent files of your own get no per-agent deny and no global GitLab deny; only the server-level `permission` of `.opencode/opencode.json` (the six Playwright tools) applies to them, so every other tool of every configured server, GitLab included, remains reachable through them. That gap is a decision of the user (2026-10-16, "No, document the gap only") and is tracked. A user-owned `playwright-local` entry is another server name and is not denied by either list. `install.sh --update` keeps your own `permission` and `excludeTools` entries and re-adds the generated ones, and replaces `.opencode/agents/` as a tree (agent files are not merged) (`docs/wiki/mcp-servers.md`, `docs/artifacts/mcp-server-denials-v1.md`, `docs/artifacts/mcp-tool-name-mapping-v1.md`; both artifacts were recorded before Cursor was removed, so their Cursor rows are historical).

### Extended servers (opt-in)
`cwso`, `hf-mcp-server`, `context-retriever`, `security-audit`, `poc-security-audit`, `filesystem`, `git`, `supabase`, `toolradar`. Most require additional credentials — see `servers.yaml` for the env-var contract.

## Token Governance
| Phase | Budget |
|-------|--------|
| Planning | ≤ 80k tokens |
| Architecture | ≤ 80k tokens |
| Implementation | ≤ 120k tokens |
| QA / Security / Release | ≤ 60k tokens |

Track usage in checkpoints. Compress context and start fresh delegation when approaching budget.
