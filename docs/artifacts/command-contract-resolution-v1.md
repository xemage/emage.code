# Artifact: command-contract-resolution-v1.md

> Filename: `command-contract-resolution-v1.md`. Immutable once produced; revisions bump `<N>`.

## Metadata

- **Producer agent**: solution-architect
- **Task**: T515
- **Created**: 2026-09-25
- **Based on**: `docs/tasks/task-T515.md`; `docs/plans/plan-066-t515-command-contract-authority.md`;
  `docs/decisions/ADR-007-command-contract-authority.md` (the decision this table implements);
  `tests/golden/README.md`; `docs/artifacts/maturity-promotion-criteria-v1.md` §3.5;
  `docs/artifacts/protected-paths-v1.md`; `AGENTS.md`.
- **Supersedes**: none (first version)

## 0. What this document is

`ADR-007` states the principle. This is the operational table: one row per `tracked_defect` golden
case, with the verdict, the clause at issue, what happens to the paired sibling, what a follow-up
implementation task would have to touch, and the promotion impact.

**This task changed no command file, no `expect.py`, and nothing under `tests/golden/`.** Those edits
belong to a follow-up task carrying an explicit `protected-paths-v1.md` §5 authorization scoped to
named files. Everything below is a specification for that task, not a record of work done.

## 1. Enumeration (own scan, not copied)

Six cases carry `status: known_failing` with `known_failing_category: tracked_defect`, found by
reading every `case.yaml` under `tests/golden/open/` and `tests/golden/held-out/`:

| Label | Case | Command | Location |
|---|---|---|---|
| **A** | `plan-real-doc-header-drift` | `/plan` | `open/` |
| **B** | `new-feature-real-checkpoint-format-drift` | `/new-feature` | `open/` |
| **C** | `prepare-release-real-verdict-missing` | `/prepare-release` | `open/` |
| **D** | `security-audit-critical-not-fail` | `/security-audit` | `open/` |
| **H-1** | *(held out — deliberately not named)* | *(withheld)* | `held-out/` |
| **H-2** | *(held out — deliberately not named)* | *(withheld)* | `held-out/` |

This matches `tests/golden/_manifest-t411.md`'s count; it was derived independently and then
cross-checked against the manifest, not read off it.

**Held-out discipline.** `tests/functional/test_golden_held_out_isolation.py` Check B fails the build
on any mention of a held-out case ID outside `tests/golden/`. H-1 and H-2 are therefore identified
here only by verdict branch. The implementing task will be authorized to read
`tests/golden/held-out/` and can recover which is which in one step by applying §2 of `ADR-007` to
the two `case.yaml` files there. Agent-level promotion impact is stated jointly for the pair, to
avoid pairing a branch to a command. The command-level identity of H-1 and H-2 is withheld on
purpose, and the resulting loss of precision in this table is a deliberate, disclosed cost.

## 2. The verdict vocabulary

Per `task-T515.md` §5. Each verdict below cites the branch of `ADR-007` §2's decision procedure it
comes from:

- **Branch 1 — amend the contract.** The clause contradicts a higher-authority document.
- **Branch 2 — reclassify (wrong artifact class).** The fixture is not an instance of the class the
  clause governs.
- **Branch 3a — amend the contract (relabelling).** The corpus carries the same content under
  different labels *and* offers a single coherent alternative.
- **Branch 3b — fix the corpus (omission).** The corpus lacks the declared content.
- **Branch 4 — reclassify (no corpus).** A hand-authored counter-example; not a contract-vs-corpus
  conflict at all.

## 3. Resolution table

### A — `plan-real-doc-header-drift` (`/plan`, `open/`)

