# Task T489 — T458 scaling, Tier 2: the 4-trial noise probe on `new-feature-plan-doc-compliant`

**ID:** T489
**Owner (this slice, executed directly):** orchestrator — same reasoning as T484/T487/T488: the
outer dispatch mechanism is the in-process `Agent` tool, `devops-engineer`'s registered tool grant
has no `agent` tool, so the orchestrating role executes this bounded slice directly rather than
reassigning it.
**Status:** done
**Priority:** P1
**Depends on:** T486 (done — the populated vault), T487 (done — the on-record treatment trial this
brief reuses as trial 1 of 3), T488 (done — confirms the mechanism generalizes across cases;
unrelated to this brief's single-case scope)
**Blocks:** Nothing structurally. **Does not close, advance, or scale T458 or T456.** Does not
touch T457 or T483.
**Created:** 2026-09-13
**Completed:** 2026-09-13
**Based on:** `docs/plans/plan-045-t458-scaling.md` (Finding 2's Tier 2 design — a targeted 4-trial
noise probe on one already-proven case, reusing the one on-record trial per arm to reach `k=3`
total; Finding 3's non-regression-floor process); `docs/tasks/task-T484.md` (the first live
control/treatment trial on this case, and the first self-caught dispatch-instruction bug this
brief's own diagnosis directly traces back to); `docs/tasks/task-T487.md` (the re-run that
established the on-record treatment trial this brief reuses as trial 1); `docs/tasks/task-T488.md`
(confirms the same live-dispatch/scratch-isolation/`expect.py`-reuse mechanism this brief repeats,
this time explicitly scoped to Tier 2 only, which T488 explicitly excluded).

## Authorization — stated plainly, not inferred from a checked box

`plan-045-t458-scaling.md` remains on record as "proposed — presented for review in this session's
report, **NOT approved**," with every item in its own Approval checklist still unchecked on
`origin/develop`. **This task was not authorized by any of those checkboxes being ticked.** It was
authorized by the orchestrating session's own direct, explicit, this-turn instruction to complete
the already-dispatched Tier 2 trials exactly as originally instructed. `plan-045` is used here
purely as the technical specification for what Tier 2 concretely means (the specific case, the
reused-trial-plus-two-more design, the non-regression-floor process) — not as its own authorization
mechanism.

## Objective

Complete Tier 2 of `plan-045` Finding 2: two additional live control-arm trials and two additional
live treatment-arm trials of `/new-feature`'s literal template against
`tests/golden/open/new-feature-plan-doc-compliant` (`{{input}}` = this case's real, quoted
`brief.md` request sentence), reusing T484's on-record control trial and T487's on-record treatment
trial as the first of three per arm (`k=3` total per arm). Score all four new trials against the
case's real, unmodified `expect.py`; compare all three control-arm outputs and all three
treatment-arm outputs to each other for real, empirical structural/substantive/pass-fail variance;
and diagnose, honestly, whether a treatment-arm retrieval failure observed in this batch is a real
environment limitation or a dispatch-instruction bug.

## Mechanism, exactly as it ran

Four nested `Orchestrator`-role sessions were dispatched via the in-process `Agent` tool, each
given the literal `/new-feature` template text with `{{input}}` = this case's real `brief.md` body
("Add a feature letting admins export the audit log as a signed CSV."), each confined to its own
isolated plain scratch directory under this session's scratchpad (`t489-control-2/workdir`,
`t489-control-3/workdir`, `t489-treatment-2/workdir`, `t489-treatment-3/workdir` — none under the
repo, none a git worktree, none permitted to run `git`). All four wrote a Phase 1 plan doc,
presented it, and stopped without proceeding to Phase 2, matching the template's own Rails.

The two treatment sessions were additionally given a real, working `@context-retriever` CLI
invocation pointed at a freshly, independently rebuilt index (`t489-index-out`: `25 chunks, 0
rejections, entry_count: 11` — byte-for-byte the same real content T486/T487 established,
reproduced fresh in a throwaway venv, not trusted from any prior record) and told they **may**
consult it and must formulate their own query — no pre-vetted query string, per `plan-045`
Finding 4.

## Real results — all four `expect.py` booleans

