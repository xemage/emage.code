# Artifact: remaining-verdict-renderings-v1.md

> Filename: `remaining-verdict-renderings-v1.md`. Immutable once produced; revisions bump `<N>`.

## Metadata

- **Producer agent**: solution-architect
- **Task**: T593 (P2, judgment tier, decision only)
- **Created**: 2026-10-08
- **Based on**:
  - `docs/tasks/task-T593.md` (the brief, authoritative);
  - `docs/plans/plan-107-remaining-verdict-renderings.md`;
  - `docs/artifacts/gate-verdict-consistency-v1.md`: §7 G3–G9, §13.1 and §13.3 (P41);
  - `docs/decisions/ADR-008-knowledge-document-authority.md` (Accepted) and
    `docs/decisions/ADR-007-command-contract-authority.md` (Accepted);
  - inputs that are **not reopened**: `conditional-pass-semantics-v4.md` (P39), `adr-008-rulings-p40-p43-v3.md`
    (P40/P43), `security-gate-alignment-v2.md`, `security-finding-grading-and-owasp-run-v2.md`,
    `security-grade-definitions-v2.md`;
  - `docs/artifacts/poc-skills-alignment-v1.md` §4d and E13 (the precedent for G7);
  - the user's instruction of 2026-10-08, "Continue with the next best step" (the recommended step was P41), and the
    user's standing ADR-008 review decision Q1, **"Self-placement only"**.
- **Supersedes**: none (first version).
- **Decision references**: ADR-008 Step A (P3a), Step B (P1), Step E (P5); ADR-008 § Scope; ADR-007 §5 (never relax a
  check); the T570 precedent (`poc-skills-alignment-v1.md` §4d, re-derived at Step B in ADR-008 Validation 1). No new
  ADR is minted.

## 0. Method and limits

- **Commit.** Every line below was re-read on the worktree `agent-solution-architect-T593`, which the orchestrator
  states is on `develop` `f301cf6`. Line numbers are at that commit. Many differ from T572's; §9 lists the shifts.
- **No shell.** No `grep`, `git`, `cmp` or test run. Uniqueness of anchors and every hit count come from reading whole
  files and are **(unverified by grep)**. §10 collects every unverified claim.
- **Golden.** I read, under `tests/golden/open/` only: the `brief.md` and `expect.py` of
  `prepare-release-real-verdict-missing`, `prepare-release-changelog-grouping-compliant`,
  `prepare-release-conditional-pass-conditions-gap`, `code-review-conditional-pass-conditions-gap`,
  `code-review-fail-blocker-details` and `validate-workflow-gate-verdict-sources`; the `brief.md` of the three
  `security-audit-*` cases named in brief §2.4; the `case.yaml` of two `prepare-release-*` cases; and the fixtures
  `prepare-release-conditional-pass-conditions-gap/fixture/release-notes.md`,
  `code-review-conditional-pass-conditions-gap/fixture/review.md` and
  `code-review-fail-blocker-details/fixture/review.md`. **I never opened `tests/golden/held-out/`.** Some open briefs
  name sibling cases; I do not repeat any name that lacks a `tests/golden/open/` directory.
- **Secrets.** I read no `.env*`, credential or key file.
- **Files read in full (source):** `implementation/AGENTS.md` and the root `AGENTS.md:1–60`; skills
  `validation-gates`, `code-review`, `release-workflow`, `project-planning`, `task-management`,
  `receiving-code-review`, and `testing-strategy:1–30, 195–254`; agents `qa-engineer`, `security-engineer`,
  `release-manager`, `tech-lead`, `orchestrator`, `scrum-master`; commands `code-review`, `security-audit`,
  `prepare-release`, `validate-workflow`; `docs/releases/_template.md`; `scripts/verify-release-docs.py`;
  `implementation/knowledge/README.md`; `docs/plans/plan-092-poc-contract-amendments.md` (for P32) and plan-095.
- **Encoding.** `§` is U+00A7, `—` is U+2014, `→` is U+2192. No emoji is introduced. Each four-backtick fence holds one
  Before/After pair; inner fences are literal three-backtick fences. Apply each edit by its Before text, never by line
  number.
- **Scope-gaming guard (ADR-008 § Risks).** Declared scope is read as of the commit where the conflict was first
  recorded: T572, `24518f6`. Every scope sentence a ruling below *relies on* was quoted by T572 itself at that commit
  (cited "T572-quoted"), except where marked. Later sentences (for example `validation-gates:72`, added by T585) are
  used only as corroboration.

## 1. Authority basis (summary)

