# `@context-retriever` — v1

**Based on:** `docs/artifacts/hybrid-retrieval-v1.md` §7 ("Interface for T454" — the exact
`MemoryIndex`/`Retriever`/`RequestingContext` API this document wraps, not re-derives);
`docs/artifacts/memory-scope-model-v1.md` §9 point 2 (the `project_id`/`platform` derivation this
task was explicitly deferred to implement), §4.2/§4.3 (the mandatory query-time scope filter this
document reuses unmodified); `docs/decisions/ADR-005-memory-layer-design.md` Decision 3 (the
three-place `ALLOW_WRITE=false` requirement) and its Validation section (the live-test wording this
document's §4 satisfies literally); `docs/artifacts/protected-paths-v1.md` §2 ("why three controls,
not one" — the structural precedent this document's §2 follows); `docs/plans/plan-035-roadmap-v7-
ground-up.md` §2.4 Phase 5, `docs/plans/plan-038-phase5-detailed-planning.md` (T454 per-task
summary).

**Refs:** T454. Wraps T453 (`implementation/runtime/memory/{retrieve,scope_filter}.py`), consumed
by (not built here): T455 (retrieval eval sub-suite), T456 (golden-suite ship gate).

**Status:** implementation artifact (not an ADR — no new architectural decision beyond what
ADR-005/memory-scope-model-v1.md already settled; this documents T454's own concrete choices: the
three-layer independence argument, the `RequestingContext` derivation mechanism, and the live-test
methodology/results).

---

## 1. What this component does

`@context-retriever` is a read-only agent (`implementation/knowledge/agents/context-retriever.md`,
the 28th agent source file) backed by a thin Python wrapper
(`implementation/runtime/memory/context_retriever.py`) around T453's existing hybrid-retrieval
`Retriever` API. It answers exactly one kind of request: "find prior knowledge relevant to
`<query>`," scoped to the calling session's own project and platform.

```
delegating agent
  -> @context-retriever (tools: read, search, execute -- no edit/write grant)
       -> ContextRetriever.query(query_text, workspace_root, platform_root, top_k)
            -> derive_requesting_context(workspace_root, platform_root)   # THIS task's own job
                 project_id  <- git remote of workspace_root (trusted, non-user-editable)
                 platform    <- .generated-manifest.json under platform_root (build-time constant)
            -> Retriever.search(query_text, requesting_context, top_k)    # T453's own API, unmodified
                 (mandatory scope pre-filter -> semantic+lexical+structural fusion -> top-K)
            -> [RetrievalResult.to_summary(), ...]                        # returned unmodified
```

No fusion, ranking, or scope-filtering logic is re-derived anywhere in this component — every
retrieval-quality property (the three-signal fusion, the mandatory filter-before-rank call order,
the cross-project unreachability guarantee) is exactly what `hybrid-retrieval-v1.md` already proved
for T453; this document only adds the agent surface, the derivation of the two `RequestingContext`
fields, and the three-layer read-only guarantee around it.

## 2. Three independent `ALLOW_WRITE=false` layers

Per `plan-035`'s literal wording ("one flag is not sufficient; three independent assertions are"),
restated in `plan-038` and ADR-005 Decision 3, and following the same "why three controls, not one"
structural pattern `protected-paths-v1.md` §2 already established for a different component (each
control there catches a different failure mode; no single one is sufficient by itself). The same
property holds here:

| Layer | Location | Mechanism | What it alone would block |
|---|---|---|---|
| 1. Agent definition | `implementation/knowledge/agents/context-retriever.md` | **Declarative/prose-only, not a technical tool-scoping restriction.** The source `tools:` list (`[read, search, execute]`) contains no `edit`/`write` token, but `execute` is not itself a scoped, read-only primitive — per the Claude Code platform manifest's own `toolMap` (`implementation/platforms/claude-code.json`: `"execute": "Bash"`), it projects to unrestricted `Bash`, confirmed live in the generated `implementation/.claude/agents/context-retriever.md` (`tools: Read, Bash`). This is the same declarative-enforcement trust model this repo's existing `implementation/knowledge/agents/security-engineer.md` "read-only mode" claim already relies on — an instruction the agent definition's prose gives the model, not a structural absence of a write-capable tool call | Nothing, technically. A `@context-retriever` session genuinely has a tool call (`Bash`) capable of writing a file; what stops it from doing so is the agent definition's own prose instruction ("you never write... you have no tool capable of doing it") being followed, not a restriction on the action space available to it. See §2.1 below |
| 2. Server config (this module) | `implementation/runtime/memory/context_retriever.py` | The module's entire public API surface (`ContextRetriever.query`, `main()`, and the free functions) has **no write/mutate function at all** — not a guarded one, an absent one | A caller that goes *through this module's own callable surface* (its Python API or its CLI) has no method or CLI flag to invoke that would write anything. This is a genuine technical property, but it only constrains callers that use this surface — see §2.1 for why a Bash-capable session is not such a caller by construction |
| 3. Deployment manifest | `deploy/docker-compose-context-retriever.yml` | Infrastructure-level: `read_only: true`, every volume mount `:ro`, `cap_drop: ["ALL"]`, no `secrets:` block (no write credential to the canonical git remote) | Would block a process running arbitrary code inside this component's own container (e.g. a supply-chain-compromised dependency) from writing anywhere — **but only if this component is actually deployed that way.** It is not, in this repo's current deployment model — see §2.1 |

**Why each was designed to be independent — the argument as originally intended, plus the honest
gap this task's own review found:**

- **Disabling layer 1 alone** (e.g. a misconfigured agent runtime that granted `edit` anyway):
  layer 2 would still hold for callers going through this module's own surface — even with an
  `Edit`/`Write` tool nominally available to the LLM, `ContextRetriever.query`/the CLI `main()` have
  no write path. This reasoning is correct as far as it goes, but it does not describe layer 1's
  *actual* current state (already not a technical restriction — §2.1), so it understates the real
  gap rather than describing a hypothetical one.
- **Disabling layer 2 alone** (hypothetically: someone adds a `write()` method to this module in a
  future, un-reviewed change): the *intended* design was that layer 1 would still hold (no tool call
  reaching the new method) and layer 3 would still hold (read-only mount). Given §2.1's finding,
  neither actually holds independently in the current deployment — a Bash-capable session could call
  the hypothetical new method directly, or bypass it and write the target file itself.
- **Disabling layer 3 alone** (e.g. deploying this component with a writable mount by mistake): the
  *intended* design was that layers 1 and 2 would still hold. Layer 2 still holds for module-surface
  callers; layer 1 does not hold as a technical matter, per §2.1.

Each layer is a **different kind of control in design intent** (LLM-facing declarative,
application-code structural, infrastructure/filesystem-permission), consistent with
`protected-paths-v1.md` §2's own reasoning for why plan-035's risk table assigns independent
controls rather than one mechanism referenced three times. **In the repo's actual current
deployment, only layer 2 is a genuine technical control** — see §2.1 for the honest accounting and
`docs/tasks/task-T457.md` for the tracked follow-up.

### 2.1 Honest note on what is and is not technically enforced today

This section exists because an earlier version of this document overstated layer 1's guarantee
(claiming "no tool call available that could write a file"), caught during this task's own MR
review, not self-caught during implementation. Stated plainly, without softening:

- **Layer 1 is prose, not a technical restriction.** The generated Claude Code agent definition
  (`implementation/.claude/agents/context-retriever.md`) grants `tools: Read, Bash` — `Bash` is
  unrestricted shell access, not a scoped read-only primitive. A `@context-retriever` session has a
  real tool call available that can create, modify, or delete any file it has filesystem permission
  to touch, entirely independent of `ContextRetriever`/`context_retriever.py`. What "enforces"
  read-only behavior at this layer is the agent definition's own instruction to the model, and the
  model choosing to follow it — the same trust model this repo's `security-engineer.md` "you operate
  in read-only mode" claim already relies on for a Bash-granted agent elsewhere in this repo. This is
  not a new or weaker standard invented for `@context-retriever`; it is this repo's existing,
  accepted posture for declarative-only agent controls, made explicit here rather than left implicit.
- **Layer 3 does not protect the real, current deployment.** As §5 below already states, this
  component's actual invocation today is a direct in-process Python call from an agent's Bash-backed
  `execute` tool grant — not a process running inside the `deploy/docker-compose-context-retriever.yml`
  container that manifest describes. That file is a declarative, checkable statement of what a future
  containerized/isolated deployment of this component must have; it is not a control actually
  protecting anything in production today.
- **Layer 2 is the one genuine technical control that exists today** — `context_retriever.py`'s
  public API has no write/mutate function. But this only constrains code paths that call *through*
  this module. It has no bearing on, and cannot prevent, a Bash-capable `@context-retriever` session
  writing to the knowledge vault or derived index directly via shell commands (`echo`, a `python3 -c`
  one-liner, editing a file in place, etc.) that never invoke this module at all.
- **Net honest statement:** in the real, non-containerized deployment this repo actually uses today,
  there is no write path that is *technically* blocked for a `@context-retriever` session — read-only
  behavior rests entirely on the agent definition's declarative instruction being followed by the
  model. This does not mean the three-layer design was pointless: layer 2 is real, and layers 1 and 3
  describe genuine (if currently unrealized) hardening that a future scoped-tool mechanism or actual
  containerized deployment would make real. It means the original "disabling any one alone does not
  enable a write" independence claim did not hold in the deployment this repo actually runs, and this
  document should not have asserted it did. Tracked as follow-up task **T457**
  (`docs/tasks/task-T457.md`) — give both `@security-engineer` and `@context-retriever` a genuinely
  scoped, non-`Bash` execution/read primitive. Not fixed in this task; recorded honestly instead.

## 3. `RequestingContext` derivation — non-spoofable by design

`memory-scope-model-v1.md` §9 point 2 flagged this derivation as a genuine ambiguity and explicitly
deferred its concrete resolution to this task ("T454's own brief should adopt this derivation
explicitly, since T454... is the task that actually implements the agent surface this identity
flows through"). This document's resolution, implemented in
`implementation/runtime/memory/context_retriever.py`:

### 3.1 `project_id` — from the workspace's own git remote

`derive_project_id(workspace_root)` runs `git -C <workspace_root> remote get-url origin` and
normalizes the result to a lowercase `<org>/<repo>` slug (`memory-scope-model-v1.md` §3's own
normalization convention — `gitlab.com/em-age/emage.code` -> `em-age/emage.code`).
`normalize_remote_to_project_id` is a pure function handling both URL shapes:

```
git@gitlab.com:em-age/emage.code.git       -> em-age/emage.code
https://gitlab.com/em-age/emage.code.git   -> em-age/emage.code
https://github.com/em-age/sia              -> em-age/sia   (no .git suffix, also handled)
```

**Concrete example demonstrating non-spoofability (acceptance criterion 4):**
`tests/functional/test_context_retriever.py::RequestingContextDerivationTests::
test_derive_project_id_reads_real_workspace_git_remote` creates a real temp git repo with remote
`git@gitlab.com:em-age/emage.code.git` and confirms `derive_project_id` returns `"em-age/emage.code"`
— read from real git configuration, not a parameter. A sibling test
(`test_derive_project_id_differs_for_a_different_workspace_remote`) repeats this against a second,
differently-configured temp repo (`https://github.com/em-age/sia.git` -> `"em-age/sia"`), proving
the function genuinely reads the workspace's own identity rather than returning a constant.
`derive_project_id`'s signature has exactly one parameter, `workspace_root: Path`
(`test_derive_project_id_signature_has_no_query_text_parameter`) — there is no argument through
which query text, a user prompt, or any other caller-editable value could reach this function at
all. If no remote is configured, `derive_project_id` raises `RemoteResolutionError` rather than
falling back to a default or inferred project — fail-closed, matching `RequestingContext`'s own
"no permissive no-context state" design (`scope_filter.py`'s `__post_init__`).

### 3.2 `platform` — from the platform's own build-time projection artifact

`resolve_platform(platform_root)` reads `<platform_root>/.generated-manifest.json`'s `platform`
field — the exact build artifact `implementation/scripts/sync.mjs`'s own `syncPlatform()` already
writes for every platform projection (one `.generated-manifest.json` per `outputDir`, e.g.
`implementation/.claude/.generated-manifest.json` carries `"platform": "claude-code"`, written by
the same sync run that produces `implementation/.claude/agents/context-retriever.md` itself). This
is the concrete instance of `hybrid-retrieval-v1.md` §7's "build-time-injected constant in each
platform's own projected agent config, the same mechanism `sync.mjs` already uses" — reusing an
existing build artifact rather than inventing a new signal, and requiring zero changes to
`sync.mjs` itself (`resolve_platform` only reads a file `sync.mjs` was already writing before this
task existed).

**Why this satisfies "never a runtime-settable parameter":** `resolve_platform`'s signature is
`resolve_platform(platform_root: Path) -> str` — the caller supplies a *path* to a platform's own
already-projected build output, never a free-text `platform: str` value directly. Two concrete
examples in the same directory produce different, correctly-resolved platforms
(`test_resolve_platform_differs_per_platform_root`: `.claude` -> `"claude-code"`, `.cursor` ->
`"cursor"`), demonstrating the mechanism actually discriminates by which platform's build output is
pointed at, not by an arbitrary string a caller chose.

**Trust-model caveat, stated explicitly (not silently assumed):** like `protected-paths-v1.md` §4's
own admission that its control is "declarative + auditable," not a cryptographic guarantee, this is
convention-plus-build-artifact trust, not a signed or tamper-evident value — a `.generated-
manifest.json` file could in principle be hand-edited on disk. This is the same trust model this
repo already applies to every other build artifact it treats as authoritative (e.g. `sync-no-diff`'s
own CI gate proves the *committed* projections match `sync.mjs`'s deterministic output, but nothing
prevents a local, uncommitted edit before that gate runs). No stronger guarantee was requested by
`memory-scope-model-v1.md` §9 point 2's own proposed resolution, and none is invented here.

### 3.3 One construction site, no duplication

`derive_requesting_context(workspace_root, platform_root)` is the **only** place either field is
combined into a `scope_filter.RequestingContext` — reused unmodified, not re-implemented as a
second context type. `tests/functional/test_context_retriever.py::
WrapperModulePublicApiSurfaceTests::test_no_second_scope_construction_site_in_module_source` asserts
the literal string `RequestingContext(` appears exactly once in this module's source, and that no
`is_visible`/`filter_candidates`/`filter_indices` function is redefined here (T453's own functions,
imported and called, never duplicated).

## 4. Live-test methodology and results (ADR-005 Validation section)

ADR-005's Validation section requires, verbatim: *"the three-place `ALLOW_WRITE=false` assertion is
live-tested (attempt a write through `@context-retriever` and confirm it is rejected at all three
layers), mirroring the live-removal-probe verification pattern already established for T416's
protected paths."* `memory-scope-model-v1.md` §8's own verification list restates this as: *"attempt
to have `@context-retriever` write or patch a chunk's scope metadata through any exposed tool call;
confirm it is rejected at all three of ADR-005 Decision 3's existing assertion points, and
additionally confirm no tool call exists that would let it set scope in the first place."*

`tests/functional/test_context_retriever.py` implements this as four test classes:

- **`AgentDefinitionToolsListTests`** (layer 1, static): parses `context-retriever.md`'s real
  frontmatter and asserts the `tools:` list is disjoint from `{edit, write}`; separately parses the
  real, `sync.mjs`-projected `implementation/.claude/agents/context-retriever.md` and asserts its
  translated tools string (`Read, Bash`) contains no `Edit`/`Write` token either — proving the
  read-only grant survives the abstract-to-concrete tool-name translation, not just the source
  vocabulary.
- **`WrapperModulePublicApiSurfaceTests`** (layer 2, static/reflection-based): asserts `ALLOW_WRITE
  is False`; enumerates every public callable defined in `context_retriever.py` and every public
  method on `ContextRetriever` and asserts none matches a write-verb name pattern
  (`write|save|persist|delete|update|mutate|patch|set_scope|commit|...`) — `ContextRetriever`'s
  public methods are exactly `{"query"}`; enumerates the real CLI's registered flags and asserts
  none is write-shaped.
- **`DeploymentManifestReadOnlyTests`** (layer 3, static): parses the real YAML manifest and asserts
  `read_only: true`, every volume mount ends in `:ro`, no `secrets:` block exists anywhere in the
  file, and `cap_drop: ["ALL"]`.
- **`EndToEndAdversarialWriteProbeTests`** (live, end-to-end, real callable surface — not a mock):
  builds a real on-disk index (`index.jsonl`/`manifest.json`, the same shape `MemoryIndex.load`
  reads in production) and a real temp git workspace, then:
  1. **Attempts a write via the real `ContextRetriever` instance's attribute surface**
     (`getattr(retriever, "write")`, `"save"`, `"delete"`, `"set_scope"`, etc.) — every attempt
     raises `AttributeError`: rejected because the capability is structurally absent, not merely
     guarded.
  2. **Attempts a write via the real CLI's `main()` entrypoint** with an invented `--write
     malicious-payload` flag — rejected by `argparse` itself (`SystemExit`) because no such flag was
     ever registered.
  3. **Attempts a write via adversarial query CONTENT** (a prompt-injection-shaped query text
     instructing the retriever to "write... and DELETE the derived index") passed through the real,
     un-mocked `.query()` method — the call returns a normal read-only result list, and a
     before/after filesystem snapshot (every file's size and mtime under the test's temp root)
     is byte-for-byte identical, proving the module is inert to instruction-shaped query content
     structurally (it only ever reads chunks and returns summaries), not merely by convention.

**Result, stated honestly (corrected from an earlier overclaim caught during this task's own MR
review):** these four test classes prove exactly what they test — the agent definition's *source*
`tools:` vocabulary excludes `edit`/`write` (layer 1, static, source-level only); the module's public
API and CLI have no write-shaped callable (layer 2, static and live); the deployment manifest
declares read-only infrastructure (layer 3, static); and `ContextRetriever`'s own attribute surface,
CLI, and `.query()` method reject every attempted write routed *through this component's own API*
(the live probe). **They do not, and cannot, prove that a `@context-retriever` LLM session is unable
to write** — that session's real, generated tool grant is `Read, Bash` (§2.1), and no test in this
suite exercises the session's independent Bash access outside `ContextRetriever`'s own callable
surface, because doing so would require simulating an actual agent-runtime tool-call loop, not a
direct Python/CLI probe. **All three layers hold as static/structural properties of the code and
config as written; only layer 2 holds as an actual barrier against a real `@context-retriever`
session with Bash access, and even it only barriers callers who go through this module** — see §2.1
for the full honest accounting and `docs/tasks/task-T457.md` for the tracked follow-up.

## 5. Known limitations / follow-ups for T455+

- `resolve_platform`'s trust model (§3.2's caveat) is convention-plus-build-artifact, not
  cryptographically verified — consistent with this repo's existing `protected-paths-v1.md`
  precedent, but flagged here for whoever next hardens this component's deployment story.
- `derive_project_id`'s git-remote-URL parser (`_REMOTE_RE`) handles the standard `https://`,
  `ssh://`, and `git@host:path` forms this repo's own remotes use, but does not handle a
  non-standard custom-port SSH URL (`ssh://git@host:2222/org/repo.git`) — not exercised by any
  remote this repo or its sibling projects (`sia`, `sia-harness`, `CWSO`) actually use; flagged as a
  scoped limitation rather than silently handled incorrectly.
- This component's actual invocation in the current deployment model is a direct in-process Python
  call from an agent's `execute`/Bash tool grant, not a standalone container — `deploy/docker-
  compose-context-retriever.yml` is a declarative, checkable statement of the runtime permissions a
  containerized/isolated deployment of this component must have (the same posture
  `protected-paths-v1.md` §4 already documents for its own declarative-not-enforced control), not a
  claim that this exact compose file is running in production today. **This is the concrete reason
  layer 3 does not protect the real deployment — see §2.1** ("Honest note on what is and is not
  technically enforced today") for the full accounting of what this means for layers 1 and 3
  combined with the `execute` → `Bash` tool-grant reality. Tracked as follow-up **T457**
  (`docs/tasks/task-T457.md`, not dispatched this session): give both `@security-engineer` and
  `@context-retriever` a genuinely scoped, non-`Bash` execution/read primitive — the likely real fix
  touches `.mcp.json` in some form, out of scope for immediate dispatch this session.
- T455's retrieval-eval sub-suite and T456's golden-suite ship gate are the next consumers of this
  interface; neither is built here (out of this task's scope per its own Constraints).
