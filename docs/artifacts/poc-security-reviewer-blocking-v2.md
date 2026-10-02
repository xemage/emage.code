# Artifact: poc-security-reviewer-blocking-v2.md

> Filename: `poc-security-reviewer-blocking-v2.md`. Immutable once produced; revisions bump `<N>`.

## Metadata

- **Producer agent**: solution-architect
- **Task**: T578 (P1, O1, SECURITY:HIGH), revision after Security Engineer review
- **Created**: 2026-10-02
- **Based on**:
  - `docs/artifacts/poc-security-reviewer-blocking-v1.md` (superseded by this version);
  - the read-only Security Engineer review of v1, **CONDITIONAL_PASS**, findings M1–M7 (MEDIUM) and L1–L5 (LOW). The
    orchestrator relayed it to me with exact After wordings. It is recorded as
    `docs/artifacts/security-review-poc-security-reviewer-blocking-v1.md`, which **I did not read**: I worked from the
    relay;
  - the **user's decision of 2026-10-02** on v1 §9 Q2, relayed verbatim by the orchestrator: **"Allow, with strict
    conditions (Recommended)"**;
  - the orchestrator's settlement of v1 §11 #9, and its `Affects` ruling (§7 here);
  - `docs/tasks/task-T578.md`; `docs/plans/plan-099-poc-security-reviewer-blocking.md`;
    `docs/artifacts/security-review-poc-security-shortcuts-v1.md` § O1;
    `docs/artifacts/poc-security-shortcut-examples-v2.md` §9, §13.2; `docs/artifacts/poc-skills-alignment-v1.md`
    §10.2; `docs/artifacts/poc-contract-resolution-v1.md` §9.2; `docs/decisions/ADR-007-command-contract-authority.md`
    (Accepted; not used to rank agents).
  - The source files were read for v1 at `e1feee4`. The orchestrator states that the three target files are unchanged
    on `develop` `c523415`.
- **Supersedes**: `poc-security-reviewer-blocking-v1.md`. v1 stays unchanged as the historical record. **Where v1 and
  v2 differ, v2 governs. FU-1 applies v2 only.**
- **Decision references**: O1 / plan-099; the user decision of 2026-10-02 (§1.4). No new ADR is minted. No P34b
  ranking is used.

## 0. What this document is, and what it did not do

This is the complete, standalone ruling on every brief §2 site, with exact edits for FU-1 to apply. It incorporates
the Security review's conditions and the user's decision. §15 lists every v1→v2 change. **It changed no agent, skill,
command, instruction or golden case.** It is the only file written in this revision.

**Method and limits.**
- **No shell.** I had no grep, git or test runs. Claims that need one are marked **(unverified)** (§11).
- **Golden files:** I opened nothing under `tests/golden/`.
- **Applying the edits:** apply each edit by matching its exact `Before:` text, never by line number. Line numbers are
  at `e1feee4` and are given for orientation only. Every `Before:` is byte-identical to v1's, and each was unique in
  its file when I read the files in full.
- **Encoding:** `—` is U+2014, as in the source.
- **Exact wording:** where I adopted a reviewer wording with a change, rather than verbatim, the change is stated next
  to the edit and in §15.

## 1. Authority basis

### 1.1 The quoted texts

**`security-guidelines.md`** (`maturity: stable`, `applyTo: "**"`):

| Location | Text |
|---|---|
| Rails, `:15–20` | Does not grant any agent authority to disable a security control "'temporarily,' even in PoC or development mode — the Immutable Security Constraints section forbids that outright, superseding any speed-over-completeness pressure from `poc-guidelines.md`." |
| Rails, `:22–24` | "`SECURITY:CRITICAL`/`SECURITY:HIGH` findings block merge per the Security Review Workflow until resolved; `SECURITY:MEDIUM` findings require a documented remediation plan before merge" |
| Secrets Management, `:73` | "Audit secret access" |
| Agent Safety Guards, `:117–118` | "Coding agents MUST treat the following as hard blocks unless the user explicitly approves in the current session" |
| `:122` | "Never run or suggest without explicit user approval" |
| `:126` | `git push --force` |
| `:128` | history rewrite |
| `:134` | "Do not read, cat, or copy: `.env`, `.env.*`, … `*.pem`, `*.key`" |
| `:135` | "Do not paste secret values into chat, handoffs, checkpoints, or commits" |
| `:136` | "reference **names only** and instruct the user to set them locally" |
| `:153` | "absolute and cannot be overridden by any agent, configuration, or runtime decision" |
| `:155`, Constraint 1 | "… may ever be committed. This is not negotiable regardless of PoC status, urgency, or convenience." |
| `:156`, Constraint 2 | real PII |
| Security Review Workflow, `:181` | the four grades |
| `:182` | "`CRITICAL` and `HIGH` findings block merge until resolved" |
| `:183` | "`MEDIUM` findings must have a remediation plan before merge" |
| `:184` | "`LOW` findings are tracked as technical debt" |

**`poc-guidelines.md`** (`stable`, `applyTo: "**"`):
- Rails `:10–13`: it applies to "a PoC specialist agent".
- Rails `:17–19`: it "Does not waive the Immutable Security Constraints".
- Rule 3 (`:55`): "If the hypothesis isn't validated by the deadline, it fails".
- Not Allowed `:144`: "Exposing secrets in code".

**`poc-orchestrator.md:73–76`** (`stable`): "every delegation this agent issues is governed by that instruction".

**`AGENTS.md`**:
- § Validation Gates: "`FAIL` blocks progression"; "`CONDITIONAL_PASS` proceeds with tracked conditions added to the
  task list"; "Review agents (Tech Lead, QA, Security) MUST NOT modify code during review".
- § Blocker Protocol: "Max 2 retries before user escalation".
- § Task Protocol: "Only orchestrators create/transition tasks".

**`git-workflow.md`** Rails: it does not grant any agent "authority to bypass branch protection for any reason".

### 1.2 Reading