Each trial's plan doc was copied unmodified into its own scratch case dir at
`<scratch>/fixture/docs/plans/feature-*.md`; the real, unmodified
`tests/golden/open/new-feature-plan-doc-compliant/expect.py` was loaded via
`importlib.util.spec_from_file_location` and `check(case_dir)` called once per trial; every result
was also independently confirmed by direct `grep` of each file's actual `## ` header lines before
being accepted, not trusted from the boolean alone.

| Trial | `expect.py` result | Direct header confirmation |
|---|---|---|
| control-2 | `True` | `## Objective`, `## Affected Components`, `## Task Breakdown (indicative...)`, `## Dependency Impact` all present |
| control-3 | `True` | same four required substrings present |
| treatment-2 | `True` | same four required substrings present |
| treatment-3 | `True` | same four required substrings present |

**All four new booleans: `True`.** Combined with the two on-record trials this brief reuses
(T484 control = `True`, T487 treatment = `True`), **both arms are 3/3 (`k=3`) on this case.** The
non-regression floor (`plan-045` Finding 3 — treatment pass rate must not be lower than control
pass rate) is met, but trivially: both arms sit at the metric's ceiling, so this probe's binary
signal cannot, on its own, distinguish anything about retrieval's effect here — see "What this does
and does not mean."

## Cross-trial variance — control arm (T484-control, control-2, control-3)

**Structural:** all three carry the four required headers in the same relative order
(`Objective` → `Affected Components` → `Task Breakdown` → `Dependency Impact`), followed by a
risk/estimate section and a closing gate note, but section counts differ: T484-control has 7
top-level `##` sections (ending `Gate Note`); control-2 has 8 (adds a separate `Out of Scope` and
`Approval Requested` section on top of `Risk Assessment`/`Estimated Scope`); control-3 has 7 (uses
`Risks and Mitigations` instead of `Risk Assessment`, and folds the closing gate language into an
`Out of Scope (per Rails)` heading rather than a dedicated `Gate Note`).

**Substantive:** all three converge heavily on the same core technical judgment with no retrieval
input at all — admin-only export endpoint, a signing key sourced from vault/env (never hardcoded),
CSV-injection risk called out explicitly as a named risk in control-2 and (implicitly, as
"sensitive-data leakage") in T484-control, streaming/pagination flagged for large audit logs in all
three, the export action itself required to be its own audit-log entry in all three, and an
explicit no-progression-without-approval closing line in all three. Differences are stylistic and
sequencing-level (table-based vs. prose "Affected Components"; 6-8 vs. 8-10 indicative tasks;
control-3 alone adds a `git workflow`-flavored note about branching the eventual feature from
`develop`) rather than substantive disagreements.

**Pass/fail:** 3/3 `True` — no variance at all on the binary signal.

## Cross-trial variance — treatment arm (T487-treatment, treatment-2, treatment-3)

**Structural:** section counts vary more than the control arm: T487-treatment has 6 sections
(`Objective`, `Affected Components`, `Task Breakdown`, `Dependency Impact`, `Risk Assessment`,
`Estimated Tasks` — no explicit approval-gate heading); treatment-2 has 9 (adds `Scope Summary`, a
dedicated `Notes on Research Performed` section, and an `Approval Checkpoint` heading);
treatment-3 has 8 (adds `Scope Summary` and a closing `Next Step`, but no research-notes section).