ADR-008 § Order of application: A (joint satisfiability, every pair) → B (tier 1: `AGENTS.md`, stable instructions) →
C (a command's declared output, for a skill or agent applied under it) → D (peers: self-placement only, per Q1) → E
(escalate). Maturity never ranks (P4). A command clause changes only on ADR-007 branch 1 or a user decision. No edit
below is upward (never `AGENTS.md`, never a stable instruction), none relaxes a check, and none touches an input
artifact's ruling.

## 2. G3 — six further verdict renderings

### 2.1 Common frame

**Subject (D3):** the format of one gate's verdict: whether each rendering is jointly satisfiable with `validation-gates`
§ Verdict Format.

**The canonical clause.** `validation-gates:33`: "Every gate MUST produce a verdict in this format:"; `:11`: "Each gate
produces a structured verdict (PASS, CONDITIONAL_PASS, or FAIL)". Neither says "only", "instead of" or "no other", so
it is not exclusive (T572 §1.2(i), carried into ADR-008 P3a).

**Declared scope relied on (D2).** `validation-gates:3` (description, T572-quoted): "Use when performing code review
gates, QA gates, security audits, or release readiness checks." `:193` (Rails Inputs, T572-quoted as `:185`): "A gate
type (architecture/implementation/integration/security/release), its designated executor agent, and that gate type's
required inputs". A rendering that maps onto one of the five kinds is within the canonical format's reach.

**One-value test (P3a step 3).** All renderings of one gate's verdict must carry one value. The criteria that compute
that value are settled inputs: `validation-gates:72` (N1, strictest applies, implementation and integration);
P39 (`conditional-pass-semantics-v4.md`); P40 S4 (security gate, jointly satisfiable); Q-O1 (grades under
`/security-audit`). None is reopened. The test below asks only whether two renderings could carry different values
for the same run.

**Notes or nothing.** T572's test for adding a note (E1, E2, E6): the file's heading reads, standing alone, as *the*
format of the gate, and the file nowhere says what it accompanies. Commands get no note: ADR-007 gives no basis to add
to a command's contract (T572 V7; ADR-008 P2 Remedy), and a command changes only by user decision.

### 2.2 D5 records

| # | Rendering (verbatim, file:line at `f301cf6`) | Gate kind, and the basis | Step A: MUSTs, exclusivity | One-value test | Step fired | Amendment |
|---|---|---|---|---|---|---|
| G3.1 | `qa-engineer:163` "## VERDICT: [PASS \| CONDITIONAL_PASS \| FAIL]" in § Structured Test Report (`:130–173`); `:132` "Every test execution must produce a structured report:"; `:114–115` "1. Every QA run must end with a gate verdict: - `pass`, `conditional_pass`, or `fail`."; `:220` "6. QA gate verdict (`pass`, `conditional_pass`, `fail`) with release impact" | **integration.** `validation-gates:27` "\| **Integration** \| QA Agent \| After feature merge, before release \|"; `orchestrator.md:208–209` "**INTEGRATION GATE** … Delegate to `@qa-engineer`: … Produce VERDICT." (both T572-quoted). Corroboration: `validation-gates:72` "the `qa-engineer` agent's § Validation Gate Protocol (Integration gate)" | Two non-exclusive MUSTs (`:114`, `:132` against `vg:33`). The report adds Summary, Coverage, Failed Tests, Acceptance Criteria, Justification, Conditions and Blockers: additions (D4) | **Holds.** `:114` makes every QA run a gate run, so the report's `## VERDICT:`, the `:115` token and the `:220` output are one gate's verdict. One set of criteria computes it (`:116–120` with `vg:72`). Case only differs (G8) | **A** | **E-Q1** (note, recommended, not compelled): the file never names `validation-gates` and its heading reads as the gate's format |
| G3.2 | `security-engineer:167` "## VERDICT: [PASS \| CONDITIONAL_PASS \| FAIL]" under `:162` "## VERDICT Format" and `:164` "Every security audit MUST conclude with a structured verdict:"; `:155` "1. Every audit must end with a gate verdict: `pass`, `conditional_pass`, or `fail`."; **also** `:98` "- **Status**: [Pass \| Fail \| Conditional Pass]" in § Security Review Report Format's Summary (not listed in T572 G3) | **security.** `validation-gates:28` "\| **Security** \| Security Agent \| Before any release \|"; `orchestrator.md:213–214` "**SECURITY GATE** … Delegate to `@security-engineer`: "Run OWASP Top 10 audit. Produce VERDICT."". Per run it is one kind: at the orchestrator's Architecture gate (`orchestrator.md:203`) the same agent's verdict is a second canonical block with `**Gate:** architecture` (T572 F3) | Non-exclusive MUSTs (`:164`, `vg:33`). The Findings Summary, Justification, Conditions, Blockers and OWASP Coverage are additions | **Holds.** `:98`, `:155` and `:167` are one audit's verdict, computed by `:155–157` (which cite `validation-gates` § Verdict Rules). Under `/security-audit` the command's `:69` rule computes the same value (P40 S4; Q-O1). `:98`'s "Conditional Pass" is a spelling variant (G8) | **A** | **E-S1** (note, recommended): the heading reads as the gate's format; the file cites `validation-gates` for criteria but never for format |
| G3.3 | `release-manager:164` "## RELEASE VERDICT: [PASS \| CONDITIONAL_PASS \| FAIL]" under `:159` "## Release Gate VERDICT" and `:161` "Every release decision MUST conclude with a structured verdict:"; `:238` "6. Release gate VERDICT (PASS/CONDITIONAL_PASS/FAIL) with full justification" | **release.** `validation-gates:29` "\| **Release** \| Release Manager \| Before deployment \|"; `orchestrator.md:216–217` "**RELEASE GATE** (before deployment): - Delegate to `@release-manager`: "Verify release readiness. Produce VERDICT."" (both T572-quoted) | Non-exclusive MUSTs (`:161`, `vg:33`, and `/prepare-release:38`, which `/prepare-release:61` reaches by naming "`release-manager` § Release Gate Policy"). The heading text equals the command's `## RELEASE VERDICT` with a different shape, but the agent never places its block in the release notes document: its block is its return (Output Format `:238`) | **Holds.** Release-manager's `:44–47` and `:216` state only blocking conditions; `/prepare-release:61, :69` state FAIL and CONDITIONAL_PASS rules (P39 R1–R5). Neither grants PASS where the other blocks, so the most restrictive value satisfies both | **A** | **E-R1** (note, recommended) — **held until G4 is decided** (§4): its sense presupposes that the release manager makes the release decision |
| G3.4 | `/code-review:36–49` "10. **Produce a structured VERDICT** at the end of the review:" then "## VERDICT" with "- **Status**: PASS \| CONDITIONAL_PASS \| FAIL"; `:22` "7. Gate status recommendation (`pass`, `conditional_pass`, `fail`)" | **implementation.** `agent: "tech-lead"` (`:3`); `validation-gates:26`; `/validate-workflow:26` "Code review gate — `validation-gates` skill § Gate Types, **Implementation**" (T572 §2) | Non-exclusive (`:36`, `vg:33`). Same as T572 V7: both can be produced | **Holds.** `:51–53` (P39 A4) and the `code-review` skill's definitions (N2) with `validation-gates` § Verdict Rules compute one value; `:22`'s "recommendation" is the same value in lowercase (G8) | **A** | **none.** ADR-007 gives no basis to add to the contract (T572 V7). The skill side already states the relationship (`code-review:121`, `tech-lead:68`) |
| G3.5 | `/security-audit:52–66` "10. **Produce a structured VERDICT** at the end of the audit:" then "## VERDICT" with "- **Status**: PASS \| CONDITIONAL_PASS \| FAIL" | **security.** `agent: "security-engineer"` (`:3`); `/validate-workflow:28` "Security audit gate — `validation-gates` skill § Gate Types, **Security**" | Non-exclusive (`:52`, `vg:33`) | **Holds.** `:69` and `security-engineer:155–157` compute one value (P40 S4, Q-O1 settled) | **A** | **none** (as G3.4). E-S1 states the relationship from the agent's side |
| G3.6 | `release-workflow:149–154` "## Gate Verdicts - Architecture: <PASS/CONDITIONAL_PASS> on YYYY-MM-DD … - Release: <PASS/CONDITIONAL_PASS> on YYYY-MM-DD" in the release-notes template (`:131–158`) | **all five**, one line each; the Release line maps to **release** | No MUST to produce a verdict here; the list reports stored verdicts (`:100` "Review gate verdict documents in `docs/artifacts/` for additional context") | **Holds by construction**: each line copies the stored verdict of its gate | **A** | **none.** It defines no verdict format and states that it summarises; a note would add nothing. (Its path is G5.) |

**Maturity** was not relied on in any G3 record (`qa-engineer`, `security-engineer`, `release-manager` and
`/security-audit` are `stable`; `/code-review` and `release-workflow` are `experimental`; neither fact is a reason).

**Not taken: a note in the `code-review` skill or `tech-lead` stating that under `/code-review` the command's
`## VERDICT` is the declared output.** P2's remedy applies only when Step A fails (P2(c)); here it holds.

## 3. G6 — second verdict vocabularies in `code-review` and `tech-lead`

### 3.1 D5 record G6.1: the review document's `### Verdict:` value set (`code-review`)

| Field | Content |
|---|---|
| **Subject (D3)** | A value set: the values of the review document's `### Verdict:` field. |
| **Clauses** | `code-review:72` (in § 3. Feedback Format, `:67–92`): "### Verdict: [Approved \| Changes Requested \| Needs Discussion]". Same file `:115`: "Code review is a **validation gate** in the emage.code workflow. Every review MUST conclude with a structured verdict that downstream gates (CI/CD, release) can consume:"; `:118` "[VERDICT] gate=code-review \| result=PASS\|CONDITIONAL_PASS\|FAIL \| …"; `:125–129` the PASS / CONDITIONAL_PASS / FAIL definitions. Tier 1: `AGENTS.md:51–52` "## Validation Gates - VERDICTS: `PASS` \| `CONDITIONAL_PASS` \| `FAIL`". |
| **Step A** | **Fails.** `AGENTS.md:52` fixes a closed value set for a validation gate's verdict (P3a step 2: "fixes a closed value set for the same field"). `code-review:115` makes every review a validation gate with one structured verdict (`validation-gates:11`, singular). The document's `### Verdict:` is therefore that one verdict, carried in values outside the set. No criterion links "Approved" or "Changes Requested" to PASS / CONDITIONAL_PASS / FAIL, so one review can carry `### Verdict: Approved` and `result=FAIL` (P3a step 3: two values for one decision). "Needs Discussion" has no counterpart at all. |
| **Coexistence and mapping (brief §1)** | A coexisting second vocabulary would need a total, one-to-one mapping. None exists in any text. `CONDITIONAL_PASS` has no natural label ("Approved" drops its conditions; "Changes Requested" suggests a blocked merge, against P39), and "Needs Discussion" maps to no gate value. Writing a mapping would invent one (the T570 §3 test: "an edit with no authority behind it"). So the two cannot coexist as renderings; the field takes the gate values. |
| **"Needs Discussion" (brief §1)** | It maps to **no verdict value**, and the texts already say what replaces it. (1) An open point that is a defect is a finding, graded on the scale (`code-review:95–99`), and the verdict follows from the definitions (`:125–129`). (2) A review that cannot conclude because a question stays open has no verdict yet: `validation-gates:195` (Rails, Failure mode) "A gate that cannot produce a verdict … is not silently skipped — the executor reports a blocker per the requesting agent's own blocker protocol rather than fabricating a PASS"; `AGENTS.md:49` "Agents MUST NOT silently fail."; `code-review:106` "Ask questions when you're uncertain". The merge waits, because `code-review:161` (Rails, Out of scope) excludes "approving a merge without producing the structured VERDICT block". **Rejected alternative: map it to `FAIL`.** `FAIL` is defined as "One or more must-fix findings" (`:129`; `validation-gates:68` likewise names findings). A `FAIL` with no finding would contradict the definition. |
| **Step fired** | **B (P1).** (a) Quotable: `AGENTS.md:52` against `code-review:72`. (b) Within scope: `AGENTS.md` "declares no scope narrower than the repository" (ADR-008 D2), and `code-review:115` places code review among validation gates in its own words (T572-quoted as `:114`). (c) Step A fails. (d) `code-review` is a skill. Corroborated by same-file coherence with `:115–129`. |
| **Declared scope relied on** | `AGENTS.md` § Validation Gates (repository-wide); `code-review:115` "Code review is a **validation gate**". |
| **Amendment** | **E-G6a** (§7.4): the field takes `PASS \| CONDITIONAL_PASS \| FAIL`, with a note citing `AGENTS.md` and stating the open-point and open-question rules from the texts above. |
| **Maturity** | Not relied on (`code-review` is `stable`; irrelevant). |

### 3.2 D5 record G6.2: the review feedback's `### Status:` value set (`tech-lead`)

| Field | Content |
|---|---|
| **Subject (D3)** | A value set: the values of the review feedback's `### Status:` field. |
| **Clauses** | `tech-lead:47` (in § Review Feedback Format, `:43–64`): "### Status: [Approved \| Changes Requested \| Needs Discussion]". Same file `:196` (Output Format): "When reviewing code, return structured review feedback with a VERDICT (PASS/CONDITIONAL_PASS/FAIL)."; `:29–30` (T572-quoted): "See skill `code-review` for the full structured checklist, feedback format, and VERDICT conventions this section summarizes."; `:71` "## VERDICT: [PASS \| CONDITIONAL_PASS \| FAIL]". Tier 1: `AGENTS.md:52`. |
| **Step A** | **Fails**, as G6.1. By `:196`, the review feedback carries the review's VERDICT in PASS / CONDITIONAL_PASS / FAIL, so the feedback's outcome field is that verdict, while `:47` gives it other values. One review, two value sets, no mapping. |
| **Step fired** | **B (P1)**, on the same four-part test as G6.1, with `tech-lead:196` and `:29–30` for (b). Step D would reach the same place: `:29–30` is `tech-lead`'s own sentence placing the feedback format with skill `code-review` (self-placement, Q1), so `code-review` governs it, and E-G6b points there rather than copying. B fires first. |
| **Declared scope relied on** | `AGENTS.md` § Validation Gates; `tech-lead:29–30` (T572-quoted); `tech-lead:196` (present at T572's commit **(unverified)**; used as corroboration only). |
| **Amendment** | **E-G6b** (§7.5): the field takes the gate values, and a note points to skill `code-review` § Feedback Format for open points and open questions. |
| **Maturity** | Not relied on (`tech-lead` is `experimental`; irrelevant). |

**Observation (no amendment).** `code-review:98` "🟡 Should Fix … Request changes". Step A holds against P39: requested
changes on should-fix items are tracked follow-ups, which `CONDITIONAL_PASS` permits with the merge (`:128`, `:154`).
Nothing is amended.

## 4. G4 — the release-gate executor: **P5 escalation**

### 4.1 D5 record

| Field | Content |
|---|---|
| **Subject (D3)** | An actor: who executes the Release gate and issues its verdict, as recorded in `/prepare-release`'s `**Release manager**` field. |
| **Clauses** | `/prepare-release:3` `agent: "orchestrator"`; `:56` "- **Release manager**: orchestrator"; `:38` "7. **Produce a structured release gate VERDICT** in the release notes document from step 5". Against: `validation-gates:29` "\| **Release** \| Release Manager \| Before deployment \| All gates passed, docs complete, migration guides ready \|"; `:39` "**Executor:** <agent-name>"; `:124` "1. Identify the gate type and assign to the correct executor."; `:188` "Gate executors should not review their own work. Cross-agent review is mandatory."; `orchestrator.md:216–217` "**RELEASE GATE** (before deployment): - Delegate to `@release-manager`: "Verify release readiness. Produce VERDICT."". Related: `orchestrator.md:259` "2. Delegate to **@release-manager** for versioning, changelog, release preparation"; `release-manager:161` "Every release decision MUST conclude with a structured verdict:"; `release-workflow:135` "**Release Manager:** <agent-name>"; `:235` "The release manager is responsible for the full release workflow, including gate coordination." |
| **Step A** | **Fails.** One gate has one executor (`validation-gates:39` is single-valued; T572 F3). The command fixes the orchestrator; the skill's Gate Types and the orchestrator's own § Validation Gates name the Release Manager, which `orchestrator.md:217` resolves to the `@release-manager` agent. Separately, under the command the orchestrator prepares the release (steps 1–6) and then issues its verdict (step 7), against `validation-gates:188`. |
| **Step B** | **Does not fire.** No tier-1 text names a release-gate executor. `AGENTS.md:53` names review agents "(Tech Lead, QA, Security)" for a different rule. |
| **Step C** | **Does not decide.** P2(a) holds (the command names `validation-gates` at `:61, :69` and is executed by `orchestrator`). P2(b) fails: the subject is an executor, a non-output clause. ADR-008 P2: "If (b) fails because the subject is a non-output clause of the command, such as a process step or an executor, P2 does not apply. See P5." ADR-008 P5 cites this very item as its example. The field `**Release manager**` is output, but its value only records the executor; the dispute is the actor. |
| **Step D** | **Not applicable.** The parties are a command against a skill and an agent, not peers. The two peers (`validation-gates`, `orchestrator.md`) agree with each other. |
| **ADR-007** | Branch 1 does not fire: no `AGENTS.md` or stable-instruction text, and no same-file contradiction (`:61` defers to `release-manager` for risk acceptance, not for execution). Branches 2–5 govern contract against corpus and do not reach an executor. **The command can change only by user decision.** |
| **Step fired** | **E (P5).** Hold: no document is amended on the executor until the user decides (P5 § Form 3). E-R1 (G3.3) is held with it. |
| **Declared scope relied on** | None decides. `validation-gates:193` (Rails Inputs) takes "its designated executor agent" as an input; `/prepare-release:67` (Rails Inputs) says nothing about an executor. |
| **Maturity** | Not relied on (`/prepare-release` is `experimental`; `validation-gates` and `release-manager` are `stable`; irrelevant). |

### 4.2 User question Q-G4

**Subject.** Who executes the Release gate and issues the release verdict: the orchestrator (`/prepare-release`) or
the release-manager agent (`validation-gates`, `orchestrator.md`)?

**Quotes.** `/prepare-release:3` `agent: "orchestrator"` and `:56` "- **Release manager**: orchestrator";
`validation-gates:29` "\| **Release** \| Release Manager \| Before deployment \| …"; `validation-gates:188` "Gate
executors should not review their own work. Cross-agent review is mandatory."; `orchestrator.md:216–217` "Delegate to
`@release-manager`: "Verify release readiness. Produce VERDICT.""

**Why the steps did not decide it.** The two texts cannot both hold for one gate (Step A fails). No tier-1 text speaks
to it (B). The executor is not part of the command's declared output, so P2 does not apply (C), and ADR-008 P5 names
this item as its example. The parties are not peers, so self-placement cannot apply (D). ADR-007 cannot change the
command without a contradiction it recognises, so only you can.

**Options.**

| Option | What changes | Consequences |
|---|---|---|
| **1. The orchestrator runs `/prepare-release`; `@release-manager` issues the verdict (Recommended)** | Command: `:56` value becomes `release-manager`, and step 7 names `@release-manager` as the verdict's issuer, citing the skill and the orchestrator (exact text, C-G4a/C-G4b in §7.7). `docs/releases/_template.md:80` follows. `validation-gates`, `orchestrator.md` and `release-manager` are unchanged | Matches both peers with no skill or agent edit. Under the command, the preparer (orchestrator, steps 1–6) and the verdict's issuer differ, which satisfies `validation-gates:188`. **Golden:** no quote and no result change (`prepare-release-real-verdict-missing` checks only that `**Release manager**:` is present; its `brief.md` lists the field name, not the value). The hand-authored fixture of `prepare-release-conditional-pass-conditions-gap` (`release-notes.md:14`, "**Release manager**: orchestrator") goes stale in a field its `check()` never reads; refreshing it is optional and would need a protected-path grant and a user-authorized v18. Residual: `orchestrator.md:259` (Core Workflow) also delegates release *preparation* to `@release-manager`; on that path the release manager prepares and gates. That is observation O1 (§8), not decided here |
| **2. `@release-manager` runs `/prepare-release` and issues the verdict** | Command: `agent:` becomes `"release-manager"` and `:56` becomes `release-manager`. `docs/releases/_template.md:80` follows | Matches both peers and `orchestrator.md:259`. But one agent prepares (steps 1–6) and issues the verdict (step 7), so the conflict with `validation-gates:188` remains inside the command. Golden as option 1. The orchestrator's tag-cutting preflights (`orchestrator.md:127–146`) stay with the orchestrator |
| **3. The orchestrator executes the Release gate** | `/prepare-release` unchanged. `validation-gates:29` becomes Orchestrator and `orchestrator.md:216–217` stops delegating; `release-manager` § Release Gate VERDICT would need rewording | Edits a stable skill and an agent toward a command on a non-output subject, which no ADR-008 step licenses: it rests on your decision alone. The orchestrator both prepares and judges the release, directly against `validation-gates:188`. The non-golden test `test_validation_gates_skill_contract` asserts the Gate Types executor mapping (`conditional-pass-semantics-v4.md` §16.1) and would change. The frozen fixture copy of `validation-gates` in `validate-workflow-gate-verdict-sources` drifts further; its `check()` only matches the `**Release**` row, so its result is unchanged |
| **4. No change now; park until the first real release** | Nothing | The conflict stays. The first real release (ADR-007 Validation 5's exit for the release cases) would record "Release manager: orchestrator" while `orchestrator.md` delegates the gate to `@release-manager`: the ambiguity lands exactly when it matters |

**Recommendation: option 1.** It is the smallest change that makes all three documents agree, it alone meets
`validation-gates:188` inside the command, and it leaves every stable skill and agent untouched. It changes no golden
quote or result.

## 5. G5 — two release-notes paths: **Step A holds; the convention question joins P32**

| Field | Content |
|---|---|
| **Subject (D3)** | A path: where a release's release-notes document lives. |
| **Clauses** | `release-workflow:56` "5. **Create the release artifact** at `docs/artifacts/release-notes-v<VERSION>.md`."; `:160` "File location: `docs/artifacts/release-notes-v<VERSION>.md`"; `:233` "Keep release notes user-facing." Against: `/prepare-release:22` "5. Prepare release notes"; `:38–42` "… in the release notes document from step 5 (`docs/releases/v<version>.md`) as a top-level `## RELEASE VERDICT` section. That document is the block's home …"; `orchestrator.md:132–134` "verify that `docs/releases/vX.Y.Z.md` exists and is committed … Publish/update release notes from that file only: … Do not pass ad-hoc inline `--notes`; it can drift from `docs/releases/vX.Y.Z.md`". Corroboration, not knowledge: `scripts/verify-release-docs.py:24–25, :207–220` checks `docs/releases/<tag>.md` for `## RELEASE VERDICT`. |
| **Step A** | **Holds.** No clause says a release has exactly one release-notes document. `orchestrator.md:133`'s "only" governs the source of the *published* GitLab notes, which `release-workflow` does not contest (it says nothing about publishing). The two templates require different sections (`release-workflow:131–158`: Summary, Changelog, Migration Guide, Known Issues, Gate Verdicts, Rollback Plan; `docs/releases/_template.md` and `orchestrator.md:135`: Install, Highlights, `## RELEASE VERDICT`). Both files can be written. One-value: the release verdict appears in both (`release-workflow:154`; the command's `**Status**`) and is one value. |
| **Step fired** | **A.** No conflict, nothing ranked, no amendment. |
| **Why the residual joins P32** | What remains is duplication, not contradiction: two documents titled release notes per release, with overlapping changelog and verdict content that can drift (`orchestrator.md:134`'s own concern). Choosing one path would be a convention choice, binding a command (user decision under ADR-007), the orchestrator's preflight and CI tooling, and no ADR-008 step supplies it. That is P32's shape (`plan-092` §4: one artifact class named at different paths by a command, a skill and practice). Deciding it with the P32 family keeps one path convention for plans and release notes. **Proposed P32 extension:** add `release-workflow:56, :160` against `/prepare-release:38–42` and `orchestrator.md:132–134`; trigger as P32's, or the next task touching `/prepare-release` or `release-workflow`. |
| **Declared scope relied on** | None. |
| **Amendment** | **None.** A note stating the relationship is not possible without first deciding whether the two documents are one (the open question). |
| **Maturity** | Not relied on. |

## 6. G7 — `project-planning` against `AGENTS.md` § Task Protocol and § Lifecycle States

### 6.1 D5 record G7.1: the task entry and its Priority

| Field | Content |
|---|---|
| **Subject (D3)** | Two subjects, each a conflict (D3): (a) the form and fields of a task entry in `active-tasks.md`, including the Priority value set; (b) the actor who creates the entry. |
| **Clauses** | `project-planning:204` "When a plan is approved, the sprint backlog tasks MUST be decomposed into entries in `docs/tasks/active-tasks.md`."; `:208–219` "1. For each task in the approved sprint backlog, create an entry in `active-tasks.md`: … ### T{ID}: {Title} - **Status:** pending - **Assignee:** {role} - **Priority:** must \| should \| could - **Points:** {N} - **Sprint:** {sprint-name} - **Depends on:** … - **Artifact refs:** … - **Created:** {YYYY-MM-DD}". Tier 1: `AGENTS.md:14` "Task list: `docs/tasks/active-tasks.md` — columns: `ID \| Title \| Owner \| Status \| Priority \| Depends on \| Last update`"; `:17` "Task briefs: `docs/tasks/task-<ID>.md` (objective, inputs, outputs, acceptance criteria)"; `:18` "Only orchestrators create/transition tasks. Agents report completion and blockers."; `:19` "Sequential IDs: `T001`, `T002`, … Priorities: `P0` (critical path), `P1`, `P2`." |
| **Step A** | **(a) Fails.** `AGENTS.md:19` is a closed value set for a task's Priority; `must \| should \| could` shares no value with it, and one task has one Priority. `AGENTS.md:14` fixes the ledger's columns; a `### T{ID}` block is not a row of them. **(b) Fails** for any applier other than an orchestrator: the skill's step 1 tells whoever applies it to create the entry, and `AGENTS.md:18` says "Only". |
| **Step fired** | **B (P1)**, both subjects. (a) quotable as above; (b) `AGENTS.md` is repository-wide (D2), and the skill places its own decomposition in `active-tasks.md` (`:204`, T572-quoted as part of `:211–222`); (c) Step A fails; (d) a skill. This reproduces the T570 precedent (`poc-skills-alignment-v1.md` §4d, E13), which ADR-008 Validation 1 re-derives at Step B. |
| **Mapping MoSCoW to P0–P2: not taken** | T570 mapped `must_fix_pre_prod` → `P0` because that skill's own `:106` already said `P0`. Here no text anchors a mapping, and `AGENTS.md:19` defines `P0` as "(critical path)", a property of the dependency graph, not of MoSCoW: an ordinal Must → `P0` would mislabel a Must task off the critical path. The orchestrator sets the value (`orchestrator.md:62` "Set priority: P0 (critical path), P1 (important), P2 (nice-to-have)"). |
| **Not amended** | The sprint backlog table's `Priority` column (`:113–120`, "Must"/"Should"). It is a plan document's estimate with IDs `1`…`6`, not a task-list entry; `AGENTS.md:19` pairs Priorities with task IDs. Recorded counter-reading: if the orchestrator reads `:19` as governing every task priority anywhere, that table needs the same change. |
| **Declared scope relied on** | `AGENTS.md` § Task Protocol (repository-wide); `project-planning:204`. |
| **Amendment** | **E-G7a** (§7.6): the orchestrator creates a 7-column row and a brief; the Priority is `P0`/`P1`/`P2`; sprint, points and artifact references move to the brief. |
| **Maturity** | Not relied on (`project-planning` is `experimental`). |

### 6.2 D5 record G7.2: the task lifecycle

| Field | Content |
|---|---|
| **Subject (D3)** | A value set: the states a task takes. |
| **Clauses** | `project-planning:225–227` "**Task lifecycle:** - `pending` → `in-progress` → `review` → `done` (moved to `completed-tasks.md`) - `pending` → `blocked` (when a `[BLOCKER]` is raised) → `in-progress` (when blocker resolved)". Tier 1: `AGENTS.md:8–10` "## Lifecycle States … pending → in_progress → blocked → in_review → done \| cancelled"; `:15` "Terminal rows move to `docs/tasks/completed-tasks.md` … in the same edit." Peer, transitions: `task-management:95–106` (valid transitions; `blocked` only from `in_progress`) and `:121` "Validate the transition is allowed". |
| **Step A** | **States: fails.** `in-progress` and `review` are not in `AGENTS.md`'s closed state set, and one task's Status carries one value. **Transitions: holds.** `pending → blocked` is a permission; `task-management`'s closed table forbids it. A permission against a prohibition is jointly satisfiable by not taking the path (the P39 precedent for waivers, `conditional-pass-semantics-v4.md` §1.5). `AGENTS.md:10`'s arrow line is a list of states, not a transition relation (read literally it would forbid `blocked → in_progress`, which `task-management:102` allows), so tier 1 does not decide transitions. |
| **Step fired** | **B (P1)** for the state names. **A** for the transitions: a note pointing to `task-management`. |
| **Edit choice (P4(d))** | Two edits are valid: (i) rename the tokens only, keeping `pending → blocked`; (ii) cite tier 1 for the states and point to `task-management` for transitions, dropping the restated paths. (ii) is chosen on P1's remedy, "Prefer citing the tier-1 text to restating it", and because (i) would leave a permission next to a pointer to a table that forbids it. Neither choice rests on maturity. The pointer is not self-placement relied on to decide anything (Step A already holds), so the scope-gaming guard is not engaged. |
| **Declared scope relied on** | `AGENTS.md` § Lifecycle States and § Task Protocol (repository-wide). |
| **Amendment** | **E-G7b** (§7.6). |
| **Maturity** | Not relied on. |

### 6.3 The plan path (noted, not ruled)

`project-planning:163–168`: "Plan documents are versioned artifacts stored under `docs/plans/`: …
`docs/plans/project-plan-v1.md`". Against `orchestrator.md:23` "Write a plan document to `docs/plans/plan-<ID>.md`" and
P32's existing parties (`plan-092` §4). **Joins P32**, as the brief directs. Not ruled.

## 7. Exact amendments

Each Before is unique in its file (checked by reading the whole file; **unverified by grep**). Apply by text.

### 7.1 E-Q1: `implementation/knowledge/agents/qa-engineer.md:112–114` (G3.1; note, recommended)

**Anchor:** `## Validation Gate Protocol` (once).

````
Before:
## Validation Gate Protocol

1. Every QA run must end with a gate verdict:

After:
## Validation Gate Protocol

The QA gate is the `validation-gates` skill's **Integration** gate (§ Gate Types). Its verdict is recorded in that skill's `## Gate Verdict` block (§ Verdict Format), with `**Gate:** integration`. The gate verdict of item 1 and the `## VERDICT:` of § Structured Test Report accompany that block and do not replace it. All of them record the gate's one verdict, so they carry the same value.

1. Every QA run must end with a gate verdict:
````

### 7.2 E-S1: `implementation/knowledge/agents/security-engineer.md:164` (G3.2; note, recommended)

**Anchor:** the full line `Every security audit MUST conclude with a structured verdict:` (once).

````
Before:
Every security audit MUST conclude with a structured verdict:

After:
Every security audit MUST conclude with a structured verdict. This block accompanies, and does not replace, the `validation-gates` skill's `## Gate Verdict` block (§ Verdict Format) for the gate the audit is run for: `**Gate:** security` at the Security gate (that skill's § Gate Types), or `**Gate:** architecture` where the orchestrator delegates an architecture review to this agent (`orchestrator` agent § Validation Gates). When this agent runs `/security-audit`, the block also accompanies that command's `## VERDICT`, the command's declared output. The `**Status**` in the Summary of § Security Review Report Format, the gate verdict of § Security Gate Protocol, this block and those blocks record the audit's one verdict, so they carry the same value:
````

It changes no security criterion, grade, deadline or FAIL class; it states format relationships only.

### 7.3 E-R1: `implementation/knowledge/agents/release-manager.md:161` (G3.3; note, recommended; **held until Q-G4 is decided**)

**Anchor:** the full line `Every release decision MUST conclude with a structured verdict:` (once).

````
Before:
Every release decision MUST conclude with a structured verdict:

After:
Every release decision MUST conclude with a structured verdict. The release decision is the `validation-gates` skill's **Release** gate (§ Gate Types), so this block accompanies, and does not replace, that skill's `## Gate Verdict` block (§ Verdict Format), with `**Gate:** release`. When the release is prepared with `/prepare-release`, that command's `## RELEASE VERDICT` section in the release notes document (its step 7) is the gate's published rendering: this block does not replace it and is not a second `## RELEASE VERDICT` section in that document. All of them record the gate's one verdict, so they carry the same Status:
````

Valid as written under Q-G4 options 1 and 2. Under option 3 or 4 it must be re-ruled.

### 7.4 E-G6a: `implementation/knowledge/skills/code-review/SKILL.md:67–72` (G6.1; required)

**Anchor:** begins with `### 3. Feedback Format` (once).

````
Before:
### 3. Feedback Format

```markdown
## Review: [MR Title]

### Verdict: [Approved | Changes Requested | Needs Discussion]

After:
### 3. Feedback Format

The `### Verdict:` below is the review's one gate verdict (§ VERDICT Format for Validation Gates), so it takes one of the values `AGENTS.md` § Validation Gates allows, `PASS`, `CONDITIONAL_PASS` or `FAIL`, and the same value as the concluding `[VERDICT]` line. An open point that is a defect is a finding: grade it on § Severity Guide, and the verdict follows from the findings. A review that cannot conclude because a question stays open issues no verdict until the question is answered: the reviewer reports a blocker (`AGENTS.md` § Blocker Protocol) rather than fabricating a `PASS` (skill `validation-gates` § Rails, Failure mode), and no merge is approved without the verdict (§ Rails).

```markdown
## Review: [MR Title]

### Verdict: [PASS | CONDITIONAL_PASS | FAIL]
````

`:73–92` (the rest of the template) is unchanged.

### 7.5 E-G6b: `implementation/knowledge/agents/tech-lead.md:43–47` (G6.2; required)

**Anchor:** begins with `### Review Feedback Format` (once). In the source, `:44`'s fence follows the heading with no
blank line; the After adds blank lines around the new sentence.

````
Before:
### Review Feedback Format
```markdown
## Code Review: [Feature/MR Title]

### Status: [Approved | Changes Requested | Needs Discussion]

After:
### Review Feedback Format

The `### Status:` below is the review's verdict, in the values of `AGENTS.md` § Validation Gates, and carries the same value as the `## VERDICT:` of § Review Verdict Format. For an open point, and for a review that cannot conclude, follow skill `code-review` § Feedback Format.

```markdown
## Code Review: [Feature/MR Title]

### Status: [PASS | CONDITIONAL_PASS | FAIL]
````

`:48–64` and § Review Verdict Format (`:66–100`) are unchanged.

### 7.6 E-G7a and E-G7b: `implementation/knowledge/skills/project-planning/SKILL.md` (G7; required)

**E-G7a, `:208–219`.** Anchor: begins with `1. For each task in the approved sprint backlog, create an entry in` (once).

````
Before:
1. For each task in the approved sprint backlog, create an entry in `active-tasks.md`:
   ```markdown
   ### T{ID}: {Title}
   - **Status:** pending
   - **Assignee:** {role}
   - **Priority:** must | should | could
   - **Points:** {N}
   - **Sprint:** {sprint-name}
   - **Depends on:** [T{ID}, ...] or none
   - **Artifact refs:** [{artifact-version}, ...]
   - **Created:** {YYYY-MM-DD}
   ```

After:
1. For each task in the approved sprint backlog, the orchestrator creates the task (`AGENTS.md` § Task Protocol: "Only orchestrators create/transition tasks"). An agent other than an orchestrator that applies this skill proposes the tasks to the orchestrator and does not write the ledger. Each task gets:
   - a row in `active-tasks.md` with the columns `ID | Title | Owner | Status | Priority | Depends on | Last update`, Status `pending`, and a Priority of `P0`, `P1` or `P2` (`AGENTS.md` § Task Protocol), which the orchestrator sets. The sprint backlog's Must / Should / Could is not a value of that column;
   - a brief at `docs/tasks/task-<ID>.md` (objective, inputs, outputs, acceptance criteria), which also records the task's sprint, points and artifact references, for which the row has no column.
````

Steps 2–4 (`:221–223`) are unchanged.

**E-G7b, `:225–227`.** Anchor: begins with `**Task lifecycle:**` (once).

````
Before:
**Task lifecycle:**
- `pending` → `in-progress` → `review` → `done` (moved to `completed-tasks.md`)
- `pending` → `blocked` (when a `[BLOCKER]` is raised) → `in-progress` (when blocker resolved)

After:
**Task lifecycle:** a task's states are those of `AGENTS.md` § Lifecycle States: `pending`, `in_progress`, `blocked`, `in_review`, `done` and `cancelled`. Only an orchestrator transitions a task (`AGENTS.md` § Task Protocol). A task is set to `blocked` when a `[BLOCKER]` is raised, and back to `in_progress` when the blocker is resolved. A task that reaches `done` or `cancelled` is moved to `completed-tasks.md` in the same edit (`AGENTS.md` § Task Protocol). The allowed transitions, and the archive procedure, are those of skill `task-management` (§ Status Lifecycle, § Complete a Task).
````

### 7.7 C-G4a and C-G4b: `implementation/knowledge/commands/prepare-release.md` (**only if the user chooses Q-G4 option 1**)

These are command changes. They rest on the user's decision alone (the E-O1a precedent,
`security-grade-definitions-v2.md` §1), not on any ADR-007 branch or on a skill or agent.

**C-G4a, `:56`.** Anchor: the full line `- **Release manager**: orchestrator` (once).

````
Before:
- **Release manager**: orchestrator

After:
- **Release manager**: release-manager
````

**C-G4b, `:42`.** Anchor: the full line `   present when the tag is cut:` (three leading spaces; once).

````
Before:
   present when the tag is cut:

After:
   present when the tag is cut. The verdict is issued by `@release-manager`, the Release gate's
   executor (skill `validation-gates` § Gate Types; `orchestrator` agent § Validation Gates):
````

**Consequential, not knowledge:** `docs/releases/_template.md:80` `- **Release manager**: orchestrator` becomes
`- **Release manager**: release-manager`, so the template keeps carrying the command's slot (`/prepare-release:40`).
It is not a protected path.

Under option 2, C-G4a applies unchanged, and `:3` `agent: "orchestrator"` becomes `agent: "release-manager"` instead
of C-G4b. Under options 3 and 4, neither applies.

## 8. Constraints check, golden coupling and hit counts

### 8.1 Per-amendment statements

| Edit | Upward? (ADR-008 V4) | Relaxes a check? (ADR-007 §5) | Reopens an input? | Touches security criteria? | Golden: quote / fixture / result |
|---|---|---|---|---|---|
| E-Q1 | No (an agent) | No: adds a note | No | No | No open case (brief §2.4): none / none / none |
| E-S1 | No (an agent) | No | No (P40 S4, Q-O1 untouched) | **No**: format only. The orchestrator may still route it to the Security Engineer because the file is that role's own | None / none / none |
| E-R1 | No (an agent) | No | No (P39 R1–R3 untouched) | No | None / none / none |
| E-G6a | No (a skill, toward tier 1) | No: narrows the field to the closed set and adds no permission | No (N2 at `:131` untouched) | No | `code-review-conditional-pass-conditions-gap` and `code-review-fail-blocker-details`: their `brief.md` quotes only the command; their fixtures use `**Status**` and contain no `Approved`/`Changes Requested`; `check()` reads only the fixture. **No quote, fixture or result change** |
| E-G6b | No (an agent, toward tier 1) | No | No (A1–A3, C4 untouched) | No | No open case: none / none / none |
| E-G7a | No (a skill, toward tier 1) | No: the moved fields go to the brief; no check is removed | No | No | No open case: none / none / none |
| E-G7b | No | No: drops a permission (`pending → blocked`) that `task-management` forbids | No | No | None / none / none |
| C-G4a/b | **A command change by user decision only**; not made on the strength of a skill or agent | No: the field stays required and present | No (R4, R5 at `:61, :69` untouched) | No | `prepare-release-real-verdict-missing`: quote no change (lists field names), fixture no change, result no change (presence check). `prepare-release-conditional-pass-conditions-gap`: quote no change; fixture `release-notes.md:14` goes **stale** (not read); result no change. `prepare-release-changelog-grouping-compliant`: none. Optional fixture refresh needs a protected-path grant and a user-authorized v18 |

`orchestrator.md` is not amended by any recommended edit. `validate-workflow-gate-verdict-sources` (cited) reads only
its fixture copies of `validation-gates` and `/validate-workflow`; neither is amended. **No recommended edit needs a
protected-path grant or a baseline.**

### 8.2 Hit counts

Case-sensitive, fixed-string, per file, after all edits in that file. **Lines** = `grep -cF`; **occurrences** =
`grep -oF … | wc -l`. Before counts are at `f301cf6`, from reading **(unverified by grep)**. "must be 0" rows test that
old wording is gone.

| # | File | Phrase | Before (lines / occ.) | After (lines / occ.) | Edit |
|---|---|---|---|---|---|
| 1 | `agents/qa-engineer.md` | `validation-gates` | 0 / 0 | 1 / 1 | E-Q1 |
| 2 | same | `**Gate:** integration` | 0 / 0 | 1 / 1 | E-Q1 |
| 3 | same | `## VERDICT:` | 1 / 1 (`:163`) | 2 / 2 | E-Q1 |
| 4 | same | `## Validation Gate Protocol` | 1 / 1 | 1 / 1 | anchor survives |
| 5 | `agents/security-engineer.md` | `**Gate:**` | 0 / 0 | **1 / 2** | E-S1 (two on one line) |
| 6 | same | `/security-audit` | 2 / 2 (`:88`, `:156`) | 3 / 3 | E-S1 |
| 7 | same | `the audit's one verdict` | 0 / 0 | 1 / 1 | E-S1 |
| 8 | same | whole line `Every security audit MUST conclude with a structured verdict:` (`grep -cxF`) | 1 | **must be 0** | E-S1 |
| 9 | `agents/release-manager.md` | `**Gate:** release` | 0 / 0 | 1 / 1 | E-R1 |
| 10 | same | `RELEASE VERDICT` | 1 / 1 (`:164`) | **2 / 3** | E-R1 (two on one line) |
| 11 | same | `/prepare-release` | 0 / 0 | 1 / 1 | E-R1 |
| 12 | `skills/code-review/SKILL.md` | `Needs Discussion` | 1 / 1 | **must be 0** | E-G6a |
| 13 | same | `Changes Requested` | 1 / 1 | **must be 0** | E-G6a |
| 14 | same | `### Verdict: [PASS \| CONDITIONAL_PASS \| FAIL]` | 0 / 0 | 1 / 1 | E-G6a |
| 15 | same | `AGENTS.md` | 0 / 0 | **1 / 2** | E-G6a |
| 16 | same | `issues no verdict until the question is answered` | 0 / 0 | 1 / 1 | E-G6a |
| 17 | `agents/tech-lead.md` | `Needs Discussion` | 1 / 1 | **must be 0** | E-G6b |
| 18 | same | `### Status: [PASS \| CONDITIONAL_PASS \| FAIL]` | 0 / 0 | 1 / 1 | E-G6b |
| 19 | same | `AGENTS.md` | 1 / 2 (`:97`) | **2 / 3** | E-G6b |
| 20 | same | `§ Feedback Format` | 0 / 0 | 1 / 1 | E-G6b |
| 21 | `skills/project-planning/SKILL.md` | `must \| should \| could` | 1 / 1 | **must be 0** | E-G7a |
| 22 | same | `### T{ID}` | 1 / 1 | **must be 0** | E-G7a |
| 23 | same | `**Points:**` | 1 / 1 | **must be 0** | E-G7a |
| 24 | same | `ID \| Title \| Owner \| Status \| Priority \| Depends on \| Last update` | 0 / 0 | 1 / 1 | E-G7a |
| 25 | same | `Only orchestrators create/transition tasks` | 0 / 0 | 1 / 1 | E-G7a |
| 26 | same | `in-progress` | 2 / 2 | **must be 0** | E-G7b |
| 27 | same | `` `review` `` | 1 / 1 | **must be 0** | E-G7b |
| 28 | same | `in_progress` | 0 / 0 | **1 / 2** | E-G7b |
| 29 | same | `in_review` | 0 / 0 | 1 / 1 | E-G7b |
| 30 | same | `task-management` | 0 / 0 | 1 / 1 | E-G7b |
| 31 | same | `AGENTS.md` | 0 / 0 | **3 / 5** | E-G7a (2 lines, 2), E-G7b (1 line, 3) |
| 32 | `commands/prepare-release.md` (option 1 only) | `**Release manager**: orchestrator` | 1 / 1 | **must be 0** | C-G4a |
| 33 | same (option 1 only) | `release-manager` | 1 / 1 (`:61`) | 3 / 3 | C-G4a, C-G4b |
| 34 | same (option 1 only) | `@release-manager` | 0 / 0 | 1 / 1 | C-G4b |

Notes: rows 14, 18, 21 and 24 contain `|`, escaped as `\|` in this table only. Row 27's phrase includes its backticks.
Row 15 counts `AGENTS.md` twice on E-G6a's note line. Row 10's two new occurrences are on E-R1's line.

### 8.3 Mechanics (for the implementing task)

1. Apply each edit by its Before; each must match exactly once at dispatch.
2. Run `node implementation/scripts/sync.mjs --root implementation` and
   `python3 implementation/scripts/generate-registry.py`, each followed by `--check`.
3. Declare root drift exactly as `--print-drift` reports it: up to 5 files × 7 platforms without E-R1, 6 × 7 with it,
   plus `prepare-release.md` under option 1 or 2 **(unverified)**.
4. `scripts/scorecard.py --check` matches the current baseline; `check-maturity.py --root implementation` reports 0
   failing; `python3 docs/tasks/validate-tasks.py` passes.
5. Byte-unchanged: `AGENTS.md`, every instruction, `validation-gates`, `/code-review`, `/security-audit`,
   `orchestrator.md`, `tests/golden/**`, and `/prepare-release` unless the user chose option 1 or 2.

### 8.4 Observations (not ruled; candidates for parking)

- **O1: release self-review on the Core Workflow path.** `orchestrator.md:259` delegates release preparation to
  `@release-manager`, and `:217` delegates the Release gate to the same agent; `release-manager:15–27` lists both
  Preparation and Validation. Against `validation-gates:188`. Not in brief §1; it bears on every Q-G4 option.
- **O2: `scrum-master` and the Task Protocol.** `scrum-master:25` "Update task status in `active-tasks.md`" and `:27`
  "Ensure every task entry includes: ID, title, assignee, status, story points, sprint, and dependencies" have G7's
  shape against `AGENTS.md:14, :18`. Not in scope.
- **O3: `prepare-release-real-verdict-missing` artifact class.** Its `case.yaml:6–8` and `expect.py:55` read the
  verdict from a release checkpoint, while `/prepare-release:39–40` now says the block's home is "not the release
  checkpoint from step 6". That is ADR-007 branch 2's shape. A golden matter: flagged only.
- **O4: G9's pointer.** Since E7, `orchestrator.md:249` points to § Validation Gates, where `:205` reads "(after core
  implementation)". See G9 (§9).

## 9. G8 and G9: dispositions

**G8 (lowercase verdict tokens): confirmed "noted only".** Re-read at `f301cf6`: `qa-engineer:115, :116, :119, :200,
:220`; `security-engineer:155–157, :226`, and `:98` "[Pass \| Fail \| Conditional Pass]"; `release-manager:44–45`;
`/code-review:22, :25, :59`; `/validate-workflow:41, :74`. Under ADR-008 Step A, each variant denotes one member of
`AGENTS.md:52`'s set one-to-one, so one decision still carries one value. `AGENTS.md:52` lists the values; no sentence
of it says other case forms are not those values, so P1(a)'s quotability test is not met. `:98` adds a space as well as
case and is still unambiguous. An edit would have no authority behind it (`poc-skills-alignment-v1.md` §3).
Counter-reading recorded: a reader who takes the code-formatted tokens as exact strings would send this to Step B; if
the orchestrator prefers uniform tokens, it is a separate editorial task. Maturity not relied on.

**G9 (`orchestrator.md:205` timing): confirmed "noted only".** `:205` "**IMPLEMENTATION GATE** (after core
implementation):"; `:249` "3. After each completion, run the **Implementation Gate**: delegate to **@tech-lead** for
code review (see § Validation Gates)"; `validation-gates:26` "After code complete, before merge". This is a same-file
matter (ADR-008 § Scope, not covered), and Step A holds: `:205` does not say "once", and when core implementation is
complete the gate has run for every item. E7's pointer now sends readers from `:249` to `:205`, which makes the looser
wording more visible (O4), but it contradicts nothing. Maturity not relied on.

