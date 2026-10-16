# Artifact: poc-security-reviewer-blocking-v1.md

> Filename: `poc-security-reviewer-blocking-v1.md`. Immutable once produced; revisions bump `<N>`.

## Metadata

- **Producer agent**: solution-architect
- **Task**: T578 (P1, O1, SECURITY:HIGH)
- **Created**: 2026-10-02
- **Based on**:
  - `docs/tasks/task-T578.md` (authoritative brief);
  - `docs/plans/plan-099-poc-security-reviewer-blocking.md`;
  - `docs/artifacts/security-review-poc-security-shortcuts-v1.md` § O1 (Security Engineer rating SECURITY:HIGH and fix
    direction);
  - `docs/artifacts/poc-security-shortcut-examples-v2.md` §9, §13.2 (O1 scoped, `rapid-prototyping:54` batched here);
  - `docs/artifacts/poc-skills-alignment-v1.md` §10.2 and `docs/artifacts/poc-contract-resolution-v1.md` §9.2 (the
    precedents for amending agent and skill files under quoted authority);
  - `docs/decisions/ADR-007-command-contract-authority.md` (Accepted; **not** used to rank agents, see §1.3).
  - Source files under `implementation/knowledge/`: `agents/poc-security-engineer.md`, `agents/poc-orchestrator.md`,
    `skills/rapid-prototyping/SKILL.md`, `instructions/security-guidelines.md`, `instructions/poc-guidelines.md`,
    `agents/security-engineer.md`; for comparison also `skills/code-review/SKILL.md`,
    `skills/technical-debt-tracking/SKILL.md`, `agents/{technical-debt-narrator,poc-qa-engineer,integration-agent,
    scaffolding-agent,poc-devops-engineer}.md`, `commands/new-poc.md`, `docs/tasks/task-T577.md`,
    `tests/functional/test_agent_escalation_consistency.py`.
  - All read on branch `agent/solution-architect/T578` at `develop` `e1feee4`.
- **Supersedes**: none (first version)
- **Decision references**: O1 / plan-099. No new ADR is minted. No P34b ranking is used (§1.3).

## 0. What this document is, and what it did not do

This is the ruling on every brief §2 site, with exact edits for the follow-up to apply. **It changed no agent, skill,
command, instruction or golden case.** It is the only file written.

**Method and limits.**
- **No shell.** I had no grep, git or test runs. Claims that need one are marked **(unverified)** and collected in §11.
- **Golden files:** I opened nothing under `tests/golden/`.
- **Applying the edits:** apply each edit by matching its exact `Before:` text, never by line number. Line numbers are
  given at `e1feee4` for orientation only. Every `Before:` text below is unique in its file at `e1feee4`, which I
  checked by reading each file in full. The `—` character in the agent files is U+2014, as in the source.

## 1. Authority basis

### 1.1 The quoted texts

**`security-guidelines.md`** (`maturity: stable`, `applyTo: "**"`, `:3–4`):
- **Rails, Out of scope, `:15–20`:** "Does not grant any agent authority to disable a security control 'temporarily,'
  even in PoC or development mode — the Immutable Security Constraints section forbids that outright, **superseding
  any speed-over-completeness pressure from `poc-guidelines.md`**."
- **Rails, Failure mode, `:22–24`:** "`SECURITY:CRITICAL`/`SECURITY:HIGH` findings block merge per the Security Review
  Workflow until resolved; `SECURITY:MEDIUM` findings require a documented remediation plan before merge".
- **Immutable Security Constraints, `:153`:** "The following constraints are absolute and cannot be overridden by any
  agent, configuration, or runtime decision".
- **`:155`, Constraint 1:** "No API keys, passwords, tokens, certificates, or private keys may ever be committed. This
  is not negotiable regardless of PoC status, urgency, or convenience."
- **Security Review Workflow, `:181–184`:** "Security Engineer flags findings as `SECURITY:CRITICAL`, `SECURITY:HIGH`,
  `SECURITY:MEDIUM`, or `SECURITY:LOW`" / "`CRITICAL` and `HIGH` findings block merge until resolved" / "`MEDIUM`
  findings must have a remediation plan before merge" / "`LOW` findings are tracked as technical debt".
