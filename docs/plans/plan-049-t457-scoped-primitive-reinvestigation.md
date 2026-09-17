# Plan 049 — T457 re-investigation: scoped, non-`Bash` execution/read primitive, post-T483/T491/T492

> Filename: `plan-049-t457-scoped-primitive-reinvestigation.md`

**Date:** 2026-09-17

**Status:** proposed — a re-investigation and design-direction document only. It does not dispatch
T457's solution-architect design pass, does not touch `docs/tasks/active-tasks.md`, does not touch
`.mcp.json` (read-only reference only, via `git show`, never written to), and does not touch
`tests/golden/**`, `scripts/scorecard.py`, `docs/benchmarks/tb-subset.json`/`.md`, or
`feature/T475-codex-platform-integration`. T456, T458, and T483 remain untouched. This document
does not assert any approval-checklist authorization — see §6's Approval section, unchecked, same
posture as `plan-047`/`plan-048`.

**Based on:** `docs/tasks/task-T457.md` and `docs/plans/plan-039-t457-tool-scoping-followup.md`
(both re-read in full, fresh, from `origin/develop` this session — not from any prior summary);
`implementation/platforms/claude-code.json` (re-read in full, `toolMap` re-verified); the real,
current `implementation/knowledge/agents/security-engineer.md` and
`implementation/knowledge/agents/context-retriever.md` source files and their generated
`.claude/agents/*.md` projections (all re-read fresh); `implementation/scripts/sync.mjs`'s
`applyAgentFrontmatter()` (re-read in full — the actual tools-list resolution logic); root
`.mcp.json` and `implementation/knowledge/mcp/servers.yaml` (both re-read fresh, read-only);
`docs/tasks/task-T483.md`, `docs/tasks/task-T491.md`, `docs/tasks/task-T492.md` (re-read — the
precedent this document's own "design-then-implementation" recommendation mirrors);
`implementation/runtime/memory/context_retriever.py` and
`deploy/docker-compose-context-retriever.yml` (re-read — the concrete existing code this document's
context-retriever design direction targets); Model Context Protocol reference-server documentation
for the `filesystem` and `git` servers, fetched fresh this session via `ctx7` from
`/modelcontextprotocol/servers` (`src/filesystem/README.md`, `src/git/README.md`); Claude Code's own
sub-agent documentation, fetched fresh this session via `ctx7` from `/websites/code_claude`
(`docs/en/sub-agents`, `docs/en/agent-sdk/mcp`) — the source for this document's central new finding
about exact-MCP-tool-name allowlisting.

## 0. Re-verified start conditions (fresh this session, not trusted from any prior summary)

- `origin/develop` HEAD independently re-verified via `git fetch origin develop` +
  `git rev-parse origin/develop`: **`f731a51a8c220bcc1d4cd942fb3b4c8499bf2251`**
  (`Merge branch 'agent/orchestrator/T494-v2' into 'develop'`) — matches the instructing session's
  stated expectation exactly.
- `docs/tasks/active-tasks.md` re-read fresh from `origin/develop`: three non-terminal rows only —
  `T456` (blocked), `T457` (pending, owner `solution-architect`, P1, depends on None), `T458`
  (pending) — matches the instructing session's stated expectation exactly. `T457` is not present in
  `completed-tasks.md`.
- `implementation/platforms/claude-code.json`'s `frontmatter.agents.toolMap`: `"execute": "Bash"`
  still holds, unchanged, no scoped alternative entry exists in the map.
- `implementation/knowledge/agents/security-engineer.md`: `tools: [read, search, execute, web,
  mcp__fetch]` — `execute` still present. Generated `.claude/agents/security-engineer.md`:
  `tools: Read, Bash, WebFetch, WebSearch, mcp__fetch` — unrestricted `Bash` still present.
- `implementation/knowledge/agents/context-retriever.md`: `tools: [read, search, execute]` —
  `execute` still present. Generated `.claude/agents/context-retriever.md`: `tools: Read, Bash` —
  unrestricted `Bash` still present.
- **Core finding fully re-confirmed, unchanged from T457's original creation.** Nothing about the
  central gap has closed on its own since 2026-09-09.

## 1. What has actually changed since `plan-039` was written (2026-09-09), re-investigated fresh

`plan-039`/`task-T457.md` recorded T457 as **un-dispatchable** for one specific, load-bearing reason:
the likely real fix (a dedicated MCP server or equivalent scoped-tool mechanism) would need to touch
`.mcp.json`, and the then-standing session constraint categorically forbade touching `.mcp.json` "for
any reason." That premise no longer holds in the same shape, for two independent reasons found this
session:

### 1.1 The MCP registration pipeline itself is now materially more capable (T483 → T491 → T492)

Before T491, `servers.yaml`/`sync.mjs` had **zero support** for a `headers` field on remote-transport
servers and **zero support** for templated (`{fromEnv: ...}`) `url` values — every remote server had
to be a literal public URL, and `hindsight`/`cwso` had been hand-added directly to `.mcp.json`,
bypassing the declarative pipeline entirely (T483's own finding). T491 closed that gap: `sync.mjs`
now has a general `mapTemplatedValue()` helper, all 6 `emitMcp()` format branches template `url` and
conditionally emit `headers`, and `test_mcp_secret_guard.py`'s `find_literal_env_values()` was
extended to walk `headers` blocks too (T492). This means: **a new MCP server, including one needing
auth headers or an env-templated URL, can now be registered the correct way — as a `servers.yaml`
entry that `sync.mjs --check` regenerates into every platform's `.mcp.json` projection with zero
hand-editing** — which was not true when `plan-039` was written. Registering a new server today is
`servers.yaml`-and-`sync.mjs` work, not "manually edit `.mcp.json`" work; the class of change T457's
original brief was worried about touching by hand is now handled by the generator, the same way
`hindsight`/`cwso` are.

### 1.2 Claude Code natively supports exact per-MCP-tool-name allowlisting — a scoped primitive already exists, this repo just isn't using it

`plan-039`'s framing assumed "there is currently no narrower, scoped … primitive in this repo's tool
vocabulary to grant instead" of `execute`. Fetched fresh this session from Claude Code's own
sub-agent documentation (`code.claude.com/docs/en/sub-agents`,
`code.claude.com/docs/en/agent-sdk/mcp`): a subagent's `tools:` allowlist is not limited to whole
built-in tools or whole MCP servers — **it accepts exact individual MCP tool names, in the form
`mcp__<server>__<tool>`**, alongside server-level wildcards (`mcp__<server>__*`) and the coarser
built-in names this repo's `toolMap` already emits. A subagent granted, e.g., only
`mcp__filesystem__read_text_file` and `mcp__filesystem__list_directory` (and nothing else) genuinely
cannot call `mcp__filesystem__write_file` — Claude Code's own tool-resolution step drops any call to
a tool name outside the resolved pool. This is a real, platform-enforced technical control, not a
prose instruction the model is trusted to honor — the same category of enforcement `plan-039`
concluded did not exist anywhere in this repo's tool vocabulary.

Critically, **this repo's own generator already passes this through with zero code changes needed for
the Claude Code case.** Re-reading `sync.mjs`'s `applyAgentFrontmatter()` directly:

```js
const expanded = tools.flatMap((t) =>
  Object.prototype.hasOwnProperty.call(toolMap, t)
    ? toolMap[t].split(',').map((s) => s.trim())
    : [t]
);
```

Any source `tools:` token that is **not** a key in `claude-code.json`'s `toolMap` (currently `read`,
`search`, `edit`, `execute`, `agent`, `web`, `todo`) is passed through to the generated frontmatter
**literally, unchanged**. This is not a hypothetical — it is exactly how `security-engineer.md`'s
existing `mcp__fetch` token already survives into its generated `tools: Read, Bash, WebFetch,
WebSearch, mcp__fetch` line today. Replacing `execute` in a source `tools:` list with one or more
literal `mcp__<server>__<read-tool-name>` tokens would, mechanically, require **no `sync.mjs` change
at all** to reach the Claude Code platform correctly — the passthrough path already exists and is
already exercised by a real token in production.

### 1.3 Net effect on `plan-039`'s central premise

`plan-039`'s "this task cannot be dispatched because the fix needs `.mcp.json`, which may not be
touched" framing is now out of date on both halves: the pipeline can register a new server properly
(§1.1), and a genuinely scoped, non-`Bash` grant may not even require a *new* server at all for at
least one of the two agents, given servers already registered under the `extended` tag that Claude
Code already receives (§2 below) — it may only require correcting the exact `tools:` tokens on the
two agent source files plus fixing a pre-existing, unrelated registry defect (§4). This is a
materially different, better-informed design space than `plan-039` had visibility into, not a reason
to skip a design pass — see §6.

## 2. Two different real needs, two different candidate directions — re-investigated, not assumed uniform

`task-T457.md`'s own Constraints already required addressing both agents together without silently
narrowing scope to one. Investigating each agent's *actual* workload (not just its `tools:` grant)
this session found they need genuinely different things, which the original `plan-039` did not yet
know because it was written before this level of investigation:

### 2.1 `@context-retriever` — a strong, concrete case for a small, purpose-built MCP server

`implementation/runtime/memory/context_retriever.py` (T454) is a thin wrapper around T453's hybrid
retrieval API. Its own docstring states plainly what this repo's *actual, current* invocation
mechanism is: **"this repo's actual invocation of `@context-retriever` is a direct in-process Python
call from an agent's `execute`/Bash tool grant, not a standalone container."** The module's public
API (the `ContextRetriever` class) has, by the module's own design and its own reflection-based test
(`tests/functional/test_context_retriever.py`), **no write/mutate method at all** — not a guarded
one, an absent one. This is close to an ideal candidate for a narrow, dedicated MCP server: a small
stdio server that imports this exact module and exposes exactly one tool (e.g. `retrieve(query,
scope)`), with no other capability surface. Unlike a generic `execute`/Bash grant, an MCP server with
a single tool cannot be asked to do anything else — there is no command string to escape into. This
is option (a) from `task-T457.md`'s own Expected Outputs list, now backed by a concrete, already-built
target module rather than a hypothetical.

This is genuinely new server-writing work (a small Python MCP server package, a `servers.yaml` entry,
platform projections, an adversarial test) — not a one-line change, but well-scoped and low-risk
because the underlying logic it wraps is already write-free and already tested as such.

### 2.2 `@security-engineer` — a harder case; likely a composed exact-tool-name allowlist over existing servers, with an explicit capability trade-off

`security-engineer.md`'s OWASP-audit workflow has no equivalent single wrapped module — its
legitimate use of `execute`/Bash today plausibly includes things a narrow retrieval-style server
cannot replace: grep-style content search, dependency-vulnerability scanning (`npm audit`,
`pip-audit`), and git-history inspection, none of which reduce to one clean read-only function call.
Investigated this session as a candidate composition, using servers **already registered** in
`servers.yaml` under the `extended` tag (which Claude Code already receives, per
`AGENTS.md`'s server-tag table):

- `filesystem` (`@anthropic/mcp-filesystem` per the current registry entry — see §4, this name is
  itself wrong) exposes, per the official reference server's own documentation (fetched fresh this
  session): read tools `read_text_file`, `read_media_file`, `list_directory`,
  `list_directory_with_sizes`, `directory_tree`, `get_file_info`, `list_allowed_directories`, and a
  filename-pattern `search_files`; separately, write tools `write_file`, `edit_file`,
  `create_directory`, `move_file`. Exact-tool-name allowlisting (§1.2) could grant only the former
  set.
- `git` (`mcp-server-git`, already registered, `extended` tag) exposes read tools `git_status`,
  `git_diff`, `git_log` (and, per the same reference implementation, `git_show`/`git_blame`-shaped
  tools); separately, write/mutating tools `git_commit`, `git_add` (and branch/checkout/reset-shaped
  tools). Same exact-tool-name allowlisting would apply.
- `fetch` (already granted to `security-engineer.md` today as `mcp__fetch`) already covers outbound
  CVE/advisory lookups without needing `execute`.

**This composition is not free of trade-offs and should not be presented to the eventual design owner
as a mechanical wiring exercise.** Filesystem `search_files` is filename-pattern matching, not
full-text content grep — the official docs do not describe a full-text search tool in this server.
Neither `filesystem` nor `git`'s read tools can run a dependency-vulnerability scanner
(`npm audit`/`pip-audit`) or a linter. Composing these servers at the exact-tool-name grain would
close the write-path gap this task exists to close, but it would also **genuinely narrow what
`@security-engineer` can practically do** relative to today's unrestricted-shell status quo — this is
a real product/security trade-off call, not a scoping detail, and the design owner (and likely the
user) should decide explicitly whether that narrowing is acceptable or whether a third, more
capable-but-still-scoped mechanism (e.g., a dedicated MCP server wrapping a fixed allowlist of
specific audit commands, closer to `docker`/`postgres`-style scoped infra access) is warranted
instead.

## 3. A pre-existing, unrelated defect found during this investigation

`servers.yaml`'s existing `filesystem` entry (`extended` tag, already present before this session):

```yaml
filesystem:
  tags: [extended]
  transport: stdio
  command: npx
  args: ["-y", "@anthropic/mcp-filesystem"]
```

Two problems, confirmed independently this session, neither introduced by this investigation and
neither part of T457's original scope:

1. **The package name appears wrong.** The real, official MCP reference filesystem server (fetched
   fresh via `ctx7` from `/modelcontextprotocol/servers`) is published as
   `@modelcontextprotocol/server-filesystem`, not `@anthropic/mcp-filesystem`. This session did not
   attempt to resolve or install either package (no new package installs were run, consistent with
   "no new paid/metered API usage" and with treating this as a finding to report, not a live change
   to make unilaterally) — this is reported as a disclosed discrepancy requiring its own verification,
   not asserted as certainly broken.
2. **No `args` specify allowed directories.** The official server "requires at least one allowed
   directory to function correctly" (its own documentation's own words) — as registered today, with
   zero directory arguments, the server would have nothing to scope itself to even before any
   agent-level tool-name allowlisting is applied.

This is flagged here as a **separate, disclosed finding**, not silently folded into or fixed as a side
effect of T457's own eventual work — per this session's instruction to run a self-referential
ledger-defect sweep. It does not currently block anything (no agent grants any `mcp__filesystem__*`
tool today), so it is not urgent, but a `filesystem`-composition design for `@security-engineer`
(§2.2) would need it corrected as a real prerequisite, not an afterthought.

## 4. Per-platform verification gap — explicitly unresolved, not silently assumed uniform

`task-T457.md`'s own Acceptance Criteria require the eventual fix to be "demonstrated per platform,
not asserted for one and assumed for the rest," and ideally proven on "at least one other platform
with a genuinely different tool-map mechanism." This session's investigation confirmed the
exact-MCP-tool-name allowlisting mechanism (§1.2) **only for Claude Code**, via that platform's own
documentation. Whether VS Code/Copilot, Gemini, Cursor, Opencode, Cline, or Codex support the same
granularity — or only support whole-server MCP enable/disable — was **not** investigated this session
and remains a genuine open question a design pass must answer per-platform, exactly as
`implementation/platforms/*.json` differ in their `toolMap` shape already (`task-T457.md`'s own
Inputs section already flagged this as unchecked, and it still is).

## 5. Assessment — plan-first, not same-turn dispatch, but now on a narrower, better-informed footing

Weighed against this repo's own precedent for what counts as "genuinely mechanical" versus "needs its
own design pass" (T420–T423 as mechanical; T483 as needing a design phase because it required real
generator/schema changes, per-platform verification gaps, and a live-status dependency it could not
assume): T457, even after this re-investigation, is closer to T483's shape than to T420–T423's.
Reasons, weighed honestly rather than defaulting to "needs a plan" by habit:

