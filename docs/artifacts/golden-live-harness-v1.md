# Golden Live-Execution Harness — v1

**Status:** Implemented (non-dispatch half only — see "What this is not" below).
**Owner:** `devops-engineer` (T458, split-ownership dispatch).
**Based on:**
- `docs/tasks/task-T458.md` — the dispatch brief this artifact fulfills Expected Output #2 of.
- `docs/plans/plan-048-t458-k-threshold-decision.md` §7 — the authoritative, already-decided
  k/escalation/floor-tolerance policy this document maps to code, not re-derives.
- `docs/plans/plan-044-t458-first-slice.md` — the walking-skeleton design (scratch isolation,
  `expect.py` reuse via `importlib.util.spec_from_file_location`) this artifact formalizes.
- `docs/tasks/task-T484.md`, `docs/tasks/task-T493.md` — the real trial execution notes this
  code's shapes (scratch layout, call shapes, classification worked examples) are drawn from.
- `docs/artifacts/golden-suite-format-v1.md` §4.1 — the `expect.py` contract reused unmodified.
- `scripts/scorecard.py` — the `load_expect_module()` pattern this code mirrors, not imports from.

## 1. Where the code lives, and why

`implementation/runtime/golden_harness/` — a new runtime subsystem package, alongside this
repo's existing `implementation/runtime/{handoff,cwso,telemetry,triggers,memory}/` convention for
runtime subsystems (the same precedent T452's own closure note cites for putting the memory
pipeline there rather than in `scripts/`). This task's deliverable is four cooperating modules
(scratch isolation, scoring, trial store, policy) with real internal dependencies between them
(policy operates on trial-store records; scoring produces the boolean a trial record stores) —
a package fits that shape better than a handful of unrelated one-off scripts under `scripts/`.

```
implementation/runtime/golden_harness/
├── __init__.py       # package docstring, no dispatch mechanism of any kind
├── schema.py          # TrialRecord, ALLOWED_ARMS/ALLOWED_CATEGORIES, validate_trial_record
├── scratch.py          # create_scratch_case_dir, write/copy_candidate_file, cleanup_scratch_dir
├── scoring.py           # load_expect_module, score_scratch_dir, find_golden_case_dir
└── trial_store.py        # append_trial, load_trials, trials_for_case, next_k_index
└── policy.py               # plan-048 §7's policy, as callable functions
```

Tests: `tests/functional/test_golden_harness_{scratch,scoring,trial_store,policy}.py`, wired into
`python3 tests/run.py`'s default (`functional`) tier — no `EMAGE_*` opt-in gate was needed because
every test in all four files uses synthetic/recorded data, never a live agent session (see §5).

## 2. Trial isolation (Objective #1 → `scratch.py`)

Formalizes exactly the isolation shape every one of the 28 real trials behind `plan-048` already
used by hand. `task-T484.md`'s Execution notes state it plainly: *"Two nested ... sessions were
dispatched ... each confined by instruction to its own isolated plain scratch directory
(`/tmp/.../scratchpad/t484-control/workdir` and `.../t484-treatment/workdir` — neither under the
repo, neither a git worktree)."*

