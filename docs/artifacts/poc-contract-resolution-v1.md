# Artifact: poc-contract-resolution-v1.md

> Filename: `poc-contract-resolution-v1.md`. Immutable once produced; revisions bump `<N>`.

## Metadata

- **Producer agent**: solution-architect
- **Task**: T563
- **Created**: 2026-10-01
- **Based on**: `docs/tasks/task-T563.md`; `docs/plans/plan-091-wave-3-promotion-and-poc-conflicts.md` §2;
  `docs/plans/plan-090-golden-wave-3.md` §2; `docs/decisions/ADR-007-command-contract-authority.md` (the
  procedure applied); `docs/artifacts/command-contract-resolution-v1.md` §3 row B (the checkpoint precedent);
  `AGENTS.md`; `docs/artifacts/protected-paths-v1.md` §5.
- **Supersedes**: none (first version)
- **Decision references**: ADR-007 (applied, not amended). No new ADR is minted here; see §8 for the one gap
  ADR-007 does not cover.

## 0. What this document is, and what it did not do

This is a decision record for four PoC-track contract conflicts (P11, P29, P30, P31), with a specification for
the follow-up that implements them. **It changed no command, agent, instruction or golden case.** Every edit
listed below belongs to a follow-up task. The golden-case edits need an explicit, file-scoped
`protected-paths-v1.md` §5 authorization.

**Method and limits.** This session had **no shell**: no `grep`, no directory listing, no git, and no test
runs. Every claim below comes from reading named files directly. Where a claim would need a search or a run, it
is marked **(unverified)**.

**Files read (source, not projections):** `implementation/knowledge/commands/{new-poc,poc-demo,evaluate-poc,
new-feature,plan}.md`; `implementation/knowledge/instructions/poc-guidelines.md`;
`implementation/knowledge/agents/{poc-orchestrator,orchestrator,technical-debt-narrator,evaluation-agent,
demo-agent}.md`; `implementation/knowledge/skills/plan-approve-execute/SKILL.md`; `AGENTS.md`;
`docs/tasks/validate-tasks.py`; the five planning/decision inputs above. Under this task's read-only grant
extension I also read `brief.md` and `expect.py` of exactly four cases under `tests/golden/open/`:
`team-status-dag-colour-code`, `new-poc-plan-hypothesis-format`, `poc-demo-hypothesis-status-evidence-gaps`,
`evaluate-poc-verdict-debt-reconciliation`. I opened **no fixture files** and nothing under
`tests/golden/held-out/`.

**Line numbers in the brief.** I verified all of them against the files on this branch (`8535dca`):
`new-poc.md:17,37,46`, `poc-demo.md:25,26,27`, `evaluate-poc.md:31,59,65`, `poc-guidelines.md:56,103,112`.
**The site lists are incomplete, though** (§7.1).

## 1. Authority ordering: what ADR-007 and `AGENTS.md` actually establish

The brief asks me to establish the ordering by quoting the sources, not to assume it. Here is what the text
supports, and where it says nothing.

**1.1 `AGENTS.md` and a `stable` instruction each outrank a command.** ADR-007 § Decision, branch 1:

> "Does the clause contradict `AGENTS.md`, a `stable` instruction, or another clause of the same command file?
> If yes, the command is wrong regardless of what the corpus does. `AGENTS.md` is this repository's top-level
> convention document; a command may specialise it but may not create a rival convention for the same thing."

and the decision sentence itself: "A command's declared contract is authoritative over the corpus **unless the
contract contradicts a higher-authority document**". So three things defeat a command clause: `AGENTS.md`, a
`maturity: stable` instruction, and the command's own other clauses. `poc-guidelines.md` qualifies as the
second. Its frontmatter, line 4, reads `maturity: stable`, and it is an instruction
(`implementation/knowledge/instructions/`).

**1.2 Promoting a command to `stable` does not change its rank.** Branch 1 names a stable *instruction*, not a
stable *command*. T562's promotion of `/new-poc`, `/poc-demo` and `/evaluate-poc` leaves them subordinate to
`poc-guidelines.md` and `AGENTS.md`.

**1.3 Nothing ranks `AGENTS.md` against a `stable` instruction.** ADR-007 lists them side by side, and
`AGENTS.md` is silent. None of the four conflicts sets them against each other, so the gap doesn't matter here.

**1.4 Nothing ranks an agent definition against a command, or against an instruction.** ADR-007's branch 1
does not mention agent definitions, and neither does `AGENTS.md`, which describes agents only under § Team
Model: "Orchestrators delegate via structured briefs. Agents do not self-activate". **I therefore do not rely
on "agent outranks command" anywhere below.** An agent definition enters a ruling only in two ways, each
quotable from the documents themselves:

- **A command imports an agent's text by reference.** That makes the imported text a clause of the command,
  so branch 1's same-file prong can apply (P11).
