# ADR-005 — Memory-layer design: storage/format, embeddings provider, read-only default

> Filename: `ADR-005-memory-layer-design.md`

- **Status**: Accepted — approved 2026-09-09 by the user (all three decisions); dispatch of
  T451–T456 is authorized subject to each task's own dependency graph and briefs
- **Date**: 2026-09-09
- **Decider(s)**: solution-architect
- **Tasks**: T450, T451, T452, T453, T454
- **Requirements**: `plan-035-roadmap-v7-ground-up.md` §2.4 Phase 5; `plan-038-phase5-detailed-
  planning.md` (approved, merged to `develop`) — its T450 per-task summary and its "embeddings-API
  cost question" framing section
- **Evidence**: `https://solomd.app/` (fetched directly, 2026-09-09 — see "SoloMD" subsection
  below); OpenAI embedding pricing and MTEB figures (fetched/searched directly, 2026-09-09 — see
  "Embeddings provider decision" below); `docs/decisions/_template.md`

## Context

`plan-035` §2.4 Phase 5 adopts a memory-layer design ("tree-sitter → chunk → embed → hybrid
retrieve, `<500ms` on 100K LOC, `@context-retriever`") but explicitly defers three decisions to
this ADR (T450's row): the storage/format substrate — labelled "SoloMD-vs-alternatives" in the
plan — the embeddings-provider choice, and the read-only-by-default principle that will govern
T454's `@context-retriever` agent.

Two constraints shape all three decisions:

1. **emage.code is a multi-agent orchestration system, not a single-user tool.** T451 (not yet
   designed in detail, but already scoped in `plan-035`) will define three *enforced* scopes:
   `general` (harness knowledge, curated), `project` (this repo only), and `shared`
   (cross-platform, explicit opt-in per entry). The `shared` scope is explicitly cross-platform and
   multi-consumer — read by multiple concurrent agent sessions, potentially across different
   projects and different coding-agent platforms (Claude Code, Codex, Gemini, etc., per this
   repo's own 7-platform projection model). Scope must be set at write time and must not be
   inferable at read time (`plan-035`'s own Phase 5 acceptance criterion).
2. **The embeddings-provider decision is the one item in Phase 5 with a real-money profile.**
   `plan-038` (the approved Phase 5 detailed plan) frames this explicitly: unlike T407's
   Terminal-Bench cost (one-off, bounded, single authorization), a paid embeddings API would be
   invoked at every indexing run (T452) *and* at every retrieval query thereafter (T453, T454, and
   every future `@context-retriever` call) — a recurring, unbounded-by-default operational cost. If
   this ADR recommends a paid provider, `plan-038`'s gate applies: T452's brief may not be
   dispatched until the user explicitly authorizes the recurring spend.

`plan-035`'s T450 row uses the label **"SoloMD"** for one side of the storage/format comparison.
This term does not resolve anywhere in this repository, and a prior planning pass
(`plan-038`, "embeddings-API cost question" section) confirmed a general web search by name alone
also failed to resolve it. This session independently fetched `https://solomd.app/` directly (not
inferred from the label) and confirms it is a real product — see below. Per this task's blocker
protocol, failing to recover the *original* source-document meaning of "SoloMD" beyond what is
confirmed by that fetch is explicitly not a blocker; this ADR proceeds by treating the confirmed
SoloMD product page as one concrete comparison point and defining emage.code's actual alternatives
from first principles, as instructed.

## Decision

This ADR makes three decisions.

### Decision 1 — Storage/format substrate: git-versioned knowledge store + locally-built vector index (not SoloMD's design)

**We adopt a git-versioned, plain-text/frontmatter knowledge store as the canonical source of
truth, with a separately-built, read-only vector index derived from it at index time (T452).**
Concretely: entries live as Markdown files with YAML frontmatter (a `scope:` field among others)
under a knowledge tree analogous to this repo's existing `docs/`/`implementation/knowledge/`
convention; the canonical store is written *only* through this repo's normal git workflow (commits
reviewed via merge request, per `.claude/rules/git-workflow.md`) — never by a live agent write
call. T452's indexing pipeline parses this tree, chunks it (tree-sitter for code, section-aware
chunking for prose), embeds each chunk, and writes the result to a **derived, rebuildable** vector
index. That index is what T453/T454 query. It is not the canonical store, and rebuilding it from a
clean git checkout must always reproduce it — the same property this repo already requires of its
knowledge-registry regeneration (`sync.mjs`/`generate-registry.py`).

This is a deliberate divergence from what a literal reading of "SoloMD does X, so we do X" would
produce. See the "SoloMD" subsection below for why.

### Decision 2 — Embeddings provider: local/open-source model, zero recurring cost

**We choose a local, open-source embedding model, run on infrastructure emage.code already has
access to (CPU, or GPU where available — the same class of environment this very session runs in).
No paid embeddings API is adopted.** Cost profile: **none** — no per-token, per-call, or
subscription cost, one-off or recurring. This resolves `plan-038`'s cost-authorization gate in the
negative: **T452 does not require user cost-authorization before dispatch**, because no recurring
spend is incurred. Primary candidate: **`nomic-embed-text-v1.5`** (Apache-2.0, 137M parameters,
768-dim with Matryoshka truncation down to 64-dim, 8192-token context). Fallback candidate for
lower-resource environments: **`bge-small-en-v1.5`** (MIT, 33.4M parameters, 384-dim). Final
selection between the two — and any further tuning of truncated dimensionality for the
latency/storage tradeoff — is left to T455's retrieval eval sub-suite to decide empirically; this
ADR locks the "local, not paid-API" decision, not the exact model build.

See "Embeddings provider decision" below for the grounded quality/latency/hardware reasoning.

### Decision 3 — Read-only-by-default: the canonical knowledge base has no agent write path

**No agent, including `@context-retriever` (T454), may write to the canonical knowledge base or
its derived index.** The canonical store's only write path is the existing git workflow (human-
reviewed merge requests). The derived vector index's only write path is T452's indexing pipeline,
which runs as an explicit, auditable rebuild step — not a live call any agent can trigger
mid-session. `@context-retriever` (T454) is read-only by construction: `ALLOW_WRITE=false` must be
asserted in three independent places — the agent definition, the server config, and the deployment
manifest — per `plan-035`'s own explicit redundancy requirement (one flag is not sufficient; three
independent assertions are). This mirrors this repo's existing "protected paths" pattern
(`docs/artifacts/protected-paths-v1.md`, established for `tests/golden/**` in Phase 1/T416): a
component that must never be self-modified by the thing it evaluates or informs is declared
out-of-write-scope in more than one place, so a single missed update cannot silently reopen the
gap.

