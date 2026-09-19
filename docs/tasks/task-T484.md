# Task T484 — T458 walking-skeleton: one live trial per arm, one golden case

**ID:** T484
**Owner (this slice, executed directly):** orchestrator — per user decision this session: the
outer dispatch mechanism for this slice is the in-process `Agent` tool (the same mechanism this
entire session uses for every delegation), and `devops-engineer`'s registered tool grant has no
`agent` tool (plan-044 Finding 3), so the orchestrator executes this specific slice directly,
mirroring the established "agent decides, orchestrator executes when the nominal owner lacks the
right tool" pattern already used for T436/T440. **`devops-engineer` remains T458's nominal owner
for the full live-execution-harness task** — this slice does not reassign T458 itself.
**Status:** done
**Priority:** P1
**Depends on:** None (reuses only already-`done` artifacts: the golden suite, `@context-retriever`)
**Blocks:** Nothing structurally. **Does not close T458 or T456.**
**Created:** 2026-09-12
**Completed:** 2026-09-12
**Based on:** `docs/plans/plan-044-t458-first-slice.md` (the backing plan this brief executes one
specific, previously-open decision of — dispatch mechanism and cost authorization, both now decided
by the user this session, see below); `docs/tasks/task-T458.md` (the full harness task this is a
bounded first slice of, not a replacement for); `tests/golden/open/new-feature-plan-doc-compliant/`
(the one golden case this slice exercises — `case.yaml`, `brief.md`, `expect.py`, all re-read fresh
and unmodified); `implementation/knowledge/commands/new-feature.md` (the literal `/new-feature`
template, `agent: "orchestrator"` frontmatter, `{{input}}` substitution point); `docs/artifacts/
context-retriever-v1.md` §2/§2.1 and `implementation/runtime/memory/context_retriever.py` (the
real CLI invocation shape for the treatment arm — see Correction below).

## Decisions this brief executes (both previously open in plan-044, now resolved by the user)

1. **Dispatch mechanism:** in-process `Agent` tool, executed by the orchestrator directly for this
   slice (plan-044 Question 1/2, decided).
2. **Cost/usage authorization:** not needed — this is ordinary interactive-session usage, comparable
   in scale to any other subagent dispatch already run this session, not a separate metered/paid API
   call (plan-044 Question 4, decided).

Plan-044's other three open questions (case-brief sufficiency, scratch-dir isolation shape) are
resolved by plan-044's own recommendation (plain temp directories; the illustrative brief is used
as-is and its sufficiency is treated as an empirical output of this slice, not a precondition).

## Correction found during fresh re-verification (this session, before any dispatch)

Plan-044 characterized the treatment arm's real CLI invocation as:
`python3 -m implementation.runtime.memory.context_retriever <query> <workspace_root>
<platform_root> <top_k>`. Re-reading `context_retriever.py`'s actual `_build_arg_parser()` this
session found this is **not accurate**: `query_text` is the only positional argument; `--index-dir`
(required), `--workspace-root` (required), `--platform-root` (required) are named flags, not
positional; `--top-k` is optional (default 10). The corrected real shape is:

```
python3 -m implementation.runtime.memory.context_retriever "<query_text>" \
  --index-dir <index_dir> --workspace-root <workspace_root> --platform-root <platform_root> \
  [--top-k <n>]
```

A second, more material finding from the same re-verification: `--index-dir` must point at a real,
already-built T452 index directory (`index.jsonl`/`manifest.json`), and none exists anywhere on
`origin/develop` (`git ls-tree` sweep: no `index.jsonl` checked in anywhere). `ContextRetriever`'s
default embedder (`LocalEmbedder`, via `fastembed`) is used by the CLI's `main()` with no override,
and `fastembed` is not installed in this environment (`python3 -c "import fastembed"` ->
`ModuleNotFoundError`). **This means the real CLI command, run exactly as documented, cannot
successfully return a retrieval result in this environment today** — it will fail before reaching
`RequestingContext` derivation, for reasons outside this slice's scope to fix (building a real index
requires the full T452 pipeline over the repo's knowledge base, and installing `fastembed` is a new
dependency change neither plan-044 nor this brief authorizes). This is treated as a real, honest
empirical fact the treatment arm's live session will encounter if it attempts the call — not
something to route around by fabricating an index or silently skipping the instruction. Reported
here per plan-044 risk item 3's own spirit (empirical discovery, not a predicted blocker) and
because it materially changes what "treatment" can concretely mean for this one trial: the session
is given the real (corrected) invocation and told it may consult prior context via it before writing
the plan doc; whatever it does when that call fails (proceeds without retrieved context, reports the
failure and reasons anyway, etc.) is itself part of this slice's real, honest result.

