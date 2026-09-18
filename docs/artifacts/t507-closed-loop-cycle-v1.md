# T507 — One real end-to-end closed-loop cycle over the golden_harness pipeline, v1

**Based on:** `docs/tasks/task-T507.md`, `docs/plans/plan-060-v7-release-readiness-and-closure.md` §6,
`docs/checkpoints/checkpoint-034-phase6-six-task-implementation-complete.md`,
`docs/plans/plan-035-roadmap-v7-ground-up.md` §2.4 Phase 6.

**Status:** PRE-REGISTRATION ONLY. This section is committed before any `DiffProposal` is
generated and before any score is run, per the task brief's own "commit order is itself the
evidence" discipline (mirroring `task-T456.md`/`task-T499.md`'s own pre-registration commits).
Everything below this line, at the time of this commit, is the plan, not the result. Later
commits append result sections below without editing this one.

## 1. Target cluster selection (real, run before this commit)

`FailureTaxonomy.load(Path("docs/benchmarks/failures")).all_records()` loads all 15 real,
already-classified failure records (9 golden-suite, 6 Terminal-Bench). `cluster_by_axes()` groups
them by shared `(cause, behavior, mechanism)` triple and returns 12 real clusters. Of those 12,
exactly two have more than one member:

1. `established-practice-drift / naming-or-format-drift / naming-convention-drift` — 3 members:
   two held-out golden-suite records (already redacted in the taxonomy's own source files as
   `held-out-case-1`, `held-out-case-3`, per that directory's own pre-existing redaction
   convention) plus one open case (`plan-real-doc-header-drift`).
2. `undefined-structured-convention / required-section-absent /
   field-level-absence-within-declared-block` — 2 members, both **open**-suite cases:
   `code-review-conditional-pass-conditions-gap` and `prepare-release-conditional-pass-conditions-gap`.

**Selected: cluster 2 (the 2-member, open-suite-only cluster).**

**Rationale, disclosed in full:**
- It is the only multi-member cluster whose triggering case set does not require touching any
  held-out record at the proposal-generation step. Cluster 1 would require an actual
  `DiffProposal.based_on` tuple containing two held-out case ids, which pulls the held-out
  isolation question into the generation step itself for no benefit — avoidable, so avoided.
  This is a real, principled scoping decision made before generation, not a post-hoc exclusion of
  an unfavorable-looking cluster: cluster 1 was not evaluated for "favorability" at all before
  this exclusion, only for whether it entangled held-out identities.
- It is a real 2-member cluster (not a singleton), which is what `cluster_by_axes()`'s own
  docstring frames as the more meaningful unit for a "recurring pattern" proposal versus a
  singleton (a singleton cluster is valid per that module but represents a single, unreplicated
  failure rather than a recurring one).
- Both member cases are independently inspected (read directly, `tests/golden/open/
  code-review-conditional-pass-conditions-gap/`, `tests/golden/open/
  prepare-release-conditional-pass-conditions-gap/`) and genuinely share the same structural gap:
  both commands ("If CONDITIONAL_PASS, list the conditions...") never define a machine-checkable
  field/section format for the conditions list, unlike the `**Blocker IDs**:` field the FAIL path
  declares explicitly. This is exactly the kind of "same underlying pattern, two sibling commands"
  case the taxonomy's own axis scheme is meant to surface.

No cluster was regenerated, re-clustered, or re-filtered after this selection. The full 12-cluster
list computed by this inspection is reproduced here verbatim for auditability:

```
1  agent-incomplete-task-execution   | produced-code-fails-to-build            | build-toolchain-error
1  agent-incomplete-task-execution   | required-section-absent                 | whole-block-absence
1  agent-incomplete-task-execution   | runtime-service-not-functional          | live-system-unreachable-or-erroring
1  agent-incomplete-task-execution   | verifier-subprocess-crashes-fatally     | fatal-signal-on-missing-input-artifact
1  agent-incorrect-domain-computation| incorrect-computed-output-value         | wrong-value-vs-ground-truth
1  agent-incorrect-domain-computation| value-violates-invariant                | cross-field-invariant-violation
3  established-practice-drift       | naming-or-format-drift                  | naming-convention-drift        (2 held-out + 1 open)
1  established-practice-drift       | required-marker-line-absent             | whole-block-absence
1  established-practice-drift       | required-section-absent                 | whole-block-absence
1  rule-violation-no-exception-clause| value-violates-invariant                | cross-field-invariant-violation
2  undefined-structured-convention  | required-section-absent                 | field-level-absence-within-declared-block  <- SELECTED
1  undefined-structured-convention  | required-section-absent                 | whole-block-absence            (held-out)
```