- **An agent subordinates itself to the instruction in its own words.** For example, `poc-orchestrator.md`
  lines 73–76: "the Debt Scorecard format this section summarizes are defined in `poc-guidelines.md` — every
  delegation this agent issues is governed by that instruction, not just the summary below" (P29, P31).

Agent edits that follow from these rulings are therefore **outside ADR-007's procedure**. They are flagged as
such in §6.

**1.5 What kind of conflict this is.** ADR-007 frames every case as *contract against corpus*. These four are
*contract against contract*, and the plan-090 case briefs record that no PoC corpus exists. Branch 1 still
applies directly, because it fires "regardless of what the corpus does". Branches 2–4, however, assume a golden
case measuring a corpus. Where branch 1 does not fire, I say so rather than forcing a later branch.

**1.6 ADR-007 is formally still `proposed`.** Its own header reads "**Status**: proposed". It has been applied
before (`command-contract-resolution-v1.md`, and `/new-feature` step 7 now carries the amended checkpoint
form), and the brief directs me to apply it. I note the status without treating it as a blocker (§7.3).

## 2. P11: the PoC plan filename

| Field | Value |
|---|---|
| **Clauses** | `new-poc.md:17`: "Write to `docs/plans/poc-<slug>.md`". `new-poc.md:18`, **same step**: "Reference protocol: `poc-orchestrator` agent § Plan-Approve-Execute (PoC-Adapted) › PLAN PHASE (lightweight)". That protocol, `poc-orchestrator.md:25`: "Write a lightweight plan in `docs/plans/plan-<ID>.md`". Consumer: `poc-demo.md:25`. |
| **Decision** | **Amend the contract.** The PoC plan is written to `docs/plans/plan-<ID>.md`, as the cited protocol says. `/poc-demo` step 7's link follows. |
| **Branch** | **Branch 1, same-file prong** ("another clause of the same command file"). |
| **Authority relied on** | ADR-007 branch 1: "A command file may also not contradict itself — where it does, the clause the rest of the file and the corpus both disagree with is the defective one." Step 1 tells the agent both to write `poc-<slug>.md` and to follow a protocol that writes `plan-<ID>.md`. The protocol is not a rival authority here. It is the command's own clause, imported by reference. |
| **Which clause is defective** | The `poc-<slug>.md` path. Every other document that names a plan path uses the `plan-` namespace: `poc-orchestrator.md:25`, `orchestrator.md:23` and its precondition at `:55–59`, `plan.md:17` and its "Task Creation Precondition" at `:34–41`, and the `plan-approve-execute` skill (`docs/plans/plan-<feature-or-phase>.md`). There is **no PoC plan corpus**: the `new-poc-plan-hypothesis-format` brief records `ls docs/plans \| grep -c '^poc-'` → `0`. The wider `docs/plans/` corpus uses the `plan-` prefix in every file I have seen (`plan-090`, `plan-091` here; 8 of 8 sampled in `command-contract-resolution-v1.md` §5). That count is **(unverified)** without a listing. **Honest weakness:** the rest of `new-poc.md` says nothing else about the plan path, so the tie-break rests on the imported protocol plus the plan-namespace corpus, not on a second in-file clause as in case A of `command-contract-resolution-v1.md`. Amending the *reference* instead is not available. It would cut the command off from the PLAN PHASE of its own executing agent (frontmatter `agent: "poc-orchestrator"`). |
| **Not relied on** | `orchestrator.md`'s precondition ("a task row may not be added … until the plan document … exists under `docs/plans/plan-<ID>.md`") corroborates the decision but is not authority for it. `orchestrator.md` is an `experimental` agent definition, and `plan.md` is an `experimental` command (§1.4). Its practical force is real, though: `poc-orchestrator` EXECUTE PHASE step 1 writes to the same single `docs/tasks/active-tasks.md` that `AGENTS.md` § Task Protocol declares. |
| **Sibling fate (ADR-007 corollary)** | "1, where the amendment changes only a *name or path*" → **survives; fixture/glob updated to the amended form**. |
| **Golden coupling** | **`new-poc-plan-hypothesis-format`: the quoted clause changes; `check()` does not.** `brief.md:18` quotes step 1 verbatim, including "Write to `docs/plans/poc-<slug>.md`", so the quote goes stale. `expect.py:71` globs `fixture/docs/plans/*.md` and never asserts the path, and the brief records it "was shown to pass with the file renamed `plan-042.md`". Under the corollary, the fixture's `poc-<slug>.md` filename should be renamed to a `plan-<ID>.md` form. That changes no result. The brief's "Contested clauses" item 1 (`:55–59`) becomes resolved text. **`poc-demo-hypothesis-status-evidence-gaps`:** step 7 is explicitly not asserted (`expect.py:8–9`). Only the descriptive text at `brief.md:58–59` goes stale. **Others:** none. |
| **Files a follow-up would edit** | `implementation/knowledge/commands/new-poc.md` (line 17); `implementation/knowledge/commands/poc-demo.md` (line 25); grant-scoped: `tests/golden/open/new-poc-plan-hypothesis-format/brief.md` and its `fixture/docs/plans/` filename; `tests/golden/open/poc-demo-hypothesis-status-evidence-gaps/brief.md` (descriptive text only). |