- Two different agents need two different real fixes (§2.1 vs §2.2), not one shared mechanical change
  — `task-T457.md`'s own Constraints already anticipated this could be a single design covering both,
  but this session's investigation found the two directions genuinely diverge in shape and effort.
- §2.2's composition is not merely a wiring exercise — it is a real capability trade-off for
  `@security-engineer` that changes what the agent can practically do, and deserves an explicit
  design-owner (and likely user) decision, not a silent narrowing.
- §3's pre-existing `filesystem` registry defect is a real prerequisite for §2.2 specifically and
  needs independent verification/correction before that direction is buildable at all.
- §4's per-platform gap is unresolved and the task's own acceptance criteria require it resolved
  before the work can be called done on more than one platform.
- A live adversarial write-attempt test (mirroring T454's own discipline) does not yet exist for
  either candidate direction and needs building either way.

None of this is a hard blocker the way the pre-T491 `.mcp.json` constraint was — this is genuine
design-plus-implementation work that deserves its own dispatch turn with a design owner, the same
conclusion `task-T483.md` reached about itself, not a reason to leave T457 sitting untouched
indefinitely. **Recommendation: dispatch `task-T457.md`'s solution-architect design pass now**, using
this document's §1–§4 findings as its starting evidence base (materially narrower and more concrete
than `plan-039`'s original framing), rather than continuing to treat `.mcp.json` as categorically
untouchable. The design pass itself — not this document — should produce
`docs/artifacts/scoped-execution-primitive-v1.md` per `task-T457.md`'s own Expected Outputs, make the
explicit call on §2.2's trade-off, resolve §3's defect, and close §4's per-platform gap.

This document does not itself dispatch that design pass — see §6.

## 6. Approval

- [ ] User confirms this document's re-investigation findings are accurate and sufficient to lift the
      old "cannot touch `.mcp.json`" framing that gated T457 since 2026-09-09, in favor of the
      narrower, T483-style "touch it only via a design-then-implementation pass, with explicit
      re-verification at each step" posture this document recommends.
- [ ] User confirms the two-direction split (§2.1 custom narrow MCP server for `@context-retriever`;
      §2.2 composed exact-tool-name allowlist for `@security-engineer`, with its capability trade-off
      made explicit) is the right framing for the solution-architect design pass to start from, or
      overrides it.
- [ ] User approves dispatching `task-T457.md`'s solution-architect design pass (owner already
      recorded as `solution-architect` in the ledger) using this document as its updated evidence
      base — this document does not dispatch that pass itself.
- [ ] Plan locked; revisions create `plan-049-t457-scoped-primitive-reinvestigation-v2.md`.
