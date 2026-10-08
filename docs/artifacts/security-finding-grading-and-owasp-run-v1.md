# Artifact: security-finding-grading-and-owasp-run-v1.md

> Filename: `security-finding-grading-and-owasp-run-v1.md`. Immutable once produced; revisions bump `<N>`.

## Metadata

- **Producer agent**: solution-architect
- **Task**: T588 (P2, judgment tier, decision only)
- **Created**: 2026-10-08
- **Based on:**
  - `docs/tasks/task-T588.md` (the brief, authoritative);
  - `docs/plans/plan-104-security-finding-grading-and-owasp-run.md`;
  - `docs/decisions/ADR-008-knowledge-document-authority.md` (Accepted), read in full: D1–D5, P1–P5, § Order of
    application, § Validation;
  - `docs/artifacts/security-review-security-gate-alignment-v1.md`, finding SEC-T586-07 (the origin of this task);
  - `docs/artifacts/security-gate-alignment-v2.md` (FU-6/FU-7, applied by T587) and
    `docs/artifacts/conditional-pass-semantics-v4.md` (P39). Both are inputs. Neither is reopened;
  - the user's instruction of 2026-10-08, verbatim: "Next item: continue as recommended" (the recommended item was
    SEC-T586-07), and the user's standing ADR-008 review decision Q1, **"Self-placement only"**.
- **Decision references**: ADR-008 Step A (P3a) for both subjects; ADR-008 § Decision ("Anything these rules do not
  decide is escalated, not chosen.") and P5 for both gap fills; ADR-007 §5 (never relax a check). No new ADR.

## 0. Method and limits

- **No shell.** I read every cited file in full in the worktree `agent-solution-architect-T588` (`develop` `51a4efb`).
  The orchestrator verified that its `implementation/` tree is identical to `7ec903a`, so every line number below is a
  line number at `7ec903a`. I re-read each quoted line for this artifact. Omissions inside a quote are marked "…".
- **Files read in full:** `security-guidelines.md`, `coding-standards.md`, `git-workflow.md`, `implementation/AGENTS.md`;
  skills `validation-gates`, `code-review`, `testing-strategy`, `ci-cd-pipeline`, `receiving-code-review`,
  `verification-before-completion`; agents `security-engineer`, `tech-lead`, `qa-engineer`, `orchestrator`,
  `release-manager`, `devops-engineer`, `backend-developer`, `poc-security-engineer`; commands `code-review`,
  `security-audit`, `new-feature`.
- **Not read** (so "no other document places the subject" is **(unverified)** for them): every other file under
  `implementation/knowledge/`.
- **Golden.** I read `tests/golden/open/validate-workflow-gate-verdict-sources/{case.yaml,brief.md,expect.py}`,
  `tests/golden/open/code-review-conditional-pass-conditions-gap/{brief.md,expect.py}` and
  `tests/golden/open/code-review-fail-blocker-details/{brief.md,expect.py}`. I did not open `tests/golden/held-out/`.
  I read no `.env*`, credential or key file.
- **Abbreviations:** `sg` = `instructions/security-guidelines.md`; `vg` = `skills/validation-gates/SKILL.md`;
  `cr` = `skills/code-review/SKILL.md`; `se` = `agents/security-engineer.md`; `tl` = `agents/tech-lead.md`;
  `/code-review` and `/security-audit` = the command files. All under `implementation/knowledge/`.
- **Encoding.** `§` is U+00A7 and `—` is U+2014. Each four-backtick fence holds one Before/After pair. No emoji.

## 1. Ruling in one paragraph

Neither subject is a contradiction. Both are **silence**. For each, Step A (P3a) fires: every clause that bears on the
subject can be obeyed together with every other, and no two clauses compute two values for one input. ADR-008 decides
conflicts. For a gap, the only amendment Step A licenses is a note that states a relationship the texts already contain
(ADR-008 P3a: "A ruling then amends at most to state the relationship where readers will see it"). Here, filling
either gap means **choosing** something no document's own text places: for (a), who grades a security finding that a
non-Security-Engineer executor raises, and by which definitions; for (b), who runs the per-MR OWASP checklist. Under
ADR-008 § Decision ("Anything these rules do not decide is escalated, not chosen.") and P5, both go to the user as
questions Q-a and Q-b (§4). Per P5 § Form 3 ("Hold the subject"), **no amendment is made now**. §5 gives exact
candidate texts for each option, so that the Security Engineer can review them and an implementing task can apply the
chosen ones verbatim.

## 2. D5 record for (a): grading a security finding raised by an executor other than the Security Engineer

### 2.1 Subject (D3)

**A criterion:** the definitions by which a `SECURITY:*` grade is assigned to a security finding that an executor other
than the Security Engineer raises (Tech Lead at the Architecture and Implementation gates, QA Engineer at the
Integration gate, Release Manager at the Release gate). Closely tied to it is an **actor** question: whether that
executor assigns the grade at all, or the Security Engineer does. D3 counts these as two subjects; both are treated
below and both reach the same outcome.

### 2.2 Clauses (verbatim, `7ec903a`)

| # | File:line | Text |
|---|---|---|
| a1 | `sg:181` (tier 1) | "2. Security Engineer flags findings as `SECURITY:CRITICAL`, `SECURITY:HIGH`, `SECURITY:MEDIUM`, or `SECURITY:LOW`" |
| a2 | `sg:182–184` (tier 1) | "3. `CRITICAL` and `HIGH` findings block merge until resolved" / "4. `MEDIUM` findings must have a remediation plan before merge" / "5. `LOW` findings are tracked as technical debt" |
| a3 | `vg:70` | "A security finding is any finding in the security category, whichever gate or executor raises it, graded on the `security-guidelines.md` § Security Review Workflow scale (`SECURITY:CRITICAL`/`HIGH`/`MEDIUM`/`LOW`); the Findings table records that grade as its Severity and `security` as its Category." |
| a4 | `vg:83` | "A security finding (§ Verdict Rules) takes the tier its grade names on the `security-guidelines.md` § Security Review Workflow scale: `SECURITY:CRITICAL` is `critical`, … `SECURITY:LOW` is `low`. What a security finding of each grade requires is stated in § Verdict Rules, and its tier never lowers that: …" |
| a5 | `vg:78` | "\| `critical` \| Broken functionality, security vulnerability, data loss risk. Blocks all progress. \|" |
| a6 | `se:77` | "All findings MUST be classified using these severity levels:" |
| a7 | `se:81–84` | "\| **CRITICAL** \| Actively exploitable, data breach risk, authentication bypass \| Must fix before release \|" / "\| **HIGH** \| Significant vulnerability, requires specific conditions to exploit \| Must fix before release \|" / "\| **MEDIUM** \| Moderate risk, defense-in-depth gap \| Fix within current sprint \|" / "\| **LOW** \| Minor issue, best-practice deviation \| Fix within next sprint \|" |
| a8 | `/security-audit:42–46` (command; `agent: "security-engineer"`, `:3`) | "9. Classify each finding with severity:" / "- **CRITICAL**: Actively exploitable, immediate remediation required" / "- **HIGH**: Exploitable with moderate effort; blocks merge until resolved (…)" / "- **MEDIUM**: Potential risk; requires a remediation plan (owner, fix, deadline) before merge" / "- **LOW**: Hardening recommendation, add to backlog" |
| a9 | `cr:130` | "Grade each finding on both scales, this skill's § Severity Guide and that skill's § Severity Definitions, and give the most restrictive verdict either requires." |
| a10 | `cr:96` | "\| 🔴 Must Fix \| Bug, security issue, data loss risk \| Block merge \|" |
| a11 | `tl:97` | "… A security finding graded `SECURITY:CRITICAL` or `SECURITY:HIGH` (`security-guidelines.md` § Security Review Workflow), whoever raised it, …" |
| a12 | `qa-engineer:59` | "### Severity: [Critical \| High \| Medium \| Low]" |

**Correction to the brief (§1(a)).** The brief says "The only definitions are in `security-engineer.md` § Findings
Classification (`:75–86`)". `/security-audit:42–46` (a8) is a second definition set, worded differently from a7. See
§6, C1 and O1.

### 2.3 Step A analysis (P3a)

1. **MUSTs.** a3 obliges a grade on the tier-1 scale for every security finding, "whichever gate or executor raises
   it". a6 obliges the Security Engineer to classify its findings with a7. a1 names the Security Engineer as the one
   who flags. a9 obliges the Tech Lead to grade on `cr`'s scale and on `vg`'s tiers.
2. **Exclusivity.** a1 has no "only", "instead of", "no other" or "replaces". It names the Security Engineer as
   flagger but does not forbid another executor from grading. a3 is passive ("graded"): it separates *raising* from
   *grading* and names no grader. a6 is an agent's instruction to its own executor. Its "All findings" is read in that
   agent's declared scope (D2 source 1, `se:3`: "Use when performing security audits, checking OWASP Top 10 compliance,
   …"). Nothing in a6 reaches a finding that a Tech Lead or QA Engineer raises (D2: "Quotable only").
3. **One-value test.** For a finding raised by a Tech Lead or a QA Engineer, **no clause supplies a definition set**:
   - a3 names the scale, a1–a2 name the grades and what they require, but nothing defines them;
   - a4 maps a grade to a tier ("takes the tier its grade names"), not a tier to a grade. Reading a5 backwards would
     make every "security vulnerability" `critical`. The T586 review already declined that reading: "FB1 lowers
     nothing. `:70` already records the tier-1 grade as the Severity" (`security-review-security-gate-alignment-v1.md`
     § Answers recorded). That is an input; it is not reopened here;
   - a10 and a12 are other scales (`cr`'s Must/Should/Nice; QA's bug severity). They do not define `SECURITY:*`. How
     `cr:96` combines with a security grade is P40 S2, parked (`conditional-pass-semantics-v4.md` §11 C4).

   With only one applicable clause (a3) and nothing that computes its value, no two clauses can produce two values for
   one input. The executor's grade is **undetermined, not contested**. That is silence.
