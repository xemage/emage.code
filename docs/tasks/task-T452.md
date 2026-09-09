# Task T452 — Indexing pipeline over the knowledge vault (parse → chunk → enrich → embed → index)

**ID:** T452
**Owner:** backend-developer
**Status:** done
**Priority:** P0
**Depends on:** T450 (done — `docs/decisions/ADR-005-memory-layer-design.md`, status `Accepted`), T451 (done — `docs/artifacts/memory-scope-model-v1.md`)
**Created:** 2026-09-09
**Completed:** 2026-09-09
**Based on:** `docs/plans/plan-035-roadmap-v7-ground-up.md` §2.4 Phase 5 (T452 row: "Indexing
pipeline over the vault: parse → chunk → enrich (path, symbol, language, AST type, parents,
imports, line range, commit) → index", acceptance criteria list, Gate G3); `docs/plans/plan-038-
phase5-detailed-planning.md` (approved, MR !228, merged `develop`) — T452 per-task summary,
task-graph dependency reasoning, and its 75k token budget; `docs/decisions/ADR-005-memory-layer-
design.md` (accepted 2026-09-09) — Decision 1 (storage substrate), Decision 2 (embeddings
provider), Decision 3 (read-only-by-default) and its "Validation"/"Follow-ups" sections naming
T452 directly; `docs/artifacts/memory-scope-model-v1.md` (T451, accepted design) — §10 "Handoff
to T452" is this task's primary functional contract.

This brief is self-contained. Read `docs/checkpoints/checkpoint-023-phase5-adr005-accepted-t451-
complete.md` for the immediate prior-session context (why T452 was paused rather than dispatched
last session) — you do not need the full Phase 5 execution history beyond that checkpoint plus
the three input documents above.

## Objective

Build the indexing pipeline that turns the knowledge vault (a git-versioned, per-project
Markdown/frontmatter knowledge tree, per ADR-005 Decision 1) into a derived, rebuildable, scope-
enforced vector index. Concretely: parse every candidate entry's frontmatter and body, apply
`memory-scope-model-v1.md` §5's write-time validation (reject malformed/missing `scope`,
`project_id`, `shared_consumers` — never default), chunk the body (tree-sitter for code,
section-aware chunking for prose, per ADR-005 Decision 1), enrich each chunk with the metadata
`plan-035` names (path, symbol, language, AST type, parents, imports, line range, commit) plus the
scope metadata `memory-scope-model-v1.md` §4.2 requires (`scope`, `project_id` if `project`-scope,
`shared_consumers` if `shared`-scope), embed each chunk using a local embedding model (ADR-005
Decision 2 — no paid API, no network egress to any embeddings provider), and write the result to
a derived, on-disk, rebuildable vector index that a fresh build from a clean checkout reproduces
functionally-equivalently.

This is `plan-038`'s own first `large`-scope, real-implementation task in Phase 5 (its words:
"real design uncertainty") — genuine implementation choices (index storage format, chunking
library integration, local embedding-model runtime management) are yours to make and document;
the storage substrate, scope-enforcement mechanism, and embeddings-provider decisions are already
made for you by T450/T451 and must not be re-derived or second-guessed.

## Context

Phase 5 (Persistent Memory/RAG, T450-T456) is approved (`plan-038`, MR !228). T450 produced
ADR-005 (accepted 2026-09-09, all three decisions approved by the user). T451 produced the scope
model (`memory-scope-model-v1.md`, merged via MR !235). Both of T452's dependencies are done. Per
`checkpoint-023`, T452 was deliberately left undispatched last session pending the user's return
— that return, and explicit dispatch approval, has now occurred; this brief is that dispatch.

No vault content currently exists on `develop` (`implementation/knowledge/memory/` does not exist
yet — confirmed directly). You are not being asked to populate a real production corpus in this
task; see "Vault content — explicitly out of scope" below.

## Inputs

- `docs/decisions/ADR-005-memory-layer-design.md` — Decision 1 (storage substrate: Markdown +
  YAML frontmatter, tree-sitter for code / section-aware chunking for prose, canonical writes only
  via reviewed git MRs, derived index is rebuildable); Decision 2 (embeddings: local model,
  `nomic-embed-text-v1.5` primary / `bge-small-en-v1.5` fallback, zero cost, no paid API, no
  network egress required to function); Decision 3 (read-only-by-default; the index's only write
  path is this task's own explicit, auditable rebuild step — never a live per-query call);
  "Validation" section's "No-cost confirmation" item (must be directly checkable: the pipeline
  runs correctly with no embeddings-provider API key or network egress configured).
- `docs/artifacts/memory-scope-model-v1.md` — §3 (frontmatter schema: `scope`, `project_id`,
  `origin_project_id`, `shared_consumers.{projects,platforms}`); §4.1 (the primary control —
  repo-boundary partitioning at index-build time; the `include(entry, P)` predicate; the
  **structural, not filtered** guarantee that a `project`-scoped entry from a different repo is
  never parsed/chunked/embedded, full stop); §4.2 (the metadata every chunk must carry, for T453's
  later query-time filter — not your job to build the filter, only to persist the metadata); §5
  (write-time-only validation — reject-not-default on any malformed/missing scope field, with an
  auditable rejection log: source path, commit SHA, reason); §8 (five proposed verification
  checks — the first two and the "cross-project unreachability probe" are this task's own
  acceptance tests, see below); §10 ("Handoff to T452" — the literal 5-point contract this task
  must satisfy at minimum).
- `plan-035-roadmap-v7-ground-up.md` §2.4 Phase 5 — T452's enrichment field list (path, symbol,
  language, AST type, parents, imports, line range, commit) and the Phase 5 acceptance criterion
  "A `project`-scoped entry is provably unreachable from a different project's session."
- `plan-038-phase5-detailed-planning.md` — T452's per-task summary (objective/inputs/outputs/
  acceptance criteria, 75k token budget, "Cost note" — not applicable here since Decision 2
  resolved the cost gate negative).
- Prior-repo precedent for "rebuildable, deterministic regeneration from a clean checkout": `node
  implementation/scripts/sync.mjs --check` and `implementation/scripts/generate-registry.py
  --check` — both already zero-drift-checkable in this repo; your index rebuild should be
  checkable the same way (a `--check`-style mode, or an equivalent before/after content-hash
  comparison you document).

## Vault content — explicitly out of scope

Populating a real production knowledge corpus under `implementation/knowledge/memory/` is **not**
this task's job — that is future content-authoring work, not indexing-pipeline engineering, and
conflating the two would make this task's scope open-ended. What you must build instead:

1. The pipeline itself, operating against whatever vault tree it is pointed at.
2. A documented vault directory convention (where `general`/`project`/`shared` entries live,
   consistent with `memory-scope-model-v1.md` §2's example paths, e.g.
   `implementation/knowledge/memory/{general,project,shared}/`).
3. A small **test fixture vault** (synthetic entries, clearly marked as test fixtures, not real
   knowledge-base content) sufficient to prove the pipeline's own contract: at minimum, one valid
   entry per scope, one entry per §5 rejection case (missing `scope`, missing `project_id` on a
   `project`-scope entry, incomplete `shared_consumers`), and the two-fixture-repo pair
   `memory-scope-model-v1.md` §8 names for the cross-project unreachability probe (see Acceptance
   Criteria). This mirrors this repo's own `tests/golden/_example-scaffold/` precedent (T410) —
   a worked, minimal example that mechanically proves a contract, not a production dataset.
4. Optionally, a handful of real `general`-scope entries about emage.code itself if useful as a
   smoke test — but this is not required for acceptance, and must not be treated as a stand-in for
   real fixture-based testing.

## Constraints

- **Token budget:** 75k (`plan-038`'s own `large`-scope estimate for this task). If you find
  yourself genuinely exceeding this mid-work, that is a checkpoint-worthy event per this repo's
  Token Governance rules (report back, don't silently absorb the overrun).
- **No paid or recurring-cost API calls of any kind.** ADR-005 Decision 2 is a hard constraint,
  not a preference: the embedding model must run locally (CPU is sufficient per ADR-005's own
  hardware reasoning; GPU only if trivially available, never required). If, during implementation,
  you find any part of this design genuinely requires a paid API call (contrary to ADR-005), **stop
  and report a blocker** (`type: technical`, appropriate severity) rather than proceeding — do not
  substitute a paid provider under any circumstance, and do not silently stub/mock the embedding
  step to avoid the question. The embedding step must actually run and produce real vector output
  in your own worktree before you report completion.
- **File ownership:** you may create the indexing pipeline implementation (path of your own
  choosing, but document it — a plausible location is `implementation/memory/` or
  `implementation/scripts/memory/`, consistent with this repo's existing `implementation/scripts/`
  convention), the vault directory convention and its test fixtures, and a short design-note
  artifact (`docs/artifacts/indexing-pipeline-v1.md`, or equivalent name — state explicitly in your
  completion report if different) documenting the on-disk index format for T453 to consume, the
  chunking/enrichment approach, and the local embedding-model runtime choice actually made.
- **Do not touch:** `.mcp.json` anywhere, for any reason. `tests/golden/**`, `scripts/scorecard.py`,
  `docs/benchmarks/tb-subset.json`/`.md` (frozen, unrelated to this task). `ADR-005-memory-layer-
  design.md` and `memory-scope-model-v1.md` themselves (consume, do not revise — if you find either
  genuinely underspecified for something you need to implement, that is a `type:
  unclear_requirements` blocker to report with a proposed resolution, not a license to silently
  edit the prior artifacts). `feature/T475-codex-platform-integration` (out of scope, unrelated
  branch). Do not start any Phase 3 work.
- **Work in your own worktree/branch:** `agent/backend-developer/T452`, created from `develop`.
  Commit as you go; run the full test suite (`python3 tests/run.py`) and confirm no regressions
  before reporting completion. **Do not self-merge** — push and open a merge request, then stop;
  the orchestrator independently verifies and merges.
- Follow this repo's coding standards (max 50-line functions, max 4 parameters, early returns) and
  Conventional Commits.

## Expected Outputs

1. Indexing pipeline implementation (parser, chunker, enricher, local-embedding step, index
   writer), with a documented CLI/entry point that accepts an explicit "building for project `P`"
   identity per `memory-scope-model-v1.md` §4.1 (never inferred from vault content) and a vault
   root to index.
2. A documented vault directory convention under `implementation/knowledge/memory/` (structure
   only — see "Vault content" above for what is and isn't populated).
3. Test fixtures proving the pipeline's own contract (§5 rejection cases; the cross-project
   unreachability + shared-scope reachability probe pair from `memory-scope-model-v1.md` §8),
   wired into `tests/` following this repo's existing test conventions (`tests/run.py`).
4. `docs/artifacts/indexing-pipeline-v1.md` (or equivalent, name stated in completion report):
   on-disk index format, chunk metadata schema (including the scope fields T453 will filter on),
   chunking approach per content type, embedding model actually wired up and how its runtime is
   managed (e.g. `sentence-transformers`/Ollama, version pinned), and the rebuild-determinism
   property and how it's checked.
5. Rejection log format/output (per §5 — auditable, not silent) for entries that fail write-time
   validation.

## Acceptance Criteria

1. **Enrichment fields present and correct**, per `plan-035`'s list: path, symbol, language, AST
   type, parents, imports, line range, commit — for at least the code-chunking path (tree-sitter).
   Prose chunking enrichment fields should be the section-aware equivalent (e.g. path, heading
   path/parents, line range, commit) — document any field that has no prose equivalent and why.
2. **Scope tagged at write time per T451, not inferred**: every entry is validated against
   `memory-scope-model-v1.md` §5 before being eligible for chunking at all. A synthetic entry with
   missing/malformed `scope:` is rejected (absent from the resulting index, present in the
   rejection log) — not defaulted to any scope. A `scope: shared` entry with an incomplete
   `shared_consumers` block (missing `platforms`, or an empty `projects` list) is rejected on the
   same terms.
3. **`project`-scope unreachability is structural, not filtered**: building project `P2`'s index
   against a fixture repo never parses, chunks, or embeds a `project`-scoped entry that lives in a
   separate fixture repo `P1` — confirm this by inspecting the pipeline's own file-scan behavior
   (it must never read `P1`'s tree while building for `P2`), not merely by checking the final
   index's contents (a filter-after-the-fact would satisfy a weaker, wrong test).
4. **`shared`-scope reachability works via the identical mechanism**: a `shared`-scoped synthetic
   entry naming `P2` in `shared_consumers.projects` does appear in `P2`'s index when P2's build is
   configured to also scan the origin repo for shared candidates, proving the same
   `include(entry, P)` logic correctly produces both the negative and positive outcome.
5. **Index is rebuildable**: a fresh build from a clean checkout of the same vault content and the
   same target project identity reproduces the same index content (byte-for-byte or
   functionally-equivalent — e.g. same chunks/metadata/vectors within embedding-model numerical
   tolerance; document which property holds and why if not byte-identical, e.g. non-determinism in
   a specific embedding backend). This must be demonstrated, not asserted — include the exact
   commands used to prove it in your completion report.
6. **No embeddings-provider credential or network egress required**: the pipeline runs correctly
   end-to-end (including the embedding step producing real, non-stubbed vector output) with no
   API key configured and no network call to any embeddings provider — demonstrate this directly
   (e.g. run with network access to any embedding API host blocked/absent and confirm it still
   works), not just by asserting the code path doesn't call one.
7. **Feeds T453**: the index format and chunk metadata schema are documented clearly enough that
   T453 (hybrid retrieval, not your task) could query it without re-deriving your design.
8. `python3 tests/run.py` passes with no regressions from your branch's baseline; new tests you add
   are included in that run, not a separate ad hoc script.
9. Coding standards and Conventional Commits followed; branch pushed, MR opened against `develop`,
   not self-merged.

## Blocker Protocol

Report any blocker with `type` (`technical` | `dependency` | `unclear_requirements` | `external`)
and `severity` (`critical` | `major` | `minor`) per `AGENTS.md`'s Blocker Protocol. Max 2 retries
before escalating to the orchestrator. Specific cases already anticipated:

- If anything in this design genuinely requires a paid/recurring-cost API call to satisfy an
  acceptance criterion (contrary to ADR-005 Decision 2): **stop immediately** and report
  `type: technical`, `severity: critical` — this is a hard stop per this brief's Constraints, not
  a judgment call to resolve on your own.
- If `ADR-005` or `memory-scope-model-v1.md` is genuinely underspecified for something you need to
  implement (e.g. the exact on-disk index format, the exact chunking library): that is expected —
  both documents explicitly leave these choices to you. Make and document the choice; this is not
  a blocker. Only escalate if the *scope-enforcement* or *cost* decisions themselves (not
  implementation details) seem contradictory or infeasible as written.
- If local embedding model installation/runtime (`nomic-embed-text-v1.5` via `sentence-
  transformers`/Ollama, or the `bge-small-en-v1.5` fallback) is not feasible in your worktree's
  actual environment: report `type: technical`, appropriate severity, with what was tried,
  mirroring this repo's existing precedent for environment-constrained blockers (e.g. T481's Codex
  runtime-host gap). Do not stub the embedding step to work around this and report success.

## Execution notes

## Completion addendum (2026-09-09)

`implementation/runtime/memory/` (pipeline: `scanner.py`, `validate.py`, `chunker.py`/
`chunk_code.py`, `enrich.py`, `embed.py`, `index_writer.py`, `build.py` CLI), the
`implementation/knowledge/memory/{general,project,shared}/` vault directory convention (structure
only, no content — as scoped), `tests/fixtures/memory/` (synthetic two-repo fixture pair plus all
§5 rejection cases), 20 new tests wired into `tests/run.py`, and
`docs/artifacts/indexing-pipeline-v1.md` published (MR !239, squash-merged `develop`, commit
`e65578b`). Disclosed deviation: pipeline code lives at `implementation/runtime/memory/` rather
than either location this brief suggested — matches this repo's existing
`implementation/runtime/{handoff,cwso,telemetry,triggers}/` convention for runtime subsystems.
Independently confirmed real (not asserted): `implementation/runtime/` already contains exactly
those four sibling directories on `develop`.

**Orchestrator independent verification performed before merging — real adversarial re-testing,
not re-reading the agent's report:**

- Confirmed MR !239 and branch `agent/backend-developer/T452` genuinely exist against live GitLab/
  git state before trusting any claim about them (a "coordinator" message mid-session asserted
  completion; per this project's own standing rule and `checkpoint-023`'s precedent, no agent
  message is ever treated as the user's authorization or as fact — everything below was
  independently re-derived, not accepted from that message).
- `python3 tests/run.py` run fresh in the merged worktree: 399 tests, `OK`, `skipped=21` (up from
  the 379/17 pre-T452 baseline — exactly the +20 new tests, 4 gracefully skipping without optional
  deps).
- Installed the optional deps (`fastembed`, `tree-sitter` + grammars) into a fresh venv myself and
  ran the full opt-in pipeline suite directly (`EMAGE_MEMORY_FULL_PIPELINE_TEST=1`): 20/20 pass,
  including a real first-time model download from Hugging Face Hub (`nomic-ai/nomic-embed-text-v1.5`,
  observed directly) — the embedding step is real, not stubbed.
- Ran the CLI directly against the fixtures myself (not the agent's transcript): `python3 -m
  implementation.runtime.memory.build --project-id fixture-org/repo-p2 ...` → "wrote 6 chunks, 2
  rejections", matching the reported figures exactly; `--check-against` on the same output → "no
  drift within vector tolerance".
- **Stronger, independent rebuildability check than the agent's own same-worktree test:** cloned the
  repo fresh into a new directory, checked out the real merged branch, built a second, entirely
  separate venv, and ran the same CLI build there. Diffed the two builds (fresh-clone vs.
  original-worktree) with the pipeline's own `diff_index_dirs` — zero diffs — and cross-checked with
  a raw file-listing diff — also zero. This is a genuine clean-checkout rebuild, not a rebuild inside
  the same already-built environment.
- **Adversarial test not present in the agent's own suite, designed and run independently:** a
  symlink-escape probe — placed a symlink inside a copied "evil" P2 fixture's own `project/`
  directory pointing at P1's `project/` directory (attempting to make P1's `project`-scope content
  reachable "from within P2's own tree," a case `memory-scope-model-v1.md` §9's literal predicate
  wording does not explicitly rule out). Built the index for the evil P2 config: output was
  identical to the non-symlinked case (still exactly 6 chunks/2 rejections) and P1's literal canary
  token (`FIXTURE-CANARY-P1-ONLY-CONTENT-4172`) never appeared — `Path.rglob` does not traverse
  symlinked directories by default in this Python version, so the escape attempt failed. Confirmed
  this holds; not merely assumed from reading the scanner code.
- Independently re-ran the shared-scope reachability case (acceptance criterion 4) via the CLI
  directly, not just the unit test: built P2's index with `--shared-source-root
  tests/fixtures/memory/repo-p1` — the shared canary (`FIXTURE-CANARY-SHARED-P1-TO-P2-8891`)
  appears, while the P1-only project-scope canary still does not, even with P1 configured as a
  shared source.
- Inspected real output content directly (not the design doc's description of it): chunk records
  carry `scope`/`project_id`/`shared_consumers`/`commit`/`path`/`symbol`/`language`/`ast_type`/
  `parents`/`imports`/`line_range` as claimed; the rejection log carries `source_path`/`repo_id`/
  `commit`/`reason`/`scope_attempted`, auditable per §5.
- Confirmed no `__pycache__` or local venv artifacts were committed (`git ls-files` clean); CI green
  (5/5) on the real branch before merging, checked directly via `glab ci status`, not assumed from
  the earlier message.

**All 9 acceptance criteria independently confirmed met**, including the three flagged in the
brief as requiring adversarial (not self-reported) verification: criterion 3 (structural
unreachability — confirmed via both the agent's audit-hook test and this review's own symlink-escape
probe), criterion 5 (rebuildability — confirmed via a genuinely independent clean-clone rebuild, not
just the agent's own same-worktree rebuild), and criterion 6 (no embeddings-provider credential/
network egress — confirmed via a real offline run producing real normalized 768-dim vectors).

T452 is `done`. T453 (hybrid retrieval) is next in `plan-038`'s dependency graph — not dispatched
this session; see `active-tasks.md`.