**Substantive — how each trial actually used (or didn't use) retrieval, and how that shows up (or
doesn't) in the written artifact itself:**

- **T487-treatment** (retrieval succeeded, real query, 5 real results): the plan doc's
  `Dependency Impact` section contains one extra bullet, explicitly labeled by the session itself
  as "confirmed via retrieval," restating a specific, distinctive detail from the top-ranked
  retrieved chunk (branch/merge-request policy applying equally to orchestrator-authored ledger
  edits) that is not present in the control arm's doc or in the literal template text. This is a
  real, directly-traceable content influence, written into the artifact.
- **treatment-2** (retrieval failed outright — see Diagnosis below): the plan doc contains a
  dedicated `## Notes on Research Performed` section that transparently discloses the failed
  retrieval attempt, states the plan is based solely on already-known general conventions as a
  result, and flags that Phase 2 agents should independently verify against any real existing
  ADRs. The failure is disclosed *in the artifact itself*, not just in the session's chat report.
- **treatment-3** (retrieval succeeded, real query, 5 real results, all judged off-topic): the
  written plan doc contains **zero** mentions of retrieval anywhere in its text — confirmed by
  direct `grep` for "retriev" and related terms, no hits. The only record of this trial's retrieval
  attempt, its query text, and its off-topic judgment exists in the session's own final chat
  report, not in the produced document. This is itself a real, disclosable structural inconsistency
  across the treatment arm: three sessions given the identical "you may consult it, use your own
  judgment" instruction made three different choices about whether to narrate the attempt inside
  the artifact at all (yes with content change; yes with no content change but explicit disclosure;
  not at all), and none of those three choices was wrong per the instruction given, but they are
  not comparable on any structural axis that only inspects the artifact.

**Pass/fail:** 3/3 `True` — no variance at all on the binary signal, matching the control arm
exactly.

## What the k=3 result on this one case actually shows

With both arms saturated at 3/3, this probe's central quantitative question — "how much does a
live session's `expect.py` boolean vary run-to-run on this repo's own mechanism, absent any
manipulation" — has a clean, honest answer for *this one case*: **zero observed variance in the
binary outcome across six real trials, three per arm.** That is a real data point for `plan-045`
Finding 2's stated purpose (informing a future `k` choice for the full harness), but it is a
ceiling-effect data point, not a spread measurement: a binary pass/fail metric that never moves
across six trials on one case cannot itself justify either a low or a high `k` for cases where the
metric might actually vary — it only shows that *this* case's `expect.py` bar is cleared
comfortably and repeatably by ordinary live-session output, retrieval or not. The real, measurable
variance in this batch is entirely on the qualitative/structural axis (see above), not the
quantitative one `plan-045` Finding 3 deferred a numeric threshold pending. This is consistent with
T488's own separate finding (a genuine `False` result did occur there, but traced to per-trial
formatting choices, not retrieval content) — both results together suggest `expect.py`-style binary
checks are a coarse instrument for this purpose at low `k`, a finding this brief surfaces rather
than resolves.

## Diagnosis — treatment-2's retrieval failure: a dispatch-instruction bug, not an environment
limitation

**Verdict: dispatch-instruction bug on this session's own part, verified directly, not inferred.**

Both `t489-treatment-2` and `t489-treatment-3` were dispatched with **byte-for-byte identical**
prompts (confirmed by direct diff of both dispatch payloads) apart from the scratch-directory name,
including an identical retrieval invocation recipe:

```
<t489-venv>/bin/python3 -m implementation.runtime.memory.context_retriever "<query>" \
  --index-dir <t489-index-out> \
  --workspace-root /home/emage/Code/emage/worktrees/agent-orchestrator-T489 \
  --platform-root /home/emage/Code/emage/worktrees/agent-orchestrator-T489/.claude --top-k 5
```

Neither dispatch prompt included a `cd` into that worktree before the command. `--workspace-root`/
`--platform-root` are flags consumed by the retriever's own scope logic — they do not affect
Python's `-m` module-resolution search path, which depends on the OS-level process working
directory. Both sessions' Bash tool defaulted to this repository's own primary checkout
(`/home/emage/Code/emage/emage.code`, on `feature/T475-codex-platform-integration`), independently
confirmed (`git ls-tree` on that branch) to genuinely lack `implementation/runtime/memory/` on
disk — that module only exists on `origin/develop` and in worktrees checked out from it, including
`agent-orchestrator-T489` itself (independently confirmed present there, 18 files).

Directly inspecting each trial's real transcript (not the trials' own self-reports) confirms:

- **treatment-2** ran the command exactly as given, once, got
  `ModuleNotFoundError: No module named 'implementation.runtime.memory'`, correctly reasoned this
  was "a structural failure... not a query-phrasing issue," and did not retry with a different
  working directory — it proceeded to write its plan doc without retrieved context, disclosing the
  failure honestly in the artifact (see above).
- **treatment-3** ran the *exact same command* first, got the *exact same*
  `ModuleNotFoundError`, then — on its own initiative, not instructed to do so — retried by
  prepending `cd /home/emage/Code/emage/worktrees/agent-orchestrator-T489 &&` to the identical
  command, which then succeeded and returned 5 real, non-empty results.