`create_scratch_case_dir(case_id, arm, k_index, base_dir=None)` creates and returns a fresh
directory under `base_dir` (or a new `tempfile.mkdtemp()` root if `base_dir` is omitted), uniquely
named per `(case_id, arm, k_index)`, with an empty `fixture/` subdirectory already created. This
directly matches the on-disk shape `expect.py`'s real, unmodified contract expects
(`case_dir / "fixture" / <relative-path>`, per `golden-suite-format-v1.md` §4.1 and confirmed
empirically by every real trial's actual layout, e.g. `<scratch>/fixture/docs/plans/
feature-<slug>.md` for `/new-feature` cases). It is **never** a git worktree and **never** the main
checkout — the same two properties `plan-044` Finding 1 and every trial since have relied on.

`write_candidate_file(case_dir, relative_path, content)` and `copy_candidate_file(case_dir,
relative_path, source_path)` place a live session's produced output at the exact relative path a
case's `expect.py` expects, from either captured text or an on-disk file the session itself wrote.
`cleanup_scratch_dir(case_dir)` removes one trial's own scratch directory (not its `base_dir`
parent, which may still hold sibling trials).

This module creates directories and copies/writes files only. It contains no dispatch call of any
kind — populating `fixture/` with a live session's real output is the caller's (orchestrator's)
job, done after that session completes, using these two helpers.

## 3. Scoring (Objective #2 → `scoring.py`)

`load_expect_module(golden_case_dir)` loads `golden_case_dir / "expect.py"` via
`importlib.util.spec_from_file_location` — the identical pattern `scripts/scorecard.py`'s own
`load_expect_module()` already uses (mirrored in shape only; `scripts/scorecard.py` is a protected
path per `docs/artifacts/protected-paths-v1.md` and is never imported from). `score_scratch_dir
(golden_case_dir, scratch_case_dir)` calls `module.check(scratch_case_dir)` and returns the real
boolean — the same call shape `task-T484.md` and `task-T493.md`'s Execution notes both describe by
hand. `find_golden_case_dir(case_id, golden_root)` resolves a case id to its real directory by
recursively globbing for `expect.py` (mirroring `scripts/scorecard.py`'s own directory-shape-
agnostic `discover_case_dirs()`), so it works whether a case lives under `open/`, `held-out/`, or
any future layout without hardcoding either name.

**Blocker case 1, resolved in the negative (no protected-path exception needed):**
`task-T458.md`'s own Blocker Protocol names "can `expect.py`'s contract be pointed at a scratch
dir without a protected-path edit?" as a pre-anticipated case. `plan-044` Finding 1 already
answered this for all 20 real cases (`case_dir` is a parameter, not a hardcoded path, in every
real `expect.py`). `tests/functional/test_golden_harness_scoring.py`'s
`TestScoreScratchDirAgainstRealExpectPy` class re-confirms this directly and mechanically: it
loads the real, unmodified `tests/golden/open/new-feature-plan-doc-compliant/expect.py` and scores
two synthetic scratch directories against it (one compliant, one missing a required header),
getting `True`/`False` as expected — with **zero edits anywhere under `tests/golden/`**. No
exception was requested or needed.

## 4. Trial-record schema and store (Objective #3 → `schema.py` + `trial_store.py`)

`TrialRecord` (a frozen dataclass) carries exactly the fields `task-T458.md`'s Objective #3 names:
`case_id`, `arm` (`"control"` / `"treatment"`), `k_index` (1-based, per case+arm), `result`
(the real boolean from §3), `category` (plan-048 §5's qualitative rubric, `"1"`-`"5"` or `None`),
`diagnosed_cause` (free-text label for a floor-relevant failure, or `None`), plus `command` and
`recorded_at` for readability/provenance. `validate_trial_record()` checks `arm`/`k_index`/
`category` against their allowed value sets without raising — callers decide whether a validation
failure is fatal.

`trial_store.py` is an append-only JSONL file, one `TrialRecord` per line, mirroring this repo's
existing deterministic-JSONL convention (`implementation/runtime/memory/index_writer.py`'s
`_write_jsonl`/`_read_jsonl`). `append_trial(store_path, record)` appends one line;
`load_trials(store_path)` reads them all back; `trials_for_case(trials, case_id, arm=None)` filters
an already-loaded list (pure, in-memory — no re-read per query); `next_k_index(trials, case_id,
arm)` computes the next 1-based `k_index` to use for a new trial. The store's location is always
caller-supplied — no default path, and nothing under `tests/golden/**` is ever written to.

Per `task-T458.md`'s own Constraints, **no retroactive re-encoding of the 28 historical trials
into this schema was attempted** — that remains optional, disclosed scope, not a precondition. The
store and schema work for new trials regardless.

## 5. `plan-048` §7 policy → code (Objective #4 → `policy.py`)

Every sentence in `plan-048` §7 ("What this document actually resolves, stated plainly") maps to
one function below. This table is the artifact a future reader uses to verify the code matches
decided policy without re-deriving it, per `task-T458.md`'s own Expected Output #2 requirement.

| `plan-048` §7 statement | Function(s) |
|---|---|
| "default `k=1`" | `DEFAULT_K = 1` |
| "escalate to `k>=3` on `k=1` arm disagreement (Part A...)" | `should_escalate()` → `EscalationDecision(True, TRIGGER_DISAGREEMENT)` when `control_k1.result != treatment_k1.result` |
| "separately escalate any unanimous case whose treatment trial showed a category-3 finding, to test reproducibility (Trigger 2...)" | `should_escalate()` → `EscalationDecision(True, TRIGGER_REPRODUCIBILITY_CHECK)` when arms agree and `treatment_k1.category == "3"` |
| "classify every `k>=3` result into one of three named outcomes — confirmed coin-flip, confirmed persistent effect, or elevated-but-heterogeneous (open) — rather than forcing a two-outcome call" | `classify_k_plus_outcome()` → one of `CONFIRMED_COIN_FLIP` / `CONFIRMED_PERSISTENT_EFFECT` / `ELEVATED_BUT_HETEROGENEOUS`, never a binary |
| §4: "a floor miss is actionable only once its specific diagnosed cause recurs across ≥2 trials within the same case; a floor miss whose causes have each occurred exactly once stays open" | `is_floor_miss_actionable(cause_occurrences)` (used internally by `classify_k_plus_outcome`, also independently callable/testable); `count_cause_occurrences()` computes the arm-agnostic per-cause counts it reads |
| §7 worked example: `code-review-fail-blocker-details` "closes as resolved noise" (floor met, 1/3 vs 1/3) despite a cause recurring across arms | `classify_k_plus_outcome()`'s floor-first ordering — `floor_met()` is checked **before** cause recurrence, so a met floor always yields `CONFIRMED_COIN_FLIP` even if a cause happens to recur evenly across both arms; see `test_code_review_fail_blocker_details_is_confirmed_coin_flip` |
| §7 worked example: `security-audit-coverage-consistency` "stays open" at `plan-048`'s own k=3 snapshot, later promoted to a "confirmed, real checker-brittleness pattern" at k=5 (`task-T493.md`) | `classify_k_plus_outcome()` returns `ELEVATED_BUT_HETEROGENEOUS` on the k=3 trial set and `CONFIRMED_PERSISTENT_EFFECT` on the k=5 trial set — both reproduced exactly as real historical fixtures in `test_golden_harness_policy.py` |
| §5: "2 of 11 classified treatment trials (18%) — or, conservatively ..., 2 of 14 (14%) — showed a traceable positive influence" | `compute_base_rate()`, reproduced from raw `TrialRecord`s, not hardcoded — see §6 below |

### A disclosed judgment call: ordering floor-met before cause-recurrence

`plan-048` §3 and §4 describe two related but separately-stated rules (the three-outcome
classification, and the floor-tolerance recurrence rule) without spelling out, as a single
formula, exactly how they compose when a floor *is* met but a cause still recurs. This case is
real in the evidence base: `code-review-fail-blocker-details`'s `owner_field_inline_prose` cause
recurs exactly twice (control-3, treatment-3) — satisfying §4's literal "recurs across ≥2 trials"
wording — yet `plan-048` §7 states this case "closes as resolved noise," not as a confirmed
persistent effect. Reading §4's own worked explanation for this case closely
(*"the recurring `Owner`-field cause is a real, repeat-observed checker brittleness, but it
strikes both arms roughly evenly, so it is not a retrieval-attributable regression"*), the
implemented reading is: **the floor-tolerance recurrence rule exists to decide whether an
*already-observed floor miss* is actionable — it is not itself a trigger for reclassifying a case
whose floor is met.** `classify_k_plus_outcome()` therefore checks `floor_met()` first and only
consults cause recurrence when the floor was missed. This reading was checked against all three
real worked examples in `plan-048`/`task-T493.md` (§6 above) and reproduces every one of them
exactly — it is disclosed here as a judgment call rather than silently assumed, per
`task-T458.md`'s Blocker Protocol case 2's own spirit (an imperfect-record reading, disclosed
rather than blocking), even though this specific instance is a policy-composition reading rather
than a base-rate-reproduction ambiguity.

## 6. The base-rate reproduction (Blocker case 2, resolved — not ambiguous)

`task-T458.md`'s Blocker Protocol names reproducing `plan-048`'s stated base rate (2 of 11, 18%)
from historical records as a case that "may prove genuinely ambiguous." `compute_base_rate(trials)`
computes it generically from any `TrialRecord` list: among treatment-arm trials, how many were
qualitatively classified at all (`category is not None`), and of those, how many landed in
category 3 ("traceable positive influence")? It reports both `rate_of_classified` (over classified
trials only) and `rate_conservative` (over all treatment trials, treating unclassified ones as
non-category-3) — the same two framings `plan-048` §5 itself states side by side.

`tests/functional/test_golden_harness_policy.py`'s
`test_reproduces_plan_048_base_rate_from_reconstructed_records` reconstructs `plan-048` §5's real
14-trial table (5× category 2, 2× category 3, 1× category 4, 3× category 5, 3× unclassified) as
synthetic `TrialRecord`s and confirms `compute_base_rate()` returns exactly 2/11 (≈18.18%) and
2/14 (≈14.29%) — matching `plan-048`'s own "18%, or 14% conservatively" statement precisely. **This
was not ambiguous in practice** — `plan-048` §5 already states its own population and per-category
counts explicitly (unlike the per-trial pass/fail causes, which required more interpretive work
per §5 above) — so no blocker was raised for this case.

## 7. Entry points for the orchestrator's own live-trial exercise

These are the exact functions the orchestrator calls directly for its own next live dispatch
(`task-T458.md` Objective #5 / Expected Output #3) — not reinvented, not wrapped further by this
package:

```python
from pathlib import Path
from implementation.runtime.golden_harness.scratch import create_scratch_case_dir, write_candidate_file
from implementation.runtime.golden_harness.scoring import find_golden_case_dir, score_scratch_dir
from implementation.runtime.golden_harness.schema import TrialRecord
from implementation.runtime.golden_harness.trial_store import append_trial, load_trials, next_k_index

# (a) create an isolated scratch dir for one trial
case_dir = create_scratch_case_dir("new-feature-plan-doc-compliant", "control", k_index=1, base_dir=my_scratch_root)

# ... dispatch the live session via the in-process Agent tool, instructing it to work in case_dir ...
# ... then place its real output at the case's expected relative path ...
write_candidate_file(case_dir, "docs/plans/feature-<slug>.md", session_output_text)

# (b) score the scratch dir against the case's real, unmodified expect.py
golden_case_dir = find_golden_case_dir("new-feature-plan-doc-compliant", Path("tests/golden"))
result = score_scratch_dir(golden_case_dir, case_dir)  # real bool

# (c) record the trial
store_path = Path("docs/benchmarks/trials/new-feature-plan-doc-compliant.jsonl")  # any caller-chosen path
existing = load_trials(store_path)
k = next_k_index(existing, "new-feature-plan-doc-compliant", "control")
append_trial(store_path, TrialRecord(case_id="new-feature-plan-doc-compliant", arm="control", k_index=k, result=result))
```

`policy.should_escalate(control_k1, treatment_k1)` and `policy.classify_k_plus_outcome(trials)`
are called the same way once k=1 (or k>=3) results are recorded, per §5's mapping table above.

## 8. What this is not

- **Not a dispatch mechanism.** No function anywhere in `implementation/runtime/golden_harness/`
  calls the in-process `Agent` tool or a `claude` CLI subprocess. Launching the live
  control/treatment session itself, and placing its output where `write_candidate_file`/
  `copy_candidate_file` expect it, remains the orchestrator's job (`task-T458.md` Objective #5).
- **Not a retroactive re-encoding of the 28 historical trials** — optional, disclosed, not
  attempted this task, per `task-T458.md`'s own Constraints.
- **Not T456's ship/no-ship measurement**, and not `plan-048` §6's still-open follow-up items
  (a harder vault-dependent case; scaling to 30-50 trials for a numeric threshold) — both remain
  separately-scoped, not-yet-dispatched future work.