4. **Specialisation (D4).** Not reached.

**Result:** Step A holds. **No contradiction.**

**Note on a7 against a8.** These are two definition sets that do apply to one executor, the Security Engineer, when it
runs `/security-audit`. They can compute two values for one input: a missing hardening header that is a
"defense-in-depth gap" is MEDIUM under a7 and, as a "Hardening recommendation", LOW under a8. That changes the verdict
(CONDITIONAL_PASS against PASS, `vg:66–67`). It is a different subject (the Security Engineer's own grading under a
command) and is outside SEC-T586-07. It is **not ruled here**; it is recorded as O1 (§6) because it bears on option
A1's consequences.

### 2.4 Steps B–D

- **Step B (P1)** fires only when Step A fails (P1 test (c)). It does not. For the record, the declared scope of tier 1
  does reach the subject:
  - `sg:2`: "Use when implementing authentication, authorization, input validation, cryptography, session management,
    or any security-sensitive code. Covers OWASP Top 10 prevention patterns, …";
  - `sg:3`: `applyTo: "**"`;
  - `sg:15–17` (Rails, Out of scope): "… see the Security Review Workflow for how OWASP findings feed into merge
    decisions."
- **Step C (P2).** No skill or agent is applied under a command on this subject. The non-SE executors' gates are not
  run through `/security-audit`. Under `/code-review` (`agent: "tech-lead"`, `:3`), the grade definitions are not part
  of the command's declared output: its VERDICT (`:38–49`) counts Must Fix, Should Fix and Nice to Have, not
  `SECURITY:*` grades. P2 does not apply.
- **Step D (P3b)** is reached only by a real contradiction between peers. There is none. Even if there were, no peer's
  own text places the grading of a non-SE executor's security finding with `se` § Findings Classification:
  - `vg` cites tier 1 for the scale (a3), and its Rails (`vg:192`) concede review content to the executor: "this skill
    defines the verdict process and format, not the review content itself";
  - `cr`, `tl:97`, `testing-strategy:240` and `release-manager:45` each cite `security-guidelines.md` § Security Review
    Workflow, never `se`;
  - `se:77` speaks to its own executor (above).

  Under the user's Q1 ("Self-placement only"), the Security Engineer's being the specialist, or its table's being the
  only full one in an agent, decides nothing.

### 2.5 Step that fired, and outcome