- **Agent Safety Guards, `:117–118`, `:122`, `:128`:** "Coding agents MUST treat the following as hard blocks unless
  the user explicitly approves in the current session" / "Never run or suggest without explicit user approval" /
  "History rewrite | `git rebase` on pushed branches, `git commit --amend` after push". **`:126`:** "`git push
  --force`, `git push -f`". **`:135`:** "Do not paste secret values into chat, handoffs, checkpoints, or commits".

**`poc-guidelines.md`** (`stable`, `applyTo: "**"`):
- **Rails, `:10–13`:** it "applies whenever `poc-orchestrator` or a PoC specialist agent begins hypothesis-driven
  exploratory work".
- **Rails, `:17–19`:** it "Does not waive the Immutable Security Constraints in `security-guidelines.md` (no exposed
  secrets, no real PII in demos) merely because a workstream is time-boxed."
- **Not Allowed, `:144`:** "Exposing secrets in code".

**`poc-orchestrator.md`** (`stable`), self-subordination, **`:73–76`**: "every delegation this agent issues is
governed by that instruction [`poc-guidelines.md`], not just the summary below."

**`AGENTS.md`**:
- **§ Validation Gates:** "VERDICTS: `PASS` | `CONDITIONAL_PASS` | `FAIL`" / "Review agents (Tech Lead, QA,
  Security) MUST NOT modify code during review." / "`FAIL` blocks progression." / "`CONDITIONAL_PASS` proceeds with
  tracked conditions added to the task list."
- **§ Blocker Protocol:** "Max 2 retries before user escalation. Agents MUST NOT silently fail."

**`git-workflow.md`** Rails: it "Does not grant any agent, including the orchestrator, authority to bypass branch
protection for any reason".

### 1.2 Reading, site by site

**The two agents (`poc-security-engineer`, `poc-orchestrator`).** "Record findings for debt handoff" of a committed
secret (`poc-security-engineer.md:20`, `:47`) is an agent's runtime decision to leave a Constraint 1 breach in place.
`:153` says no agent or runtime decision can override the constraint. The agents' text and the instruction cannot
both be satisfied. The instruction asserts its precedence by name, including over PoC speed pressure (`:17–20`).
Neither agent claims any exemption, and `poc-guidelines` concedes the point (`:17–19`). As in
`poc-security-shortcut-examples-v2.md` §1.2, one side asserts and the other does not contest, so **no ranking is
needed**.

Each agent is also inside the instruction's reach in its own terms:
- **`poc-orchestrator`** subordinates every delegation to `poc-guidelines` (`:73–76`). That covers the speed
  directive (`:66`), which is part of every delegation brief, and the security-scan delegation (`:53`).
- **`poc-security-engineer`** is a "PoC specialist agent" under `poc-guidelines` Rails `:10–13`. It is in
  `poc-orchestrator`'s `agents:` roster (`:5`). It is also a Security review agent under `AGENTS.md` § Validation
  Gates.

**Precedent.** FU-C (`poc-contract-resolution-v1.md` §9.2) approved amending two `stable` PoC agents. Its basis was
"the T542 precedent, where ADR-007 branch 1 was applied by analogy to an agent file that contradicted a `stable`
instruction". It also relied on each agent's own subordination, or on its falling under `poc-guidelines.md`'s scope
"which covers PoC specialist agents". Both legs are present here.

**The skill (`rapid-prototyping`, `experimental`).** `poc-skills-alignment-v1.md` §10.2 already approved extending
the T542/FU-C precedent from agent files to these PoC skill files. The skill places itself in PoC work by its own
description: "fast proof-of-concept delivery".

**The secret-exposure procedure.** This is the one **weaker leg**, and I state it as such. Constraint 1 forbids
committing a secret but does not prescribe the remedy once one has been committed. The content of the procedure,
"revoke or rotate, and remove from history", therefore rests on two sources:
- the Security Engineer's fix direction (`security-review-…-v1.md` § O1);
- plan-099 §2 item 1, the scope the user approved at P1.

Its **routing** of the history rewrite through the user rests directly on Agent Safety Guards `:117–128` and on
`git-workflow`'s Rails. The procedure creates no new obligation beyond what those sources name.

### 1.3 Does anything need a P34b ranking? **No.**

Every edit below rests on text that asserts its own reach, and that the edited file does not contest. None of it
rests on "an instruction outranks an agent". ADR-007 is cited only as the procedure the precedents used. **No
`dependency` blocker is raised.**

## 2. `poc-security-engineer.md` (held at `beta` while the P1 row is open)

**What the agent does after these edits:**
- It grades findings on the Security Review Workflow's scale.
- It **blocks** on any Immutable Security Constraint breach and on any `SECURITY:CRITICAL` or `SECURITY:HIGH` finding,
  returning `FAIL`. Such a finding is never debt.
- It does **not block** on `SECURITY:MEDIUM` (which gets a remediation plan before merge) or on `SECURITY:LOW` (which
  goes to debt handoff).
- For an exposed secret, deleting it from the code does not clear the finding.
- It never rotates credentials or rewrites history itself.

### E1: `:3`, description (site `:3`)

````
Before:
description: "Use for lightweight PoC security review that flags critical risks without blocking rapid validation."

After:
description: "Use for lightweight PoC security review. Flags high-risk issues, and blocks the PoC on critical or high findings and on any Immutable Security Constraint breach, such as a committed secret."
````

**Why the description must change:** subagent delegation is driven by `description` (`CLAUDE.md`: "let Claude
delegate automatically based on each subagent's `description`"). "Without blocking" in that field would keep teaching
the old rule to every router. **Authority:** `security-guidelines:22–24`, `:153`, `:155`.

### E2: `:18–20`, § Behavior (site `:18–20`)

````
Before:
## Behavior
- Do not block progress by default
- Record findings for debt handoff

After:
## Behavior
- Grade every finding `SECURITY:CRITICAL`, `SECURITY:HIGH`, `SECURITY:MEDIUM` or `SECURITY:LOW`, as in `security-guidelines.md` § Security Review Workflow
- **Blocking findings:** any breach of an Immutable Security Constraint in `security-guidelines.md` (for example a committed secret, or real PII in demo data), and any `SECURITY:CRITICAL` or `SECURITY:HIGH` finding (for example an obvious injection or authorization gap). Report each one to the PoC orchestrator as a blocker. A blocking finding is never recorded for debt handoff, and it stays open until its fix is re-checked and confirmed
- **Non-blocking findings:** do not block progress on `SECURITY:MEDIUM` or `SECURITY:LOW` findings. Give each `SECURITY:MEDIUM` finding a remediation plan (owner, fix, deadline), which must exist before the affected work merges. Record `SECURITY:LOW` findings for debt handoff
- **Exposed secret:** report the file, line, commits, whether they were pushed, the credential's type and issuer, and the environment variable that should replace it. Never reproduce the value. Deleting the secret from the code does not resolve the finding. It stays open until the user confirms the secret is revoked or rotated, the code reads it from the environment or a secret vault, and the secret is removed from git history with the user's explicit approval (`poc-orchestrator` § Security Findings). Never revoke or rotate credentials, rewrite history or force-push yourself
- End every scan with a verdict (`AGENTS.md` § Validation Gates): `FAIL` while any blocking finding is open, `CONDITIONAL_PASS` if `SECURITY:MEDIUM` findings remain with their remediation plans, otherwise `PASS`
````

**Brief §3 items covered:**
- **1:** "Do not block by default" is kept for MEDIUM and LOW only.
- **2:** the blocking carve-out.
- **3:** the agent's half of the secret procedure.
- **5:** the MEDIUM remediation plan (§6).

**Authority:**
- `security-guidelines:153`, `:155`, `:181–184`.
- `AGENTS.md` § Validation Gates. "`FAIL` blocks progression" makes "block" mechanical rather than prose.
- Agent Safety Guards `:135`, for "never reproduce the value".
- "Never … yourself" follows from "Review agents … MUST NOT modify code during review" and from Safety Guards
  `:117–128`.

**Plan content:** the "(owner, fix, deadline)" content follows the production reviewer's Conditions format,
"owner=@[who], remediation=[what], deadline=[when]" (`security-engineer.md:177`). That is corroboration, not
authority (§6).

### E3: `:35`, § Blocker Reporting step 3 (site `:35`; escalation sentence preserved)

````
Before:
3. Suggest a workaround — PoC speed matters, prefer unblocking over perfection

After:
3. Suggest a workaround — PoC speed matters, prefer unblocking over perfection. A blocking finding (§ Behavior) has no workaround: name the fix it needs instead
````

**Mechanical constraint met.** Line `:36`, "4. The PoC orchestrator will handle escalation", is **not** in any
`Before:` text and stays byte-identical. `test_each_poc_track_agent_names_poc_orchestrator`
(`tests/functional/test_agent_escalation_consistency.py:102–110`) asserts that literal with `assertIn` over the whole
file. I read the test.

**Why amend rather than delete:** the line governs the agent's *own* blockers, such as a repository it cannot read,
where a workaround is legitimate. Only its spill-over onto findings is wrong. The same line appears in eleven other
PoC agents, which is out of scope (§12, X2).

### E4: `:46`, Rails, Out of scope (site `:46`)

````
Before:
**Out of scope**: Blocking PoC progress on non-critical findings; performing a full OWASP-style audit.

After:
**Out of scope**: Blocking PoC progress on `SECURITY:MEDIUM` or `SECURITY:LOW` findings; performing a full OWASP-style audit; revoking or rotating credentials, or rewriting git history (§ Behavior).
````

**Why:** "non-critical" is ambiguous on this scale. `SECURITY:HIGH` is "non-critical", but it must block
(`security-guidelines:183`).

### E5: `:47`, Rails, Failure mode (site `:47`)

````
Before:
**Failure mode**: If a critical risk (exposed secret, obvious injection/auth gap) is found, records it explicitly for debt handoff rather than silently omitting it to avoid blocking progress.

After:
**Failure mode**: If a blocking finding is found (an exposed secret, an obvious injection or authorization gap, any other `SECURITY:CRITICAL` or `SECURITY:HIGH` finding, or any Immutable Security Constraint breach), reports it to the PoC orchestrator as a blocker and returns `FAIL`, rather than recording it for debt handoff or omitting it to avoid blocking progress.
````

**Unchanged in this file:**
- `:1–2` and `:4–17`. The `maturity: beta` line (`:6`) is not this task's to change; plan-099 §2 step 4 covers
  re-promotion.
- `:21–34`, `:36–45` and `:48–52`.

## 3. `poc-orchestrator.md` (stable)

### E6: `:49`, a secrets check after scaffolding and integration (brief §3 item 4, "earlier than step 9")

````
Before:
5. **Integration** — `@integration-agent`: third-party API/SDK wiring (parallel with scaffolding if independent)

After:
5. **Integration** — `@integration-agent`: third-party API/SDK wiring (parallel with scaffolding if independent)
   - **Secrets check** — `@poc-security-engineer`: whenever work from steps 4, 5 or 7 is about to be pushed or merged for the first time, check it for committed secrets and hardcoded credentials. A finding blocks (§ Security Findings)
````

**Decision: yes, earlier.** Keep step 9's full scan. Add a secrets-only check triggered by the first push or merge
of the steps that bring in configuration and credentials:
- step 4, scaffolding, whose deliverables include a "Minimal environment template" (`scaffolding-agent.md:17`);
- step 5, integration, which delivers "Required environment variables" (`integration-agent.md:16`);
- step 7, implementation.

**Why push or merge is the trigger.** Before a push, the secret exists only in local history. That gives the smallest
exposure surface, and the clean-up does not touch a shared or protected branch. A step-number trigger alone would be
wrong, because step 9 runs after work from steps 4–7 may already have been pushed.

**Recorded alternatives:**
- **(a) Move step 9 earlier wholesale. Not taken.** The full scan must see the implementation (step 7).
- **(b) A pre-commit secret-scanning hook. Not ruled.** It is the only control that stops a commit at all. It is a
  tooling choice that would land in `scaffolding-agent` or `poc-devops-engineer`, so it is parked as §12, X1.

**Format:** the 3-space sub-bullet indentation matches step 2's sub-bullet (`:46`).

**Test effect:**
- `test_workflow_mentions_are_real_registered_agents` and `test_workflow_roster_matches_frontmatter_roster` read the
  `## PoC Workflow` section.
