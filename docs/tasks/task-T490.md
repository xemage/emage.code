# Task T490 — T458 scaling: k≥3 escalation on the two brittle T488 cases, plus a repeat of the clear-influence case

**ID:** T490
**Owner (this slice, executed directly):** orchestrator — same reasoning as T484/T487/T488/T489: the
outer dispatch mechanism is the in-process `Agent` tool, `devops-engineer`'s registered tool grant
has no `agent` tool, so the orchestrating role executes this bounded slice directly rather than
reassigning it.
**Status:** done
**Priority:** P1
**Depends on:** T488 (done — the on-record trial-1 data for all three cases this brief adds 2 more
trials per arm to), T489 (done — the k=3 mechanism and disclosure-pattern rubric this brief reuses
unchanged)
**Blocks:** Nothing structurally. **Does not close, advance, or scale T458 or T456.** Does not
touch T457 or T483.
**Created:** 2026-09-13
**Completed:** 2026-09-13
**Based on:** `docs/plans/plan-047-t458-k-threshold-resolution.md` §2 (the escalation rule: raise a
case to `k≥3` only when its `k=1` result is ambiguous, then classify — same-arm-same-reason
recurrence is a real finding, fluctuation confirms a formatting coin-flip) and §5 ("the single most
valuable next experiment this document identifies" — `k≥3` on `code-review-fail-blocker-details`
and `security-audit-coverage-consistency`, plus a repeat of `plan-required-sections-compliant`'s
clear-influence trial); `docs/tasks/task-T488.md` (the exact 5-case `k=1` results and diagnoses this
brief adds 2 trials per arm to, per case, reaching `k=3`); `docs/tasks/task-T489.md` (the k=3
mechanism — reuse the on-record trial as trial 1 of 3 — the `cd`-before-module-resolution dispatch
fix, and the five-category qualitative-influence rubric this brief applies unchanged, per
`plan-047` §3.2).

## Authorization — stated plainly, not inferred from a checked box

`plan-047-t458-k-threshold-resolution.md` is a decision/design document only, explicit in its own
Status line that it "does not dispatch... any new live trial" and its own closing section that it
"does not authorize any live trial... that remains a separate dispatch decision, not made here."
**This task was not authorized by that document, nor by any checkbox in `plan-045` or `plan-047`.**
It was authorized by the orchestrating session's own direct, explicit, this-turn instruction: run 2
additional trials per arm on each of the 3 cases plan-047 §5 names, reusing each case's T488
on-record trial as trial 1 of 3, reaching `k=3` per arm per case (12 new live trials total).
`plan-047` is used here purely as the technical specification for *which* cases and *what*
classification rule to apply — not as its own authorization mechanism.

## Objective

For `code-review-fail-blocker-details`, `security-audit-coverage-consistency`, and
`plan-required-sections-compliant`: run 2 additional live control-arm trials and 2 additional live
treatment-arm trials of each case's own command template (`{{input}}` = the case's real, quoted
`brief.md` request sentence only, per T488's established input-substitution rule, applied uniformly
across all three cases), each in its own fresh, isolated, plain scratch directory, dispatched via
the in-process `Agent` tool as the role each command's own frontmatter declares. Reuse each case's
T488 on-record trial as trial 1 of 3 per arm. Score all 12 new trials against each case's real,
unmodified `expect.py`. For the two brittle cases, apply plan-047 §2's classification rule
(same-reason recurrence vs. fluctuation). For the clear-influence case, check whether that influence
reproduces under repetition, applying plan-047 §3.2's five-category qualitative rubric to all three
treatment trials.

## Pre-dispatch verification performed (before any trial ran)

1. Independently re-fetched `origin/develop` and confirmed `HEAD` = `823f2a55a19c217b1f265ec6fe44d6cb83d936cd`
   (`Merge branch 'plan-047-t458-k-threshold' into 'develop'`), matching the orchestrating session's
   stated expectation.