## 3. P29: the debt scorecard's home and format

The brief describes "three homes, two formats". **Reading the clauses shows two homes for the scorecard, a
separate artifact wrongly counted as a third home, and one rival format.** The conflict splits into three
parts.

### 3a. Home: `docs/decisions/poc-debt-<slug>.md` vs `POC-DEBT-SCORECARD.md`

| Field | Value |
|---|---|
| **Clauses** | `new-poc.md:37`: "Write to `docs/decisions/poc-debt-<slug>.md`". `poc-demo.md:27`: "Reference the Technical Debt Scorecard (`docs/decisions/poc-debt-<slug>.md`)". Against them, `poc-guidelines.md:103`: "Create a `POC-DEBT-SCORECARD.md` file in the PoC root with this structure". |
| **Decision** | **Amend the contract.** The scorecard is `POC-DEBT-SCORECARD.md` in the PoC root, in `poc-guidelines.md` § Debt Scorecard's structure. Both commands point there. |
| **Branch** | **Branch 1, stable-instruction prong.** |
| **Authority relied on** | `poc-guidelines.md` (`maturity: stable`), line 103, quoted above, and Scorecard Rule 4 (`:136`): "No PoC task may be marked complete without a finalized scorecard". That is a completion gate, so the scorecard's identity matters. Corroboration only, not authority: `poc-orchestrator.md:73–76` says the scorecard format "[is] defined in `poc-guidelines.md`". `AGENTS.md` § Decision Log reserves `docs/decisions/` for "ADRs: `docs/decisions/ADR-<NNN>-<slug>.md`". It does not say "only ADRs", so I do not treat it as a branch-1 contradiction. |
| **Residual under-specification (not a command defect)** | `poc-guidelines.md` does not define "PoC root". The follow-up should **quote the instruction's phrase rather than define it**. A command that defines it would be deciding the instruction's meaning on the instruction's behalf. This is recorded for the instruction's owner (§7.4), like the placement gap in case C of `command-contract-resolution-v1.md`. |

### 3b. Format: `/evaluate-poc`'s scales vs the scorecard's