- **Step that fired: A (P3a).** Jointly satisfiable; no conflict, no rank.
- **Outcome: gap, escalated.** Step A's licence is a note that states an existing relationship. The texts contain two
  relationships: tier 1 names the Security Engineer as flagger (a1), and the Security Engineer classifies with a7 (a6).
  Neither says what a Tech Lead, QA Engineer or Release Manager does with a security finding it raises: grade it
  itself (and by which definitions), or refer it to the Security Engineer. Any sentence that says so chooses an
  answer. ADR-008 § Decision: "Anything these rules do not decide is escalated, not chosen." → **P5, question Q-a
  (§4.1).**

### 2.6 Remaining D5 fields

- **Declared scope relied on:** none for the outcome. Quoted for the P1 and P3 tests above: `sg:2`, `sg:3`, `sg:15–17`,
  `se:3`, `vg:192`.
- **Amendment:** **none now** (P5 § Form 3: "Until the conflict is decided, neither document is amended on the disputed
  subject."). Candidate texts per option: E-A1 (option A1); E-A2a and E-A2b (option A2). See §5.
- **Maturity:** not relied on. `vg` and `se` are `stable` and `tl` and `orchestrator` are `experimental`; none of this
  is a reason anywhere above (P4). Neither are corpus counts, majority practice or golden coupling.

## 3. D5 record for (b): the per-MR OWASP run

### 3.1 Subject (D3)

**An actor for a step:** who runs `sg:180` step 1, "Run OWASP Top 10 checklist against every merge request touching
security-sensitive code".

### 3.2 Clauses (verbatim, `7ec903a`)

| # | File:line | Text |
|---|---|---|
| b1 | `sg:180` (tier 1) | "1. Run OWASP Top 10 checklist against every merge request touching security-sensitive code" |
| b2 | `sg:181` (tier 1) | "2. Security Engineer flags findings as `SECURITY:CRITICAL`, `SECURITY:HIGH`, `SECURITY:MEDIUM`, or `SECURITY:LOW`" |
| b3 | `sg:164` (tier 1) | "Use this checklist during security reviews and audits:" |
| b4 | `AGENTS.md:81` (tier 1; `implementation/AGENTS.md`) | "- OWASP Top 10 compliance required." |
| b5 | `vg:17` | "- Before any release or deployment (security gate, release gate)" |
| b6 | `vg:28` | "\| **Security** \| Security Agent \| Before any release \| Vulnerabilities, auth flaws, data exposure, OWASP Top 10 \|" |
| b7 | `vg:15`, `vg:26`, `vg:183` | "- Before merging implementation work (implementation gate)"; "\| **Implementation** \| Tech Lead \| After code complete, before merge \| Code quality, test coverage, convention adherence \|"; "- Gates are non-negotiable checkpoints. Do not skip gates to save time." |
| b8 | `cr:34–39` | "#### Security (OWASP)" / "- [ ] Input validation on all user inputs" / "- [ ] No SQL/command/XSS injection vectors" / "- [ ] Authentication/authorization checks present" / "- [ ] Sensitive data not logged or exposed" / "- [ ] No hardcoded secrets or credentials" |
| b9 | `cr:3`, `cr:120` | "… Use when reviewing merge requests, pull requests, checking code quality, or performing peer review."; "Code review is the `validation-gates` skill's **Implementation** gate (§ Gate Types: Tech Lead, after code complete, before merge). …" |
| b10 | `/code-review:2`, `:3`, `:15`, `:17` | "Request a thorough code review of specified files or the current changes, following the code review skill checklist."; `agent: "tech-lead"`; "Review against:"; "2. Security (OWASP Top 10)" |
| b11 | `tl:29–30`, `tl:38` | "See skill `code-review` for the full structured checklist, feedback format, and VERDICT conventions this section summarizes."; "4. **Security**: Input validation, SQL injection, XSS, auth checks" |
| b12 | `orchestrator:205–206` | "**IMPLEMENTATION GATE** (after core implementation):" / "- Delegate to `@tech-lead`: "Review implementation against architecture-v1.md. Produce VERDICT."" |
| b13 | `orchestrator:213–214`, `:145` | "**SECURITY GATE** (before release):" / "- Delegate to `@security-engineer`: "Run OWASP Top 10 audit. Produce VERDICT.""; "- Security Gate must pass if security changes are in the release" |
| b14 | `se:18`, `se:222` | "Systematically review the codebase against the OWASP Top 10:"; "**Inputs**: The codebase, configuration, and infrastructure definitions under audit; the OWASP Top 10 checklist; prior findings and their remediation status." |
| b15 | `/security-audit:4`, `:15` | `argument-hint: "Specify scope: full project, specific feature, or files..."`; "1. OWASP Top 10 compliance check" |
| b16 | `testing-strategy:100` (inside the Test Plan Template fence) | "\| Security \| OWASP Top 10 \| Manual + SAST \| Security \|" |
| b17 | `ci-cd-pipeline:173`; `devops-engineer:23` | "\| **Security Scan** \| `security` \| No critical/high vulnerabilities \|"; "- security      # SAST, DAST, dependency scan" |
| b18 | `git-workflow:132`, `:200–201` | "- Tech Lead or Orchestrator reviews the worktree diff"; "- Require at least 1 approval" / "- All CI checks must pass" |

### 3.3 Step A analysis (P3a)

1. **MUSTs.** b1 requires a per-MR run for MRs touching security-sensitive code. It is passive and names no actor. b4
   requires compliance without naming an actor. b6 requires a Security gate before any release, executed by the
   Security Agent, with OWASP Top 10 in focus. b7 makes the Implementation gate (Tech Lead) mandatory before every
   merge, with no security item in its Focus cell.
2. **Exclusivity.** None of b5, b6, b13 or b14 says the OWASP checklist runs *only* before release, or *only* at the
   Security gate. b5 is a "When to Use" bullet; b6 sets a trigger for a gate, not for the checklist. Nothing fixes a
   closed set of points at which the checklist may run.
3. **One-value test.** The subject is an actor and a step, not a computed value. One schedule satisfies every clause:
   some executor runs the checklist on each MR touching security-sensitive code (b1), and the Security Engineer runs
   the Security gate before release (b6, b13). Nothing produces two values.
4. **Specialisation (D4).** b8 fills part of b1's slot at the Implementation gate (five checks, covering parts of
   A01/A07, A02, A03 and A09, with no citation of `sg`). b10 names "Security (OWASP Top 10)" for reviews requested
   through `/code-review`. b17 is an automated scan, not the checklist (A04, "Insecure Design", is not a scan result).
   Each is partial coverage; none competes with b1.

