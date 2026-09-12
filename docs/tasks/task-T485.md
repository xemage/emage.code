# Task T485 — Build the first-ever real memory index against this repo's own vault

**ID:** T485
**Owner (executed directly):** orchestrator — per this session's user decision, mirroring T484's
"agent decides, orchestrator executes" precedent for a small, bounded, investigative
prerequisite task. `devops-engineer` (T452's original implementer) is not reassigned or blocked
by this — this task does not touch `implementation/runtime/memory/`'s pipeline *code*, only runs
it and records the result.
**Status:** done
**Priority:** P1
**Depends on:** None (reuses only already-`done` artifacts: T452's pipeline, T453/T454's
`ContextRetriever`/CLI)
**Blocks:** Nothing structurally. **Does not close or advance T458 or T456.** Distinct from T458
itself — this is prerequisite infrastructure (build the index at least once), not the live-harness
scaling task.
**Created:** 2026-09-12
**Completed:** 2026-09-12
**Based on:** `docs/tasks/task-T484.md` (merged `origin/develop` at `602ad12`, MR !289 — the
walking-skeleton trial whose treatment-arm finding is this task's entire premise: "no memory index
has ever been built anywhere in this repo"); `docs/artifacts/indexing-pipeline-v1.md` (T452's own
build-pipeline design — on-disk format, CLI shape, embedding runtime, rebuild-determinism); the
real, current `implementation/runtime/memory/build.py` and `context_retriever.py` source (read
fresh this task, not from any prior summary); `docs/artifacts/memory-scope-model-v1.md` (T451 —
the `general`/`project`/`shared` scope model governing what the index should cover);
`implementation/knowledge/memory/{general,project,shared}/` (the T452-established vault
directories); `docs/decisions/ADR-005-memory-layer-design.md` (Decision 1 — git-versioned
canonical store + a **separately-built, read-only, rebuildable, non-canonical** vector index;
Decision 2 — `nomic-embed-text-v1.5` via `fastembed`, confirmed local/zero-cost);
`docs/artifacts/retrieval-eval-v1.md` §5 (T455's own precedent for the identical
fastembed-not-installed situation: throwaway-venv install of the already-repo-pinned
`fastembed==0.8.0`, explicitly framed as "no new dependency was added to the repo").

## Objective

Build a real index for the first time against this repo's actual, current knowledge-vault content
by running T452's real, unmodified build pipeline exactly as it exists on `origin/develop` — no
invented process — then independently prove the index works by re-running T484's exact corrected
`@context-retriever` CLI invocation against it and confirming the previously-reported
`FileNotFoundError` is gone. This is scoped strictly to "build the index and prove it works," not
to scaling T458 or re-running T484's walking-skeleton trial.

## Constraints

- Never touch `feature/T475-codex-platform-integration`.
- Never edit `tests/golden/**`, `scripts/scorecard.py`, or `docs/benchmarks/tb-subset.json`/`.md`.
- No new paid/metered API usage.
- Do not silently `pip install` a new dependency, and do not silently fall back to a different
  embedder if `fastembed` is unavailable — report precisely instead. (Resolved: `fastembed` is
  already a repo-declared, pinned optional dependency in
  `implementation/runtime/memory/requirements.txt`, committed on `origin/develop`; installing it
  into a throwaway venv to run already-committed, already-reviewed pipeline code is not a "new
  dependency" decision — this is the exact precedent T455 already established and used for the
  identical situation. No repo dependency manifest is modified by this task.)
- T456, T457, T458, T483 remain untouched.
- Do not pad out the vault with filler content to make the index look non-trivial if it is
  genuinely empty — report the true state.

## What was found (read fresh this session, not from any prior summary)

1. **`origin/develop` HEAD independently re-verified:** `602ad120692f2d5ed12252211d0944b36d4203d1`
   (`git rev-parse origin/develop` after `git fetch`), matching the prompt's stated `602ad12`.
   Ledger confirmed fresh: `active-tasks.md` holds T456/T457/T458/T483 as its only non-terminal
   rows (all `pending`/`blocked`, none touched here); T484's closure note present and matches
   `task-T484.md` verbatim.
2. **`fastembed` is genuinely not importable in this task's own default shell**
   (`python3 -c "import fastembed"` → `ModuleNotFoundError`, confirmed directly, matching T484's
   and T455's own finding in their respective environments). `LocalEmbedder.__init__`
   (`embed.py`) hard-imports `from fastembed import TextEmbedding` with no alternate-embedder
   parameter or fallback path anywhere in `build.py`/`embed.py`/`context_retriever.py` — there is
   no supported way to build a real index without it. Resolved per Constraints above: installed
   `fastembed==0.8.0` (the exact pin in `implementation/runtime/memory/requirements.txt`) into a
   throwaway venv outside the repo (`python3 -m venv` + `pip install -r
   implementation/runtime/memory/requirements.txt`), exactly reproducing T455's own documented
   resolution of the identical blocker. Confirmed importable afterward.
3. **The vault is genuinely, structurally empty today.** `implementation/knowledge/memory/`
   contains only `README.md` (top-level, not scanned — `scanner.py`'s `_scan_subdir` only
   `rglob("*.md")`s the named `project/`/`general/`/`shared/` subdirectories) and three
   `.gitkeep` placeholders (`project/.gitkeep`, `general/.gitkeep`, `shared/.gitkeep` — not `.md`
   files, never matched by the scanner). T452's own closing brief (`task-T452.md`) explicitly
   scoped "vault content" as out of scope for that task. No sibling repo
   (`sia`, `sia-harness`, `CWSO`) has an `implementation/knowledge/memory/shared/` subtree either,
   so no `--shared-source-root` would have contributed real content. **Building "the real index"
   today is, honestly, building an index of zero real entries** — this is the true, disclosed state
   of this repo's knowledge vault, not something padded out with filler content to look
   non-trivial.
4. **Real build executed, real output produced.** Ran (from this task's own `origin/develop`
   worktree, throwaway venv active):
   ```
   python3 -m implementation.runtime.memory.build \
     --project-id em-age/emage.code --own-repo-root . --general-repo-root . \
     --output-dir <scratch>/t485-index-out
   ```
   Result: `wrote 0 chunks, 0 rejections to <scratch>/t485-index-out` (exit 0). Real output files
   on disk, matching `indexing-pipeline-v1.md` §2's documented three-file format exactly:
   `index.jsonl` (0 bytes), `rejections.jsonl` (0 bytes),
   `manifest.json` = `{"chunk_count": 0, "embedding_dim": 768, "embedding_model":
   "nomic-ai/nomic-embed-text-v1.5", "entry_count": 0, "index_format_version": 1, "project_id":
   "em-age/emage.code", "rejection_count": 0}`. The embedder was still constructed (needed to
   populate `embedding_model`/`embedding_dim` in the manifest even with zero chunks), confirming
   `fastembed`/ONNX Runtime genuinely ran, not merely skipped. (Stderr showed benign
   `pthread_setaffinity_np` warnings from ONNX Runtime's thread pool under this sandbox's CPU
   affinity restrictions — cosmetic, non-fatal, did not affect the exit code or output.)
5. **Index storage location — determined not to be git-versioned.** ADR-005 Decision 1 states the
   derived index is "a **separately-built, read-only, rebuildable** vector index derived from"
   the canonical git-versioned store, and explicitly: "That index is what T453/T454 query. It is
   **not** the canonical store." T452's own closing verification explicitly confirms
   `git ls-files` was clean of any built index/venv artifacts before that task's merge. No
   `.gitignore` entry existed for the pipeline's own documented default output location
   (`implementation/runtime/memory/_index/`) — a real, pre-existing gap this task closes: added
   `implementation/runtime/memory/_index/` to `.gitignore` under the existing "Memory / agent
   runtime scratch" section, formalizing what ADR-005 Decision 1 and T452's own precedent already
   establish. The actual built index for this task lives in this session's scratch directory
   (outside the repo entirely) and is **not** included in this MR — both because the design says it
   shouldn't be, and, independently, because it is trivially small regardless (212-byte manifest,
   two empty files) given finding 3 above.
6. **Independent proof the index works — T484's exact corrected CLI invocation, re-run against the
   new index:**
   ```
   python3 -m implementation.runtime.memory.context_retriever \
     "how does the memory scope model enforce project isolation" \
     --index-dir <scratch>/t485-index-out --workspace-root . --platform-root .claude --top-k 5
   ```
   Result: **exit 0**, stdout `[]` (a valid, empty JSON array — no results, because the index has
   zero chunks, not because of any error). This is the real, new, different, honest outcome the
   task's own acceptance criterion asked for: the old `FileNotFoundError: manifest.json` (T484's
   finding) is gone, replaced by a real success with an empty result set — not a new failure. This
   is the actual proof of this task: the pipeline's read path now genuinely completes end-to-end
   against a real, on-disk, T452-built index, for the first time in this repo's history.

