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
>    - Write to `docs/plans/plan-<ID>.md`
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

### Output paths — formerly contested, resolved by T563/T564; still not asserted
When this case was authored (T561), `/new-poc`'s three output files were each contradicted by another
document, and the case asserted none of them. `poc-contract-resolution-v1.md` ruled all three
`ADR-007` branch 1, and T564 amended the command. The clauses now read verbatim:

1. **The plan path (P11, resolution §2): resolved.** Step 1 now says "Write to
   `docs/plans/plan-<ID>.md`" (quoted above), which is the path its cited protocol uses
   (`poc-orchestrator` § PLAN PHASE (lightweight): "Write a lightweight plan in
   `docs/plans/plan-<ID>.md`"). Under `ADR-007`'s corollary row for a name-or-path-only amendment, the
   case survives with its fixture moved to the amended form: T565 renamed the plan
   `fixture/docs/plans/plan-001.md` (formerly `poc-local-note-search.md`, contents unchanged). After
   `T596` (P32) defined `<ID>` as a three-digit number, a hyphen and a slug (`plan-approve-execute`
   § File Location), `T597` renamed it `fixture/docs/plans/plan-001-local-note-search.md`, contents
   byte-identical. `check()` is unchanged and path-agnostic. It reads whichever single `*.md` sits in
   `fixture/docs/plans/`, so neither rename changes a result.
2. **The debt scorecard (P12/P29, resolution §3a): resolved.** Step 11 now reads:

   >     - Write to `POC-DEBT-SCORECARD.md` in the PoC root, per `poc-guidelines.md` § Debt Scorecard

   `TECHNICAL-DEBT.md` was ruled a separate narrative register, not a scorecard home (§3c).
3. **The checkpoint path (P30, resolution §4): resolved.** Step 14 now reads:

   > 	- Write checkpoint per `AGENTS.md` § Checkpoint Protocol: store at `docs/checkpoints/checkpoint-<SEQ>-<phase>.md`, with `<phase>` naming the PoC gate

The contract no longer contradicts itself or another document, but this case **still asserts none of
the three paths**. Its `check()` covers step 1's *content* only, and this realignment (T565) does not
change it. A green here therefore still does **not** attest that `/new-poc` writes its artifacts where
it should. A path assertion would be a new check, left as a candidate follow-up.

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
plan file added. It stays `True` with the plan renamed `plan-042.md` (path not asserted) and with
"Evaluate and demo" for "Evaluate & demo". After the T565 rename to `plan-001.md` it is still `True`,
and it stays `True` with the file renamed back to `poc-local-note-search.md` (path not asserted).
After the T597 rename to `plan-001-local-note-search.md` it is still `True`, and it stays `True` with
the file named `plan-001.md` or `poc-local-note-search.md` (path not asserted).

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
