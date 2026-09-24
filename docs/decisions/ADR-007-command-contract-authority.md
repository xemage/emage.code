# ADR-007 — command-contract-authority

> Filename: `ADR-007-command-contract-authority.md` (zero-padded sequential, kebab-case slug).

- **Status**: proposed
- **Date**: 2026-09-25
- **Decider(s)**: solution-architect
- **Tasks**: T515 (this decision); follow-up implementation task, not yet opened
- **Requirements**: `docs/tasks/task-T515.md` §§1–7; `docs/plans/plan-066-t515-command-contract-authority.md`;
  `docs/artifacts/maturity-promotion-criteria-v1.md` §3.5; `tests/golden/README.md`
  ("What 'known-failing' means"); `AGENTS.md`
- **Implements into**: `docs/artifacts/command-contract-resolution-v1.md` (the per-case table)

## Context

Six golden cases carry `status: known_failing` with `known_failing_category: tracked_defect`. Each
records a conflict between a command's *declared* contract and this repository's *actual* artifact
practice. Together they are the entire remaining `tracked_defect` blocker on `maturity-promotion-criteria-v1.md`
§3.5 for three `experimental` agents and for the five commands that have golden coverage at all.

Three properties of the problem make it a decision rather than a fix:

1. **The obvious move is wrong.** "Zero real plan documents use the declared headers, therefore amend
   the command" makes the paired `expected_pass` sibling fail. The failure relocates rather than
   disappearing.
2. **The incentive is bad.** Every command whose contract bends is owned by an agent that a
   favourable ruling promotes. Three of the four owning agents are among the three still at
   `experimental`. Asking any of them to rule is a direct conflict; `T515` was assigned to an agent
   that owns zero commands for that reason.
3. **Six ad-hoc judgments would not be a decision.** Without a stated principle, each case can be
   argued either way, and the arguments would reliably land wherever the promotion pressure points.

The failure mode this must avoid is not "getting a case wrong." It is **majority rule**: treating
"N of N real artifacts disagree with the contract" as self-evidently settling the question in the
corpus's favour. Counting artifacts measures what was done, not what is authoritative. A contract
that has never been honoured is indistinguishable, by that metric, from a contract that has never
been *tried* — and from one that is being quietly ignored because honouring it is work.

## Decision

**A command's declared contract is authoritative over the corpus unless the contract contradicts a
higher-authority document, or unless the only thing in dispute is a label for content the corpus
already carries. Popularity is not authority.**

Operationally, every contract-vs-corpus conflict is resolved by this procedure, applied in order.
The first branch that fires decides the case.

### 1. Authority conflict → **amend the contract**

Does the clause contradict `AGENTS.md`, a `stable` instruction, or another clause of the same
command file?

If yes, the command is wrong regardless of what the corpus does. `AGENTS.md` is this repository's
top-level convention document; a command may specialise it but may not create a rival convention for
the same thing. A command file may also not contradict itself — where it does, the clause the rest of
the file and the corpus both disagree with is the defective one.

The corpus wins on this branch because a higher-authority document says so, **not** because it is the
majority. If the corpus happened to follow the command and disagree with `AGENTS.md`, this branch
would still amend the command and the corpus would be wrong too.

### 2. Wrong artifact class → **reclassify / re-fixture**, do not amend

Is the case's fixture an instance of the artifact class the cited clause governs?

If not, the case cannot evidence a defect in this command. It is measuring command A's contract
against artifact class B, and amending A on that evidence would be amending a contract on the
strength of an artifact it never governed. This step is placed second, before any content
comparison, because §5 of the resolution artifact shows that *all three* open sibling pairs embed an
unstated disagreement about which artifact the clause governs.

### 3. Relabelling versus omission

For an in-class, non-conforming corpus, ask what is actually different.

- **3a — relabelling → amend the contract's labels.** The corpus carries the *same information* under
  different section names, **and** offers a single coherent alternative vocabulary. Then the labels
  are the arbitrary part; prefer the form the repository's own higher-authority vocabulary already
  uses. Structure, ordering and field counts are preserved — only names change. A hand-authored
  sibling fixture is re-authored to the amended labels; that is a fixture update tracking a corrected
  contract, not a weakened check.

  The second condition is load-bearing. If the corpus is merely *heterogeneous* — many structures,
  no shared alternative — there is nothing to defer to, and elevating one document's choices to a
  convention would convert a discriminating check into a rubber stamp for that document.