**The two agents.** Recording a committed secret, or an omitted or weakened control, "for debt handoff" is an agent's
runtime decision to leave a breach in place. That cannot coexist with `:153` and the Rails `:17–20`. The instruction
asserts its precedence by name, including over PoC speed pressure. Neither agent claims an exemption, and
`poc-guidelines` concedes the point (`:17–19`). As in `poc-security-shortcut-examples-v2.md` §1.2, one side asserts
and the other does not contest, so **no ranking is needed**.

Each agent is also within the instruction's reach in its own terms:
- `poc-orchestrator` subordinates every delegation to `poc-guidelines` (`:73–76`).
- `poc-security-engineer` is a PoC specialist agent, under `poc-guidelines:10–13`, and is in `poc-orchestrator`'s
  roster (`:5`).

The precedent is FU-C (`poc-contract-resolution-v1.md` §9.2), which built on T542.

**M1's widened blocking class rests on the same Rails sentence.** It denies any agent authority to disable "a security
control … even in PoC or development mode". A required control that is omitted, removed, disabled or weakened is a
disabled control, whatever severity grade it would otherwise get. `poc-security-shortcut-examples-v2.md` §1.2 read the
Rails' scope the same way ("a security control", not only the six constraints), and that reading was accepted in its
§13.2.

**The skill.** `poc-skills-alignment-v1.md` §10.2 approved extending the precedent to these PoC skill files.

### 1.3 The secret procedure: content and routing

**Content.** Revoke, audit, inventory copies, purge, and remove from history. Constraint 1 forbids committing a
secret but does not prescribe the remedy, so the content rests on:
- the Security Engineer's fix direction (§ O1 of the first review) and its M4/M5 conditions;
- plan-099 §2, which the user approved;
- `:73` "Audit secret access", for the log review.

**Routing.** All destructive steps go through the user. This rests directly on Agent Safety Guards `:117–128` and on
the `git-workflow` Rails.

### 1.4 The user's decision on the declined-rewrite path

v1 kept a finding open whenever the user declined the history rewrite. The user chose **"Allow, with strict
conditions (Recommended)"** (2026-10-02, relayed verbatim). That decision is the authority for E8 step 4's declined
path, and for E2's reference to it.

**It is a user decision, not an agent's runtime decision.** It does not purport to let any agent override `:153`.
Its conditions are written so that the residue left in history is a value that no longer works, has no recognised
misuse, and is not key material.

### 1.5 Does anything need a P34b ranking? **No.**

No `dependency` blocker is raised.

## 2. `poc-security-engineer.md` (held at `beta` while the P1 row is open)

### E1: `:3`, description

````
Before:
description: "Use for lightweight PoC security review that flags critical risks without blocking rapid validation."

After:
description: "Use for lightweight PoC security review. Flags high-risk issues, and blocks the PoC on critical or high findings, on any removed or weakened security control, and on any Immutable Security Constraint breach, such as an exposed secret."
````

**Source and authority.** The reviewer's M1 wording, verbatim. Delegation is driven by `description`, so "without
blocking" in it would keep teaching the old rule. Authority: `security-guidelines:17–20`, `:22–24`, `:153`, `:155`.

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
- **Exposed secret:** report the file, line, commits, whether they were pushed, the credential's type and issuer, and the environment variable that should replace it. Never reproduce the value, including in a search pattern or any other tool argument; scan by pattern. Deleting the secret from the code does not resolve the finding. It stays open until the user confirms the secret is revoked (the old value no longer works), the code reads it from the environment or a secret vault, and the secret is removed from git history with the user's explicit approval, or declined under the conditions in `poc-orchestrator` § Security Findings, which also covers a secret not yet committed. Never revoke or rotate credentials, rewrite history or force-push yourself
- End every scan with a verdict (`AGENTS.md` § Validation Gates): `FAIL` while any blocking finding is open, `CONDITIONAL_PASS` if `SECURITY:MEDIUM` findings remain with their remediation plans, otherwise `PASS`
````

