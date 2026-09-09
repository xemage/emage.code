# T452 pipeline test fixtures — synthetic, not real knowledge-base content

Mirrors this repo's `tests/golden/_example-scaffold/` precedent: a worked,
minimal example that mechanically proves the pipeline's own contract, not a
production dataset. See `docs/tasks/task-T452.md`, "Vault content —
explicitly out of scope", and `docs/artifacts/memory-scope-model-v1.md` §8
(the verification checks these fixtures exist to satisfy).

## Layout

- `general-source/` — simulates the single harness repo's `general/` tree
  (one valid entry).
- `repo-p1/` — simulates a *foreign* project's own repo. Contains one valid
  `project`-scope entry (whose content is distinctively tagged so a leak into
  another project's index is trivially detectable) and one valid
  `shared`-scope entry naming `fixture-org/repo-p2` as a consumer.
- `repo-p2/` — simulates the *target* project's own repo. Contains one valid
  `project`-scope entry (with a fenced Python code block, to exercise the
  tree-sitter chunking path end-to-end) plus every §5 rejection case:
  - `reject-missing-scope.md` — no `scope:` field at all
  - `reject-missing-project-id.md` — `scope: project`, no `project_id`
  - `reject-incomplete-shared-missing-platforms.md` — `shared_consumers.projects`
    present, `.platforms` missing
  - `reject-incomplete-shared-empty-projects.md` — `shared_consumers.projects: []`
    (empty list, not omission — still malformed per §5)

`tests/functional/test_memory_indexing_pipeline.py` builds project
`fixture-org/repo-p2`'s index against `repo-p2` (own repo) +
`general-source` (general source) — proving the rejection cases and the
one-code-chunk-per-symbol enrichment. A second build additionally configures
`repo-p1` as a shared source to prove both the negative (structural
unreachability of `repo-p1`'s `project`-scope entry) and positive
(`repo-p1`'s opted-in `shared`-scope entry does appear) outcomes from the
identical `include(entry, P)` mechanism.

These fixture repos are copied into a temp directory and given a real `git`
commit at test time (see the test module) so the pipeline's `commit`
enrichment field and repo-boundary scan are exercised against genuine git
checkouts, not synthetic placeholders.
