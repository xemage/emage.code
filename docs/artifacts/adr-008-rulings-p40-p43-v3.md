# Artifact: adr-008-rulings-p40-p43-v3.md

> Filename: `adr-008-rulings-p40-p43-v3.md`. Immutable once produced; revisions bump `<N>`.

## Metadata

- **Producer agent**: solution-architect
- **Task**: T584 (P2, decision only), third version
- **Created**: 2026-10-07
- **Based on**:
  - `docs/artifacts/adr-008-rulings-p40-p43-v2.md`: the implementation input this version supersedes. Its §1 (the user's
    decisions) and §2 (the P43 analysis) stand.
  - `docs/artifacts/adr-008-rulings-p40-p43-v1.md`: the analysis (§§1–8, 10–12) stands and is referenced, not repeated.
  - The user's decisions of 2026-10-07, verbatim as recorded in v2 §1:
    - P43: **"Evaluation decides, tighten-only (Recommended)"**;
    - P40 S2/S3: **"Strictest applies (Recommended)"**;
    - Notes: **"N1 + N2 + N3 (Recommended)"**.
  - **The Security Engineer's phrase check of N1: PASS.** The orchestrator relayed it and adopted three optional
    `SECURITY:LOW` wording points, F1, F2 and the N2 point. All three are applied here verbatim as relayed (§1).
  - The orchestrator's direction to resolve v2 §3's "§" flag. It is resolved here (§1, change 4).
  - The orchestrator's verification of v2:
    - the P1–P3 anchors are unique;
    - N1–N3 are byte-identical to v1 §9;
    - the cited lines and headings exist;
    - `discover-skills-registry-grounded-recommendation` and `sprint-status-dag-ledger-grounded` mention these names
      only in frozen snapshots, so they are not coupled.
- **Supersedes**: `adr-008-rulings-p40-p43-v2.md`. v1 and v2 stay unchanged. **v3 alone is the implementation input.**
- **Decision references**: as v2; plus the Security Engineer's phrase check of N1 (PASS).

## 1. Change log against v2

There are exactly four changes. Every other byte of every edit is identical to v2.

| # | Source | Edit | Before (in v2's After text) | After (in v3) |
|---|---|---|---|---|
| 1 | F1 (`SECURITY:LOW`), adopted | N1 | `So the verdict is PASS only if every applicable set of criteria admits PASS,` | `So the verdict is PASS only if every applicable set of criteria, the rules above included, admits PASS,` |
| 1 | F1 (continued) | N1 | `None of them makes another less strict.` | `No set of criteria, the rules above included, makes another less strict.` |
| 2 | F2 (`SECURITY:LOW`), adopted | N1 | `Other documents also state verdict criteria for two of the gates:` | `Other documents also state verdict criteria; this note covers two of the gates:` |
| 3 | N2 point (`SECURITY:LOW`), adopted | N2 | `for a high finding with a documented mitigation` | `for a high finding outside the security category with a documented mitigation` |
| 4 | The "§" flag (v2 §3), resolved | N2 | `(§ Criteria from the executor's own documents there)` | `(the paragraph "Criteria from the executor's own documents" there)` |
| 4 | The "§" flag (continued) | N3 | `(`validation-gates` § Verdict Rules, Criteria from the executor's own documents)` | `(`validation-gates` § Verdict Rules, the paragraph "Criteria from the executor's own documents")` |

**Change 4 rationale.** N1 introduces "Criteria from the executor's own documents" as a bold lead-in paragraph inside
§ Verdict Rules, not as a heading. N2 and N3 now name it as a paragraph within that section. The wording is minimal, and
the `§` remains only before real headings.

**Unchanged:** the N1–N3 Before texts and anchors, and every byte of P1, P2 and P3.

## 2. Final edits (complete; v3 alone is the implementation input)

