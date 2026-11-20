# Knowledge-vault indexing pipeline (T452) + hybrid retrieval (T453)

Turns the knowledge vault (`implementation/knowledge/memory/{general,project,shared}/`,
git-versioned Markdown + YAML frontmatter, per ADR-005 Decision 1) into a
derived, rebuildable, scope-enforced vector index (T452), then queries that
index with a fused semantic+lexical+structural ranking, behind a mandatory
query-time scope filter (T453).

**Full design docs:** `docs/artifacts/indexing-pipeline-v1.md` (T452 — on-disk
index format, chunk metadata schema, chunking approach, embedding model/
runtime, rebuild-determinism property); `docs/artifacts/hybrid-retrieval-v1.md`
(T453 — fusion strategy, query-time scope filter, latency benchmark).

**Contracts implemented:** `docs/artifacts/memory-scope-model-v1.md` §10
("Handoff to T452") and §4.2 ("mandatory query-time filter", implemented by
T453's `scope_filter.py`).

## Modules

| Module | Stage | Optional deps |
|--------|-------|----------------|
| `schema.py` | shared data types (T452) | none (stdlib) |
| `validate.py` | §5 write-time scope validation (T452) | PyYAML |
| `scanner.py` | §4.1 structural repo-boundary scanning (T452) | none (stdlib + `git`) |
| `chunk_code.py` | tree-sitter code-block chunking (T452) | `tree-sitter`, grammar packages |
| `chunker.py` | body dispatcher, code fences vs. section-aware prose (T452) | (delegates to `chunk_code.py`) |
| `enrich.py` | attach plan-035 + §4.2 metadata to chunks (T452) | none |
| `embed.py` | local embedding, ADR-005 Decision 2 (T452 build; reused by T453 at query time) | `fastembed` |
| `index_writer.py` | deterministic on-disk writer + rebuild diff (T452) | none |
| `build.py` | CLI orchestrator, wires T452's stages together | (all of the above) |
| `scope_filter.py` | §4.2 mandatory query-time scope pre-filter (T453) | none (stdlib) |
| `lexical.py` | BM25 lexical signal over text/symbol/tags (T453) | none (stdlib) |
| `structural.py` | enrichment-metadata boost signal (T453) | none (stdlib) |
| `rank.py` | weighted fusion of the three signals (T453) | none (stdlib) |
| `retrieve.py` | `MemoryIndex`/`Retriever` — T453's query API, integration surface for T454 | `fastembed` (via `embed.py`) |

Only `embed.py`, `chunk_code.py`, `build.py`, and `retrieve.py`
(transitively, via `embed.py`) need the optional deps in `requirements.txt`.
Everything else is stdlib + PyYAML, consistent with this repo's existing
dependency-light convention — `scope_filter.py`, `lexical.py`, `structural.py`,
and `rank.py` are all fully unit-testable with no optional dependency
installed.

## CLI usage

```bash
python3 -m implementation.runtime.memory.build \
    --project-id em-age/emage.code \
    --own-repo-root . \
    --general-repo-root . \
    --shared-source-root ../sia \
    --output-dir implementation/runtime/memory/_index/em-age-emage.code
```

`--project-id` is always explicit — never inferred from vault content
(memory-scope-model-v1.md §4.1). It must be the id the server derives from
the workspace's git remote `origin`: lower case, `<org>/<repo>` (for a nested
group, the last two path parts). The build refuses any other spelling with a
non-zero exit and writes nothing (T790, QA-T760-02): the query-time filter
compares exactly, so an index built under `Acme/Widget` answered nothing. It
also derives that id from the `origin` remote of `--own-repo-root`, with the
server's own normalisation, and refuses a `--project-id` that is not exactly
that id (a well-formed `acme/other` beside a remote `Acme/Widget`), or any
`--project-id` when `--own-repo-root` has no usable `origin`: the server does
not start without one (T828, QA-T818-03). The refusal names the derived id,
never the remote's credentials. The
`project_id` in a project-scope entry's frontmatter must be that same string.
An entry whose `project_id` is any other string is still indexed under its own
spelling and is never returned, and the build names its path (never its
content) in a warning on stderr: one wording when the difference is only
letter case, another for any other difference (a typo, `org/repo.git`, the
top group of a nested path; T795, SEC-T791-02). A remote whose `<org>` or
`<repo>` is `.` or `..` gives no project id: the server does not start, and
`--project-id` refuses such an id (T795, SEC-T791-03). Run the build in the
virtual environment that holds `requirements.txt` (for example prefix it with
`source .venv-mcp/bin/activate &&`, as the installer's note prints it).
`--shared-source-root` may be repeated zero
or more times, once per foreign repo this build should also scan for
`shared`-scope candidates (only that repo's `shared/` subtree is ever read —
see `scanner.py`'s module docstring for the structural guarantee this gives).

Write the index to `implementation/runtime/memory/_index/<org>-<repo>`, the
`--project-id` with `/` replaced by `-` (lower case). The `context-retriever`
MCP server entry in `servers.yaml` passes no `--index-dir` (T722,
TD-T671-K5): the server derives this directory from the workspace's own git
remote, so each project reads its own index. Pass `--index-dir` to the server
to use another location.

## Query API (T453)

```python
from implementation.runtime.memory.retrieve import MemoryIndex, Retriever
from implementation.runtime.memory.scope_filter import RequestingContext

index = MemoryIndex.load(Path("implementation/runtime/memory/_index/em-age-emage.code"))
retriever = Retriever(index)  # loads the LocalEmbedder once (embed.py)

context = RequestingContext(project_id="em-age/emage.code", platform="claude-code")
results = retriever.search("load_config helper", context, top_k=10)
for r in results:
    print(r.score, r.chunk["path"], r.chunk["symbol"])
```

`RequestingContext` is a required, non-defaultable argument to every
`Retriever.search` call — see `scope_filter.py` and
`docs/artifacts/hybrid-retrieval-v1.md` for the mandatory query-time scope
filter this enforces before any ranking runs.

## Vault content

Populating a real production knowledge corpus is explicitly out of scope for
T452 — see the task brief. `implementation/knowledge/memory/{general,project,shared}/`
currently contain only a `README.md` documenting the convention (no real
entries). Test fixtures proving the pipeline's own contract live under
`tests/fixtures/memory/`.