**Sources:**
- **Grading bullet:** v1.
- **Severity floor:** M2, verbatim.
- **Blocking findings:** M1, verbatim.
- **Non-blocking findings:** M1's opening plus L5's deadline, verbatim.
- **Exposed secret**, with these stated changes from the reviewer's instruction:
  1. **"or rotated" becomes "(the old value no longer works)".** This aligns the bullet with M4 ("rotation counts
     only if the old value stops working").
  2. **"…removed from git history with the user's explicit approval, or declined under the conditions in
     `poc-orchestrator` § Security Findings"** is kept verbatim, as instructed. I appended ", which also covers a
     secret not yet committed", so that the M2 path is reachable from the agent file.
  3. **"including in a search pattern or any other tool argument; scan by pattern"** is added, to mirror L3 in the
     agent that actually runs the scan.
- **Verdict bullet:** v1.

**Authority:**
- `security-guidelines:17–20`, `:153`, `:155–156`, `:181–184`.
- `AGENTS.md` § Validation Gates.
- Safety Guards `:134–135`.
- The user decision (§1.4), for the declined path.

### E3: `:35`, § Blocker Reporting step 3 (escalation sentence preserved)

````
Before:
3. Suggest a workaround — PoC speed matters, prefer unblocking over perfection

After:
3. Suggest a workaround — PoC speed matters, prefer unblocking over perfection. A blocking finding (§ Behavior) has no workaround: name the fix it needs instead
````

**Mechanical constraint.** `:36`, "4. The PoC orchestrator will handle escalation", is in no `Before:` text and stays
byte-identical. `test_agent_escalation_consistency.py:102–110` asserts it with `assertIn` over the whole file.

### E4: `:46`, Rails, Out of scope

````
Before:
**Out of scope**: Blocking PoC progress on non-critical findings; performing a full OWASP-style audit.

After:
**Out of scope**: Blocking PoC progress on other `SECURITY:MEDIUM` or `SECURITY:LOW` findings; performing a full OWASP-style audit; revoking or rotating credentials, or rewriting git history (§ Behavior).
````

**Why:** "non-critical" is ambiguous, because `SECURITY:HIGH` is non-critical yet blocks (`security-guidelines:182`).
"Other" excludes the M1 class (M1).

### E5: `:47`, Rails, Failure mode

````
Before:
**Failure mode**: If a critical risk (exposed secret, obvious injection/auth gap) is found, records it explicitly for debt handoff rather than silently omitting it to avoid blocking progress.

After:
**Failure mode**: If a blocking finding is found (an exposed secret, an obvious injection or authorization gap, any omitted, removed, disabled or weakened security control, any other `SECURITY:CRITICAL` or `SECURITY:HIGH` finding, or any Immutable Security Constraint breach), reports it to the PoC orchestrator as a blocker and returns `FAIL`, rather than recording it for debt handoff or omitting it to avoid blocking progress.
````

**Unchanged in this file:** everything not named in E1–E5, including `:6` `maturity: beta` (FU-2 handles it) and the
§ Scope bullets `:14–16` (see §9 QA).

## 3. `poc-orchestrator.md` (stable, and stays stable; §7)

### E6: `:49`, the secrets check (reviewer M6; keeps v1's step-5 placement)

````
Before:
5. **Integration** — `@integration-agent`: third-party API/SDK wiring (parallel with scaffolding if independent)

After:
5. **Integration** — `@integration-agent`: third-party API/SDK wiring (parallel with scaffolding if independent)
   - **Secrets check** — `@poc-security-engineer`: before any delegated agent's work is first pushed, and before every merge, at any step (including steps 10, 13 and 14, which run after step 9), check the change for committed secrets, hardcoded credentials, tracked secret-bearing files (identified by name, never opened) and real PII. A finding blocks (§ Security Findings). Neither this check nor step 9 is ever dropped to reduce scope, time or tokens
````

**Source:** M6, verbatim.

**Why:** step 9 runs after work from steps 4–7 may already be pushed. Steps 10, 13 and 14 run after it. Push and
merge are the points where exposure grows.

**Recorded alternatives:**
- **(a) Move step 9 earlier wholesale. Not taken.** The full scan must see step 7.
- **(b) A pre-commit hook. Parked (§12 X1).**

**Authority:**
- `security-guidelines:155`, `:156`, and `:134` ("by name, never opened").
- `:107`, the token Failure mode, is why "never dropped" is needed.

**Tests:** `@poc-security-engineer` is registered and in the roster (`:5`), and the distinct-mention count is
unchanged. `test_workflow_*` stays green **(reasoned, not run)**.

### E7: `:53`, step 9

````
Before:
9. **Security Scan** — `@poc-security-engineer`: critical risks only

After:
9. **Security Scan** — `@poc-security-engineer`: high-risk issues, not a full audit. Blocking findings stop the PoC (§ Security Findings)
````

**Authority:** `security-guidelines:182` (corrected from v1's `:183`, per L1). "Critical risks only" also matched
nothing in the agent's Scope (`poc-security-engineer.md:14`).

### E8: new `## Security Findings` section, between § PoC Workflow and § Delegation Brief

````
Before:
14. **DevOps** — `@poc-devops-engineer`: fast local reproducibility

## Delegation Brief (PoC-Adapted)

After:
14. **DevOps** — `@poc-devops-engineer`: fast local reproducibility

## Security Findings

`security-guidelines.md` applies to PoC work in full. Its Rails withhold authority to disable a security control "even in PoC or development mode", its Immutable Security Constraints "cannot be overridden by any agent, configuration, or runtime decision", and `poc-guidelines.md` "Does not waive the Immutable Security Constraints". Route `@poc-security-engineer`'s findings as its § Behavior grades them, per `security-guidelines.md` § Security Review Workflow:

- **Blocking** (any Immutable Security Constraint breach; any required security control omitted, removed, disabled or weakened, tagged or not; any `SECURITY:CRITICAL` or `SECURITY:HIGH` finding): set the affected task to `blocked`, stop every delegation except the remediation, record the blocker in the next checkpoint, and tell the user. Delegate the fix, then have `@poc-security-engineer` re-check it. Apart from the timebox verdict below, the PoC does not continue, demo, evaluate or close until the re-check confirms the finding is resolved. Never record a blocking finding as debt. The speed directive, the timebox and the token envelope do not waive it. If two remediation cycles fail, escalate to the user (`AGENTS.md` § Blocker Protocol). Stopping, cancelling or timing out the PoC does not resolve a blocking finding. Before the PoC's tasks are archived, create a separate task for each open blocking finding, with status `blocked`. Its owner is the user for step 1 of an exposed secret, and the remediating agent otherwise. That task stays in `active-tasks.md` until `@poc-security-engineer` confirms the finding resolved. If the timebox expires, record the verdict `poc-guidelines.md` Rule 3 requires, but do not close the PoC. Escalation after two failed cycles asks the user to direct further remediation or to stop; it never turns the finding into debt.
- **Other `SECURITY:MEDIUM` findings**: do not block. Before the affected work merges, add the remediation plan (owner, fix, deadline no later than the production handoff) to the task list as a tracked condition (`AGENTS.md` § Validation Gates), and carry it into the debt handoff.
- **Other `SECURITY:LOW` findings**: record for debt handoff.

**Exposed secret.** Deleting a secret from the code does not resolve it: it stays in git history, and it is exposed from the moment an agent can read it. Never copy its value into chat, a brief, report, checkpoint, handoff, commit, issue, merge request, or any tool or command argument (for example a search pattern); refer to it by file, commit and environment-variable name only. Scan with pattern-based secret detection, never by its literal value. Identify committed secret files such as `.env` or `*.key` by name; do not open them (`security-guidelines.md` § Agent Safety Guards).

1. **Revoke — the user.** Ask the user to revoke the secret at its issuer (rotation counts only if the old value stops working), to set the replacement locally, and to review the issuer's access or audit logs for any use between first exposure and revocation (`security-guidelines.md` § Secrets Management, "Audit secret access"). If the logs show use the user does not recognise, it is an incident, not a PoC finding: tell the user and stop. If the secret is key material (an encryption, signing or TLS private key), name what it protected or signed, because revocation does not undo past use. No agent does this.
2. **Fix the code — a delegated agent.** Delegate the change that reads the secret from an environment variable or a secret vault, by name only, as a normal commit.
3. **Remove it from history — only with the user's approval.** Rewriting history is a destructive operation that agents "MUST treat … as hard blocks unless the user explicitly approves in the current session" (`security-guidelines.md` § Agent Safety Guards). Ask the user, naming the commits and branches affected. The rewrite happens only after that approval. On GitLab a rewrite and force-push is not enough. Commit content stays cached and visible, and merge-request and pipeline refs keep the old commits, until a maintainer runs the project's sensitive-data removal (Remove blobs, Redact text or Repository cleanup). For any pushed secret, the user performs step 3. For a secret only in local history, the user performs the rewrite or names the agent and the branches. No agent bypasses branch protection (`git-workflow.md`). List, by location only, every copy the project controls that may hold the secret (branches, tags, agent worktrees, CI job logs, artifacts and caches, images or packages built from the affected commits, merge-request diffs) and ask the user to delete or expire them. Deletion is destructive and is the user's to do. Copies no one here controls, such as other people's clones and forks, are why step 1 comes first.
4. **Resolve.** `@poc-security-engineer` confirms the finding resolved only when: the user has confirmed step 1; the step 2 fix is in place; a pattern-based secret scan of all branches and tags, never by the literal value, finds no occurrence (in their history, or only at their tips if step 3 was declined under the conditions below); and step 3 is done, not applicable, or declined under the conditions below. If the user declines step 3, the finding may be resolved as "revoked; retained in history by the user's decision" only if (a) the user has confirmed revocation, meaning the old value no longer works; (b) the audit-log review in step 1 found no unrecognised use; and (c) the secret is not key material whose past use revocation cannot undo. Record the decision, the commits and the date in the finding's task and in the next checkpoint. It is never recorded as debt. Otherwise the finding stays open and the PoC stays blocked.

**A secret not yet committed** is still blocking (`SECURITY:HIGH` at least). It is one commit away from breaching Constraint 1, and its value has already passed through at least one agent's context. Steps 1, 2 and 4 apply; step 3 does not. Step 1 may be skipped only if the user confirms the value authenticates nowhere except an ephemeral local instance.

## Delegation Brief (PoC-Adapted)
````

**Sources and stated changes:**

| Part | Source | Change from the reviewer's wording |
|---|---|---|
| Blocking parenthesis | M1, verbatim | — |
| Blocking bullet body | v1, plus M3 appended verbatim | **"Apart from the timebox verdict below,"** is prepended to v1's "the PoC does not continue, demo, evaluate or close" sentence. Without it, that sentence and M3's "record the verdict `poc-guidelines.md` Rule 3 requires" would contradict each other. |
| MEDIUM bullet | L5 deadline | Labelled "Other `SECURITY:MEDIUM` findings", and the LOW bullet likewise, so they cannot be read as covering the M1 class. This is my wording, equivalent to M1's "any other". |
| Secret paragraph, first sentence | M2's replacement | — |
| Secret paragraph, rest | L3, verbatim | — |
| Step 1 | M4, verbatim | — |
| Step 3 | v1, plus M5's GitLab text and M4's copy inventory, both verbatim | **"For a secret only in local history, the user performs the rewrite or names the agent and the branches"** keeps v1's local-only route, which M5 does not address. M5's "For any pushed secret, the user performs step 3" governs everything pushed. v1's closing sentence becomes "Copies no one here controls, such as other people's clones and forks, are why step 1 comes first", because merge-request refs and CI logs are now covered by the purge and the inventory. |
| Step 4 | M5's conditions plus the user-decision wording, verbatim, apart from one stated deviation | **The scan condition reads "(in their history, or only at their tips if step 3 was declined under the conditions below)".** As relayed, "a scan of all branches and tags … finds no occurrence" would, read as a history scan, always find the retained secret, so the user-approved declined path could never be satisfied. Reading it as a tip-only scan would weaken the normal path. My wording keeps the history scan by default and the tip scan only on the declined path. |
| Not-yet-committed paragraph | M2, verbatim | — |

**Authority:**
- §1.1 in full.
- `:73` for the audit-log review.
- `AGENTS.md` § Task Protocol for the separate tasks, since this agent is an orchestrator.
- `poc-guidelines` Rule 3 for the timebox verdict.
- The user decision (§1.4) for the declined path.

**Placement is test-safe.** The workflow regex `## PoC Workflow\n(.*?)\n## ` stops at `## Security Findings`.

### E9: `:66`, the speed directive

````
Before:
4. **Speed directive**: "Optimize for demo speed, not production quality"

After:
4. **Speed directive**: "Optimize for demo speed, not production quality. Security is the exception: simplify how a security control is built, but never omit, remove or weaken one the code needs, never commit a secret, never use real PII, and never breach any other Immutable Security Constraint (`security-guidelines.md`)."
````

**Source:** L2, verbatim.

**Authority:**
- `security-guidelines:17–20`, which supersedes "any speed-over-completeness pressure".
- `:153–160`.
- `poc-orchestrator:73–76`.

**Why it cites `security-guidelines.md`:** the citation does not depend on whether T577 lands first. `:34` ("speed
priority") is unchanged.

### E10: `:114`, § Constraints

````
Before:
- **DO NOT** block on non-critical security findings — record for debt handoff

After:
- **DO NOT** block on other `SECURITY:MEDIUM` or `SECURITY:LOW` findings — a MEDIUM finding gets a remediation plan (owner, fix, deadline no later than the production handoff) before merge, a LOW finding is recorded for debt handoff (§ Security Findings)
- **DO** block on every Immutable Security Constraint breach, every required security control omitted, removed, disabled or weakened (tagged or not), and every `SECURITY:CRITICAL` or `SECURITY:HIGH` finding until it is resolved, and never hand one off as debt (§ Security Findings)
````

**Sources:** M1's third class is mirrored on the DO line, and L5's deadline on the DO NOT line.

**Authority:** `security-guidelines:17–20`, `:182–184`.

**Unchanged in this file:** the frontmatter, the Rails `:103–107`, and everything not named in E6–E10.

## 4. `rapid-prototyping/SKILL.md` (experimental), `:61` "Enforcement"

### What the current text already does

As amended by T575, `:61` grades "the shortcut itself" on the code-review scale: a "security issue" is 🔴 Must Fix,
and `code-review:96` maps that to "Block merge".

**The routes that remain open:**
- **Tagged shortcuts.** The bullet covers "untagged" shortcuts only.
- **Omitted controls.** "Security issue" is left undefined, so omitted controls are not reliably covered.
- **The debt ledger.** technical-debt-tracking Step 3 merges "🔴 Must Fix and 🟡 Should Fix items" into it, and
  `technical-debt-tracking:93` allows status `accepted-risk`.
- **The Tech Lead waiver** at `code-review:150` ("no override without Tech Lead waiver").

### E11: `:61` (append to the bullet)

````
Before:
- An untagged shortcut discovered during review is flagged as a review finding. The missing tag is a 🟡 Should Fix finding. The shortcut itself is graded like any other finding on the code-review skill's § Severity Guide, so a shortcut that is a bug, security issue or data loss risk is a 🔴 Must Fix finding. These labels grade review findings, not debt: the technical-debt-tracking skill assigns the debt severity when it merges the finding into the debt ledger (§ POC-DEBT Tag Scanning Procedure, Step 3).

After:
- An untagged shortcut discovered during review is flagged as a review finding. The missing tag is a 🟡 Should Fix finding. The shortcut itself is graded like any other finding on the code-review skill's § Severity Guide, so a shortcut that is a bug, security issue or data loss risk is a 🔴 Must Fix finding. These labels grade review findings, not debt: the technical-debt-tracking skill assigns the debt severity when it merges the finding into the debt ledger (§ POC-DEBT Tag Scanning Procedure, Step 3). Security is the exception: omitting, removing or weakening a security control that `security-guidelines.md` requires for the code in question, or breaching an Immutable Security Constraint in `security-guidelines.md`, is a 🔴 Must Fix finding whether or not it is tagged. It blocks until it is fixed. No Tech Lead waiver applies to it (`security-guidelines.md` Rails: no agent has authority to disable a security control "even in PoC or development mode"). It enters the debt ledger only as `resolved`, never as `open`, `in-progress` or `accepted-risk`. An exposed secret is not fixed by deleting it from the code: report it to the PoC orchestrator, which follows `poc-orchestrator` § Security Findings.
````

**Source:** M7, verbatim.

**Authority:**
- `security-guidelines:17–20`, `:153`, `:155`.
- The first review's "An untagged removal of a security control should block".
- T576 R6 ("it does not make a forbidden shortcut permissible").

**Why E11 is no longer the only backstop.** In v1, this review gate was the stricter one. After M1, the security scan
(E2) blocks on the same class, so a PoC workflow with no guaranteed pre-merge review gate is still covered.

**Concurrency with T577.** T577's sites (v2 R6–R9, the `:33–49` region) do not overlap `:61`, but T577 shifts the line
number. Apply E11 by text. The second task to land re-runs `--print-drift` and must not double-declare paths.

## 5. The secret-exposure procedure: who does what

This table summarises E2 and E8. The binding text is in those edits.

| # | Step | Actor | May an agent do it alone? |
|---|---|---|---|
| 0 | Detect by pattern; report the location, commits, whether pushed, credential type and issuer, and replacement variable name. Never the value, and never as a tool argument. Verdict `FAIL`. | `poc-security-engineer` | Yes, read-only |
| 1 | Halt: task `blocked`, delegations stopped except remediation, blocker checkpointed, user told | `poc-orchestrator` | Yes |
| 2 | **Revoke** (rotation counts only if the old value stops working), set the replacement locally, **review the issuer's audit logs**, name what any key material protected or signed. Unrecognised use is an incident: stop. | **User** | **No** |
| 3 | Code reads the secret from env or vault, as a normal commit | Delegated write-capable agent | Yes |
| 4 | **History rewrite**, **GitLab sensitive-data removal**, **deletion of listed copies** | **User**, for anything pushed. For local-only history: the user, or an agent the user names after explicit approval. | **No** |
| 5 | Re-check: pattern scan of all branches and tags | `poc-security-engineer` | Yes |
| 5′ | Declined rewrite: resolved as "revoked; retained in history by the user's decision", only under conditions (a)–(c), recorded in the task and the checkpoint, never as debt | User decides; orchestrator records | **No** |
| — | PoC stopped, cancelled or timed out with the finding open: a separate `blocked` task survives archival | `poc-orchestrator` creates it | Yes |
| — | Not yet committed: steps 1–3 and 5 apply (in this table's numbering), but not step 4. Step 2 is skippable only for an ephemeral local value the user vouches for. | as above | — |

## 6. MEDIUM findings and the remediation plan: **required, non-blocking**

**Ruling.**
- Any `SECURITY:MEDIUM` finding outside the M1 blocking class does not block the PoC.
- It must have a remediation plan (**owner, fix, deadline no later than the production handoff**) before the
  affected work merges.
- The orchestrator records the plan as a tracked condition in the task list (`CONDITIONAL_PASS`) and carries it into
  the debt handoff.

**Authority:**
- `security-guidelines:23–24` and `:183`, which are not track-scoped.
- `AGENTS.md` § Validation Gates.
- The deadline cap comes from the reviewer's L5. v1 left the deadline unbounded.

**LOW:** "tracked as technical debt" (`:184`), so "record for debt handoff" survives exactly where the instruction
allows it.

## 7. Blast radius and golden coupling

| Neighbour | Effect |
|---|---|
| `security-guidelines.md`, `poc-guidelines.md`, `AGENTS.md`, all commands | **Unchanged.** |
| `code-review:150` (Tech Lead waiver) and `technical-debt-tracking:93` (`accepted-risk`) | **Unedited.** E11 closes both for security findings within its own text. The orchestrator's sweep (§11 #9) found these the only related general routes. A matching security carve-out in `code-review:150` is a **candidate, not ruled** (§12 X7). |
| `technical-debt-tracking` Step 3 | No edit. Only non-blocking findings reach the ledger as open items; resolved blocking findings appear only as `resolved`. |
| Other PoC agents' "prefer unblocking over perfection" | Unchanged (§12 X2). |
| `test_agent_escalation_consistency.py` | Expected green: the literal is preserved and E6's mention is registered and in the roster **(reasoned, not run)**. |
| `test_check_maturity.py` snapshot | No change from FU-1. |
| **`Affects` (settled by the orchestrator)** | The row stays **`agent/poc-security-engineer` only**. `poc-orchestrator` is edited but stays `stable`, per the user's P1 approval for "the agent". |
| Registry | Checksums for the three files change. E1 changes `poc-security-engineer`'s `description` field **(that the registry carries it is unverified)**. |
| Mirrors and root projections | `make sync`. 3 files × 7 platforms = 21 root paths, net of T577 **(unverified)**. Declare exactly what `--print-drift` reports. |
| `poc-orchestrator.md` line numbers | E6 and E8 shift every line after `:49` **(no live citation verified)**. |

**Golden coupling: (unverified), with no golden access.** For `rapid-prototyping`, the prior record shows existence
checks only (`poc-skills-alignment-v1.md` §10.1 #2). For the two agents there is no record.

**Expected outcome:** no grant, no fixture change, no baseline change. The orchestrator should confirm this by
searching `tests/golden/` (with `held-out` pruned) for:
- `without blocking rapid validation`
- `Record findings for debt handoff`
- `records it explicitly for debt handoff`
- `critical risks only`
- `non-critical security findings`
- `Optimize for demo speed`
- `prefer unblocking over perfection`
- `Should Fix finding`

## 8. Follow-ups

| Step / task | Covers | Files | `tests/golden/**` grant? | Owner (suggested) | Priority | Depends on / verify |
|---|---|---|---|---|---|---|
| **REV-2** (orchestrator's call): confirm v2 meets the CONDITIONAL_PASS conditions | M1–M7, L1–L3, L5; the §9 QA–QC questions; the stated deviations in E2 and E8 | None | No | Security Engineer (read-only) or the orchestrator's own check | P1 | Each condition traced to its v2 text (§15). |
| **FU-1**: apply O1 per **v2** | E1–E11 | `implementation/knowledge/agents/poc-security-engineer.md` (E1–E5); `…/agents/poc-orchestrator.md` (E6–E10); `…/skills/rapid-prototyping/SKILL.md` (E11); regenerated `implementation/.<platform>/` mirrors; `implementation/registry/index.json` (generator); the `drift` list in `tests/_baselines/root-install-drift.json` | **No** (pending the §7 search) | Backend Developer (needs a shell) | P1 | **Affects:** `agent/poc-security-engineer` only. **Verify:** see the list below. |
| **FU-2**: re-promote `poc-security-engineer` to `stable` | Maturity | `poc-security-engineer.md:6`; registry; `tests/functional/test_check_maturity.py` snapshot | No | Orchestrator scopes it | P2 | After FU-1 merges and the P1 row is archived. `check-maturity` 0 failing; nothing else in the file changed. |

**FU-1 verification:**
1. Each `Before:` matches **exactly once by text** on `develop` at dispatch (`c523415` or later, post-T577 if it has
   landed).
2. `The PoC orchestrator will handle escalation` still occurs in `poc-security-engineer.md`.
3. 0 hits under `implementation/knowledge/` for:
   - `without blocking rapid validation`
   - `Record findings for debt handoff`
   - `records it explicitly for debt handoff`
   - `critical risks only`
   - `block on non-critical security findings`
   - `Do not block progress by default`
4. 0 hits for `as open debt` in `rapid-prototyping/SKILL.md`.
5. Exactly 1 hit each for:
   - `accepted-risk` in `rapid-prototyping/SKILL.md`;
   - `Severity floor` in `poc-security-engineer.md`;
   - `## Security Findings`, `**Secrets check**` and `A secret not yet committed` in `poc-orchestrator.md`;
   - `Security is the exception:` in `poc-orchestrator.md` and in `rapid-prototyping/SKILL.md`;
   - `has no workaround` in `poc-security-engineer.md`.
6. Grep live files (not `docs/artifacts/`) for `poc-orchestrator.md:` citations made stale, and report them.
7. `sync.mjs --check` and `generate-registry.py --check` are clean. The root parity gate is green, declaring exactly
   what `--print-drift` reports, with no double-counting against T577.
8. `security-guidelines.md`, `poc-guidelines.md`, `commands/` and `tests/golden/**` are byte-unchanged.
9. `check-maturity.py --root implementation`: 0 failing; `poc-security-engineer` is `beta`; `poc-orchestrator` is
   `stable`.
10. `scorecard.py --check` is unchanged against the current baseline.
11. `python3 docs/tasks/validate-tasks.py` passes.
12. `python3 tests/run.py`: exit code checked, output redirected to a file, not piped.

**Release note (plan-099 §3) unchanged:** no release ships the current text until FU-1 merges.

## 9. Review questions

**v1's questions, now resolved:**
- **Q1, settled by M1.** The security scan blocks on any omitted, removed, disabled or weakened required control at
  any severity. This is the stricter alternative v1 recorded but did not take.
- **Q2, settled by the user** ("Allow, with strict conditions (Recommended)"). This is E8 step 4's declined path.
- **Q3, settled by M2.** The severity floor applies, and a not-yet-committed secret is blocking.

**New questions raised by the v2 text (decide explicitly; none blocks FU-1 unless the reviewer says so):**
- **QA: Scope against blocking class.** M1 makes the scan block on any omitted required control. But the agent's
  § Scope (`:14–16`, "Flag obvious high-risk issues …") and Rails (`:46`, no "full OWASP-style audit") do not ask it
  to *look* for all such controls. Some omissions, such as missing security headers or missing rate limiting, block
  only if someone notices them. Should § Scope gain a bullet such as "Check that the security controls
  `security-guidelines.md` requires for the code are present"? I did not add one, because neither the reviewer nor
  the brief asked for it.
- **QB: User as task owner.** M3 makes "the user" the owner of a finding's task. `docs/tasks/active-tasks.md`'s
  legend says "Owners are agent names from `knowledge/agents/`" (as quoted in `poc-skills-alignment-v1.md` §4d).
  Whether `validate-tasks.py` checks owner values is **(unverified)**. If it does, the owner could be
  `poc-orchestrator`, with "awaiting user: step 1" in the title.
- **QC: Timebox against cancellation.** Under M3, an expired timebox records the Rule 3 verdict but does not close the
  PoC. A stop or cancel archives the PoC's tasks behind a surviving `blocked` task. My reading: on expiry the PoC
  stays open and `blocked` until the user either clears the finding or stops the PoC, at which point the
  separate-task rule applies. The reviewer should confirm.

## 10. Corrections to the brief (`unclear_requirements`, all `minor`)

- **C1: `poc-security-engineer` is `beta`, not "stable".** On `e1feee4` the file reads `maturity: beta` (`:6`), set by
  `416b734`. Brief §2's facts were verified on `81921f7`. All line numbers still match.
- **C2: `poc-orchestrator.md:66` uses double quotes in the source.** The brief shows single quotes.
- **C3: `rapid-prototyping:61` already blocks a "security issue" via `code-review:96`.** The review read the
  pre-T575 `:54`. What remains is tagged and omitted controls, the debt-ledger route, `accepted-risk`, and the waiver
  (§4). "Nothing anywhere says that a critical finding blocks" is true of the two agents only.
- **C4: two edits fall outside the §2 site list.** These are E6 (`:49`) and the E8 insertion point.
  `security-guidelines.md:151–160` is ruled unchanged and used as authority only.
- **C5: the worktree was at `e1feee4`, not `81921f7`.** The orchestrator states the target files are unchanged
  through `c523415`.

## 11. Unverified claims (need a shell)

1. No golden case asserts the content of the three target sites (§7 search list).
2. The registry carries the agent `description`.
3. 21 root-projection paths, net of T577.
4. No live file cites `poc-orchestrator.md` line numbers.
5. No other test asserts text in these files. I read only `test_agent_escalation_consistency.py`.
6. The three target files are byte-unchanged from `e1feee4` to `c523415`. This is the orchestrator's statement, and
   I did not re-read the files at `c523415`.
7. **The GitLab facts in E8 step 3** (cached commit content, merge-request and pipeline refs, and "Remove blobs,
   Redact text or Repository cleanup") are the reviewer's wording. I did not verify them independently against
   GitLab documentation.
8. Whether `validate-tasks.py` accepts "user" as an owner (§9 QB).
9. **Settled by the orchestrator.** Outside the three amended files, nothing routes security findings to debt. The only
   related general routes are `code-review:150` (Tech Lead waiver, a general `FAIL` override) and
   `technical-debt-tracking:93` (`accepted-risk`), and E11 closes both for security findings.
10. I did not read the recorded review file (`security-review-poc-security-reviewer-blocking-v1.md`). v2 follows the
    orchestrator's relay of it.

## 12. Findings outside scope (not ruled; candidates for parking)

- **X1: no pre-commit secret-scanning hook.** It is a tooling choice for `scaffolding-agent` or
  `poc-devops-engineer`.
- **X2: "prefer unblocking over perfection" appears in eleven other PoC agents.** Five were read; the rest are
  unverified. E9 reaches them through every brief, so no edit is compelled.
- **X3: `integration-agent.md:22` and `:50`.** `:22` reads "label … unresolved security/reliability gaps", and `:50`
  puts "secrets rotation" out of scope as production-hardening. Both are worth clarifying in light of E8 step 1.
- **X4: the scan's scope against Security Review Workflow step 1** (the OWASP checklist on every security-sensitive
  MR). This is now sharper because of M1 (§9 QA).
- **X5 (the reviewer's L4, parked): replace `poc-security-engineer`'s `execute` tool with a fixed-command scanner.**
  Recorded only, not ruled.
- **X6: `security-guidelines` defines no residual-risk path of its own** for a revoked secret that cannot be purged.
  The user's decision (§1.4) fills it for the PoC track only. Whether the instruction should carry it is for the
  instruction's owner.
- **X7: `code-review:150`'s Tech Lead waiver** is a candidate for a matching security carve-out in the code-review
  skill itself. E11 closes it only for PoC shortcuts. Not ruled.

## 13. Blockers

**None.** No P34b ranking is needed (§1.5).

## 14. Summary

| Site | Ruling | Edit | Authority |
|---|---|---|---|
| `poc-security-engineer:3` | Blocks on critical/high, removed or weakened controls, and constraint breaches | E1 | `:17–20`, `:22–24`, `:153`, `:155` |
| `poc-security-engineer:18–20` | Grade; severity floor; three-class blocking (never debt); MEDIUM plan with a deadline at or before handoff; LOW to debt; secret rules incl. the declined path; verdict | E2 | `:17–20`, `:153–156`, `:181–184`; `AGENTS.md`; user decision |
| `poc-security-engineer:35` | Qualified; `:36` kept verbatim | E3 | as E2; mechanical test |
| `poc-security-engineer:46` | "Other" MEDIUM/LOW; no rotation or rewrite | E4 | `:182` |
| `poc-security-engineer:47` | Blocker plus `FAIL`, three classes | E5 | as E2 |
| `poc-orchestrator:49` | Secrets/PII check before every first push and every merge, at any step; never dropped | E6 | `:134`, `:155–156` |
| `poc-orchestrator:53` | High-risk issues; blocking stops the PoC | E7 | `:182` |
| `poc-orchestrator` § Security Findings | Routing; survives stop, cancel or timeout; revoke plus audit; inventory; GitLab purge; pattern re-scan; user-decided declined path; not-yet-committed | E8 | §1.1; user decision |
| `poc-orchestrator:66` | Security exception covering omission, secrets, PII and all constraints | E9 | `:17–20`, `:153–160` |
| `poc-orchestrator:114` | DO NOT (other MEDIUM/LOW) and DO (three classes) | E10 | `:17–20`, `:182–184` |
| `rapid-prototyping:61` | 🔴 tagged or not, omitted included; no waiver; ledger only as `resolved` | E11 | `:17–20`, `:153`, `:155` |
| MEDIUM | Plan required before merge; deadline no later than production handoff; non-blocking | E2, E8, E10 | `:23–24`, `:183`; L5 |
| `Affects` | `agent/poc-security-engineer` only; `poc-orchestrator` stays `stable` | — | orchestrator, per the user's P1 approval |

## 15. Change log v1 → v2

| Item | Severity / source | v2 change | Where | Verbatim? |
|---|---|---|---|---|
| **M1**: blocking class includes omitted, removed, disabled or weakened controls at any severity | MEDIUM | New third blocking class in E2. "Any other" / "other" in E2, E4 and E10's DO NOT line. Mirrored in E8's Blocking parenthesis, E10's DO line and E5's parenthesis. E1 rewritten. §1.2 authority added. v1 Q1 settled. | E1, E2, E4, E5, E8, E10; §1.2; §9 | Yes. E8's MEDIUM and LOW bullets relabelled "Other …" as an equivalent of "any other". |
| **M2**: severity floor; never-committed secrets | MEDIUM | New "Severity floor" bullet in E2. E8's first secret sentence becomes "exposed from the moment an agent can read it". New "A secret not yet committed" paragraph. Step 4 accepts "not applicable". v1 Q3 settled. | E2, E8 | Yes. E2's secret bullet also says the orchestrator section "also covers a secret not yet committed" (my addition, for reachability). |
| **M3**: stopping, cancelling or timing out does not bury a finding | MEDIUM | Appended to E8's Blocking bullet. | E8 | Yes. Added "Apart from the timebox verdict below," to v1's "does not continue, demo, evaluate or close" sentence, to remove the contradiction. §9 QB and QC raised. |
| **M4**: audit logs, key material, copy inventory | MEDIUM | E8 step 1 replaced. Copy inventory added to step 3. | E8 | Yes. v1's closing sentence of step 3 narrowed to "copies no one here controls". |
| **M5**: GitLab purge; re-check scope | MEDIUM | GitLab text added to step 3. Step 4's conditions replaced. | E8 | **One deviation:** the scan condition gains "(in their history, or only at their tips if step 3 was declined under the conditions below)", without which the user-approved declined path could never be met. v1's local-only route is kept for unpushed secrets. |
| **M6**: scan coverage | MEDIUM | E6's sub-bullet replaced; placement kept. | E6 | Yes |
| **M7**: E11's escape routes (waiver, `accepted-risk`, omission) | MEDIUM | E11's appended sentences replaced. | E11 | Yes |
| **User decision on Q2** ("Allow, with strict conditions (Recommended)") | User, 2026-10-02 | Declined-rewrite path appended to E8 step 4. E2's phrase extended with "or declined under the conditions in `poc-orchestrator` § Security Findings". Authority recorded in §1.4. | E2, E8; §1.4 | Yes |
| **L1**: `:182`, not `:183` | LOW | E4's rationale and E7's authority corrected. §1.1 lists `:181–184` individually. | E4, E7, §1.1 | — |
| **L2**: E9 After | LOW | Replaced. | E9 | Yes |
| **L3**: secret-handling sentence | LOW | Replaced in E8. Mirrored briefly in E2 ("including in a search pattern or any other tool argument; scan by pattern"). | E8, E2 | Yes in E8; the E2 mirror is my addition |
| **L4**: `execute` → fixed-command scanner | LOW | Parked, recorded only. | §12 X5 | — |
| **L5**: MEDIUM deadline | LOW | "(owner, fix, deadline no later than the production handoff)" in E2 and E8. Also in E10's DO NOT line and §6, for consistency. | E2, E8, E10, §6 | Yes |
| FU-1 checks | Orchestrator | Added: 0 hits for `as open debt` in `rapid-prototyping`; exactly 1 each for `accepted-risk` (`rapid-prototyping`) and `Severity floor` (`poc-security-engineer`). Also added `A secret not yet committed`, and a maturity check that `poc-orchestrator` stays `stable`. | §8 | — |
| §11 #9 sweep | Orchestrator | Recorded as settled. `code-review:150` noted as a carve-out candidate, not ruled. | §7, §11, §12 X7 | — |
| `Affects` | Orchestrator | Settled: `agent/poc-security-engineer` only, and `poc-orchestrator` stays `stable`. v1's open decision point is removed. | §7, §8, §14 | — |
| E2 secret bullet: "revoked or rotated" | Consistency with M4 | Now "revoked (the old value no longer works)". | E2 | Stated equivalent |
| New review questions | — | QA (Scope against M1), QB (user as task owner), QC (timebox against cancel). | §9 | — |
| Unchanged from v1 | — | E3, E7's text, every `Before:` text, the authority legs, the blast-radius method, FU-2, C1–C5. | — | — |
