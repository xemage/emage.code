# Artifact: security-grade-definitions-v1.md

> Filename: `security-grade-definitions-v1.md`. Immutable once produced; revisions bump `<N>`.

## Metadata

- **Producer agent**: solution-architect
- **Task**: T590 (P2, judgment tier, decision only)
- **Created**: 2026-10-08
- **Based on:**
  - `docs/tasks/task-T590.md` (the brief, authoritative);
  - `docs/plans/plan-105-security-grade-definitions-o1.md`;
  - `docs/decisions/ADR-008-knowledge-document-authority.md` (Accepted), read in full, especially P2, P5, § Order of
    application and § Relationship to ADR-007;
  - `docs/decisions/ADR-007-command-contract-authority.md` (Accepted), read in full, especially branch 1 and §5;
  - `docs/artifacts/security-finding-grading-and-owasp-run-v1.md` (O1, §2.3 note and §6) and
    `docs/artifacts/security-finding-grading-and-owasp-run-v2.md` (E-A1, final text, §3; O1, §6);
  - `docs/artifacts/security-review-security-finding-grading-v1.md` (observations);
  - the user's decision of 2026-10-08, verbatim option label: O1, **"Rule it next (Recommended)"**; and the user's
    standing ADR-008 review decision Q1, **"Self-placement only"**.
- **Decision references**: ADR-008 Step A (P3a, one-value test) fails; Step B (P1) and ADR-007 branch 1 do not fire;
  Step C (P2) is met but its remedy is barred by ADR-007 §5; ADR-008 P5 (escalation, question Q-O1). No new ADR.

## 0. Method and limits

- **Commit.** Worktree `agent-solution-architect-T590`. Its `.git` file points to
  `.git/worktrees/agent-solution-architect-T590`, whose `HEAD` is `ref: refs/heads/agent/solution-architect/T590`, and
  that ref reads `40dc780541e04cef823b4e382d0476556e70973d`. Every line number below is at `40dc780`. I have no shell, so
  I could not confirm that the working tree is clean against that commit **(unverified: no `git status`)**.
- **Files read in full at `40dc780`:** `implementation/knowledge/agents/security-engineer.md`,
  `implementation/knowledge/commands/security-audit.md`, `implementation/knowledge/instructions/security-guidelines.md`,
  `implementation/knowledge/skills/validation-gates/SKILL.md`, `implementation/AGENTS.md`. Read in part:
  `implementation/knowledge/agents/orchestrator.md:195–229`.
- **Not read**, so "no other document places the subject" is **(unverified)** for them: every other file under
  `implementation/knowledge/`.
- **Golden.** I read, by path, `tests/golden/open/<case>/{case.yaml,brief.md,expect.py,fixture/audit.md}` for
  `security-audit-coverage-consistency`, `security-audit-critical-not-fail` and `security-audit-verdict-fields-compliant`.
  Two of the briefs above also name a sibling case that has no `tests/golden/open/` directory (its name is redacted
  here by the orchestrator, see O3). I never opened `tests/golden/held-out/`. I read no `.env*`, credential or key file.
- **E-A1.** T589 is applying it in parallel. It is **not** in this tree: `validation-gates/SKILL.md:83` (FB1) is followed
  directly by `:84` (blank) and `:85` `## Gate Input Requirements`. I use E-A1's final text from
  `security-finding-grading-and-owasp-run-v2.md` §3 (`:99`), quoted in §3 below.
- **Abbreviations:** `se` = `implementation/knowledge/agents/security-engineer.md`; `/security-audit` =
  `implementation/knowledge/commands/security-audit.md`; `sg` = `implementation/knowledge/instructions/security-guidelines.md`;
  `vg` = `implementation/knowledge/skills/validation-gates/SKILL.md`.
- **Encoding.** `§` is U+00A7 and `—` is U+2014. Quotes are verbatim; omissions are marked "…". Each four-backtick fence
  holds one Before/After pair. No emoji is introduced.

## 1. Ruling in one paragraph