- The added mention, `@poc-security-engineer`, is registered and is in the roster (`:5`).
- The distinct-mention count is unchanged, so the "≥ 10" assertion still holds.

### E7: `:53`, step 9 (site `:53`)

````
Before:
9. **Security Scan** — `@poc-security-engineer`: critical risks only

After:
9. **Security Scan** — `@poc-security-engineer`: high-risk issues, not a full audit. Blocking findings stop the PoC (§ Security Findings)
````

**Why:** "critical risks only" reads as "only SECURITY:CRITICAL matters". It also matches nothing in the agent's own
Scope ("Flag obvious high-risk issues", `poc-security-engineer.md:14`).

### E8: new `## Security Findings` section, inserted between § PoC Workflow and § Delegation Brief (brief §3 items 2–5)

````
Before:
14. **DevOps** — `@poc-devops-engineer`: fast local reproducibility

## Delegation Brief (PoC-Adapted)

After:
14. **DevOps** — `@poc-devops-engineer`: fast local reproducibility

## Security Findings

`security-guidelines.md` applies to PoC work in full. Its Rails withhold authority to disable a security control "even in PoC or development mode", its Immutable Security Constraints "cannot be overridden by any agent, configuration, or runtime decision", and `poc-guidelines.md` "Does not waive the Immutable Security Constraints". Route `@poc-security-engineer`'s findings as its § Behavior grades them, per `security-guidelines.md` § Security Review Workflow:

- **Blocking** (any Immutable Security Constraint breach; any `SECURITY:CRITICAL` or `SECURITY:HIGH` finding): set the affected task to `blocked`, stop every delegation except the remediation, record the blocker in the next checkpoint, and tell the user. Delegate the fix, then have `@poc-security-engineer` re-check it. The PoC does not continue, demo, evaluate or close until the re-check confirms the finding is resolved. Never record a blocking finding as debt. The speed directive, the timebox and the token envelope do not waive it. If two remediation cycles fail, escalate to the user (`AGENTS.md` § Blocker Protocol).
- **`SECURITY:MEDIUM`**: does not block. Before the affected work merges, add its remediation plan (owner, fix, deadline) to the task list as a tracked condition (`AGENTS.md` § Validation Gates), and carry it into the debt handoff.
- **`SECURITY:LOW`**: record for debt handoff.

**Exposed secret.** Deleting a secret from the code does not resolve it: it stays in git history, and it is compromised from the moment it was committed. Never copy its value into a brief, report, checkpoint, handoff or commit; refer to it by file, commit and environment-variable name only (`security-guidelines.md` § Agent Safety Guards).

1. **Revoke or rotate — the user.** Ask the user to revoke or rotate the secret at its issuer, and to set the replacement locally. No agent does this.
2. **Fix the code — a delegated agent.** Delegate the change that reads the secret from an environment variable or a secret vault, by name only, as a normal commit.
3. **Remove it from history — only with the user's approval.** Rewriting history is a destructive operation that agents "MUST treat … as hard blocks unless the user explicitly approves in the current session" (`security-guidelines.md` § Agent Safety Guards). Ask the user, naming the commits and branches affected. The rewrite happens only after that approval: the user performs it, or names the agent and the branches. No agent bypasses branch protection (`git-workflow.md`). Copies a rewrite cannot reach, such as clones, forks, merge-request refs and CI logs, are why step 1 comes first.
4. **Resolve.** `@poc-security-engineer` confirms the finding resolved only when the user has confirmed step 1, the step 2 fix is in place, and step 3 is done. If the user does not approve step 3, the finding stays open and the PoC stays blocked; record the user's decision in the next checkpoint.

## Delegation Brief (PoC-Adapted)
````

**Why a section, not more bullets in the Workflow.** The routing applies to findings from both the secrets check (E6)
and step 9 (E7). It also has to be referable from three other places:
- the agent (E2);
- the Constraints line (E10);
- the skill (E11).

**Placement is test-safe.** The workflow regex `## PoC Workflow\n(.*?)\n## ` now stops at `## Security Findings`.
The workflow section's content is unchanged, apart from E6 and E7.

**Authority:** the quotes inside the section are verbatim from §1.1. The rest maps as follows:
- "set … `blocked`" follows `AGENTS.md` § Lifecycle States.
- "record … in the next checkpoint" follows `AGENTS.md` § Checkpoint Protocol, which lists "blockers".
- "tracked condition" follows `AGENTS.md` § Validation Gates.
- "two remediation cycles" follows `AGENTS.md` § Blocker Protocol ("Max 2 retries before user escalation").
- "The token envelope do[es] not waive it" closes the route through this agent's own Failure mode (`:107`, "reduces
  scope rather than exceeding the budget"). Without it, the security remediation could be cut as "scope".

### E9: `:66`, the speed directive (site `:66`)

````
Before:
4. **Speed directive**: "Optimize for demo speed, not production quality"

After:
4. **Speed directive**: "Optimize for demo speed, not production quality. Security is the exception: simplify how a security control is built, but never remove or weaken it, and never commit a secret (`security-guidelines.md`)."
````

**Authority:**
- `security-guidelines:17–20`, the passage "superseding any speed-over-completeness pressure from `poc-guidelines.md`",
  which names this exact pressure.
- `:155`.
- `poc-orchestrator:73–76`: "every delegation … is governed by" `poc-guidelines`.

**Why it cites `security-guidelines.md`, not `poc-guidelines` § Allowed Shortcuts.** T577 is still pending, and the
wording matching T576 R4 ("may simplify how security controls are built but never remove or weaken them") is not in
`poc-guidelines` until T577 lands. Citing `security-guidelines.md` makes E9 independent of merge order.

**Untouched:** `:34` ("speed priority") in EXECUTE PHASE is unchanged, because every brief carries item 4, which now
includes the exception.

### E10: `:114`, § Constraints (site `:114`)

````
Before:
- **DO NOT** block on non-critical security findings — record for debt handoff

After:
- **DO NOT** block on `SECURITY:MEDIUM` or `SECURITY:LOW` findings — a MEDIUM finding gets a remediation plan before merge, a LOW finding is recorded for debt handoff (§ Security Findings)
- **DO** block on every Immutable Security Constraint breach and every `SECURITY:CRITICAL` or `SECURITY:HIGH` finding until it is resolved, and never hand one off as debt (§ Security Findings)
````

