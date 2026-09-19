# Scoped, non-`Bash` execution/read primitive for `@security-engineer` and `@context-retriever` — v1

**Status:** Proposed (design pass only — no implementation, no `.mcp.json`/`servers.yaml`/agent
`tools:` change, no `sync.mjs` change, no live adversarial test; all deferred, see §6).
**Owner:** solution-architect
**Task:** T457 (design pass, Expected Outputs item 1 only — items 2–4 are explicitly out of scope
for this dispatch)
**Based on:**
- `docs/tasks/task-T457.md` (full brief, read in full this session from this worktree)
- `docs/plans/plan-039-t457-tool-scoping-followup.md` (original, now-superseded framing — read for
  history; its central premise, "no scoped primitive exists and `.mcp.json` may never be touched,"
  is superseded by `plan-049` and is not carried forward here except where explicitly noted as
  disagreement)
- `docs/plans/plan-049-t457-scoped-primitive-reinvestigation.md` (primary, current evidence base —
  §1's `.mcp.json`-constraint-lifted finding, §2.1's dedicated-MCP-server direction for
  `@context-retriever`, §2.2's composed-allowlist direction for `@security-engineer`, §3's
  `filesystem` registry defect, §4's unresolved per-platform gap — all cited by section number
  below, not re-derived)
- `implementation/knowledge/agents/security-engineer.md`, `implementation/knowledge/agents/
  context-retriever.md` (current `tools:` grants, both include `execute`, re-read fresh this
  session)
- `implementation/platforms/*.json` (all 7 platform manifests, re-read fresh this session — see §4)
- `implementation/knowledge/mcp/servers.yaml`, root `.mcp.json` (read-only reference, re-read fresh
  this session — see §3)
