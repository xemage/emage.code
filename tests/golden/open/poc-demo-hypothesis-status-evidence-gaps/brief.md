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
> - **Validation status**: VALIDATED | INVALIDATED | INCONCLUSIVE | IN_PROGRESS
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
the block's own `Validation status` says the demo has *not* shown the evidence (`INCONCLUSIVE` or
`IN_PROGRESS`), `Evidence gaps` must be a real, non-empty list — `None`, `n/a`, `—`, `TBD` and an empty
field all fail. Conversely, a decided status (`VALIDATED` / `INVALIDATED`) with nothing under `Key
evidence demonstrated` fails: a verdict the demo did not demonstrate is the over-claim in another form.
The fixture is deliberately `IN_PROGRESS`, so the Failure mode branch is exercised, not vacuous.

Around that, the block's structure: exactly one `## Hypothesis Status` heading; the five fields, each
once, in declared order; `Validation status` and `Confidence level` each a single value from the
declared enum (`PARTIALLY_VALIDATED`, `VERY HIGH` fail). And the package's seven declared deliverables
(items 1–6 and step 10), each present as a heading, matched by concept — the command names deliverables,
not heading text.

### Contested clause deliberately not asserted — reported, not resolved
**Step 7, `## Artifact References`, is not checked, because every path it names is contested:**
- "Link to the PoC plan document (`docs/plans/poc-<slug>.md`)" — parked item **P11**: `poc-orchestrator`
  writes PoC plans to `docs/plans/plan-<ID>.md`.
- "Link to the latest checkpoint (`docs/checkpoints/checkpoint-poc-<gate>.md`)" — contradicts
  `AGENTS.md` § Checkpoint Protocol's `checkpoint-<SEQ>-<phase>.md`; the same defect class `ADR-007`
  ruled on for `/new-feature` (reported with the `new-poc-plan-hypothesis-format` case).
- "Reference the Technical Debt Scorecard (`docs/decisions/poc-debt-<slug>.md`)" — parked item **P12**:
  `poc-guidelines.md` declares `POC-DEBT-SCORECARD.md` in the PoC root.

Item 6's "tied to the Technical Debt Scorecard" is checked only as a heading for the same reason: which
scorecard it is tied to is P12. The fixture states its transition notes without citing a scorecard
path rather than pick a side.

### Readings deliberately not asserted
- **That the restated hypothesis matches the plan's.** "Restated" admits paraphrase; equality would
  over-assert and anything looser is LLM-judged.
- **That `VALIDATED` demos list no gaps, or that confidence agrees with status.** Neither is declared;
  a `VALIDATED` demo with `Evidence gaps: None` passes (demonstrated).
- **Step 9 ("Highlight which parts … directly validate").** No declared form; the fixture carries a
  line for it, ungraded.
- **`poc-guidelines.md` Rule 4, "Binary outcome".** The status enum's `INCONCLUSIVE` sits awkwardly
  against "A PoC either validates or invalidates the hypothesis"; for a mid-PoC demo, `IN_PROGRESS` is
  not in tension with it, and this case does not adjudicate the rest (see the `/evaluate-poc` case).

## Pass condition
`fixture/poc-demo.md` has headings covering all seven deliverables; exactly one `## Hypothesis Status`
block whose five declared fields appear once each in order, with non-empty `Hypothesis`, a single
declared `Validation status` and `Confidence level`; if the status is `INCONCLUSIVE`/`IN_PROGRESS`,
`Evidence gaps` is non-empty and not a none-marker; if `VALIDATED`/`INVALIDATED`, `Key evidence
demonstrated` is.

## Discrimination (demonstrated at authoring, on temp copies)
`check()` is `True` on the fixture and `False` on each of: `Evidence gaps: None` with `IN_PROGRESS`;
`Evidence gaps: n/a` with `INCONCLUSIVE`; the gaps field omitted; status `PARTIALLY_VALIDATED`;
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