**Unchanged in this file:**
- The frontmatter. Its `description` says nothing about blocking.
- The Rails (`:103–107`): the Failure mode is about tokens, and E8 makes the token envelope unable to waive a
  blocking finding.
- Everything not named in E6–E10.

## 4. `rapid-prototyping/SKILL.md` (experimental): site `:61`, "Enforcement" (brief §3 item 6)

### What the current text already does (brief correction, §10 C3)

The Security review read the **pre-T575** line (`:54`, "🟡 Should Fix"). As amended by T575, `:61` already grades
"the shortcut itself" on the code-review scale, "so a shortcut that is a bug, security issue or data loss risk is a 🔴
Must Fix finding". `code-review/SKILL.md:96` (stable) maps 🔴 Must Fix to "Block merge".

**Two gaps remain:**
1. "Security issue" is left to the reviewer's judgement. A *tagged* removal of a security control is outside the
   bullet entirely, because the bullet covers "untagged" shortcuts only.
2. The bullet's last sentence routes the finding "into the debt ledger" (technical-debt-tracking Step 3 merges "🔴
   Must Fix and 🟡 Should Fix items"). That is a debt route. The code-review skill's waiver (`:150`, "no override
   without Tech Lead waiver") would let it stand there unfixed.

### E11: `:61` (append three sentences to the bullet)

````
Before:
- An untagged shortcut discovered during review is flagged as a review finding. The missing tag is a 🟡 Should Fix finding. The shortcut itself is graded like any other finding on the code-review skill's § Severity Guide, so a shortcut that is a bug, security issue or data loss risk is a 🔴 Must Fix finding. These labels grade review findings, not debt: the technical-debt-tracking skill assigns the debt severity when it merges the finding into the debt ledger (§ POC-DEBT Tag Scanning Procedure, Step 3).

After:
- An untagged shortcut discovered during review is flagged as a review finding. The missing tag is a 🟡 Should Fix finding. The shortcut itself is graded like any other finding on the code-review skill's § Severity Guide, so a shortcut that is a bug, security issue or data loss risk is a 🔴 Must Fix finding. These labels grade review findings, not debt: the technical-debt-tracking skill assigns the debt severity when it merges the finding into the debt ledger (§ POC-DEBT Tag Scanning Procedure, Step 3). Security is the exception: removing or weakening a security control, or breaching an Immutable Security Constraint in `security-guidelines.md`, is a 🔴 Must Fix finding whether or not it is tagged. It blocks until it is fixed, and it never enters the debt ledger as open debt. An exposed secret is not fixed by deleting it from the code: report it to the PoC orchestrator, which follows `poc-orchestrator` § Security Findings.
````

**Authority:**
- `security-guidelines:17–20`: no authority to disable "a security control … even in PoC". "Blocks until it is fixed"
  therefore excludes a waiver.
- `:153`, `:155`.
- The reviewer's statement: "An untagged removal of a security control should block" (`security-review-…-v1.md`
  § Findings, last bullet).
- "Whether or not it is tagged" matches T576 R6, which T577 inserts into this same file: "A tag records a shortcut;
  it does not make a forbidden shortcut permissible."

**Two gates, on purpose.** This review gate (code-review scale) blocks on *any* removed or weakened security control.
The security scan (E2) blocks only on CRITICAL, HIGH or a constraint breach. The same split exists on the production
track: `code-review:96` blocks merge on any "security issue", while the Security Review Workflow blocks on
CRITICAL/HIGH. These are two gates with different jobs, and the stricter one governs wherever it runs. See §9 Q1 for
the alternative.

**Concurrency with T577.**
- T577 edits this file at v2's sites R6–R9 (`:33–49` region). None of them overlaps `:61`.
- T577 inserts lines above `:61`, so its number will shift. E11 must be applied by text.
- Whichever task lands second re-runs `--print-drift` and must not double-declare the `rapid-prototyping` projection
  paths.

**Unchanged:**
- The Rails (`:14`, "A shortcut found without a `POC-DEBT` tag is flagged as a review finding") is still true.
- The rest of the file.

## 5. The secret-exposure procedure (brief §3 item 3): who does what

This summarises E2 (the agent's side) and E8 (the orchestrator's side). The text is in E8; this table adds nothing
to it.

| # | Step | Actor | May an agent do it alone? | Basis |
|---|---|---|---|---|
| 0 | Detect and report: file, line, commits, pushed or not, credential type and issuer, replacement env-var name. **Never the value.** Verdict `FAIL`. | `poc-security-engineer` | Yes, read-only | E2; Safety Guards `:135`; `AGENTS.md` § Validation Gates |
| 1 | Halt: set task `blocked`, stop delegations except remediation, checkpoint the blocker, tell the user | `poc-orchestrator` | Yes | E8; `AGENTS.md` § Lifecycle States, § Checkpoint Protocol |
| 2 | **Revoke or rotate** at the issuer; set the replacement locally | **User** | **No.** No agent handles the value or the issuer console | E8 step 1; Safety Guards `:136` ("reference **names only** and instruct the user to set them locally") |
| 3 | Code reads the secret from env or vault, as a normal commit | Delegated write-capable agent (for example the one that introduced it) | Yes, as a normal commit | E8 step 2 |
| 4 | **Remove from git history** | **User**, or an agent the user names for named branches after explicit approval in the current session | **No.** It is a hard block without user approval. No agent bypasses branch protection. | E8 step 3; Safety Guards `:117–128`; `git-workflow` Rails |
| 5 | Re-check and confirm resolved | `poc-security-engineer` | Yes, once the user has confirmed step 2 and step 4 is done | E8 step 4 |

**Why the order matters.** Rotation comes first, because a rewrite cannot reach clones, forks, merge-request refs or
CI logs. That a hosting platform keeps such copies is general knowledge; GitLab's specifics are **(unverified)**.