## Reasoning: why emage.code's multi-agent/shared-memory requirements do not favor SoloMD's design

This is required reasoning, not an appended caveat, per this task's acceptance criteria.

**What SoloMD actually is, confirmed directly (`https://solomd.app/`, fetched 2026-09-09).** SoloMD
is a free, MIT-licensed, open-source Markdown editor for macOS/Windows/Linux/Android/iOS. It is
explicitly local-first: notes are plain UTF-8 Markdown files in a user-selected folder on one
device. Its semantic search is genuinely on-device — "no model file download, no network call,
ever" — with an embedder running inside its own Rust process and an index stored at
`.solomd/embeddings.sqlite`. It has no built-in CRDT sync; multi-device use relies on external
folder-sync tools (iCloud/Dropbox/OneDrive/Syncthing) or an optional GitHub-backed sync with
client-side encryption. Its bundled MCP server exposes **read-only tools by default** — write
tools require an explicit `--allow-write` flag — and it supports 14 BYOK LLM providers for its own
AI features. It has no API or mechanism for an external multi-agent system to persistently write
structured, scoped data back into it, and no concept of concurrent multi-user or multi-session
access at all: it is designed around exactly one person editing exactly one folder on (at most, via
folder-sync) their own set of devices.

**Where this transfers to emage.code, and where it does not.**