Apply each edit by its Before text, not by line number. Line numbers are at `develop` `c0138a7`, where
`implementation/` is identical to `a54bbba` (the orchestrator verified this). The orchestrator has verified that each
anchor is unique.

Encoding:
- `§` is U+00A7, `–` is U+2013, and `"` is U+0022.
- No emoji is introduced.
- Each four-backtick fence holds one Before/After pair.

### N1: `implementation/knowledge/skills/validation-gates/SKILL.md`, before `:72`

**Anchor:** `### Severity Definitions`, which occurs once.

````
Before:
### Severity Definitions

After:
**Criteria from the executor's own documents.** Other documents also state verdict criteria; this note covers two of the gates: skill `code-review` § VERDICT Format for Validation Gates (Implementation gate); skill `testing-strategy` § VERDICT Format for QA Gate and § Coverage Thresholds That Determine Gate Outcome, and the `qa-engineer` agent's § Validation Gate Protocol (Integration gate). They apply together with the rules above to the gate's one verdict. A PASS or CONDITIONAL_PASS row states what that verdict requires; it does not grant the verdict when another applicable criterion requires a stricter one. So the verdict is PASS only if every applicable set of criteria, the rules above included, admits PASS, CONDITIONAL_PASS only if every one admits at least CONDITIONAL_PASS, and FAIL otherwise. No set of criteria, the rules above included, makes another less strict.

### Severity Definitions
````

### N2: `implementation/knowledge/skills/code-review/SKILL.md`, before `:130`

**Anchor:** `### Artifact Version Awareness`, which occurs once.

````
Before:
### Artifact Version Awareness

After:
These definitions apply together with skill `validation-gates` § Verdict Rules, which applies to the same verdict (the paragraph "Criteria from the executor's own documents" there). Grade each finding on both scales, this skill's § Severity Guide and that skill's § Severity Definitions, and give the most restrictive verdict either requires. A Must Fix finding is `FAIL` even where that skill would admit `CONDITIONAL_PASS` for a high finding outside the security category with a documented mitigation, and a high finding without a documented mitigation is `FAIL` even when it is graded Should Fix here.

### Artifact Version Awareness
````

### N3: `implementation/knowledge/skills/testing-strategy/SKILL.md:233`

**Anchor:** the full `:233` line, which occurs once.

````
Before:
The following coverage thresholds directly determine the QA gate verdict:

After:
The following coverage thresholds directly determine the QA gate verdict, together with skill `validation-gates` § Verdict Rules and the executing agent's own gate criteria; the verdict is the most restrictive that any of them requires (`validation-gates` § Verdict Rules, the paragraph "Criteria from the executor's own documents"):
````

### P1: `implementation/knowledge/skills/rapid-prototyping/SKILL.md`, before `:129`. Unchanged from v2

**Anchor:** `**Evidence items** should be specific and measurable:`, which occurs once.

````
Before:
**Evidence items** should be specific and measurable:

After:
**The PoC's outcome.** The `verdict=` in this line is the prototyping agent's report and an input to the PoC evaluation (the poc-evaluation skill); it is not the PoC's outcome. The outcome is the evaluation's verdict: the poc-evaluation skill's `[VERDICT]` `result=`, which is the `/evaluate-poc` command's `Status` when the evaluation is run through that command, or the `evaluation-agent`'s Verdict. The evaluation may turn a `validated` reported here into `INVALIDATED`. It never turns an `invalidated` reported at a trigger into `VALIDATED`: if the evidence later appears to support the hypothesis, the next step is a follow-up PoC with refined criteria (`poc-guidelines.md` § Hypothesis-First Validation, Rule 4).

**Evidence items** should be specific and measurable:
````

### P2: `implementation/knowledge/skills/poc-evaluation/SKILL.md:117`. Unchanged from v2

**Anchor:** the full `:117` line, which occurs once.