**A secret found before any commit** (for example in a working tree): Constraint 1 ("committed") is not yet breached.
It is still a blocking finding under E2, because a hardcoded secret about to be committed is at least
`SECURITY:HIGH`. Steps 3 and 5 resolve it. I did not write this case into E8 as a separate rule; the trigger "once
committed" in E8's first paragraph covers it implicitly. See §9 Q3.

## 6. MEDIUM findings and the remediation plan (brief §3 item 5): **yes, required, non-blocking**

**Ruling.** A `SECURITY:MEDIUM` PoC finding does not block. It must have a remediation plan (owner, fix, deadline)
before the affected work merges. The orchestrator records the plan as a tracked condition in the task list, and it is
carried into the debt handoff.

**Authority:**
- `security-guidelines:23–24` and `:183` are not track-scoped, and the instruction is `applyTo: "**"`.
- `AGENTS.md` § Validation Gates: "`CONDITIONAL_PASS` proceeds with tracked conditions added to the task list", which
  is the verdict E2 assigns.

**Why it is not left as "debt handoff" alone.** Debt handoff happens at evaluation, *after* merges. The workflow
requires the plan "before merge".

**Kept light on purpose.** The plan is three fields. The deadline is set by whoever writes the plan and is not fixed
here; `security-guidelines` does not fix one.

**LOW:** "tracked as technical debt" (`:184`). That equals "record for debt handoff", so the old rule survives
exactly where the instruction allows it.

## 7. Blast radius and golden coupling

| Neighbour | Effect |
|---|---|
| `security-guidelines.md`, `poc-guidelines.md`, `AGENTS.md`, every command | **Unchanged.** |
| `technical-debt-tracking` Step 3 ("Security scan findings" merged into the ledger) | **No edit compelled.** After E2, only MEDIUM/LOW findings (and resolved blocking findings, as history) can reach it as open items. Its `Status: resolved` value already exists (`:93`). |
| `code-review` (stable) | Unchanged. E11 relies on its `:96` mapping. |
| Other PoC agents' "prefer unblocking over perfection" | Unchanged; §12, X2. |
| `tests/functional/test_agent_escalation_consistency.py` | Stays green **(reasoned from reading the test, not run)**: the escalation literal is preserved (E3), and E6's workflow mention is registered and in the roster. |
| `tests/functional/test_check_maturity.py` snapshot | No change from FU-1 itself. No maturity line is edited. Re-promotion (FU-2) moves it. |
| Registry `implementation/registry/index.json` | Checksums for the three files change. **E1 changes `poc-security-engineer`'s `description`**, so its descriptive field changes too. That the registry carries `description` is inferred from `poc-skills-alignment-v1.md` §4 ("The frontmatter `description` does not change, so the registry's descriptive fields do not change") **(unverified)**. |
| Platform mirrors `implementation/.<platform>/` | Regenerate with `make sync`. |
| Repo-root projections | 3 files × 7 platforms = **21 paths** to declare in `tests/_baselines/root-install-drift.json`, net of any `rapid-prototyping` paths T577 already declared **(unverified; declare exactly what `--print-drift` reports)**. Do not hand-edit root folders. |
| Line numbers of `poc-orchestrator.md` | E6 and E8 shift every line after `:49`. A live file citing `poc-orchestrator.md:<n>` would go stale **(unverified that none exists)**. Immutable past artifacts are historical and are not edited. |
| `check-maturity` and the `Affects` field | Plan-099 has the implementation row declare `agent/poc-security-engineer`. If FU-1 also declares `agent/poc-orchestrator` at P1, `check-maturity` would count an open P1 defect against a `stable` agent and fail, unless it too is held at `beta`. That mechanism is inferred from plan-099 §1 **(unverified)**. This is a decision for the orchestrator or the user (§8, FU-1 note), not for me. |