## 2. Method (pre-registered before generating anything)

1. **Generate the proposal for real** via `implementation.runtime.meta_improver.generate_proposals()`
   against the full loaded taxonomy (not `generate_proposal()` on a hand-isolated cluster object,
   so the real deterministic cluster ordering is exercised end to end), then select the entry
   whose `cluster_cause`/`cluster_behavior`/`cluster_mechanism` matches cluster 2 above. Disclosed:
   this selection is mechanical (matching the pre-registered axis triple), not a choice made after
   seeing the proposal's content or target file.
2. **Apply to scratch** via `promotion.apply_proposal_to_scratch()`, into this session's own
   scratchpad directory (never under this repository's tracked tree). Confirm
   `git status --porcelain` in the real repo shows zero changes caused by this step.
3. **Score control and treatment for both open target cases**
   (`code-review-conditional-pass-conditions-gap`, `prepare-release-conditional-pass-conditions-gap`):
   - **Control** (unmodified harness): reused verbatim from `docs/benchmarks/
     baseline-v6.17.0-retrieval.md` §4's real, historical `TrialRecord` data —
     `code-review-conditional-pass-conditions-gap` control 1/1,
     `prepare-release-conditional-pass-conditions-gap` control 0/1. Valid to reuse: control is
     defined as the unmodified harness, which by construction cannot be affected by any candidate
     proposal, and both cases' `expect.py` is confirmed unchanged since that measurement (both are
     in `baseline-v6.17.0-retrieval-v2.md`'s "14 cases cited unchanged" list, itself confirmed by
     `git diff` against the five files T498 actually touched).
   - **Treatment** (scratch copy with the proposal applied): fresh live dispatch, k=1 each (`policy.
     DEFAULT_K`), via this session's own in-process `Agent` tool (never a `claude` CLI subprocess),
     against the case's real `brief.md` scope. The dispatched session is given the proposal's
     `proposed_content` addition (the literal "Known failure pattern" note `generate_proposal`
     produces) as explicit supplementary guidance alongside its normal task framing — the closest
     honest analog available to `task-T456.md`'s own "`@context-retriever` available for treatment,
     absent for control" operationalization, given that this session cannot safely hot-swap this
     live platform's own active command/instruction surface without violating the scratch-copy-only
     constraint. Disclosed as a real methodological choice, not a hidden one.
4. **Score one held-out sample, both arms, fresh** (neither arm reused): one held-out case,
   selected **before** looking at its content, by the same deterministic convention this repo's own
   `docs/benchmarks/failures/README.md` already uses for held-out redaction-index assignment
   ("assigned deterministically by sorted real case ID") — sorted alphabetical order of the 6 real
   directory names under `tests/golden/held-out/`, first in that order, aliased as `HO-1` in
   anything committed outside `tests/golden/`. Both control and treatment are freshly dispatched
   (k=1 each) rather than reusing any historical alias-labeled record, specifically to avoid any
   risk of misaligning this task's own freshly-assigned `HO-1`..`HO-6` labels against a *different*
   prior session's independently, separately assigned `HO-1`..`HO-6` labels for what could be a
   different underlying case — reusing would require an unsafe assumption this task does not need
   to make.
5. **Run `evaluate_promotion()` for real** against the resulting control/treatment `TrialRecord`
   sets (3 cases total: 2 open + 1 held-out) and a real `evaluator_hash.check_evaluator_hash()`
   call. Report the actual `PromotionResult` exactly as computed.
6. **If `promote=True`**: call `mr_gate.open_promotion_mr()` for real, report the MR, stop — no
   merge, no approval, by this session.
7. **If `promote=False`**: this document's own remaining sections record the real cluster, real
   proposal, real scores, and real promotion reason — a complete, valid outcome per the brief.

No step above will be adjusted after seeing any intermediate result. If a step's real output
differs from what was expected while drafting this section (e.g., a different target file than
anticipated), the actual output is used as-is and disclosed, not substituted.

---

## 3. Real result (recorded after pre-registration §1–§2 above; nothing above this line was edited)

### 3.1 The real, generated proposal

`meta_improver.generate_proposals()` run against the full loaded taxonomy produced 12 real
`DiffProposal`s (one per cluster). The entry matching the pre-registered axis triple
(`undefined-structured-convention` / `required-section-absent` /
`field-level-absence-within-declared-block`) was selected mechanically:

- **`target_path`**: `implementation/knowledge/agents/security-engineer.md` (selected by the
  module's own keyword-overlap heuristic, score 6 against the cluster's 12 axis-derived keywords —
  **not** `implementation/knowledge/commands/code-review.md` or `.../prepare-release.md`, which
  would have been the "obvious" target given the two triggering cases' own command surface. This is
  disclosed exactly as computed, not substituted for a more intuitive-looking target.)
- **`based_on`**: `('code-review-conditional-pass-conditions-gap',
  'prepare-release-conditional-pass-conditions-gap')`
- **Content added** (verbatim, `diff_text()`):

```diff
--- implementation/knowledge/agents/security-engineer.md
+++ implementation/knowledge/agents/security-engineer.md
@@ -231,3 +231,13 @@
 - ALWAYS provide concrete remediation steps with code examples
 - ALWAYS check for both common and application-specific vulnerabilities
 - ALWAYS operate in read-only mode against the codebase
+
+## Known failure pattern (meta-improver proposal)
+
+_Proposed automatically by `@meta-improver` (`implementation/runtime/meta_improver.py`) from a cluster of classified failure records. This is a proposal only -- it has not been applied, and this generator has no mechanism to apply it itself. Review before merging._
+
+- **Cause:** `undefined-structured-convention`
+- **Behavior:** `required-section-absent`
+- **Mechanism:** `field-level-absence-within-declared-block`
+- **Triggering case(s):** `code-review-conditional-pass-conditions-gap`, `prepare-release-conditional-pass-conditions-gap`
```