**Result:** Step A holds. **No contradiction.** The Security gate's "Before any release" trigger and the per-MR run
coexist. What is missing is an owner for b1.

### 3.4 Steps B–D, and why no text places the owner

- **Step B (P1)** does not fire: Step A holds. Tier-1 declared scope reaches the subject (`sg:2`, `sg:3`, `sg:15–17`, as
  in §2.4). **No upward amendment:** tier 1 says nothing about the actor, and `sg` is not amended (brief §2.3; ADR-008
  P1 Remedy).
- **Step C (P2)** does not apply. b10's "2. Security (OWASP Top 10)" is a review-checklist item of `/code-review`, a
  process step. P2 test (b): "If (b) fails because the subject is a non-output clause of the command, such as a process
  step or an executor, P2 does not apply." Also, `/code-review` is run on request (b10 `:2`). Nothing makes it the run
  for every MR, and b12 delegates the Implementation gate without naming the command.
- **Step D (P3b)** is not reached (no contradiction). As to placement, every candidate falls short of a sentence that
  assigns b1 to an actor:

  | Candidate | Why it does not place b1's owner |
  |---|---|
  | b2, "Security Engineer flags findings" | It names the *flagger* in step 2, not the runner of step 1. Reading the workflow as the Security Engineer's own is an inference from sequence, and D2 is "Quotable only" |
  | b3, "during security reviews and audits" | It says when the checklist is used, not by whom, and not per MR |
  | b6, b13, b14, b15 | They place a full OWASP audit with the Security Engineer **before release**, or on request. None says "every merge request" |
  | b8, b9, b11 | The Implementation gate runs before every merge and has a "Security (OWASP)" heading, but its five items are not the Top 10 and it does not cite `sg` § OWASP Top 10 Checklist Reference or step 1 |
  | b10 | It covers the Top 10 for reviews requested through the command. It is not stated to run per MR, and it is a command (brief §2.3: no command change) |
  | b16 | A row in a test-plan template (inside a code fence), not a sentence assigning step 1 |
  | b17, b18 | Automated scan and approval rules. Neither is the checklist |

  Under Q1, breadth or specificity decides nothing. "The Security Engineer is the specialist" and "the Tech Lead
  already reviews every MR" are both arguments of that kind.

### 3.5 Step that fired, and outcome

- **Step that fired: A (P3a).** Jointly satisfiable; no conflict, no rank.
- **Outcome: gap, escalated.** Assigning b1's owner is a choice that no document's own text makes. P5 → **question
  Q-b (§4.2).**
- **Which document must say so, and how** (answering brief §1(b)), conditional on the owner the user picks:
  - **Never `sg`, `AGENTS.md` or a command** (brief §2.3). The owner is stated in lower documents that cite `sg:180`.
  - **Not `vg` § Gate Types.** Editing `vg:28`'s trigger would change a gate's semantics and the pipeline order
    (`vg:146`). That is a design reason, and it is why no option proposes it. Golden coupling is not a reason (P4(e)).
  - **If the Tech Lead owns it:** skill `code-review` § Security (OWASP), which is the Implementation gate's review
    content. `vg:192` leaves review content to the executor's documents. Add a pointer in `tl:38`, which "summarizes"
    `code-review` (`tl:29–30`). That is E-B1a and E-B1b.
  - **If the Security Engineer owns it:** `orchestrator` § Validation Gates, where the gates' invocation points live
    (it delegates; agents "do not self-activate", `AGENTS.md:6`), plus a responsibility in `se`. That is E-B2a and
    E-B2b.
  - **No option needs a command change.** Under B1, `/code-review:17` already says "Security (OWASP Top 10)". Under B2,
    the Security Engineer may use `/security-audit` with a file scope as written (`:4`). Nothing is parked for a
    command.

### 3.6 Remaining D5 fields

- **Declared scope relied on:** none for the outcome. Quoted for the tests: `sg:2`, `sg:3`, `sg:15–17`, `cr:3`,
  `tl:29–30`, `vg:192`, `se:3`, `se:222`.
- **Amendment:** **none now** (P5 § Form 3). Candidate texts per option: E-B1a and E-B1b (option B1); E-B2a and E-B2b
  (option B2). See §5.
- **Maturity:** not relied on. Neither are corpus counts, majority practice or golden coupling.

## 4. Escalations to the user (P5)

**Routing (P5 § Form).** Both items carry the ADR's escalation content: type `unclear_requirements`, the subject, the
quotes and the step that failed to decide. Per the brief §5, each is a ruling outcome, not a task blocker. Both are
one-off questions, so they go to the user, as P36 did. They are coupled: see §4.3.

### 4.1 Q-a: How is a security finding graded when a Tech Lead, QA Engineer or Release Manager raises it?

**Subject.** `validation-gates` requires every security finding to be graded on the tier-1 scale, "whichever gate or
executor raises it" (`vg:70`). The scale's grades decide the verdict: CRITICAL/HIGH block merge, MEDIUM needs a plan,
LOW is debt (`sg:182–184`). Tier 1 names only the Security Engineer as flagger: "2. Security Engineer flags findings as
`SECURITY:CRITICAL`, …" (`sg:181`). The only definitions are in Security Engineer documents: `security-engineer.md`
§ Findings Classification (`se:77–84`) and, worded differently, `/security-audit:42–46`. Nothing tells the other
executors what to do.

**Why the rules did not decide it.** There is no contradiction (Step A, §2.3): with no definition set for those
executors, no two clauses compute two values. Stating that they use the Security Engineer's definitions, or that they
refer findings to the Security Engineer, would be a choice. No document's own text makes it (§2.4), and under your Q1
decision, "the Security Engineer is the specialist" is not a reason.

**Options.**

