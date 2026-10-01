# Case: new-poc-plan-hypothesis-format

## Command under test
`/new-poc`

## Brief (illustrative — not executed live)
"I want to prove that SQLite's FTS5 can back search-as-you-type over a couple of hundred thousand notes
on a laptop, without a search service." Phase 0's lightweight plan is produced and presented for
approval.

## What this checks
`implementation/knowledge/commands/new-poc.md` `## Phase 0: Lightweight Plan` step 1, verbatim:

> 1. **Create a lightweight PoC plan** before execution:
>    - **Hypothesis**: Restate the hypothesis clearly with measurable success criteria
>    - **Validation path**: Define what evidence proves/disproves the hypothesis
>    - **3-step plan**: (a) Feasibility check → (b) Core build → (c) Evaluate & demo
>    - Write to `docs/plans/poc-<slug>.md`
>    - Reference protocol: `poc-orchestrator` agent § Plan-Approve-Execute (PoC-Adapted) › PLAN PHASE (lightweight); hypothesis format: `poc-guidelines.md` § Hypothesis-First Validation

and the format that last bullet imports, `implementation/knowledge/instructions/poc-guidelines.md`
§ Hypothesis-First Validation › Hypothesis Format and its Rule 2, verbatim:

> ```
> HYPOTHESIS: [What we believe]
> VALIDATION: [How we will prove/disprove it]
> SUCCESS CRITERIA: [Measurable outcome that confirms the hypothesis]
> FAILURE CRITERIA: [Measurable outcome that disproves the hypothesis]
> ```

> 2. **One hypothesis per PoC** — Keep scope tight. If multiple hypotheses emerge, split into separate PoCs

**This is the clause the whole PoC track hangs off** — `poc-guidelines.md` forbids "Starting
implementation without a documented hypothesis" — and it is the one Phase 0 clause whose content is
not contested by another document. Three assertions:

- **The four-field block**, labels exactly as the format declares them, **each exactly once and in
  declared order**, each non-empty. Exactly once is Rule 2: a second `HYPOTHESIS:` is a second
  hypothesis. A plan that states its hypothesis in prose, or under its own labels, fails — step 1 points
  at a *format*, not at a topic.
- **Measurable criteria.** Step 1 says "measurable success criteria" and the format says "Measurable
  outcome" for both criteria. The deterministic reading is that each criterion carries a quantitative
  threshold (at least one numeral). That is necessary rather than sufficient — "3 users are happy"
  passes — and it is stated so it can be tightened; "search feels instant" fails.
- **The 3-step plan**: three list items or headings led by the declared step names — "Feasibility
  check", "Core build", "Evaluate & demo" (`and` for `&` accepted) — each exactly once, in the declared
  order, and where an explicit `(a)`/`(b)`/`(c)` label is present it must be the declared one.
  Feasibility comes first because the command's Failure mode depends on it: "If the feasibility check …
  finds a critical assumption fails, stops or reframes rather than continuing to build."

### Contested clauses deliberately not asserted — reported, not resolved
`/new-poc` declares three output files, and **every one of the three is contradicted by another
document**. This case asserts none of them, and the green it earns covers step 1's *content* only:

1. **The plan path (parked item P11).** Step 1 says `docs/plans/poc-<slug>.md`; the protocol step 1
   itself cites — `poc-orchestrator` § PLAN PHASE (lightweight), step 3 — says "Write a lightweight plan
   in `docs/plans/plan-<ID>.md`". The fixture uses `poc-<slug>.md` (the command under test's own form);
   `check()` reads whichever single `*.md` sits in `fixture/docs/plans/`, and was shown to pass with the
   file renamed `plan-042.md`.
2. **The debt scorecard (parked item P12).** Step 11 says `docs/decisions/poc-debt-<slug>.md`;
   `poc-guidelines.md` § Debt Scorecard says "Create a `POC-DEBT-SCORECARD.md` file in the PoC root";
   and `poc-orchestrator` / `technical-debt-narrator` name a third artifact, `TECHNICAL-DEBT.md`. Any
   check of step 11 would have to pick one, which is the adjudication `T561` forbids.
3. **The checkpoint path — a new finding.** Step 14 says "Write checkpoint to
   `docs/checkpoints/checkpoint-poc-<gate>.md`"; `AGENTS.md` § Checkpoint Protocol says
   `docs/checkpoints/checkpoint-<SEQ>-<phase>.md`. That is the same defect class `ADR-007` already ruled
   on for `/new-feature`'s `checkpoint-feature-<slug>.md` (branch 1, contract amended;
   `command-contract-resolution-v1.md`), which `/new-feature` no longer carries but `/new-poc` still does.

A green here therefore does **not** attest that `/new-poc` writes its artifacts where it should — it
cannot, while the command and three other documents disagree about where that is.

### Readings deliberately not asserted
- **The other `poc-guidelines` rules** (time-box, binary outcome). Step 1 cites the section for its
  *format*; the fixture carries a timebox, but its absence would not fail.
- **`poc-orchestrator`'s PLAN PHASE contents** (agent assignments, token budget, risks). Step 1 cites it
  as the protocol to follow, not as a content list; the fixture includes risks and budget, ungraded.
- **Step 2's approval.** A chat interaction with no declared artifact.

## Pass condition
`fixture/docs/plans/` holds exactly one `*.md`; it contains the four fields `HYPOTHESIS:`,
`VALIDATION:`, `SUCCESS CRITERIA:`, `FAILURE CRITERIA:` exactly once each, in that order, each
non-empty, with a numeral in both criteria; and it carries the three declared plan steps, each exactly
once as a list-item or heading lead, in order (a) → (b) → (c).

## Discrimination (demonstrated at authoring, on temp copies)
`check()` is `True` on the fixture and `False` on each of: `FAILURE CRITERIA` removed; (b) and (c)
swapped; a second `HYPOTHESIS:` added; success criteria made non-numeric ("search feels instant while
typing"); the feasibility step removed; (b) renamed "Build everything"; (b) mislabelled `(c)`; the
`VALIDATION:` label removed with its prose kept; `SUCCESS CRITERIA` moved before `VALIDATION`; a second
plan file added. It stays `True` with the plan renamed `plan-042.md` (path not asserted — P11) and with
"Evaluate and demo" for "Evaluate & demo".

## Provenance
**Hand-authored; no real corpus exists.** No `/new-poc` run has ever produced a committed artifact in
this repository, at any point in its history. Checked with:

```
ls docs/plans | grep -c '^poc-'                                    ->  0
ls docs/decisions | grep -c 'poc-debt'                             ->  0
ls docs/checkpoints | grep -c 'checkpoint-poc'                     ->  0
git log --all --diff-filter=A --name-only --format= \
  | grep -E '(^|/)(POC-DEBT-SCORECARD\.md|checkpoint-poc-[^/]*\.md|poc-debt-[^/]*\.md|TECHNICAL-DEBT\.md)$|docs/plans/poc-'   ->  0
```

The only `POC-DEBT-SCORECARD.md` string anywhere is the instruction that declares it, its platform
projections, and planning documents discussing its absence (`plan-072` §2). This is `ADR-007` branch 4
territory: there is no corpus to fix. The PoC described is illustrative and uses synthetic data only;
its content is not graded — only its structure.