- **Transfers: read-only-by-default for agent-facing tool exposure.** SoloMD's own MCP server
  ships read-only, opt-in-write — the same posture Decision 3 above adopts for
  `@context-retriever`. This is the one point of direct design alignment, and it is adopted
  explicitly (see Decision 3), not by unexamined imitation — it is independently justified by this
  repo's own protected-paths precedent (T416) regardless of SoloMD's example.
- **Transfers: local, on-device embeddings as a real zero-cost existence proof.** SoloMD's "$0
  forever" local-embeddings model demonstrates that fully local semantic search is a viable,
  shipped, non-toy design, not merely a theoretical option — this is one input into Decision 2, but
  not the deciding one; Decision 2 is grounded independently in emage.code's own quality/latency
  numbers below, because SoloMD's use case (searching one person's personal notes) has a much
  lower quality bar than a multi-agent system whose retrieval output feeds directly into other
  agents' task execution.
- **Does not transfer: single-device storage and no write-back API.** emage.code's `shared` scope
  is explicitly cross-platform and multi-consumer — read by multiple concurrent agent sessions,
  potentially on different machines and different coding-agent platforms simultaneously. SoloMD has
  no mechanism for this at all; its "multi-device" story is external folder-sync of one person's
  own files, not concurrent access by independent consumers who did not author the content. A
  design that copied SoloMD's substrate literally (one local SQLite embeddings file per device,
  no write-back API) would have no way to satisfy `plan-035`'s own Phase 5 acceptance criterion
  that a `project`-scoped entry be "provably unreachable from a different project's session" while
  a `shared`-scoped entry *is* reachable across sessions — SoloMD's model has no scope concept at
  all, let alone an enforced one.
- **Does not transfer: no external write-back path.** emage.code's indexing pipeline (T452) is
  itself the "write path" that populates the derived index from the canonical git store — a role
  SoloMD's design has no equivalent of, because SoloMD's embeddings index is built from files the
  same single user is directly editing in the same app, not from a separately-governed multi-writer
  knowledge base that other automated systems contribute to via reviewed commits.

**The concrete alternative named and compared, per this task's acceptance criteria:** a
conventional server-side vector-DB-backed store (Chroma, Qdrant, or pgvector running as a shared
service) was considered as the multi-consumer-native alternative to SoloMD's single-device design.
It was **not** chosen as the primary substrate for this ADR — see the Alternatives table below for
the full comparison — because emage.code's actual near-term requirement (concurrent *readers*
against a periodically-rebuilt index, not concurrent *writers* contending for a single mutable
store) is satisfied by the git-versioned-source + locally-rebuilt-index design without adding a
persistent service dependency this repo does not otherwise require. This is flagged explicitly as
a reasoned choice, not an oversight: if T451's scope-enforcement design or T453's retrieval-latency
work later surfaces a real need for a single shared mutable index serving many concurrent readers
without each needing its own rebuilt copy, a server-side vector DB is the documented upgrade path
(see Consequences → Follow-ups), not a design this ADR forecloses.

## Embeddings provider decision — grounded reasoning

