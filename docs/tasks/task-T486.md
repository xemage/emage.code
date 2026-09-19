# Task T486 — First real population of the knowledge vault

**ID:** T486
**Owner:** devops-engineer
**Status:** done
**Priority:** P1
**Depends on:** T485 (done — built the first-ever real index against this repo, found the vault
itself is genuinely empty)
**Blocks:** Nothing structurally. **Does not close, advance, or scale T458 or T456.** Does not
re-run T484's walking-skeleton trial. T456/T457/T458/T483 remain untouched by this task.
**Created:** 2026-09-12
**Based on:** `docs/tasks/task-T485.md` (merged `origin/develop` at `4eb732c`, MR !290 — its own
finding is this task's entire premise: "the vault is genuinely, structurally empty today...
`implementation/knowledge/memory/` contains only `README.md`... and three `.gitkeep`
placeholders"); `docs/artifacts/memory-scope-model-v1.md` (T451 — the `general`/`project`/`shared`
scope model and its `include(entry, P)` predicate, read fresh this task); `docs/artifacts/
indexing-pipeline-v1.md` (T452 — on-disk index format, chunking approach); the real, current
`implementation/runtime/memory/scanner.py`, `validate.py`, `schema.py`, `chunker.py`, `build.py`,
`context_retriever.py` source (read fresh this task, not guessed at); `implementation/knowledge/
memory/README.md` (T452's own vault directory convention note, explicitly scoping "populate a real
corpus" out of T452 and into "future content-authoring work"); `docs/artifacts/protected-paths-
v1.md`, `docs/decisions/ADR-005-memory-layer-design.md`, `docs/artifacts/golden-suite-format-
v1.md` §2, `AGENTS.md`, this repo's own branch-protection convention document under
`.claude/rules/` (the real, already-merged source content this task's vault entries are drawn
from — see each entry's own frontmatter `tags` for which source it summarizes; deliberately not
naming that file's exact filename here, since it is a currently-top-tier registry component and
this brief is itself an open `P1` task — see entry 2's own content, and the sweep in step 9 below,
for why).

## Objective

Populate `implementation/knowledge/memory/{project,general}/` with a small, bounded, honest first
set of real vault entries — 11 total (6 `project`-scope, 5 `general`-scope; no `shared`-scope
entries this task, see "Explicitly out of scope" below) — each a genuinely useful, durable fact
about this project/harness sourced from real, already-merged repo content, not fabricated. Then
rebuild the index for real against this new content (same throwaway-venv `fastembed` approach
T485 already established) and prove via the real `context_retriever` CLI that a real query now
returns real, non-empty, relevant results. This is explicitly a small, illustrative first
population, **not comprehensive coverage of this project's knowledge** — do not report or imply
completeness beyond these 11 entries.

## Why this split of scopes (read `memory-scope-model-v1.md` §2 before objecting to any placement)

`general` = "knowledge about emage.code itself (the harness), not about any one project that
installs or runs it" — portable to every project this harness is deployed against, because it
describes the harness's own standing conventions/mechanisms, not this one repo's own engineering
history. `project` = specific to this repo's own current-development engineering history/decisions
— not portable to a different project's session. Six of the eleven entries below turned out to be
genuinely `general` per that literal definition (the vault-authoring convention itself, the
blocker-retry rule, the protected-branch policy, the validation-gate verdict protocol, and the
agent-tool-grant-check discipline are all standing harness mechanisms, true for every project using
this harness) — this is disclosed as a real finding from applying the model's own predicate, not a
deviation from the instruction to "prefer project scope for most of it" (6 of 11 are still
`project`-scope, the plurality).

## Exact files to create (verbatim — do not paraphrase, do not add or remove entries)

All 11 files go under `implementation/knowledge/memory/<scope>/<filename>`. Each is delimited below
by its exact target path, then its exact literal content between `---FILE START---`/`---FILE
END---` markers (the markers themselves are not part of the file — everything between them,
including the leading `---` YAML fence, is the file's exact real content).

### 1. `implementation/knowledge/memory/project/protected-golden-suite-paths.md`

---FILE START---
---
scope: project
project_id: em-age/emage.code
title: "Protected paths: tests/golden/** and scripts/scorecard.py are frozen against normal improvement-task edits"
tags: [golden-suite, protected-paths, branch-protection]
---

## Why these two paths are protected

Two paths in this repository, `tests/golden/**` and `scripts/scorecard.py`, are protected: no agent
definition may edit them as part of normal improvement-task work. They are the golden-suite
evaluator's own interface and held-out data — the thing improvement work is graded against, not a
thing improvement work may itself change to make its own results look better. Source:
`docs/artifacts/protected-paths-v1.md`.

## Three independent controls, not one

Because "held-out set leaks into improvement work" is rated Medium likelihood / Critical impact in
this project's own roadmap risk table, three independent controls apply at once: a repo-wide static
path guard that catches functional access to the held-out set and bare mentions of specific
held-out case IDs anywhere outside `tests/golden/`; an evaluator-hash tamper-evidence check; and
this document's own per-agent write-scope exclusion plus a static guard proving every agent
definition declares the exclusion. Each control catches a different failure mode; none alone is
treated as sufficient on its own.

## What is not frozen

Freezing write scope does not freeze read scope: the orchestrator retains standing read/audit
access to both paths for verification and evaluation. Genuine future maintenance to a protected
path requires an explicit, named task brief that cites the protection document and states the
exception outright — never a silent incidental edit inside unrelated work.
---FILE END---

### 2. `implementation/knowledge/memory/project/held-out-isolation-ledger-defect-sweep.md`

---FILE START---
---
scope: project
project_id: em-age/emage.code
title: "Two independent leak guards this repo runs before any push: held-out case-ID isolation and the maturity registry's self-referential ledger-defect check"
tags: [golden-suite, protected-paths, maturity-registry]
---

## Held-out case-ID isolation

A repo-wide static guard fails if any file outside `tests/golden/` (as a whole) mentions one of the
golden suite's real held-out case IDs as a whole token, or if any Python source file outside the
held-out directory contains the literal held-out path string. This catches doc or report content
that would otherwise reveal what a held-out case actually tests. New documentation, task briefs,
and reports authored in this repo must never quote a real held-out case ID by name — describe
held-out findings by aggregate or category instead.

## The maturity registry's own self-referential trap

Separately, this repo's component-maturity checker treats any currently-open (non-`done`,
non-`cancelled`), `P0`- or `P1`-priority task row whose title or brief text names an already-top-
tier component's real registry id as a whole word as an open defect against that component — even
if the task has nothing to do with that component. This exact class of mistake has recurred
repeatedly in this project's own task history. The safe pattern established in response: never
trust a previously-quoted id list or count; re-derive the live, current set of top-tier component
ids directly before writing new task content; sweep new task titles/briefs against that live list;
and prefer closing a task within the same commit sequence that created it, so its brief is never
left attached to an open ledger row at all.
---FILE END---

### 3. `implementation/knowledge/memory/project/golden-suite-no-live-model-design.md`

---FILE START---
---
scope: project
project_id: em-age/emage.code
title: "The golden suite deliberately never invokes a live, sampling model completion"
tags: [golden-suite, evaluation-design]
---

## The tension this design resolves

This project's roadmap sets two hard constraints in tension: a golden case's checker must return
binary pass/fail with no LLM-judged scoring, and re-running the suite on an unchanged tree must
produce an identical scorecard (deterministic). A checker that invokes a live agent or model
completion in-process is not run-to-run deterministic — model sampling, latency, and transient
infrastructure failures all vary — and is too slow and costly to run repeatedly at suite scale.

## The resolution

Each case's checker performs deterministic, scripted validation of a given end state and never
itself invokes a live, sampling model completion. A case's brief documents intent and may separately
be reused as literal input to a real live agent run in a different system as an authoring aid, but
the checker that actually grades pass/fail stays pure, offline, and repeatable. Source:
`docs/artifacts/golden-suite-format-v1.md` §2.
---FILE END---

### 4. `implementation/knowledge/memory/project/terminal-bench-two-host-topology.md`

---FILE START---
---
scope: project
project_id: em-age/emage.code
title: "Terminal-Bench trial data lives on two hosts; the remote host's data is read, never copied into the repo"
tags: [terminal-bench, infrastructure, evaluation]
---

## Two independent trajectory sources

This project's Terminal-Bench measurement work combines trial data from two separate hosts: a
local run, and a separate remote host reached over read-only SSH. Both sources' raw result/verifier
output are treated as authoritative and are independently re-derived directly from the raw files
(not trusted from any prior self-report) when closing out a measurement task.

## Deliberate non-duplication

The remote host's own trial data is read directly for analysis but is explicitly not copied into
this repository — an artifact-reconciliation decision made when the two sources were first
combined. Verification steps that need to confirm "no new trial activity happened" check the remote
host's own state directly (e.g. its container/image list) rather than relying on a summary produced
by whichever pass generated the report being verified.
---FILE END---

### 5. `implementation/knowledge/memory/project/adr-005-memory-layer-decisions.md`

---FILE START---
---
scope: project
project_id: em-age/emage.code
title: "ADR-005: this repo's memory layer keeps a git-versioned canonical store and a separate, non-canonical derived index"
tags: [adr, memory-layer, architecture]
---

## Storage: canonical store vs. derived index are two different things

This repo's accepted memory-layer decision record establishes that knowledge entries live as
Markdown files with YAML frontmatter, committed and reviewed through the normal git workflow, as
the canonical source of truth. A separate, rebuildable vector index is derived from that store at
build time; the index is read-only, is not itself git-versioned, and rebuilding it from a clean
checkout must always reproduce it. Querying code talks to the derived index, never to the canonical
store directly.

## Embeddings: local model, zero recurring cost, chosen precisely to avoid a spend-authorization gate

The same decision record chooses a local, open-source embedding model over any paid embeddings API,
specifically because a paid API would be invoked at every index build and at every retrieval query
thereafter — a recurring, unbounded operational cost, unlike a one-off bounded expense. Because the
chosen model has no per-token or subscription cost, building the indexing pipeline did not require
prior user cost-authorization the way a paid alternative would have.

## Read-only-by-default, asserted in three independent places

No agent may write to the canonical store or the derived index outside the sanctioned rebuild step.
The read-only guarantee is asserted in three independent places (agent definition, server config,
deployment manifest) rather than one — the same "more than one independent control" pattern this
repo already uses for its protected golden-suite paths, so a single missed update cannot silently
reopen the write path.
---FILE END---

### 6. `implementation/knowledge/memory/project/memory-scope-enforcement-mechanism.md`

---FILE START---
---
scope: project
project_id: em-age/emage.code
title: "One predicate, not two: how this repo's memory index makes project-scope content provably unreachable across projects"
tags: [memory-layer, scope-model, architecture]
---

## The same function produces both outcomes

This repo's knowledge-vault indexing pipeline enforces scope with a single inclusion predicate,
evaluated identically regardless of an entry's declared scope: `general`-scope entries are always
included; `project`-scope entries are included only if they were found while scanning the target
project's own repository tree; `shared`-scope entries are included only if the target project is
named in that entry's own explicit consumer allowlist. There is no separate "exclusion mechanism"
for project scope and a separate "inclusion mechanism" for shared scope — one function, branching on
frontmatter data written once at commit time.

## Why project-scope unreachability is structural, not filtered

Building one project's index never even opens a directory outside an explicit, named set of
repository roots. A project-scoped entry that lives in a different repository is not read and then
discarded by a filter — the filesystem call that would have read its directory never happens at
all. This is what makes cross-project unreachability provable rather than merely "currently
observed to work."

## Reject, never default

A missing or malformed scope value is rejected and logged at index-build time; it is never defaulted
to the least-restrictive scope (`general`) or the most-restrictive (`project`). The same rule
applies to a `shared`-scope entry with an incomplete consumer allowlist — an incomplete allowlist is
treated as malformed input, not as "share with everyone" or "share with no one."
---FILE END---

### 7. `implementation/knowledge/memory/general/knowledge-vault-frontmatter-convention.md`

---FILE START---
---
scope: general
title: "How to author a knowledge-vault entry this harness's indexing pipeline will actually pick up"
tags: [memory-layer, vault-convention, authoring]
---

## Required shape

A vault entry is a Markdown file with a YAML frontmatter block at the very top. Every entry
requires a `scope` field set to exactly one of `general`, `project`, or `shared` — a `project`-
scope entry additionally requires `project_id`; a `shared`-scope entry additionally requires a
`shared_consumers` block naming both an explicit project allowlist and an explicit platform
allowlist. A missing or malformed value in any of these is rejected at index-build time, never
defaulted.

## Where the file has to live, and why headings matter

The indexing pipeline only ever looks for `.md` files inside three exactly-named subdirectories —
`general/`, `project/`, and `shared/` — under each repository's own knowledge-vault root; a file
placed anywhere else, or a scope value that does not match the subdirectory it was found in, is
never indexed. The body below the frontmatter is chunked section-aware: each Markdown heading
starts a new retrievable chunk, so an entry covering more than one distinct fact reads and retrieves
better as multiple headed sections than as one long undifferentiated block.
---FILE END---

### 8. `implementation/knowledge/memory/general/blocker-retry-limit.md`

---FILE START---
---
scope: general
title: "This harness's own blocker escalation limit: two retries, then escalate"
tags: [blocker-protocol, agent-behavior]
---

## The rule

Per this harness's own standing agent conventions, a blocker is classified by type (technical,
dependency, unclear-requirements, or external) and by severity, and an agent working a blocker
retries it at most twice before treating it as escalation-worthy rather than continuing to retry
silently. This applies to every agent role and every project this harness is deployed against — it
is not a convention any one project's own codebase defines for itself.

## Why a hard number, not a judgment call

A fixed retry ceiling exists so that "still trying" cannot silently substitute for "actually stuck."
An agent that has retried twice and still failed is expected to report the blocker upward — with its
type, severity, and what was already tried — rather than either giving up silently or looping
indefinitely on the same failing approach.
---FILE END---

### 9. `implementation/knowledge/memory/general/protected-branch-no-direct-commit-policy.md`

---FILE START---
---
scope: general
title: "No direct commits to the two protected branches, ever - not even a one-line docs edit"
tags: [branch-protection, branch-policy]
---

## The rule has no size or content exception

This harness's two integration branches are protected on the remote: the remote git host rejects
any direct push to either one, with no exception carved out for a change that is small, urgent, or
documentation-only. A single-file ledger-status edit requires exactly the same branch-plus-merge-
request flow as an application-code change — branch protection does not distinguish by diff size or
file type, and neither does this convention. This applies equally to changes an orchestrating role
makes directly, not only to changes made inside a dispatched agent's own isolated workspace.

## Recovery if it happens anyway

If a commit ends up directly on a local protected branch that is protected on the remote too, the
recovery is: create a new branch pointing at that commit, diff it against the remote branch to
confirm nothing unique would be lost, reset the local protected branch back to match the remote,
then push the new branch and open an ordinary merge request. Never force-push over the rejection,
and never discard the commit outright.
---FILE END---

### 10. `implementation/knowledge/memory/general/validation-gate-verdict-protocol.md`

---FILE START---
---
scope: general
title: "Validation gates use exactly three verdicts, and reviewers do not fix what they are reviewing"
tags: [quality-gates, review-protocol]
---

## Three verdicts, three consequences

Every quality gate in this harness resolves to exactly one of three verdicts. `PASS` proceeds to
the next phase outright. `CONDITIONAL_PASS` also proceeds, but the reviewer's stated conditions are
recorded and tracked in the task list rather than silently dropped. `FAIL` blocks progression
entirely until fix tasks are created and re-delegated, and the same gate is re-invoked once the fix
lands — it is not overridden or waived.

## Reviewers do not edit what they are reviewing

A review-role agent (Tech Lead, QA, or Security) does not modify code or content during its own
review pass — its output is the verdict itself, plus annotations, approvals, or rejections. Fixing
a finding is always a separate, subsequently-dispatched task, never something the reviewer does in
the same pass as producing the verdict.
---FILE END---

### 11. `implementation/knowledge/memory/general/agent-tool-grant-check-discipline.md`

---FILE START---
---
scope: general
title: "Before dispatching a nested Agent-tool call, check the assignee actually has the Agent tool"
tags: [agent-dispatch, tool-grants]
---

## The gap this guards against

Most specialist agent roles in this harness do not carry the tool that lets one dispatched session
launch another (an in-process nested agent dispatch) — only orchestrator-shaped roles do by
default. A task whose objective requires that capability cannot simply be handed to a specialist
role and assumed to work; the assignee's own declared tool grant has to be checked explicitly
first, not inferred from the role's general competence at the task's subject matter.

## What to do when the gap is real

Do not silently widen a role's tool grant to route around a missing capability for one task — that
is a standing, cross-task change to a role's permissions being made to solve a local problem.
Instead, reassign the specific slice that needs the capability to a role that already has it, or
have the orchestrating role execute that bounded slice directly, and record which of the two was
chosen and why.
---FILE END---

## Exact commands to run, in order

All commands run from this worktree's own root (the branch `agent/devops-engineer/T486`, checked
out from `origin/develop`), unless otherwise noted.

1. Write all 11 files above verbatim (paths and content exactly as given — do not add, remove, or
   edit any entry; if you believe a fact is wrong, stop and report a `type: unclear_requirements`
   blocker rather than silently changing it).
2. Confirm `fastembed` availability the same way T485 did — do not assume:
   ```
   python3 -c "import fastembed" 2>&1
   ```
   If it fails with `ModuleNotFoundError` (expected, matching T484/T485's own finding in every
   environment checked so far), resolve it exactly as T485 did: create a throwaway venv **outside
   this repo** (e.g. under your own scratch directory, never inside this worktree) and install the
   already-repo-pinned `fastembed==0.8.0` from `implementation/runtime/memory/requirements.txt`
   into it. Do **not** touch this repo's own dependency manifests. Do **not** silently fall back to
   a different embedder or skip the real build.
3. With the throwaway venv active, build the index for real:
   ```
   python3 -m implementation.runtime.memory.build \
     --project-id em-age/emage.code --own-repo-root . --general-repo-root . \
     --output-dir <your-scratch-dir>/t486-index-out
   ```
   Report the exact stdout line (`wrote N chunks, M rejections to ...`) and the real
   `manifest.json` contents. **`N` must be greater than 0** (this task's entire point is that it no
   longer is) — if it is still 0, stop and report a blocker rather than declaring success; something
   about the vault content or the scanner's expectations was misunderstood, and this task needs to
   find out what before claiming completion.
4. Confirm zero rejections, or if any rejection exists, report its exact reason from
   `rejections.jsonl` rather than silently ignoring it — every one of the 11 entries above was
   authored against this task's own reading of the real `validate.py`/`schema.py` source, so a
   rejection here is a signal this brief's understanding of that source was wrong somewhere and
   needs to be corrected, not worked around.
5. Run the real proof-of-retrieval query with the real CLI (same invocation shape T484/T485 already
   established and corrected):
   ```
   python3 -m implementation.runtime.memory.context_retriever \
     "why are tests/golden and scripts/scorecard.py protected paths in this repository" \
     --index-dir <your-scratch-dir>/t486-index-out --workspace-root . --platform-root .claude --top-k 5
   ```
   Report the exact JSON output. **This is the task's central deliverable** — a real, non-empty,
   genuinely relevant result set (expected: entry 1 above,
   `protected-golden-suite-paths.md`, should be at or near the top; report honestly if it is not,
   do not reorder or cherry-pick what you report).
6. Run a second, different query to confirm this isn't a one-off fluke — your choice of a query
   that should hit a different one of the 11 entries (e.g. something about the memory scope model,
   or about blocker escalation), same CLI shape, report the exact JSON output for this one too.
7. Scope-isolation and rebuild-determinism spot checks — do not skip:
   - `python3 -m pytest tests/functional/test_memory_indexing_pipeline.py -q` (or
     `python3 -m unittest tests.functional.test_memory_indexing_pipeline -v` if `pytest` is not
     available) with the throwaway venv active — report pass/fail/skip counts.
   - `python3 -m pytest tests/functional/test_retrieval_eval_metrics.py -q` — the existing
     retrieval-eval suite (T455) — report pass/fail counts. This does not require the real vault
     content (it uses its own synthetic corpus per `retrieval-eval-v1.md` §3) — it is a regression
     check that this task's changes did not break its assumptions about the vault's structure, not
     a retrieval-eval re-run against the new content.
   - `python3 -m implementation.runtime.memory.build --check-against <t486-index-out> --project-id em-age/emage.code --own-repo-root . --general-repo-root . --output-dir <anything, ignored by --check-against>`
     — confirm rebuild-determinism holds against the index you already built in step 3 (should
     print "no drift").
8. Full baseline regression: `python3 tests/run.py` — report the exact pass/skip/fail counts and
   compare against the pre-existing baseline (514 tests per T443's last recorded run; if this
   differs for a reason unrelated to this task's own changes, say so plainly rather than silently
   reconciling it).
9. Self-referential ledger-defect sweep (see entry 2's own content above for why this matters):
   re-derive the live, current top-tier component id list
   (`python3 implementation/scripts/check-maturity.py --root implementation --verbose`) and grep
   this brief's own text and all 11 new vault files against it — report the real result. Also grep
   all 11 new vault files against the live held-out case-ID list
   (`ls tests/golden/held-out/`) — report the real result (expected: zero hits on both sweeps,
   since none of this brief's content was written by copying either list).
10. `git status --short` and `git diff --stat origin/develop` — confirm the diff touches exactly:
    the 11 new files under `implementation/knowledge/memory/{project,general}/`, and nothing else
    (this task does not touch `docs/tasks/active-tasks.md`/`completed-tasks.md` — ledger
    transitions are orchestrator-only; the orchestrator has already added this task's `in_progress`
    row and will close it separately). Confirm no stray venv/`__pycache__`/index-output artifacts
    are staged.
11. Commit (conventional commit, e.g. `feat(memory): populate knowledge vault with first real
    entries`), push the branch `agent/devops-engineer/T486`, and open a merge request to `develop`
    referencing T486. **Do not run `glab mr merge`.** Leave it open for the orchestrator.
12. Poll the pipeline to completion (`glab` / `mcp__gitlab`) and report the real, final CI status —
    do not report before it has actually finished.

## Constraints

- Never touch `feature/T475-codex-platform-integration`.
- Never edit `tests/golden/**`, `scripts/scorecard.py`, or `docs/benchmarks/tb-subset.json`/`.md`.
- No new paid/metered API usage.
- Do not install `fastembed` (or anything else) into this repo's own dependency manifests — the
  throwaway-venv approach is mandatory, per the exact T455/T485 precedent.
- Do not edit `docs/tasks/active-tasks.md` or `docs/tasks/completed-tasks.md` — ledger transitions
  are orchestrator-only. Report completion back to the orchestrator; do not archive your own task
  row.
- Do not run `glab mr merge` (or any equivalent). Open the MR, leave it open, and stop.
- Do not add, remove, reword, or "improve" any of the 11 entries above beyond fixing a literal
  transcription mistake — if you believe an entry is factually wrong or badly scoped, report it as
  a blocker rather than silently changing it; every entry here was deliberately drawn from real,
  already-merged source content and independently checked against the current live repo state
  before being written into this brief.
- T456/T457/T458/T483 remain untouched by this task.

## Acceptance criteria

1. Exactly the 11 files above exist, verbatim, at the exact paths given.
2. A real index build against them produces `chunk_count > 0` and `rejection_count == 0` (or, if
   not, the exact rejection reason is reported honestly rather than the task being declared done
   anyway).
3. Both real CLI queries (step 5, step 6) return real, non-empty, genuinely relevant results — the
   exact JSON reported, not summarized or predicted.
4. `test_memory_indexing_pipeline.py`, `test_retrieval_eval_metrics.py`, and the `--check-against`
   rebuild-determinism check all pass/hold, with real reported counts.
5. `python3 tests/run.py` passes with no new failures versus the pre-existing baseline.
6. The self-referential ledger-defect sweep (step 9) is actually performed against a freshly
   re-derived live list, not a count copied from this brief, and its real result is reported.
7. `git diff --stat origin/develop` shows only the 11 new vault files — nothing under
   `tests/golden/**`, `scripts/scorecard.py`, `docs/benchmarks/tb-subset.*`, `.mcp.json`, or the
   ledger files.
8. MR opened from `agent/devops-engineer/T486` to `develop`, referencing T486, left unmerged, CI
   polled to a real final state (not assumed green).
9. The completion report explicitly states this is a small, illustrative first population (11
   entries) and does not claim comprehensive coverage of this project's knowledge.

## Blocker protocol

Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`) +
severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries before
escalating back to the orchestrator.

## Explicitly out of scope

- **No `shared`-scope entries this task.** `shared` scope requires explicit named consumer
  projects/platforms and, per the scanner's own design, an entry in this repo's own `shared/`
  subtree is only ever picked up when building a *different* project's index via
  `--shared-source-root` — it would never appear in this task's own verification build for
  `em-age/emage.code` itself, making it impossible to prove via this task's own CLI-query
  deliverable. A future task with a real sibling-project consumer in mind, and a way to actually
  test the cross-repo build, is the right place for `shared`-scope content, not this one.
- Does not scale T458, does not re-run T484's walking-skeleton trial, does not touch T456/T457/T483.
- Does not claim this is comprehensive coverage of this project's knowledge — it explicitly is not.


## Execution notes

Dispatched to `devops-engineer` on `agent/devops-engineer/T486` (from `origin/develop` `4eb732c`).
Delivered exactly the 11 files above verbatim; real build `wrote 25 chunks, 0 rejections`
(`entry_count: 11`); both required CLI queries returned real, relevant top hits (`protected-
golden-suite-paths.md`, `memory-scope-enforcement-mechanism.md`); `test_memory_indexing_
pipeline.py` (18 pass/2 env-gated skip), `test_retrieval_eval_metrics.py` (24 pass), and
`--check-against` rebuild-determinism ("no drift") all held. One pre-existing, orchestrator-owned
`tests/run.py` finding disclosed honestly rather than worked around: `test_every_active_task_has_
a_plan` failed while this task's row was still `in_progress` with no backing plan doc — resolved
by this same closure (see `active-tasks.md`'s T486 closure note), not by adding a retroactive plan
reference.

**Orchestrator independently re-verified before this brief was marked `done`, not accepted on the
implementer's self-report alone**: re-derived the live 31-id stable-component list and the 6-id
held-out list directly and re-swept this brief and all 11 committed vault files against both
(zero hits); independently rebuilt the index in a separate throwaway venv and reproduced the exact
`25 chunks, 0 rejections, entry_count: 11` manifest byte-for-byte; independently re-ran both CLI
queries against that independently-built index and confirmed the same top hits and scores
(`0.924`, `0.875`) reported by the implementer; confirmed `git diff --stat origin/develop` on the
pushed branch is exactly the 11 vault files (269 insertions), nothing else; confirmed MR !291
(`agent/devops-engineer/T486` -> `develop`) open, unmerged, referencing T486; confirmed the actual
GitLab pipeline (`2843462694`, SHA `9564fbc`) via `glab ci status` directly — 5/5 jobs green.

**A real self-referential ledger-defect was caught and fixed during this task's own authoring,
before dispatch** — see `active-tasks.md`'s T486 closure note for the full account (two
currently-top-tier component ids appeared as bare tokens in this brief's own first draft; caught
by running `check-maturity.py --verbose` against the undispatched draft, fixed, re-confirmed
31/31 stable before the brief was ever handed to `devops-engineer`).

This is a small, illustrative first population of the knowledge vault (11 entries) — it does not
claim comprehensive coverage of this project's knowledge, does not close, advance, or scale T458
or T456, and does not re-run T484's walking-skeleton trial. Left unmerged (MR !291) per this
session's standing no-self-merge instruction.
