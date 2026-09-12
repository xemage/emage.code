# Plan 045 — T458 scaling: the real next bounded step between "one case, one trial" and the full harness

> Filename: `plan-045-t458-scaling.md`

**Status:** proposed — presented for review in this session's report, **NOT approved**. This
document mirrors `plan-044-t458-first-slice.md`'s own role and framing exactly: it is an
investigative/scoping pass, not a dispatch. **No task brief is authored and no live trial is run
on the strength of this document alone.** It does not modify `docs/tasks/active-tasks.md` beyond
this document's own commit touching nothing there — no task row is created, transitioned, or
closed by this plan.

**Based on:** `docs/plans/plan-044-t458-first-slice.md` (re-read in full, fresh, from
`origin/develop` this session — the walking-skeleton plan this document scales up from, not
re-derived from any prior summary); `docs/tasks/task-T484.md`, `docs/tasks/task-T485.md`,
`docs/tasks/task-T486.md`, `docs/tasks/task-T487.md` (all re-read in full, fresh, from
`origin/develop` — the four executed slices this plan's entire premise rests on: live dispatch
works, index-build works, a populated vault produces relevant retrieval, and retrieval can
genuinely, traceably influence a live session's output in at least one trial); `docs/tasks/
task-T458.md` (re-read in full, fresh — the original full-harness brief, predates T484-T487,
still `pending`, still not dispatched); `docs/plans/plan-040-t458-golden-live-harness-followup.md`
(re-read in full, fresh — the still-`proposed`, not-approved planning pass T458's brief traces to);
`docs/plans/plan-035-roadmap-v7-ground-up.md` §2.2.1 and §2.4 Phase 1's frozen decision rule (T407's
own `k`-run/spread-based Inconclusive-Null-Positive-Negative design, re-read fresh, reused here only
as a **contrast case**, not a template to copy verbatim — see Finding 2); `docs/decisions/
ADR-004-tb-inconclusive-guardrail-demotion.md` (the real cost/outcome of T407's `k=3` design —
≈$100, 13+ hours wall-clock, landed Inconclusive at spread exactly on the rule's own threshold —
re-read fresh as the closest real precedent for what a naively-copied `k`-run design would cost and
risk here); `docs/artifacts/context-retriever-v1.md` §1 and `implementation/knowledge/agents/
context-retriever.md` "What you do" step 1 (re-read fresh — the real, documented invocation shape:
"receive a query... from the delegating agent," i.e. the calling live session formulates its own
query, not a human-equivalent judgment call made ahead of time — see Finding 4); all 20 real golden
cases' `case.yaml`/`brief.md`/`expect.py` under `tests/golden/{open,held-out}/` (swept fresh this
session, not counted from any prior summary — see Finding 1); `docs/tasks/active-tasks.md` (re-read
fresh from `origin/develop`, confirming current ledger state).

## 0. Re-verified start conditions (fresh this session, not trusted from any prior summary)

- `origin/develop` HEAD independently re-verified via `git fetch origin develop` + `git rev-parse
  origin/develop`: **`36c8271d4ddb9071d00dbfd5145111a7931a98b7`**
  (`Merge branch 'agent/orchestrator/T487' into 'develop'`) — matches the session's stated
  expectation exactly.
- `docs/tasks/active-tasks.md` re-read fresh: exactly four non-terminal rows —
  `T456` (`blocked`, depends on `T454`/`T455` done + `T458` pending), `T457` (`pending`), `T458`
  (`pending`, owner `devops-engineer`, `P1`), `T483` (`pending`). T487's closure note is present and
  matches `task-T487.md` verbatim. T484/T485/T486/T487 are all `done` in `completed-tasks.md`.
  Nothing about this state has changed since T487 closed — T458 remains exactly as scoped in
  `plan-040`, unblocked to dispatch but not yet dispatched at the scale this document investigates.
- The current working branch (`feature/T475-codex-platform-integration`, with pre-existing
  uncommitted changes) was **not touched** — this document was authored in a fresh git worktree
  (`docs/plan-045-t458-scaling`, branched from `origin/develop`), per this session's explicit
  instruction to never touch that branch.
- Max existing plan number on `origin/develop` is `044` (`plan-044-t458-first-slice.md`) — this
  document is `plan-045`, the next free number, not `plan-047` as loosely suggested; verified by
  direct listing, not assumed.

## What T484–T487 actually proved, restated precisely (not overstated)

Four bounded slices, one case (`new-feature-plan-doc-compliant`), executed directly by the
orchestrator (the in-process `Agent` tool dispatch mechanism, since `devops-engineer`'s registered
tool grant has no `agent` tool — plan-044 Finding 3, unchanged):

1. **T484** — the live-dispatch + `expect.py`-reuse mechanism works end-to-end for one case, one
   trial per arm (control = `True`, treatment = `True`, though the treatment arm's retrieval call
   failed on a missing index — an honestly-reported empirical fact, not a mechanism failure).
2. **T485** — a real index can be built against this repo's own vault for the first time
   (0 chunks, because the vault was empty — an honest finding, not a workaround).
3. **T486** — a small, real, non-fabricated 11-entry vault population produces a real, non-empty,
   relevant index (25 chunks) that two independent proof-of-retrieval queries confirmed worked.
4. **T487** — re-running T484's exact mechanism against the now-populated index showed retrieval
   genuinely, traceably influencing the treatment arm's plan-doc content in one specific,
   inspectable way (a Dependency Impact bullet tracing near-verbatim into a retrieved chunk) —
   while **both arms still passed `expect.py` regardless**, and T487's own closure text is explicit
   that "a single observed influence in one trial is not evidence that retrieval reliably helps,
   hurts, or is neutral across cases."

This is the honest floor this plan starts from: **mechanism proven, one case, one trial per arm,
n=1 for everything.** Nothing below assumes more than that.

## Finding 1 — case selection: the 20 cases are not one homogeneous population for this purpose

Swept all 20 real `case.yaml`/`brief.md`/`expect.py` files fresh this session (not counted from any
prior summary). They fall into **four structurally distinct shapes** for live-execution purposes,
not one:

| Shape | Count | Examples | Fit for a live two-arm trial |
|---|---|---|---|
| (a) `open`, `expected_pass`, hand-authored brief, single fresh artifact expected | 7 | `new-feature-plan-doc-compliant` (done), `new-feature-checkpoint-line-compliant`, `plan-required-sections-compliant`, `prepare-release-changelog-grouping-compliant`, `code-review-fail-blocker-details`, `security-audit-coverage-consistency`, `security-audit-verdict-fields-compliant` | **Natural fit** — the brief is an actionable prompt, the pass condition is "did the live session produce one compliant artifact," exactly what T484/T487 already exercised |
| (b) `open`, `expected_pass`, but fixture is a real, already-existing historical artifact pair, not something a live session would freshly author | 1 | `plan-task-creation-precondition-real` (validates that real, already-merged `plan-030`/`task-T365.md` satisfy a precondition — there is nothing for a live session to *write*) | **Poor fit as-is** — running a live session against this brief doesn't test the same property; would need its own redesign, not a silent inclusion |
| (c) `open` or `held-out`, `known_failing` | 9 (6 open + 3 held-out) | e.g. cases whose fixture is a real historical artifact deliberately checked against a contract it fails | **Semantically different question** — the checker here proves the *checker* correctly flags a real historical drift; it does not define what a *fresh live run* of the same brief "should" produce. A live session given the current, correct command template might well produce compliant output where history didn't — that would be a real, interesting finding, but it answers a different question than "does retrieval improve pass rate," and conflating the two would corrupt any aggregate pass-rate comparison |
| (d) `held-out`, `expected_pass` | 3 | e.g. one case per command not in `open/` | Structurally like (a), but every doc this plan or any future task-brief writes must never name a held-out case ID as a bare token, per the vault's own `held-out-isolation-ledger-defect-sweep.md` entry (T486) — an extra discipline requirement, not a blocker, but a real cost |

Of the 20, only **7 cases are the same shape** as what's already been proven (shape a), and of
those 7, one is done (`new-feature-plan-doc-compliant`) and one (`new-feature-checkpoint-line-
compliant`) is the case `plan-044` itself already flagged as materially harder — it requires
reaching Phase 3 of `/new-feature` (a full implementation-and-checkpoint session, not a single
Phase-1 plan doc), confirmed by re-reading its `expect.py`/`brief.md` fresh this session: it
requires the *same* feature reach Phase 3 and produce a `[CHECKPOINT] id=feature-<slug> | done=... 
| in_flight=... | blocked=... | artifact_refs=... | next=...` line — an order-of-magnitude larger
live session than a Phase-1 plan doc.

**Recommendation:** the next bounded step draws only from shape (a), excluding the already-done
case and the harder checkpoint case, and excluding (b)/(c)/(d) pending their own separate scoping
decisions (see "What this document does not resolve" below). That leaves exactly **5 cases**:
`plan-required-sections-compliant`, `prepare-release-changelog-grouping-compliant`,
`code-review-fail-blocker-details`, `security-audit-coverage-consistency`,
`security-audit-verdict-fields-compliant` — spanning all **five** of the suite's distinct commands
(`/new-feature` already covered, plus `/plan`, `/prepare-release`, `/code-review`,
`/security-audit`), each confirmed by direct inspection to require exactly one fresh, Phase-1-
shaped artifact (a plan doc, a changelog, a review doc, or an audit doc respectively) — the same
cheap, low-ambiguity shape `plan-044` deliberately picked for the first case, not a jump to the
suite's hardest cases or to the semantically-different known_failing/held-out categories.

This is a real tradeoff, not a free win: 5 cases is a 5x increase in live sessions over what has
been run so far (10 new trials at one trial per arm, see Finding 6), and it deliberately leaves
13 of 20 cases (the checkpoint case, the one real-fixture oddity, all 6 known_failing, all 6
held-out) unaddressed — each for a stated, disclosed reason, not silently dropped.

## Finding 2 — a `k`-run noise design does not transfer cheaply from Terminal-Bench, and should not be copied uncritically

`plan-035` §2.4's frozen decision rule (`k ≥ 3` per arm, spread-based Inconclusive/Null/Positive/
Negative classification) was designed for **Terminal-Bench's cost structure**: Docker-container
trials, dispatched via Harbor, individually cheap and (per T407/ADR-004's real record) parallelizable
at scale — the actual `k=3` measurement still cost **≈$100 and 13+ hours wall-clock** for a
25-task subset, and it landed **Inconclusive** (Arm A's cross-run spread hit exactly the rule's own
`≥8pp` threshold), which ADR-004 then had to spend a further decision cycle resolving rather than
re-running at higher `k` — explicitly rejected as poor expected value against an instrument the
plan's own authors had already predicted would be under-resolution.

Live-agent trials here are a different cost structure entirely: each trial is a full nested
`Orchestrator`-role `Agent`-tool dispatch producing a complete document from a template — not a
containerized task run. There is no Harbor-equivalent batch runner; each trial consumes this
session's own real wall-clock and context budget, dispatched one or a few at a time (T487 ran
exactly two, in parallel, via `run_in_background`). Naively copying `k=3` onto even the 5-case
expansion in Finding 1 would mean `5 cases × 2 arms × k=3 = 30` live trials just for this step,
before ever reaching the other 13 cases — a scale-up an order of magnitude beyond anything run so
far, undertaken with **zero empirical evidence yet that live-session non-determinism even behaves
the way Terminal-Bench's reward variance does** (a continuous reward metric vs. a binary
`expect.py` pass/fail; T407's own spread units, "percentage points of reward," have no direct
analogue here).

**Recommendation — a two-tier, evidence-first design, not a blanket `k=3`:**

1. **Tier 1 (breadth, `k=1`):** run the 5 new cases from Finding 1 at one trial per arm — matching
   exactly what T484/T487 already did, just across more cases. This is the cheapest way to learn
   whether the *mechanism itself* (dispatch, scratch-dir isolation, `expect.py` reuse) generalizes
   beyond one case and one command, which is a real open question `plan-044`/T484 never had to
   answer (they only ever ran `/new-feature`).
2. **Tier 2 (a targeted noise probe, not a blanket re-run):** separately, run **one already-proven,
   cheap case** (`new-feature-plan-doc-compliant`, the one with the most existing data) for two
   *additional* trials per arm (bringing it to `k=3` total, reusing the one trial already on
   record from T484/T487 as the first of the three) — specifically to get a real, empirical
   measurement of how much a live session's plan-doc output and `expect.py` boolean actually vary
   run-to-run on this repo's own mechanism, before committing to any `k` value for the full harness.
   This is 4 additional trials (2 arms × 2 additional runs), not 30.
3. **Do not pre-commit a `k` value for the eventual 20-case full harness in this document.** Set it
   only after Tier 2's real spread number exists — mirroring the spirit of T407's frozen-rule
   discipline (commit to a rule before seeing results) while refusing to copy a specific numeric
   threshold (`8pp`, `k=3`) that was calibrated for a different metric and cost structure. This is
   explicitly left open, not resolved here — see "What this document does not resolve."

## Finding 3 — the pre-registered "measurably improve" threshold: a process, not a fabricated number

`task-T458.md` Objective #5 requires a threshold be written down *before* any comparison run.
`T456`'s own literal text is the only pre-existing attempt at one: **"If the golden suite does not
improve, the feature does not ship."** This is binary but undefined at the resolution this harness
can actually produce today.

Two concrete problems with inventing a numeric percentage-point threshold right now, both grounded
in what has actually been observed, not speculation:

1. **Statistical resolution.** At 5-6 cases with `k=1`, a pass-rate delta moves in increments of
   `1/N` — one case flipping is a 16-20 percentage-point swing. ADR-004 already shows this failure
   mode playing out at a *much* larger scale (25 tasks, `k=3`) and still landing Inconclusive on a
   spread threshold calibrated for that scale. A percentage-point threshold invented now, before
   Finding 2's Tier 2 probe produces a real spread number, would be exactly the kind of "looks
   rigorous, measures nothing" number this repo's own roadmap (`plan-035` §2.2.1) already warns
   against for a different metric.
2. **T487's own real finding would fail a pass-rate-only definition of "improve."** Both arms
   passed `expect.py` regardless of retrieval — a pass-rate-only threshold would call T487's own
   genuine, traceable, directly-inspected content influence a "no effect," which misdescribes what
   actually happened. A threshold that only looks at the binary pass/fail signal is not yet honest
   about what this harness's real, current evidence looks like.

**Recommendation — a concrete two-part process, not a fabricated number:**

1. **A non-regression floor, statable now:** across whatever case set is actually run, **treatment
   pass rate must not be lower than control pass rate.** This is the same "no-harm guardrail"
   posture ADR-004 already adopted for Terminal-Bench after its own signal proved unable to resolve
   a positive effect — a floor, not a claim of improvement, and cheap to state honestly today
   because it requires no calibration.
2. **A qualitative supplementary signal, using T487's own already-demonstrated method:** for cases
   where the treatment arm's retrieval call returns non-empty results, perform the same direct,
   manual diff T487 already used (compare control vs. treatment output section-by-section, trace
   specific retrieved phrases into specific output content) and report the fraction of such cases
   showing a genuine, traceable influence — explicitly reported as **descriptive, not a pass/fail
   gate**, until a case count large enough to support a real proportion exists (this document does
   not assert what that count is — that determination should itself wait for Finding 2's Tier 1/2
   results).
3. **A quantitative percentage-point threshold is deliberately deferred**, to be set as a **dated
   successor** to this document (mirroring `plan-035` §2.4's own supersession mechanism for its
   frozen TB rule) once Tier 1 (case breadth) and Tier 2 (the noise probe) produce real numbers to
   calibrate against — not invented here without that evidence.

## Finding 4 — query strategy: the real documented usage pattern is agent-formulated, not human-picked

Re-read `implementation/knowledge/agents/context-retriever.md` "What you do" step 1 fresh this
session: **"Receive a query (natural-language question, symbol name, or task description) from the
delegating agent."** The real, documented invocation shape is that the *calling live session*
formulates its own query based on its own reasoning about the task at hand — retrieval is
something an agent reaches for and phrases itself, not a fixed string handed to it externally.

T487's own design deviated from this, necessarily, for a first proof-of-influence trial: the
orchestrator inspected the vault's real 11 entries, chose a query text it judged plausible for the
task, **confirmed that exact string worked against the index before ever handing it to the
treatment arm**, and only then dispatched it. T487's own text is honest about this being "a real
question a session about to write this case's Task Breakdown / Dependency Impact sections would
plausibly ask" — a defensible choice for n=1, but a human-curated golden query nonetheless, with
the human doing the curating already knowing what was in the (small) vault.

**Recommendation:** for the case-diversity expansion in Finding 1, treatment-arm sessions should be
given the real, corrected CLI invocation shape and told they *may* consult it, and must decide for
themselves what to query (if anything) and how to use the results — matching the real agent-facing
instruction verbatim, not a pre-vetted query string. This matters for the following reason, stated
directly: continuing T487's hand-picked-query pattern at N=5-6 would mean every trial's retrieval
quality is upper-bounded by the orchestrator's own advance knowledge of the vault's contents — an
experimenter-selection bias that would make any observed influence evidence about "how good is a
hand-tuned query," not "is retrieval useful as an agent actually invokes it." The real tradeoff:
agent-formulated queries are noisier and may retrieve irrelevant top-k results the treatment arm
correctly ignores (as it already did for 3 of 5 hits in T487, even with a good query) — a
"no observable influence" result under this design is a legitimate, disclosable finding about
real-world query quality, not a mechanism failure to route around.

## Finding 5 — vault content adequacy: a real chicken-and-egg problem, named explicitly

T486's 11 entries were deliberately drawn from real, already-merged content that happened to be
genuinely useful *on its own merits* (protected-path policy, branch policy, memory-layer
architecture, blocker/validation-gate protocol, tool-grant discipline) — none of it targets the
substantive content of `/plan`, `/prepare-release`, `/code-review`, or `/security-audit`'s own
command templates (required headers, changelog grouping, verdict field formats). Combined with
Finding 4's recommendation (agent-formulated queries, not hand-picked), this produces a real,
disclosable prediction, stated here *before* any trial runs (per this document's own "state before
seeing results" discipline): **most Tier-1 trials on the 5 new cases will likely retrieve low-
relevance or no-relevant results**, because the vault's current topical coverage doesn't overlap
much with what those cases' own tasks are actually about.

This is a genuine chicken-and-egg tension, not a false one: to get a *meaningful* multi-case
comparison across diverse commands, the vault plausibly needs entries relevant to each command's
own domain — but authoring those entries by looking at the golden-suite cases first and writing
vault content to match them would **rig the comparison**, turning "does retrieval help" into a
circular, self-confirming exercise. T486's own brief already modeled the discipline that avoids
this (every entry "sourced from real, already-merged repo content, not fabricated... for the sake
of testing") — that discipline has to hold for any future vault growth too, or the eventual full-
harness result would not be honest evidence of anything.

**Recommendation:**
1. Run Finding 1's Tier 1 expansion **without** growing the vault first, and pre-register the
   expectation above (low/no-relevant-hit trials are likely and are not a mechanism failure) so a
   null retrieval result isn't later mistaken for a bug.
2. If a future step wants to grow the vault, source new entries the same way T486 did — real,
   independently-useful repo content, never authored by looking at which golden case needs a hit —
   and treat vault-growth and case-diversity-expansion as **separate, independently-attributable
   steps**, never bundled into the same dispatch, so any change in results can be traced to one
   cause, not a tangle of two.

## Finding 6 — cost/scope estimate for the recommended next step

Recommended scope, concretely:

| Component | Trials | Notes |
|---|---|---|
| Tier 1 — 5 new cases × 2 arms × `k=1` | 10 live trials | Finding 1 |
| Tier 2 — 1 already-proven case × 2 arms × 2 *additional* trials (reaching `k=3` total, reusing the 1 existing trial per arm) | 4 live trials | Finding 2 |
| **Total new live trials this step** | **14** | Brings the cumulative total (T484: 2, T487: 2) to **18 live sessions** run to date |

Each trial is a full nested `Orchestrator`-role live session producing one Phase-1-shaped artifact
from a template (comparable in size to T484/T487's own trials) — order-of-magnitude a few thousand
to low tens of thousands of tokens per trial including the artifact itself, the dispatch prompt,
and this session's own verification pass (independent re-inspection of headers, re-run of
`check()`, in T486/T487's own established pattern of not trusting a self-report alone). Across 14
trials, a reasonable order-of-magnitude estimate is **on the order of 150k-300k tokens of total
session activity**, which exceeds this project's own single-phase token budget (`AGENTS.md`:
Implementation ≤120k tokens) and should be split across **at least two dispatch batches with an
intervening checkpoint**, not attempted in one uninterrupted pass. Wall-clock-wise, running arms in
parallel per case (as T487 already did) keeps this to roughly 5-7 dispatch rounds rather than 14
sequential ones, but this is still a multi-hour, multi-checkpoint undertaking, not a quick
follow-up.

**Cost-authorization determination:** this recommended scope uses exactly the same mechanism
T484-T487 already used and the user already found not to require authorization — the in-process
`Agent`-tool dispatch (ordinary interactive-session usage) and the local, zero-cost `fastembed`
embedding pipeline (no metered API, per ADR-005 Decision 2 and T485's own precedent). **This
recommended next step does not cross into T407's "paid/recurring-cost API call" money-gate
territory** — no new authorization is being requested or flagged as needed for the 14-trial scope
above. This is stated explicitly, not left ambiguous, because it is a real determination this
document is responsible for making, not a default assumption.

This determination does **not** extend to the eventual full-harness ambition. A rough projection:
even after Finding 1's category exclusions, a genuinely full run (remaining shape-(a) cases +
the harder checkpoint case + a resolved treatment of shape (b)/(c)/(d), at whatever `k` Finding
2's Tier 2 probe justifies) plausibly reaches on the order of **60-120+ live trials** — a scale
where, even absent a literal dollar cost, the sheer session-count/wall-clock commitment starts to
resemble a dedicated compute campaign rather than "ordinary interactive usage," and is flagged here
as **likely warranting its own explicit scope/budget conversation with the user before dispatch**,
not something this document authorizes by extension.

## What this document does not resolve (explicitly deferred, not silently dropped)

- **Shape (b)** (`plan-task-creation-precondition-real`) — this case's fixture is already-existing
  real historical content with nothing for a live session to freshly author; whether/how to adapt
  it for live execution (or exclude it permanently) is not decided here.
- **Shape (c)** (9 `known_failing` cases) — what "pass/fail" should even mean for a live run of a
  known_failing case's brief (a fresh session isn't reproducing a fixed historical drift) is a
  real, separate design question this document surfaces but does not answer.
- **Shape (d)** (6 `held-out` cases) — deferred, both because they raise the case-ID non-disclosure
  discipline the vault's own `held-out-isolation-ledger-defect-sweep.md` entry (T486) already names,
  and because folding held-out cases into an *improvement-measurement* comparison (rather than a
  final held-out verification pass) needs its own explicit decision about what that would even mean
  for the suite's held-out/open separation.
- **The exact numeric "measurably improve" threshold** — Finding 3 proposes a process and a floor,
  not a final number; the number itself is deferred to a dated successor document once Finding 2's
  Tier 1/2 results exist.
- **The exact `k` value for the full 20-case harness** — deferred to the same successor, pending
  Tier 2's real spread measurement.
- **Whether/how to grow the vault beyond T486's 11 entries** — Finding 5 names the tension but does
  not resolve it; this document does not propose new vault content.
- **Whether `devops-engineer` should ever become the real executing owner** for a harness at this
  scale, versus the orchestrator continuing to execute bounded slices directly (`plan-044` Finding
  3's still-unresolved Question 1/2) — unchanged by this document.

## What this document is not

- It is not `docs/tasks/task-T458.md`'s dispatch, and it does not modify that brief.
- It is not a new task brief — no `docs/tasks/task-T4xx.md` is authored by this document, and
  `docs/tasks/active-tasks.md`/`completed-tasks.md` are untouched.
- It does not authorize any live trial, any vault-content change, or any `k`-run measurement.
- It does not touch `tests/golden/**`, `scripts/scorecard.py`, `docs/benchmarks/tb-subset.json`/
  `.md`, `.mcp.json`, or `feature/T475-codex-platform-integration`.
- It does not authorize any paid/metered API usage, and does not itself request authorization for
  anything beyond what T484-T487 already established as unnecessary for the scope in Finding 6.
- It is not an approval of `plan-040` or `task-T458.md` — both remain exactly as found, `proposed`/
  `pending`, unapproved for full dispatch.

## Approval

- [ ] User reviews Findings 1-6 and the six explicitly-deferred items above
- [ ] User approves (or modifies) Finding 1's case selection (5 named cases) as the next
      authorized case-diversity step, distinct from approving the full `task-T458.md` brief
- [ ] User approves (or modifies) Finding 2's two-tier design (Tier 1 breadth at `k=1`, Tier 2 a
      4-trial noise probe on one existing case) as the next authorized trial-count step
- [ ] User approves (or modifies) Finding 3's process (non-regression floor now, qualitative
      diff-based reporting, numeric threshold deferred to a dated successor)
- [ ] User approves (or modifies) Finding 4's agent-formulated-query design for treatment arms
- [ ] User acknowledges Finding 5's chicken-and-egg vault-content tension and confirms no vault
      growth is authorized alongside this case-diversity step
- [ ] User confirms Finding 6's cost/scope estimate (14 new live trials, no new cost authorization
      needed at this scope) before any dispatch
- [ ] Plan locked; revisions create `plan-045-t458-scaling-v2.md`