| Option | What changes | Who runs what | Workload | Consequences |
|---|---|---|---|---|
| **A1. Pointer (Recommended)** | One paragraph in `vg` § Severity Definitions (E-A1). Every executor grades with `se` § Findings Classification. A finding that fits more than one definition takes the highest grade it fits | Tech Lead, QA Engineer and Release Manager grade their own security findings. The Security Engineer is unchanged | None new | One definition set at every gate outside `/security-audit`. Tier 1's named flagger (`sg:181`) is not made literal; this does not contradict it, since `sg:181` has no "only". The under-grading risk from a non-specialist is bounded by three things: the highest-fit rule; the grade-independent FAIL classes (`vg:70`: constraint breach and omitted control "whatever its tier", `vg:83`); and the Security Engineer's own audit before release (`vg:28`). Residual: under `/security-audit`, `:42–46` may grade the same finding differently (O1) |
| **A2. Pointer plus Security Engineer confirmation** | A1's paragraph, plus: when another executor grades a security finding `SECURITY:MEDIUM` or `SECURITY:LOW`, the Security Engineer confirms the grade before the gate returns PASS or CONDITIONAL_PASS, and a higher grade from the Security Engineer applies (E-A2a). The orchestrator routes the confirmation (E-A2b) | As A1. The Security Engineer is also delegated a grade confirmation whenever another executor's gate raises a security finding graded MEDIUM or LOW | One extra Security Engineer delegation for each such gate run. That gate's verdict waits for it. CRITICAL/HIGH need no confirmation: they already block | Puts tier 1's flagger on every grade that would let a merge proceed. More latency at the Implementation and Integration gates. Same O1 residual |
| **A3. No change** | Nothing. SEC-T586-07(a) stays parked | As today | None | Each non-SE executor grades with no stated definitions, so the same finding can get different grades, and therefore different verdicts, at different gates |

*Considered and not offered:* "the Security Engineer grades every security finding any executor raises". A2 gives the
same protection where it matters at lower cost, because a CRITICAL or HIGH already blocks whoever grades it.

**Recommendation: A1.** It is the smallest change that gives every gate one definition set. The definitions it points
to belong to the agent tier 1 names as flagger. Every grade it can produce still yields at least what `vg` § Verdict
Rules already requires. Choose **A2** if you want the Security Engineer's judgement on every security finding that
would let a merge proceed, at the cost of an extra delegation per such gate run. Separately, O1 (§6) should be
scheduled whichever option you choose.

### 4.2 Q-b: Who runs the OWASP Top 10 checklist against every merge request that touches security-sensitive code?

**Subject.** Tier 1: "1. Run OWASP Top 10 checklist against every merge request touching security-sensitive code"
(`sg:180`). The step names no actor. The Security gate, which has OWASP Top 10 in its focus, triggers "Before any
release" (`vg:28`, `vg:17`). The orchestrator delegates "Run OWASP Top 10 audit" to the Security Engineer only at the
"SECURITY GATE (before release)" (`orchestrator:213–214`). The Implementation gate runs before every merge (`vg:26`,
`vg:183`). Its checklist has a "Security (OWASP)" section of five items (`cr:34–39`). The `/code-review` command lists
"2. Security (OWASP Top 10)" (`/code-review:17`), but that command runs on request.

**Why the rules did not decide it.** There is no contradiction (Step A, §3.3): a per-MR run and a pre-release gate can
both happen. No document's own text assigns step 1 to anyone (§3.4 table). Under your Q1 decision, "the Tech Lead
already reviews every MR" and "the Security Engineer is the specialist" are not reasons.

**Options.**

| Option | What changes | Who runs what | Workload | Consequences |
|---|---|---|---|---|
| **B1. Tech Lead, at the Implementation gate (Recommended)** | `cr` § Security (OWASP) gains a checklist item: for an MR touching security-sensitive code, run `sg` § OWASP Top 10 Checklist Reference against the change, all ten categories (E-B1a). `tl:38` points to it (E-B1b) | Tech Lead: the full checklist on each MR touching security-sensitive code, as part of the review it already does before merge. Security Engineer: unchanged, full audit before release | No new delegation. Each such review gets longer | Aligns the skill with what `/code-review:17` already says, with no command change. The per-MR merge block (`sg:182`) then rests on a generalist's run, with specialist review only before release. Together with A1, the Tech Lead both runs the checklist and grades; `sg:181` names the Security Engineer as flagger but does not say "only" |
| **B2. Security Engineer, per MR** | `orchestrator` § Validation Gates: at the Implementation gate, for an MR touching security-sensitive code, also delegate to `@security-engineer` to run the checklist; its findings are findings of that gate, and the verdict waits for them (E-B2a). `se` gains a "Per-Merge-Request Review" responsibility (E-B2b) | Security Engineer: the checklist on each such MR. Tech Lead: still issues the Implementation gate's one verdict, which includes the Security Engineer's findings. Orchestrator: decides that the MR touches security-sensitive code and delegates | One extra Security Engineer delegation per such MR, from the QA/Security token budget (`AGENTS.md` § Token Governance: "QA / Security / Release \| ≤ 60k tokens"). The merge waits for it | The most literal fit to tier 1, whose only named actor in the workflow is the Security Engineer (`sg:181`). Specialist review on every security-sensitive merge. For those MRs, the Security Engineer grades its own findings, so Q-a matters only for findings the Tech Lead or QA Engineer raise. The orchestrator's "touches security-sensitive code" call becomes a point of failure |
| **B3. No change** | Nothing. SEC-T586-07(b) stays parked | As today: partial coverage at the Implementation gate (five items), full audit before release | None | Tier-1 step 1 has no owner, and whether it is met cannot be checked |

*Considered and not offered:* making the Security gate itself per-MR by editing `vg:28`. That would change the gate
pipeline (`vg:146`: "Architecture Gate → Implementation Gate → Integration Gate → Security Gate → Release Gate").

**Recommendation: B1.** It assigns step 1 to the one executor that already reviews every MR before merge. It matches the
`/code-review` command's existing "Security (OWASP Top 10)". It needs two small edits and no new delegation, and the
Security Engineer's pre-release audit stays as the specialist check. **Disclosure:** B2 is the more literal reading of
tier 1 and the stronger control. If you prefer specialist review on every security-sensitive merge (in line with your
fail-safe choice in P39 Q8, "Yes, block"), choose B2.

### 4.3 How the two answers combine

| Q-b \ Q-a | A1 | A2 | A3 |
|---|---|---|---|
| **B1** | Recommended. The Tech Lead runs and grades with the Security Engineer's definitions | The Tech Lead runs; the Security Engineer confirms MEDIUM/LOW grades | The Tech Lead runs and grades without stated definitions |
| **B2** | The Security Engineer runs and grades per MR; others use its definitions | As B2+A1, plus confirmation of grades from the Tech Lead or QA Engineer | The Security Engineer grades its own findings; other executors have no stated definitions |
| **B3** | Definitions fixed; no per-MR owner | — | Status quo |

