# Failure Taxonomy (`cause × behavior × mechanism`) — v1

**Status:** Proposed (author-only; not yet independently reviewed).
**Based on:** `docs/plans/plan-035-roadmap-v7-ground-up.md` §2.4 Phase 1 (Layer 1, T415 row:
*"Failure taxonomy: classify each golden failure as `cause × behavior × mechanism`, stored in
`docs/benchmarks/failures/`."*) and §1.1's verdict on the idea (*"Correct and cheap. Adopted."*).
`docs/tasks/task-T415.md`, `docs/artifacts/golden-suite-format-v1.md` (T410, for the
`tracked_defect`/`capability_gap` distinction this scheme relates to but does not duplicate),
`docs/benchmarks/scorecard-v6.12.0.json` (T413, the source-of-truth `known_failing` set this
scheme classifies).
**Owner:** qa-engineer
**Consumers:** T409 (`T41C` in this ledger's backlog — extends this scheme to ingest
Terminal-Bench/Harbor trajectory failures into the same three axes, "one taxonomy, two
sources"); CWSO (cross-repo reference — this scheme is defined once here and referenced there,
not redefined).

## 1. Why this exists

`docs/benchmarks/scorecard-v6.12.0.json` (T413) tells you *how many* golden cases fail and
whether each is a `tracked_defect` or a `capability_gap`. It does not tell you *why* they fail in
a structured, comparable way — two `tracked_defect` cases can fail for structurally unrelated
reasons (a whole section missing vs. a header renamed), and knowing which is which matters for
triage (a missing block is a different kind of fix than a renamed header) and for later
cross-source comparison (T409 needs to place Harbor trajectory failures into the *same* buckets
as golden-suite failures, which requires the buckets to be defined by observable failure shape,
not by golden-suite-specific mechanics).

This document defines three independent axes — `cause`, `behavior`, `mechanism` — and enumerates
their values, derived bottom-up from the 9 real cases the golden suite currently classifies as
`known_failing` (per `docs/benchmarks/scorecard-v6.12.0.json`, `content.summary.known_failing:
9`). It is deliberately **not** a general-purpose, invented scheme: every value below exists
because at least one real case requires it, and every value is retired if a future re-derivation
finds no case that needs it.

## 2. Relationship to `known_failing_category` (`tracked_defect` / `capability_gap`)

`golden-suite-format-v1.md` §4.4 already splits `known_failing` cases into two categories at
authoring time: `tracked_defect` (a real, fixable gap between declared contract and either
implementation or established practice) and `capability_gap` (the command surface has no
machine-checkable convention for the thing at all, so there's nothing yet to "fix" in the
narrow sense). This taxonomy's `cause` axis is **related to but finer-grained than** that split,
not a renaming of it:

- `capability_gap` cases all share exactly one `cause` value below
  (`undefined-structured-convention`) — by construction, since "no declared schema exists" is
  what `capability_gap` means.
- `tracked_defect` cases split across **two** distinct `cause` values
  (`established-practice-drift` and `rule-violation-no-exception-clause`) — the real 9 cases show
  these are genuinely different situations that both happen to be authored-time-classified as
  `tracked_defect`, but which imply different remediation paths (reconcile contract vs. practice,
  versus add an exception clause to an existing rule).

So `cause` is not redundant with `known_failing_category`: it is strictly more granular on the
`tracked_defect` side, and exactly as granular on the `capability_gap` side (§4 below shows the
full case-by-case mapping, including this asymmetry).

## 3. The three axes

### 3.1 `cause` — the root reason the check fails today

| Value | Definition | Real cases (open, real ID; held-out, redacted label — see §5) |
|---|---|---|
| `undefined-structured-convention` | The command's own text mandates a behavior/outcome, but declares no machine-checkable field/section schema for verifying it happened. Not a mistake by whoever produced the document — there is nothing to conform to yet. | `code-review-conditional-pass-conditions-gap`, `prepare-release-conditional-pass-conditions-gap`, `held-out-case-4` |
| `established-practice-drift` | The command's declared contract is unambiguous, but a real corpus of existing artifacts across this repo's history consistently uses a different convention instead — grounded in an explicit corpus survey cited in the case's `known_failing_reason` (e.g. `grep -rn`/`grep -rl` counts across all matching real files, not just the one fixture). | `new-feature-real-checkpoint-format-drift`, `plan-real-doc-header-drift`, `prepare-release-real-verdict-missing`, `held-out-case-1`, `held-out-case-3` |
| `rule-violation-no-exception-clause` | The command states an unconditional rule; a plausible, hand-authored scenario (no real corpus precedent exists to source it from) produces output that violates the rule, and the rule's own text carries no exception carve-out for the judgment call that led there. | `security-audit-critical-not-fail` |
| `agent-incorrect-domain-computation` *(T409, Harbor)* | The agent understood the required output contract/shape and attempted the underlying technical/domain task, but the substantive computation, analysis, or generated-artifact content is factually wrong or violates a declared constraint — a wrong answer, not a missing or malformed one. | See `docs/benchmarks/failures/terminal-bench/incorrect-computed-output-value.md`, `.../invariant-violation-in-generated-artifact.md` |
| `agent-incomplete-task-execution` *(T409, Harbor)* | The agent's session did not result in the task reaching a functionally working end state: a required output artifact was never produced, a required live system/service was left non-functional, submitted code never compiled, or a verifier-invoked tool crashed fatally attempting to consume a missing intermediate artifact — the root problem is execution stopping short of "done," not an incorrect answer being recorded. | See `docs/benchmarks/failures/terminal-bench/required-output-artifact-absent.md`, `.../runtime-service-not-functional.md`, `.../produced-code-fails-to-build.md`, `.../verifier-crashes-on-missing-dependency.md` |

Why these three are genuinely distinct (not a forced split): `undefined-structured-convention`
cases have *no* schema to violate — the fix is "define one." `established-practice-drift` cases
have a schema and a *corpus of real, already-existing artifacts* that ignore it — the fix is
"reconcile contract and practice," evidenced by grep counts, not by one hand-picked example.
`rule-violation-no-exception-clause` has a schema, a real rule, and a single hand-authored
scenario that breaks it because the rule text has no escape hatch — the fix is "add an exception
clause or hold the line," a narrower and different kind of decision than the other two.

### 3.2 `behavior` — the observable symptom in the failing document

| Value | Definition | Real cases |
|---|---|---|
| `required-section-absent` | A declared section/field-group is completely missing from the document (no partial trace of it anywhere). | `code-review-conditional-pass-conditions-gap`, `prepare-release-conditional-pass-conditions-gap`, `prepare-release-real-verdict-missing`, `held-out-case-4`; also reused unmodified for 3 Terminal-Bench cases (required output file, not document section, but same "total absence, no partial trace" shape), see `docs/benchmarks/failures/terminal-bench/required-output-artifact-absent.md` |
| `required-marker-line-absent` | A specific declared single-line marker convention never appears anywhere in the real corpus surveyed. | `new-feature-real-checkpoint-format-drift` |
| `naming-or-format-drift` | The conceptual content is present in the document, but expressed under different header names, inline formatting, or a different naming/filename pattern than the declared spec. | `plan-real-doc-header-drift`, `held-out-case-1`, `held-out-case-3` |
| `value-violates-invariant` | All required fields are present and individually well-formed, but their combined values contradict an explicitly declared cross-field rule. | `security-audit-critical-not-fail`; also reused unmodified for 3 Terminal-Bench cases, see `docs/benchmarks/failures/terminal-bench/invariant-violation-in-generated-artifact.md` |
| `incorrect-computed-output-value` *(T409, Harbor)* | The required output artifact is present, well-formed, and structurally complete, but a computed/extracted value inside it is factually wrong relative to an independently-known correct answer — not an internal cross-field contradiction, a single external correctness mismatch. | See `docs/benchmarks/failures/terminal-bench/incorrect-computed-output-value.md` |
| `runtime-service-not-functional` *(T409, Harbor)* | A live functional check against a running service/process/system the agent was required to stand up fails (connection refused, non-2xx/no response, non-zero exit) even though static setup artifacts may be present. | See `docs/benchmarks/failures/terminal-bench/runtime-service-not-functional.md` |
| `produced-code-fails-to-build` *(T409, Harbor)* | Submitted source/config artifacts fail to compile or link entirely, before any functional or correctness check can run. | See `docs/benchmarks/failures/terminal-bench/produced-code-fails-to-build.md` |
| `verifier-subprocess-crashes-fatally` *(T409, Harbor, fix pass 2026-09-08)* | An external tool/process the verifier invokes to evaluate the produced artifact terminates via an uncaught fatal error or signal — not a graceful assertion/exception — before completing its evaluation, so the check never produces a clean pass/fail signal for the underlying condition being tested. | See `docs/benchmarks/failures/terminal-bench/verifier-crashes-on-missing-dependency.md` |

`required-section-absent` and `required-marker-line-absent` are kept separate rather than merged
into one "absent" bucket because they differ in grain: a *section* is a multi-line structural
unit (a whole `##` block or field-group), while the one real case in
`required-marker-line-absent` is specifically a single required line with no surrounding
block — worth distinguishing because "add a missing line" and "add a missing section" are
different-sized fixes, and a future case could exercise either independently of the other.

### 3.3 `mechanism` — how/where the gap manifests structurally

| Value | Definition | Real cases |
|---|---|---|
| `whole-block-absence` | An entire required heading/section/marker is missing — no partial container for it exists anywhere in the document. | `new-feature-real-checkpoint-format-drift`, `prepare-release-real-verdict-missing`, `held-out-case-4`; also reused unmodified for 3 Terminal-Bench cases, see `docs/benchmarks/failures/terminal-bench/required-output-artifact-absent.md` |
| `field-level-absence-within-declared-block` | The surrounding block/convention *is* present (e.g. a verdict block with a `Status` field exists), but one specific sub-field the contract requires — with no declared schema for it — is missing from within it. | `code-review-conditional-pass-conditions-gap`, `prepare-release-conditional-pass-conditions-gap` |
| `naming-convention-drift` | Required content is present in some structural form, but under different header/field names or a different naming pattern than declared. | `plan-real-doc-header-drift`, `held-out-case-1`, `held-out-case-3` |
| `cross-field-invariant-violation` | Individually well-formed, present fields whose combined values break a declared cross-field rule. | `security-audit-critical-not-fail`; also reused unmodified for 3 Terminal-Bench cases, see `docs/benchmarks/failures/terminal-bench/invariant-violation-in-generated-artifact.md` |
| `wrong-value-vs-ground-truth` *(T409, Harbor)* | The output's shape and internal consistency are correct; verification fails purely on comparing the produced value(s) to an expected/reference value computed independently by the verifier. | See `docs/benchmarks/failures/terminal-bench/incorrect-computed-output-value.md` |
| `live-system-unreachable-or-erroring` *(T409, Harbor)* | At verification time, the required service/process is not reachable, not responding correctly, or exits with a non-zero/error status when exercised. | See `docs/benchmarks/failures/terminal-bench/runtime-service-not-functional.md` |
| `build-toolchain-error` *(T409, Harbor)* | A compiler or linker step exits non-zero due to a defect in the agent's submitted code — verification never reaches the runtime or value-comparison stage. | See `docs/benchmarks/failures/terminal-bench/produced-code-fails-to-build.md` |
| `fatal-signal-on-missing-input-artifact` *(T409, Harbor, fix pass 2026-09-08)* | The invoked tool's own internal fatal-error path (e.g. a native `CHECK`/fatal-log macro) aborts the process with a terminating signal when it attempts to load a required artifact that an earlier task step never produced, rather than that absence being caught and reported gracefully by a Python-level existence check. | See `docs/benchmarks/failures/terminal-bench/verifier-crashes-on-missing-dependency.md` |

`mechanism` is not a re-labeling of `behavior`: the two `undefined-structured-convention`
"conditions gap" cases (`code-review-conditional-pass-conditions-gap`,
`prepare-release-conditional-pass-conditions-gap`) share `behavior: required-section-absent`
with `prepare-release-real-verdict-missing` and `held-out-case-4`, but split off into their own
`mechanism` value (`field-level-absence-within-declared-block`) because — unlike those other
two — the surrounding verdict block *does* exist in the failing document (a `Status:
CONDITIONAL_PASS` field is present); only the undeclared sub-field is missing. This distinction
would be lost if `mechanism` just mirrored `behavior`.

## 4. Full case-by-case axis assignment

| Case (real ID / redacted label) | `known_failing_category` | `cause` | `behavior` | `mechanism` |
|---|---|---|---|---|
| `code-review-conditional-pass-conditions-gap` | capability_gap | undefined-structured-convention | required-section-absent | field-level-absence-within-declared-block |
| `new-feature-real-checkpoint-format-drift` | tracked_defect | established-practice-drift | required-marker-line-absent | whole-block-absence |
| `plan-real-doc-header-drift` | tracked_defect | established-practice-drift | naming-or-format-drift | naming-convention-drift |
| `prepare-release-conditional-pass-conditions-gap` | capability_gap | undefined-structured-convention | required-section-absent | field-level-absence-within-declared-block |
| `prepare-release-real-verdict-missing` | tracked_defect | established-practice-drift | required-section-absent | whole-block-absence |
| `security-audit-critical-not-fail` | tracked_defect | rule-violation-no-exception-clause | value-violates-invariant | cross-field-invariant-violation |
| `held-out-case-1` (redacted) | tracked_defect | established-practice-drift | naming-or-format-drift | naming-convention-drift |
| `held-out-case-3` (redacted) | tracked_defect | established-practice-drift | naming-or-format-drift | naming-convention-drift |
| `held-out-case-4` (redacted) | capability_gap | undefined-structured-convention | required-section-absent | whole-block-absence |

Full per-case detail (what was actually read, why each axis value was assigned) lives in
`docs/benchmarks/failures/*.md` — one file per case, see `docs/benchmarks/failures/README.md`
for the index.

## 5. Held-out identity handling

Per T412/T413/T414 precedent (`scripts/scorecard.py`'s `redact_held_out_identities()`), the 3
held-out cases among the 9 (out of the golden suite's 6 total held-out cases — 3 are
`expected_pass` and out of scope here) are labeled `held-out-case-<n>`, where `<n>` is assigned
by the **same rule** `scripts/scorecard.py` uses: sort all 6 real held-out case IDs
alphabetically, number 1–6 in that order, keep the label for whichever of those 6 land in the
`known_failing` bucket. This task's own read of
`tests/functional/test_golden_held_out_isolation.py`'s
`test_held_out_dir_has_the_expected_six_cases` (the authoritative list of all 6 real held-out
IDs) confirms the resulting labels for the 3 that are `known_failing` are `held-out-case-1`,
`held-out-case-3`, and `held-out-case-4` — consistent with, and traceable to,
`docs/benchmarks/scorecard-v6.12.0.json`'s own labeling for the same 3 cases. No real held-out
case ID, path, or fixture content appears anywhere in this document or in
`docs/benchmarks/failures/`.

## 6. Known limitation: no `regression` / `unexpected_pass` bucket yet

This taxonomy currently classifies **only** the `known_failing` bucket (9 cases, 0 regressions, 0
`unexpected_pass` per `docs/benchmarks/scorecard-v6.12.0.json`'s
`content.summary.{regressions,unexpected_pass}` fields, both `0` at authoring time). It does not
yet define what `cause`/`behavior`/`mechanism` would mean for a case that unexpectedly starts
failing (`regression`) or unexpectedly starts passing (`unexpected_pass`) — there is no real
example of either today to derive values from, and per this scheme's own bottom-up-only
discipline (§1), inventing values without a real case to ground them is exactly what this
document avoids. This is a natural, explicitly flagged follow-up for whichever task first
encounters a real regression or `unexpected_pass` case, not something to solve speculatively now.

## 7. Reuse notes for T409 (Harbor trajectory extension)

T409 extends this scheme to Terminal-Bench/Harbor trajectory failures ("one taxonomy, two
sources," per plan-035's cross-repo coordination table). The three axis definitions in §3 are
written in terms of *observable document/output shape* (block absence, field absence, naming
drift, invariant violation) rather than golden-suite-specific mechanics (`expect.py`,
`case.yaml`), so they should transfer without redefinition. T409 will likely need to decide
whether a Harbor trajectory failure that doesn't fit any of the 9 enumerated values here should
extend an existing axis's value set or flag a genuine fourth axis value — that decision is
explicitly out of scope for this document and left to T409.

**Resolved (2026-09-08, T409):** the hypothesis above holds. No fourth axis was needed. Two of
`behavior`/`mechanism`'s existing values (`value-violates-invariant`/`cross-field-invariant-violation`
and `required-section-absent`/`whole-block-absence`) transferred to real Terminal-Bench failures
completely unmodified. Three genuinely new `behavior`/`mechanism` value pairs and two new `cause`
values were added (§3.1–3.3 above) because no existing value could describe them without forcing a
bad fit — full detail, real task-name citations, and verbatim verifier evidence in §8 below.

## 8. Terminal-Bench/Harbor trajectory extension (T409)

**Status:** Closes Phase 1's Gate G1 acceptance bullet "Terminal-Bench and golden failures appear
in one taxonomy" (`plan-035-roadmap-v7-ground-up.md` §2.4). Sections 1–7 above are the original
T415 golden-suite scheme and are unchanged in substance by this section; only new axis-value rows
were added to the §3 tables (marked `(T409, Harbor)`) and this section was appended.

### 8.1 Sources used

1. **Local k=3 single-pass run** (`tb-delta-20260814T111217Z`, arms A and B, T407's original
   measurement) — 150 trials total (75 per arm), read from
   `/home/emage/Code/emage/worktrees/t407-tb-delta/jobs/tb-delta-20260814T111217Z-arm-{A,B}/*/result.json`
   (a leftover T407 working directory, confirmed present at this task's dispatch time, not a
   tracked repo artifact).
2. **Remote Design A successful passes** (`tb-delta-{20260907T162617Z,20260907T203448Z,20260908T001726Z}`,
   arms A and B) — 150 trials total, read via read-only SSH from
   `10.10.160.11:/root/emage-code-t407/jobs/tb-delta-<run>-arm-{A,B}/*/result.json`. No `harbor` or
   Docker command was executed on that host; only pre-existing `result.json` and
   `verifier/test-stdout.txt` files were read.

Combined: 300 trials read, 157 genuine task-level failures classified (71 from source 1, 86 from
source 2), across **21** distinct failing task names, grouped into **6** distinct failure patterns.
(Corrected 2026-09-08 — see §8.6. The original pass undercounted this as "17 task names / 5
patterns," which was the local source's own distinct-task-name count, not the true union across
both sources.)

### 8.2 Extraction method

For each trial's `result.json`: a trial counts as a genuine task-level failure iff
`exception_info` is `null` (Harbor's own harness reports it as an ordinary verifier outcome, not a
harness/agent-execution exception) **and** `verifier_result.rewards.reward == 0.0`. For each such
trial, `verifier/test-stdout.txt` (pytest output) and, where present, `verifier/ctrf.json` were
read to determine the actual failure content before assigning axis values — the same discipline
`failure-taxonomy-v1.md` §1 already requires for golden cases (derive bottom-up from real evidence,
not from the task name alone).

### 8.3 Infrastructure-failure exclusion (Objective 4)

Trials where `exception_info` is **not** `null` were explicitly excluded from this classification
pass — they are harness/infra failures (predominantly `AgentTimeoutError`, i.e. the agent's own
execution exceeded its time budget before the verifier could even run), not task-outcome failures,
and the `cause × behavior × mechanism` scheme classifies the latter, not the former (per Objective
4 of this task's brief). Counts, not silently dropped:

- Local k=3 run: 38 of 150 trials excluded as infra failures (all `AgentTimeoutError`).
- Remote Design A passes: 19 of 150 trials excluded as infra failures (all `AgentTimeoutError`).
- **The two fully-failed Design A attempts** (100% `RewardFileNotFoundError`/`AgentTimeoutError`,
  per `docs/tasks/task-T407.md`'s closing note) are excluded in their entirety — every trial in
  those two attempts is an infra failure by construction, so none contribute genuine task-level
  data to this scheme. They are real trajectory data of a different kind and are noted here, not
  silently omitted, per this task's Objective 4/source (3).

157 genuine failures + 57 infra-excluded trials + 86 passes (41 local `reward: 1.0` + 45 remote,
sanity-checked against the totals above) accounts for all 300 trials read. (Corrected 2026-09-08 —
the original pass misstated this as "45 local," an arithmetic slip: 150 local trials − 38
infra-excluded − 71 genuine local failures = 41 genuine local passes, not 45. The aggregate 86
figure itself was always correct; only the local/remote breakdown inside the parenthetical was
wrong. See §8.6.)

### 8.4 Pattern-by-pattern summary

| Pattern file (`docs/benchmarks/failures/terminal-bench/`) | `cause` | `behavior` | `mechanism` | Task names | Trials |
|---|---|---|---|---|---|
| `incorrect-computed-output-value.md` | `agent-incorrect-domain-computation` (new) | `incorrect-computed-output-value` (new) | `wrong-value-vs-ground-truth` (new) | `chess-best-move`, `gcode-to-text`, `log-summary-date-ranges`, `video-processing`, `db-wal-recovery`, `sparql-university`, `rstan-to-pystan`†, `train-fasttext`† (1 of its 4 trials) | 20 |
| `invariant-violation-in-generated-artifact.md` | `agent-incorrect-domain-computation` (new) | `value-violates-invariant` (**reused**) | `cross-field-invariant-violation` (**reused**) | `protein-assembly`, `dna-assembly`, `overfull-hbox` | 14 |
| `required-output-artifact-absent.md` | `agent-incomplete-task-execution` (new) | `required-section-absent` (**reused**) | `whole-block-absence` (**reused**) | `crack-7z-hash`, `feal-linear-cryptanalysis`, `make-mips-interpreter`, `train-fasttext`† (3 of its 4 trials) | 14 |
| `runtime-service-not-functional.md` | `agent-incomplete-task-execution` (new) | `runtime-service-not-functional` (new) | `live-system-unreachable-or-erroring` (new) | `configure-git-webserver`, `kv-store-grpc`, `install-windows-3-11`, `pypi-server`, `hf-model-inference` | 21 |
| `produced-code-fails-to-build.md` | `agent-incomplete-task-execution` (new) | `produced-code-fails-to-build` (new) | `build-toolchain-error` (new) | `custom-memory-heap-crash` (remote source only) | 1 (representative; task passed 3/3 locally, showing cross-source variance) |
| `verifier-crashes-on-missing-dependency.md` † | `agent-incomplete-task-execution` (**reused**) | `verifier-subprocess-crashes-fatally` (new) | `fatal-signal-on-missing-input-artifact` (new) | `caffe-cifar-10`† (remote source only) | 1 |

† = added in the 2026-09-08 fix pass (§8.6) — these 3 task names (`caffe-cifar-10`,
`rstan-to-pystan`, `train-fasttext`) were present in the remote source's genuine-failure set but
were entirely absent from the original pass's pattern files and headline counts.

The "Trials" column above counts only the trials individually cited by hash in each pattern file
(71 total post-fix, up from 65 in the original pass — predominantly from the local source, whose
71 genuine failures were read in full). The remaining 86 genuine failures (157 total − 71 cited by
hash) are additional trials of the *same 21* task names, confirmed by re-running the same
`exception_info`/`reward` extraction against the remote source's 3 runs — 16 of the 17
local-failing task names also fail genuinely in at least one remote run (`pypi-server` is the one
exception: it failed once locally but passed in all 6 remote Design-A trials, i.e. it is present
but not reproduced across sources — noted here rather than silently assumed universal). No task
name introduces a failure pattern outside the 6 above except `custom-memory-heap-crash` and
`caffe-cifar-10` (both remote-only, both spot-read in full — the other two fix-pass additions,
`rstan-to-pystan` and `train-fasttext`, fit entirely within already-existing patterns and so do not
introduce anything outside the 6). Per this task's Objective 5 granularity guidance ("classify by
distinct failure pattern, citing which real task names exhibit each pattern," not per-trial, given
~150+ failing trials across sources), pattern files cite representative trials with full verbatim
evidence rather than re-deriving a new pattern file for every repeat occurrence of the same
task/pattern pair.

### 8.5 "One taxonomy, two sources" — concrete proof

`docs/benchmarks/failures/README.md`'s combined index (updated by this task) lists golden-suite
and Terminal-Bench entries side by side, sharing the same `cause`/`behavior`/`mechanism` column
headers and, in 2 of 6 Terminal-Bench patterns, the **exact same existing axis values**
(`value-violates-invariant`/`cross-field-invariant-violation` and
`required-section-absent`/`whole-block-absence`) used by real golden-suite cases
(`security-audit-critical-not-fail`; `prepare-release-real-verdict-missing` et al.) — the same
value, unmodified, produced independently by two different benchmark sources.

### 8.6 Fix pass (2026-09-08): 3 remote-only task names missing from the first pass

The first T409 pass (commit `2535a54`, MR !215) derived its headline "17 distinct task names"
count from the **local source alone** and never independently computed the true union of distinct
failing task names across local ∪ remote. Re-deriving both sources' genuine-failure sets
independently (same `exception_info is None and reward == 0.0` method as §8.2, re-run against
every `result.json` in both sources) found:

- Local source: 150 trials, 38 infra-excluded, 71 genuine failures, **17** distinct failing task
  names — matches the first pass exactly.
- Remote source: 150 trials, 19 infra-excluded, 86 genuine failures, **20** distinct failing task
  names — 3 more than the first pass's pattern files cited (`caffe-cifar-10`, `rstan-to-pystan`,
  `train-fasttext`), plus `custom-memory-heap-crash` (already correctly captured in
  `produced-code-fails-to-build.md`, but never folded into the headline "17" count, which should
  always have read "18" even before this fix).

Union of local (17) ∪ remote (20) = **21** distinct task names (16 task names common to both
sources, 1 local-only — `pypi-server` — and 4 remote-only — `caffe-cifar-10`,
`custom-memory-heap-crash`, `rstan-to-pystan`, `train-fasttext`).

Each of the 3 newly-added task names was independently verified against its raw `result.json` and
`verifier/test-stdout.txt` before classification (not taken on the fix-request's characterization
on faith):

- **`caffe-cifar-10`** (1 trial, remote `tb-delta-20260907T162617Z-arm-A`, `Wq8EjvK`) — confirmed a
  fatal `SIGABRT` crash (`returncode: -6`) inside the `caffe.bin` binary's own
  `CopyTrainedLayersFromHDF5()`, triggered by an HDF5 open failure on a `.caffemodel` file that
  training never produced. This does not fit any of the 5 existing patterns (it is a process crash,
  not a graceful missing-file assertion, a live-service-liveness failure, a build failure, or a
  wrong computed value) — a new pattern,
  `docs/benchmarks/failures/terminal-bench/verifier-crashes-on-missing-dependency.md`, was created
  with a new `behavior` (`verifier-subprocess-crashes-fatally`) and `mechanism`
  (`fatal-signal-on-missing-input-artifact`), reusing the existing `agent-incomplete-task-execution`
  `cause`. See that file's "Why this is a distinct pattern" section for the full comparison against
  all 5 pre-existing patterns.
- **`rstan-to-pystan`** (1 trial, remote `tb-delta-20260907T203448Z-arm-B`, `TFqBMv2`) — confirmed
  `alpha_est.csv`/`rho_est.csv` exist and pass 4 of 6 checks, but `test_alpha_estimation_accuracy`
  and `test_rho_estimation_accuracy` fail on out-of-range statistical values. This is the same
  observable shape as `incorrect-computed-output-value.md`'s existing `video-processing` and
  `log-summary-date-ranges` cases (well-formed output, wrong value vs. an independently-known
  correct answer) — added as a new row to that file, no new axis values needed.
- **`train-fasttext`** (4 trials across all 3 remote passes) — confirmed **not uniform**: 3 trials
  (`omH7FVB`, `c96WNaX`, `n8bk9hZ`) show a clean `FileNotFoundError` on `/app/model.bin` (fits
  `required-output-artifact-absent.md`, added there), but the 4th (`UKRXPtU`) has `model.bin`
  present and loadable with wrong accuracy (`0.600325` vs. required `> 0.62`) and oversized model
  (`661644996` vs. cap `157286400`) — that trial fits `incorrect-computed-output-value.md` instead
  and was added there, not to `required-output-artifact-absent.md`. This 3-vs-1 split is called out
  explicitly in both pattern files' trial tables to avoid over-generalizing one task name to a
  single failure shape.

**Corrected totals:** 21 distinct failing task names (was 17), 6 distinct failure patterns (was 5),
71 trial hashes cited across all pattern files (was 65). §8.1, §8.3's genuine-failure/pass totals
(157 failures, 86 passes) were already correct in aggregate and are unchanged by this fix pass —
only the local/remote pass breakdown inside §8.3's parenthetical (41 local, not 45) and the
distinct-task-name/pattern counts throughout §8.1/§8.4 and `docs/benchmarks/failures/README.md`
were wrong and are corrected by this section and the accompanying file edits.