## Objective

Execute exactly plan-044's recommended walking-skeleton scope, once: for
`tests/golden/open/new-feature-plan-doc-compliant`, run one live control-arm trial and one live
treatment-arm trial of `/new-feature`'s literal template (with `{{input}}` = this case's real
`brief.md` text) in two separate, isolated plain scratch directories, then check each arm's real
produced output against the case's real, unmodified `expect.py` via the same
`importlib.util.spec_from_file_location` / `check(case_dir)` pattern `scripts/scorecard.py` already
uses. Report both real booleans, honestly, regardless of outcome.

## Constraints

- Never touch `feature/T475-codex-platform-integration`.
- Never edit anything under `tests/golden/**` — `expect.py` is read/imported only.
- Never edit `scripts/scorecard.py` or `docs/benchmarks/tb-subset.json`/`.md` (no second
  protected-path exception authorized this turn).
- No new paid/metered API usage beyond ordinary interactive-session dispatch.
- Do not install new dependencies (e.g. `fastembed`) or fabricate/construct a fake memory index to
  make the treatment arm's retrieval call artificially succeed — let the real environment's actual
  state (no index, no `fastembed`) play out honestly.
- This slice does not touch T456, T457, or T483.

## Expected Outputs

1. Two real, on-disk scratch runs (outside the repo, in plain temp directories — not committed).
2. Two real boolean `check()` results (control, treatment).
3. This brief's own Execution notes section, filled in with what actually happened.
4. `docs/tasks/active-tasks.md` / `completed-tasks.md` updated to close this row.

## Acceptance Criteria

1. Both arms' live sessions actually ran via the in-process `Agent` tool (not simulated, not
   hand-authored fixtures standing in for live output).
2. Both `check()` calls used the real, unmodified `tests/golden/open/new-feature-plan-doc-compliant/
   expect.py`, loaded via `importlib.util.spec_from_file_location`, called against a scratch
   directory laid out at `<scratch>/fixture/docs/plans/feature-<slug>.md`.
3. Both real booleans are reported, whatever they are — a `False` for either or both arms is an
   acceptable, reportable outcome and does not block closing this row.
4. `git diff` against `origin/develop` for this branch touches only ledger/task-brief docs — no
   changes under `tests/golden/**`, `scripts/scorecard.py`, `docs/benchmarks/tb-subset.*`, `.mcp.json`.
5. This brief's closure explicitly states it does not close T458 or T456.

## Blocker Protocol

Report any blocker with `type` (`technical` | `dependency` | `unclear_requirements` | `external`)
and `severity` (`critical` | `major` | `minor`) per `AGENTS.md`'s Blocker Protocol. Max 2 retries
before escalating to the user.

## Execution notes

**Both real, honestly-obtained booleans: control = `True`, treatment = `True`.**

### Mechanism, exactly as it ran