The two definition sets **contradict** under `/security-audit`. Step A fails on the one-value test: both sets fix the
four-grade value of the same output field, the Severity of each finding the command reports, and they can give one
finding two grades. For a hardening gap that `sg` does not list as a required control, `se:83` gives MEDIUM ("defense-in-depth
gap") and `/security-audit:46` gives LOW ("Hardening recommendation"), so the verdict is CONDITIONAL_PASS under one and PASS
under the other (`/security-audit:67`). Step B does not fire: no tier-1 text defines the grades, and the command does not
contradict itself. Step C's test is met: the agent is applied under the command (`:3`) and severity is the command's
declared output (`:72`, "this command only produces findings, severity, and remediation recommendations"). But P2's
remedy, amending the agent to defer to the command, would **lower** grades (MEDIUM to LOW; CRITICAL to HIGH), which
ADR-007 §5 and the brief forbid. The agent cannot instead raise the command's grades, because P2 forbids an agent to
override the command's output. Step D does not apply, because a command is not a peer. So **no step decides it.
Escalated under P5 as question Q-O1 (§4).** Per P5 § Form 3, **no amendment is made now**. §5 gives exact candidate texts
for the recommended option, which is a command change and therefore a user decision only.

## 2. D5 record

### 2.1 Subject (D3)

**A value set:** the four-grade Severity value (CRITICAL, HIGH, MEDIUM, LOW) that `/security-audit` declares for each
finding, and what each value means, when the Security Engineer runs the command. The same value feeds the VERDICT counts
(`/security-audit:56–59`) and, through `:67`, the Status.

Outside `/security-audit` there is no second clause. There, `se` § Findings Classification applies alone (and, after
T589, through E-A1 for every executor). This record therefore concerns runs of the command only.

### 2.2 Clauses (verbatim, `40dc780`)

**Agent `se` § Findings Classification** (heading `:75`):

- `se:77`: "All findings MUST be classified using these severity levels:"
- `se:79`: "| Severity | Definition | SLA |"
- `se:81`: "| **CRITICAL** | Actively exploitable, data breach risk, authentication bypass | Must fix before release |"
- `se:82`: "| **HIGH** | Significant vulnerability, requires specific conditions to exploit | Must fix before release |"
- `se:83`: "| **MEDIUM** | Moderate risk, defense-in-depth gap | Fix within current sprint |"
- `se:84`: "| **LOW** | Minor issue, best-practice deviation | Fix within next sprint |"
- `se:86` (SLA paragraph, an input from FA1, not on this subject): "Each SLA is the latest point by which the fix is due. … A
  CRITICAL or HIGH finding blocks merge until it is resolved, whatever its SLA; …"

**Command `/security-audit` § Severity Classification** (heading `:40`):

- `:3`: `agent: "security-engineer"`
- `:42`: "9. Classify each finding with severity:"
- `:43`: "- **CRITICAL**: Actively exploitable, immediate remediation required"
- `:44`: "- **HIGH**: Exploitable with moderate effort; blocks merge until resolved (`security-guidelines.md` § Security Review
  Workflow)"
- `:45`: "- **MEDIUM**: Potential risk; requires a remediation plan (owner, fix, deadline) before merge"
- `:46`: "- **LOW**: Hardening recommendation, add to backlog"

**Other command clauses relied on below:**

- `:27`: "| # | OWASP Category | Status | Findings | Severity |" (the matrix carries a Severity column)
- `:56`–`:59`: "- **CRITICAL findings**: <count>" / "- **HIGH findings**: <count>" / "- **MEDIUM findings**: <count>" /
  "- **LOW findings**: <count>"
- `:66`: "Provide a structured security report with findings, severity levels, and remediation steps."
- `:67` (extract): "If any CRITICAL or HIGH finding exists, … the verdict MUST be FAIL … A required control missing only
  from code outside the change under review is graded at its own severity. … If any MEDIUM finding exists, the verdict is
  at best CONDITIONAL_PASS, with a remediation plan (owner, fix, deadline) listed as a condition for each MEDIUM finding.
  PASS requires no CRITICAL, HIGH or MEDIUM finding."
- `:72` (Rails, Out of scope): "Fixing any finding directly — this command only produces findings, severity, and
  remediation recommendations."

**Tier 1, checked for Step B:**

- `sg:57`: "- Set security headers:", with the fenced list at `sg:59`–`sg:63` (`Strict-Transport-Security`,
  `Content-Security-Policy`, `X-Content-Type-Options`, `X-Frame-Options`, `X-XSS-Protection`).
- `sg:181`–`sg:184`: "2. Security Engineer flags findings as `SECURITY:CRITICAL`, `SECURITY:HIGH`, `SECURITY:MEDIUM`, or
  `SECURITY:LOW`" / "3. `CRITICAL` and `HIGH` findings block merge until resolved" / "4. `MEDIUM` findings must have a
  remediation plan before merge" / "5. `LOW` findings are tracked as technical debt"
- `implementation/AGENTS.md:79`–`:84` (§ Security): "- See `knowledge/instructions/security-guidelines.md` and
  `SECURITY.md`." / "- OWASP Top 10 compliance required." / …

**Skill `vg`, bearing on the subject:**

- `vg:70` (extract): "A security finding is any finding in the security category, whichever gate or executor raises it,
  graded on the `security-guidelines.md` § Security Review Workflow scale … The same FAIL rule, with no waiver, holds for
  any security control `security-guidelines.md` requires for the code under review that is omitted, removed, disabled or
  weakened, tagged or not … With no change under review (for example a full-project `/security-audit`), the whole project
  is the code under review. A security finding graded medium yields at best CONDITIONAL_PASS: …"
- E-A1, after T589 (quoted in §3).

### 2.3 Step A (P3a)

1. **MUSTs.** `se:77` obliges the agent's executor to classify all findings "using these severity levels" (`se:81–84`).
   `/security-audit:42` obliges the command's executor, the same agent (`:3`), to "Classify each finding with severity"
   by `:43–46`. Under the command both bind one executor on one finding.
