# Indexing Pipeline — v1

**Based on:** `docs/decisions/ADR-005-memory-layer-design.md` (accepted 2026-09-09) — Decision 1
(storage substrate), Decision 2 (embeddings provider), Decision 3 (read-only-by-default);
`docs/artifacts/memory-scope-model-v1.md` (T451, accepted design) — §3 (frontmatter schema), §4
(the `include(entry, P)` enforcement mechanism), §5 (write-time-only validation), §10 ("Handoff to
T452"); `docs/plans/plan-035-roadmap-v7-ground-up.md` §2.4 Phase 5 (T452's enrichment field list).

**Refs:** T452. Implemented in `implementation/runtime/memory/`. Consumed by: T453 (hybrid
retrieval — this document is written so T453 can query the index without re-deriving this design).

**Status:** implementation artifact (not an ADR — no new architectural decision beyond what
ADR-005/memory-scope-model-v1.md already settled; this documents the concrete choices T452's own
brief explicitly left open: on-disk index format, chunking library, embedding-model runtime).

---

## 1. What this pipeline does

`implementation/runtime/memory/build.py` turns a knowledge vault (git-versioned Markdown +
YAML frontmatter, per ADR-005 Decision 1) into a derived, on-disk, rebuildable vector index, for
one explicit "building for project `P`" identity at a time:

```
scan (structural, repo-boundary-partitioned)
  -> validate (§5, write-time-only, reject-not-default)
    -> chunk (tree-sitter for code, section-aware for prose)
      -> enrich (plan-035 fields + §4.2 scope metadata)
        -> embed (local model, ADR-005 Decision 2)
          -> write (deterministic JSONL + manifest)
```

Every stage is a separate, independently importable module under
`implementation/runtime/memory/` — see that directory's own `README.md` for the module table.

## 2. On-disk index format

One output directory per build (`--output-dir`), containing exactly three files:

```
<output_dir>/
├── index.jsonl        one JSON object per chunk, sorted by (path, line_range, chunk_id)
├── rejections.jsonl    one JSON object per §5 rejection, sorted by (repo_id, source_path)
└── manifest.json        deterministic build summary (see §5 below)
```

`index.jsonl`/`rejections.jsonl` are plain JSON-Lines (one record per line, no wrapping array) —
trivially streamable by T453 without loading the whole index into memory, and diffable line-by-line
for the rebuild-determinism check (§5).

### 2.1 Chunk metadata schema (`index.jsonl`, one line)

```json
{
  "chunk_id": "implementation/knowledge/memory/project/example.md::chunk0::ea9fdcf62cbb",
  "text": "...the chunk's raw text...",
  "vector": [0.0123, -0.0456, "... 768 floats, L2-unit-normalized ..."],
  "embedding_model": "nomic-ai/nomic-embed-text-v1.5",
  "embedding_dim": 768,

  "path": "implementation/knowledge/memory/project/example.md",
  "repo_id": "em-age/emage.code",
  "commit": "8732ef8cadeedc17fe7ef0bbc220ce036eaeeac5",

  "content_type": "code",
  "language": "python",
  "symbol": "foo",
  "ast_type": "function_definition",
  "parents": ["Bar"],
  "imports": ["import os"],
  "line_range": [12, 14],

  "title": "Entry title from frontmatter",
  "tags": ["tag-a", "tag-b"],

  "scope": "project",
  "project_id": "em-age/emage.code",
  "shared_consumers": null
}
```

Field groups:

- **Embedding fields** (`vector`, `embedding_model`, `embedding_dim`): `vector` is always L2-unit
  length (cosine similarity == dot product at query time); `embedding_model`/`embedding_dim` are
  per-chunk (not just per-build) so T453 can refuse to compare vectors from mixed model builds if
  an index is ever assembled from multiple runs.
- **Provenance/enrichment fields** — plan-035's own list (path, symbol, language, AST type,
  parents, imports, line range, commit), plus `repo_id` (which repo checkout the entry came from —
  needed because `shared`-scope chunks originate from a different repo than the one being built
  for): see §3 for the code-vs-prose chunking approach that produces `symbol`/`ast_type`/`parents`/
  `imports`.