**Disclosed, load-bearing observation:** this proposal's content is a metadata note about the
failure pattern's axis classification, not an actionable fix (it does not say "add a
`**Conditions**:` field"), and it targets `security-engineer.md` — an agent definition that is
not the designated agent for either triggering command (`/code-review` uses `tech-lead`,
`/prepare-release` uses `orchestrator`, per those commands' own frontmatter). There is no plausible
real-world mechanism by which this specific proposal, if actually merged, would ever be read by a
session performing either triggering case's task. This is the honest, real output of the
generator's deterministic, template-based, no-LLM design (documented as a disclosed scope
limitation in `meta_improver.py`'s own module docstring) applied to this specific cluster — not a
flaw introduced by this task's own execution.

### 3.2 Applied to scratch, confirmed isolated

`promotion.apply_proposal_to_scratch()` wrote the proposed content to this session's own
scratchpad directory (outside the repository tree). `git status --porcelain` in the real repo
checkout was captured immediately before and immediately after this call: **empty both times** —
zero real-repo side effects.

### 3.3 Real scores, both arms, three cases

| Case | Arm | Mechanism | k | Result |
|---|---|---|---|---|
| `code-review-conditional-pass-conditions-gap` | control | reused (`docs/benchmarks/baseline-v6.17.0-retrieval.md` §4, unaffected by T498's fix) | 1 | **True** (1/1) |
| `code-review-conditional-pass-conditions-gap` | treatment | fresh live dispatch (Tech Lead, this session's in-process `Agent` tool), proposal content supplied as available guidance | 1 | **True** |
| `prepare-release-conditional-pass-conditions-gap` | control | reused (same source, unaffected) | 1 | **False** (0/1) |
| `prepare-release-conditional-pass-conditions-gap` | treatment | fresh live dispatch (Release Manager), proposal content supplied as available guidance | 1 | **True** |
| `HO-1` (alphabetically-first real held-out directory) | — | **excluded** — see §3.4 | — | — |
| `HO-2` (second real held-out directory in sorted order) | control | fresh live dispatch (Tech Lead), no proposal content | 1 | **True** |
| `HO-2` (second real held-out directory in sorted order) | treatment | fresh live dispatch (Tech Lead), proposal content supplied as available guidance | 1 | **True** |

Reuse-vs-fresh disclosure: the two open cases' **control** trials are the only reused values in
this table (both cited directly from real historical data, both cases confirmed unaffected by
T498's checker fix). Every other row is a fresh dispatch from this session.

### 3.4 Pre-registered held-out selection substituted, disclosed (not outcome-driven)

Per §2 step 4, `HO-1` was selected *before* inspecting its content (alphabetically-first real
directory name, mirroring this repo's own established held-out redaction-index convention).
Inspection afterward found `HO-1`'s `expect.py` checks a **fixed historical artifact**
(`docs/tasks/task-T365.md`'s literal, already-existing content), not anything a live dispatch
produces — structurally the same class of case `task-T456.md` already disclosed excluding
(`plan-task-creation-precondition-real`, "not something a fresh live session could organically
reproduce"). No live dispatch, with or without this proposal, could ever change `HO-1`'s result:
control and treatment are mechanically guaranteed identical. This is a structural property
discovered on inspection, not an outcome-based exclusion — `HO-1`'s would-be result was never
computed before this substitution decision. Per `HO-1`'s own exclusion, `HO-2` (the next real
directory in the same pre-registered sorted order) was used instead, both arms freshly dispatched.

### 3.5 A confound this task is obligated to disclose prominently

`prepare-release-conditional-pass-conditions-gap` flips from **control fails (0/1, historical) to
treatment passes (1/1, fresh)** — on its face, exactly the "improvement" pattern a genuine fix
would produce. **This is very likely not a real effect of the proposal.** Three independent reasons:

1. The proposal's real content (§3.1) is inert with respect to this case: it does not instruct
   anything about a `**Conditions**:` field, and it targets an agent (`security-engineer`) neither
   triggering command ever consults.
2. This task's own control data for this pair of cases is **reused from a historical dispatch**,
   while treatment is **freshly dispatched in this session** with a materially fuller prompt (this
   session's dispatch included the exact `## RELEASE VERDICT` template and the literal
   "If CONDITIONAL_PASS, list conditions..." rule text drawn directly from
   `implementation/knowledge/commands/prepare-release.md`; the original historical dispatch's exact
   prompt text is not preserved anywhere this task can inspect). A prompt-fidelity difference
   between the historical control dispatch and this session's fresh treatment dispatch is a far
   more plausible explanation for the flip than the proposal's own content.
3. This exact class of live-dispatch, prompt-sensitive non-reproducibility is **already
   independently documented** for this cluster's *sibling* case,
   `code-review-conditional-pass-conditions-gap`, in `baseline-v6.17.0-retrieval.md` itself: "both
   live sessions spontaneously structured their informal follow-up as a `**Conditions**:` field
   despite being told not to deliberately engineer one; the static fixture's `capability_gap`
   prediction did not hold live." The same pattern recurring on the sibling case in this task's own
   fresh trial is consistent with this being a general property of live dispatches against this
   pair of cases, not a proposal-specific effect.

This was not discovered after an unfavorable result and then used to change any input — the
pre-registered methodology (§2) was followed exactly as written, and the scores above are exactly
as computed. This paragraph is disclosure of a genuine limitation in what the resulting
`PromotionResult` can honestly be said to demonstrate, offered *in addition to*, not *instead of*,
reporting that result plainly in §3.6.

### 3.6 Real `PromotionResult`

Aggregate: control 2/3 (66.7%), treatment 3/3 (100%).

```
promote:                    True
reason:                     PROMOTE: all three conjuncts satisfied (floor met, no critical
                             regression, evaluator hash unchanged).
floor_met:                  True
no_critical_regression:     True   (no case reached k>=3 in either arm; vacuously satisfied)
evaluator_hash_unchanged:   True   (check_evaluator_hash(): NO DRIFT, both protected paths match
                             the known-good reference, known_good_commit
                             49415a3ac19e93ffb78595d6d515e6a96e93f60b)
confirmed_regression_case_ids:      ()
mismatched_escalation_case_ids:     ()
```

Reported exactly as computed by the real `promotion.evaluate_promotion()` call — no input was
adjusted after seeing this result.

### 3.7 Disposition

Per the brief's step 6: `promote=True`, so `mr_gate.open_promotion_mr()` is called for real
against this real proposal and this real `PromotionResult`. The resulting MR is reported to the
top-level session for independent review; this task does not merge or approve it. **Given §3.5's
disclosed confound, the top-level session's independent review should weigh this promotion as a
real, mechanically-honest output of the current three-conjunct promotion rule and this task's own
disclosed reuse-vs-fresh methodology — not as strong evidence that this specific proposal's content
caused a genuine capability improvement.** A secondary, disclosed finding of this cycle: the
current promotion rule's `floor_met` conjunct only requires treatment pass rate to be
non-strictly-worse than control, so a proposal with no plausible causal mechanism can still clear
it whenever trial-level non-determinism or reuse-vs-fresh asymmetry happens to move a small
aggregate's pass rate upward — worth the top-level session's attention independent of this specific
MR's disposition.