2. **Exclusivity.** Neither clause says "only", "instead of", "no other" or "replaces". But each fixes a closed value set
   for the same field, the Severity of each finding (`:27`, `:56–59`), and attaches a definition to each value. That is
   the closed-set form of exclusivity in P3a step 2. The labels are identical; the definitions differ.
3. **One-value test.** One finding carries one Severity in one audit. The two sets can compute different values for the
   same input:
   - **(i) Verdict changes.** A missing `Referrer-Policy` response header, on code under review. `sg:59–63` does not list
     that header, so the grade-independent FAIL rule for an omitted required control (`vg:70`, `se:154`,
     `/security-audit:67`) does not catch it. Under `se:83` it is a "defense-in-depth gap", so MEDIUM. Under
     `/security-audit:46` it is a "Hardening recommendation", so LOW. Then by `/security-audit:67` the verdict is at best
     CONDITIONAL_PASS under the first and PASS under the second.
   - **(ii) Count changes, verdict does not.** An authentication bypass that requires a specific configuration to be
     reachable. Under `se:81` it is an "authentication bypass", so CRITICAL (and, after E-A1, the highest grade it fits
     must be taken). Under `/security-audit:43–44` it is not "Actively exploitable", so it is HIGH ("Exploitable with
     moderate effort"). Both give FAIL, but the VERDICT's `CRITICAL findings` and `HIGH findings` fields (`:56–57`) carry
     different counts.

   **Counter-reading considered.** "Potential risk" (`:45`) is broad enough that the gap in (i) also fits the command's
   MEDIUM, so a single value (MEDIUM) could satisfy both sets. I do not take this as saving Step A. The test asks whether
   the clauses *can* compute different values for one input, not whether a careful executor could find an overlap.
   `:46` names this class of finding ("Hardening recommendation") for LOW, so an executor following the command can, and
   naturally would, give LOW. Neither text tells the executor to pick the overlap. ADR-008 § Risks makes the one-value
   test mandatory precisely so that "Both can be emitted" does not "hide a real criteria conflict". After E-A1, (ii) has
   no common value at all if the bypass is not "Actively exploitable": E-A1's highest-fit rule demands CRITICAL, and the
   command's CRITICAL does not fit.
4. **Specialisation (D4).** Not available. The command's values do not nest inside the agent's: a "Hardening
   recommendation" can be a "defense-in-depth gap", which `se` grades above LOW. Neither set fills a slot the other
   leaves open; both fill the same slot.

**Result: Step A fails. Contradiction.**

### 2.4 Step B (P1) and ADR-007 branch 1

Step B does not fire. P1 test (a) needs a quotable tier-1 sentence that one of the clauses contradicts.

- `sg:181–184` names the grades and says what each requires. It defines none of them. Both sets agree with what it
  requires: `/security-audit:44–46` restates the merge consequences, and `se:86` subordinates the SLAs to `sg` § Security
  Review Workflow. The subject here is the definitions, on which `sg` is silent.
- `sg:57–63` makes the listed headers required controls. Any grade-independent FAIL that follows from them applies under
  both sets alike (`vg:70`, `se:154`, `/security-audit:67`). It does not choose between the definitions.
- `implementation/AGENTS.md` § Security says nothing about grade definitions.
- **ADR-007 branch 1, same-file prong:** `/security-audit:42–46` does not contradict another clause of the command.
  `:67` reads the grades and does not define them. The command does not import `se`'s text. It names the agent only in
  `agent:` (`:3`) and in the `**Auditor**` value (`:62`), and P2 Remedy treats only "Text that a command imports by
  reference" as a command clause.

Declared scope of tier 1 on the subject, quoted for the record: `sg:2` "Use when implementing authentication,
authorization, input validation, cryptography, session management, or any security-sensitive code. Covers OWASP Top 10
prevention patterns, …"; `sg:3` `applyTo: "**"`; `sg:15–17` "… see the Security Review Workflow for how OWASP findings
feed into merge decisions." The scope reaches the subject. No tier-1 sentence decides it.

### 2.5 Step C (P2)

**The test is met.**

- **(a) Applied under.** `/security-audit:3`: `agent: "security-engineer"`. The command is "executed by it through its
  `agent:` frontmatter".
- **(b) Output contract.** Severity is something the command declares it produces:
  - `:72` (Rails): "this command only produces findings, severity, and remediation recommendations";
  - `:66`: "findings, severity levels, and remediation steps";
  - `:27`, the matrix's Severity column;
  - `:56–59`, the VERDICT counts.

  `:43–46` define the four values of that declared value set. P2(b) lists "value set". Reading the contract as covering
  only the four labels, and not what they mean, would make it protect only the arbitrary part. ADR-007 3a treats labels
  as "the arbitrary part".
- **(c)** Step A fails (§2.3).

**The remedy cannot be applied.**

- **P2's remedy lowers grades.** P2 Remedy: "Amend the skill or agent, not the command. Scope the amendment to "when run
  through `/<command>`". Under the command, the skill or agent then accompanies or defers to the contract". Here,
  deferring means grading with `:43–46` under the command. That lowers example (i) from MEDIUM to LOW, which removes the
  remediation-plan requirement (`sg:183`) and turns CONDITIONAL_PASS into PASS. It also lowers example (ii) from CRITICAL
  to HIGH. It would do so by choice of invocation path: the same finding graded at the Security gate through
  `orchestrator.md:214` ("Delegate to `@security-engineer`: "Run OWASP Top 10 audit. Produce VERDICT."", which names no
  command) would keep `se`'s grade, and after E-A1 so would every other executor. ADR-007 §5, "Never resolve by relaxing a
  check", applies "unchanged wherever an ADR-008 amendment touches a check" (ADR-008 § Relationship to ADR-007). The brief
  §1 also says "Any fix must never lower a grade." **Barred.**
- **The opposite agent-side fix overrides the command.** An agent-side rule "under `/security-audit`, the higher of the
  two grades applies" would give CRITICAL where the command's definitions admit only HIGH (example (ii)). P2: the agent
  "may specialise that output (D4), but it may not override it". **Barred.**
- **The command cannot be amended under P2.** P2 Remedy: "The command is never amended on the strength of a skill or
  agent." No ADR-007 branch fires either. Branch 1 fails (§2.4). Branches 2–4 concern contract against corpus, and there
  is no corpus: no real `/security-audit` output exists (`security-audit-critical-not-fail/brief.md:38`: "No real
  `/security-audit` output exists in this repo's history").

**Alternative reading of P2(b), and why the outcome does not depend on it.** One could read the definitions as a
criterion, and so as a non-output clause, since P2(b)'s list does not name "criterion". Then P2(b) fails, and ADR-008 P5
says so directly: "a non-output clause of a command against a skill or agent, which fails P2(b)". Both readings end at
P5.

**Step C does not decide.**

### 2.6 Step D (P3b)

Not applicable. Peers are "skills, agents and `experimental` instructions". A command is not a peer. For the record, no
self-placement text exists either way:

- `se`'s only mention of the command is `se:154`, "(for example a full-project `/security-audit`)". That sentence
  defines code under review. It does not assign grading.
- The command names the agent only as executor (`:3`) and as the `**Auditor**` value (`:62`).

Under Q1, "the Security Engineer is the specialist" decides nothing.

### 2.7 Step that fired, and outcome

- **Step that fired: E (P5).** A failed (contradiction). B did not fire. C's test is met but its only remedy lowers a
  grade (ADR-007 §5), and the alternative fix overrides the command (P2). D does not apply.
- **Outcome: escalated as Q-O1 (§4).** Type `unclear_requirements`. Per the brief §5, this is a ruling outcome, not a task
  blocker.

### 2.8 Declared-scope text relied on

- `se:3` (description): "Use when performing security audits, checking OWASP Top 10 compliance, reviewing authentication
  and authorization, scanning for vulnerabilities, assessing cryptographic implementations, reviewing input validation,
  checking for injection attacks, or hardening infrastructure." This brings `se` into play for `/security-audit` runs.
- `se:222` (Rails, Inputs): "The codebase, configuration, and infrastructure definitions under audit; the OWASP Top 10
  checklist; prior findings and their remediation status." `se:223` (Rails, Out of scope): "Applying fixes directly to
  production code, configuration, or infrastructure — …". Neither excludes grading under a command.
- `/security-audit:2` (description): "Request a security audit of the project or specific components, checking for OWASP
  Top 10 vulnerabilities."
- `/security-audit:71–72` (Rails): "**Inputs**: The scope to audit (`{{input}}`: full project, a feature, or specific
  files)." / "**Out of scope**: Fixing any finding directly — this command only produces findings, severity, and
  remediation recommendations." This is the P2(b) basis.
- Tier 1, for Step B: `sg:2`, `sg:3`, `sg:15–17` (§2.4).

### 2.9 Amendment

**None now** (ADR-008 P5 § Form 3: "Until the conflict is decided, neither document is amended on the disputed
subject."). Candidate texts E-O1a and E-O1b for option A are in §5. They are **held** and are **not settled**. E-O1a
amends a command, so it can be applied only on the user's decision.

### 2.10 Maturity

Not relied on. `se:6` and `/security-audit:5` both read `maturity: stable`, and that is a reason for nothing above (P4).
Neither are corpus counts (there is no corpus), majority practice, or golden coupling (P4(e)).

## 3. Interaction with E-A1 (T589)

**E-A1's final text** (`security-finding-grading-and-owasp-run-v2.md:99`, the new `vg` paragraph after `:83`):

> "Whichever gate or executor raises a security finding, it is graded with the definitions in agent `security-engineer`
> § Findings Classification, whose CRITICAL, HIGH, MEDIUM and LOW are `SECURITY:CRITICAL`, `SECURITY:HIGH`,
> `SECURITY:MEDIUM` and `SECURITY:LOW`. A finding that fits more than one definition takes the highest grade it fits.
> Those definitions decide the grade only; what each grade requires is stated in § Verdict Rules and in the paragraph
> above. No grade so given is lower than a minimum grade set elsewhere for that kind of finding (for example
> `poc-security-engineer` § Behavior, "Severity floor", or `poc-orchestrator` § Security Findings for a secret not yet
> committed). Nor does this paragraph lift an earlier deadline that the executor's own documents set (for the Security
> Engineer, the SLA paragraph of that section)."

1. **E-A1 does not decide O1.** v2 §6 says so: "Whether the set the Security Engineer uses under `/security-audit` is
   `se`'s or the command's is O1's question, and E-A1 does not answer it." This ruling does not change that.
2. **E-A1 adds a third party on the agent's side.** "Whichever gate or executor" reaches the Security Engineer under the
   command too, and `vg:70` itself contemplates "a full-project `/security-audit`". `vg` is not "applied under" the command
   in P2(a)'s sense: the command neither names, invokes nor imports it. So E-A1 against `/security-audit:42–46` is also
   undecided by Steps A–D. It is the **same subject**, so it joins Q-O1 rather than forming a second escalation.
3. **E-A1 sharpens the one-value test.** Its highest-fit rule removes the overlap inside `se`'s set. A hardening gap that
   is both a "defense-in-depth gap" and a "best-practice deviation" is MEDIUM, deterministically. The divergence from
   `/security-audit:46` therefore becomes certain, not just possible, once T589 lands.
4. **Residual under each option.**
   - Option A (§4) removes it. Under the command, the grade is the higher of the command's grade and `se`'s highest-fit
     grade. That is never lower than E-A1 gives. It is consistent with E-A1's floor sentence, which already admits a
     higher "minimum grade set elsewhere", and E-A1's pointer to `se` § Findings Classification picks up E-O1b, which sits
     inside that section.
   - Options B and C leave the residual v1 recorded for Q-a option A1: "under `/security-audit`, `:42–46` may grade the
     same finding differently".
5. **Sequencing.** E-O1a cites `vg` § Severity Definitions for the floor sentence that E-A1 adds. If the user chooses
   option A, its implementation must start after T589 has merged. The anchors of E-O1a and E-O1b lie in `/security-audit`
   and `se`, which T589 does not edit (plan-105 §2), so the anchors do not collide.

## 4. Escalation to the user (P5)

**P5 content.** Type: `unclear_requirements`. Subject: §2.1. Quotes: §2.2. Steps that failed to decide: §2.3–§2.6. Route:
a one-off question to the user, as P36 was. Option B below offers the general-rule route instead.

### Q-O1: When the Security Engineer runs `/security-audit`, which definitions decide a finding's grade?

**Subject.** The agent's table (`se:81–84`) and the command's step 9 (`/security-audit:43–46`) define CRITICAL, HIGH,
MEDIUM and LOW in different words. Under the command, both apply to the same finding, and they can disagree.

- A missing `Referrer-Policy` header is a "defense-in-depth gap" (MEDIUM, `se:83`) and a "Hardening recommendation" (LOW,
  `/security-audit:46`). The verdict is then CONDITIONAL_PASS with a remediation plan under the first, and PASS under the
  second (`/security-audit:67`).
- A headers gap that `security-guidelines.md` lists as required (`sg:57–63`) is not an example: in the code under review
  it yields FAIL under both sets.
- After T589, every other executor grades with the agent's table and takes the highest grade it fits (E-A1).

**Why the rules did not decide it.**

- The command's contract governs its own output (ADR-008 P2). But making the agent follow the command would **lower**
  grades, and no fix may do that (ADR-007 §5).
- Making the agent override the command is forbidden by the same P2.
- Only a command change can reconcile the two without lowering anything, and a command change is yours to make.

**Options.**

| Option | What changes | Consequences |
|---|---|---|
| **A. Higher of the two (Recommended)** | `/security-audit` step 9 keeps its four definitions byte for byte and gains one paragraph: each finding is also graded with `se` § Findings Classification (highest grade it fits there), the higher of the two grades applies, and no grade is below a floor set elsewhere (E-O1a). `se` § Findings Classification gains one sentence: under `/security-audit`, the command's step decides, and its grade is never lower than the agent's table gives (E-O1b). The Security Engineer reviews both texts first | **Nothing is lowered.** Under the command, a grade is at least what either set gives, so the hardening example is MEDIUM (CONDITIONAL_PASS), and the conditional bypass is CRITICAL. The conflict becomes jointly satisfiable. It agrees with E-A1 and with the "most restrictive" practice already in `code-review:130` and `vg:72`. **Costs:** a `stable`, user-facing command changes, so every downstream target project receives it (ADR-007 § Risks); expect more MEDIUM grades, and so more CONDITIONAL_PASS verdicts, than the command alone gives; and the command cites an agent section for the first time. Implementation waits for T589. **Golden:** no quote, fixture or result changes, and no grant is needed (§6) |
| **B. Decide it by a general rule (new ADR)** | Nothing now. A new ADR would state when an agent's or skill's grading criteria may raise a command's output value, for example "when two criteria sets grade one output, the stricter governs". This is P5 § Form 2, "A question that needs a general rule goes to an ADR" | It decides this and future cases of the same shape the same way. It would add a way to modify a command's output that ADR-007 branch 1 and ADR-008 P2 do not have today, so it needs its own drafting, review and acceptance. The O1 residual remains until then. Slowest option |
| **C. No change (park with a trigger)** | Nothing. O1 is parked, with a trigger: the first real `/security-audit` output, or the next change to either text | Under `/security-audit`, one finding can still get two grades and two verdicts. After T589, the Security Engineer under the command is the only executor without one definition set. Q-a's A1 residual stays open. No document is changed |

*Considered and not offered.* Each of these lowers a grade or overrides the command:

1. **The agent defers to the command (P2's usual remedy).** It lowers MEDIUM to LOW and CRITICAL to HIGH (§2.5).
2. **The command's step 9 is replaced by a pointer to `se` alone.** That can also lower a grade. An account-enumeration
   timing difference is "Exploitable with moderate effort" (HIGH, `:44`) but may be only "Moderate risk" (MEDIUM, `se:83`),
   which turns FAIL into CONDITIONAL_PASS.
3. **An agent-side "higher of the two" rule without a command change.** It overrides the command's output, which P2
   forbids (§2.5).
4. **Rewording both tables into one merged set.** It makes two copies that can drift (ADR-008 P3b Remedy: "Do not copy
   the governing text"). Its effect is option A's.

**Recommendation: A.** It is the only option that removes the conflict now without lowering any grade. It keeps the
command's own text and adds a single upward-only rule. It agrees with what the user already chose for every other
executor (Q-a, "Pointer (Recommended)"), and with the "highest grade it fits" rule the Security Engineer's review found
"monotone and fail-strict" (`security-review-security-finding-grading-v1.md` § Answers recorded). Choose **B** if you want
cases of this shape settled by a standing rule rather than one at a time. Choose **C** only if you accept two grades
under the command until real audit output exists.

**Every option is valid without reference to maturity (P4(d)).** None relaxes a check.

## 5. Candidate amendments (held; option A only; never settled until the user decides)

**Authority, if chosen.** The user's decision on Q-O1 (ADR-008 § Scope: "A question already settled by … a recorded user
decision. That decision governs, and documents are amended to it."). No ADR-007 branch licenses E-O1a (§2.5), so the
user's decision is its only basis. **E-O1a is not made on the strength of the agent** (ADR-008 Validation 4). E-O1b is
P2's remedy shape (the agent, scoped to the command), which becomes lawful only once E-O1a removes the lowering. **Apply
both or neither.** Before applying either, a Security Engineer reviews them (brief §1).

### E-O1a: `implementation/knowledge/commands/security-audit.md`, new paragraph in step 9 after `:46`

Anchor: the full line `:46`, including its three leading spaces. Inside this file, the text `Hardening recommendation`
occurs on that line only (1 line, 1 occurrence).

````
Before:
   - **LOW**: Hardening recommendation, add to backlog

After:
   - **LOW**: Hardening recommendation, add to backlog

   Grade each finding also with the definitions in agent `security-engineer` § Findings Classification, taking the highest grade it fits there. Where that grade differs from the one the definitions above give, the higher of the two applies. No grade so given is lower than a minimum grade set elsewhere for that kind of finding (skill `validation-gates` § Severity Definitions).
````

The new paragraph is indented three spaces and follows a blank line, so it continues list item 9 rather than adding a
fifth grade. The existing blank line `:47` and `## Verdict Output` (`:48`) follow it unchanged.

### E-O1b: `implementation/knowledge/agents/security-engineer.md`, new paragraph at the end of § Findings Classification

Anchor: the full line `:88`, `## Security Review Report Format` (1 line, 1 occurrence in the file). The new paragraph
goes before it, after `se:86` and the blank line `:87`, so it stays inside § Findings Classification. That is where
E-A1's pointer leads.

````
Before:
## Security Review Report Format

After:
When this agent runs `/security-audit`, that command's § Severity Classification decides each finding's grade: it grades with these definitions as well as its own, and the higher grade applies, so the grade is never lower than this section gives.

## Security Review Report Format
````

### 5.1 Per-edit statements

| Edit | Upward? | Lowers a grade or relaxes a check? (ADR-007 §5) | Command change without a user decision? |
|---|---|---|---|
| E-O1a | It changes a command. Its basis is the user's decision, not the agent (ADR-008 Validation 4) | No. It keeps `:43–46` byte for byte and adds a max with a second set plus a floor. Every grade after it is at least every grade before it, under either set | It is held until the user chooses A |
| E-O1b | No. It amends an agent, scoped to the command (P2 Remedy) | No. It states that the grade is "never lower than this section gives" | Not a command edit. It is valid only with E-O1a |

### 5.2 Implementation checks (for the task that applies option A, after T589 merges)

1. **Each Before matches once.** Before editing, `grep -cxF` on each Before line must return 1:
   - E-O1a: `'   - **LOW**: Hardening recommendation, add to backlog'` in `security-audit.md`;
   - E-O1b: `'## Security Review Report Format'` in `security-engineer.md`.

   This is from reading, **(unverified by grep)**. After editing, both anchors survive in their After texts and still
   return 1.
2. **Regenerate.**
   - Run `node implementation/scripts/sync.mjs --root implementation` and
     `python3 implementation/scripts/generate-registry.py`, each followed by `--check`.
   - Declare the root drift as `--print-drift` reports it. Expect up to 2 files × 7 platforms **(unverified)**.
3. **Golden and maturity.**
   - `scripts/scorecard.py --check` must match the current baseline.
   - `check-maturity.py --root implementation` must report 0 failing.
   - No protected-path grant is needed (§6).

## 6. Golden coupling

`/security-audit` is cited by the three open cases below. `se` is cited by none of them; the `**Auditor**:
security-engineer` lines in their fixtures are field values, not citations. That no other open case cites `se` is from
the brief §2.3 and is **(unverified)** by me.

| Case (`tests/golden/open/…`) | Status | What it quotes from the command | Quote change under E-O1a | Fixture change | Result change |
|---|---|---|---|---|---|
| `security-audit-coverage-consistency` | `expected_pass` (`case.yaml:3`) | § "Verdict Output", `OWASP coverage: <n>/10 categories assessed` (`brief.md:11–12`), and § "Audit Scope" (`brief.md:13`) | None. E-O1a does not touch `:13–21` or `:48–64` | None | None. `check()` compares only `**OWASP coverage**` with the A01–A10 rows (`expect.py:24–33`) |
| `security-audit-critical-not-fail` | `known_failing`, `capability_gap` (`case.yaml:3–4`) | The verdict rule, "If any CRITICAL or HIGH finding exists, … the verdict MUST be FAIL" (`case.yaml:6–7`, `brief.md:13–14`, `expect.py:4–5`) | None. E-O1a does not touch `:67`. A higher grade can only make that rule fire more often | None | None. `check()` reads `**CRITICAL findings**` and `**Status**` from the fixture (`expect.py:31–41`). It stays False |
| `security-audit-verdict-fields-compliant` | `expected_pass` (`case.yaml:3`) | § "Verdict Output" field formats (`brief.md:10–16`) | None | None | None. `check()` reads matrix rows and VERDICT field formats only (`expect.py:36–66`) |

- **E-O1b:** no case cites `se`, so there is no quote, fixture or result to change.
- **Options B and C:** no edit, so there is no change.
- **Grants.** No option needs a protected-path grant or an evaluator-hash baseline. If a later revision of E-O1a touched
  `/security-audit:67` or § Verdict Output, the quotes listed above would change. That would need a protected-path grant
  and a user-authorized evaluator-hash baseline.
- **Observation, not a reason (P4(e)).** `security-audit-coverage-consistency/fixture/audit.md:10` grades "password reset
  token has short TTL margin" LOW with `Status: PASS`. Under option A, an auditor might grade it MEDIUM if they read it as
  a "defense-in-depth gap". No `check()` reads a grade, so no result changes, and the fixture is frozen and hand-authored.
  That grade is a judgment **(unverified)**.

## 7. Hit counts

All counts are case-sensitive, fixed-string and per file, in the file named.

- **Lines** means `grep -cF` (the lines that contain the phrase).
- **Occurrences** means `grep -oF … | wc -l`.
- **Before** is the count at `40dc780`, from reading each whole file **(unverified by grep)**.
- **After** applies only if the user chooses option A.
- No phrase below is split by an After text. Each After phrase is contiguous on one line.
- No edit removes text, so there is no row whose count must fall to 0.

| # | Phrase | File | Before: lines / occ. | After: lines / occ. | Edit |
|---|---|---|---|---|---|
| 1 | `Hardening recommendation` | `security-audit.md` | 1 / 1 (`:46`) | 1 / 1 | anchor, survives |
| 2 | `§ Findings Classification` | `security-audit.md` | 0 / 0 | 1 / 1 | E-O1a |
| 3 | `security-engineer` | `security-audit.md` | 2 / 2 (`:3`, `:62`) | 3 / 3 | E-O1a adds one |
| 4 | `taking the highest grade it fits there` | `security-audit.md` | 0 / 0 | 1 / 1 | E-O1a |
| 5 | `the higher of the two applies` | `security-audit.md` | 0 / 0 | 1 / 1 | E-O1a |
| 6 | `minimum grade set elsewhere` | `security-audit.md` | 0 / 0 | 1 / 1 | E-O1a |
| 7 | `validation-gates` | `security-audit.md` | 0 / 0 | 1 / 1 | E-O1a |
| 8 | `§ Severity Definitions` | `security-audit.md` | 0 / 0 | 1 / 1 | E-O1a |
| 9 | `## Security Review Report Format` | `security-engineer.md` | 1 / 1 (`:88`) | 1 / 1 | anchor, survives |
| 10 | `/security-audit` | `security-engineer.md` | 1 / 1 (`:154`) | 2 / 2 | E-O1b adds one |
| 11 | `§ Severity Classification` | `security-engineer.md` | 0 / 0 | 1 / 1 | E-O1b |
| 12 | `never lower than this section gives` | `security-engineer.md` | 0 / 0 | 1 / 1 | E-O1b |
| 13 | `defense-in-depth gap` | `security-engineer.md` | 1 / 1 (`:83`) | 1 / 1 | unchanged (clause quote) |
| 14 | `All findings MUST be classified` | `security-engineer.md` | 1 / 1 (`:77`) | 1 / 1 | unchanged (clause quote) |
| 15 | `Potential risk` | `security-audit.md` | 1 / 1 (`:45`) | 1 / 1 | unchanged (clause quote) |

**Notes on the counts:**

- **`§`.** Rows 2, 8 and 11 contain `§` (U+00A7). Use a UTF-8 locale.
- **Row 2 against the heading.** `se:75` reads `## Findings Classification` without `§`, so it is not counted in `se`.
  Row 2 counts `security-audit.md` only.
- **Row 11 against the heading.** `/security-audit:40` reads `## Severity Classification` without `§`, so it is not
  counted there. Row 11 counts `security-engineer.md` only.

## 8. Observations and corrections

- **C1. The brief's example needs narrowing** (`unclear_requirements`, `minor`). The brief §1 and plan-105 §1 use "a
  missing hardening header". For a header that `sg:57–63` lists, missing from code under review, both sets give FAIL
  whatever the grade (`vg:70`, `se:154`, `/security-audit:67`). In a full-project audit the whole project is code under
  review. The example holds for a header that `sg` does not list, or for a listed header missing only from code outside
  the change under review ("graded at its own severity", `:67`). §2.3 uses `Referrer-Policy`. The ruling does not change.
- **O2. Each set overlaps internally.**
  - `se`: "defense-in-depth gap" against "best-practice deviation". E-A1's highest-fit rule resolves this for `se`.
  - The command: "Potential risk" against "Hardening recommendation". This is a same-file ambiguity of the command, so it
    is outside ADR-008 (§ Scope, "A document that contradicts itself") and outside this subject.

  Under option A it cannot pull a grade below `se`'s. It is recorded, not ruled.
- **O3. A sibling case named in two open briefs has no `tests/golden/open/` directory.** I did not look in held-out.
  *Orchestrator note (2026-10-08):* the name is redacted here. `tests/functional/test_golden_held_out_isolation.py`
  documents it as a held-out case that open briefs cite from before the open/held-out split (T411), and held-out case
  IDs must not appear in committed files outside `tests/golden/`. Nothing was read from held-out.
- **O4. Not on this subject.** The command's LOW reads "add to backlog" (`:46`), and `sg:184` reads "tracked as technical
  debt". These are consequences, not definitions. They are jointly satisfiable, since a backlog item can be the debt
  record. Not ruled.

## 9. Summary

| Item | Step | Contradiction? | Outcome | Escalation | Candidate edits (held) | Files |
|---|---|---|---|---|---|---|
| O1: two grade-definition sets under `/security-audit` (`se:81–84` against `/security-audit:43–46`) | **E (P5)**. A fails (one-value test); B does not fire; C is met, but its remedy lowers grades (ADR-007 §5) and the alternative overrides the command (P2); D does not apply | **Yes.** One finding can carry two grades (MEDIUM/LOW for a non-required hardening gap; the verdict moves between CONDITIONAL_PASS and PASS) | Not decidable without lowering a grade or changing the command | **Q-O1** (§4). Options: A (Recommended), B, C | Option A: E-O1a (command; user decision only) and E-O1b (agent, scoped) | `commands/security-audit.md`, `agents/security-engineer.md` |

- **Amendments made now:** none (P5 § Form 3).
- **Interaction with E-A1:** E-A1 does not decide O1. It joins the same subject on the agent's side and makes the
  divergence certain. Option A is consistent with it, and its implementation follows T589's merge (§3).
- **Golden:** under any option, no quote, fixture or result changes. No protected-path grant or evaluator-hash baseline
  is needed (§6).
- **Maturity** was not relied on. Neither were corpus counts, majority practice or golden-coupling convenience.
- **Blockers:** none. Q-O1 is a ruling outcome. C1 is a `minor` brief correction.
- **Still unverified:**
  - the working tree's cleanliness against `40dc780`;
  - every count in §7 and the anchor uniqueness in §5.2, which come from reading, not `grep`;
  - that no unread file under `implementation/knowledge/` places the subject;
  - that no open case other than the three cites `se`;
  - the root-drift count;
  - the grade judgment in §6's fixture observation and in the illustrative examples of §2.3 and §4.