**Line shifts since T572** (T572 → `f301cf6`): `code-review:71` → `:72`; `qa-engineer:163–172` → `:163–173`;
`security-engineer:151` → `:155`, `:158–195` → `:162–199`; `/code-review:36–49` → `:34–49`; `/security-audit:50–64` →
`:50–66`; `prepare-release:56` unchanged; `project-planning:211–222` → `:208–219`, `:229` → `:226–227`, `:169–170` →
`:163–168`; `validation-gates:180` → `:188`, `:185` → `:193`.

## 10. Unverified claims (need a shell)

1. Every anchor's uniqueness and every Before count in §8.2 (by reading, not `grep`).
2. No non-golden test asserts the amended text: `Needs Discussion`, `Changes Requested`, `must | should | could`,
   `in-progress`, the three agents' anchor lines, `**Release manager**: orchestrator`. (`test_validation_gates_skill_contract`
   is reported to assert only tokens, markers and the executor mapping; I could not open it.)
3. No other file under `implementation/knowledge/` carries the `Approved | Changes Requested | Needs Discussion` set, a
   `### T{ID}` task block, or another statement of the release-gate executor. I checked only the files listed in §0.
4. `tech-lead:196` existed at T572's commit `24518f6` (used only as corroboration).
5. The root-drift path count.
6. What `audience: authoring` (`/prepare-release:6`) means for whether the command ships to target projects. It would
   affect only the context of G5's deferral, not its ruling.
