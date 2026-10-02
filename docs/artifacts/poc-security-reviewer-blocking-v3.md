# Artifact: poc-security-reviewer-blocking-v3.md

> Filename: `poc-security-reviewer-blocking-v3.md`. Immutable once produced; revisions bump `<N>`.

## Metadata

- **Producer agent**: solution-architect
- **Task**: T578 (P1, O1, SECURITY:HIGH), third revision
- **Created**: 2026-10-02
- **Based on**:
  - `docs/artifacts/poc-security-reviewer-blocking-v2.md` (superseded by this version) and, through it, v1;
  - the Security Engineer's **delta re-review of v2, CONDITIONAL_PASS**. It found every v1 condition met (M3 and M5 by
    accepted equivalents), with one new MEDIUM item (R2-6) and seven LOW items (R2-1 … R2-5, R2-7, R2-8). The
    orchestrator relayed it with exact After texts and stated: "the reviewer said no re-review is needed if you
    [adopt them verbatim]". I did not read the review record itself;
  - the orchestrator's own check of v2 ("complete and correct");
  - **user decisions of 2026-10-02**, all relayed verbatim by the orchestrator:
    - on v1 Q2: **"Allow, with strict conditions (Recommended)"**;
    - on the R2-6 disclosure: **"Accept the presence check (Recommended)"**;
    - on QD: **"No, keep it strict (Recommended)"**;
  - the orchestrator's correction: `rapid-prototyping/SKILL.md` was edited by T577 (MR !474, `develop` `0a61c4c`)
    after `e1feee4`. The orchestrator ran E11's Before text against post-T577 `develop` and it matched exactly once.
    `poc-security-engineer.md` and `poc-orchestrator.md` are unchanged since `e1feee4`;
  - the inputs listed in v1 and v2: `task-T578.md`, plan-099, the first Security review § O1,
    `poc-security-shortcut-examples-v2.md`, `poc-skills-alignment-v1.md` §10.2, `poc-contract-resolution-v1.md` §9.2,
    and ADR-007 (Accepted; not used to rank agents);
  - for R2-8, `https://docs.gitlab.com/user/project/repository/repository_size/`, which I fetched (§11 #7).
- **Supersedes**: `poc-security-reviewer-blocking-v2.md`. v1 and v2 stay unchanged as the historical record. **Where
  they differ, v3 governs. FU-1 applies v3 only.**
- **Decision references**: O1 / plan-099; the three user decisions (§1.4). No new ADR is minted. No P34b ranking is
  used.

## 0. What this document is, and what it did not do

This is the complete, standalone ruling, with exact edits for FU-1. It incorporates both Security reviews and all three
user decisions. §15 lists every v2→v3 change. **It changed no agent, skill, command, instruction or golden case.**

**Method and limits.**
- **No shell:** claims that need one are marked **(unverified)** (§11).
- **No golden access:** I opened nothing under `tests/golden/`.
- **Apply by text:** apply each edit by its exact `Before:` text, never by line number. Line numbers are at `e1feee4`.
- **Before texts:** every `Before:` that existed in v1 or v2 is byte-identical here. The only new one is E2a, which
  the reviewer supplied.
- **Uniqueness:** in the two agent files, each Before was unique when I read them in full at `e1feee4`, and the
  orchestrator states they are unchanged since. In `rapid-prototyping`, my copy is pre-T577. The orchestrator
  confirmed E11's Before matches exactly once on post-T577 `develop`.
- **Characters:** `—` is U+2014.
- **Verbatim adoption:** every reviewer After text in this round is adopted verbatim. Text carried over from v2 that is
  not a reviewer wording is marked as v2's.

## 1. Authority basis

### 1.1 The quoted texts

**`security-guidelines.md`** (`maturity: stable`, `applyTo: "**"`):
- **Rails `:15–20`:** it does not grant any agent authority to disable a security control "'temporarily,' even in PoC
  or development mode — the Immutable Security Constraints section forbids that outright, superseding any
  speed-over-completeness pressure from `poc-guidelines.md`".
- **Rails `:22–24`:** CRITICAL/HIGH "block merge … until resolved"; MEDIUM "require a documented remediation plan
  before merge".
- **Secrets Management `:73`:** "Audit secret access".
- **Agent Safety Guards:**
  - `:117–118`: "hard blocks unless the user explicitly approves in the current session";
  - `:122`: "Never run or suggest without explicit user approval";
  - `:126`: `git push --force`;
  - `:128`: history rewrite;
  - `:134`: "Do not read, cat, or copy: `.env`, … `*.key`";
  - `:135`: "Do not paste secret values into chat, handoffs, checkpoints, or commits";
  - `:136`: "reference **names only**".
- **Immutable Security Constraints:**
  - `:153`: "absolute and cannot be overridden by any agent, configuration, or runtime decision";
  - `:155`, Constraint 1: "… not negotiable regardless of PoC status";
  - `:156`, Constraint 2 (PII).
- **Security Review Workflow:** `:181` (the four grades); `:182` "`CRITICAL` and `HIGH` findings block merge until
  resolved"; `:183` MEDIUM remediation plan; `:184` LOW tracked as debt.

**`poc-guidelines.md`** (`stable`, `applyTo: "**"`):
- Rails `:10–13`: "a PoC specialist agent";
- Rails `:17–19`: "Does not waive the Immutable Security Constraints";
- Rule 3 (`:55`).

**`poc-orchestrator.md:73–76`** (`stable`): "every delegation this agent issues is governed by that instruction".

**`AGENTS.md`:** § Validation Gates ("`FAIL` blocks progression"; "`CONDITIONAL_PASS` proceeds with tracked conditions
added to the task list"; "Review agents … MUST NOT modify code during review"), § Blocker Protocol ("Max 2 retries
before user escalation"), and § Task Protocol ("Only orchestrators create/transition tasks").

**`git-workflow.md`** Rails: no agent has "authority to bypass branch protection for any reason".

### 1.2 Reading

**The two agents.** Recording a committed secret, or a missing, removed or weakened control, "for debt handoff" is an
agent's runtime decision to leave a breach in place. That contradicts `:153` and Rails `:17–20`. The instruction
asserts its precedence by name, including over PoC speed. Neither agent claims an exemption, and `poc-guidelines`
concedes the point (`:17–19`). One side asserts and the other does not contest, so **no ranking is needed**
(`poc-security-shortcut-examples-v2.md` §1.2).

Each agent is also within the instruction's reach in its own terms:
- `poc-orchestrator` through `:73–76`;
- `poc-security-engineer` through `poc-guidelines:10–13`, and through its place in `poc-orchestrator`'s roster (`:5`).

The precedent is FU-C (`poc-contract-resolution-v1.md` §9.2), building on T542.

**The blocking class covers omitted controls at any severity (M1).** The same Rails sentence denies any agent authority
to disable "a security control … even in PoC or development mode". A required control that is omitted, removed,
disabled or weakened is a disabled control. `poc-security-shortcut-examples-v2.md` §13.2 accepted this reading of the
Rails' scope.

**The presence check (E2a, R2-6)** follows from that class. A reviewer cannot block on a missing control it never
looks for. E2a stays inside the agent's Rails ("not a full OWASP-style audit").

**The skill.** `poc-skills-alignment-v1.md` §10.2 extended the precedent to these PoC skills.

### 1.3 The secret procedure: content and routing

**Content.** Revoke, audit logs, copy inventory, GitLab purge, and history removal. Constraint 1 does not prescribe a
remedy, so the content rests on:
- the Security Engineer's fix direction and conditions (O1, M4, M5, R2-1, R2-8);
- plan-099 §2, which the user approved;
- `:73`.

**Routing.** Every destructive step goes through the user, under Safety Guards `:117–128` and the `git-workflow` Rails.

### 1.4 User decisions (2026-10-02, relayed verbatim)

| Question | Decision | Authority for |
|---|---|---|
| May a user who declines the history rewrite close the finding? | **"Allow, with strict conditions (Recommended)"** | E8 step 4's declined path; E2's reference to it |
| "PoCs will block noticeably more often. Accept that?" (the R2-6 disclosure) | **"Accept the presence check (Recommended)"** | E2a, and its consequence that PoCs block more often |
| QD: may a committed secret that only ever authenticated an ephemeral local instance satisfy (b) without logs? | **"No, keep it strict (Recommended)"** | E8 step 4 condition (b) with no exception |

These are user decisions, not an agent's runtime decision under `:153`. The declined path's conditions mean that what
stays in history is a value that works nowhere, shows no unrecognised use in available logs, and is not key material.

### 1.5 Does anything need a P34b ranking? **No.**

No `dependency` blocker is raised.

## 2. `poc-security-engineer.md` (held at `beta` while the P1 row is open)

### E1: `:3`, description

````
Before:
description: "Use for lightweight PoC security review that flags critical risks without blocking rapid validation."

After:
description: "Use for lightweight PoC security review. Flags high-risk issues, and blocks the PoC on critical or high findings, on any omitted, removed or weakened security control, and on any Immutable Security Constraint breach, such as an exposed secret."
````

**Source:** R2-5, verbatim. **Authority:** `:17–20`, `:22–24`, `:153`, `:155`. Delegation is driven by
`description`.

### E2a: `:16`, § Scope (new in v3)

````
Before:
- Identify major auth or injection concerns

After:
- Identify major auth or injection concerns
- Check that the security controls `security-guidelines.md` requires for the code the PoC actually contains are present and enforced (for example authentication and authorization on endpoints that handle non-public data, input validation at system boundaries, parameterized queries, secrets read from the environment, TLS for external and database connections). This is a presence check, not a full OWASP-style audit
````

**Source:** R2-6, verbatim.

**Authority:**
- `security-guidelines:17–20` (§1.2).
- The **user's decision "Accept the presence check (Recommended)"** (§1.4) is the authority for the disclosed
  consequence that PoCs will block noticeably more often.

**Placement:** the Before line (`:16`) is unique in the file. It does not overlap E2's Before, which starts at `:18`
`## Behavior`.

### E2: `:18–20`, § Behavior

````
Before:
## Behavior
- Do not block progress by default
- Record findings for debt handoff

After:
## Behavior
- Grade every finding `SECURITY:CRITICAL`, `SECURITY:HIGH`, `SECURITY:MEDIUM` or `SECURITY:LOW`, as in `security-guidelines.md` § Security Review Workflow
- **Severity floor:** never grade any of these below `SECURITY:HIGH`: a real credential in code or configuration, committed or not; an injection path (SQL, command, template or similar) reachable from external input; a missing or bypassable authentication or authorization check on an endpoint that handles non-public data. A placeholder that cannot authenticate anywhere (for example `<set-me>` or a `${VAR}` reference) is not a secret
- **Blocking findings:** any breach of an Immutable Security Constraint in `security-guidelines.md` (for example a committed secret, or real PII in demo data); any security control that `security-guidelines.md` requires for the code in question and that is omitted, removed, disabled or weakened, tagged or not, whatever its severity (`security-guidelines.md` Rails: no authority to disable a security control "even in PoC or development mode"); and any `SECURITY:CRITICAL` or `SECURITY:HIGH` finding. Report each one to the PoC orchestrator as a blocker. A blocking finding is never recorded for debt handoff, and it stays open until its fix is re-checked and confirmed
- **Non-blocking findings:** do not block progress on any other `SECURITY:MEDIUM` or `SECURITY:LOW` finding. Give each `SECURITY:MEDIUM` finding a remediation plan (owner, fix, deadline no later than the production handoff), which must exist before the affected work merges. Record `SECURITY:LOW` findings for debt handoff
- **Exposed secret:** report the file, line, commits, whether they were pushed, the credential's type and issuer, and the environment variable that should replace it. Never reproduce the value, including in a search pattern or any other tool argument; scan by pattern, with redacted output. Deleting the secret from the code does not resolve the finding. It stays open until the user confirms the secret is revoked (the old value no longer works), the code reads it from the environment or a secret vault, and the secret is removed from git history with the user's explicit approval, or declined under the conditions in `poc-orchestrator` § Security Findings, which also covers a secret not yet committed. Never revoke or rotate credentials, rewrite history or force-push yourself
- End every scan with a verdict (`AGENTS.md` § Validation Gates): `FAIL` while any blocking finding is open, `CONDITIONAL_PASS` if `SECURITY:MEDIUM` findings remain with their remediation plans, otherwise `PASS`
````

**Sources:**
- Grading and verdict bullets: v2.
- Severity floor: M2.
- Blocking findings: M1.
- Non-blocking findings: M1 and L5.
- Exposed secret: v2's text, accepted in the delta review, with R2-4's "scan by pattern, with redacted output",
  verbatim.

**Authority:** `:17–20`, `:134–135`, `:153–156`, `:181–184`; `AGENTS.md` § Validation Gates; user decision (§1.4) for
the declined path.

### E3: `:35`, § Blocker Reporting step 3 (escalation sentence preserved)

````
Before:
3. Suggest a workaround — PoC speed matters, prefer unblocking over perfection

After:
3. Suggest a workaround — PoC speed matters, prefer unblocking over perfection. A blocking finding (§ Behavior) has no workaround: name the fix it needs instead
````

**Mechanical constraint.** `:36` "4. The PoC orchestrator will handle escalation" is in no `Before:` text and stays
byte-identical. `test_agent_escalation_consistency.py:102–110` asserts it.

### E4: `:46`, Rails, Out of scope

````
Before:
**Out of scope**: Blocking PoC progress on non-critical findings; performing a full OWASP-style audit.

After:
**Out of scope**: Blocking PoC progress on `SECURITY:MEDIUM` or `SECURITY:LOW` findings outside the blocking classes in § Behavior; performing a full OWASP-style audit; revoking or rotating credentials, or rewriting git history (§ Behavior).
````

**Source:** R2-5's first clause, verbatim; the rest is v2. **Authority:** `:182` (HIGH blocks, so "non-critical" was
ambiguous); M1.

### E5: `:47`, Rails, Failure mode

````
Before:
**Failure mode**: If a critical risk (exposed secret, obvious injection/auth gap) is found, records it explicitly for debt handoff rather than silently omitting it to avoid blocking progress.

After:
**Failure mode**: If a blocking finding is found (an exposed secret, an obvious injection or authorization gap, any omitted, removed, disabled or weakened security control, any other `SECURITY:CRITICAL` or `SECURITY:HIGH` finding, or any Immutable Security Constraint breach), reports it to the PoC orchestrator as a blocker and returns `FAIL`, rather than recording it for debt handoff or omitting it to avoid blocking progress.
````

**Unchanged in this file:** everything not named in E1, E2a and E2–E5, including `:6` `maturity: beta` (FU-2) and
`:14–15`.

## 3. `poc-orchestrator.md` (stable, and stays stable; §7)

### E6: `:49`, the secrets check

````
Before:
5. **Integration** — `@integration-agent`: third-party API/SDK wiring (parallel with scaffolding if independent)

After:
5. **Integration** — `@integration-agent`: third-party API/SDK wiring (parallel with scaffolding if independent)
   - **Secrets check** — `@poc-security-engineer`: before every push that carries a delegated agent's commits not yet checked, and before every merge, at any step (including steps 10, 13 and 14, which run after step 9), check the change for committed secrets, hardcoded credentials, tracked secret-bearing files (identified by name, never opened) and real PII. A finding blocks (§ Security Findings). Neither this check nor step 9 is ever dropped to reduce scope, time or tokens
````

**Source:** R2-3, verbatim. It closes v2's "first push" gap, where later pushes of the same agent's work went
unchecked. The `**Secrets check**` literal is kept.

**Authority:** `:134`, `:155–156`; "never dropped" closes the route through the token Failure mode (`:107`).

**Recorded alternatives:** moving step 9 earlier (not taken: it must see step 7), and a pre-commit hook (parked, §12
X1).

**Tests:** the added mention is registered and in the roster, so `test_workflow_*` should stay green **(reasoned, not
run)**.

### E7: `:53`, step 9

````
Before:
9. **Security Scan** — `@poc-security-engineer`: critical risks only

After:
9. **Security Scan** — `@poc-security-engineer`: high-risk issues, not a full audit. Blocking findings stop the PoC (§ Security Findings)
````

**Authority:** `security-guidelines:182`.

### E8: new `## Security Findings` section, between § PoC Workflow and § Delegation Brief

````
Before:
14. **DevOps** — `@poc-devops-engineer`: fast local reproducibility

## Delegation Brief (PoC-Adapted)

After:
14. **DevOps** — `@poc-devops-engineer`: fast local reproducibility

## Security Findings

`security-guidelines.md` applies to PoC work in full. Its Rails withhold authority to disable a security control "even in PoC or development mode", its Immutable Security Constraints "cannot be overridden by any agent, configuration, or runtime decision", and `poc-guidelines.md` "Does not waive the Immutable Security Constraints". Route `@poc-security-engineer`'s findings as its § Behavior grades them, per `security-guidelines.md` § Security Review Workflow:

- **Blocking** (any Immutable Security Constraint breach; any required security control omitted, removed, disabled or weakened, tagged or not; any `SECURITY:CRITICAL` or `SECURITY:HIGH` finding): set the affected task to `blocked`, stop every delegation except the remediation, record the blocker in the next checkpoint, and tell the user. Delegate the fix, then have `@poc-security-engineer` re-check it. Apart from the timebox verdict below, the PoC does not continue, demo, evaluate or close until the re-check confirms the finding is resolved. Never record a blocking finding as debt. The speed directive, the timebox and the token envelope do not waive it. If two remediation cycles fail, escalate to the user (`AGENTS.md` § Blocker Protocol). Stopping, cancelling or timing out the PoC does not resolve a blocking finding. Before the PoC's tasks are archived, create a separate task for each open blocking finding, with status `blocked`. Give it priority `P1` or higher. Its owner is `poc-orchestrator` while the finding awaits the user's step 1, with "awaiting user: step 1" in the title, and the remediating agent otherwise. That task stays in `active-tasks.md` until `@poc-security-engineer` confirms the finding resolved. If the timebox expires, record the verdict `poc-guidelines.md` Rule 3 requires, but do not close the PoC. Escalation after two failed cycles asks the user to direct further remediation or to stop; it never turns the finding into debt.
- **Other `SECURITY:MEDIUM` findings**: do not block. Before the affected work merges, add the remediation plan (owner, fix, deadline no later than the production handoff) to the task list as a tracked condition (`AGENTS.md` § Validation Gates), and carry it into the debt handoff.
- **Other `SECURITY:LOW` findings**: record for debt handoff.

**Exposed secret.** Deleting a secret from the code does not resolve it: it stays in git history, and it is exposed from the moment an agent can read it. Never copy its value into chat, a brief, report, checkpoint, handoff, commit, issue, merge request, or any tool or command argument (for example a search pattern); refer to it by file, commit and environment-variable name only. Scan with pattern-based secret detection, never by its literal value, with the scanner's output redacted so that no value is printed. Identify committed secret files such as `.env` or `*.key` by name; do not open them (`security-guidelines.md` § Agent Safety Guards).

1. **Revoke — the user.** Ask the user to revoke the secret at its issuer (rotation counts only if the old value stops working), to set the replacement locally, and to review the issuer's access or audit logs for any use between first exposure and revocation (`security-guidelines.md` § Secrets Management, "Audit secret access"). If the logs show use the user does not recognise, it is an incident, not a PoC finding: tell the user and stop. If the secret is key material (an encryption, signing or TLS private key), name what it protected or signed, because revocation does not undo past use. No agent does this.
2. **Fix the code — a delegated agent.** Delegate the change that reads the secret from an environment variable or a secret vault, by name only, as a normal commit.
3. **Remove it from history — only with the user's approval.** Rewriting history is a destructive operation that agents "MUST treat … as hard blocks unless the user explicitly approves in the current session" (`security-guidelines.md` § Agent Safety Guards). Ask the user, naming the commits and branches affected. The rewrite happens only after that approval. On GitLab a rewrite and force-push is not enough. Commit content stays cached and visible, and merge-request and pipeline refs keep the old commits, until the project's sensitive-data removal is run: Remove blobs or Redact text (project Owner role), or Repository cleanup (Maintainer or Owner). For any pushed secret, the user performs step 3. For a secret only in local history, the user performs the rewrite or names the agent and the branches. No agent bypasses branch protection (`git-workflow.md`). List, by location only, every copy the project controls that may hold the secret (branches, tags, agent worktrees, CI job logs, artifacts and caches, images or packages built from the affected commits, merge-request diffs) and ask the user to delete or expire them. Deletion is destructive and is the user's to do. Copies no one here controls, such as other people's clones and forks, are why step 1 comes first.
4. **Resolve.** `@poc-security-engineer` confirms the finding resolved only when: the user has confirmed step 1, or, for a secret not yet committed, has confirmed the step 1 skip condition below; the step 2 fix is in place; a pattern-based secret scan of all branches and tags, never by the literal value, finds no occurrence (in their history, or only at their tips if step 3 was declined under the conditions below); and step 3 is done, declined under the conditions below, or not applicable because the secret was never committed. If the user explicitly declines step 3, the finding may be resolved as "revoked; retained in history by the user's decision" only if (a) the user has confirmed revocation, meaning the old value no longer works anywhere; (b) the audit-log review in step 1 found no unrecognised use (if the issuer keeps no access or audit logs, (b) is not met); and (c) the secret is not key material whose past use revocation cannot undo. Record the decision, the commits and the date in the finding's task and in the next checkpoint. It is never recorded as debt. Otherwise the finding stays open and the PoC stays blocked.

**A secret not yet committed** is still blocking (`SECURITY:HIGH` at least). It is one commit away from breaching Constraint 1, and its value has already passed through at least one agent's context. Steps 1, 2 and 4 apply; step 3 does not. Step 1 may be skipped only if the user confirms the value authenticates nowhere except an ephemeral local instance. For this case, the step 4 scan also covers the working tree, index and stashes of every worktree that held the value.

## Delegation Brief (PoC-Adapted)
````

**Sources, all verbatim:**

| Part | Source |
|---|---|
| Blocking parenthesis | M1 |
| Blocking body | v2 plus M3, with v2's accepted equivalent "Apart from the timebox verdict below,"; R2-7's priority and owner sentences |
| MEDIUM / LOW | L5, plus v2's accepted "Other …" labels |
| Secret paragraph | M2's first sentence; L3; R2-4's redaction clause |
| Step 1 | M4 |
| Step 3 | v2, plus M5 with R2-8's role wording, plus M4's inventory. v2's local-only route was accepted in the delta review. |
| Step 4 | R2-1's first sentence; R2-2's declined-path sentence; the closing sentences are the user-decision wording carried from v2 |
| Not-yet-committed paragraph | M2, plus R2-1's appended sentence |

**Authority:**
- §1.1; `:73`;
- `AGENTS.md` § Task Protocol (this agent is an orchestrator, so it creates the separate tasks);
- `poc-guidelines` Rule 3;
- the user decisions (§1.4): the declined path, and (b) with no exception for issuers that keep no logs (QD).

**QC, confirmed by the reviewer; no edit.** On timebox expiry the PoC stays open and `blocked`, and remediation may
continue. A stop triggers the separate-task rule.

**Note for the follow-up and for runtime (R2-7), outside the agent text.** A finding's separate task, at `P1` or
higher, also needs:
- a brief (`validate-tasks` C7, every ledger ID has a `task-<ID>.md`);
- an `**Affects:** —` line (C11, required at P0/P1).

C7 is quoted in `poc-skills-alignment-v1.md` §1.3. C11 comes from the reviewer, and I have not seen its code
**(unverified)**.

The reviewer gave no After wording for this note, so it is **not** added to E8, to keep the After texts verbatim. If
the orchestrator wants it in the agent itself, a sentence for the end of the Blocking bullet would be: "Write its brief
and an `**Affects:** —` line, as `validate-tasks` requires at `P0`/`P1`." That would be the orchestrator's call, and the
reviewer would need to see it.

**Placement is test-safe.** The workflow regex `## PoC Workflow\n(.*?)\n## ` stops at `## Security Findings`.

### E9: `:66`, the speed directive

````
Before:
4. **Speed directive**: "Optimize for demo speed, not production quality"

After:
4. **Speed directive**: "Optimize for demo speed, not production quality. Security is the exception: simplify how a security control is built, but never omit, remove or weaken one the code needs, never commit a secret, never use real PII, and never breach any other Immutable Security Constraint (`security-guidelines.md`)."
````

**Source:** L2. **Authority:** `:17–20`, `:153–160`, `poc-orchestrator:73–76`.

### E10: `:114`, § Constraints

````
Before:
- **DO NOT** block on non-critical security findings — record for debt handoff

After:
- **DO NOT** block on other `SECURITY:MEDIUM` or `SECURITY:LOW` findings — a MEDIUM finding gets a remediation plan (owner, fix, deadline no later than the production handoff) before merge, a LOW finding is recorded for debt handoff (§ Security Findings)
- **DO** block on every Immutable Security Constraint breach, every required security control omitted, removed, disabled or weakened (tagged or not), and every `SECURITY:CRITICAL` or `SECURITY:HIGH` finding until it is resolved, and never hand one off as debt (§ Security Findings)
````

**Authority:** `:17–20`, `:182–184`.

**Unchanged in this file:** the frontmatter, the Rails `:103–107`, and everything not named in E6–E10.

## 4. `rapid-prototyping/SKILL.md` (experimental), "Enforcement" bullet (`:61` pre-T577)

**T577 has landed** (MR !474, `0a61c4c`). It changed the POC-DEBT example sites and added the pointer sentence
(T576 R6) above this bullet, so the bullet's line number has moved. **E11's Before is byte-identical to v1.** The
orchestrator confirmed it matches exactly once on post-T577 `develop`. Only the After differs from v1, as M7 specifies.

**Routes that remain open:**
- tagged shortcuts;
- omitted controls;
- the debt ledger (technical-debt-tracking Step 3; the `accepted-risk` status at `technical-debt-tracking:93`);
- the Tech Lead waiver at `code-review:150`.

### E11: append to the Enforcement bullet

````
Before:
- An untagged shortcut discovered during review is flagged as a review finding. The missing tag is a 🟡 Should Fix finding. The shortcut itself is graded like any other finding on the code-review skill's § Severity Guide, so a shortcut that is a bug, security issue or data loss risk is a 🔴 Must Fix finding. These labels grade review findings, not debt: the technical-debt-tracking skill assigns the debt severity when it merges the finding into the debt ledger (§ POC-DEBT Tag Scanning Procedure, Step 3).

After:
- An untagged shortcut discovered during review is flagged as a review finding. The missing tag is a 🟡 Should Fix finding. The shortcut itself is graded like any other finding on the code-review skill's § Severity Guide, so a shortcut that is a bug, security issue or data loss risk is a 🔴 Must Fix finding. These labels grade review findings, not debt: the technical-debt-tracking skill assigns the debt severity when it merges the finding into the debt ledger (§ POC-DEBT Tag Scanning Procedure, Step 3). Security is the exception: omitting, removing or weakening a security control that `security-guidelines.md` requires for the code in question, or breaching an Immutable Security Constraint in `security-guidelines.md`, is a 🔴 Must Fix finding whether or not it is tagged. It blocks until it is fixed. No Tech Lead waiver applies to it (`security-guidelines.md` Rails: no agent has authority to disable a security control "even in PoC or development mode"). It enters the debt ledger only as `resolved`, never as `open`, `in-progress` or `accepted-risk`. An exposed secret is not fixed by deleting it from the code: report it to the PoC orchestrator, which follows `poc-orchestrator` § Security Findings.
````

**Source:** M7. **Authority:** `:17–20`, `:153`, `:155`; T576 R6.

**This is no longer the only backstop.** After M1, R2-6 and E2a, the security scan looks for, and blocks on, the same
class.

## 5. The secret-exposure procedure: who does what

This summarises E2 and E8; their text is binding.

| # | Step | Actor | Agent alone? |
|---|---|---|---|
| 0 | Detect by pattern with redacted output; report location, commits, pushed or not, type, issuer and variable name, never the value. Verdict `FAIL`. | `poc-security-engineer` | Yes, read-only |
| 1 | Halt: task `blocked`, remediation only, blocker checkpointed, user told | `poc-orchestrator` | Yes |
| 2 | **Revoke** (the old value stops working), replacement set locally, **issuer audit-log review**, key material named. Unrecognised use is an incident: stop. | **User** | **No** |
| 3 | Code reads from env or vault, as a normal commit | Delegated write-capable agent | Yes |
| 4 | **History rewrite; GitLab sensitive-data removal** (Remove blobs or Redact text: Owner; Repository cleanup: Maintainer or Owner); **deletion of listed copies** | **User**, for anything pushed; for local-only history, the user or an agent the user names after approval | **No** |
| 5 | Re-check: pattern scan of all branches and tags (history, or tips on the declined path), plus the working tree, index and stashes for a never-committed secret | `poc-security-engineer` | Yes |
| 5′ | Declined rewrite: resolved only under (a) works nowhere, (b) logs show no unrecognised use, with no logs meaning not met, and (c) not key material; recorded, never debt | User decides; orchestrator records | **No** |
| — | Stop, cancel or timeout with the finding open: a separate `blocked` task at `P1` or higher, owned by `poc-orchestrator` ("awaiting user: step 1") or by the remediating agent, with a brief and `**Affects:** —` | `poc-orchestrator` | Yes |
| — | Never committed: no history step; revocation skippable only for an ephemeral local value the user vouches for | as above | — |

## 6. MEDIUM findings and the remediation plan: **required, non-blocking**

Any `SECURITY:MEDIUM` finding outside the blocking classes does not block. It must have a plan (**owner, fix, deadline
no later than the production handoff**) before the affected work merges. The plan is recorded as a tracked condition
(`CONDITIONAL_PASS`) and carried into the debt handoff.

**Authority:** `security-guidelines:23–24`, `:183`; `AGENTS.md` § Validation Gates; L5. LOW findings are "tracked as
technical debt" (`:184`).

## 7. Blast radius and golden coupling

| Neighbour | Effect |
|---|---|
| `security-guidelines.md`, `poc-guidelines.md`, `AGENTS.md`, commands | **Unchanged.** |
| `code-review:150` (waiver), `technical-debt-tracking:93` (`accepted-risk`) | **Unedited.** E11 closes both for security findings. These were the only related general routes in the orchestrator's sweep. A security carve-out in `code-review:150` is a candidate, not ruled (§12 X7). |
| Other PoC agents' "prefer unblocking over perfection" | Unchanged (§12 X2). |
| `test_agent_escalation_consistency.py` | Expected green **(reasoned, not run)**. |
| `test_check_maturity.py` snapshot | No change from FU-1. |
| **`Affects`** (settled) | **`agent/poc-security-engineer` only.** `poc-orchestrator` is edited but stays `stable`, per the user's P1 approval for "the agent". |
| Registry | Checksums for three files. E1 changes the `description` field **(that the registry carries it is unverified)**. |
| Mirrors and root projections | `make sync`. 3 files × 7 platforms. **T577 has landed**, so `rapid-prototyping`'s projection paths may already be in the `drift` list. Declare exactly what `--print-drift` reports, without duplicates **(count unverified)**. |
| `poc-orchestrator.md` line numbers | E6 and E8 shift lines after `:49` **(no live citation verified)**. |

**Golden coupling: (unverified), with no golden access.** The expected outcome is no grant, no fixture change and no
baseline change. The orchestrator should confirm by searching `tests/golden/` (with `held-out` pruned) for:
- `without blocking rapid validation`
- `Record findings for debt handoff`
- `records it explicitly for debt handoff`
- `critical risks only`
- `non-critical security findings`
- `Optimize for demo speed`
- `prefer unblocking over perfection`
- `Should Fix finding`
- `Identify major auth or injection concerns`

## 8. Follow-ups

| Step / task | Covers | Files | `tests/golden/**` grant? | Owner (suggested) | Priority | Depends on / verify |
|---|---|---|---|---|---|---|
| **FU-1**: apply O1 per **v3** | E1, E2a, E2–E11 | `implementation/knowledge/agents/poc-security-engineer.md` (E1, E2a, E2–E5); `…/agents/poc-orchestrator.md` (E6–E10); `…/skills/rapid-prototyping/SKILL.md` (E11); regenerated `implementation/.<platform>/` mirrors; `implementation/registry/index.json`; the `drift` list in `tests/_baselines/root-install-drift.json` | **No** (pending the §7 search) | Backend Developer (needs a shell) | P1 | **Affects:** `agent/poc-security-engineer` only. No re-review is needed: every reviewer After is adopted verbatim. **Verify:** see the list below. |
| **FU-2**: re-promote `poc-security-engineer` to `stable` | Maturity | `poc-security-engineer.md:6`; registry; `test_check_maturity.py` snapshot | No | Orchestrator scopes it | P2 | After FU-1 merges and the P1 row is archived. `check-maturity` 0 failing; nothing else in the file changed. |

**FU-1 verification:**
1. Each of the 12 `Before:` texts matches **exactly once by text** on `develop` at dispatch (post-T577).
2. `The PoC orchestrator will handle escalation` is still present in `poc-security-engineer.md`.
3. 0 hits under `implementation/knowledge/` for:
   - `without blocking rapid validation`
   - `Record findings for debt handoff`
   - `records it explicitly for debt handoff`
   - `critical risks only`
   - `block on non-critical security findings`
   - `Do not block progress by default`
4. 0 hits for `as open debt` in `rapid-prototyping/SKILL.md`.
5. Exactly 1 hit each for:
   - in `rapid-prototyping/SKILL.md`: `accepted-risk`, `Security is the exception:`;
   - in `poc-security-engineer.md`: `Severity floor`, `This is a presence check`, `has no workaround`;
   - in `poc-orchestrator.md`: `## Security Findings`, `**Secrets check**`, `A secret not yet committed`,
     `awaiting user: step 1`, `Security is the exception:`.
6. Grep live files (not `docs/artifacts/`) for stale `poc-orchestrator.md:` citations, and report them.
7. `sync.mjs --check` and `generate-registry.py --check` are clean. The root parity gate is green, declaring exactly
   what `--print-drift` reports, without duplicating T577's entries.
8. `security-guidelines.md`, `poc-guidelines.md`, `commands/` and `tests/golden/**` are byte-unchanged.
9. `check-maturity.py --root implementation`: 0 failing; `poc-security-engineer` is `beta`; `poc-orchestrator` is
   `stable`.
10. `scorecard.py --check` is unchanged against the current baseline.
11. `python3 docs/tasks/validate-tasks.py` passes.
12. `python3 tests/run.py`: exit code checked, output redirected to a file.

**Release note (plan-099 §3) unchanged:** no release ships the current text until FU-1 merges.

## 9. Review questions: all settled

| Question | Settled by |
|---|---|
| v1 Q1: should the scan block on omitted or weakened controls? | M1 (yes, any severity) |
| v1 Q2: may a user who declines the rewrite close the finding? | User: "Allow, with strict conditions (Recommended)"; R2-2 tightened the conditions |
| v1 Q3: is a never-committed secret blocking? | M2 (yes; severity floor) |
| v2 QA: does the agent's Scope match its blocking class? | R2-6 (E2a presence check); user: "Accept the presence check (Recommended)" |
| v2 QB: may "the user" own a task? | R2-7 (owner `poc-orchestrator`, "awaiting user: step 1") |
| v2 QC: what happens on timebox expiry? | Reviewer confirmed v2's reading; no edit |
| QD: is there an ephemeral-local exception to (b)? | User: "No, keep it strict (Recommended)" |

**Open:** none.

## 10. Corrections

**To the brief** (`unclear_requirements`, `minor`; unchanged from v2):
- **C1:** `poc-security-engineer` is `beta` (`:6`, `416b734`), not "stable".
- **C2:** `poc-orchestrator.md:66` uses double quotes in the source.
- **C3:** `rapid-prototyping`'s Enforcement bullet already blocked a "security issue" via `code-review:96` after T575.
- **C4:** E6 and the E8 insertion point, and in v3 also E2a, are outside §2's site list.
- **C5:** the facts were verified on `81921f7`; the worktree was at `e1feee4`.

**To v2 (from the orchestrator's correction):**
- **C6:** v2's Metadata and §11 #6 relayed that "the three target files are unchanged on `develop` `c523415`". That is
  wrong for `rapid-prototyping/SKILL.md`, which T577 edited at `0a61c4c`.
- **Consequence:** none for the edit. E11's Before is byte-identical to v1 and matches exactly once on post-T577
  `develop`, per the orchestrator's run. v2 §4's "concurrency" note is now historical: T577 has landed, so FU-1
  applies after it.

## 11. Unverified claims (need a shell)

1. No golden case asserts the content of the target sites (§7 search list).
2. The registry carries the agent `description`.
3. The root-projection count, net of T577's existing declarations.
4. No live file cites `poc-orchestrator.md` line numbers.
5. No other test asserts text in these files. I read only `test_agent_escalation_consistency.py`.
6. **Settled by the orchestrator:**
   - the two agent files are unchanged since `e1feee4`;
   - E11's Before matches once on post-T577 `develop`;
   - `rapid-prototyping`'s E2a-style uniqueness does not arise, since E11 is the only edit there.
7. **GitLab facts in E8 step 3, partly verified.** I fetched the cited page
   (`docs.gitlab.com/user/project/repository/repository_size/`):
   - **Confirmed:**
     - "Information about commits, including file content, is cached in the database, and remains visible even
       after they have been removed from the repository";
     - Owner role for Remove blobs and for Redact text.
   - **Partly confirmed:** "Maintainer or Owner" for Repository cleanup. The page states it as a prerequisite in that
     context, but my fetch tool's summary did not show the cleanup section restating it.
   - **Not confirmed on that page:** "merge-request and pipeline refs keep the old commits". The page, as summarised
     to me, warns that open merge requests may fail to merge and that pipelines referencing old SHAs may break.
   - **Assessment:** the wording is adopted verbatim and its direction (do the purge) is safe. The refs clause rests
     on the reviewer.
8. `validate-tasks` C11 ("`**Affects:**` required at P0/P1") is the reviewer's citation. I have not read that check's
   code.
9. **Settled by the orchestrator:** nothing outside the three files routes security findings to debt, except
   `code-review:150` and `technical-debt-tracking:93`, which E11 closes for security findings.
10. I did not read either review record. v2 and v3 follow the orchestrator's relays.

## 12. Findings outside scope (not ruled; candidates for parking)

- **X1:** there is no pre-commit secret-scanning hook. This is a tooling choice for `scaffolding-agent` or
  `poc-devops-engineer`.
- **X2:** "prefer unblocking over perfection" appears in eleven other PoC agents. E9 reaches them through every brief.
- **X3:** `integration-agent.md:22` ("label … unresolved security/reliability gaps") and `:50` ("secrets rotation" out
  of scope) could use clarifying in light of E8 step 1.
- **X4:** the scan's scope against Security Review Workflow step 1 (the OWASP checklist on every security-sensitive
  MR). E2a narrows the gap with a presence check but deliberately stops short of a full audit.
- **X5 (L4, parked):** replace `poc-security-engineer`'s `execute` tool with a fixed-command scanner.
- **X6:** `security-guidelines` defines no residual-risk path for a revoked secret that stays in history. The user's
  decision fills it for the PoC track only.
- **X7:** `code-review:150`'s Tech Lead waiver is a candidate for a matching security carve-out in the code-review
  skill itself.
- **X8 (new):** the separate finding tasks need a brief and `**Affects:** —` (§3, R2-7 note). Whether to say so inside
  `poc-orchestrator` is left to the orchestrator.

## 13. Blockers

**None.** No P34b ranking is needed.

## 14. Summary

| Site | Ruling | Edit | Authority |
|---|---|---|---|
| `poc-security-engineer:3` | Blocks on critical/high, omitted/removed/weakened controls, and constraint breaches | E1 | `:17–20`, `:22–24`, `:153`, `:155` |
| `poc-security-engineer:16` Scope | Presence check of required controls, not a full audit | E2a | `:17–20`; user decision |
| `poc-security-engineer:18–20` | Grade; severity floor; three blocking classes (never debt); MEDIUM plan with a deadline at or before handoff; LOW to debt; secret rules with redacted scanning and the declined path; verdict | E2 | `:17–20`, `:134–135`, `:153–156`, `:181–184`; `AGENTS.md`; user decision |
| `poc-security-engineer:35` | Qualified; `:36` kept verbatim | E3 | mechanical test |
| `poc-security-engineer:46` | MEDIUM/LOW outside the blocking classes; no rotation or rewrite | E4 | `:182` |
| `poc-security-engineer:47` | Blocker plus `FAIL` | E5 | as E2 |
| `poc-orchestrator:49` | Secrets/PII check before every push of unchecked commits and every merge; never dropped | E6 | `:134`, `:155–156` |
| `poc-orchestrator:53` | High-risk issues; blocking stops the PoC | E7 | `:182` |
| `poc-orchestrator` § Security Findings | Routing; separate `P1`+ task that survives stop, cancel or timeout; revoke plus audit; inventory; GitLab purge with roles; redacted pattern re-scan; strict declined path; not-yet-committed incl. worktrees and stashes | E8 | §1.1; user decisions |
| `poc-orchestrator:66` | Security exception | E9 | `:17–20`, `:153–160` |
| `poc-orchestrator:114` | DO NOT / DO | E10 | `:17–20`, `:182–184` |
| `rapid-prototyping` Enforcement | 🔴 tagged or not, omitted included; no waiver; ledger only as `resolved` | E11 | `:17–20`, `:153`, `:155` |
| `Affects` | `agent/poc-security-engineer` only; `poc-orchestrator` stays `stable` | — | orchestrator, per the user's P1 approval |

## 15. Change log v2 → v3

| Item | Severity / source | v3 change | Where | Verbatim? |
|---|---|---|---|---|
| **R2-6**: presence check | MEDIUM | New edit **E2a** in § Scope. New FU-1 check: exactly 1 hit for `This is a presence check`. v2 QA settled. | E2a, §8, §9 | Yes |
| User decision on R2-6 ("Accept the presence check (Recommended)") | User | Recorded as authority for E2a's consequence (PoCs block more often). | §1.4, E2a | Quoted verbatim |
| **R2-1**: step 4 for never-committed secrets | LOW | Step 4's first sentence replaced. Working tree, index and stashes sentence appended to the not-yet-committed paragraph. | E8 | Yes |
| **R2-2**: strict declined path | LOW | Declined-path sentence replaced: "explicitly declines", "works anywhere", "no logs → (b) not met". | E8 | Yes |
| User decision on QD ("No, keep it strict (Recommended)") | User | Recorded. (b) is kept with no ephemeral-local exception. | §1.4, §9 | Quoted verbatim |
| **R2-3**: secrets check before every push of unchecked commits | LOW | E6's After replaced; `**Secrets check**` literal kept. | E6 | Yes |
| **R2-4**: redacted scanner output | LOW | E8 sentence extended. E2's mirror becomes "scan by pattern, with redacted output". | E8, E2 | Yes |
| **R2-5**: "omitted" in E1; E4's first clause | LOW | E1's After replaced; E4's first clause replaced. | E1, E4 | Yes |
| **R2-7**: finding task priority and owner | LOW | Owner sentence replaced with the `P1`+ and `poc-orchestrator`/"awaiting user: step 1" wording. Note on brief (C7) and `**Affects:** —` (C11) added **outside** the agent text, because no After wording was given; an optional sentence is offered for the orchestrator. New FU-1 check: 1 hit for `awaiting user: step 1`. v2 QB settled. | E8, §3 note, §8, §12 X8 | Yes for the replacement; the note is mine and not in the agent text |
| **R2-8**: GitLab roles | LOW | Step 3's purge clause replaced with role wording. Source URL recorded and fetched; partly verified. | E8, §11 #7 | Yes |
| QC | Reviewer | Confirmed; no edit. | §3, §9 | — |
| Orchestrator's T577 correction | Orchestrator | v2's "unchanged on `c523415`" corrected for `rapid-prototyping` (C6). E11's Before kept byte-identical to v1; only the After changed. Drift-count note updated for T577's existing declarations. | Metadata, §4, §7, §10 C6, §11 #6 | — |
| FU-1 verification | — | 12 Befores, not 11. New 1-hit checks for `This is a presence check` and `awaiting user: step 1`. `Identify major auth or injection concerns` added to the golden search list. | §7, §8 | — |
| Unchanged from v2 | — | E3, E5, E7, E9, E10, E11 (After as M7), E2's other bullets, every pre-existing Before, the authority legs, FU-2, C1–C5, X1–X7. | — | — |

## 16. Orchestrator verification and rulings (added before commit, 2026-10-02)

*This section was added by the orchestrator, not by the producing agent, on `develop` `c523415`, which includes T577.
§§0–15 are unchanged.*

**16.1 Verified**

- **Every edit still applies.** All **12** Before→After pairs were simulated in order against the live files: 6 in
  `poc-security-engineer.md` (E1, E2a, E2–E5), 5 in `poc-orchestrator.md` (E6–E10) and 1 in
  `rapid-prototyping/SKILL.md` (E11). Each Before text occurs **exactly once**.
- **The applied result contains every required phrase.** It keeps the literal "The PoC orchestrator will handle
  escalation". "This is a presence check" and "Severity floor" each occur once. It contains every reviewer After
  text for M1–M7, L1–L3, L5 and R2-1 to R2-8, plus both user decisions. "as open debt" has 0 hits.
- **No golden case or prose test depends on these files.** I searched `tests/golden/` with `held-out` pruned before
  traversal. The only hit is the presence-only `/discover-skills` fixture. `test_platform_projections` and
  `test_cross_references` check only structural properties of the orchestrator agents. The registry has no
  `description` field, so E1 changes only that entry's checksum. No live file cites `poc-orchestrator.md` line
  numbers.
- **Nothing else routes security findings to debt** (sweep for §11 #9). See
  `security-review-poc-security-reviewer-blocking-v1.md`.
- **The GitLab refs clause stands.** In E8 step 3, the statement that merge-request and pipeline refs keep old
  commits is GitLab behaviour: `refs/merge-requests/*`, `refs/pipelines/*` and keep-around refs retain commits until
  the sensitive-data removal runs. The wording is kept.

**16.2 Rulings**

- **v3 E1, E2a and E2–E11 are accepted as written. FU-1 is `T579`, at P1** (the user's decision), with
  `Affects: agent/poc-security-engineer`. When T578's P1 row archives, T579's P1 row keeps the agent at `beta` with
  no gap. Re-promotion to `stable` comes after T579 closes.
- **Reviews.** v1 got CONDITIONAL_PASS (`security-review-poc-security-reviewer-blocking-v1.md`). The delta review of
  v2 also got CONDITIONAL_PASS (`security-review-poc-security-reviewer-blocking-v2.md`). The reviewer said that if v3
  adopted the After texts verbatim, the orchestrator's phrase check would suffice in place of another review. That
  phrase check passed (16.1).
- **User decisions (2026-10-02):** declined-rewrite path, "Allow, with strict conditions"; R2-6 presence check,
  "Accept"; QD, "No, keep it strict".
- **X8 (the C7/C11 note) stays in the rationale, not in agent text.** The brief and `Affects` requirements for the
  surviving task are already enforced by `validate-tasks.py`.
- **Parked:** L4/X5 (a fixed-command scanner in place of `execute`), and `code-review:150`'s waiver as a candidate
  for a matching security carve-out.