| Field | Value |
|---|---|
| **Clauses** | `evaluate-poc.md:59`: Severity `CRITICAL/HIGH/MEDIUM/LOW`, Effort `S/M/L/XL`. `evaluate-poc.md:34`, **not in the brief's site list**: `Debt items: <count> (CRITICAL: <n>, HIGH: <n>, MEDIUM: <n>, LOW: <n>)`. Against them, `poc-guidelines.md:134`: "Each item must have an estimated production effort: `S` (small), `M` (medium), `L` (large)", and `:123–126`, which summarises items as "Critical (must fix before production) / Medium (should fix before production) / Low (nice to have)". |
| **Decision** | **Amend the contract's value scales; keep its extra columns.** Effort becomes `S/M/L`. Severity becomes three tiers, `CRITICAL/MEDIUM/LOW`, carrying the instruction's meanings one-to-one. The VERDICT `Debt items` line becomes `<count> (CRITICAL: <n>, MEDIUM: <n>, LOW: <n>)`. The extra `Risk`, `Owner` and `Production Impact` columns stay. They add attributes without competing with any, which is a specialisation. |
| **Branch** | **Branch 1, stable-instruction prong.** |
| **Authority relied on** | The two `poc-guidelines.md` clauses quoted above. `/evaluate-poc` step 7 says its table summarises "the Technical Debt Scorecard", so it scores *the same items*. An item rated `XL` there has no legal value in the scorecard (Rule 2 is a closed set). A `HIGH` item falls between "must fix" and "should fix", which have different production consequences. Each difference is a "rival convention for the same thing" (ADR-007 branch 1), not a specialisation: a specialisation would nest inside the parent tiers, and `HIGH` does not. |
| **Recorded alternative** | Amend `poc-guidelines.md` to four tiers and `S/M/L/XL`, after which `/evaluate-poc` needs no change and the golden case is untouched. **Not taken.** ADR-007 decides command contracts and has no branch for amending a stable instruction to match a command. Taking that route *because* it avoids golden edits is exactly the incentive ADR-007 § Context warns about. If a four-tier scale is wanted on the merits, it belongs to a separate instruction-change task, and `/evaluate-poc` would then be re-checked against the new text. |
| **ADR-007 Validation 1** | "the replacement `expect.py` requires the same number of structural elements with the same ordering and value constraints". The eight VERDICT fields and the seven table columns are unchanged. The severity breakdown goes from four sub-counts to three **because the enum shrinks**. Reconciliation still covers every row against the whole declared enum, and the value space only tightens. I read this as no weakening (Validation 1's own heading is "No check is weaker"). **A literal reader could disagree,** and the reviewer should decide that explicitly. |

### 3c. `TECHNICAL-DEBT.md` is not a scorecard home (brief correction)

| Field | Value |
|---|---|
| **Clauses** | `poc-orchestrator.md:56`: "`@technical-debt-narrator`: TECHNICAL-DEBT.md **+ scorecard**". `:84`: "`TECHNICAL-DEBT.md` from `@technical-debt-narrator`", listed alongside, and separate from, the scorecard delegation at `:39`. `technical-debt-narrator.md:14` ("TECHNICAL-DEBT.md with categorized debt") and `:17` ("Technical Debt Scorecard with severity, effort, risk, and ownership") are **two separate deliverables**. `poc-guidelines.md:139` ("update `TECHNICAL-DEBT.md`") sits in § Required Debt Marking (Legacy), apart from § Debt Scorecard. |
| **Decision** | **No change.** Every document that names `TECHNICAL-DEBT.md` names it **next to** the scorecard, never **as** it. It is a narrative debt register, a different artifact class. The two genuine scorecard homes are the ones in §3a. |
| **Branch** | **None fires.** There is no contradiction, so branch 1 does not apply. The question answered is branch 2's (is this an instance of the artifact class the clause governs?), decided from the clauses' own wording as ADR-007 § Risks requires. No golden case is involved, so branch 2's reclassify/re-fixture remedy has nothing to act on. |
| **Residual (not decided here)** | `poc-guidelines.md`'s Legacy section is ambiguous. Its note (`:141`) supersedes "the legacy `DEBT:` comment format" but says nothing about `TECHNICAL-DEBT.md`, which two `stable` agents still require. Reading the note literally, the file survives. Clarifying this is the instruction owner's call (§7.4). |

**P29 golden coupling (3a + 3b):**

- **`evaluate-poc-verdict-debt-reconciliation`: the quoted clauses change, and so does `check()`.**
  - `brief.md` quotes the `Debt items` line (`:22`) and the table row (`:34`) verbatim.
  - `expect.py` hard-codes the current scales: `SEVERITIES` (`:25`, four values), `EFFORT` (`:26`, includes
    `XL`) and `DEBT_ITEMS_RE` (`:29–30`, with a `HIGH:` group).
  - If these are left alone, the check accepts values the amended contract forbids. Stale, but still green.
  - The fixture `poc-evaluation.md` is **unread (outside the grant)**. If any row uses `HIGH` or `XL`, the
    fixture must be re-authored. ADR-007 §5 permits that ("Re-authoring a *hand-authored fixture* to a
    corrected contract is permitted"). `brief.md:72–80` (P12 section) becomes resolved text.
- **`poc-demo-hypothesis-status-evidence-gaps`:** step 7's scorecard link is not asserted. Only the
  descriptive text at `brief.md:63–68` goes stale.
- **`new-poc-plan-hypothesis-format`:** step 11 is not asserted. Only `brief.md:60–63` goes stale.
- **`team-status-dag-colour-code`:** none.

**Files a follow-up would edit:**
- `implementation/knowledge/commands/new-poc.md` (lines 36–37)
- `implementation/knowledge/commands/poc-demo.md` (line 27)
- `implementation/knowledge/commands/evaluate-poc.md` (lines 34, 59)
- Grant-scoped: `tests/golden/open/evaluate-poc-verdict-debt-reconciliation/{expect.py,brief.md}`, plus
  `fixture/poc-evaluation.md` if it uses `HIGH`/`XL`; descriptive-text updates in the other two PoC cases'
  `brief.md`.

## 4. P30: the PoC checkpoint path

| Field | Value |
|---|---|
| **Clauses** | `new-poc.md:46`: "Write checkpoint to `docs/checkpoints/checkpoint-poc-<gate>.md`". Consumer: `poc-demo.md:26`. Against them, `AGENTS.md` § Checkpoint Protocol: "Checkpoints: `docs/checkpoints/checkpoint-<SEQ>-<phase>.md`". |
| **Decision** | **Amend the contract (path only).** Step 14 writes the checkpoint, per `AGENTS.md` § Checkpoint Protocol, to `docs/checkpoints/checkpoint-<SEQ>-<phase>.md`, with `<phase>` naming the PoC gate. Choosing a value for `<phase>` is a specialisation inside `AGENTS.md`'s own slot, not a new namespace. `<SEQ>` is the repository's single checkpoint sequence. `/poc-demo` step 7's link follows. |
| **Branch** | **Branch 1, `AGENTS.md` prong.** |
| **Authority relied on** | `AGENTS.md` § Checkpoint Protocol, quoted above, and ADR-007 branch 1: "a command may specialise it but may not create a rival convention for the same thing". **Precedent:** `command-contract-resolution-v1.md` row B ruled the identical shape for `/new-feature`'s `checkpoint-feature-<slug>.md`: "A command may not create a second, incompatible checkpoint convention." `/new-feature` step 7 now reads "per `AGENTS.md` § Checkpoint Protocol: Store at `docs/checkpoints/checkpoint-<SEQ>-<phase>.md`" (`new-feature.md:30–31`), and the follow-up should mirror that wording. |
| **Where this differs from precedent B (content)** | B also replaced the content, because `/new-feature`'s marker lacked key decisions and token metrics. `/new-poc` does not have that defect. `AGENTS.md` requires "completed tasks, key decisions, blockers, token metrics, next steps". Step 14's marker carries `done=`, `decisions=`, `blocked=` and `next=`, and step 16 requires "spend telemetry (`used`, `remaining`, `projected_total`) in each PoC checkpoint". All five elements are present, so **branch 1 fires on the path only** and the marker line stays. Going further would change content that does not contradict `AGENTS.md`. `AGENTS.md` does not make the order of its "Include:" list normative, so I do not treat the marker's field order as a contradiction. |
| **Sibling fate** | Corollary row "1, … only a name or path" → survives. No golden case asserts step 14. |
| **Golden coupling** | **No quoted clause changes and no `check()` changes.** `new-poc-plan-hypothesis-format/brief.md:64–68` and `poc-demo-hypothesis-status-evidence-gaps/brief.md:60–62` describe the conflict as reported-not-resolved. That descriptive text goes stale. |
| **Files a follow-up would edit** | `implementation/knowledge/commands/new-poc.md` (line 46); `implementation/knowledge/commands/poc-demo.md` (line 26); grant-scoped descriptive text in the two briefs named above. |

## 5. P31: outcome vocabulary (`INCONCLUSIVE`)

| Field | Value |
|---|---|
| **Clauses** | `evaluate-poc.md:31`: "**Status**: VALIDATED \| INVALIDATED \| INCONCLUSIVE". `:65`: Failure mode "returns `INCONCLUSIVE` rather than forcing a Validated/Invalidated call". **Not in the brief's list:** `evaluate-poc.md:16` "Verdict (Validated, Invalidated, Inconclusive)" and `poc-demo.md:37` "VALIDATED \| INVALIDATED \| INCONCLUSIVE \| IN_PROGRESS". Against them, `poc-guidelines.md:56` Rule 4: "**Binary outcome** — A PoC either validates or invalidates the hypothesis. 'Partially validated' requires a follow-up PoC with refined criteria". Rule 3 (`:55`): "If the hypothesis isn't validated by the deadline, it fails". Scorecard `## Result` (`:112`): "[VALIDATED / INVALIDATED]". |
| **Decision** | **Amend the contract.** `INCONCLUSIVE` is removed from `/evaluate-poc` (lines 16 and 31). The Failure mode (line 65) becomes, in substance: *weak evidence, or a hypothesis not actually tested by its deadline, returns `INVALIDATED` (Rule 3) with `Evidence strength: weak`, and names a follow-up PoC with refined criteria as the recommended next step (Rule 4), rather than forcing a `VALIDATED` call.* `/poc-demo` (line 37) also drops `INCONCLUSIVE` and **keeps `IN_PROGRESS`**. A demo runs before evaluation (`poc-orchestrator.md:54–55`, Demo Packaging step 10, then Evaluation step 11), so "not yet decided" is a legitimate state that Rule 4 does not touch. Once `/evaluate-poc` can no longer produce an `INCONCLUSIVE` outcome, the demo has no such outcome to report. |
| **Branch** | **Branch 1, stable-instruction prong**, for both commands. |
| **Authority relied on** | `poc-guidelines.md` Rules 3–4 and `## Result`, quoted above. "Inconclusive" is a third terminal outcome, which Rule 4 rules out, and Rule 3 already says what an unvalidated PoC at its deadline is: failed. **Semantic cost, stated plainly:** `INVALIDATED` will now cover both "disproven" and "not proven in time". The `Evidence strength` field is what tells them apart. That is the instruction's design, not something this ruling introduces. |
| **Recorded alternative** | Amend Rule 4 to admit a third outcome. Not taken, for the same reason as §3b's alternative. Rule 4 is a deliberate design (it already prescribes what happens to a partial result), and ADR-007 gives no path for bending a stable instruction toward a command. |
| **Agent-side consequence (outside ADR-007)** | Two `stable` agents carry the same third outcome: `poc-orchestrator.md:83` "Hypothesis verdict (Validated / Invalidated / Inconclusive)", and `evaluation-agent.md:16` "Verdict: Validated \| Invalidated \| Inconclusive" with Failure mode `:49` "returns `Inconclusive`". `poc-orchestrator` EVALUATE PHASE step 1 delegates the verdict to `@evaluation-agent`. If only the commands are amended, `/evaluate-poc` (run by `poc-orchestrator`) would receive a verdict it may no longer emit. **ADR-007 does not govern agent definitions (§1.4)**, so I recommend these edits on narrower grounds. For `poc-orchestrator`, line 83 sits inside the section it declares "governed by [`poc-guidelines.md`]" (`:73–76`). For `evaluation-agent`, `poc-guidelines.md`'s Rails claim jurisdiction over "a PoC specialist agent", and the agent is one of `poc-orchestrator`'s listed specialists. Neither is an ADR-007 ranking. **This leg needs explicit approval** (§6, FU-C). |
| **Golden coupling: the quoted Status line changes** | **`evaluate-poc-verdict-debt-reconciliation`:**<br>• `brief.md:19` quotes the Status line verbatim and `:40` quotes the Failure mode verbatim. Both change.<br>• `expect.py:22` `STATUS` contains `INCONCLUSIVE` and must drop it.<br>• The "asserted only in its uncontested part" section (`brief.md:58–70`, `expect.py:116–119`) is no longer contested. With a binary `Status`, the existing check "weak is never `VALIDATED`" is exactly "weak ⇒ `INVALIDATED`", the amended Failure mode. The assertion strengthens with no code beyond the enum change.<br>• The discrimination note (`brief.md:103`, "stays `True` for weak + `INCONCLUSIVE`") inverts, and that case must now fail.<br>• Fixture status is **unread**. If the fixture uses `INCONCLUSIVE`, it must be re-authored.<br><br>**`poc-demo-hypothesis-status-evidence-gaps`:**<br>• `brief.md:20` quotes the enum verbatim.<br>• `expect.py:20` `STATUS_VALUES` and `:23` `NO_EVIDENCE_STATUSES` both contain `INCONCLUSIVE` and must drop it.<br>• The brief says the fixture is "deliberately `IN_PROGRESS`" (`:48`), so the fixture is unaffected and the Failure-mode branch stays exercised. I did not read the fixture.<br>• The discrimination perturbation "`Evidence gaps: n/a` with `INCONCLUSIVE`" (`:90`) now fails on the enum instead. The gap rule stays demonstrated by "`Evidence gaps: None` with `IN_PROGRESS`".<br>• `brief.md:77–79` (Rule 4 "not asserted") becomes resolved.<br><br>**Others:** none. |
| **Files a follow-up would edit** | `implementation/knowledge/commands/evaluate-poc.md` (lines 16, 31, 65); `implementation/knowledge/commands/poc-demo.md` (line 37); with approval, `implementation/knowledge/agents/poc-orchestrator.md` (line 83) and `implementation/knowledge/agents/evaluation-agent.md` (lines 16, 49); grant-scoped: both cases' `expect.py` and `brief.md`, and the evaluate-poc fixture if it uses `INCONCLUSIVE`. |

## 6. Follow-up specification

**Why the work is batched by file, not by conflict.** The four decisions overlap on the same lines:
`poc-demo.md` step 7 (lines 25–27) carries P11, P30 and P29 together, and `evaluate-poc.md` carries P29 and
P31. Splitting the work per conflict would produce competing edits of the same lines, so I batch it by kind of
edit instead. Every row must start **after T562 merges**, because T562 edits the same three command files
(frontmatter only).

| Task | Covers | Files | `tests/golden/**` grant? | Owner (suggested) | Notes |
|---|---|---|---|---|---|
| **FU-A**: amend the PoC command contracts | P11, P29 (3a+3b), P30, P31 (commands) | `implementation/knowledge/commands/new-poc.md` (17, 36–37, 46); `…/poc-demo.md` (25, 26, 27, 37); `…/evaluate-poc.md` (16, 31, 34, 59, 65); then regenerate with `node implementation/scripts/sync.mjs --root implementation` and `python3 implementation/scripts/generate-registry.py`. Top-level platform folders are refreshed by `scripts/install.sh --update` per `AGENTS.md`, never hand-edited. | **No** | Backend Developer (same owner class as T562) | Mirror `new-feature.md:30–31`'s wording for the checkpoint clause. Quote "in the PoC root" from `poc-guidelines.md`; do not define it. Breaks no case on its own: every affected `check()` accepts a superset of the amended values. A stale case is green, not red. |
| **FU-B**: realign the three PoC golden cases | Golden coupling of all four | `tests/golden/open/evaluate-poc-verdict-debt-reconciliation/{expect.py,brief.md}` + `fixture/poc-evaluation.md` *only if* it uses `INCONCLUSIVE`/`HIGH`/`XL`; `tests/golden/open/poc-demo-hypothesis-status-evidence-gaps/{expect.py,brief.md}`; `tests/golden/open/new-poc-plan-hypothesis-format/brief.md` + fixture plan filename (rename to a `plan-<ID>.md` form). **Not** `team-status-dag-colour-code`, which is uncoupled. | **Yes.** `protected-paths-v1.md` §5, scoped to these three named `open/` case directories; no `held-out/` access | QA Engineer (same owner class as T561) | Depends on FU-A; same MR or immediately after. ADR-007 Validation 1: no check gets weaker, and the enums only tighten (reviewer to confirm the §3b severity reading). Re-run `scripts/scorecard.py` and `scripts/check-maturity.py` afterwards: T562's three PoC greens must be **re-earned** on the amended contract, not inherited. Any `expect.py` edit presumably moves the evaluator hash past v13 and needs the user's baseline authorization, as in plan-090 §1. That is inferred from commit `c818a59`'s subject and **(unverified)**. |
| **FU-C**: align the two PoC agents' outcome vocabulary | P31 (agent side) | `implementation/knowledge/agents/poc-orchestrator.md` (83); `implementation/knowledge/agents/evaluation-agent.md` (16, 49); regenerate as in FU-A | **No** | Backend Developer | **Needs explicit orchestrator/user approval:** ADR-007 does not govern agent definitions (§1.4), and both agents are `stable`. Recommended to batch into FU-A's MR once approved, so the commands and the agents they run never disagree. |
| *(optional)* **FU-D**: ADR on agent-definition authority | The gap in §1.4 | new `docs/decisions/ADR-<NNN>-<slug>.md` | **No** | Solution Architect | Only if the orchestrator wants a general rule. FU-C does not need one; its basis is quoted per agent. |

**Minimum viable batch:** FU-A + FU-C in one MR, then FU-B in one grant-bearing MR. That is **one** protected-path
authorization in total.

## 7. Findings outside the four decisions

### 7.1 Corrections to the brief

The orchestrator asked for these to be reported, not worked around. All are `unclear_requirements`, severity
`minor`.

1. **P31's site list is incomplete.** It is also at `evaluate-poc.md:16`, `poc-demo.md:37`,
   `poc-orchestrator.md:83`, `evaluation-agent.md:16` and `evaluation-agent.md:49`.
2. **P29's site list is incomplete.** The `Debt items` breakdown at `evaluate-poc.md:34` carries the four-tier
   severity and is what the golden case's reconciliation reads.
3. **P29's "three homes" is a misreading.** `TECHNICAL-DEBT.md` is a distinct artifact in every document that
   names it (§3c). The real conflict is two homes plus one rival format.

### 7.2 The same defect shape on the production track (out of scope)

These are not decided here. They are candidates for parking.

- `new-feature.md:14` (`stable`) writes `docs/plans/feature-<slug>.md`. That is P11's shape: `/new-feature`
  later creates tasks, while `orchestrator.md`'s precondition demands a `plan-<ID>.md`.
- The `plan-approve-execute` skill uses `plan-<feature-or-phase>.md` / `plan-<name>.md`, while `orchestrator.md`
  and `plan.md` say `plan-<ID>.md`.
- Real plans are named `plan-<ID>-<slug>.md` (for example `plan-091-wave-3-promotion-and-poc-conflicts.md`).

P11's decision adopts `plan-<ID>.md` exactly as `poc-orchestrator.md` states it. Whether `<ID>` admits a slug
suffix belongs to whoever adjudicates the production-track plan path.

### 7.3 ADR-007's status reads `proposed`

I could not see whether it was accepted elsewhere, for example in a ledger row or a checkpoint. That needs a
search **(unverified)**. If it is formally unaccepted, these rulings and those in
`command-contract-resolution-v1.md` share that status.

### 7.4 For `poc-guidelines.md`'s owner (not a follow-up sized here)

These are not command defects, so ADR-007 does not reach them:

- "PoC root" is undefined.
- The Debt Inventory table has no per-item severity column, but the Summary counts items by tier.
- The Legacy section's status for `TECHNICAL-DEBT.md` is ambiguous.

### 7.5 Possible verbatim-quote tests (unverified)

Each golden `brief.md` claims to quote its command "verbatim". I could not determine whether any test enforces
brief quotes against command bodies. That needs a `grep` under `tests/`. If such a test exists, FU-A on its own
would turn it red, and FU-A and FU-B must land in one MR.

## 8. Summary

| # | Decision | ADR-007 branch | Authority (quoted in §§2–5) | Quoted golden clause changes? | `check()` changes? |
|---|---|---|---|---|---|
| P11 | PoC plan → `docs/plans/plan-<ID>.md` | 1 (same file, by imported protocol) | `new-poc.md:18` → `poc-orchestrator.md:25` | Yes: `new-poc` `brief.md:18` | No (path-agnostic glob) |
| P29 | Scorecard → `POC-DEBT-SCORECARD.md` in PoC root; `/evaluate-poc` to `S/M/L` + three tiers; `TECHNICAL-DEBT.md` unchanged | 1 (stable instruction); none for `TECHNICAL-DEBT.md` | `poc-guidelines.md:103,123–126,134` | Yes: `evaluate-poc` `brief.md:22,34` | Yes: `evaluate-poc` `SEVERITIES`, `EFFORT`, `DEBT_ITEMS_RE` |
| P30 | Checkpoint → `docs/checkpoints/checkpoint-<SEQ>-<phase>.md`; marker kept | 1 (`AGENTS.md`) | `AGENTS.md` § Checkpoint Protocol; precedent row B | No (descriptive text only) | No |
| P31 | Binary outcome; weak → `INVALIDATED` + follow-up PoC; `/poc-demo` keeps `IN_PROGRESS` | 1 (stable instruction) | `poc-guidelines.md:55,56,112` | Yes: `evaluate-poc` `brief.md:19,40`; `poc-demo` `brief.md:20` | Yes: `STATUS` / `STATUS_VALUES` / `NO_EVIDENCE_STATUSES` |

All four decisions amend commands in the direction of a higher-authority text that I quote. None widens a
contract, and none unblocks a promotion. If anything they put T562's three PoC greens at risk until FU-B
re-earns them. `team-status-dag-colour-code` is coupled to none of them.

## 9. Orchestrator verification and rulings (added before commit, 2026-10-01)

*Added by the orchestrator, not the producing agent. It settles the items marked (unverified) above, using a
shell on `develop` at `8535dca`, and decides the two questions §§3b and 6 left to the reviewer. The text in
§§0–8 is unchanged.*

**9.1 Unverified claims, now checked**

| Claim (section) | Check | Result |
|---|---|---|
| Every `docs/plans/` file uses the `plan-` prefix (§2) | `ls docs/plans \| grep -v '^plan-'` | Only `_template.md`. **Confirmed.** |
| A test enforces brief quotes against command bodies (§7.5) | Searched `tests/` outside `tests/golden/` for `brief.md` | The two hits (`test_golden_suite_format.py:40`, `test_golden_held_out_isolation.py`) check that the file exists and that held-out cases are isolated. Neither compares content. **No such test**, so FU-A does not have to land in the same MR as FU-B. |
| ADR-007 was accepted elsewhere (§7.3) | Header plus a search of `docs/` | Still `proposed`. The precedent is T542 (`completed-tasks.md`) and `skillify-output-path-resolution-v1.md:438`, which used ADR-007 **as a procedure**, with authority taken directly from the quoted higher document. §§2–5 follow that pattern: each quotes `AGENTS.md` or the `stable` `poc-guidelines.md`. **Not a blocker.** Formal acceptance is parked as P34. |
| The `evaluate-poc` fixture uses `INCONCLUSIVE`/`HIGH`/`XL` (§§3, 5) | `grep` of `fixture/poc-evaluation.md` | **`HIGH` at lines 31, 44 and 65**, with no `INCONCLUSIVE` and no `XL`. FU-B **must** re-author the fixture to the three-tier scale. The `poc-demo` fixture contains none of the three. |
| Line citations throughout | Read every cited line in source | All match. |

**9.2 Rulings on the open questions**

- **§3b, ADR-007 Validation 1 (the severity breakdown goes from four counts to three):** **not a weakening.**
  The removed sub-count is for a value the amended contract makes illegal. Reconciliation still covers every
  row against the whole declared enum, and the set of accepted outputs is a strict subset of the old one.
  FU-B's `check()` must reject `HIGH` and `XL` outright. Silently ignoring them is not enough, and its
  discrimination notes must show that rejection.
- **§6 FU-C (agent-side P31 edits):** **approved, batched into FU-A's task.** The basis is the T542 precedent,
  where ADR-007 branch 1 was applied by analogy to an agent file that contradicted a `stable` instruction.
  Each agent also subordinates itself in its own words: `poc-orchestrator.md:73–76` does so directly, and
  `evaluation-agent` falls under `poc-guidelines.md`'s own scope, which covers PoC specialist agents. FU-D (an
  ADR ranking agent definitions) is not needed for this, and is parked as part of P34.

**9.3 Parked (not actioned here)**

- **P32:** the production-track plan path (§7.2). Covers `new-feature.md:14` `feature-<slug>.md`, the
  skill's `plan-<feature-or-phase>.md`, and whether `<ID>` takes a slug suffix.
- **P33:** the `poc-guidelines.md` owner items (§7.4).
- **P34:** formal acceptance of ADR-007, and whether an ADR on agent-definition authority is wanted.
