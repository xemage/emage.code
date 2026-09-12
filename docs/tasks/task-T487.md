# Task T487 — Re-run T484's walking-skeleton trial now that a real vault index exists

**ID:** T487
**Owner (this slice, executed directly):** orchestrator — same reasoning as T484: the outer
dispatch mechanism is the in-process `Agent` tool, `devops-engineer`'s registered tool grant has
no `agent` tool, so the orchestrating role executes this bounded slice directly rather than
reassigning it.
**Status:** done
**Priority:** P1
**Depends on:** T486 (done — first real population of the knowledge vault; this task's entire
premise is that a real, populated index now exists to query against)
**Blocks:** Nothing structurally. **Does not close, advance, or scale T458 or T456.** Does not
touch T457 or T483.
**Created:** 2026-09-12
**Completed:** 2026-09-12
**Based on:** `docs/tasks/task-T484.md` (merged `origin/develop`, MR !288 — the first live
control/treatment trial, whose treatment arm's retrieval call failed outright because no index
existed anywhere in the repo); `docs/tasks/task-T485.md` (built the first real index against this
repo, found the vault itself genuinely empty); `docs/tasks/task-T486.md` (merged `origin/develop`
at `97dbd1d`, MR !291 — populated the vault with 11 real entries, 6 project-scope/5 general-scope,
and independently proved retrieval now returns real, relevant, non-empty results); `tests/golden/
open/new-feature-plan-doc-compliant/` (`case.yaml`, `brief.md`, `expect.py` — re-read fresh this
task, confirmed still accurate to T484's own description, unchanged); `implementation/knowledge/
commands/new-feature.md` (re-read fresh, unchanged since T484); the 11 real vault entries under
`implementation/knowledge/memory/{project,general}/` (re-read fresh this task to determine an
honest, non-rigged retrieval query).

## Objective

Repeat T484's exact mechanism once — one live control-arm trial and one live treatment-arm trial
of `/new-feature`'s literal template (`{{input}}` = this case's real `brief.md` text), each in its
own fresh isolated plain scratch directory — with exactly one real difference from T484: the
treatment arm's `@context-retriever` CLI call now has a real, populated index to query against
(the 11-entry, 25-chunk index T486 delivered) instead of failing on a missing index. Report both
real `expect.py` booleans and an honest assessment of whether the retrieved content observably
influenced the treatment arm's plan doc, without overclaiming any statistical finding from a
single trial.

## Pre-dispatch verification performed (before any trial ran)

1. Independently re-fetched `origin/develop` and confirmed `HEAD` = `97dbd1d` (matching T486's own
   closure record) before doing anything else.
2. Re-read `case.yaml`, `brief.md`, and `expect.py` fresh in this task's own worktree — all three
   unchanged from T484's description: `expect.py` requires exactly one `fixture/docs/plans/
   feature-*.md` file containing the four literal headers `## Objective`, `## Affected
   Components`, `## Task Breakdown`, `## Dependency Impact`.
3. Rebuilt the index myself, from scratch, in a fresh throwaway venv outside this repo (the exact
   `fastembed==0.8.0` precedent T485/T486 established; no repo dependency manifest touched):
   `python3 -m implementation.runtime.memory.build --project-id em-age/emage.code --own-repo-root
   . --general-repo-root . --output-dir <scratch>/t487-index-out` produced `wrote 25 chunks, 0
   rejections`, `manifest.json` = `{"chunk_count": 25, "entry_count": 11, "rejection_count": 0,
   "embedding_model": "nomic-ai/nomic-embed-text-v1.5", "embedding_dim": 768}` — byte-for-byte the
   same real content T486 delivered, independently reproduced rather than trusted from T486's own
   report.
4. Listed the real vault content directly (`ls implementation/knowledge/memory/{project,general}/`)
   before choosing a query, rather than picking a query first and hoping it would hit something.
   Chose: `"what branch and merge request workflow applies when starting implementation of a new
   feature in this repo"` — a real question a session about to write this case's Task Breakdown /
   Dependency Impact sections would plausibly ask (this repo enforces a strict branch-plus-MR flow
   for new feature work with no size/urgency exception), not a query engineered to force a hit on
   any specific entry. Ran it once against my own independently-built index to confirm the CLI
   itself worked end-to-end before handing the same query to the treatment arm — this is
   verification of tooling, not query selection by peeking at results and then rationalizing a
   choice after the fact; the query's rationale (above) was fixed before this confirmation run.

## Mechanism, exactly as it ran

Two nested `Orchestrator`-role sessions were dispatched via the in-process `Agent` tool (one per
arm, in parallel, `run_in_background: true`), each given the literal `/new-feature` template text
with `{{input}}` replaced by this case's real `brief.md` body ("Add a feature letting admins
export the audit log as a signed CSV."), each confined by instruction to its own isolated plain
scratch directory (`/tmp/.../scratchpad/t487-control/workdir` and `.../t487-treatment/workdir` —
neither under the repo, neither a git worktree, neither permitted to run git commands). Both
sessions wrote their Phase 1 plan doc, presented it, and stopped without proceeding to Phase 2 —
matching the template's own Rails, with no approval given in either trial. Neither session touched
the real repository.

The treatment arm's dispatch additionally gave it the real, corrected CLI invocation (same shape
T484 corrected and T486 re-confirmed: `query_text` positional, `--index-dir`/`--workspace-root`/
`--platform-root` named flags) pointed at this task's own independently-built index, with
instructions to run it once before writing the plan doc, read the real results, and use its own
judgment about whether the retrieved content was actually useful — not a forced instruction to
incorporate it regardless of relevance.