## Expected Outputs

1. `.gitignore` entry for `implementation/runtime/memory/_index/` (this MR).
2. This task brief, with Execution/finding notes filled in (this MR).
3. `docs/tasks/active-tasks.md`/`completed-tasks.md` updated to close this row (this MR).
4. The actual built `index.jsonl`/`rejections.jsonl`/`manifest.json` — **not committed**, per
   finding 5 above; left in this session's scratch directory, reproducible on demand via the exact
   command in finding 4.

## Acceptance Criteria

1. `fastembed` availability independently checked in this task's own environment before any other
   step — done, `ModuleNotFoundError` confirmed, then resolved per the T455 precedent (no silent
   workaround, no silent dependency-manifest change).
2. Real vault content state determined by direct inspection (not assumed) — done: zero `.md`
   files anywhere under `project/`/`general/`/`shared/`.
3. Real build pipeline run, real output produced and inspected — done: 0 chunks/0
   rejections/manifest as shown above, using the pipeline's own real CLI, no invented process.
4. Index storage location (git-versioned vs. gitignored) determined from ADR-005's own text, not
   assumed either way — done: gitignored, per Decision 1's literal "not the canonical store"
   framing and T452's own clean-`git-ls-files` precedent; `.gitignore` updated to formalize this.
5. T484's exact corrected CLI invocation re-run against the new index, real before/after outcome
   reported — done: `FileNotFoundError` → exit 0 with `[]`.