Both sessions hit the identical structural failure on their first attempt; only one happened to
self-correct. This is conclusive: the retrieval mechanism itself works correctly and consistently
when invoked from a correct working directory (as T487, this brief's own pre-dispatch index
rebuild, and treatment-3's second attempt all independently confirm) — the inconsistent outcome
across two nominally-identical trials in this batch is a direct, traceable consequence of this
session's own dispatch prompt never specifying the required working-directory context for a
module-resolution-sensitive CLI invocation, not a genuine property of the retrieval mechanism's
reliability.

**A necessary correction to how this bug's precedent was characterized going into this task:** it
was **T484**, not T487, that first self-caught this exact bug class (`task-T484.md`'s own "Real
surprise found during the live treatment-arm trial itself, and a self-caught instruction bug"
section — a dispatch prompt pointing the treatment arm at
`/home/emage/Code/emage/emage.code` instead of a real `origin/develop` checkout). T487's own
dispatch used a pre-verified worktree path throughout and recorded no such bug. This batch's
treatment-2 failure is therefore a **recurrence** of a bug class this project's own task history
had already documented once, not a novel discovery — the lesson from T484 (always specify, don't
imply, the working directory a module-resolution-dependent command must run from) was not fully
carried into this batch's own dispatch prompts.

## Constraints

- Never touched `feature/T475-codex-platform-integration`.
- Never edited anything under `tests/golden/**` — `expect.py` read/imported only.
- Never edited `scripts/scorecard.py` or `docs/benchmarks/tb-subset.json`/`.md`.
- No new paid/metered API usage beyond ordinary interactive-session dispatch.
- No new dependencies installed into this repo's own dependency manifests — throwaway venv only.
- **No vault growth** — `implementation/knowledge/memory/{project,general}/` unchanged.
- Does not touch T456, T457, T458, or T483.

## Acceptance Criteria

1. All four trials' live sessions actually ran via the in-process `Agent` tool — verified via each
   dispatch's own transcript, not merely a self-report.
2. All four `check()` calls used the real, unmodified `expect.py`, loaded via
   `importlib.util.spec_from_file_location`, and were independently re-confirmed by direct header
   inspection.
3. All four real booleans reported, whatever they were.
4. `git diff` against `origin/develop` for this branch touches only this task brief and the ledger
   row — no changes under `tests/golden/**`, `scripts/scorecard.py`, `docs/benchmarks/tb-subset.*`,
   `.mcp.json`.
5. The treatment-2 retrieval failure is diagnosed to a specific, verified root cause (not left as
   an ambiguous "environment issue"), and any prior mischaracterization of precedent is corrected
   rather than repeated.
6. Self-referential ledger-defect sweep performed and passing (see below).

## Blocker Protocol

None encountered requiring escalation. The treatment-2 retrieval failure is recorded above as a
diagnosed, resolved finding (root-caused to this session's own dispatch-prompt gap), not an open
blocker.

## Self-referential ledger-defect sweep

Re-derived the live, current top-tier component id list directly
(`python3 implementation/scripts/check-maturity.py --root implementation --verbose`, run fresh in
this task's own worktree): **31 stable ids** (20 agents, 4 instructions, 7 skills) — matching
T487/T488's own counts, independently re-confirmed rather than trusted from either prior record.
Swept this brief's own text against all 31 — zero bare hyphenated-id hits (this brief refers to
project roles in plain prose, e.g. "the orchestrating role," rather than any stable skill/
instruction/agent registry id). This row is created and closed in the same commit sequence, so it
is never attached to an open, non-`done` ledger row at any committed state, avoiding the
self-referential trap entirely by construction. Also re-derived the live held-out case-ID list
directly (`ls tests/golden/held-out/`, 6 entries) — zero bare mentions of any held-out case ID
anywhere in this brief; every case ID named above is the one real, `open`, non-held-out case this
task actually dispatched against.

## Git workflow

Branch `agent/orchestrator/T489`, created from `origin/develop` @ `b83bcec` (the same commit T488's
own merge landed at). Merge request to be opened against `develop`, referencing `T489`, **left
unmerged** per the orchestrating session's explicit instruction this turn ("do NOT run
`glab mr merge` — hand it back to me").