- **Entry-level fields** (`title`, `tags`): carried through unchanged from frontmatter, repeated on
  every chunk from the same entry (denormalized, so T453 never needs a second lookup to display a
  result's title).
- **Scope metadata** (`scope`, `project_id`, `shared_consumers`) — memory-scope-model-v1.md §4.2's
  required fields, written once at build time, immutable thereafter. `project_id` is `null` unless
  `scope == "project"`; `shared_consumers` is `null` unless `scope == "shared"` (mirrors §3's
  frontmatter schema exactly — this is the "T453's query-time filter" defense-in-depth control
  §4.2 specifies, T452's job is only to persist it faithfully).

### 2.2 Rejection record schema (`rejections.jsonl`, one line)

```json
{"source_path": "implementation/knowledge/memory/project/bad-entry.md",
 "repo_id": "em-age/emage.code", "commit": "8732ef6...",
 "reason": "missing scope field", "scope_attempted": null}
```

Auditable per §5: every entry that fails write-time validation is logged here — source path,
commit SHA, and a human-readable reason — never silently dropped. `scope_attempted` is the raw
(possibly malformed) `scope:` value seen, or `null` if the field was absent entirely, so a human
reviewing the log can distinguish "typo'd scope value" from "forgot the field."

### 2.3 Manifest schema (`manifest.json`)

```json
{"project_id": "em-age/emage.code", "embedding_model": "nomic-ai/nomic-embed-text-v1.5",
 "embedding_dim": 768, "entry_count": 2, "chunk_count": 6, "rejection_count": 2,
 "index_format_version": 1}
```

Deliberately **excludes** any field that would vary run-to-run for reasons unrelated to actual
content (timestamps, PIDs, absolute paths, hostnames) — this is what makes the manifest part of
the rebuild-determinism comparison rather than a source of spurious diffs. `index_format_version`
is bumped on any future breaking change to this schema, so T453 can detect an incompatible index.

## 3. Chunking approach per content type

A vault entry's body is Markdown (ADR-005 Decision 1); code appears inside it as fenced blocks
(` ```language ... ``` `), not as separate raw source files. `implementation/runtime/memory/chunker.py`
walks the body once, tracking the current Markdown heading stack, and dispatches:

- **Fenced code blocks with an installed tree-sitter grammar** (`python`, `javascript`/`js`/
  `typescript`, `bash`/`sh` — see `chunk_code.py`'s `_SUPPORTED_LANGUAGES`): parsed via
  `tree-sitter`; one chunk per top-level `function_definition`/`class_definition` (etc.), plus one
  chunk per method nested inside a class (`parents=(class_name,)`). `imports` are the block's
  top-level `import`/`from ... import` statements, attached to every chunk from that block.
  `ast_type` is the tree-sitter node type verbatim (e.g. `function_definition`) — not a repo-defined
  taxonomy, so it stays accurate as grammars evolve.
- **Fenced code blocks with no installed grammar**: indexed as one whole-block chunk,
  `ast_type=None`, `symbol=None` — a documented fallback (`chunk_unsupported_code`), not a silent
  mis-attribution to some AST node type the block was never actually parsed into.
- **Everything else (prose between headings/fences)**: one chunk per contiguous run of text,
  section-aware — `symbol` = the nearest enclosing Markdown heading text, `parents` = the ancestor
  heading path (same "own name / enclosing scope chain" shape as the code path's `symbol`/
  `parents`, by design, for a consistent mental model across content types).

### 3.1 Fields with no prose equivalent (acceptance criterion 1)

Prose chunks always carry `ast_type=None` and `imports=()`. This is a documented absence, not a
gap: prose has no abstract syntax tree to name a node type from, and no import-statement concept.
`symbol`/`parents`/`line_range`/`path`/`commit` all have direct section-aware equivalents (heading
text, heading path, body-relative line span, and the two provenance fields respectively) and are
populated identically in shape to the code path.

## 4. Embedding model and runtime

**Library: `fastembed`** (Apache-2.0, ONNX Runtime CPU backend), not `sentence-transformers`.
Both wrap the same two ADR-005-named candidate models
(`nomic-ai/nomic-embed-text-v1.5` primary, `BAAI/bge-small-en-v1.5` fallback — both are
`fastembed`-supported model names verbatim), but `fastembed` avoids pulling in `torch` (a
multi-hundred-MB dependency this pipeline has no other use for), installs from prebuilt wheels
with no C/C++ toolchain requirement, and its default model is literally `BAAI/bge-small-en-v1.5` —
i.e. this is a well-trodden path for exactly ADR-005's fallback candidate, not an obscure
integration. Confirmed working in this task's own sandbox: `pip install fastembed` succeeds cleanly
into a plain venv, and both `nomic-ai/nomic-embed-text-v1.5` and `BAAI/bge-small-en-v1.5` are in
`TextEmbedding.list_supported_models()`.

**Selected model: `nomic-ai/nomic-embed-text-v1.5`** (ADR-005's primary candidate) —
`implementation/runtime/memory/embed.py`'s `PRIMARY_MODEL` default; `--embedding-model` overrides
per-build for T455's later empirical A/B against `bge-small-en-v1.5` (`FALLBACK_MODEL`).

**Runtime management:** the model weights are fetched once (via `huggingface_hub`, `fastembed`'s
own dependency) into a local cache directory (`EMAGE_MEMORY_MODEL_CACHE` env var, default
`~/.cache/emage-memory-embeddings/`) on first use, then loaded from that cache on every subsequent
run — no re-download, no network call, once warm. Vectors are L2-normalized to unit length by
`embed.py` after `fastembed` returns them (`fastembed` itself does not guarantee pre-normalized
output for every model), so T453 can use plain dot product as cosine similarity.

**No-cost / no-network confirmation (ADR-005's own Validation checklist item, and acceptance
criterion 6):** demonstrated directly, not merely asserted — reproduced end-to-end via the real CLI
(not just the pytest suite) in this task's completion report, using: model cache already warm,
`HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1`, and `HTTP_PROXY`/`HTTPS_PROXY` (both cases) pointed
at `http://127.0.0.1:1` (nothing listens there — any attempted network call fails immediately
rather than hanging or silently succeeding via a real connection) — the pipeline still builds a
real index with real, non-stub 768-dimensional unit vectors. See
`tests/functional/test_memory_indexing_pipeline.py::FullPipelineTests::test_embedding_runs_with_no_network_egress_or_credential`
for the same proof as an automated, repeatable test (gated behind
`EMAGE_MEMORY_FULL_PIPELINE_TEST=1` so `python3 tests/run.py`'s default run doesn't require the
optional dependency or a warm model cache).

## 5. Rebuild-determinism property

**Property that holds: functionally-equivalent, not byte-identical.** Every non-vector field
(text, all enrichment/scope metadata, rejection records, manifest) is byte-identical across two
builds of the same vault content for the same project identity — confirmed by direct JSON-field
comparison in `index_writer.diff_index_dirs`. Vector fields are compared with a tolerance
(`VECTOR_TOLERANCE = 1e-6` max absolute per-component delta), not asserted bit-identical, because
ONNX Runtime's CPU multi-threaded reduction order is not documented as bit-stable across process
runs. **Measured in this task's own environment: two consecutive builds of the same fixture vault
produced zero diffs at all**, including in the vector fields (i.e. the observed delta was smaller
than even a much tighter tolerance would have required) — but the tolerance-based comparison is
kept as the documented contract rather than a stricter byte-identity assertion, since bit-exact
reproducibility across ONNX Runtime versions/thread counts/hardware is not a guarantee this
pipeline's own dependency (`onnxruntime`) makes.

**How it's checked**, mirroring this repo's `sync.mjs --check`/`generate-registry.py --check`
precedent: `python3 -m implementation.runtime.memory.build --check-against <existing_index_dir>
<... same --project-id/--own-repo-root/--general-repo-root/--shared-source-root as the original
build ...>` rebuilds into a fresh temp directory and diffs it against `<existing_index_dir>`,
printing every diff (if any) and exiting non-zero if the rebuild drifted. See this task's
completion report for the exact commands and real output.

## 6. Scope enforcement — what T452 guarantees, what T453 still needs to do

T452 implements memory-scope-model-v1.md §4.1 (the primary, structural control) in
`implementation/runtime/memory/scanner.py`: building project `P`'s index only ever reads three
kinds of directory — `P`'s own repo's `.../memory/project/` subtree, the single harness repo's
`.../memory/general/` subtree, and (only for repos explicitly passed via `--shared-source-root`)
that repo's `.../memory/shared/` subtree — never any other directory, for any reason, under any
configuration. See `scanner.py`'s own module docstring and
`tests/functional/test_memory_indexing_pipeline.py::StructuralScanTests` for the adversarial proof
(a file-open audit hook confirming a foreign repo's tree is never even opened, not merely filtered
out of the final index).

T452 also persists every chunk's `scope`/`project_id`/`shared_consumers` (§2.1 above) so T453 can
implement §4.2's defense-in-depth query-time filter — **T452 does not build that filter itself**;
this is explicitly T453's job (memory-scope-model-v1.md §10, point 4: "persist... for T453's
query-time filter... to consume").

## 7. Vault directory convention

`implementation/knowledge/memory/{general,project,shared}/` — see
`implementation/knowledge/memory/README.md` for the full convention and a minimal worked example.
No real content is populated in this task (see `docs/tasks/task-T452.md`,
"Vault content — explicitly out of scope"); test fixtures proving the pipeline's own contract live
under `tests/fixtures/memory/` (see that directory's own `README.md`).

## 8. Known limitations / follow-ups for T453+

- Only `python`, `javascript`/`typescript`, and `bash` have installed tree-sitter grammars in this
  task's `requirements.txt`. Additional languages are a matter of adding another
  `pip install tree-sitter-<lang>` entry and a `_SUPPORTED_LANGUAGES` row in `chunk_code.py` — no
  design change needed.
- `--shared-source-root` currently expects a local filesystem path (e.g. an already-cloned sibling
  repo checkout). memory-scope-model-v1.md §4.1 describes this as "a pinned-ref `git fetch`/shallow
  clone... performed by T452 at build time" for the general case of a repo not already checked out
  locally — that fetch/clone step itself is not implemented here (out of this task's own scope: the
  brief names the *scan* mechanism as the required contract, not a specific transport for acquiring
  a remote repo's working tree). A caller (or a thin wrapper script) is expected to ensure the
  passed-in root is a valid, read-only local checkout before invoking `build.py`.
- T455's empirical `nomic-embed-text-v1.5` vs. `bge-small-en-v1.5` comparison is unblocked by this
  pipeline's `--embedding-model` flag but not performed here (explicitly deferred to T455 by
  ADR-005).
