# Case: poc-demo-hypothesis-status-evidence-gaps

## Command under test
`/poc-demo`

## Brief (illustrative — not executed live)
"Package the note-search PoC for the platform leads; they need to decide whether we can drop the
search service from v1." The demo is prepared mid-PoC, with one of the three required measurement
runs complete.

## What this checks
`implementation/knowledge/commands/poc-demo.md`, three clauses verbatim. Step 8:

> 8. **Include hypothesis validation status in the demo**:
>
> ```
> ## Hypothesis Status
>
> - **Hypothesis**: <restated hypothesis>
> - **Validation status**: VALIDATED | INVALIDATED | IN_PROGRESS
> - **Key evidence demonstrated**: [list what the demo proves]
> - **Evidence gaps**: [list what the demo does NOT prove]
> - **Confidence level**: HIGH | MEDIUM | LOW
> ```

the `## Rails` Failure mode:

> **Failure mode**: If the demo cannot show evidence for the stated hypothesis, reports the evidence gap explicitly in the Hypothesis Status block rather than omitting it.

and the `## Demo Package` deliverables with step 10:

> 1. Demo walkthrough script
> 2. Required sample data and input sequence
> 3. Expected visible outcomes
> 4. Presenter notes and fallback path
> 5. Explicit PoC-only shortcuts shown in the demo
> 6. Production transition notes tied to the Technical Debt Scorecard

> 10. Call out any demo elements that are mocked/simulated vs. real implementation

**The load-bearing assertion is the Failure mode, because it is the one that protects the audience.**
A demo is the PoC artifact most likely to over-claim: it is built to persuade, and the cheapest way to
look finished is to leave the gaps out. The Failure mode forbids exactly that, and it is checkable: when
the block's own `Validation status` says the demo has *not* shown the evidence (`IN_PROGRESS`, the
enum's one undecided value), `Evidence gaps` must be a real, non-empty list — `None`, `n/a`, `—`, `TBD` and an empty
field all fail. Conversely, a decided status (`VALIDATED` / `INVALIDATED`) with nothing under `Key
evidence demonstrated` fails: a verdict the demo did not demonstrate is the over-claim in another form.
The fixture is deliberately `IN_PROGRESS`, so the Failure mode branch is exercised, not vacuous.

Around that, the block's structure: exactly one `## Hypothesis Status` heading; the five fields, each
once, in declared order; `Validation status` and `Confidence level` each a single value from the
declared enum (`PARTIALLY_VALIDATED`, `VERY HIGH` and the removed `INCONCLUSIVE` fail). And the package's seven declared deliverables
(items 1–6 and step 10), each present as a heading, matched by concept — the command names deliverables,
not heading text.

### Step 7 — formerly contested, resolved by T563/T564; still not asserted
When this case was authored (T561), every path step 7 named was contested: the plan path (parked item
**P11**, `docs/plans/poc-<slug>.md` against `poc-orchestrator`'s `docs/plans/plan-<ID>.md`), the
checkpoint path (`checkpoint-poc-<gate>.md` against `AGENTS.md` § Checkpoint Protocol), and the debt
scorecard (parked item **P12**, `docs/decisions/poc-debt-<slug>.md` against `poc-guidelines.md`'s
`POC-DEBT-SCORECARD.md`). `poc-contract-resolution-v1.md` §§2, 4 and 3a ruled all three `ADR-007` branch
1, and T564 amended the links, which now read verbatim:

>    - Link to the PoC plan document (`docs/plans/plan-<ID>.md`)
>    - Link to the latest checkpoint (`docs/checkpoints/checkpoint-<SEQ>-<phase>.md`, per `AGENTS.md` § Checkpoint Protocol, with `<phase>` naming the PoC gate)
>    - Reference the Technical Debt Scorecard (`POC-DEBT-SCORECARD.md` in the PoC root, per `poc-guidelines.md` § Debt Scorecard)

The contract is no longer contested, but step 7 is **still not asserted**. This realignment (T565)
carries the amended wording and value sets only. It adds no new assertion, and the fixture, which has no
`## Artifact References` section, is outside its grant. Asserting step 7 would be a new check with a new
fixture, so it is left as a candidate follow-up. Item 6's "tied to the Technical Debt Scorecard" stays a
heading-only check for the same reason. The fixture states its transition notes without citing a
scorecard path.

### Readings deliberately not asserted
- **That the restated hypothesis matches the plan's.** "Restated" admits paraphrase; equality would
  over-assert and anything looser is LLM-judged.
- **That `VALIDATED` demos list no gaps, or that confidence agrees with status.** Neither is declared;
  a `VALIDATED` demo with `Evidence gaps: None` passes (demonstrated).
- **Step 9 ("Highlight which parts … directly validate").** No declared form; the fixture carries a
  line for it, ungraded.
- **`poc-guidelines.md` Rule 4, "Binary outcome" — resolved, not a reading any more.** The enum's
  former `INCONCLUSIVE` sat against "A PoC either validates or invalidates the hypothesis".
  `poc-contract-resolution-v1.md` §5 (P31) removed it and kept `IN_PROGRESS`: a demo runs before
  evaluation, so "not yet decided" is a legitimate state that Rule 4 does not touch. T564 amended the
  enum (quoted above), and the check now rejects `INCONCLUSIVE` as off-enum.

## Pass condition
`fixture/poc-demo.md` has headings covering all seven deliverables; exactly one `## Hypothesis Status`
block whose five declared fields appear once each in order, with non-empty `Hypothesis`, a single
declared `Validation status` and `Confidence level`; if the status is `IN_PROGRESS`,
`Evidence gaps` is non-empty and not a none-marker; if `VALIDATED`/`INVALIDATED`, `Key evidence
demonstrated` is.

## Discrimination (demonstrated at authoring, on temp copies)
`check()` is `True` on the fixture and `False` on each of: `Evidence gaps: None` with `IN_PROGRESS`;
`Evidence gaps: n/a` with `IN_PROGRESS`; status `INCONCLUSIVE` with the fixture's real gaps kept (it
now fails on the enum; at T561 the perturbation was `Evidence gaps: n/a` with `INCONCLUSIVE`, which
exercised the gap rule, and the gap rule is now shown by the two `IN_PROGRESS` rows); the gaps field
omitted; status `PARTIALLY_VALIDATED`;
confidence `VERY HIGH`; `VALIDATED` with `Key evidence demonstrated: none`; the mocked/simulated
heading renamed; `Confidence level` moved above `Evidence gaps`; "Fallback Path" dropped from the
presenter heading; a second `## Hypothesis Status` block. It stays `True` for `VALIDATED` with
`Evidence gaps: None` — the rule binds where the Failure mode binds and no wider.

## Provenance
**Hand-authored; no real corpus exists.** No `/poc-demo` output has ever been committed here:

```
grep -rlE '^## (POC VERDICT|Hypothesis Status)' --include=*.md . | grep -vE '/commands/|/prompts/|/skills/|/agents/|/workflows/'  ->  0 matches
ls docs/plans | grep -c '^poc-'  ->  0     (nothing to demo: no PoC has been run in this repository)
```

and the history survey in `new-poc-plan-hypothesis-format/brief.md` finds no PoC artifact of any kind
in any revision. `ADR-007` branch 4 territory. The PoC is the same illustrative note-search PoC that
case plans; its sample data is declared synthetic, and its content is not graded.