| Field | Value |
|---|---|
| **Clause at issue** | `implementation/knowledge/commands/plan.md` step 5, two separable halves: **(a)** the output path `docs/plans/<slug>-plan.md`; **(b)** the six section names `Goal`, `Task Decomposition`, `Dependency Graph`, `Resource Assignments`, `Risk Assessment`, `Open Questions`. |
| **Verdict (a) — path** | **Amend the contract** (branch 1). |
| **Verdict (b) — section names** | **Fix the corpus** (branch 3b). Contract stands unchanged. |
| **Why (a)** | `plan.md` contradicts *itself*: step 5 says `docs/plans/<slug>-plan.md`, while the same file's "Task Creation Precondition" section says the plan document lives at `docs/plans/plan-<ID>.md`. 8 of 8 sampled real plan documents follow the second form. An internal contradiction is resolved against the clause the rest of the file and the whole corpus disagree with. |
| **Why (b)** | Branch 3a was considered and rejected on evidence. The corpus does **not** offer a single coherent alternative convention: 8 sampled plan documents use 8 different structures (§5). Only one of them (`plan-030`, this case's own fixture) carries all six required concepts at all; the rest *omit* sections outright. Adopting `plan-030`'s labels would elevate one document's idiosyncrasy to a convention and would convert a check with real discriminating power into one that rubber-stamps a single artifact. |
| **Paired sibling** | `plan-required-sections-compliant` (`open/`, hand-authored, currently passing). **Fate: survives, with one mechanical change.** Its `check()` globs `*-plan.md`, i.e. it encodes step 5's *wrong* path form; when (a) lands, its glob and its fixture filename must be updated to `plan-*.md`. The six-header check, the ordering requirement and the mermaid requirement are all untouched — no loss of strength. |
| **Does the case pass after the fix?** | **No. It stays `known_failing`.** The fixture is a verbatim copy of `docs/plans/plan-030-mcp-remote-transport-alignment.md`, a shipped document that drove real tasks T360–T367. Retro-editing it is forbidden by `AGENTS.md`'s immutability convention, so this frozen fixture can **never** pass verdict (b). |
| **Files a follow-up would touch** | `implementation/knowledge/commands/plan.md` (step 5 path only); `tests/golden/open/plan-required-sections-compliant/expect.py` (glob) and its `fixture/docs/plans/` filename; **protected-path authorization required**. |
| **Recommended exit** | Re-fixture the case against the first plan document authored *after* the contract is reaffirmed, i.e. earn the pass by producing a conforming plan. Until one exists the case is a standing red. Do **not** relax the header list. |
| **Promotion impact** | **Unblocks nothing.** `/plan` keeps an open `tracked_defect`, so `/plan` still fails command criterion 7, and `orchestrator` still fails agent criteria 3 and 7 transitively. |

### B — `new-feature-real-checkpoint-format-drift` (`/new-feature`, `open/`)

| Field | Value |
|---|---|
| **Clause at issue** | `implementation/knowledge/commands/new-feature.md` Phase 3 step 7: a single-line `[CHECKPOINT] id=feature-<slug> \| done=[...] \| in_flight=[...] \| blocked=[...] \| artifact_refs=[...] \| next=[...]` marker, stored at `docs/checkpoints/checkpoint-feature-<slug>.md`. |
| **Verdict** | **Amend the contract** (branch 1). |
| **Why** | Direct contradiction with `AGENTS.md` § Checkpoint Protocol, the highest-authority document in this repository. `AGENTS.md` mandates `docs/checkpoints/checkpoint-<SEQ>-<phase>.md` and a document containing completed tasks, key decisions, blockers, token metrics and next steps. Step 7 mints a parallel filename namespace (`checkpoint-feature-<slug>.md`) and replaces the mandated document with a one-line marker. A command may not create a second, incompatible checkpoint convention. Independently corroborated by `docs/checkpoints/_template.md`, which contains no marker line — no checkpoint generated from the repo's own template could ever satisfy step 7. |
| **Replacement contract (specification)** | Step 7 should require a checkpoint per `AGENTS.md` § Checkpoint Protocol: filename `docs/checkpoints/checkpoint-<SEQ>-<phase>.md`, containing the five elements `AGENTS.md` itself names. Derive the replacement check from `AGENTS.md`'s five-item list, **not** from `docs/checkpoints/_template.md`'s full heading set — see the caution below. |
| **Paired sibling** | `new-feature-checkpoint-line-compliant` (`open/`, hand-authored, currently passing). **Fate: invalidated, not merely re-fixtured.** Its fixture is a `checkpoint-feature-*.md` file whose whole content is the marker line; under the amended contract that artifact is itself non-conforming. The case must be **re-purposed**: new fixture (`checkpoint-<SEQ>-<phase>.md`) and new `check()` asserting the `AGENTS.md` shape. **This is the only one of the six where the zero-sum trap genuinely bites** — see `ADR-007` §4. |
| **Does the case pass after the fix?** | **Probably, but not automatically.** The fixture (`checkpoint-017-t417-harbor-oracle-smoke-complete.md`) has Completed tasks, Key decisions, Blockers, Token usage and Next steps — so it satisfies `AGENTS.md`'s five elements. It uses `## Summary` where `_template.md` says `## Phase summary`, and has no `## Maturity distribution` section (added later, by T437). **A replacement check written against `_template.md`'s headings would fail this fixture and simply relocate the drift one level down.** Write the check against `AGENTS.md`. |
| **Files a follow-up would touch** | `implementation/knowledge/commands/new-feature.md` (Phase 3 step 7); `tests/golden/open/new-feature-checkpoint-line-compliant/{expect.py,fixture/,brief.md,case.yaml}`; `tests/golden/open/new-feature-real-checkpoint-format-drift/{expect.py,case.yaml}` (status flip if it passes); **protected-path authorization required**. |
| **Promotion impact** | Removes one of `orchestrator`'s four `tracked_defect` blockers. **`orchestrator` does not promote** — A and C remain open. `/new-feature` clears command criterion 7 only if B *and* H-1 both close. |

### C — `prepare-release-real-verdict-missing` (`/prepare-release`, `open/`)

| Field | Value |
|---|---|
| **Clause at issue** | `implementation/knowledge/commands/prepare-release.md` step 7: a `## RELEASE VERDICT` block with 11 named fields and `Status` ∈ {`PASS`, `CONDITIONAL_PASS`, `FAIL`}. |
| **Verdict** | **Fix the corpus** (branch 3b), plus a narrow placement clarification that adds no requirement. |
| **Why** | No authority conflict: `AGENTS.md` § Validation Gates endorses the `PASS`/`CONDITIONAL_PASS`/`FAIL` vocabulary, and step 7 is a refinement of it, not a competitor. And this is **omission, not relabelling** — the corpus did not adopt a rival verdict format; it dropped the verdict. The decisive evidence is inside the fixture itself: `checkpoint-release-v6.4.1.md` writes *"See RELEASE VERDICT for how this factors into the release status"* while no such block exists anywhere. The corpus names the obligation and does not discharge it. That is a corpus defect, not a contract defect. |
| **The under-specification that is real** | Step 7 never says *where* the block goes, and the two golden cases disagree: the paired sibling checks `release-notes.md`, this case checks a release checkpoint. Neither governed template has a slot — `docs/checkpoints/_template.md` (mandated by step 6) has none, and `docs/releases/_template.md` has none. **Recommendation: declare the release-notes file (`docs/releases/v<version>.md`) as the home** and add the section to `docs/releases/_template.md`. Reasons: it matches the sibling's existing encoding; `docs/checkpoints/_template.md` is the generic every-phase template and a release-only section does not belong in it; and `scripts/verify-release-docs.py` already governs release-notes sections, so the gate has somewhere to enforce it. The 11 fields and the `Status` enum are **unchanged** — this is a clarification, not a widening. |
| **Paired sibling** | Held out, hand-authored, currently passing; it already encodes the release-notes placement. **Fate: unaffected.** The contract is unchanged and the recommended placement is the one it already assumes. |
| **Does the case pass after the fix?** | **No. It stays `known_failing`, indefinitely as fixtured.** The fixture is a verbatim copy of a shipped release checkpoint. It cannot be retro-edited, and under the recommended placement it is also the wrong artifact class. |
| **Robustness note** | If a reviewer instead treats this as branch 2 (mis-fixtured — the clause governs release notes, not checkpoints), the outcome is identical: `docs/releases/v6.4.1.md` and `docs/releases/v7.0.1.md` have no verdict block either, so a re-targeted case still fails. The conclusion does not depend on which reading is taken. |
| **Files a follow-up would touch** | `implementation/knowledge/commands/prepare-release.md` (step 7, placement sentence only); `docs/releases/_template.md` (add the section); optionally `scripts/verify-release-docs.py`; re-fixturing the case later requires **protected-path authorization**. |
| **Recommended exit** | Emit a conforming `## RELEASE VERDICT` in the next real release, then re-fixture the case against it. Promotion is earned by producing conforming output, not by editing the test. |
| **Promotion impact** | **Unblocks nothing.** `/prepare-release` stays blocked; `orchestrator` stays blocked. |

### D — `security-audit-critical-not-fail` (`/security-audit`, `open/`)

| Field | Value |
|---|---|
| **Clause at issue** | `implementation/knowledge/commands/security-audit.md`, closing sentence and Rails "Failure mode": *"If any CRITICAL findings exist, the verdict MUST be FAIL."* |
| **Verdict** | **Reclassify** (branch 4): `known_failing_category: tracked_defect` → `capability_gap`. The case stays `known_failing`; nothing is swept away. |
| **Why** | This is not a contract-vs-corpus conflict. There is **no corpus** — the case's own `brief.md` records that no real `/security-audit` output exists in this repo's history, so the fixture was hand-authored *to violate the rule*. `README.md`'s `tracked_defect` means "a known, expected-to-be-fixed bug"; there is no bug here. Nothing in the repository is broken, no artifact needs correcting, and the rule must **not** be amended — `security-guidelines.md`'s Security Review Workflow independently requires `SECURITY:CRITICAL` findings to block, and its Immutable Security Constraints forbid disabling a control for convenience. Widening the contract with a compensating-control exception is explicitly rejected. What the case actually demonstrates is that the command's VERDICT surface gives an auditor **no way to record "CRITICAL present, mitigated by a compensating control"** other than by breaking the rule — a deliberate demonstration that the command surface does not support something, which is `README.md`'s `capability_gap` definition verbatim. |
| **Corroborating metadata** | This is the only one of the six `tracked_defect` cases tagged `hand-authored` and `rule-violation`; the other five all carry `real-artifact` and a drift tag. It is an outlier against the suite's own metadata. The two existing `capability_gap` cases share its exact shape (deliberately constructed, no real precedent). |
| **Paired sibling** | **None.** `security-audit-verdict-fields-compliant` encodes field presence and value formats (ISO-8601 timestamp, `OWASP coverage` = 10/10, `Blocker IDs` = none when `PASS`), not the CRITICAL → FAIL rule. `security-audit-coverage-consistency` and the command's remaining case encode other clauses. No sibling is affected by any verdict on this case. |
| **Can it ever pass?** | **No, and it should not.** The only ways are to edit the fixture's `Status` to `FAIL` (which deletes the demonstration and duplicates an existing compliant case) or to relax `expect.py` (forbidden). It is a permanent, correct red. |
| **Recorded alternative** | A reviewer may reasonably object that `capability_gap` still over-claims: the "capability" is one `security-guidelines.md` deliberately refuses, so it is a closed door rather than a gap. Under that reading the honest answer is that the suite's two-flavour vocabulary has **no slot** for a negative/counter-example fixture — `expect.py` returns `bool` and `status` is `expected_pass \| known_failing`, with no way to say "`check()` correctly returning `False` *is* the pass condition." **Consequence of taking that reading instead:** it requires a change to `tests/golden/README.md` (a third flavour) and to `maturity-promotion-criteria-v1.md` §3.5 (declaring the new flavour non-blocking), and `/security-audit` and `security-engineer` stay blocked until that lands. Recommended as a follow-up improvement either way; `capability_gap` is the truthful classification available under today's vocabulary. |
| **Files a follow-up would touch** | `tests/golden/open/security-audit-critical-not-fail/case.yaml` (category + reason) and `brief.md` (Category section); **protected-path authorization required**. No command file changes. |
| **Promotion impact** | **This is the one verdict that unblocks a promotion, and it should be scrutinised hardest.** `capability_gap` does not count under `maturity-promotion-criteria-v1.md` §3.5, so `/security-audit` clears command criterion 7 and `security-engineer` clears agent criteria 3 and 7. Per `docs/tasks/active-tasks.md`'s T514 closure note, that golden case is `security-engineer`'s only remaining gap — so `security-engineer` is expected to promote to `stable`. **Do not take that on this document's word: re-run `scripts/check-maturity.py` before promoting.** `/security-audit`'s own promotion may still be blocked by command criterion 6 (a full sentence of description under `docs/wiki/**`), which this task did not verify. |

### H-1 — held-out `tracked_defect` case (identity withheld)

| Field | Value |
|---|---|
| **Clause at issue** | Withheld. Recorded in the case's own `case.yaml` `known_failing_reason`, which names the command file and step. |
| **Verdict** | **Amend the contract** (branch 1 — the clause contradicts `AGENTS.md`). |
| **Why** | Same shape as B: a command clause declares a convention that `AGENTS.md` already governs and specifies differently. `AGENTS.md` is the higher authority; the corpus agrees with `AGENTS.md` in every instance sampled. The corpus wins because `AGENTS.md` says so, not because it is the majority. |
| **Paired sibling** | **None exists.** No other case in the suite encodes this clause. This is a counter-example to `task-T515.md` §3's premise that every defect case is half of a zero-sum pair — see `ADR-007` §4. |
| **Does the case pass after the fix?** | **Yes.** Both its fixtures already conform to the `AGENTS.md` form, so the case flips to `expected_pass` with no fixture change. |
| **Files a follow-up would touch** | One clause in one command file; the case's own `case.yaml` (status flip). **Protected-path authorization required** for the `case.yaml` edit. |

### H-2 — held-out `tracked_defect` case (identity withheld)

| Field | Value |
|---|---|
| **Clause at issue** | Withheld. Recorded in the case's own `case.yaml` `known_failing_reason`. |
| **Verdict** | **Fix the corpus** (branch 3b — omission). Contract stands unchanged. |
| **Why** | Same shape as C. No authority conflict, and the corpus difference is **omission, not relabelling**: the repo's established practice genuinely does not carry the information the clause requires, rather than carrying it under different names. A contract that is the only thing demanding that information is doing real work and is not surrendered to practice. |
| **Paired sibling** | Hand-authored, currently passing, encodes the same clause. **Fate: unaffected** — the contract does not change. |
| **Does the case pass after the fix?** | **No. It stays `known_failing`.** Its fixture is a verbatim copy of a shipped historical artifact and cannot be retro-edited; it can never pass. Exit is to produce one conforming artifact of that class and re-fixture the case against it. |
| **Fixture-quality caveat for the follow-up** | The case's own `brief.md` concedes its fixture was not produced by the command under test, and argues by analogy that the same pattern holds for outputs that *are*. The analogy is sound, but a re-fixture should use a genuine output of the command rather than the analogous one. |
| **Files a follow-up would touch** | No command file. Re-fixturing later requires **protected-path authorization**. |

### Held-out pair — joint promotion impact

Between them, H-1 and H-2 account for the whole of one experimental agent's remaining blocker and one
of `orchestrator`'s four. Under these verdicts one of the two clears and one does not. **Neither
`tech-lead` nor `orchestrator` promotes.** Stated jointly on purpose, so that no verdict branch is
pinned to a command.

## 4. Summary

| Case | Verdict | Branch | Case status after | Sibling fate | Promotion unblocked |
|---|---|---|---|---|---|
| A `/plan` | amend (path) + fix corpus (headers) | 1 + 3b | stays failing | survives, glob + fixture filename updated | none |
| B `/new-feature` | amend the contract | 1 | expected to pass (check must be written against `AGENTS.md`) | **re-purposed — fixture and check both rewritten** | none on its own |
| C `/prepare-release` | fix the corpus (+ placement clarification) | 3b | stays failing | unaffected | none |
| D `/security-audit` | reclassify → `capability_gap` | 4 | stays failing, stops blocking | none exists | **`/security-audit`, `security-engineer`** |
| H-1 | amend the contract | 1 | passes | none exists | none on its own |
| H-2 | fix the corpus | 3b | stays failing | unaffected | none |

**Net:** 2 of 6 cases end green, 1 stops blocking without going green, 3 stay red and blocking.
**1 of the 3 experimental agents promotes** (`security-engineer`); `orchestrator` and `tech-lead` do
not. Of the five covered commands, `/security-audit` and `/new-feature` clear the defect criterion;
`/plan`, `/prepare-release` and `/code-review` do not.

**Suite-health consequence the follow-up must handle.** These verdicts move two cases from
`known_failing` to `expected_pass` and one from `tracked_defect` to `capability_gap`, shrinking the
`tracked_defect` population from 6 to 3. `tests/golden/README.md` records T411's ≥5-known-failing
discipline and `plan-064` §2.6 carries T414's reject-a-perfect-baseline rule. The suite still holds
6 `known_failing` cases afterwards (3 `tracked_defect` + 3 `capability_gap`), so the floor is met —
but the margin narrows, and `plan-064` Phase 9's 14 new cases are where the replacement difficulty
has to come from. Do not let the baseline drift toward perfect as a side effect of closing these.

## 5. Corpus re-verification, and what had drifted

Every `known_failing_reason` cites a survey run at authoring time (T411, 2026-08). Those were
re-run. **Method and its limits, stated plainly: this session had no shell, `grep`, or directory
listing available**, so surveys were performed by reading named files directly. They are therefore
*sampled and file-enumerated*, not exhaustive greps. Every figure below states its own sample.

| Original claim | Re-verified finding | Verdict on the original |
|---|---|---|
| "zero of this repo's **34** real `docs/plans/*.md` files use `Task Decomposition` or `Resource Assignments` verbatim" | **Direction holds; denominator is stale.** In a sample of 8 plan documents spanning 2026-05 → 2026-09 (`plan-003`, `-007`, `-030`, `-041`, `-064`, `-065`, `-066`, `-067`): `## Task Decomposition` 0/8, `## Resource Assignments` 0/8, `## Risk Assessment` 0/8, all six headers in order 0/8. Plan IDs now run to at least `plan-067`, so the denominator has roughly doubled since authoring. | **Stale denominator, sound conclusion.** |
| *(implied by the case's framing)* "the corpus uses a different, consistent header set" | **Not supported, and this is the finding that changed verdict A.** The 8 sampled plans use 8 different structures. `## Goal` appears verbatim in 1/8 (`plan-041`) — contradicting the tidy claim that the declared names are wholly unused. `## Dependency Graph` and `## Open Questions` appear in 1/8 (`plan-030`, this case's own fixture). Only `plan-030` carries all six required *concepts* under any name; the others omit sections outright. There is no rival convention to defer to. | **Materially overstated.** |
| "`grep -rn "^\[CHECKPOINT\] id=" docs/checkpoints/*.md` returns zero matches" | **Holds.** Verified against `checkpoint-017-t417-harbor-oracle-smoke-complete.md`, `checkpoint-release-v6.4.1.md`, `checkpoint-release-v7.0.1.md`, and decisively against `docs/checkpoints/_template.md` — the template that defines the convention contains no marker line, so no checkpoint generated from it can. | **Accurate.** |
| "`grep -rl "## RELEASE VERDICT" docs/checkpoints/*.md` returns zero matches" | **Holds, and extends further than claimed.** Absent from `checkpoint-release-v6.4.1.md`, `checkpoint-release-v7.0.1.md`, `docs/checkpoints/_template.md`, **and** from the other candidate home: `docs/releases/v6.4.1.md`, `docs/releases/v7.0.1.md`, `docs/releases/_template.md`. Six artifacts across both candidate classes and both governed templates. | **Accurate and understated.** |
| "zero of this repo's **43** real `docs/artifacts/*-v<N>.md` files use a two-part `major.minor` version" | **Direction holds; denominator is stale.** Every artifact filename encountered in this session — roughly 50 distinct names cited across `docs/tasks/completed-tasks.md` rows T001–T236, `docs/tasks/active-tasks.md`, `plan-064`, and the release checkpoints — uses single-integer `-v<N>.md`; zero use `-v<major>.<minor>.md`. The artifact corpus has grown well past 43 since authoring. Independently settled by `AGENTS.md` § Artifact Versioning, which mandates `<type>-v<N>.md` outright, so the count is not load-bearing. | **Stale denominator, sound conclusion.** |
| "no real historical `/security-audit` output exists to source a fixture from" | **Consistent with everything read this session.** No structured `## VERDICT` audit output was encountered anywhere outside the golden fixtures. Not independently provable without a repo-wide grep — flagged as unverified rather than confirmed. | **Unverified, not contradicted.** |

### A structural finding the surveys surfaced

`task-T515.md` §3 describes each defect case and its sibling as "the *same* contract against an
*opposite* fixture." Reading the `expect.py` pairs shows that is not quite what they are. In **all
three** open pairs, the two siblings disagree about the **artifact class or path**, not only about
the content:

| Pair | Defect case reads | Paired sibling reads |
|---|---|---|
| `/plan` | `fixture/docs/plans/*.md` | `fixture/docs/plans/*-plan.md` |
| `/new-feature` | `fixture/docs/checkpoints/*.md` | `fixture/docs/checkpoints/checkpoint-feature-*.md` |
| `/prepare-release` | `fixture/docs/checkpoints/*.md` | `fixture/release-notes.md` |

Each pair therefore embeds an unstated disagreement about *which artifact the clause governs*. That
is why the naive "amend the contract to match reality" move relocates the failure — and why the
first question to ask of any of these cases is the artifact-class question, not the content
question. `ADR-007` §2 makes that step 2 of the procedure for exactly this reason.

## 6. Consumed by

- The follow-up implementation task for `plan-064` Phase 9, which will carry an explicit,
  file-scoped `protected-paths-v1.md` §5 authorization. Rows A–D and H-1/H-2 above are its
  specification.
- `plan-064` Phase 9's "re-run promotion readiness" step — but only after `scripts/check-maturity.py`
  is re-run for real. No promotion should be granted on this document alone.