2. Re-read `docs/tasks/active-tasks.md` fresh, from `origin/develop` (not from a stale local
   checkout): unchanged since T489 closed (`T456` blocked, `T457` pending, `T458` pending, `T483`
   pending). Confirmed the real max existing task file on `origin/develop` is `task-T489.md` via a
   direct `git ls-tree` sweep (not a naive substring grep, which T488 already documented produces
   false positives from `RUN_ID` timestamps) — **T490 is the correct next sequential ID.**
3. Confirmed, via `git merge-base --is-ancestor`, that `plan-047`'s own authoring commit and both of
   T488/T489's closure commits are genuine ancestors of `origin/develop` — this session's interactive
   working branch (`feature/T475-codex-platform-integration`) is 176 commits behind and was not
   touched; this task was authored in a fresh worktree (`agent-orchestrator-T490`, branched from
   `origin/develop`) confirmed clean (`git status --short` empty, `git diff origin/develop --stat`
   empty) before any work began.
4. Read all 3 real `case.yaml`/`brief.md`/`expect.py` files fresh, in full, from this task's own
   worktree — all three confirmed to match `task-T488.md`'s own characterization exactly (same
   quoted request sentences, same checker logic, same field/format contracts).
5. Read all 3 real command templates (`plan.md`, `code-review.md`, `security-audit.md`) in full,
   including frontmatter, confirming each `agent:` role: `/plan` → `orchestrator`; `/code-review` →
   `tech-lead`; `/security-audit` → `security-engineer` — matching T488's own confirmed roles.
6. Rebuilt the knowledge-vault index myself, from scratch, in a fresh throwaway venv outside the
   repo (`fastembed==0.8.0`, the exact T485-T489 precedent; no repo dependency manifest touched).
   Result independently reproduced T486-T489's own manifest byte-for-byte: `chunk_count: 25`,
   `entry_count: 11`, `rejection_count: 0`, `embedding_model: nomic-ai/nomic-embed-text-v1.5`. The
   vault itself was independently confirmed unchanged at 11 files (5 general + 6 project) before and
   after this task — **no vault growth performed**, per plan-045 Finding 5's constraint, carried
   forward unchanged by plan-047.
7. Ran a real sanity retrieval query against the fresh index, from inside the correct worktree with
   an explicit `cd` first, and confirmed non-empty, relevant results before any dispatch — directly
   addressing T489's own diagnosed dispatch-instruction bug (a missing `cd` before a
   module-resolution-sensitive CLI invocation) by verifying the fix myself, before dispatch, not
   after a failure. Every treatment-arm dispatch prompt in this task explicitly included the `cd`
   into the correct worktree as the first command in the retrieval invocation shape given to the
   nested session.
8. Confirmed the worktree (`/home/emage/Code/emage/worktrees/agent-orchestrator-T490`, branch
   `agent/orchestrator/T490`, from `origin/develop` @ `823f2a5`) stayed clean (`git status --short`
   empty) after the index build — the build step touches no repo file, confirmed directly.

## Mechanism, exactly as it ran (all 12 trials genuinely live, dispatched in this session)