**Golden coupling: (unverified), with no golden access.**
- **`rapid-prototyping`.** The orchestrator's earlier searches found it only as an installed copy in the
  `/discover-skills` fixture, whose `expect.py` checks that skill directories exist, not their content
  (`poc-skills-alignment-v1.md` §10.1 #2). If that still holds, E11 has no coupling.
- **The two agents.** No prior record covers them. The PoC golden cases I know of by name are
  `new-poc-plan-hypothesis-format`, `poc-demo-hypothesis-status-evidence-gaps` and
  `evaluate-poc-verdict-debt-reconciliation`. They quote commands and `poc-guidelines`, and reference
  `poc-orchestrator`'s PLAN PHASE by name, which no edit here touches (`poc-contract-resolution-v1.md` §§2–5). Whether
  any fixture holds an installed copy of either agent whose *content* is asserted is **(unverified)**.
- **Expected outcome:** no grant, no fixture change, no baseline or evaluator-hash change. **The orchestrator must
  confirm by searching `tests/golden/` (with `held-out` pruned before traversal) for:**
  - `without blocking rapid validation`
  - `Record findings for debt handoff`
  - `records it explicitly for debt handoff`
  - `critical risks only`
  - `non-critical security findings`
  - `Optimize for demo speed`
  - `prefer unblocking over perfection` (expected to hit 12 agents' worth of installed copies, if any)
  - `Should Fix finding`

## 8. Follow-ups

| Step / task | Covers | Files | `tests/golden/**` grant? | Owner (suggested) | Priority | Depends on / verify |
|---|---|---|---|---|---|---|
| **REV**: Security Engineer review of this ruling (plan-099 §2 step 2) | E1–E11, §5, §6, §9 Q1–Q3 | None. The orchestrator records the hand-back as `docs/artifacts/security-review-poc-security-reviewer-blocking-v1.md` | No | Security Engineer (read-only) | P1 | **Verify:** a verdict (`PASS` / `CONDITIONAL_PASS` / `FAIL`) per `AGENTS.md`; explicit answers to §9 Q1–Q3. A `FAIL` or any condition produces a `-v2` of this artifact, never an edit to v1. |
| **FU-1**: apply O1 (plan-099 §2 step 3) | E1–E11 | `implementation/knowledge/agents/poc-security-engineer.md` (E1–E5); `…/agents/poc-orchestrator.md` (E6–E10); `…/skills/rapid-prototyping/SKILL.md` (E11); regenerated `implementation/.<platform>/` mirrors (`make sync`); `implementation/registry/index.json` (generator); the `drift` list in `tests/_baselines/root-install-drift.json` | **No** (pending the §7 golden search) | Backend Developer (needs a shell) | P1 | **Depends on REV** (and on any v2 it triggers). **Affects:** `agent/poc-security-engineer`; whether to also declare `agent/poc-orchestrator` is the §7 decision. **Verify:** (1) each `Before:` matches **exactly once by text** on `develop` at dispatch, after T577 if it has landed, then apply; (2) `The PoC orchestrator will handle escalation` still occurs in `poc-security-engineer.md`; (3) 0 hits under `implementation/knowledge/` for `without blocking rapid validation`, `Record findings for debt handoff`, `records it explicitly for debt handoff`, `critical risks only`, `block on non-critical security findings`, `Do not block progress by default`; (4) exactly once each: `## Security Findings` in `poc-orchestrator.md`; `**Secrets check**` in `poc-orchestrator.md`; `Security is the exception:` in `poc-orchestrator.md` and in `rapid-prototyping/SKILL.md`; `has no workaround` in `poc-security-engineer.md`; (5) grep `implementation/knowledge/` and `docs/` (not `docs/artifacts/`, which is immutable) for live citations `poc-orchestrator.md:` and report any that E6/E8 made stale; (6) `sync.mjs --check` and `generate-registry.py --check` clean; root parity green, declaring exactly what `--print-drift` reports and not double-counting T577; (7) `security-guidelines.md`, `poc-guidelines.md`, `commands/` and `tests/golden/**` byte-unchanged; (8) `check-maturity.py --root implementation`: 0 failing, and `poc-security-engineer` still `beta` while the P1 row is open; (9) `scorecard.py --check` unchanged against the current baseline; (10) `python3 docs/tasks/validate-tasks.py` passes; (11) `python3 tests/run.py`, exit code checked, output redirected to a file, not piped. |
| **FU-2**: re-promote `poc-security-engineer` to `stable` (plan-099 §2 step 4) | Maturity | `implementation/knowledge/agents/poc-security-engineer.md` (`:6` only); registry; `tests/functional/test_check_maturity.py` snapshot | No | Orchestrator scopes it | P2 | After FU-1 merges and the P1 row is archived. **Verify:** `check-maturity` 0 failing with the agent `stable`; snapshot updated; nothing else in the file changed. |

**Release note (plan-099 §3) unchanged:** no release ships the current text until FU-1 merges.

## 9. Questions for the Security Engineer review (decide explicitly)

- **Q1: Should the security scan block on any removed or weakened control?** E2 blocks on Immutable Constraint
  breaches and on `CRITICAL`/`HIGH` findings, as the fix direction says. After T577, `poc-guidelines` Not Allowed
  also lists "Removing or weakening any security control … with or without a `POC-DEBT` tag".
  - **Recorded alternative:** the scan also blocks on any removed or weakened control, whatever its severity.
  - **Not taken.** `security-guidelines:183` gives MEDIUM a plan, not a block. The stricter rule already applies at
    the review gate (E11, `code-review:96`).
  - The reviewer may prefer the stricter scan.
- **Q2: What if the user declines the history rewrite?** E8 step 4 keeps the PoC blocked, so the user's choice is
  approve or stop.
  - **Recorded alternative:** a revoked secret may stay in history under a user risk acceptance logged in the
    checkpoint.
  - **Not taken.** `:153` allows no "runtime decision" to override Constraint 1, and I will not invent a waiver.
  - If the reviewer reads a user's decision as outside "runtime decision", a v2 can add the acceptance path.
- **Q3: Is a hardcoded secret that was never committed always at least `SECURITY:HIGH`?** §5 treats it as blocking.
  Should E8 state this case explicitly?

## 10. Corrections to the brief (`unclear_requirements`, all `minor`)

- **C1: `poc-security-engineer` is `beta`, not `stable`.** Brief §1 and §2 (every row for that file) say "stable". On
  `e1feee4` the file reads `maturity: beta` (`:6`), set by the scoping MR `416b734`, which plan-099 §1 describes.
  §2's facts were verified on `81921f7`, before that MR. Every cited line number still matches on `e1feee4`.
- **C2: `poc-orchestrator.md:66` uses double quotes.** Brief §2 quotes it as `'Optimize for demo speed, not
  production quality'`. The source reads `"Optimize for demo speed, not production quality"`. This matters for exact
  `Before:` matching, and E9 uses the source form.
- **C3: `rapid-prototyping:61` already blocks some of what the reviewer asked about.** The review cited the pre-T575
  `:54` ("🟡 Should Fix"). Post-T575 `:61` already makes a "security issue" shortcut 🔴 Must Fix, which is "Block
  merge" (`code-review:96`). The residual gaps are tagged removals, the undefined scope of "security issue", and the
  debt-ledger route (§4). Separately, brief §2 says "Nothing anywhere says that a *critical* finding blocks". That is
  true of the two agents, but not of the PoC track as a whole, because of this path.
- **C4: two sites are touched that §2 does not list.**
  - `poc-orchestrator.md:49` (E6), for brief §3 item 4's "earlier".
  - The insertion point between `:58` and `:60` (E8), which holds the routing and procedure that items 2–5 require.
  - Brief §2 also lists `security-guidelines.md:151–160`; it is ruled **unchanged**, as authority only.
- **C5: the worktree is at `e1feee4`, not the brief's `81921f7`.** The intervening commits are `416b734` (scoping,
  maturity line) and the T576 merge. That nothing else in the three target files changed is **(unverified)**, but
  every line I cite matches the brief's text.

## 11. Unverified claims (need a shell)

1. No golden case asserts the content of `poc-security-engineer.md` or `poc-orchestrator.md`, or of
   `rapid-prototyping:61` (§7; search list given there).
2. The registry carries the agent `description` (§7).
3. The root-projection count of 21 paths, net of T577 (§7).
4. No live (non-immutable) file cites `poc-orchestrator.md` line numbers (§7).
5. How `check-maturity` reads `Affects`, and therefore whether declaring `agent/poc-orchestrator` on a P1 row would
   fail it (§7). This comes from plan-099 §1's description only.
6. No other test asserts text in the three files (for example description length or Rails format). I read only
   `test_agent_escalation_consistency.py`.
7. `e1feee4` differs from `81921f7` in the three target files only at `poc-security-engineer.md:6` (C5).
8. The hosting platform keeps copies outside a rewrite (merge-request refs, CI logs). This is general knowledge; I
   fetched no GitLab documentation (§5).
9. No other knowledge file outside the files read here routes security findings to debt. A sweep for `debt handoff`,
   `without blocking` and `non-critical` under `implementation/knowledge/` is needed.

## 12. Findings outside scope (not ruled; candidates for parking)

- **X1: no pre-commit secret scanning.** Only a hook stops a commit. Every agent-level check, E6 included, runs after
  a commit. This is a tooling choice for `scaffolding-agent` or `poc-devops-engineer` (which tool, and whether a hook
  in a PoC template conflicts with "non-essential tooling", `scaffolding-agent.md:19`).
- **X2: "prefer unblocking over perfection" in eleven other PoC agents' Blocker Reporting.** I read it in
  `poc-qa-engineer:36`, `technical-debt-narrator:36`, `integration-agent:39`, `scaffolding-agent:34` and
  `poc-devops-engineer:33`. The rest are **(unverified)**. It is harmless for their own blockers, but nothing ties it
  to security. E9's speed directive exception reaches them through every brief, so no edit is compelled.
- **X3: `integration-agent.md:22` and `:50`.** `:22` says "Explicitly label … unresolved security/reliability gaps",
  which is a labelling route that could read as debt. `:50` puts "secrets rotation" out of scope as
  production-hardening. Routine rotation policy is different from incident rotation (E8 step 1, a user action), but
  the wording could confuse. Clarification is a candidate.
- **X4: the security scan's scope against Security Review Workflow step 1.** Step 1 says "Run OWASP Top 10 checklist
  against every merge request touching security-sensitive code". The PoC agent's Rails exclude "a full OWASP-style
  audit". These are not reconciled here, and the reviewer's fix direction did not raise it.
- **X5: `poc-security-engineer` has the `execute` tool.** E2 and E4 forbid it from rotating credentials or rewriting
  history, but the tool would allow `git` writes. Trimming tools is a separate decision.
- **X6: no residual-risk path in `security-guidelines` for a revoked secret that cannot be purged** (for example one
  pushed to a public fork). This is for the instruction's owner (see §9 Q2).

## 13. Blockers

**None.** No part of this ruling needs an agent ranking (§1.3), so no P34b `dependency` blocker is raised. The §9
questions are review decisions, not blockers.

## 14. Summary

| Site | Ruling | Edit | Authority |
|---|---|---|---|
| `poc-security-engineer:3` description | "Without blocking" → blocks on critical, high and constraint breaches | E1 | `security-guidelines:22–24`, `:153`, `:155` |
| `poc-security-engineer:18–20` Behavior | Grade on the SECURITY scale; block on breach, CRITICAL or HIGH (never debt); MEDIUM gets a plan; LOW goes to debt; secret not cleared by deletion; verdict | E2 | `:153`, `:155`, `:181–184`; `AGENTS.md` § Validation Gates |
| `poc-security-engineer:35` Blocker Reporting | Qualified; `:36` escalation sentence kept verbatim | E3 | as E2; mechanical test |
| `poc-security-engineer:46` Rails, Out of scope | "non-critical" → MEDIUM/LOW; no rotation or rewrite | E4 | `:183`; Safety Guards |
| `poc-security-engineer:47` Rails, Failure mode | Debt handoff → blocker plus `FAIL` | E5 | as E2 |
| `poc-orchestrator:49` | Secrets check before the first push or merge of steps 4/5/7 | E6 | `:155`; Safety Guards (cheaper clean-up before a push) |
| `poc-orchestrator:53` step 9 | "critical risks only" → high-risk, blocking stops the PoC | E7 | `:183` |
| `poc-orchestrator` new § Security Findings | Routing, procedure, no waiver by speed, timebox or tokens | E8 | §1.1 in full |
| `poc-orchestrator:66` speed directive | Security exception | E9 | `security-guidelines:17–20`; `poc-orchestrator:73–76` |
| `poc-orchestrator:114` Constraints | DO NOT (MEDIUM/LOW) plus DO (block) | E10 | `:183–184` |
| `rapid-prototyping:61` Enforcement | Tagged or untagged removal or breach is 🔴, blocks, never open debt; secret goes to the orchestrator | E11 | `:17–20`; `code-review:96`; T576 R6 |
| `security-guidelines.md` | Unchanged | — | — |
| MEDIUM | Plan required before merge, non-blocking, tracked condition | E2, E8, E10 | `:23–24`, `:183`; `AGENTS.md` |