- **3b — omission → fix the corpus.** The corpus does not carry the declared information at all. Then
  the contract is the only thing demanding it, which is precisely when a contract is doing real work.
  It is not surrendered to practice. The case stays failing.

  A frozen historical fixture can then **never** pass, and must not be retro-edited: `AGENTS.md`'s
  artifact-immutability convention and shipped release history both forbid it. The exit is to
  **produce one conforming artifact of that class and re-fixture the case against it** — promotion
  earned by doing the work, not by editing the test.

### 4. No corpus at all → **reclassify**

A hand-authored fixture built to violate a rule is not a contract-vs-corpus conflict. There is no
corpus to fix and, if the rule is independently backed, no contract to amend. `tests/golden/README.md`
defines `tracked_defect` as "a known, expected-to-be-fixed bug"; where nothing is broken, the
classification is wrong even though the failure is real. Such a case is a deliberate demonstration
that the command surface does not support something — `capability_gap` under today's vocabulary.

### 5. Never resolve by relaxing a check

Deleting required fields, loosening a regex, or admitting a second form for convenience is
prohibited, on every branch. Re-authoring a *hand-authored fixture* to a corrected contract is
permitted and is not relaxation: the check's strength is unchanged and only the example moves.

### Corollary — what happens to the paired sibling

The sibling's fate follows mechanically from the branch, and is not a separate judgment:

| Branch | Sibling fate |
|---|---|
| 1, where the amendment changes only a *name or path* | survives; fixture/glob updated to the amended form |
| 1, where the amendment changes the *artifact class* | **invalidated — must be re-purposed**, new fixture and new check |
| 3a | survives; fixture re-authored to the amended labels |
| 3b, 4, 2 | **unaffected** — the contract does not change |

## Alternatives considered

| Option | Pros | Cons | Why not chosen |
|--------|------|------|----------------|
| **A. Corpus always wins** ("N of N real artifacts disagree, so amend the command") | Mechanical; resolves all six; unblocks all three agents | Makes practice self-ratifying: any contract can be retired by not honouring it. Would amend two clauses that contradict `AGENTS.md`'s own conventions *in the direction of* `AGENTS.md`, by coincidence rather than by reason — and would amend three more where the corpus simply dropped required information | Rejected. It cannot distinguish "the contract is wrong" from "the contract is inconvenient", which is the only distinction that matters here |
| **B. Contract always wins** ("the corpus is non-conforming, fix the corpus") | Preserves every declared contract; unblocks nothing, so obviously not incentive-driven | Would keep two clauses that directly contradict `AGENTS.md`, letting commands mint rival conventions for checkpoint filenames and artifact versioning. Leaves all six red and all three agents blocked indefinitely | Rejected. Being uniformly harsh is not the same as being right |
| **C. Widen every contract to admit both forms** | Resolves every case; breaks no sibling | A shipped, user-facing command that declares two acceptable output forms is worse guidance than one that declares one. And in four of the six cases there is no legitimate second form to admit — either the second form contradicts `AGENTS.md`, or the "second form" is the absence of the required content | Rejected as a general rule. Branch 3a is the narrow, conditioned case where a label change is genuinely warranted, and it replaces the labels rather than doubling them |
| **D. Reclassify all six as `capability_gap`** | Unblocks everything immediately; touches no contract | Dishonest for five of the six: `capability_gap` means the surface does not support something, and in five cases the surface supports it fine and the artifact simply does not comply. This is the "relax until it passes" failure mode wearing a taxonomy disguise | Rejected |
| **E. Six independent judgments, no principle** | Each case gets its most natural answer | Not reviewable: with no stated rule, no reader can check whether a verdict was reasoned or was reached because it unblocked a promotion. `T515`'s whole purpose is to make the judgment auditable on its own merits | Rejected — `task-T515.md` §6 requires a general principle |

## Consequences

