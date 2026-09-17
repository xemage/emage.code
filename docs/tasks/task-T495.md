# Task T495 — `@context-retriever` dedicated MCP server (T457 §1.4 implementation, Track 1)

**ID:** T495
**Owner:** backend-developer
**Status:** done
**Priority:** P1
**Depends on:** None structurally. Implements the recommendation `docs/artifacts/
scoped-execution-primitive-v1.md` §1.4 already produced (T457's design-phase deliverable, merged
`origin/develop` at `7885989`).
**Created:** 2026-09-17
**Completed:** 2026-09-17
**Based on:**
- `docs/artifacts/scoped-execution-primitive-v1.md` §1.4 (`@context-retriever`'s recommendation —
  read this section in full before starting; it is the authoritative spec for what to build) and
  §1.3 (the `sync.mjs`/`claude-code.json` exact-MCP-tool-name passthrough mechanism this task
  delivers through)
- `docs/tasks/task-T457.md` Expected Outputs items 2 and 3 (the `tools:` grant update and the live
  adversarial write-attempt test — this task closes both, for `@context-retriever` only; item 3's
  literal "for both agents" wording is only half-satisfied by this task, since `@security-engineer`
  is Track 2, design-only, not implemented this round)
- `implementation/runtime/memory/context_retriever.py` (`ContextRetriever.query()`, the exact
  function this new server wraps — do not re-derive or duplicate its retrieval/scope-filtering
  logic, call it directly)
- `implementation/knowledge/agents/context-retriever.md` (current `tools: [read, search, execute]`
  — the file this task edits)
- `implementation/knowledge/mcp/servers.yaml` (registry format — see the existing `gitlab`/
  `playwright`/`fetch`/`memory`/`sequential-thinking`/`brave` `stdio` entries, lines ~17–58, as the
  structural template; this new entry is `stdio` with a plain `command`/`args`, same shape)
- `implementation/scripts/sync.mjs` (`applyAgentFrontmatter()` lines ~250–286, `claude-code.json`'s
  `toolMap` lines 16–24 — confirms an unmapped token like `mcp__context-retriever__retrieve` passes
  through literally with zero generator change)