- Control plan doc: `feature-signed-audit-log-csv-export.md`, headers `## Objective`, `## Scope
  Summary`, `## Affected Components`, `## Task Breakdown`, `## Dependency Impact`, `## Risk
  Assessment`, `## Estimated Tasks`, `## Rails`.
- Treatment plan doc: `feature-audit-log-signed-csv-export.md` (independent trial, different slug
  chosen), headers `## Objective`, `## Affected Components`, `## Task Breakdown`, `## Dependency
  Impact`, `## Risk Assessment`, `## Estimated Tasks`.

Each was copied, unmodified, into its own scratch case dir at `<scratch>/fixture/docs/plans/
feature-*.md` (exactly one match each). The real, unmodified `tests/golden/open/
new-feature-plan-doc-compliant/expect.py` was loaded via `importlib.util.spec_from_file_location`
and `check(case_dir)` called once per arm, both directly inspected (grepped `## ` lines in both
files) before accepting the boolean result, not just trusted from the return value.

## Real results

**Retrieval query issued by the treatment arm (verbatim):** `"what branch and merge request
workflow applies when starting implementation of a new feature in this repo"`

**Real retrieval results returned (top 5, real scores, non-empty):**

1. `implementation/knowledge/memory/general/protected-branch-no-direct-commit-policy.md` — chunk
   "Recovery if it happens anyway" — score `0.806`
2. `implementation/knowledge/memory/general/protected-branch-no-direct-commit-policy.md` — chunk
   "The rule has no size or content exception" — score `0.771`
3. `implementation/knowledge/memory/general/agent-tool-grant-check-discipline.md` — chunk "What to
   do when the gap is real" — score `0.674`
4. `implementation/knowledge/memory/project/protected-golden-suite-paths.md` — chunk "What is not
   frozen" — score `0.598`
5. `implementation/knowledge/memory/project/adr-005-memory-layer-decisions.md` — chunk "Read-only-
   by-default, asserted in three independent places" — score `0.534`

Independently re-run by the orchestrator against its own separately-built index and confirmed to
match the treatment arm's own reported JSON exactly (same top hits, same scores) — not accepted on
the treatment arm's self-report alone.

**Both real, honestly-obtained `expect.py` booleans: control = `True`, treatment = `True`.**