Every combination is valid on the texts. None relaxes a check, and none needs maturity to choose it (P4(d)).

## 5. Candidate amendments (held until the user answers; apply only those of the chosen options)

**Constraints met by every candidate.**
- **Not upward.** Every target is a skill or an agent: `vg`, `cr`, `tl`, `se`, `orchestrator`. No edit touches
  `security-guidelines.md`, `AGENTS.md`, any command, `tests/golden/**`, or `vg` § Gate Types.
- **Not relaxing.** Each candidate only adds an obligation, a check or a wait. None removes or lowers a requirement
  (ADR-007 §5). Detail is in the table in §5.3.
- **Inputs not reopened.** FB1 (`vg:83`) is used as an anchor and its text is kept byte for byte. P39 and FU-6/FU-7 are
  untouched.

**Which edits go with which option.**
- **A1:** E-A1.
- **A2:** E-A2a and E-A2b. E-A1 and E-A2a share an anchor, so apply one or the other, never both.
- **B1:** E-B1a and E-B1b.
- **B2:** E-B2a and E-B2b.
- **A3, B3:** none.

E-A2b and E-B2a both edit `orchestrator.md`, at different anchors, so both can be applied.

### 5.1 For Q-a

#### E-A1: `vg`, new paragraph after `:83` (option A1)

````
Before:
A security finding (§ Verdict Rules) takes the tier its grade names on the `security-guidelines.md` § Security Review Workflow scale: `SECURITY:CRITICAL` is `critical`, `SECURITY:HIGH` is `high`, `SECURITY:MEDIUM` is `medium` and `SECURITY:LOW` is `low`. What a security finding of each grade requires is stated in § Verdict Rules, and its tier never lowers that: a breach of an Immutable Security Constraint, or a security control that `security-guidelines.md` requires for the code under review and that is omitted, removed, disabled or weakened, yields FAIL whatever its tier; any other security finding graded medium needs its remediation plan before merge, and any other graded low is tracked as technical debt.

After:
A security finding (§ Verdict Rules) takes the tier its grade names on the `security-guidelines.md` § Security Review Workflow scale: `SECURITY:CRITICAL` is `critical`, `SECURITY:HIGH` is `high`, `SECURITY:MEDIUM` is `medium` and `SECURITY:LOW` is `low`. What a security finding of each grade requires is stated in § Verdict Rules, and its tier never lowers that: a breach of an Immutable Security Constraint, or a security control that `security-guidelines.md` requires for the code under review and that is omitted, removed, disabled or weakened, yields FAIL whatever its tier; any other security finding graded medium needs its remediation plan before merge, and any other graded low is tracked as technical debt.

Whichever gate or executor raises a security finding, it is graded with the definitions in agent `security-engineer` § Findings Classification, whose CRITICAL, HIGH, MEDIUM and LOW are `SECURITY:CRITICAL`, `SECURITY:HIGH`, `SECURITY:MEDIUM` and `SECURITY:LOW`. A finding that fits more than one definition takes the highest grade it fits. Those definitions decide the grade only; what each grade requires is stated in § Verdict Rules and in the paragraph above.
````

Citing an agent section from `vg` follows the file's own practice: `vg:67` and `vg:70` cite "`poc-orchestrator`
§ Security Findings". The paragraph names where the definitions are; it does not restate them, so `vg` still does not
define "the review content itself" (`vg:192`).

#### E-A2a: `vg`, new paragraph after `:83` (option A2; replaces E-A1)

````
Before:
A security finding (§ Verdict Rules) takes the tier its grade names on the `security-guidelines.md` § Security Review Workflow scale: `SECURITY:CRITICAL` is `critical`, `SECURITY:HIGH` is `high`, `SECURITY:MEDIUM` is `medium` and `SECURITY:LOW` is `low`. What a security finding of each grade requires is stated in § Verdict Rules, and its tier never lowers that: a breach of an Immutable Security Constraint, or a security control that `security-guidelines.md` requires for the code under review and that is omitted, removed, disabled or weakened, yields FAIL whatever its tier; any other security finding graded medium needs its remediation plan before merge, and any other graded low is tracked as technical debt.

After:
A security finding (§ Verdict Rules) takes the tier its grade names on the `security-guidelines.md` § Security Review Workflow scale: `SECURITY:CRITICAL` is `critical`, `SECURITY:HIGH` is `high`, `SECURITY:MEDIUM` is `medium` and `SECURITY:LOW` is `low`. What a security finding of each grade requires is stated in § Verdict Rules, and its tier never lowers that: a breach of an Immutable Security Constraint, or a security control that `security-guidelines.md` requires for the code under review and that is omitted, removed, disabled or weakened, yields FAIL whatever its tier; any other security finding graded medium needs its remediation plan before merge, and any other graded low is tracked as technical debt.

Whichever gate or executor raises a security finding, it is graded with the definitions in agent `security-engineer` § Findings Classification, whose CRITICAL, HIGH, MEDIUM and LOW are `SECURITY:CRITICAL`, `SECURITY:HIGH`, `SECURITY:MEDIUM` and `SECURITY:LOW`. A finding that fits more than one definition takes the highest grade it fits. Those definitions decide the grade only; what each grade requires is stated in § Verdict Rules and in the paragraph above. A security finding that an executor other than the Security Engineer grades `SECURITY:MEDIUM` or `SECURITY:LOW` is confirmed by the Security Engineer before the gate returns PASS or CONDITIONAL_PASS; if the Security Engineer grades it higher, the higher grade applies. Until it is confirmed, the gate lacks a required input (§ Rails, Failure mode). A finding graded `SECURITY:CRITICAL` or `SECURITY:HIGH` needs no confirmation to block.
````

#### E-A2b: `orchestrator.md`, new line after `:222` (option A2)

````
Before:
- `FAIL` → Create fix tasks, delegate fixes, re-invoke gate

After:
- `FAIL` → Create fix tasks, delegate fixes, re-invoke gate
- A gate executor other than `@security-engineer` asks for confirmation of a security finding's grade (skill `validation-gates` § Severity Definitions) → delegate the confirmation to `@security-engineer` before processing that gate's verdict
````