**Quality.** OpenAI's `text-embedding-3-small` — the most commonly cited "cheap hosted" embeddings
option — scores **62.3% average on MTEB** (English tasks), per OpenAI's own published announcement
of the v3 embedding models (verified via direct search, 2026-09-09; the announcement states the
improvement from `text-embedding-ada-002`'s 61.0% to `text-embedding-3-small`'s 62.3%). The local
candidate, **`nomic-embed-text-v1.5`, scores 62.28 on MTEB** (verified via direct search,
2026-09-09) — within noise of the paid hosted option, not a meaningfully worse alternative. This is
the central fact this decision rests on: the quality gap that would normally justify paying for a
hosted embeddings API does not exist here. The fallback candidate, `bge-small-en-v1.5`, scores
lower on MTEB retrieval specifically (53.9 average NDCG@10 on MTEB v2 retrieval, per direct
search) but is far smaller (33.4M parameters vs. nomic's 137M) and is named as the option to fall
back to if `nomic-embed-text-v1.5`'s resource footprint proves too heavy for a constrained CI or
agent-sandbox environment — a tradeoff for T455 to resolve empirically, not this ADR to pre-decide.

**Latency, against the `<500ms` p95 target.** The `<500ms` budget (`plan-035`'s own Phase 5
headline acceptance criterion, restated in `plan-038`) covers the full retrieval path: embedding
the query, vector search against the 100K-LOC-repo index, lexical and structural signal fusion
(T453), and ranking. A local embedding call for one short query string, run in-process or via a
local server (no network hop), completes in tens of milliseconds on CPU — this is architecturally
favorable *specifically because* it removes the one variable-latency, non-local step a hosted API
would otherwise add to every single query: a network round-trip. Hosted embedding APIs typically
add on the order of 100–300ms of network + queueing latency per call before any local ranking work
even starts, and that latency is only partially within emage.code's control (subject to the
provider's own load and the caller's network conditions) — a source of exactly the kind of
p95-tail variance a hard latency budget is most vulnerable to. A local embedding step spends a
small, predictable slice of the 500ms budget and leaves the remainder for T453's actual retrieval
and ranking work, which is where the harder design problem (hybrid semantic + lexical + structural
fusion) actually lives.