- **Positive**
  - The verdicts are checkable. A reviewer can disagree with a branch assignment on the evidence
    rather than on taste, and `docs/artifacts/command-contract-resolution-v1.md` records which branch
    each case took and why.
  - The principle refuses the self-ratifying reading of practice. A contract cannot be retired by
    being ignored; it can be retired only by contradicting a higher authority or by being shown to
    dispute nothing but a label.
  - Branch 3b's exit condition — produce a conforming artifact, then re-fixture — keeps the maturity
    ladder honest. The blocked commands become promotable by emitting the output they promise, which
    is exactly what a maturity claim is supposed to attest.
  - Applied to the six cases, the result is uneven, which is the expected shape of an honest answer:
    **2 cases end green, 1 stops blocking without going green, 3 stay red.** `task-T515.md` §2 warns
    that "all six resolve cleanly" would be a suspicious result; this is not that result.

- **Negative**
  - **It unblocks one promotion, not three.** `security-engineer` clears; `orchestrator` and
    `tech-lead` do not. Three of the six cases stay red and keep blocking, and two of them stay red
    *indefinitely* until new conforming artifacts exist. `plan-064` Gate G6 moves less than Phase 9
    hoped.
  - **The one verdict that unblocks a promotion is a reclassification, which is the most
    contestable kind.** That is recorded prominently in the resolution artifact rather than buried,
    with its alternative reading and the cost of taking that reading instead.
  - One case's paired sibling is genuinely destroyed rather than adjusted, and must be re-authored
    from scratch inside a protected path.
  - Branch 3b produces standing red cases with no near-term exit, which is uncomfortable for a suite
    whose own README treats `known_failing` as "expected to be fixed."

- **Risks introduced**
  - **Branch 1 is the loophole to watch.** "It contradicts `AGENTS.md`" is the branch a motivated
    reader would reach for to amend an inconvenient contract. Mitigation: the contradiction must be
    quotable from `AGENTS.md`'s own text, and both invocations in the resolution artifact quote the
    specific `AGENTS.md` section.
  - **Branch 2 is the loophole to watch second.** "Wrong artifact class" could dismiss any
    inconvenient case. Mitigation: it is decided from the clause's own wording and the governing
    template, not from the fixture's convenience — and in the one case where it was available, the
    verdict was reached on branch 3b instead and was noted to be robust to taking branch 2 anyway.
  - Amending a command changes what every downstream target project is told to produce. Two commands
    are amended here; both amendments move them *toward* `AGENTS.md`, which every target project also
    receives, so the drift is corrective rather than novel.
  - Closing these shrinks the suite's `tracked_defect` population from 6 to 3. The floor in
    `tests/golden/README.md` (≥5 `known_failing`) still holds at 6, but the margin narrows — see the
    suite-health note in the resolution artifact.

- **Follow-ups**
  - One implementation task carrying an explicit, file-scoped `protected-paths-v1.md` §5
    authorization, specified row-by-row by `docs/artifacts/command-contract-resolution-v1.md` §3.
  - A separate task to give `tests/golden/README.md` a flavour for negative/counter-example fixtures,
    which today's `expected_pass`/`known_failing` vocabulary cannot express.
  - `T516` (already on the ledger) — narrowing `maturity-promotion-criteria-v1.md` §3.5's free-text
    component scan to a declared field. Unrelated to these verdicts, but it gates when the promotions
    they permit can actually be claimed.

## Validation

This decision is correct if the following hold. Each is checkable, and a failure of any one is
grounds to revisit the ADR rather than to work around it.

1. **No check is weaker.** For every amended contract, the replacement `expect.py` requires the same
   number of structural elements with the same ordering and value constraints as the one it replaces.
   A follow-up that produces a shorter required-field list has violated §5, not implemented it.
2. **Every claimed pass is a real pass.** After the follow-up lands, `scripts/scorecard.py` reports
   exactly the case-status transitions predicted in the resolution artifact's §4 summary — no extra
   greens, and specifically no green for a case this ADR predicts stays red.
3. **Branch 1's amendments are quotable.** A reader can open `AGENTS.md`, find the cited section, and
   see the contradiction without taking this document's word for it.
4. **The promotion outcome matches.** Re-running `scripts/check-maturity.py` after the follow-up
   promotes `security-engineer` and does **not** promote `orchestrator` or `tech-lead`. If it
   promotes more than that, a verdict was more generous than this ADR intended and should be re-read.
5. **The standing reds get an exit, not an erasure.** The next real release emits a conforming
   release verdict, and the next plan document and code review conform to their declared contracts —
   after which those cases are re-fixtured against the new artifacts. If instead they are quietly
   reclassified or retired, branch 3b was not implemented; it was evaded.