### 5.2 For Q-b

#### E-B1a: `cr`, new checklist item after `:39` (option B1)

````
Before:
- [ ] No hardcoded secrets or credentials

After:
- [ ] No hardcoded secrets or credentials
- [ ] For a merge request touching security-sensitive code: the `security-guidelines.md` § OWASP Top 10 Checklist Reference run against the change, all ten categories (A01 to A10), as that instruction's § Security Review Workflow step 1 requires; each security finding recorded with its grade (skill `validation-gates` § Verdict Rules)
````

#### E-B1b: `tl:38` (option B1)

````
Before:
4. **Security**: Input validation, SQL injection, XSS, auth checks

After:
4. **Security**: Input validation, SQL injection, XSS, auth checks; for a merge request touching security-sensitive code, the full OWASP Top 10 checklist (skill `code-review` § Security (OWASP); `security-guidelines.md` § Security Review Workflow, step 1)
````

#### E-B2a: `orchestrator.md`, new line after `:206` (option B2)

````
Before:
- Delegate to `@tech-lead`: "Review implementation against architecture-v1.md. Produce VERDICT."

After:
- Delegate to `@tech-lead`: "Review implementation against architecture-v1.md. Produce VERDICT."
- When the change touches security-sensitive code (`security-guidelines.md` § Security Review Workflow, step 1), also delegate to `@security-engineer`: "Run the OWASP Top 10 checklist against this merge request. Report each finding with its grade." Its findings are security findings of this gate (skill `validation-gates` § Verdict Rules), and the gate's verdict is not given until they are reported.
````

#### E-B2b: `se`, new subsection before `:75` (option B2)

````
Before:
## Findings Classification

After:
### Per-Merge-Request Review
For a merge request touching security-sensitive code, run the OWASP Top 10 checklist above against the change (`security-guidelines.md` § Security Review Workflow, step 1) and grade each finding as § Findings Classification requires. Report the findings to the Implementation gate, whose verdict includes them (skill `validation-gates` § Verdict Rules). This review does not replace the Security gate before release.

## Findings Classification
````

### 5.3 Per-edit statements

| Edit | Upward? | Relaxes a check? (ADR-007 §5) | Security effect |
|---|---|---|---|
| E-A1 | No (skill) | No. It adds a definition source and a highest-fit rule. Requirements per grade stay in § Verdict Rules | Removes the undefined-grade gap. The highest-fit rule biases toward stricter grades |
| E-A2a | No (skill) | No. It adds a confirmation wait. A Security Engineer grade can only raise the grade ("the higher grade applies") | As E-A1, plus specialist confirmation of every non-blocking grade from another executor |
| E-A2b | No (agent) | No. It adds a delegation | Routes E-A2a's confirmation, since agents do not self-activate (`AGENTS.md:6`) |
| E-B1a | No (skill) | No. It adds a checklist item | The full Top 10 per security-sensitive MR, where five items ran before |
| E-B1b | No (agent) | No. It adds a pointer | Keeps `tl`'s summary in line with `cr` (`tl:29–30`) |
| E-B2a | No (agent) | No. It adds a delegation and a wait before the verdict | Specialist checklist run per security-sensitive MR |
| E-B2b | No (agent) | No. It adds a responsibility and states that the Security gate stays | As E-B2a |

### 5.4 Golden coupling (each edit: quote / fixture / result)

