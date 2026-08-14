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
| `required-section-absent` | A declared section/field-group is completely missing from the document (no partial trace of it anywhere). | `code-review-conditional-pass-conditions-gap`, `prepare-release-conditional-pass-conditions-gap`, `prepare-release-real-verdict-missing`, `held-out-case-4` |
| `required-marker-line-absent` | A specific declared single-line marker convention never appears anywhere in the real corpus surveyed. | `new-feature-real-checkpoint-format-drift` |
| `naming-or-format-drift` | The conceptual content is present in the document, but expressed under different header names, inline formatting, or a different naming/filename pattern than the declared spec. | `plan-real-doc-header-drift`, `held-out-case-1`, `held-out-case-3` |
| `value-violates-invariant` | All required fields are present and individually well-formed, but their combined values contradict an explicitly declared cross-field rule. | `security-audit-critical-not-fail` |

`required-section-absent` and `required-marker-line-absent` are kept separate rather than merged
into one "absent" bucket because they differ in grain: a *section* is a multi-line structural
unit (a whole `##` block or field-group), while the one real case in
`required-marker-line-absent` is specifically a single required line with no surrounding
block — worth distinguishing because "add a missing line" and "add a missing section" are
different-sized fixes, and a future case could exercise either independently of the other.

### 3.3 `mechanism` — how/where the gap manifests structurally

| Value | Definition | Real cases |
|---|---|---|
| `whole-block-absence` | An entire required heading/section/marker is missing — no partial container for it exists anywhere in the document. | `new-feature-real-checkpoint-format-drift`, `prepare-release-real-verdict-missing`, `held-out-case-4` |
| `field-level-absence-within-declared-block` | The surrounding block/convention *is* present (e.g. a verdict block with a `Status` field exists), but one specific sub-field the contract requires — with no declared schema for it — is missing from within it. | `code-review-conditional-pass-conditions-gap`, `prepare-release-conditional-pass-conditions-gap` |
| `naming-convention-drift` | Required content is present in some structural form, but under different header/field names or a different naming pattern than declared. | `plan-real-doc-header-drift`, `held-out-case-1`, `held-out-case-3` |
| `cross-field-invariant-violation` | Individually well-formed, present fields whose combined values break a declared cross-field rule. | `security-audit-critical-not-fail` |

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