````
Before:
- Otherwise, if any such criterion is "Not Tested" or rests only on weak evidence, the verdict is `INVALIDATED` with `Evidence strength: weak`, and the Recommended next step names a follow-up PoC with refined criteria. Never force a `VALIDATED` call (`poc-guidelines.md` § Hypothesis-First Validation, Rules 3–4).

After:
- Otherwise, if any such criterion is "Not Tested" or rests only on weak evidence, the verdict is `INVALIDATED` with `Evidence strength: weak`, and the Recommended next step names a follow-up PoC with refined criteria. Never force a `VALIDATED` call (`poc-guidelines.md` § Hypothesis-First Validation, Rules 3–4).
- This verdict is the PoC's outcome. A `[CHECKPOINT]` line from the rapid-prototyping skill is an input to it (§ Hypothesis Validation Checkpoint Format there), never a substitute for this assessment: its `verdict=validated` does not stand in for a criterion that the rules above find untested, unmet or resting only on weak evidence. If a `[CHECKPOINT]` line reported at a checkpoint trigger carries `verdict=invalidated`, the verdict is `INVALIDATED`, whatever the assessment table shows; if the assessment would otherwise support `VALIDATED`, the Recommended next step names a follow-up PoC with refined criteria (`poc-guidelines.md` § Hypothesis-First Validation, Rule 4).
````

### P3: `implementation/knowledge/agents/evaluation-agent.md:22`. Unchanged from v2

**Anchor:** `Tie conclusions directly to observable outcomes.`, which occurs once.

````
Before:
Tie conclusions directly to observable outcomes.

After:
Tie conclusions directly to observable outcomes.

Your Verdict is the PoC's outcome. A prototyping agent's `[CHECKPOINT]` line (skill `rapid-prototyping`, § Hypothesis Validation Checkpoint Format) is an input to it, never a substitute for evidence: its `verdict=validated` does not stand in for a success criterion that is untested, unmet or supported only by weak evidence. If a `[CHECKPOINT]` line reported at a checkpoint trigger carries `verdict=invalidated`, the Verdict is Invalidated, whatever the success-criteria assessment shows; if the evidence otherwise supports the hypothesis, recommend a follow-up PoC with refined criteria as the next step (`poc-guidelines.md` § Hypothesis-First Validation, Rule 4).
````

## 3. Per-edit statements (carried over from v1 §9 and v2 §2)

| Edit | Upward? (ADR-008 Validation 4) | Relaxes a check? (ADR-007 §5) | Golden coupling | Touches security? |
|---|---|---|---|---|
| **N1** | **No.** The file is a skill, not tier 1 and not a command | **No.** It adds no permission. F1 makes explicit that `validation-gates`' own rules, including its security rules, are among the sets no other set may relax | `validate-workflow-gate-verdict-sources` holds a fixture copy frozen at `7be9926`, and `check()` reads only the fixture. N1 adds neither "every gate must produce a verdict" nor a `**Gate:**` line. **No quote, fixture or result change** | It changes no security criterion. It was classified as touching for routing, and the **Security Engineer phrase check is done: PASS**, with F1 and F2 adopted |
| **N2** | **No** | **No.** The N2 point narrows the example to non-security highs, matching `validation-gates:70` ("The "documented mitigations" route above is for high findings outside the security category only") | No open case is coupled | It changes no security criterion. Its example now matches the security exclusion, per the Security Engineer's N2 point |
| **N3** | **No** | **No** | No open case is coupled | **No** |
| **P1** | **No.** A skill, amended to the user's P43 decision | **No.** Every `rapid-prototyping` invalidation rule survives: `:127` (binary at a trigger, time-box, partial result) and the `:136` showstopper trigger | No open case cites or copies the live file. Golden cases that mention these names hold only frozen snapshots (the orchestrator verified this) | **No** |
| **P2** | **No.** A skill; `/evaluate-poc` is untouched | **No.** It only adds an `INVALIDATED` condition. `:115`–`:117` are unchanged. The command's `Status` value set and Failure mode are untouched | `evaluate-poc-verdict-debt-reconciliation`: `brief.md:11` quotes only the command, and `check()` reads only `fixture/poc-evaluation.md` (`expect.py:107`). **No quote, fixture or result change** | **No** |
| **P3** | **No.** An agent; `poc-orchestrator` is untouched | **No.** It only adds an `Invalidated` condition; `:49` is unchanged | No open case is coupled | **No** |