6. `git diff` against `origin/develop` for this branch touches only `.gitignore` and
   `docs/tasks/*.md` — no changes under `tests/golden/**`, `scripts/scorecard.py`,
   `docs/benchmarks/tb-subset.*`, `.mcp.json`, and no built index artifact committed.
7. This brief's closure explicitly states it does not close, advance, or scale T458/T456, and does
   not itself re-run T484's walking-skeleton trial.

## Blocker Protocol

No blocker escalation required — the one real blocker encountered (`fastembed` not installed) was
resolved within this task's own scope via the already-established T455 precedent, not escalated.

## Explicitly out of scope (flagged for the user, not assumed)

Re-running T484's full walking-skeleton trial (one live control/treatment trial pair) with the
treatment arm's retrieval now actually reaching a real (if empty) index, to see whether that
changes anything about the observed booleans or the treatment arm's behavior when a real retrieval
call succeeds but returns no results. This task deliberately does not do this — it is a distinct
next step for the user to authorize, not something this "build the index and prove it works" task
is scoped to decide unilaterally.

## Execution notes

All six findings above are the real execution record. Worktree: `docs/t485-first-memory-index-build`
branch, from `origin/develop` at `602ad12`. Throwaway venv:
`python3 -m venv` + `pip install -r implementation/runtime/memory/requirements.txt` in this
session's scratch directory (outside the repo) — no repo dependency manifest touched. `git status
--short` in the worktree confirmed clean (no stray `__pycache__`/venv artifacts) both before and
after running the build and the CLI query. `git diff --stat` against `origin/develop` for this
branch: `.gitignore` (4 lines added), `docs/tasks/task-T485.md` (new),
`docs/tasks/active-tasks.md`/`completed-tasks.md` (ledger closure) — nothing else.
