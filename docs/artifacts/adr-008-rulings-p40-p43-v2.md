# Artifact: adr-008-rulings-p40-p43-v2.md

> Filename: `adr-008-rulings-p40-p43-v2.md`. Immutable once produced; revisions bump `<N>`.

## Metadata

- **Producer agent**: solution-architect
- **Task**: T584 (P2, decision only), second version
- **Created**: 2026-10-07
- **Based on**:
  - `docs/artifacts/adr-008-rulings-p40-p43-v1.md`. v1 is unchanged; **where the two differ, v2 governs**. v2 is the
    single implementation input.
  - The user's decisions of 2026-10-07, relayed verbatim by the orchestrator:
    - P43: **"Evaluation decides, tighten-only (Recommended)"**, which is v1 §7 option 1;
    - P40 S2/S3: **"Strictest applies (Recommended)"**. The user adopts the rule, v1 §1.1's Step A reading stands, and
      CQ-1 (v1 §8) is not needed;
    - Notes: **"N1 + N2 + N3 (Recommended)"**.
  - The orchestrator's verification of v1:
    - all 65 cited quotes are verbatim at `a54bbba`;
    - `implementation/` is identical between `a54bbba` and `c0138a7`;
    - each N1/N2/N3 anchor occurs exactly once, at `validation-gates:72`, `code-review:130` and `testing-strategy:233`.
  - `docs/decisions/ADR-008-knowledge-document-authority.md` (§ Scope: "A question already settled by … a recorded user
    decision. That decision governs, and documents are amended to it."); `docs/decisions/ADR-007-command-contract-authority.md` §5.
  - Source files re-read at `develop` `c0138a7`, as listed in §6.
- **Supersedes**: `adr-008-rulings-p40-p43-v1.md`, for implementation purposes. v1's analysis (§§1–8, 10–12) still
  stands and is referenced below, not repeated.
- **Decision references**: the user's P43, S2/S3 and notes decisions above; ADR-008 Step A (S2, S3, S4) and § Scope
  (P43); ADR-007 §5.

## 1. The user's decisions, recorded

| Item | v1 outcome | User decision (verbatim label) | Effect |
|---|---|---|---|
| **P43** | P5 escalation (v1 §6, §7) | **"Evaluation decides, tighten-only (Recommended)"** | **Decided.** The PoC's outcome is the evaluation's verdict. The `[CHECKPOINT]` `verdict=` is the prototyping agent's report and an input to the evaluation. The evaluation may turn `validated` into `INVALIDATED`, but it never turns a trigger checkpoint's `invalidated` into `VALIDATED`. In that case a follow-up PoC with refined criteria is the next step. The P5 hold (Form 3) is lifted, and documents are amended to the decision (ADR-008 § Scope). Edits P1–P3 in §2. |
| **P40 S2, S3** | Step A: jointly satisfiable (v1 §3, §4) | **"Strictest applies (Recommended)"** | **Adopted.** v1 §1.1 stands, and CQ-1 (v1 §8) is withdrawn. The rule is now also a recorded user decision. |
| **P40 S4** | Step A: jointly satisfiable (v1 §5) | — | Unchanged. No amendment; FU-6 is untouched. |
| **Notes** | N1 recommended; N2 and N3 optional (v1 §9) | **"N1 + N2 + N3 (Recommended)"** | All three are required. They are carried over unchanged in §3. |

v1 §6.5's P5 blocker for P43 is **closed by the user's decision**.

## 2. P43 amendments (new in v2)

**Common to P1–P3:**
- **Authority.** The user's P43 decision (ADR-008 § Scope).
- **Character.** No rank is created. Each edit states the decided issuer, adds one invalidation condition, and removes
  no existing condition.
- **Files not amended:** `/evaluate-poc`, `poc-orchestrator`, `poc-guidelines.md`, and every tier-1 file.
- **Encoding.** `§` is U+00A7 and `–` is U+2013. No emoji is introduced.

### P1: `implementation/knowledge/skills/rapid-prototyping/SKILL.md`, a note before `:129`

**Anchor:** `**Evidence items** should be specific and measurable:`. Re-read at `:129`; it occurs once in the file.

````
Before:
**Evidence items** should be specific and measurable:

After:
**The PoC's outcome.** The `verdict=` in this line is the prototyping agent's report and an input to the PoC evaluation (the poc-evaluation skill); it is not the PoC's outcome. The outcome is the evaluation's verdict: the poc-evaluation skill's `[VERDICT]` `result=`, which is the `/evaluate-poc` command's `Status` when the evaluation is run through that command, or the `evaluation-agent`'s Verdict. The evaluation may turn a `validated` reported here into `INVALIDATED`. It never turns an `invalidated` reported at a trigger into `VALIDATED`: if the evidence later appears to support the hypothesis, the next step is a follow-up PoC with refined criteria (`poc-guidelines.md` § Hypothesis-First Validation, Rule 4).

**Evidence items** should be specific and measurable:
````

### P2: `implementation/knowledge/skills/poc-evaluation/SKILL.md:117`, a rule appended to § Hypothesis Success Criteria Reference › Rules

**Anchor:** the whole `:117` line, re-read verbatim; it occurs once in the file.

````
Before:
- Otherwise, if any such criterion is "Not Tested" or rests only on weak evidence, the verdict is `INVALIDATED` with `Evidence strength: weak`, and the Recommended next step names a follow-up PoC with refined criteria. Never force a `VALIDATED` call (`poc-guidelines.md` § Hypothesis-First Validation, Rules 3–4).

After:
- Otherwise, if any such criterion is "Not Tested" or rests only on weak evidence, the verdict is `INVALIDATED` with `Evidence strength: weak`, and the Recommended next step names a follow-up PoC with refined criteria. Never force a `VALIDATED` call (`poc-guidelines.md` § Hypothesis-First Validation, Rules 3–4).
- This verdict is the PoC's outcome. A `[CHECKPOINT]` line from the rapid-prototyping skill is an input to it (§ Hypothesis Validation Checkpoint Format there), never a substitute for this assessment: its `verdict=validated` does not stand in for a criterion that the rules above find untested, unmet or resting only on weak evidence. If a `[CHECKPOINT]` line reported at a checkpoint trigger carries `verdict=invalidated`, the verdict is `INVALIDATED`, whatever the assessment table shows; if the assessment would otherwise support `VALIDATED`, the Recommended next step names a follow-up PoC with refined criteria (`poc-guidelines.md` § Hypothesis-First Validation, Rule 4).
````

### P3: `implementation/knowledge/agents/evaluation-agent.md:22`, the same rule

**Anchor:** `Tie conclusions directly to observable outcomes.`. Re-read at `:22`; it occurs once in the file. `:48` reads
"directly tied to observable outcomes", which is different text.

````
Before:
Tie conclusions directly to observable outcomes.

After:
Tie conclusions directly to observable outcomes.

Your Verdict is the PoC's outcome. A prototyping agent's `[CHECKPOINT]` line (skill `rapid-prototyping`, § Hypothesis Validation Checkpoint Format) is an input to it, never a substitute for evidence: its `verdict=validated` does not stand in for a success criterion that is untested, unmet or supported only by weak evidence. If a `[CHECKPOINT]` line reported at a checkpoint trigger carries `verdict=invalidated`, the Verdict is Invalidated, whatever the success-criteria assessment shows; if the evidence otherwise supports the hypothesis, recommend a follow-up PoC with refined criteria as the next step (`poc-guidelines.md` § Hypothesis-First Validation, Rule 4).
````

### Per-edit statements

| Edit | Upward? (Validation 4) | Relaxes a check? (ADR-007 §5) | Golden coupling | Touches security? |
|---|---|---|---|---|
| **P1** | **No.** The file is a skill, not tier 1 and not a command, and it is amended to a user decision | **No.** It removes no condition. Every invalidation rule in `rapid-prototyping` survives unchanged: binary at a trigger, time-box expiry, partial result (`:127`), and the showstopper trigger (`:136`). It states that its `invalidated` binds the outcome | No open case cites or copies the live file (T584 brief §2.7). The `/discover-skills` case holds an installed copy, checked for presence only, per `poc-skill-command-overlaps-v1.md` §16.1 **(not re-read)**. No quote, fixture or result change | **No** |
| **P2** | **No.** A skill, amended to a user decision; `/evaluate-poc` is untouched | **No.** It only adds an `INVALIDATED` condition. `:115`–`:117` are unchanged. `/evaluate-poc`'s `Status` value set and Failure mode are untouched: the command leaves open when `VALIDATED` may be given, and P2 narrows that within the command's contract (ADR-008 P2, D4 specialisation) | `evaluate-poc-verdict-debt-reconciliation`: **confirmed by re-read.** Its `brief.md:11` quotes `implementation/knowledge/commands/evaluate-poc.md` "verbatim", not the skill. Its `check()` reads only `case_dir / "fixture" / "poc-evaluation.md"` (`expect.py:107`), which is a hand-authored output, not the skill file. No quote, fixture or result change | **No** |
| **P3** | **No.** An agent, amended to a user decision; `poc-orchestrator` is untouched | **No.** It only adds an `Invalidated` condition; the Rails Failure mode (`:49`) is unchanged | No open case cites or copies `agents/evaluation-agent.md` (T584 brief §2.7) | **No** |

**Consistency with the files left unedited.**
- **`poc-orchestrator`** is consistent as it stands. `:38` ("Delegate to `@evaluation-agent` for hypothesis verdict"),
  `:56` and `:101` already route the outcome to the evaluation. `:65`'s timebox verdict is Rule 3's `invalidated`, which
  P1–P3 preserve.
- **`/evaluate-poc`** is consistent as it stands. Its Status is the evaluation's verdict.
- **`poc-guidelines.md`.** Its Rule 4 single outcome is now met by construction.

## 3. N1, N2 and N3, carried over unchanged from v1 §9

These are byte-identical to v1. The orchestrator verified each anchor once, and I re-read each anchor at `c0138a7`.

### N1: `implementation/knowledge/skills/validation-gates/SKILL.md`, before `:72`

````
Before:
### Severity Definitions

After:
**Criteria from the executor's own documents.** Other documents also state verdict criteria for two of the gates: skill `code-review` § VERDICT Format for Validation Gates (Implementation gate); skill `testing-strategy` § VERDICT Format for QA Gate and § Coverage Thresholds That Determine Gate Outcome, and the `qa-engineer` agent's § Validation Gate Protocol (Integration gate). They apply together with the rules above to the gate's one verdict. A PASS or CONDITIONAL_PASS row states what that verdict requires; it does not grant the verdict when another applicable criterion requires a stricter one. So the verdict is PASS only if every applicable set of criteria admits PASS, CONDITIONAL_PASS only if every one admits at least CONDITIONAL_PASS, and FAIL otherwise. None of them makes another less strict.

### Severity Definitions
````

### N2: `implementation/knowledge/skills/code-review/SKILL.md`, before `:130`

````
Before:
### Artifact Version Awareness

After:
These definitions apply together with skill `validation-gates` § Verdict Rules, which applies to the same verdict (§ Criteria from the executor's own documents there). Grade each finding on both scales, this skill's § Severity Guide and that skill's § Severity Definitions, and give the most restrictive verdict either requires. A Must Fix finding is `FAIL` even where that skill would admit `CONDITIONAL_PASS` for a high finding with a documented mitigation, and a high finding without a documented mitigation is `FAIL` even when it is graded Should Fix here.

### Artifact Version Awareness
````

### N3: `implementation/knowledge/skills/testing-strategy/SKILL.md:233`

````
Before:
The following coverage thresholds directly determine the QA gate verdict:

After:
The following coverage thresholds directly determine the QA gate verdict, together with skill `validation-gates` § Verdict Rules and the executing agent's own gate criteria; the verdict is the most restrictive that any of them requires (`validation-gates` § Verdict Rules, Criteria from the executor's own documents):
````

**The per-edit statements are unchanged from v1 §9.** In short:
- none is upward, and none relaxes a check;
- N1 is classified as touching security criteria for routing, so it gets a Security Engineer phrase check;
- N1's golden coupling: the `validate-workflow-gate-verdict-sources` fixture copy is frozen at `7be9926`, and there is
  no quote, fixture or result change;
- N2 and N3 have no open-case coupling.

**Flag, wording not changed.** N2 and N3 cite "Criteria from the executor's own documents" with `§`, but N1 introduces
that label as a bold lead-in paragraph, not as a heading. The reference is findable as written. If the implementer or
the Security Engineer prefers, `§` could become "the paragraph" in both N2 and N3. I have **not** made that change.

## 4. Consolidated implementation list

| # | Edit | File | Anchor (line at `c0138a7`) | Source | Security Engineer phrase check? |
|---|---|---|---|---|---|
| 1 | N1 | `implementation/knowledge/skills/validation-gates/SKILL.md` | `### Severity Definitions` (`:72`) | v1 §9, unchanged | **Yes** |
| 2 | N2 | `implementation/knowledge/skills/code-review/SKILL.md` | `### Artifact Version Awareness` (`:130`) | v1 §9, unchanged | No |
| 3 | N3 | `implementation/knowledge/skills/testing-strategy/SKILL.md` | `The following coverage thresholds directly determine the QA gate verdict:` (`:233`) | v1 §9, unchanged | No |
| 4 | P1 | `implementation/knowledge/skills/rapid-prototyping/SKILL.md` | `**Evidence items** should be specific and measurable:` (`:129`) | §2 | No |
| 5 | P2 | `implementation/knowledge/skills/poc-evaluation/SKILL.md` | the full `:117` line | §2 | No |
| 6 | P3 | `implementation/knowledge/agents/evaluation-agent.md` | `Tie conclusions directly to observable outcomes.` (`:22`) | §2 | No |

**Mechanics** (for the implementing task):
1. **Apply each edit by its Before text.** Each Before must match exactly once at dispatch.
2. **Regenerate and check.** Run `node implementation/scripts/sync.mjs --root implementation` and
   `python3 implementation/scripts/generate-registry.py`, each followed by `--check`.
3. **Declare root drift** exactly as `--print-drift` reports it: 6 files × 7 platforms, up to 42 paths **(unverified)**.
4. **Golden and maturity checks.** `scripts/scorecard.py --check` must match the current baseline, and
   `check-maturity.py --root implementation` must report 0 failing.
5. **No protected-path grant is needed.** No `tests/golden/**` file changes.
6. **Byte-unchanged:** `AGENTS.md`, every instruction, every command (including `/evaluate-poc` and `/code-review`),
   `poc-orchestrator.md`, `orchestrator.md`, `security-engineer.md`, `qa-engineer.md`, `tech-lead.md`, and
   `tests/golden/**`.
7. **Expected hit counts** under `implementation/knowledge/` (case-sensitive):
   - `Criteria from the executor's own documents`: 3 (N1, N2, N3);
   - `is the PoC's outcome`: 1 in `rapid-prototyping` (P1) and 1 in `poc-evaluation` (P2);
   - `Your Verdict is the PoC's outcome`: 1 (P3).

## 5. Summary

| Slice | Outcome | Authority | Edits |
|---|---|---|---|
| P40 S2 | Strictest applies | ADR-008 Step A (v1 §3), adopted by the user | N1, N2 |
| P40 S3 | Strictest applies | ADR-008 Step A (v1 §4), adopted by the user | N1, N3 |
| P40 S4 | Jointly satisfiable; no amendment | ADR-008 Step A (v1 §5) | none (FU-6 untouched) |
| P43 | The evaluation decides, tighten-only | User decision (ADR-008 § Scope); v1 §6–§7 | P1, P2, P3 |

**Maturity** is not relied on anywhere. **Blockers:** none.

## 6. Verification notes

**Re-read at `c0138a7`:**
- `rapid-prototyping:117–138`;
- `poc-evaluation:106–121`;
- `evaluation-agent.md` in full;
- `validation-gates:70–72`, `code-review:128–130`, `testing-strategy:231–233`.

The uniqueness of the P1–P3 anchors rests on full-file reads in this task (v1 §0). I have no shell, so a `grep -c` is
still owed for P1–P3. The orchestrator has already confirmed N1–N3.

**Unverified:**
1. The P1–P3 anchor counts by `grep`.
2. The root-drift path count.
3. The `/discover-skills` case's installed copies (presence-only, per `poc-skill-command-overlaps-v1.md` §16.1). I did
   not re-read that case.