- `implementation/runtime/memory/context_retriever.py`, `deploy/docker-compose-context-retriever.yml`
  (the concrete existing module/deployment target for §1's `@context-retriever` recommendation)
- `implementation/scripts/sync.mjs` (`applyAgentFrontmatter()`, `emitMcp()`, `parseServersYaml()` —
  re-read in full this session to independently confirm plan-049's passthrough claim and to check
  each platform's actual tools-frontmatter code path, not just its manifest declaration)
- `docs/artifacts/mcp-header-url-templating-design-v1.md` (T483, structural/rigor precedent — this
  document mirrors its explicit-alternatives, explicit-trade-offs, explicit-citation, explicit
  not-decided-here structure)
- `docs/artifacts/mcp-platform-contract-v1.md` (T420, the per-platform MCP contract any new server
  registration in §1's recommendation would need to conform to)
- Official upstream documentation fetched fresh this session (WebSearch/WebFetch, no `ctx7` grant
  in this session's tool set): Claude Code sub-agent docs (already cited by plan-049, not
  re-fetched here); VS Code Copilot custom-agent docs (`raw.githubusercontent.com/microsoft/
  vscode-docs/main/docs/agent-customization/custom-agents.md`); a VS Code GitHub issue
  (`microsoft/vscode#269600`); Cursor subagent and `permissions.json` docs (`cursor.com/docs/
  subagents`, `cursor.com/docs/reference/permissions`); OpenCode docs (`opencode.ai/docs/agents/`,
  `/docs/tools/`, `/docs/mcp-servers/`, `/docs/config/`); Gemini CLI subagent docs
  (`geminicli.com/docs/core/subagents/`, `raw.githubusercontent.com/google-gemini/gemini-cli/main/
  docs/core/subagents.md`); the official MCP reference-server READMEs for `filesystem` and `git`
  (`raw.githubusercontent.com/modelcontextprotocol/servers[-archived]/main/src/{filesystem,git}/
  README.md`); an npm registry lookup for `@modelcontextprotocol/mcp-git` (404 — see §3.2, a new
  finding this session, not in plan-049).

---

## 0. Scope of this document

This is a design artifact only, per this dispatch's explicit constraints. It does **not**: edit
`.mcp.json`, `servers.yaml`, any agent `tools:` grant, `sync.mjs`, or any platform projection file;
run or propose running any code; touch the task ledger; or resolve the one real open decision this
document exists to surface (§2). It answers task-T457.md's Expected Outputs item 1 only.

## 1. Evaluation of candidate mechanisms

`task-T457.md`'s Expected Outputs item 1 names three candidates to evaluate: **(a)** a dedicated
MCP server exposing a narrow, read-only, non-shell primitive; **(b)** a per-platform tool-map
change mapping a new abstract tool name to a scoped command allowlist rather than full `Bash`;
**(c)** "any other viable mechanism ... not obvious at task-creation time." `plan-049` §1.2 found a
fourth option since task creation: **(d)** Claude Code's native exact-MCP-tool-name allowlisting
(`mcp__<server>__<tool>` tokens in an agent's `tools:` list), which this repo's generator already
passes through unmodified for Claude Code with **zero `sync.mjs` change** (confirmed independently
this session — see §1.4).

### 1.1 Option (b) — new abstract tool name mapped to a scoped shell-command allowlist

This would mean adding a new `toolMap` key (e.g. `read_execute`) to `claude-code.json` (and
whichever other platform manifests have an equivalent map — today, only `claude-code.json` has any
`toolMap` at all; see §4) that expands to some platform-native construct enforcing "only these
specific shell commands, nothing else." **Rejected as the primary mechanism, for two reasons:**

1. **No such platform-native construct exists to map onto.** Claude Code's `toolMap` (`implementation/
   platforms/claude-code.json` lines 16–24) maps an abstract token to one or more of the platform's
   own built-in tool names (`Read`, `Edit, Write`, `Bash`, etc.) — it is a renaming/grouping layer,
   not a policy engine. There is no Claude Code built-in tool called, say, `RestrictedBash` that
   takes a command allowlist as a parameter; `Bash` is unrestricted or absent, nothing in between.
   Building "a scoped command allowlist" would mean either (i) a wrapper shell script the agent is
   instructed to always invoke instead of raw commands (which is prose enforcement again — the
   model could still call `Bash` directly with anything else, since the underlying grant is still
   full `Bash`) or (ii) an actual sandboxing/allowlisting layer between the model and the shell,
   which does not exist in this repo's tool vocabulary and would be a much larger infrastructure
   build than either (a) or (d).
2. **It does not compose with the one real technical control this repo already has for narrowing a
   tool grant** — MCP tool-name allowlisting (§1.3–1.4) — because `execute`/`Bash` is a single
   opaque built-in tool, not an MCP server with individually nameable tools. Any "scoped `execute`"
   design would have to invent its own enforcement layer from scratch rather than reuse the
   platform's own resolution/pooling step the way (a) and (d) both do.

**Not recommended.** This is the shape of primitive `plan-039` originally imagined not existing
("no narrower, scoped ... primitive in this repo's tool vocabulary to grant instead" —
`plan-039` line 40–41, restating `task-T457.md` line 40); `plan-049` §1.2 found that a *different*
kind of scoped primitive (MCP tool-name granularity) already exists and needs no such invention.
Building (b) from scratch when (a)/(d) already provide real, platform-enforced scoping is not
justified.

### 1.2 Option (c) — any other viable mechanism

Investigated: a per-agent shell wrapper/sandbox (Docker, gVisor, seccomp) invoked in place of raw
`Bash`. This is a real, heavier-weight mechanism used elsewhere in the industry, but: (i) it is
infrastructure this repo does not currently have any analog for (no sandboxed-execution service is
registered anywhere in `servers.yaml` or `AGENTS.md`'s MCP server table); (ii) it would require
new deployment infrastructure (a container runtime available to every platform's agent session, not
just Claude Code) far beyond this task's P1, hardening-not-new-capability scope; (iii) `context-
retriever.py`'s own docstring already states this repo's actual invocation model is "a direct
in-process Python call from an agent's `execute`/Bash tool grant, not a standalone container" (cited
by `plan-049` §2.1, itself citing the module directly) — a sandboxed-shell mechanism would be a
strictly larger architectural change than either agent's actual workload requires. **Not recommended
as a first-pass mechanism**; noted as a theoretically viable but disproportionate option, not
pursued further here.

### 1.3 Option (a) — dedicated MCP server, and option (d) — exact-MCP-tool-name allowlisting

These two are not actually mutually exclusive alternatives; they are complementary layers of the
same real mechanism this repo already has, confirmed independently this session by re-reading
`sync.mjs`'s `applyAgentFrontmatter()` directly (lines 250–286) and `claude-code.json`'s `toolMap`
(lines 16–24, unchanged from `plan-049`'s citation):

```js
let tools = data.tools;
...
} else if (cfg.tools === 'string') {
  if (Array.isArray(tools)) {
    const toolMap = cfg.toolMap || {};
    const expanded = tools.flatMap((t) =>
      Object.prototype.hasOwnProperty.call(toolMap, t)
        ? toolMap[t].split(',').map((s) => s.trim())
        : [t]
    );
    out.tools = [...new Set(expanded)];
  }
}
```

(`implementation/scripts/sync.mjs` lines 267–276, `cfg.tools === 'string'` branch — the branch
`claude-code.json` actually uses, since its manifest declares `"tools": "string"` at line 14.) Any
source token not a key of `toolMap` (`read`, `search`, `edit`, `execute`, `agent`, `web`, `todo` —
`claude-code.json` lines 17–23) is returned via the `[t]` fallback, i.e. passed through literally.
This is independently re-confirmed, not just re-asserted from `plan-049`: it is exactly the code
path that already carries `security-engineer.md`'s pre-existing `mcp__fetch` token (`implementation/
knowledge/agents/security-engineer.md` line 4, `tools: [read, search, execute, web, mcp__fetch]`)
into its generated `.claude/agents/security-engineer.md` frontmatter unchanged today. **(d)** is
therefore the *delivery* mechanism (how a scoped grant reaches Claude Code with zero generator
change); **(a)** is a *design choice about what capability to expose* through that same delivery
mechanism when the underlying capability doesn't already exist as a public, off-the-shelf MCP
server tool. `@context-retriever` needs (a)+(d) together (a new server, delivered via exact-tool-
name grant); `@security-engineer` (§2) is evaluated against composing *existing* registered servers
via (d) alone, versus a new (a)-style server, versus status quo.

### 1.4 Recommendation for `@context-retriever`: a dedicated single-tool MCP server (confirms `plan-049` §2.1, with an additional structural argument for why)

**Recommended direction:** build a small `stdio`-transport MCP server that imports
`implementation.runtime.memory.context_retriever.ContextRetriever` (`implementation/runtime/memory/
context_retriever.py`, re-read fresh this session) and exposes exactly one MCP tool — call it
`retrieve(query, top_k)` — with no other capability. Register it in `servers.yaml` as a new entry
(mechanically possible with zero `.mcp.json` hand-editing, per `plan-049` §1.1's T491/T492 finding,
independently re-confirmed by reading `sync.mjs`'s now-general `mapTemplatedValue()`/`BLOCK_KEYS`
parser — this is `stdio`-transport with a plain `command`/`args`, though, so it does not even need
the templated-`url`/`headers` machinery T491 added; a plain `command: python3, args: [-m, ...]`
entry, structurally identical to the existing `gitlab`/`playwright`/`fetch` stdio entries already in
`servers.yaml`, lines 17–36, is sufficient). Grant `@context-retriever` only
`mcp__context-retriever__retrieve` (Claude Code) in place of `execute`.

**Why this, and not the alternatives, with ADR-005-level rigor:**

- **Why not option (b)/(c) (§1.1–1.2):** already rejected above — no reuse of an existing
  enforcement layer, or disproportionate new infrastructure, for a component whose actual logic is
  already a single pure function call.
- **Why a *new* server rather than composing existing registered servers (the §2.2-style approach
  used for `@security-engineer`):** `@context-retriever`'s entire legitimate workload is one call —
  `ContextRetriever.query()` (`context_retriever.py` lines 173–181) — which has **no equivalent
  tool in any already-registered server** (`filesystem`, `git`, `fetch`, etc. all expose generic
  file/network primitives, none of them perform T453's hybrid semantic+lexical+structural fusion
  search over this repo's own derived index). There is nothing to compose; the capability must be
  built, and building it as a single-tool wrapper is strictly narrower than building it as, say, a
  new `filesystem`-style multi-tool server would be.
- **Why this is a *structurally stronger* scoping guarantee than `@security-engineer`'s composed
  approach, independent of platform-granularity questions:** because the new server would expose
  **exactly one tool and that tool has no write path** (`context_retriever.py`'s own docstring,
  lines 9–26, and its reflection-based test `tests/functional/test_context_retriever.py`, both cited
  by `plan-049` §2.1), even the *coarsest* possible MCP scoping mechanism any platform might support
  — whole-server enable/disable, with no per-tool granularity at all — is already sufficient to make
  this grant safe. `@context-retriever` does not depend on any platform supporting exact-tool-name
  granularity to be meaningfully scoped; `@security-engineer`'s composed-allowlist direction (§2)
  does, because `filesystem`/`git` are multi-tool servers with real write tools alongside the read
  ones a composed grant would want. This asymmetry is the single most important reason this
  direction is lower-risk and more likely to generalize across all 7 platforms than §2's — see §4's
  per-platform table, where `@context-retriever`'s risk profile is meaningfully better even on
  platforms with no exact-tool-name mechanism.
- **Cost, honestly stated:** this is genuine new server-writing work — a small Python MCP server
  package (probably using the official `mcp` Python SDK's `stdio_server` helper, not investigated in
  detail here since that is implementation-phase work), a `servers.yaml` entry, a live adversarial
  test (task-T457.md Expected Outputs item 3, explicitly deferred, not this document's job) — not a
  one-line change. `plan-049` §2.1 already states this plainly ("well-scoped and low-risk ... not a
  one-line change"); this document does not walk that back.

This confirms `plan-049` §2.1's starting candidate rather than revising it — this session's own
independent re-reading of `context_retriever.py`, `sync.mjs`, and `claude-code.json` did not surface
a reason to prefer a different direction, and surfaced one additional argument (the single-tool
structural-safety point above) `plan-049` did not make explicitly.

## 2. `@security-engineer` — an open decision, not resolved here

`plan-049` §2.2 already found that `@security-engineer`'s legitimate workload (grep-style content
search, dependency-vulnerability scanning, git-history inspection) does not reduce to one clean
wrapped function the way `@context-retriever`'s does, and proposed a composed exact-tool-name
allowlist over already-`servers.yaml`-registered servers as a candidate. This section works out that
candidate concretely, presents it alongside two alternatives, and **does not pick one** — per this
dispatch's explicit instruction, this mirrors how T443's protected-path exception and T492's
allowlist decision were each presented as options before implementation, not decided unilaterally
by the design pass.

### 2.1 Option A — accept the narrowing: composed exact-tool-name allowlist

**Concrete composition** (tool names independently re-verified this session against the official MCP
reference-server READMEs, not just re-cited from `plan-049`):

| Server | Read tools (grantable) | Write/mutating tools (withheld) | Source |
|---|---|---|---|
| `filesystem` | `read_text_file`, `read_media_file`, `read_multiple_files`, `list_directory`, `list_directory_with_sizes`, `directory_tree`, `get_file_info`, `list_allowed_directories`, `search_files` (filename-pattern only, not full-text content) | `write_file`, `edit_file`, `create_directory`, `move_file` | `raw.githubusercontent.com/modelcontextprotocol/servers/main/src/filesystem/README.md`, fetched fresh this session — tool list independently re-verified, adds `read_multiple_files` to `plan-049`'s enumeration (a minor completeness addition, not a disagreement) |
| `git` | `git_status`, `git_diff_unstaged`, `git_diff_staged`, `git_diff`, `git_log`, `git_show` | `git_commit`, `git_add`, `git_reset`, `git_create_branch`, `git_checkout`, `git_init` | `raw.githubusercontent.com/modelcontextprotocol/servers-archived/main/src/git/README.md`, fetched fresh this session — 12 tools total, 6 read / 6 write, matches `plan-049`'s characterization |
| `fetch` | already granted (`mcp__fetch`, `security-engineer.md` line 4) | n/a — no MCP-side write path for an outbound HTTP fetch tool | already in production |

Proposed grant (Claude Code): `tools: [read, search, mcp__filesystem__read_text_file,
mcp__filesystem__read_multiple_files, mcp__filesystem__list_directory,
mcp__filesystem__list_directory_with_sizes, mcp__filesystem__directory_tree,
mcp__filesystem__get_file_info, mcp__filesystem__list_allowed_directories,
mcp__filesystem__search_files, mcp__git__git_status, mcp__git__git_diff_unstaged,
mcp__git__git_diff_staged, mcp__git__git_diff, mcp__git__git_log, mcp__git__git_show, web,
mcp__fetch]` — in place of `execute`.

**What's gained:** a technical, platform-enforced boundary in place of the current prose-only
"you operate in read-only mode" instruction (`security-engineer.md` line 13). A subagent granted
only these tool names genuinely cannot call `mcp__filesystem__write_file` or `mcp__git__git_commit`
— the platform's own tool-resolution step drops any call outside the pool (the same mechanism
`plan-049` §1.2 established for Claude Code, re-confirmed by this session's own reading of
`sync.mjs`'s passthrough).

**What's lost — real, not hypothetical:**

- **No full-text content search.** `filesystem`'s `search_files` is filename/glob-pattern matching
  per its own README (fetched fresh this session — the tool description does not mention content
  grep at all; matches `plan-049`'s finding). `@security-engineer`'s existing checklist explicitly
  calls for content-level search (`security-engineer.md`'s Injection/A03 section implies scanning
  code for unparameterized queries, hardcoded secrets, etc. — currently done via shell `grep`/`rg`
  through `execute`). Composing `filesystem`+`git` gives no equivalent.
- **No dependency-vulnerability scanning.** `npm audit`, `pip-audit`, `dotnet list package
  --vulnerable` — explicitly named in `security-engineer.md`'s own A06 checklist (`security-
  engineer.md` line 50) — have no MCP tool in any already-registered server. Composing existing
  servers cannot restore this capability; it would have to be dropped or replaced by manual
  developer-report-provided output.
- **No linter/static-analysis invocation** — same gap, same reason.
- **Ongoing composition-drift risk:** if either `filesystem` or `git`'s upstream reference server
  adds a new read-shaped tool in a future version, the composed allowlist does not pick it up
  automatically (unlike a wildcard grant); this is a minor, disclosed maintenance cost of exact-name
  enumeration versus `mcp__<server>__*`-wildcard usage (the wildcard form is available per Claude
  Code's own docs per `plan-049` §1.2, and would reduce this specific risk at the cost of also
  auto-granting any future *write* tool the upstream server might add without a re-review step —
  itself a trade-off worth flagging, not resolved here).

### 2.2 Option B — reject the narrowing: status quo (prose-only `execute`/`Bash`, unchanged)

Keep `security-engineer.md`'s current `tools: [read, search, execute, web, mcp__fetch]` exactly as
is. **What's gained:** zero capability loss — `npm audit`, full-text `grep`/`rg`, any ad hoc shell
command the audit workflow needs, all remain available exactly as today. **What's lost:** the
"read-only mode" claim (`security-engineer.md` line 13, "CRITICAL: You operate in read-only mode")
continues to rest entirely on the model choosing to follow that instruction while holding
unrestricted shell access — the exact gap `task-T457.md` exists to close. This is the precedent this
repo already explicitly, consciously accepted once (`plan-039` lines 20–24, "the user's explicit
disposition ... was to accept this for now"); Option B simply continues that acceptance rather than
closing the gap for this agent specifically (it would still close for `@context-retriever` under
§1.4's recommendation either way, since that direction has no such dependency-scanning workload to
lose).

### 2.3 Option C — a third, more-capable-but-still-scoped mechanism: a dedicated audit-command MCP server

`plan-049` §2.2 itself named this as a candidate worth considering ("a dedicated MCP server wrapping
a fixed allowlist of specific audit commands, closer to `docker`/`postgres`-style scoped infra
access"). Worked out slightly further here: a small `stdio` MCP server exposing a **fixed, named set
of tools**, each one a thin wrapper around exactly one specific, pre-approved command invocation —
e.g. `run_npm_audit(package_json_dir)` → internally executes `npm audit --json` and nothing else
(no free-form command string ever reaches a shell), `run_pip_audit(requirements_path)`,
`grep_content(pattern, path_glob)` → internally executes a fixed `rg`/`grep` invocation with the
caller's `pattern`/`path_glob` as data arguments, never as part of a shell command string the model
constructs.

**What's gained relative to Option A:** restores dependency-audit and full-text-search capability
without restoring general shell access — each tool's implementation is a fixed command shape with
data-only parameters, structurally similar to how `context_retriever.py`'s own `main()` (§1.4) takes
`query_text` as a data argument to a fixed Python call, never as a shell string. **What's gained
relative to Option B:** a real technical boundary, same as Option A. **What's lost relative to both:**
this is the largest implementation lift of the three options — new server code, careful design of
each wrapped command's parameter surface (to avoid reintroducing command-injection risk through a
parameter that gets shell-interpolated — an explicit design hazard worth flagging now: if
`run_npm_audit`'s `package_json_dir` parameter were naively string-concatenated into a shell command
rather than passed as a subprocess argument list element, this server would reintroduce exactly the
injection risk it exists to close), and an open question this document does not resolve: which exact
commands make the fixed list (do `pip-audit`, `dotnet list package --vulnerable`, and per-language
linters all need their own wrapped tool, or a smaller curated subset?).

### 2.4 Recommendation (labeled as a recommendation, not a decision)

**This document's author recommendation, offered for the user/orchestrator's actual decision, not
as a resolution:** Option C is the most technically satisfying long-term answer (closes the gap
without narrowing capability), but Option A is the more honest **next step** if the priority is
closing *some* real technical gap now rather than deferring further — it uses infrastructure that
already exists (once §3's registry defects are fixed) and ships a real, if narrower, boundary
immediately, while Option C's exact scope (which commands, how parameterized) needs its own design
pass before it is buildable. Option B (status quo) remains legitimate and low-risk precisely because
it changes nothing — it is not a regression, only a continued deferral, consistent with this repo's
own prior explicit acceptance of the same posture (`plan-039`). **This recommendation is explicitly
not a decision.** The orchestrator/user should choose among A/B/C (or a hybrid — e.g., Option A now
as an incremental step, with Option C tracked as a follow-up task) before any implementation task is
opened for `@security-engineer` specifically. `@context-retriever` (§1.4) does not share this open
question and can proceed independently once a future dispatch is authorized.

## 3. `servers.yaml` registry defects — disclosed, not fixed here

### 3.1 `filesystem` entry (already flagged by `plan-049` §3, independently re-verified this session)

`implementation/knowledge/mcp/servers.yaml` lines 81–85:

```yaml
  filesystem:
    tags: [extended]
    transport: stdio
    command: npx
    args: ["-y", "@anthropic/mcp-filesystem"]
```

Independently fetched this session, the official MCP reference filesystem server's own README
(`raw.githubusercontent.com/modelcontextprotocol/servers/main/src/filesystem/README.md`) states:
"Published on npm as `@modelcontextprotocol/server-filesystem`" — confirming `plan-049`'s claim that
`@anthropic/mcp-filesystem` is the wrong package name, from a fresh, independent fetch rather than
trusting `plan-049`'s own citation. The same README also independently confirms `plan-049`'s second
sub-finding word for word in substance: "the server will only allow operations within directories
specified either via `args` or via Roots" and "Server requires at least ONE allowed directory to
operate" — the registered entry has zero `args` beyond the package name, so it has no directory to
scope itself to. **This is a real, disclosed prerequisite for §2's Option A specifically** (the
`filesystem` composition), not fixed by this document — this document only reads and reports; the
fix (correct package name, add an allowed-directory `args` entry) is implementation-phase work for
whichever task eventually pursues §2 Option A, if chosen.

### 3.2 `git` entry — a second, previously undisclosed defect found this session, not in `plan-049`

While independently verifying `git`'s read/write tool names for §2.1's table, this session found
`servers.yaml`'s `git` entry (lines 93–97) has the same class of problem, **not previously flagged
by `plan-049`**:

```yaml
  git:
    tags: [extended]
    transport: stdio
    command: npx
    args: ["-y", "@modelcontextprotocol/mcp-git"]
```

The official MCP reference git server's own README (`raw.githubusercontent.com/modelcontextprotocol/
servers-archived/main/src/git/README.md`) documents installation only via `uvx`/`pip`
("Using uv (recommended) ... we will use `uvx` to directly run *mcp-server-git*" / "Alternatively
you can install `mcp-server-git` via pip") — **it is a Python package (`mcp-server-git`), not an npm
package at all.** An `npm registry` lookup performed this session for `@modelcontextprotocol/mcp-git`
returned **HTTP 404** — the package does not exist on npm under that name. `npx -y
@modelcontextprotocol/mcp-git` as registered today would fail outright, not merely misbehave.

**Disclosure, not a fix:** this is flagged here exactly as `plan-049` flagged the `filesystem`
defect — a real, pre-existing, unrelated-to-T457 registry problem, found as a side effect of this
design pass's own verification work, not fixed in this document. It is a **second** prerequisite for
§2's Option A specifically (both `filesystem` and `git` would need correcting before that
composition is buildable, not just `filesystem` as `plan-049` alone would suggest), and it does not
block or change anything about §1's `@context-retriever` recommendation, which does not depend on
either entry.

## 4. Per-platform verification — closed for some platforms, honestly scoped down for others

`plan-049` §4 confirmed the exact-MCP-tool-name mechanism only for Claude Code and left the other 6
platforms explicitly open. This session investigated each of the 6 directly, via each platform's own
official documentation where reachable within this session's tooling (WebSearch + WebFetch/`fetch__*`
MCP tools; no `ctx7` documentation-lookup tool was available in this session's actual tool grant
despite the global `context7.md` instruction file's general guidance — noted as a disclosed tooling
gap, not worked around by fabricating a citation).

| Platform | This repo's current tools-frontmatter mechanism (`sync.mjs`/manifest, re-verified this session) | Real per-tool MCP granularity? | Evidence class |
|---|---|---|---|
| `claude-code` | `claude-code.json` line 14 `"tools": "string"` + `toolMap` (lines 16–24); unmapped tokens (incl. `mcp__server__tool`) pass through literally, `sync.mjs` lines 267–276 | **Yes** — `mcp__<server>__<tool>` exact names, confirmed by Claude Code's own docs (`plan-049` §1.2, not re-fetched this session, cited as already-established) | Official docs |
| `github` (VS Code Copilot) | `github.json` line 14 `"tools": "array"`, no `toolMap`, raw array passthrough (`sync.mjs`'s default `else` branch, line 278); `fileMap.agents` is `{dir: "agents", ext: ".agent.md"}` (line 7) | **Yes, with a caveat.** Official VS Code docs (`raw.githubusercontent.com/microsoft/vscode-docs/main/docs/agent-customization/custom-agents.md`, fetched fresh): custom agents live in `.github/agents` as `.agent.md` files — an exact structural match to this repo's own `github.json` fileMap, independently confirmed, not assumed. The `tools` frontmatter field is documented as "A list of tool or tool set names that are available for this custom agent. Can include built-in tools, tool sets, MCP tools, or tools contributed by extensions." A GitHub issue against `microsoft/vscode` (#269600, title: "Custom Chat Modes Cannot Use Tool Groups - Must Explicitly List Individual Tools") independently corroborates that *individual* tool names — not just group/server references — are the form that is actually callable, i.e. the same exact-name granularity Claude Code has. **Caveat, disclosed:** this session could not confirm the exact string format for an individual MCP tool name in this context (e.g. `<server>/<tool>` vs. some other separator) within budget — the wildcard form `<server name>/*` was confirmed by search-result synthesis of the official docs, but the non-wildcard individual form was not independently byte-verified against primary source text. | Official docs (structure, field semantics) + community bug report (individual-name requirement) + **unverified exact naming syntax** |
| `cursor` | `cursor.json` line 14 `"tools": "array"`, `keepKeys` includes `"tools"` (line 15), no `toolMap`, raw array passthrough | **No mechanism exists for this at all, on this platform, today.** Official Cursor docs (`cursor.com/docs/subagents`, fetched fresh, "Configuration fields" table) enumerate exactly 5 supported custom-subagent frontmatter fields: `name`, `description`, `model`, `readonly` (boolean, "restricted write permissions" — coarse, not per-tool), `is_background`. **There is no `tools` field in Cursor's own documented subagent contract.** This means this repo's `cursor.json` manifest emitting a `tools:` key into generated Cursor subagent files is, per Cursor's own documentation, emitting a key Cursor's subagent format does not recognize — a separate, disclosed, pre-existing gap this document did not go looking for and is not fixing (see note below). Cursor does have a real exact-tool-name mechanism, `permissions.json`'s `mcpAllowlist` (`server:tool` strings, `*` wildcards — `cursor.com/docs/reference/permissions`, fetched fresh, "MCP allowlist format" section, confirmed verbatim) — but it is a **workspace/user-level auto-approval routing list**, not a per-subagent tool-availability grant; it governs whether a tool call is auto-approved versus prompted/classified, for every agent in the workspace alike, and cannot give `@security-engineer` a narrower *available* tool set than any other agent on this platform. | Official docs (both the absence of a `tools` field and the `mcpAllowlist` mechanism's actual scope are directly documented) |
| `opencode` | `opencode.json` line 14 `"tools": "object"`; `applyAgentFrontmatter()`'s `cfg.tools === 'object'` branch (`sync.mjs` lines 265–266) sets `out.tools = tools` (the raw array), then `emitFrontmatter()`'s `toolsFormat: 'object'` (line 140) renders each entry as `<token>: true` | **Likely yes, at moderate confidence.** Official OpenCode docs (`opencode.ai/docs/tools/`, fetched fresh) document a `permission` config block supporting exact per-tool control with wildcards, explicit example: `{"permission": {"mymcp_*": "ask"}}` — confirming the naming convention is `<server>_<tool>` (single underscore, distinct from Claude Code's `mcp__server__tool`). Whether the *same* per-tool exactness is honored through the agent-frontmatter `tools:` boolean map specifically (this repo's actual emission target, as opposed to the separate global/per-agent `permission` block shown in the official JSON-config example) was corroborated only by secondary sources this session (a GitHub issue and a third-party skill-marketplace listing describing `tools: bash: true read: true ... "mcp-server/*": false`-style per-tool booleans) — not independently confirmed against OpenCode's own primary docs within this session's budget. | Official docs (permission mechanism + naming convention) + **secondary-source corroboration only** for the frontmatter `tools:` map specifically |
| `gemini` | `gemini.json` line 14 `"tools": "drop"`; `applyAgentFrontmatter()`'s `cfg.tools === 'drop'` branch (`sync.mjs` line 263–264) **deletes** the `tools` key entirely — no tool restriction of any kind is emitted to Gemini for any agent today, not even the current weak `execute` grant | **Gemini CLI itself likely supports it, but this repo does not currently emit anything for Gemini to use it with.** Official Gemini CLI docs, per this session's WebSearch synthesis of `geminicli.com`/`google-gemini/gemini-cli` sources (not independently byte-verified against primary doc text for the non-wildcard form): subagent tool grants support `mcp_*` (all MCP tools), `mcp_<server>_*` (all tools from one server), implying by direct pattern extension `mcp_<server>_<tool>` for a single exact tool — the individual-tool form was not found verbatim in the two Gemini CLI doc pages this session actually fetched in full (`docs/core/subagents.md`'s built-in-subagent reference content, which does not cover custom-subagent-definition file syntax). **Independent of that Gemini-CLI-side question, this repo's own `gemini.json` manifest drops the `tools:` key outright (confirmed by direct read, cited above) — implementing any scoped grant for Gemini would first require changing `gemini.json`'s `"tools": "drop"` to a real emission mode, a `sync.mjs`/manifest change this document does not make and flags as a necessary prerequisite, separate from and in addition to whatever Gemini CLI itself supports.** | Search-result synthesis of official docs (Gemini-CLI-side capability) + **direct, confirmed citation** (this repo's own manifest currently emits nothing) |
| `cline` | `cline.json` (read in full, lines 1–24) has **no `agents` key in `fileMap` at all** — only `instructions` and `skills` | **Not applicable — moot for this task today.** `sync.mjs`'s `syncPlatform()` only processes agent files `if (manifest.fileMap.agents)` (`sync.mjs` line 469); since `cline.json` never declares that key, **no `@security-engineer` or `@context-retriever` agent (or any agent at all) is projected to Cline today**, regardless of what `tools:` value either source file carries. Whatever Cline's own native subagent/tool-scoping mechanism may or may not be was not investigated, because it is currently disconnected from this repo's agent pipeline entirely — a future Cline agent-projection feature would need its own separate design work first. | Direct, confirmed citation of this repo's own manifest (definitive for "does this apply today") |
| `pi` | `pi.json` line 14 `"tools": "array"`, no `toolMap`, raw array passthrough (same code path as `cursor`/`github`); MCP registration reuses `"format": "cursor"` (line 30, per `mcp-platform-contract-v1.md` §3 row for `pi`, already established) but **agent-frontmatter tooling is a separate manifest key from MCP format and is not necessarily the same platform** | **Unresolved — could not identify an authoritative source within this session's budget.** This repo's `pi.json` `displayName: "Pi"` was not conclusively matched to a specific real-world product this session; the most plausible candidate found by search (`mariozechner`/`badlogic` "Pi Coding Agent," `earendil-works/pi`) has third-party documentation (`github.com/tintinweb/pi-subagents`, a community extension, not Pi's own core docs) describing custom agent frontmatter with "tool restrictions," but this session could not confirm (a) that this is actually the same "Pi" this repo's `pi.json` targets, or (b) whether those tool restrictions reach exact-MCP-tool-name granularity or only coarser categories. **Honestly scoped down: no recommendation in this document should be read as applying to `pi` without further, dedicated investigation.** | **Unverified — disclosed as an open gap, not silently assumed to generalize** |

**Bottom line for §4, stated plainly per this dispatch's explicit instruction:** the exact-tool-name
mechanism this document's `@context-retriever` recommendation (§1.4) and `@security-engineer` §2
Option A both lean on is **confirmed for `claude-code`**, **plausibly confirmed with a caveat for
`github`**, **confirmed absent for `cursor`** (a real, documented gap, not an oversight), **plausibly
present but only secondary-sourced for `opencode`**, **present upstream but currently unreachable
through this repo's own manifest for `gemini`** (a disclosed, separate prerequisite fix), **not
applicable today for `cline`** (no agent projection exists), and **genuinely unresolved for `pi`**.
Per §1.4's structural argument, `@context-retriever`'s single-tool-server design is safe even on
platforms with only coarse whole-server granularity (i.e., it degrades gracefully on `cursor` and
`pi` rather than failing outright, if whole-server-level scoping is available there — not itself
confirmed for either platform in this session, another disclosed gap); `@security-engineer`'s
multi-tool composed allowlist (§2 Option A) does **not** degrade as gracefully and would need
platform-by-platform re-evaluation of whether whole-server or better granularity is achievable before
being called done on any platform beyond Claude Code, consistent with `task-T457.md`'s own
Acceptance Criteria 1's "demonstrated per platform, not asserted for one and assumed for the rest."
This document does **not** claim the recommendation is cross-platform-ready; it is Claude-Code-
confirmed, with a mixed, disclosed picture elsewhere, exactly as `task-T457.md`'s own Inputs section
anticipated might be the case.

## 5. What this document does NOT decide

1. **The single most important open decision: `@security-engineer`'s capability trade-off (§2).**
   Whether to accept Option A's narrowing, keep Option B's status quo, or pursue Option C's
   more-capable-but-heavier dedicated server is explicitly left to the user/orchestrator. This
   document presents the options and a labeled, non-binding recommendation only.
2. **Implementation task IDs and ownership.** No `T458`/`T459`-style follow-up task is created or
   assigned here — per `task-T457.md`'s own framing ("implementation owner(s) TBD once the design
   ... [is] resolved"), that is the orchestrator's job once §2's decision is made, not this
   document's.
3. **Whether `.mcp.json`/`servers.yaml` are touched now.** They are not touched by this document
   (read-only references throughout, confirmed by the absence of any `Edit`/`Write` call against
   either in this session). Any future implementation of §1.4 or §2 Option A/C would need to extend
   `servers.yaml` (a new `context-retriever` entry for §1.4; corrected `filesystem`/`git` entries
   plus new exact-tool-name grants for §2 Option A; an entirely new server entry for §2 Option C) —
   all deferred to that future, separately-scoped and separately-authorized task.
4. **The exact individual-MCP-tool-name string format for `github`/`opencode`/`gemini`/`pi`** (§4) —
   flagged as needing primary-source confirmation before any of those platforms' grants are
   actually written, not assumed by pattern-extension from the wildcard forms this session did
   confirm.
5. **`pi`'s platform identity and tool-scoping mechanism** (§4) — genuinely unresolved, not silently
   assumed to match `cursor`'s (its MCP-registration sibling) or any other platform.
6. **Whether Cursor's currently-emitted but seemingly-unrecognized `tools:` frontmatter key (§4) is
   a pre-existing defect worth its own fix task.** Flagged as an observation this session made while
   investigating §4, not evaluated for severity or remediation — that is a separate question from
   this task's own scope (T457 is about `@security-engineer`/`@context-retriever` specifically, not
   a general audit of every platform's frontmatter contract).
7. **The second `servers.yaml` defect found this session (`git` entry, §3.2) — its remediation.**
   Disclosed, not fixed, same posture as `filesystem`'s already-known defect.

## 6. Self-assessment of citation accuracy

Mirroring T483's own "Ratification note" precedent (`docs/artifacts/mcp-header-url-templating-
design-v1.md`, "Ratification note" section): every non-trivial factual claim above is either (a) a
direct citation of a `plan-049` finding by section number, explicitly marked as such, or (b) a fresh
citation this session performed independently, with a file path + line number (for this repo's own
files) or a fetched-URL + quoted snippet (for external documentation). Honest confidence accounting,
by section:

- **§1.3–1.4 (`sync.mjs`/`claude-code.json` passthrough mechanism):** high confidence — re-read the
  actual current file content directly this session (not reused from `plan-049`'s quoted excerpt
  alone), line numbers given against this session's own `Read` output.
- **§2.1 (`filesystem`/`git` tool-name tables):** high confidence for the tool names themselves
  (fetched official READMEs directly, quoted); the exact Claude Code `tools:` array syntax proposed
  is this document's own construction, not independently test-run (no execute/Bash tool available to
  this session, consistent with this task's constraints) — should be treated as a well-founded draft,
  not a verified-working grant, until an implementation pass actually exercises it.
- **§3.1 (`filesystem` defect):** high confidence — independently re-fetched the official README this
  session and found language matching `plan-049`'s characterization closely, not merely trusted it.
- **§3.2 (`git` defect, new this session):** high confidence on the README content (fetched directly,
  quoted); the npm-404 claim is a single lookup performed once this session (`registry.npmjs.org/
  @modelcontextprotocol/mcp-git` → HTTP 404) and was not cross-checked with a second method (e.g. an
  `npm view` command, unavailable — no execute tool) — a 404 from the registry API is strong but not
  absolute evidence the package has never existed under any historical version; treated here as
  sufficient to disclose as a real, actionable finding, not as forensically exhaustive.
- **§4 (per-platform table):** deliberately mixed and stated as such per row — `claude-code` and
  `cline` are high confidence (direct primary-source/direct-file-read evidence); `github` and
  `cursor` are high confidence on the structural claims (official docs fetched and quoted directly)
  with one explicitly flagged naming-format gap for `github`; `opencode` and `gemini` are explicitly
  marked moderate/mixed confidence (official docs confirm the general mechanism, secondary sources
  or pattern-extension fill the remaining gap); `pi` is explicitly marked unresolved. This
  gradation is intentional, not a hedge — per this task's Blocker Protocol, an honestly-documented
  open question is the expected, correct outcome, not a failure to route around.
- **No claim in this document asserts a live command was run, a test was executed, or any file
  outside `docs/artifacts/scoped-execution-primitive-v1.md` was modified in this session** — all
  verification was `Read`/`WebSearch`/`WebFetch`/`fetch__*`-based, consistent with this dispatch's
  explicit "no execute tool, no live test" constraints.

## Blockers

None. `task-T457.md`'s Blocker Protocol anticipated one specific scenario ("no non-`.mcp.json`-
touching design proves viable after genuine investigation") that did not occur — `plan-049` already
resolved that the `.mcp.json` constraint is lifted, and this document found two viable, if
differently-shaped, directions (§1.4 for `@context-retriever`, §2's three options for
`@security-engineer`). The one genuinely open item (§2's trade-off) is not a blocker per this
dispatch's own instruction — it is the expected, correct, honestly-documented outcome of a design
pass that surfaces a real product/security decision rather than making it unilaterally.