7. The worktree commit `f301cf6`, as stated by the orchestrator.

## 11. Summary

| Item | Subject | Step fired | Outcome | Amendments | User decision? |
|---|---|---|---|---|---|
| G3.1 `qa-engineer` | Integration-gate verdict format | A | Jointly satisfiable; one value | E-Q1 (note, recommended) | No |
| G3.2 `security-engineer` (incl. `:98`) | Security-gate verdict format | A | Jointly satisfiable; one value | E-S1 (note, recommended) | No |
| G3.3 `release-manager` | Release-gate verdict format | A | Jointly satisfiable; one value | E-R1 (note, **held for Q-G4**) | Sequencing only |
| G3.4 `/code-review` | Implementation-gate verdict format | A | Jointly satisfiable; no basis to add to a command | none | No |
| G3.5 `/security-audit` | Security-gate verdict format | A | As G3.4 | none | No |
| G3.6 `release-workflow` | Summary of stored verdicts | A | Holds by construction | none | No |
| G4 | Release-gate executor | **E (P5)** | Escalated: Q-G4; recommendation option 1 | C-G4a/b only on option 1 | **Yes** |
| G5 | Release-notes path | A | No conflict; the convention question joins P32 | none | No (P32) |
| G6 `code-review` | `### Verdict:` value set; "Needs Discussion" | B (P1) | Gate values only; open defect → finding; open question → blocker, no verdict | E-G6a | No |
| G6 `tech-lead` | `### Status:` value set | B (P1); D agrees | Gate values; points to `code-review` | E-G6b | No |
| G7 task entry | Entry form, Priority, actor | B (P1) | 7-column row + brief; `P0`–`P2` set by the orchestrator | E-G7a | No |
| G7 lifecycle | State set; transitions | B (states), A (transitions) | `AGENTS.md` states; transitions per `task-management` | E-G7b | No |
| G7 plan path | Path | — | Joins P32 | none | No (P32) |
| G8 | Token case | A | Confirmed noted only | none | No |
| G9 | Gate timing wording | A (same file) | Confirmed noted only | none | No |

- **Maturity, corpus counts, majority practice and golden-coupling convenience** were relied on nowhere.
- **No upward and no relaxing edit.** No input artifact is reopened.
- **Golden:** no recommended edit changes a quote, a fixture or a result. Option 1 of Q-G4 leaves one fixture value
  stale in a field no check reads.
- **Blockers:** none. Q-G4 is a ruling outcome, not a blocker.