Twelve nested `Agent`-tool sessions were dispatched in three batches of four (one batch per case,
each batch run as four parallel calls in a single message, per the orchestrating session's own
pacing instruction to avoid an unbroken 12-trial burst). Each trial was given: (a) the case's own
real command template text verbatim, with `{{input}}` substituted per T488's rule (only the case's
quoted `brief.md` request sentence, uniformly, never an unquoted answer-revealing continuation); (b)
a sandbox instruction confining it to its own absolute, plain scratch directory (never a git
worktree, never under the repo, never permitted to run `git`); (c) for treatment arms only, the real,
corrected `@context-retriever` CLI invocation shape with an explicit `cd` into the correct worktree
as the first token of the command, an explicit instruction that it must formulate its own query and
decide for itself whether to run it at all, and an explicit instruction to report verbatim whether
it queried, its exact query text, and what it did with the results. No treatment arm was given a
pre-vetted query string or any hint about vault contents. Each arm's role matched its command's own
frontmatter. Each arm's real output file was copied, unmodified, into its own case-shaped fixture
directory at the exact relative path its case's real `expect.py` expects (`fixture/review.md`,
`fixture/audit.md`, `fixture/docs/plans/*-plan.md`). The real, unmodified `expect.py` for each case
was loaded via `importlib.util.spec_from_file_location` and `check(case_dir)` called once per trial.
Every reported boolean was independently re-derived by direct regex/field inspection of each real
output file (not accepted on the trial's own self-report or the boolean alone).

Zero dispatch-prompt module-resolution failures occurred in this batch — the `cd`-first fix
diagnosed in `task-T489.md` held across all 4 treatment-arm retrieval invocations that queried.

## Real results — `code-review-fail-blocker-details` (`/code-review`, `tech-lead`)

| Trial | Result | Root cause (directly inspected, not self-report alone) |
|---|---|---|
| control-1 (T488, on record) | **True** | Literal `**Status**: FAIL`, non-empty `**Blocker IDs**:`, standalone `**Owner**:` field, "retry" present — all matched. |
| control-2 (new) | **False** | Verdict itself was **`CONDITIONAL_PASS`, not `FAIL`** — a different severity judgment entirely, not a field-formatting issue. The checker requires literal `FAIL` and short-circuits immediately on any other status. |
| control-3 (new) | **False** | `Status: FAIL` and non-empty `Blocker IDs` both present, but every blocker's owner was written as inline prose inside the bullet ("`Owner: Backend Engineer`") rather than a standalone bolded `**Owner**:` field — the literal field the checker's regex requires never appears anywhere in the document. |
| treatment-1 (T488, on record) | **False** | Owner presented as a markdown table column header ("`\| ... \| Owner \| Retry Guidance \|`"), not a bolded inline field. |
| treatment-2 (new) | **True** | Literal `**Status**: FAIL`, non-empty `**Blocker IDs**:`, standalone `**Owner**:` field, "retry" present — all matched. |
| treatment-3 (new) | **False** | Same inline-prose-`Owner`-inside-bullet pattern as control-3 (`"— Owner: Backend Engineer —"` inside each blocker line, never a standalone bolded field). |

**Control: 1/3. Treatment: 1/3.**

**Classification (plan-047 §2's own rule, applied honestly):** pass/fail **fluctuates** across
trials in *both* arms (control: True, False, False; treatment: False, True, False) — this is not
the same arm failing for the same diagnosed reason across all `k=3` trials. Per plan-047 §2 item 2's
own text, this "confirms a formatting coin-flip rather than a persistent effect." A genuinely new
detail this batch surfaces beyond T488's original diagnosis: the coin-flip is not limited to a
single formatting axis (bolded field vs. table column vs. inline prose for `Owner`) — one of the
four new failures (control-2) is a **different verdict-severity judgment entirely**
(`CONDITIONAL_PASS` vs. `FAIL`), a coarser and more consequential source of trial-to-trial noise than
any single field's literal formatting. Both arms are equally exposed to both failure modes; nothing
in this batch traces either failure mode to retrieval content specifically. Non-regression floor
(treatment pass rate not lower than control): **met** (1/3 vs. 1/3, equal).

## Real results — `security-audit-coverage-consistency` (`/security-audit`, `security-engineer`)

| Trial | Result | Root cause (directly inspected) |
|---|---|---|
| control-1 (T488, on record) | **True** | Declared coverage matched actual matrix row count. |
| control-2 (new) | **True** | Declared `8/10`; matrix contained exactly 8 distinct `A0X` rows (`A08`, `A10` correctly excluded as out of scope, with an explicit rationale). |
| control-3 (new) | **True** | Declared `9/10`; matrix contained exactly 9 distinct `A0X` rows (`A10` excluded). |
| treatment-1 (T488, on record) | **False** | Coverage field was written as `"**Declared OWASP coverage: 9/10 categories assessed**"` — one bolded sentence, not the template's literal `**OWASP coverage**: 9/10` field-label pattern. The checker's field regex found no match at all (not a row-count mismatch — a total format miss). |
| treatment-2 (new) | **False** | Field format matched correctly (`**OWASP coverage**: 9/10`), but the audit's main matrix **explicitly included a 10th row for `A10`** (marked "Not assessed" / "Out of scope") in addition to the 9 assessed rows — the checker counts any `A0X`/`A10` row present regardless of its "assessed" annotation, so actual rows = 10 against a declared 9. A genuinely new, distinct root cause from trial 1: not a missing-field-format problem, but a self-consistency slip caused by trying to be maximally transparent (listing all 10 categories with a status for each, including the explicitly out-of-scope one). |
| treatment-3 (new) | **True** | Declared `9/10`; matrix contained exactly 9 distinct rows, no extra row. |

**Control: 3/3. Treatment: 1/3.**

**Classification (plan-047 §2's own rule, applied honestly — and reported as neither of the rule's
two named outcomes fits cleanly):** this is **not** a clean "same arm fails for the same diagnosed
reason across all `k=3` trials" (the two treatment failures are two different, independently
diagnosed root causes: a total field-format miss in trial 1, a matrix-row self-consistency slip in
trial 2), but it is also **not** a clean "pass/fail fluctuates" coin-flip result in the way case 1
above is, because the *control* arm never failed at all in this batch (3/3) while the *treatment*
arm failed in 2 of 3 trials. The honest, un-forced reading: in this small sample, the treatment arm
carried a real, elevated failure rate (2/3) that the control arm did not exhibit (0/3), but the two
treatment failures do not share a mechanism, so this is not evidence of one specific, stable,
reproducible bug — it is evidence that this case's checker has at least two independent, unrelated
ways to be tripped by formatting/self-consistency choices, and this small sample happened to surface
both of them exclusively in the treatment arm. Neither failure traces to the substantive content
retrieval contributed (both treatment-1 and treatment-2's own self-reports credit retrieval only
with confirming already-known conventions, not with introducing the specific field/row-count
choices that failed). Non-regression floor: **not met** (1/3 vs. 3/3).

## Real results — `plan-required-sections-compliant` (`/plan`, `orchestrator`)

| Trial | Result |
|---|---|
| control-1 (T488, on record) | **True** |
| control-2 (new) | **True** |
| control-3 (new) | **True** |
| treatment-1 (T488, on record) | **True** |
| treatment-2 (new) | **True** |
| treatment-3 (new) | **True** |

**Control: 3/3. Treatment: 3/3.** All six real trials passed; direct inspection confirmed all six
fixture documents contain exactly the 6 required `##` headers, in order, with a fenced ` ```mermaid ` 
block under Dependency Graph, in all six cases with no extra or missing header. Non-regression
floor: **met** (3/3 vs. 3/3, equal) — but, per T489's own precedent for the other ceiling-effect
case, **trivially**: this is a second real ceiling-effect data point on a second distinct case,
confirming T489's finding generalizes beyond the one case it was originally observed on.

**Reproduction check — does T488's clear, traceable retrieval influence reproduce?** **No.** T488's
trial 1 treatment session added a "Process Notes (from repository conventions)" section containing
three claims each traceable to a distinct retrieved chunk (branch/MR-flow policy, "reviewers do not
modify what they review," the two-retry-then-escalate rule) — plan-047 §3.2's category 3 ("Retrieval
used, traceable positive influence on the artifact"). Both new treatment trials queried the
retrieval tool (once each, real, non-empty, top-5 results), but **both independently judged every
result off-topic for a background-sync/reconciliation-job plan** (the hits were general
harness-process conventions — golden-suite test-design philosophy, protected-branch policy,
nested-agent-dispatch tool-grant checks, the two-retry blocker rule, an unrelated ADR about
embedding-model cost — none substantively about sync-job design, conflict resolution, or
idempotency) and **left zero trace of the retrieval attempt anywhere in the produced artifact**,
confirmed by direct `grep` for retrieval-related terms in both files (the only "vault" hits found
are unrelated generic-secrets-management language, not retrieval-mechanism references). This is
plan-047 §3.2's **category 5** ("Retrieval attempted... with no disclosure of the attempt anywhere
in the artifact") for both new trials — the same category `task-T489.md` first identified on an
entirely different case. **Conclusion:** T488's clear-influence result on this case was a
**one-off**, tied to that specific trial's query happening to retrieve genuinely on-topic vault
content (the vault's process/governance entries happened to be relevant to a sync-job *planning
process* question in a way they were not relevant to a sync-job *technical design* question) — it
did not reproduce under 2 further trials on the same case with the same command. This adds a second,
independent instance of category 5 to this project's real evidence base (alongside T489's own), while
category 3 (the original clear-influence case) now looks query/content-dependent rather than a
repeatable property of this case.

## Retrieval query texts used in this batch (verbatim, agent-formulated, not hinted)

1. (code-review treatment-2) "code review verdict format conventions for payment webhook handlers, blocker and retry attempt guidance for FAIL verdicts"
2. (code-review treatment-3) "tech lead code review verdict format, blocker ID naming, and retry attempt guidance conventions for a FAIL gate status"
3. (security-audit treatment-2) "security audit report format, OWASP coverage matrix, and VERDICT block conventions for security engineer agent"
4. (security-audit treatment-3) "security audit report and VERDICT format conventions for internal admin CLI authentication and authorization review"
5. (plan treatment-2) "conventions for planning a background sync job that reconciles local state with a remote service: task decomposition granularity, agent assignment for backend/qa/devops, and idempotency or conflict-resolution risk considerations"
6. (plan treatment-3) "conventions for planning a background sync or reconciliation job that compares local state against a remote inventory service, including idempotency, conflict resolution, task decomposition, and risk assessment practices"

All 6 top-hit sets were independently re-derivable against this task's own freshly-built index
(confirmed by the orchestrator inspecting each treatment trial's disclosed raw results directly,
not accepted on self-report alone) and matched each trial's own reported results substantively.

## Non-regression floor — reported exactly as measured, per plan-045 Finding 3 (unchanged by plan-047 §3)

| Case | Control | Treatment | Floor met? |
|---|---|---|---|
| `code-review-fail-blocker-details` | 1/3 | 1/3 | Yes (equal) |
| `security-audit-coverage-consistency` | 3/3 | 1/3 | **No** |
| `plan-required-sections-compliant` | 3/3 | 3/3 | Yes (equal, ceiling) |

Reported honestly: the floor is met on 2 of 3 cases in this batch and not met on the third. This is
not evidence of a uniform "retrieval helps" or "retrieval hurts" effect — every individual failure in
this entire batch (7 of the 12 new trials failed; 3 of the 6 T488 on-record trials reused also
failed) traces to a formatting, verdict-severity, or matrix-self-consistency choice, never to
retrieval content itself.

## What this does and does not mean

This is the specific, named `k≥3` escalation experiment plan-047 §5 identified as "the single most
valuable next experiment" — now actually run. It resolves the two live possibilities plan-047 §2
posed for the two brittle T488 cases in different ways for each case: `code-review-fail-blocker-
details` cleanly confirms possibility (a) (a roughly-even formatting/severity coin-flip, symmetric
across both arms); `security-audit-coverage-consistency` fits neither possibility cleanly and is
reported as its own, third, honestly-inconclusive pattern (an elevated-but-mechanistically-
heterogeneous treatment-arm failure rate in a small sample) rather than forced into either bucket.
It also directly tests, and answers, whether `plan-required-sections-compliant`'s one clear-influence
trial was reproducible: it was not, under 2 further trials, both of which instead exhibited the
same disclosure-gap pattern (category 5) T489 first found on a different case — a second, independent
instance of that category, strengthening it as a real, recurring pattern rather than a one-off itself.
It does **not** close T458 (the full 20-case harness with a pre-registered "measurably improve"
threshold) or T456 (the ship-gate measurement) — both remain exactly as they were before this task,
`pending`/`blocked`. It does not touch T457 or T483. It does not set a numeric "measurably improve"
threshold — plan-047 §3's own deferral stands; this task supplies data toward that eventual
threshold, not the threshold itself.

## Constraints

- Never touched `feature/T475-codex-platform-integration`.
- Never edited anything under `tests/golden/**` — `expect.py` read/imported only, in all 3 cases.
- Never edited `scripts/scorecard.py` or `docs/benchmarks/tb-subset.json`/`.md`.
- No new paid/metered API usage beyond ordinary interactive-session dispatch.
- Did not install new dependencies into this repo's own dependency manifests — throwaway-venv only
  (`fastembed==0.8.0`, outside the repo).
- **No vault growth** — `implementation/knowledge/memory/{project,general}/` unchanged at 11 files
  before and after this task, independently confirmed.
- This task does not touch T456, T457, T458, or T483.

## Expected Outputs

1. Twelve real, on-disk scratch runs (outside the repo, in plain temp directories — not committed).
2. Twelve real boolean `check()` results (3 cases × 2 arms × 2 new trials), reported in the tables
   above, combined with the 6 on-record T488 trials to report full `k=3` per arm per case.
3. This brief's own results and classification sections, filled in with what actually happened.
4. `docs/tasks/active-tasks.md`/`completed-tasks.md` updated (this task closes in the same commit
   sequence that creates it, per T489's own precedent, since the work is already complete and
   verified at authoring time).

## Acceptance Criteria

1. All 12 new trials' live sessions actually ran via the in-process `Agent` tool (not simulated) —
   true, verifiable via each dispatch's own `agentId`/token-usage metadata returned this session.
2. All 12 new `check()` calls used the real, unmodified `expect.py` for each of the 3 cases, loaded
   via `importlib.util.spec_from_file_location`.
3. All 12 real booleans reported, whatever they are — 7 of 12 `False` results reported honestly, not
   suppressed or retried to force a different outcome.
4. `git diff` against `origin/develop` for this branch touches only this task brief and the ledger
   rows — no changes under `tests/golden/**`, `scripts/scorecard.py`, `docs/benchmarks/tb-subset.*`,
   `.mcp.json`.
5. This brief's closure explicitly states it does not close T458 or T456, does not set a numeric
   threshold, and reports the non-regression floor exactly as measured per case (met on 2 of 3,
   not met on 1 of 3), per plan-045 Finding 3's own discipline against inventing a threshold that
   flatters the result.
6. The classification for each of the 3 cases is stated plainly, including the one case (the
   security-audit case) that does not fit either of plan-047 §2's two named outcomes cleanly — not
   forced into a cleaner story than the data supports.
7. Self-referential ledger-defect sweep performed and passing (see below).

## Blocker Protocol

None encountered requiring escalation. Zero dispatch-instruction module-resolution failures occurred
in this batch (the `cd`-first fix from `task-T489.md`'s diagnosis was applied and verified before
every dispatch, not after a failure) — recorded here as a confirmation that the fix generalizes, not
as a blocker.

## Self-referential ledger-defect sweep

Re-derived the live, current top-tier component id list directly
(`python3 implementation/scripts/check-maturity.py --root implementation --verbose`, run fresh this
session, from this task's own worktree): **31 stable ids** (20 agents, 4 instructions, 7 skills) —
matching T487/T488/T489's own counts exactly, independently re-confirmed rather than trusted from
any prior record (79 total components checked, 0 failing their claimed level). Swept this brief's
own text against all 31 — zero bare hyphenated-id hits (this brief refers to agent roles in plain
prose, e.g. "the tech-lead role," rather than any stable skill/instruction/agent registry id). Also
re-derived the live held-out case-ID list directly (`ls tests/golden/held-out/`, 6 entries) — zero
bare mentions of any held-out case ID anywhere in this brief; every case ID named above is one of the
3 real, `open`, non-held-out cases this task actually dispatched. This row is created and closed in
the same commit sequence, so it is never attached to an open, non-`done` ledger row at any committed
state, matching T489's own precedent for avoiding the self-referential trap by construction.

## Git workflow

Branch `agent/orchestrator/T490`, created from `origin/develop` @ `823f2a5`. Merge request opened to
`develop`, referencing `T490`, **left unmerged** per the orchestrating session's explicit instruction
this turn ("do NOT run `glab mr merge` — hand it back to me").