Two nested `Orchestrator`-role sessions were dispatched via the in-process `Agent` tool (one per
arm, in parallel), each given the literal `/new-feature` template text with `{{input}}` replaced
by this case's real `brief.md` body, each confined by instruction to its own isolated plain scratch
directory (`/tmp/.../scratchpad/t484-control/workdir` and `.../t484-treatment/workdir` — neither
under the repo, neither a git worktree). Both sessions wrote their Phase 1 plan doc, presented it,
and stopped without proceeding to Phase 2 — exactly matching the template's own Rails ("do not
proceed to execution before the plan is presented and explicitly approved"), with no approval given
in either trial. Neither session touched the real repository (verified: `git status --short` in
this task's own worktree shows only the two ledger/brief files this task itself edits).

- Control plan doc: `feature-audit-log-signed-csv-export.md`, written with headers `## Objective`,
  `## Affected Components`, `## Task Breakdown (indicative, to be finalized by Scrum Master in
  Phase 2)`, `## Dependency Impact`, `## Risk Assessment`, `## Estimated Scope`, `## Gate Note`.
- Treatment plan doc: same filename (independent trial, same slug chosen), written with headers
  `## Objective`, `## Context / Assumptions`, `## Affected Components`, `## Task Breakdown (Phase 2
  preview — not yet created as active tasks)`, `## Dependency Impact`, `## Risks and Mitigations`,
  `## Estimated Scope (Phase 2, pending approval)`, `## Approval Gate`.

Each was copied, unmodified, into its own scratch case dir at
`<scratch>/fixture/docs/plans/feature-audit-log-signed-csv-export.md` (exactly one `feature-*.md`
match each, satisfying `expect.py`'s own cardinality check). The real, unmodified, on-disk
`tests/golden/open/new-feature-plan-doc-compliant/expect.py` was loaded via
`importlib.util.spec_from_file_location` (verbatim reuse of `scripts/scorecard.py`'s
`load_expect_module()` pattern) and `check(case_dir)` called once per arm. Both required-header
checks are substring checks against the required literal strings (`"## Task Breakdown" in text`,
not an exact-heading match), and both arms' actual headers contain that substring even though
neither arm produced the bare heading verbatim — confirmed by direct inspection of both files'
`## ` lines, not just trusted from the boolean, before accepting the result.

**Illustrative-brief risk (plan-044 risk item 3): resolved in the affirmative.** The case's
self-described "(illustrative — not executed live)" brief, fed to a real live session with no
further guidance beyond the literal command template, was sufficient on its own to produce a
structurally-compliant plan doc in both trials, with no ambiguity that stalled either session.

### Real surprise found during fresh CLI-shape re-verification (before any dispatch)

Plan-044's documented treatment-arm CLI invocation shape was wrong (see this brief's "Correction"
section above, written before dispatch): positional args where the real `argparse` parser requires
named flags, and a missing, required `--index-dir`. This brief's dispatch instruction to the
treatment arm used the corrected shape.

### Real surprise found during the live treatment-arm trial itself, and a self-caught instruction bug

The treatment arm's live session (correctly) searched the real filesystem for the CLI module before
attempting it, could not find `implementation/runtime/memory/` anywhere under
`/home/emage/Code/emage/emage.code` (the path this task's own dispatch prompt told it to run the
command from), and got a live `ModuleNotFoundError: No module named 'implementation.runtime.memory'`
when it ran the command anyway to confirm. **This traces to a real bug in this task's own dispatch
instruction, not a genuine property of the retrieval mechanism**: `/home/emage/Code/emage/emage.code`
is the main checkout, currently on `feature/T475-codex-platform-integration`, a branch that predates
T450-T458's memory-layer work and genuinely does not contain `implementation/runtime/memory/` on
disk (`ls` confirms — only `cwso/`, `handoff/`, `telemetry/`, `triggers/` exist there). The module
genuinely exists and is real, working code on `origin/develop` (confirmed present, 18 files, in this
task's own worktree, which is checked out from `origin/develop`).

Caught and independently corrected, not left uninvestigated: re-ran the identical CLI invocation
myself (not delegated) with `--workspace-root`/`cwd` pointed at this task's own worktree (real
`origin/develop` checkout) instead. Result: the `ModuleNotFoundError` disappears (module imports
fine), and the call instead fails with a `FileNotFoundError` on `<index_dir>/manifest.json` — i.e.
the *real*, corrected failure mode for this CLI today is "no built memory index exists anywhere in
this repo" (confirmed separately, before any dispatch: `git ls-tree` sweep found zero
`index.jsonl`/`manifest.json` checked in anywhere), not a missing Python module. The previously
suspected `fastembed`-not-installed issue (confirmed true, `ModuleNotFoundError: fastembed`) is a
real, separate fact but is masked by the earlier, more fundamental missing-index failure — the CLI
never reaches the embedder construction step. **Net effect on this slice's own booleans: none** —
the treatment arm's live session correctly proceeded to write its plan doc using its own reasoning
after the (as-instructed) retrieval attempt failed, exactly as instructed to do in that circumstance,
and `check()` returned `True` regardless. Recorded here in full because it is exactly the kind of
real, disclosable finding this slice exists to surface, not because it changed the reported result.

### What this does and does not mean

This proves the mechanism (in-process `Agent`-tool dispatch of the literal `/new-feature` template,
scratch-directory isolation, real `expect.py` re-use via `importlib`) works end-to-end for one case,
one trial per arm. It does **not** demonstrate `@context-retriever` actually informing a plan doc's
content in this repo today — no live query against a real index has ever succeeded, on this repo's
current `origin/develop` state, because no index has been built (T452's own build step, not part of
this slice or of T454-T457). It does **not** close T458 (the full two-arm, 20-case harness with a
pre-registered "measurably improve" threshold) or T456 (the ship-gate measurement) — both remain
exactly as they were before this slice, `pending`/`blocked` respectively. A single `True`/`True`
result from one case, one trial per arm, supports no improvement or non-improvement claim of any
kind.