**Not amended:**
- every tier-1 file and every command, including `/evaluate-poc` and `/code-review`;
- `poc-orchestrator.md`, `orchestrator.md`, `security-engineer.md` (FU-6), `qa-engineer.md` and `tech-lead.md`;
- `tests/golden/**`.

## 4. Consolidated implementation list

| # | Edit | File | Anchor (line at `c0138a7`) | Security Engineer phrase check |
|---|---|---|---|---|
| 1 | N1 | `implementation/knowledge/skills/validation-gates/SKILL.md` | `### Severity Definitions` (`:72`) | **Done: PASS** (F1 and F2 applied) |
| 2 | N2 | `implementation/knowledge/skills/code-review/SKILL.md` | `### Artifact Version Awareness` (`:130`) | Not required; the N2 point applied |
| 3 | N3 | `implementation/knowledge/skills/testing-strategy/SKILL.md` | full `:233` line | Not required |
| 4 | P1 | `implementation/knowledge/skills/rapid-prototyping/SKILL.md` | `**Evidence items** should be specific and measurable:` (`:129`) | Not required |
| 5 | P2 | `implementation/knowledge/skills/poc-evaluation/SKILL.md` | full `:117` line | Not required |
| 6 | P3 | `implementation/knowledge/agents/evaluation-agent.md` | `Tie conclusions directly to observable outcomes.` (`:22`) | Not required |

**Mechanics** (for the implementing task):
1. **Apply each edit by its Before text.** Each Before must match exactly once at dispatch.
2. **Regenerate and check.** Run `node implementation/scripts/sync.mjs --root implementation` and
   `python3 implementation/scripts/generate-registry.py`, each followed by `--check`.
3. **Declare root drift** exactly as `--print-drift` reports it: up to 6 files × 7 platforms = 42 paths **(unverified)**.
4. **Golden and maturity checks.** `scripts/scorecard.py --check` must match the current baseline, and
   `check-maturity.py --root implementation` must report 0 failing.
5. **No protected-path grant is needed.**
6. **Expected hit counts** under `implementation/knowledge/` (case-sensitive):
   - `Criteria from the executor's own documents`: 3 (N1, N2, N3);
   - `the rules above included`: 2 (N1);
   - `this note covers two of the gates`: 1 (N1);
   - `outside the security category with a documented mitigation`: 1 (N2);
   - `the paragraph "Criteria from the executor's own documents"`: 2 (N2, N3);
   - `is the PoC's outcome`: 1 each in `rapid-prototyping` (P1) and `poc-evaluation` (P2);
   - `Your Verdict is the PoC's outcome`: 1 (P3);
   - `None of them makes another less strict` and `for two of the gates:`: **0** (the v2 wording must not land).

## 5. Summary

| Slice | Outcome | Authority | Edits |
|---|---|---|---|
| P40 S2 | Strictest applies | ADR-008 Step A (v1 §3), adopted by the user | N1, N2 |
| P40 S3 | Strictest applies | ADR-008 Step A (v1 §4), adopted by the user | N1, N3 |
| P40 S4 | Jointly satisfiable; no amendment | ADR-008 Step A (v1 §5) | none (FU-6 untouched) |
| P43 | The evaluation decides, tighten-only | User decision (ADR-008 § Scope); v1 §6–§7; v2 §1–§2 | P1, P2, P3 |

- **Maturity:** not relied on anywhere.
- **Blockers:** none.
- **Unverified (no shell):** the root-drift path count. The anchor uniqueness and the golden coupling are verified by the
  orchestrator.
