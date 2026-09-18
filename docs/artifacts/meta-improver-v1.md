# `@meta-improver` — v1

**Based on:** `docs/tasks/task-T503.md` (`plan-035-roadmap-v7-ground-up.md`'s nominal T462,
`docs/plans/plan-055-phase6-closed-loop-rescoped-detailed-planning.md` §4's `T462-equiv` row,
`docs/artifacts/phase6-sia-readiness-audit-v1.md` §5 item 2 and §6),
`implementation/runtime/golden_harness/failure_taxonomy.py` (T501, this task's real, concrete
input), `docs/artifacts/protected-paths-v1.md` (authoritative source for the two protected paths
this task's own guard reproduces exactly), `docs/artifacts/phase6-kill-switch-v1.md` (T502, style
precedent for this document's own "prove the safety property with an adversarial test" approach).

**Refs:** T503. Builds the failure-cluster -> diff-proposal generator for Phase 6's eventual
closed loop.

## 1. What this document declares

This repository now has a real, tested `@meta-improver` module:

- `implementation/runtime/meta_improver.py` — the importable library: `DiffProposal`,
  `FailureCluster`, `classify_target_path`, `cluster_by_axes`, `generate_proposal`,
  `generate_proposals`.
- `tests/functional/test_meta_improver.py` — the committed test suite proving every safety
  property and functional behavior documented below, including the adversarial "never writes"
  proof.

`@meta-improver` consumes a failure cluster (built from T501's `FailureTaxonomy`) and emits the
smallest viable harness-change suggestion as a `DiffProposal` — **never an applied edit**. This is
the single most safety-relevant property this document exists to prove, not merely assert (see §6).

## 2. The proposal schema, and why

`DiffProposal` is a frozen `@dataclass` with these fields:

- `target_path` — repo-root-relative POSIX path of the file this proposal would change if a human
  reviewer accepted and applied it.
- `target_file_class` — one of `"agent"`/`"skill"`/`"command"`/`"instruction"`, **derived
  automatically** from `target_path` via `classify_target_path` in `__post_init__` (`init=False`)
  rather than accepted as a separate constructor argument. This is a deliberate design choice: it
  makes it structurally impossible for `target_file_class` to ever disagree with what
  `target_path` actually is, eliminating an entire class of "the label says X but the path says Y"
  bug.
- `rationale` — human-readable explanation of why this change is proposed and why this target file
  was selected (cites the cluster's axis values, the triggering case IDs, and the target-selection
  heuristic's score — see §4).
- `base_content` / `proposed_content` — the chosen representation of "the actual proposed change"
  (see below for why this pair, not a stored diff string).
- `based_on` — the triggering `FailureRecord.case_id` values, referenced by id into
  `FailureTaxonomy`, never duplicating the records' own data (per the task brief's explicit
  instruction).
- `cluster_cause` / `cluster_behavior` / `cluster_mechanism` — the triggering cluster's axis
  triple, carried for a reviewer's convenience (also recoverable via `based_on` +
  `FailureTaxonomy.get()`, so this is redundant-but-convenient, not the only source of truth).

**Base-content + proposed-content pair, not a stored diff string.** The task brief's Objective
point 1 allows either "a real diff/patch representation" or "a base-content + proposed-content
pair." This module stores the pair and exposes a `diff_text()` *method* that computes a real
unified diff (`difflib.unified_diff`, stdlib) on demand from the two stored strings. Reasons:

1. A stored pair is strictly more informative than a stored diff string alone — a reviewer (or a
   future T464-equiv MR-gate tool) can always derive the diff from the pair, but cannot recover the
   full proposed file content from a diff string without also having the base content on hand
   anyway. Storing the pair means the diff is never the *only* copy of "what would this file look
   like after."
2. `diff_text()` is a pure, in-memory computation over two strings already held by the object —
   `difflib` never touches the filesystem, so exposing it as a computed method (rather than a
   pre-baked stored field) adds no I/O surface at all, and no method on `DiffProposal` ever needs
   to re-read anything from disk after construction.

**No method anywhere on `DiffProposal` (or `FailureCluster`, or any object either can produce)
performs a real filesystem write, `git` subprocess call, or any other repository-mutating
operation.** This is proven in §6, not merely stated here.

## 3. Allowed target-file classes, and why

A proposal may only target files under exactly these four directories, matching this repo's actual
harness surface:

- `implementation/knowledge/agents/*.md`
- `implementation/knowledge/skills/*/SKILL.md`
- `implementation/knowledge/commands/*.md`
- `implementation/knowledge/instructions/*.md`

**Why these four and no others:** this is this repo's own definition of "the harness" — the agent
definitions, skills, commands, and instructions that shape how work in this repo is done — as
opposed to application code, which `@meta-improver` has no mandate to touch at all (per the task
brief's own framing, "this repo's own agent definitions, skills, commands, instructions — not
application code"). A diff proposal is a suggestion about *how the harness should change in
response to an observed failure pattern*; application code is out of scope for this generator by
construction, not merely by convention.

**Why never `tests/golden/**` or `scripts/scorecard.py`:** these are `docs/artifacts/
protected-paths-v1.md`'s own two declared protected paths, reproduced here exactly (not
reinvented): the golden-suite evaluator's own interface and held-out data — "the thing improvement
work is graded against, not a thing improvement work may itself change to make its own results
look better." `@meta-improver` is squarely "improvement work" in that document's sense, so its
target-path allowlist must, and does, exclude both paths by construction (they simply do not match
any of the four allowed directory patterns — see `classify_target_path`).

**Rejected at construction time, as a first layer of defense only.** `classify_target_path` is a
pure string/path computation with no filesystem access; it raises `ValueError` — never silently
accepts — for any path outside the four allowed classes, any absolute path, and any path containing
a `..` traversal segment. `DiffProposal.__post_init__` calls it unconditionally, so a `DiffProposal`
naming a disallowed path simply cannot be constructed. Per the task brief's own framing, this is a
**first layer only**; full enforcement (detecting a disallowed proposal that some other, future
code path might try to apply anyway) is T463-equiv's separate, not-yet-built job. This module's own
job is narrower and already fully met: making it *impossible for this generator itself* to produce
a `DiffProposal` object naming a disallowed path in the first place.

## 4. Clustering approach, and why

`cluster_by_axes(taxonomy)` groups every `FailureRecord` in a `FailureTaxonomy` by its
`(cause, behavior, mechanism)` triple (`FailureRecord.axes()`), returning one `FailureCluster` per
distinct triple, sorted by `(cause, behavior, mechanism)` for a deterministic, testable order.

**Why this grouping:** T461's brief explicitly deferred "clustering" as this task's own design
decision to make. Grouping by the shared axis triple is the minimal, well-defined choice that:

1. Requires no new query logic beyond what `FailureTaxonomy.filter_by` already supports —
   `filter_by(cause=..., behavior=..., mechanism=...)` returns exactly one cluster's membership,
   so clustering and querying are the same operation viewed from two directions.
2. Directly reflects this repo's own three-axis classification scheme (`docs/artifacts/
   failure-taxonomy-v1.md`): two failures with the same cause/behavior/mechanism are, by that
   scheme's own definition, the same *kind* of failure. A diff proposal generated from such a
   cluster is proposing to address one recurring, well-defined pattern, not an arbitrary grab-bag
   of unrelated failures that happen to share nothing meaningful.

**Alternatives considered and rejected:**

- Clustering by a single axis (e.g. `behavior` alone) was rejected: the real taxonomy data shows
  `behavior="required-section-absent"` shared across records with different `cause`/`mechanism`
  values that represent meaningfully different underlying problems (e.g.
  `undefined-structured-convention` / `field-level-absence-within-declared-block` vs.
  `established-practice-drift` / `whole-block-absence`) — collapsing them into one cluster would
  blur genuinely distinct failure patterns into a single, less-actionable proposal.
- A similarity-scoring/embedding-based clustering approach was rejected as unnecessary complexity
  for 15 already-classified records against a three-axis scheme that already provides exact-match
  grouping — the axis scheme itself is the similarity function this repo has already invested in
  building and validating (T501/T410/T409).

**A cluster of size 1 is valid, expected output, not an error.** Several real axis triples in the
current 15-record taxonomy are unique to one record; `cluster_by_axes` emits a singleton cluster for
each of them, and `generate_proposal` produces a proposal from a singleton cluster exactly the same
way as from a multi-record one (proven by `tests/functional/test_meta_improver.py`'s
`test_generate_proposal_for_real_singleton_cluster_is_plausible`).

## 5. Generation mechanism and target-selection heuristic, and why

`generate_proposal(cluster, repo_root=...)` is a **deterministic, rule-based/template generator**
— no live LLM dispatch of any kind. Given a cluster, it:

1. Selects a target file via `_select_target`'s keyword-overlap heuristic (below).
2. Appends a "Known failure pattern" note (`_render_addition`) citing the cluster's
   `cause`/`behavior`/`mechanism` and the triggering case IDs, framed explicitly as "a proposal
   only... this generator has no mechanism to apply it itself."

**Target-selection heuristic:** hyphen-derived keyword matching. `_axis_keywords(cluster)` splits
each of the cluster's three axis values on `-` and lowercases them (e.g.
`cause="undefined-structured-convention"` contributes the keywords `"undefined"`, `"structured"`,
`"convention"`), deduplicated across all three axes. Every candidate file under the four allowed
classes is scored by how many of these keywords appear as a case-insensitive substring anywhere in
that file's real, on-disk content; the highest-scoring file is selected, with ties broken by the
lexicographically smallest repo-relative POSIX path for full determinism. If every candidate scores
`0` (no keyword overlap at all — not observed against the real, current knowledge base, but a real
fallback path is still required so the function always returns *some* allowed target rather than
raising), the generator falls back to the lexicographically smallest file under
`implementation/knowledge/instructions/*.md` — deterministic, always present (that directory is
never empty in this repo), and instructions are this repo's most general "how work here is done"
surface, the most plausible home for a pattern with no clearer, more specific keyword match.

**Why this heuristic, and why it does not need to be sophisticated:** the task brief explicitly
authorizes "a simple, deterministic heuristic such as keyword/substring matching... it does not
need to be sophisticated, it needs to be deterministic, documented, and testable." Substring
matching over hyphen-derived tokens meets all three: it is trivially deterministic (no randomness,
no external state beyond the on-disk knowledge base at call time), fully documented here and in the
module's own docstrings, and directly testable (`tests/functional/test_meta_improver.py`'s
`TestClusterAndSelectSyntheticFixtures` proves both the overlap-wins case and the no-overlap
fallback case against synthetic fixtures with a controlled, known-content knowledge base — not just
the real tree's current, unverified overlap behavior).

**Why a template generator was judged sufficient, and no live LLM dispatch was required:** once
the schema and clustering logic existed, generating a plausible "Known failure pattern" note from a
cluster's own axis values and case IDs turned out to be a straightforward, deterministic
transformation — the axis values themselves (already human-readable strings like
`"undefined-structured-convention"`) are the substance of what needs to be communicated to a
reviewer, and a template renders them faithfully without requiring any generative drafting. This
was verified directly: `generate_proposal` run against the real cluster
`cause=established-practice-drift / behavior=naming-or-format-drift /
mechanism=naming-convention-drift` (3 real triggering cases) produces a proposal whose rationale and
proposed content correctly reference all three real axis values and all three real case IDs (see
`tests/functional/test_meta_improver.py`'s `test_generate_proposal_for_real_multi_case_cluster_is_
plausible`) — a genuinely plausible, reviewable suggestion, with no live dispatch needed. Per the
task brief's own instruction, this conclusion (template sufficiency) is reported here rather than
assumed silently; if a future reviewer judges a specific proposal's prose too thin for a real
merge decision, that is exactly the kind of refinement T464-equiv's human review step exists to
catch — this module's job is "smallest viable harness change as a diff proposal," not
publication-quality prose.

## 6. The adversarial "never writes" proof

`tests/functional/test_meta_improver.py`'s `TestNoFilesystemMutation` class proves the load-bearing
safety property two independent ways, both **passing** against the real, committed module (not a
hypothetical/idealized version of it):

1. **Static AST scan** (`test_static_scan_finds_zero_mutation_calls`): walks every `ast.Call` node
   in `implementation/runtime/meta_improver.py`'s own real source and asserts zero occurrences of:
   a write-capable `open(...)` call (mode `"w"`/`"a"`/`"x"`, or any dynamic/non-constant mode,
   conservatively flagged), `.write_text`/`.write_bytes`/`.unlink` method calls, `os.remove`/
   `os.rename`/`os.replace`/`os.system` calls, any `shutil.*` call, and any `subprocess.*` call.
   **Passed.** A companion test (`test_static_scan_detects_a_synthetic_violation`) proves the
   scanner is a real detector and not a no-op that always reports clean, by feeding it fourteen
   synthetic snippets — one per banned call shape — and confirming every single one is flagged. A
   third companion test (`test_static_scan_does_not_false_positive_on_read_only_calls`) proves the
   scanner does not over-flag ordinary read-only operations (plain `open()`, `Path.read_text()`,
   `str.replace()` — which is not `os.replace` — and `FailureTaxonomy.filter_by`), so the "zero
   violations" result on the real module is a meaningful pass, not an artifact of an overly narrow
   or overly broad scanner.
2. **Behavioral, real-filesystem snapshot test** (`test_full_pipeline_leaves_repo_byte_identical`):
   snapshots the repository's tracked-file state (`git status --porcelain`) plus a SHA-256 content
   hash of every file under the four target-eligibility-allowlisted knowledge directories and the
   real `docs/benchmarks/failures/**` data, runs the full real pipeline (load T501's real taxonomy
   -> `cluster_by_axes` -> `generate_proposals` for every real cluster, touching every proposal's
   `diff_text()` too), then re-snapshots and asserts byte-identical. **Passed** — nothing on disk
   changed as a side effect of generating proposals from real data.

Additionally, `TestTargetPathRejection` proves the first-layer defense-in-depth control from §3
against both of `docs/artifacts/protected-paths-v1.md`'s explicitly-named protected paths: a
proposal naming `tests/golden/open/example-case/expect.py` (representative of `tests/golden/**`)
and one naming `scripts/scorecard.py` both raise `ValueError` at construction time — a rejection,
not a silently-produced proposal object. (This test deliberately targets a path under
`tests/golden/open/**` rather than literally naming `tests/golden/held-out/**`, to avoid tripping
`tests/functional/test_golden_held_out_isolation.py`'s own unrelated Check A, which flags any
Python source literally containing the string `tests/golden/held-out` — `tests/golden/**` as a
whole, the actual protected-paths declaration, is fully exercised either way.)

## 7. `@meta-improver` is a Python module, not a registered subagent — this task's own decision

Reproduced here as this task's own documented decision, not merely a citation back to
`docs/tasks/task-T503.md`:

T454's `@context-retriever` precedent built a full 28th registered Claude subagent (a new
`implementation/knowledge/agents/context-retriever.md` definition, projected across all 7 platforms
via `sync.mjs`, plus a Docker Compose manifest and a supporting Python wrapper). **This task
deliberately does not follow that precedent.** A registered Claude subagent has a `tools:` grant. A
registered `@meta-improver` would put real pressure toward giving it enough tool access to function
as an interactive LLM session — at minimum `Read`, likely `Edit`/`Write` if some future session ever
asked it to "just fix it" directly — and that expansion pressure is exactly the shape of risk this
task exists to prevent.

Proving "architecturally incapable of writing" is far more tractable for a plain Python library
than for a registered agent definition: the question reduces entirely to "does this module's own
source code ever call a filesystem-mutating function," answerable by a static AST scan with no
tool-grant reasoning involved at all (§6). A registered agent's safety, by contrast, would depend on
a `tools:` YAML line in its own definition never being loosened in some later, unrelated edit — a
much weaker, more easily eroded guarantee.

**Decision: `@meta-improver` is built as a plain Python module and query/generation API under
`implementation/runtime/meta_improver.py`, callable directly (imported and invoked as a function
call — by the orchestrator today for live end-to-end validation, and by a future T463-equiv/
loop-runner later), not as a new `implementation/knowledge/agents/meta-improver.md` registered
subagent.** The `@meta-improver` name from `plan-035`/`plan-055` is used throughout this module's
own docstrings and this document purely as its conceptual/documentary name — it is not, and does
not imply, an instruction to run `sync.mjs`/`generate-registry.py` or to add any file under
`implementation/knowledge/agents/`, any platform's agent-projection folder, or
`implementation/registry/`. None of those were touched by this task.

## 8. Module placement

A single sibling module, `implementation/runtime/meta_improver.py`, directly alongside
`implementation/runtime/kill_switch.py` (T502) rather than a new package — mirroring
`kill_switch.py`'s own single-file precedent (not `golden_harness/`'s multi-file package shape,
which this module's scope did not require: one schema, one classifier, one clustering function, one
generation function is small enough to stay in one file without losing readability). `REPO_ROOT` is
derived identically to `kill_switch.py`'s own `Path(__file__).resolve().parents[2]` pattern.

## 9. What this does *not* do (scope boundary)

- **No apply/write path of any kind.** There is no `apply()` method, no `write()` function, no CLI
  wrapper that would take a `DiffProposal` and act on it. T464-equiv (the human MR gate) is the
  only path a proposal can ever take toward `develop`, and it does not exist yet.
- **No live LLM dispatch.** `generate_proposal`/`generate_proposals` are pure, deterministic,
  template-based functions with no `agent` tool call, no nested session, no network call of any
  kind.
- **No import from, reference to, or reuse of `implementation/sia/`,
  `implementation/adapters/sia-target/` (including `reward_shaping.py`'s blended-reward pattern), or
  `implementation/scripts/sia-executor.py`** — this module's only real dependency is
  `implementation/runtime/golden_harness/failure_taxonomy.py`'s public API, per this task's own
  brief.
- **No T463-equiv/T464-equiv/T465-equiv work.** No evaluator-hash tamper-evidence check, no
  promotion rule, no before/after golden-suite comparison run, no MR-gate automation, no lineage
  document — all remain separate, not-yet-dispatched future tasks.

## 10. Verification

- `tests/functional/test_meta_improver.py` — 21 tests: the two-part adversarial "never writes"
  proof (§6), the target-path rejection tests (§3/§6), real-data functional tests against T501's
  real taxonomy (§4/§5), and synthetic-fixture edge-case tests for the clustering singleton case and
  the target-selection heuristic's overlap/fallback behavior (§4/§5).
- `tests/functional/test_golden_held_out_isolation.py` re-run fresh after adding this task's files:
  passes (8/8) — no held-out isolation violation introduced.
- Run directly: `python3 -m unittest tests.functional.test_meta_improver -v`.
- Included automatically in `python3 tests/run.py` (discovered under `tests/functional/`): 649
  tests total (628 pre-task baseline + 21 new), `OK (skipped=38)` — no new failures.