**Did retrieval observably influence the treatment arm's output? Yes, in this one trial, in one
specific, inspectable way.** Direct diff of both arms' `## Dependency Impact` sections: the control
arm's Dependency Impact section (four bullets: admin-auth precondition, no new audit-capture
dependency, secrets/vault provisioning for the signing key, no cross-task contention) contains no
mention of branch or merge-request policy anywhere. The treatment arm's Dependency Impact section
contains the same categories of content plus one additional, clearly-attributable bullet, labeled
by the treatment arm itself as "confirmed via retrieval," restating specifics that appear in the
retrieved `protected-branch-no-direct-commit-policy.md` chunks essentially verbatim: the no-size/
urgency/doc-only exception, and — the more distinctive detail, unlikely to be volunteered from
generic reasoning alone — that this applies "equally to any orchestrator-authored ledger/checkpoint
edits tracking this feature's task state," a specific point present in the retrieved chunk's own
text ("This applies equally to changes an orchestrating role makes directly") and not present
anywhere in the control arm's plan doc or in the literal `/new-feature` template text either arm
was given. The three lower-ranked retrieval hits (agent-tool-grant discipline, frozen golden-suite
paths, ADR-005 read-only guarantee) were, by the treatment arm's own stated judgment, correctly
identified as off-topic for this feature and were not incorporated — a real instance of the
retrieved context being used selectively rather than dumped in wholesale.

## What this does and does not mean

**This is one trial per arm, on one golden case.** It supports no statistical claim about whether
retrieval improves outcomes in general, even though this specific trial shows a real, observable,
directly-inspected content difference attributable to the retrieval call (not merely "it
succeeded" — the actual retrieved text traces into the actual plan-doc content). A single
observed influence in one trial is not evidence that retrieval reliably helps, hurts, or is neutral
across cases; both arms passed `expect.py` regardless of whether retrieval was used, so this trial
also does not show retrieval was *necessary* for a compliant plan doc — only that it was, in this
one case, genuinely consulted and selectively used rather than ignored. This does not close T458
(the full two-arm, 20-case harness with a pre-registered "measurably improve" threshold) or T456
(the ship-gate measurement) — both remain exactly as they were before this task. It does not touch
T457 or T483.

## Constraints

- Never touch `feature/T475-codex-platform-integration`.
- Never edit anything under `tests/golden/**` — `expect.py` is read/imported only.
- Never edit `scripts/scorecard.py` or `docs/benchmarks/tb-subset.json`/`.md`.
- No new paid/metered API usage beyond ordinary interactive-session dispatch.
- Do not install new dependencies into this repo's own dependency manifests — throwaway-venv only.
- This task does not touch T456, T457, T458, or T483.

## Expected Outputs

1. Two real, on-disk scratch runs (outside the repo, in plain temp directories — not committed).
2. Two real boolean `check()` results (control, treatment).
3. This brief's own results, filled in with what actually happened.
4. `docs/tasks/active-tasks.md` / `completed-tasks.md` updated to close this row.

## Acceptance Criteria

1. Both arms' live sessions actually ran via the in-process `Agent` tool (not simulated).
2. Both `check()` calls used the real, unmodified `expect.py`, loaded via
   `importlib.util.spec_from_file_location`.
3. Both real booleans reported, whatever they are.
4. `git diff` against `origin/develop` for this branch touches only ledger/task-brief docs.
5. This brief's closure explicitly states it does not close T458 or T456, and does not overclaim a
   general "retrieval helps" finding from n=1.

## Blocker Protocol

Report any blocker with `type` (`technical` | `dependency` | `unclear_requirements` | `external`)
and `severity` (`critical` | `major` | `minor`) per `AGENTS.md`'s Blocker Protocol. Max 2 retries
before escalating to the user.

## Self-referential ledger-defect sweep

Re-derived the live, current top-tier component id list directly (`python3 implementation/
scripts/check-maturity.py --root implementation --verbose`, 31 stable ids across agent/instruction/
skill categories) and swept this brief's own text and the ledger closure note against it before
pushing — zero bare-token hits. Also swept against the live held-out case-ID list (`ls tests/
golden/held-out/`) — zero hits. This brief deliberately describes the branch-and-merge-request
policy and the review-verdict/reporting conventions in plain prose rather than by their hyphenated
component ids or exact file paths, following the same precedent T486 itself established for the
same reason.