**Hardware.** emage.code's indexing (T452) and retrieval (T453/T454) both run inside environments
that already have real CPU (and, per this task's own brief, potentially GPU) resources available —
the same class of environment this session itself runs in. `nomic-embed-text-v1.5` at 137M
parameters and `bge-small-en-v1.5` at 33.4M parameters are both small enough to run comfortably on
CPU alone (both are shipped as CPU-friendly options via Ollama/`sentence-transformers`, per direct
search of current deployment guides), so no new GPU provisioning is required to adopt either.

**Recurring vs. one-off, restated explicitly per this task's acceptance criteria:** because the
decision is a local/open-source model, **the cost profile is none** — not a one-off cost and not a
recurring cost. There is no per-token or per-call unit price to state, because no paid API is being
invoked. This is stated as an explicit, load-bearing conclusion, not left implicit: **T452 and
T453 may be dispatched without a separate user cost-authorization step**, because `plan-038`'s
gate ("if T450 recommends a hosted/paid embeddings provider, T452's brief must not be dispatched
until the user explicitly authorizes the recurring cost") does not apply — no hosted provider is
recommended.

## Alternatives considered

### Storage / format substrate

| Option | Pros | Cons | Why not chosen |
|--------|------|------|----------------|
| **SoloMD's design** (single local SQLite embeddings file per device, folder-sync for multi-device, read-only-default MCP, no write-back API) | Zero-cost existence proof for fully local embeddings; read-only-default posture is genuinely good practice | No scope concept at all; no concurrent multi-consumer access; no write-back path for an external indexing pipeline to populate it; "multi-device" means folder-sync of one person's own files, not independent readers/writers | Does not satisfy `plan-035`'s own Phase 5 acceptance criteria (enforced, provably-isolated scopes; multi-consumer `shared` scope) — see "Reasoning" above |
| **Git-versioned Markdown/frontmatter store + locally-rebuilt vector index (chosen)** | Reuses this repo's existing, already-governed knowledge-tree convention and git-review write path; scope tag lives in frontmatter, set at write time, satisfying the "cannot be inferred at read time" criterion directly; no new persistent service to operate; index rebuild is deterministic and auditable, same pattern as `sync.mjs`/registry regeneration | Index is a periodically-rebuilt derived artifact, not live-updated; very-low-latency "index reflects the last second's writes" use cases are not served | Chosen: matches emage.code's actual write pattern (human-reviewed commits, not live agent writes) and its actual read pattern (concurrent readers against a point-in-time index), without adding infrastructure this repo does not otherwise need |
| **Server-side vector DB (Chroma / Qdrant / pgvector) as the canonical or primary store** | Naturally multi-consumer; a single mutable index avoids per-consumer rebuild staleness; well-trodden pattern for RAG systems with many concurrent readers and writers | Introduces a persistent service dependency (must be deployed, operated, and kept available for every retrieval call); does not by itself solve the scope-enforcement or write-governance problem — scope tagging and the git-review write discipline would still need to be layered on top | Not chosen as the primary substrate now: emage.code's near-term need is concurrent *reading* of a periodically-rebuilt index, not concurrent *writing* to a single mutable store. Documented as the upgrade path if that need changes (see Consequences → Follow-ups) |

### Embeddings provider

| Option | Pros | Cons | Why not chosen |
|--------|------|------|----------------|
| **Paid hosted API** (e.g. OpenAI `text-embedding-3-small`, $0.02/M input tokens per direct pricing search, 2026-09-09) | No local compute/model-management burden; marginal quality edge on some benchmarks; simple integration | Recurring cost incurred at every indexing run *and* every retrieval query, unbounded by default; per-query network round-trip adds latency variance directly against the `<500ms` p95 budget; sends chunked source-code content to a third-party API on every call | Not chosen: quality parity with the local option (62.3% vs. 62.28% MTEB) does not justify converting a currently-zero, currently-local cost into an unbounded recurring one, and the network round-trip works directly against the latency target |
| **Local/open-source model — `nomic-embed-text-v1.5` primary, `bge-small-en-v1.5` fallback (chosen)** | Zero cost, one-off or recurring; MTEB quality within noise of the paid hosted option; no network round-trip in the retrieval hot path; runs on CPU already available in emage.code's own environments; no source code leaves the local environment | Requires managing a local model artifact/runtime (Ollama or `sentence-transformers`) as part of T452/T453's implementation; local model quality could still trail a larger paid model (e.g. `text-embedding-3-large`) on some benchmarks | Chosen: resolves `plan-038`'s cost-authorization gate in the negative (no gate applies), and the quality/latency reasoning above holds independently of the cost question |

## Consequences

- **Positive**:
  - No user cost-authorization step is required before T452/T453 dispatch — `plan-038`'s
    recurring-cost gate does not apply, unblocking Phase 5's two `large`-scope tasks immediately
    once this ADR is accepted.
  - The canonical knowledge base's write path is identical to every other governed artifact in this
    repo (git commit + reviewed merge request) — no new write-governance model needs to be
    invented or explained to future agents.
  - Read-only enforcement for `@context-retriever` reuses an already-proven pattern in this repo
    (protected paths, T416) rather than inventing a new mechanism.
  - No source code or proprietary content leaves the local environment via an embeddings API call.

- **Negative**:
  - The derived vector index is only as fresh as its last rebuild; a purely "live update on every
    commit" retrieval experience is not what this design provides out of the box. T452's indexing
    pipeline must define a rebuild cadence/trigger (out of scope for this ADR; T452's own brief).
  - Adopting a local embedding model means T452/T453's implementation owns model lifecycle
    concerns (version pinning, artifact distribution, runtime dependency) that a hosted API would
    have externalized.
  - `bge-small-en-v1.5`'s retrieval MTEB score (53.9) trails `nomic-embed-text-v1.5`'s general MTEB
    score; if resource constraints force the fallback model, T455's eval sub-suite must confirm the
    `<500ms`-and-quality targets still hold with it, not assume parity.

- **Risks introduced**:
  - If concurrent-writer contention against the derived index becomes a real requirement later
    (not currently identified), the periodic-rebuild design will need to migrate toward the
    deferred server-side vector-DB alternative — a nontrivial follow-on architecture change, not a
    configuration tweak.
  - A future decision to add a paid embeddings provider as a secondary/comparison option (e.g. for
    a `text-embedding-3-large`-quality tier) would reopen `plan-038`'s cost-authorization gate; this
    ADR's "no gate applies" conclusion is specific to the current local-only decision and does not
    generalize to any future provider addition.

- **Follow-ups**:
  - T451 — design the three enforced scopes on top of this ADR's frontmatter-tagged,
    git-versioned substrate.
  - T452 — implement the indexing pipeline against `nomic-embed-text-v1.5` (or `bge-small-en-v1.5`
    if T455 finds it necessary), consuming this ADR's storage decision and T451's scope model.
  - T453 — implement hybrid retrieval against the derived index, budgeting the `<500ms` p95 target
    per the latency reasoning above.
  - T454 — implement `@context-retriever` with the three-place `ALLOW_WRITE=false` assertion
    required by Decision 3.
  - T455 — empirically resolve `nomic-embed-text-v1.5` vs. `bge-small-en-v1.5` (and any
    dimensionality truncation) against real precision/recall/latency numbers, not the MTEB
    benchmark figures alone.
  - Documented, not yet scheduled: revisit the server-side vector-DB alternative if a genuine
    concurrent-writer or live-update requirement is identified after T451–T456 ship.

## Validation

This decision is validated, not merely asserted, by the following downstream checks — all already
scoped to Phase 5 tasks in `plan-035`/`plan-038`, not new work invented by this ADR:

- **Scope isolation** (T451's own acceptance criterion): a `project`-scoped entry is provably
  unreachable from a different project's session — confirms the frontmatter-scope-at-write-time
  design actually enforces what Decision 1 claims it enforces.
- **Latency** (T453/Phase 5's own headline acceptance criterion): `<500ms` p95 retrieval measured
  on a real 100K-LOC repo — confirms the local-embeddings latency reasoning above holds under real
  load, not just the tens-of-milliseconds estimate cited here.
- **Retrieval quality** (T455): precision, recall, and irrelevant-context rate measured
  independently, before any downstream capability claim — confirms `nomic-embed-text-v1.5`'s MTEB
  parity with the paid hosted option translates into real retrieval quality for emage.code's actual
  chunked code/knowledge corpus, not just the general-purpose MTEB tasks it was benchmarked on.
- **No-cost confirmation**: T452/T453's implementation must not require any embeddings-provider API
  key or network egress to an embeddings API to function — this is a direct, checkable consequence
  of Decision 2 and should be verified at T452's completion (e.g. the indexing pipeline runs
  correctly with no such credential configured).
- **Read-only enforcement** (T454): the three-place `ALLOW_WRITE=false` assertion is live-tested
  (attempt a write through `@context-retriever` and confirm it is rejected at all three layers),
  mirroring the live-removal-probe verification pattern already established for T416's protected
  paths.
- **Downstream ship gate** (T456, Phase 5's own literal rule): if the golden suite does not improve
  with retrieval enabled, the feature does not ship — this is the ultimate test of whether this
  ADR's substrate and provider choices were the right ones, independent of any individual metric
  above.

## Approval

This ADR's status is **`proposed`**, not `accepted`. Per `plan-035`'s own T450 scoping and this
task's brief, it does not self-authorize dispatch of T451–T456 or any other downstream task.
Advancing to `accepted` requires explicit human (user) approval of:

- [ ] Decision 1 — git-versioned knowledge store + locally-rebuilt vector index as the storage/
      format substrate (rejecting SoloMD's single-device design and deferring the server-side
      vector-DB alternative)
- [ ] Decision 2 — local/open-source embeddings (`nomic-embed-text-v1.5` primary,
      `bge-small-en-v1.5` fallback), zero cost profile, no paid-API cost-authorization gate applies
- [ ] Decision 3 — read-only-by-default for the canonical knowledge base and for `@context-retriever`
      (T454), enforced via the three-place `ALLOW_WRITE=false` assertion

Until approved, T451–T454 briefs may be drafted with reference to this ADR's conclusions but should
not be dispatched as final designs.