- `tests/functional/test_context_retriever.py` (T454's existing test file — in particular
  `EndToEndAdversarialWriteProbeTests`, cited by name in `task-T457.md` Expected Outputs item 3 as
  the discipline this task's new adversarial test must mirror, this time proving the *tool-scoping*
  mechanism blocks a write, not just the module's own API surface)
- `deploy/docker-compose-context-retriever.yml` (layer-3 precedent for how this repo documents a
  component's runtime permission boundary declaratively)

## Objective

Build a small, dedicated `stdio`-transport MCP server that imports and calls
`ContextRetriever.query()` and exposes **exactly one** MCP tool (e.g. `retrieve(query, top_k)`) with
no other capability — per `scoped-execution-primitive-v1.md` §1.4's recommendation, already reviewed
and its lifted-`.mcp.json`-constraint reconfirmed by the user this session ("@context-retriever OK").
Register it in `servers.yaml`, regenerate all platform projections with zero drift elsewhere, update
`@context-retriever`'s `tools:` grant to replace `execute` with the new exact-tool-name form, and
build a live adversarial test proving the new grant genuinely cannot write — mirroring
`test_context_retriever.py`'s own `EndToEndAdversarialWriteProbeTests` discipline, but this time
demonstrating the *tool-scoping* control (the new server + grant), not the module-level API-absence
control T454 already has.

## Constraints

- **Never touch `feature/T475-codex-platform-integration`.** This worktree is already isolated on
  its own branch (`agent/backend-developer/T495`, branched from `origin/develop` at `7885989`) — do
  not fetch, merge, or reference that branch for any reason.
- **Never edit** `tests/golden/**`, `scripts/scorecard.py`, `docs/benchmarks/tb-subset.json`,
  `docs/benchmarks/tb-subset.md`.
- **No new paid/metered API usage.** The official `mcp` Python SDK (or an equivalent minimal
  stdio-JSON-RPC implementation, your call, disclose reasoning) is open-source and free to install;
  this constraint is about live paid services, not local dependencies.
- **`T456`, `T458`, `T483` are untouched by this task** — do not reference, modify, or re-scope any
  of them.
- **`.mcp.json`/`servers.yaml` changes are expected and pre-authorized** for exactly this new
  `context-retriever` server entry — per the user's explicit "@context-retriever OK" approval of
  §1.4's recommendation and §1.4's own already-lifted `.mcp.json` constraint. Do **not** touch any
  *other* existing entry in either file.
- **Do not fix the two disclosed `servers.yaml` registry defects** (`filesystem`'s wrong npm package
  name; `git`'s wrong npm package name, §3.1/§3.2 of the design doc) as a drive-by. Your new entry is
  unrelated to both — leave them exactly as they are, still-disclosed, not silently fixed.
- **Git workflow (mandatory, zero exceptions):** you are already on branch
  `agent/backend-developer/T495` in this worktree (`/home/emage/Code/emage/worktrees/
  agent-backend-developer-T495`), branched from `origin/develop`. Commit all work here. Do **not**
  commit to `develop`/`main` directly, and do **not** merge your own MR — open it against `develop`
  and leave it unmerged for the orchestrator/user to merge. Conventional Commits format
  (`feat(mcp): ...`, etc.).
- Follow this repo's `security-guidelines.md` Injection/A03 discipline throughout: the new server's
  `query`/`top_k` parameters must reach `ContextRetriever.query()` as ordinary Python function
  arguments — never shell-interpolated, never passed through a `subprocess` shell string (there is
  no legitimate reason for this server to invoke a subshell at all; if you find yourself reaching for
  `subprocess`/`os.system`, stop and reconsider the design).

## Expected Outputs

1. A new small Python MCP server package wrapping `ContextRetriever.query()` — suggested location
   `implementation/runtime/memory/context_retriever_mcp_server/` (module name and internal layout
   are your call; disclose your choice and reasoning), exposing exactly one MCP tool. Name it
   `retrieve(query, top_k)` per §1.4's own naming, unless you find a concrete reason to deviate
   (disclose if so). `stdio` transport, no other tool, no write/mutate capability anywhere on its
   public surface (mirror `context_retriever.py`'s own "no write method exists, not a guarded one"
   discipline — the safety property should come from the absence of any other tool, not from a
   runtime check).
2. Any new dependency this requires (most likely the official `mcp` Python SDK) declared in a new,
   clearly-scoped requirements file — mirror `implementation/runtime/memory/requirements.txt`'s own
   documentation convention (what it's for, how to install into a throwaway venv, why it's not part
   of `tests/run.py`'s core dependency set).
3. A new `servers.yaml` entry, `stdio` transport, plain `command`/`args` (structurally identical to
   the existing `gitlab`/`playwright`/`fetch` entries) — no templated `url`/`headers` needed. Decide
   the entry's `tags` (`core` vs `extended`) and state your reasoning explicitly in the MR
   description (does `@context-retriever`'s functionality need to be available unconditionally, or
   is `extended` more consistent with this being narrowly-scoped infrastructure rather than a
   general-purpose server every platform profile gets by default? — your call, either is
   defensible, just don't leave it undisclosed).
4. `implementation/knowledge/agents/context-retriever.md`'s `tools:` list updated: replace `execute`
   with the new exact Claude Code MCP tool name (`mcp__context-retriever__retrieve`) per §1.4's own
   text ("Grant `@context-retriever` only `mcp__context-retriever__retrieve` ... in place of
   `execute`"). Keep `read`/`search` unless you find a concrete reason they're no longer needed
   (disclose if you remove either).
5. `implementation/scripts/sync.mjs --root implementation` run and committed — all 7 platform
   projections regenerated with zero drift outside what this change actually causes (the new
   server's projection into each platform's MCP config, and `context-retriever`'s own regenerated
   agent file across platforms). Re-run with `--check` after committing and confirm clean.
6. A live adversarial test (new test file or an addition to `tests/functional/
   test_context_retriever.py`) that actually exercises the new server/grant and proves a write
   attempt is rejected — for example: (a) start the new server as a real subprocess over stdio, (b)
   attempt to call a tool name other than `retrieve` (e.g. a fabricated `write`/`execute`/`shell`
   tool name) and confirm the server has no such tool and rejects the call; (c) separately, confirm
   by direct inspection of the regenerated Claude Code projection
   (`implementation/.claude/agents/context-retriever.md`) that its `tools:` frontmatter no longer
   contains `Bash` anywhere, only `mcp__context-retriever__retrieve` (plus whatever of `read`/
   `search` you kept). This is the proof `task-T457.md` Expected Outputs item 3 asks for, for this
   agent specifically.

## Acceptance Criteria

1. The new server has exactly one callable tool, and that tool has no write/mutate path — verified
   by the adversarial test (Expected Output 6), not merely asserted in prose.
2. `.mcp.json`/`servers.yaml` diff against `origin/develop` (`7885989`) is scoped to exactly the new
   `context-retriever` entry — byte-level confirmation that every other existing entry (`gitlab`,
   `playwright`, `fetch`, `memory`, `sequential-thinking`, `brave`, `context7`, `hindsight`, `cwso`,
   `hf-mcp-server`, `filesystem`, `github`, `git`, `supabase`, `docker`, `postgresql`, `toolradar`)
   is byte-identical before/after, especially `filesystem`/`git` (not touched as a drive-by).
3. `node implementation/scripts/sync.mjs --root implementation --check` reports no drift after your
   commit.
4. `python3 tests/run.py` passes with no regressions against the pre-task baseline (report the exact
   pass/skip counts you observe).
5. `git diff --stat` against `origin/develop` shows no hits on `tests/golden/**`,
   `scripts/scorecard.py`, `docs/benchmarks/tb-subset.json`, `docs/benchmarks/tb-subset.md`.
6. A self-referential ledger-defect sweep: grep this brief and your own commits against the current
   real `stable`-tier component id list (`python3 implementation/scripts/check-maturity.py --root
   implementation --verbose`, derive it fresh yourself, do not assume a cached count) — report zero
   hits, or report a blocker if you find one.
7. Branch `agent/backend-developer/T495` pushed to `origin`, MR opened against `develop`
   (`glab mr create`), CI polled to completion and reported green — **left unmerged**. If `glab`
   shows an apparent auth issue, test both `PRIVATE-TOKEN` and `Authorization: Bearer` headers via a
   raw `curl` against `/api/v4/user` before concluding anything is broken (a prior task in this
   session hit a stale-token 401 that `glab api user` transparently refreshed).

## Blocker Protocol

Report any blocker with `type` (`technical` | `dependency` | `unclear_requirements` | `external`)
and `severity` (`critical` | `major` | `minor`) per `AGENTS.md`. Max 2 retries before escalating to
the orchestrator. If you find a design gap in §1.4 itself (e.g. the exact `mcp` SDK API doesn't
support what the design assumed), report `type: technical` with your concrete finding and a proposed
resolution — do not silently improvise something structurally different from §1.4's recommendation
without disclosing the deviation and why.

## Closure notes (orchestrator, 2026-09-17)

Independently re-verified against the pushed branch (not accepted on the implementer's self-report
alone) — full diff, adversarial test re-run in an isolated throwaway venv (8/8 pass), `sync.mjs
--check` clean, `.mcp.json`/registry diffs purely additive. Full detail, including a corrected
implementer self-report inaccuracy (the "4 pre-existing failures" claim does not hold under a
complete environment — plain `develop` is genuinely clean, 0 failures; the 2 that looked
pre-existing in an initial throwaway-venv check turned out to be that venv's own missing
`requests` dependency, not a repo defect; the other 2 were this branch's own false-positive
regression, now resolved by this closure) and two disclosed dispatch-mechanics fixes (plan
coverage; missing sibling brief), is recorded in `docs/tasks/active-tasks.md`'s T495 closure note
and this row's `docs/tasks/completed-tasks.md` entry — not duplicated here. MR !308 left unmerged
per the standing no-self-merge instruction.