| Edit | File | Open case(s) | Quote | Fixture | Result |
|---|---|---|---|---|---|
| E-A1, E-A2a | `vg` | `validate-workflow-gate-verdict-sources` | No change. `brief.md` quotes the command's steps 5–6, its Rails and template, and from `vg` only "Every gate MUST produce a verdict in this format" and the `**Gate:**` line (`brief.md:49–51`) | No change. The copy is frozen at `7be9926` (`brief.md:174–179`); FB1 and FD1 were applied later by T587, so it likely already lags the source **(unverified: no `cmp` run)** | No change. `check()` reads only the fixture. The new paragraph is in § Severity Definitions, a level-3 subsection inside `## Verdict Format`, which `_section(…, ("## Verdict Format",))` does read. But the paragraph contains neither "every gate must produce a verdict" nor a line starting `**Gate:**`, so it would not change the result even on a fresh copy. **§ Gate Types is not touched** |
| E-A2b, E-B2a | `orchestrator.md` | `validate-workflow-gate-verdict-sources` (cited: the command's step 5 names "the `orchestrator` agent's § Validation Gates") | No change. The section name stays; no `orchestrator` text is quoted | None. `T568` removed the `orchestrator.md` copy (`brief.md:181–185`) | No change. `check()` reads neither `orchestrator.md` nor its copy |
| E-B1a | `cr` | `code-review-conditional-pass-conditions-gap`, `code-review-fail-blocker-details` | No change. Both `brief.md` files quote only `commands/code-review.md` | No change. The fixtures are `fixture/review.md` only | No change. Each `check()` reads only `fixture/review.md` |
| E-B1b | `tl` | none (brief §2.5 table) | — | — | — |
| E-B2b | `se` | none (brief §2.5 table) | — | — | — |
| — | `commands/security-audit.md` | `security-audit-coverage-consistency`, `security-audit-critical-not-fail`, `security-audit-verdict-fields-compliant` | Not applicable: no candidate amends the command | — | — |

**§ Gate Types warning (brief §2.5).** No candidate edits `vg` § Gate Types, the table that
`validate-workflow-gate-verdict-sources` checks. If a later revision did edit it, the fixture is frozen, so the result
would not change, but the case's provenance would lag further. Golden coupling was not a reason for any ruling or
option (P4(e)).

### 5.5 Implementation checks (for the task that applies the chosen edits)

1. **Each Before matches once.** Before editing, `grep -cxF '<Before line>' <file>` must return **1**. I checked this
   only by reading each file in full **(unverified by grep)**:
   - E-A1 and E-A2a: `vg:83`;
   - E-A2b: `orchestrator:222`;
   - E-B1a: `cr:39`;
   - E-B1b: `tl:38`;
   - E-B2a: `orchestrator:206`;
   - E-B2b: `se:75`.
2. **After the edits:**
   - E-B1b's Before is replaced: `grep -cxF '4. **Security**: Input validation, SQL injection, XSS, auth checks'` →
     **0**.
   - Every other anchor line survives inside its After and still matches **1**. So for those, check the added text
     with the counts below, not the anchor.
3. **Regenerate.** Run `node implementation/scripts/sync.mjs --root implementation` and
   `python3 implementation/scripts/generate-registry.py`, each followed by `--check`. Declare root drift as
   `--print-drift` reports it (edited files × 7 platforms; **unverified**).
4. **Golden and maturity.** `scripts/scorecard.py --check` must match the current baseline. `check-maturity.py --root
   implementation` must report 0 failing. No protected-path grant is needed.

**Hit counts.** All counts are case-sensitive, fixed-string and per file, in the file named.
- **Lines** = `grep -cF` (lines containing the phrase).
- **Occurrences** = `grep -oF … | wc -l`.
- **Before** is the count at `7ec903a`, established by reading the whole file **(unverified by grep)**.
- No phrase below is a substring that any After text splits or negates. None of the edits removes text, so there is no
  "must be 0" row except E-B1b's whole-line check above.

| # | Phrase | File | Before | After: lines | After: occurrences | Edit |
|---|---|---|---|---|---|---|
| 1 | `it is graded with the definitions in agent` | `vg` | 0 | 1 | 1 | E-A1 or E-A2a |
| 2 | `§ Findings Classification` | `vg` | 0 | 1 | 1 | E-A1 or E-A2a |
| 3 | `takes the highest grade it fits` | `vg` | 0 | 1 | 1 | E-A1 or E-A2a |
| 4 | `Those definitions decide the grade only` | `vg` | 0 | 1 | 1 | E-A1 or E-A2a |
| 5 | `is confirmed by the Security Engineer before the gate returns PASS or CONDITIONAL_PASS` | `vg` | 0 | 1 under A2; 0 under A1 | 1 under A2; 0 under A1 | E-A2a |
| 6 | `asks for confirmation of a security finding's grade` | `orchestrator.md` | 0 | 1 | 1 | E-A2b |
| 7 | `OWASP Top 10 Checklist Reference` | `cr` | 0 | 1 | 1 | E-B1a |
| 8 | `all ten categories (A01 to A10)` | `cr` | 0 | 1 | 1 | E-B1a |
| 9 | `the full OWASP Top 10 checklist` | `tl` | 0 | 1 | 1 | E-B1b |
| 10 | `Run the OWASP Top 10 checklist against this merge request` | `orchestrator.md` | 0 | 1 | 1 | E-B2a |
| 11 | `Its findings are security findings of this gate` | `orchestrator.md` | 0 | 1 | 1 | E-B2a |
| 12 | `### Per-Merge-Request Review` | `se` | 0 | 1 | 1 | E-B2b |
| 13 | `This review does not replace the Security gate before release` | `se` | 0 | 1 | 1 | E-B2b |
| 14 | `§ Findings Classification` | `se` | 0 | 1 | 1 | E-B2b (`se:75`'s heading reads `## Findings Classification`, which does not contain `§`) |

Rows 1–4 count the same under A1 and A2, because E-A2a contains E-A1's paragraph unchanged. Rows 6, 10 and 11 are in
the same file but come from different edits; each counts 0 unless its own option is chosen.

## 6. Observations, corrections and parked items

- **O1 (new; not ruled): two Security Engineer definition sets.** `se:81–84` and `/security-audit:42–46` define the four
  grades differently, and can compute two values for one finding (§2.3 note). Under `/security-audit`, P2 would apply,
  since the classification is the command's declared output. The command cannot be amended on the strength of an agent
  (ADR-008 P2 Remedy). Any agent-side alignment must not lower a grade (ADR-007 §5). **Suggested:** a separate ruling
  task. It affects option A1's residual risk. Any command change it might suggest is parked here, because commands are
  out of scope (plan-104 §3: "No command is amended").
- **O2: the actor half of (a).** `sg:181` names the Security Engineer as flagger. Option A2 is the option that gives
  that actor a role for findings other executors raise. Recorded so the choice is visible; it is part of Q-a.
- **O3: automated coverage.** `ci-cd-pipeline:173` and `devops-engineer:23` give a per-pipeline SAST/dependency scan.
  It is not the OWASP checklist, and it is not offered as an owner for `sg:180`. It is unaffected by every option.
- **C1 (correction to the brief, `unclear_requirements`, `minor`):** brief §1(a) says the only definitions are in
  `security-engineer.md` § Findings Classification. `/security-audit:42–46` also defines them (O1).
- **C2 (note, `minor`):** brief §1(a) cites § Findings Classification as `:75–86`. Confirmed: heading `:75`, table
  `:79–84`, SLA paragraph `:86`. The definitions themselves are `:81–84`.

## 7. Summary

| Subject | Step fired | Contradiction? | Outcome | Escalation | Candidate edits (held) | Files |
|---|---|---|---|---|---|---|
| (a) Grading by a non-SE executor | **A** (P3a) | No: silence. No clause gives those executors a definition set, so no two values arise | Gap. Filling it chooses a grader and/or a definitions home that no document's own text places | **Q-a** (§4.1). Recommended: **A1** | A1: E-A1. A2: E-A2a + E-A2b | `vg`; and for A2 `orchestrator.md` |
| (b) Per-MR OWASP run | **A** (P3a) | No: silence. The pre-release Security gate and a per-MR run can both occur; nothing is exclusive | Gap. Assigning an owner for `sg:180` is a choice that no document's own text makes | **Q-b** (§4.2). Recommended: **B1** | B1: E-B1a + E-B1b. B2: E-B2a + E-B2b | B1: `cr`, `tl`. B2: `orchestrator.md`, `se` |

- **Amendments made now:** none (P5 § Form 3). The candidates are exact, not upward and not relaxing. None needs a
  command change, and none touches § Gate Types.
- **Maturity** was not relied on anywhere. Neither were corpus counts, majority practice or golden-coupling
  convenience.
- **Blockers:** none. The two P5 escalations are ruling outcomes (brief §5). C1 and C2 are brief corrections of
  severity `minor`.
- **Still unverified:**
  - the `grep` counts and anchors in §5.5;
  - that no file I did not read (§0) places either subject;
  - the root-drift count;
  - byte identity of `implementation/` with `7ec903a`, which the orchestrator verified and I did not.
