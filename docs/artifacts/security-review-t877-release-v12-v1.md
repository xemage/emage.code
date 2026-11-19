# Artifact: security-review-t877-release-v12-v1.md

> Immutable once produced; revisions bump `<N>`.

# Security Review T877: release-level security re-check, v12.0.0

## Metadata

- **Date:** 2026-11-19
- **Reviewer:** security-engineer. The review was read-only: no shell, no write tool, no GitLab call, no token use, no job log.
- **Task:** T877 (plan-182 § Task Decomposition item 10, wave 3).
- **The user's words, verbatim, as relayed by the orchestrator:** "release plan go", "Approve (Recommended)", "v12.0.0, MAJOR (Recommended)", "Yes, probe first (Recommended)", "Accept for v12.0.0 (Recommended)" (for SEC-T660-01 and SEC-T665-01) and "Yes, push the probe tag (Recommended)".
- **Where I read:**
  - **Direct reads in the release worktree** `/home/emage/Code/emage/worktrees/release-v12.0.0` (branch `release/v12.0.0`, tip `90124fb6` per the brief):
    - `docs/releases/v12.0.0.md`, all of it;
    - `docs/tasks/task-T877.md`;
    - `docs/plans/plan-182-next-release.md:181-236` (Addenda 2 and 3);
    - `.gitlab-ci.yml:267-340`;
    - `.opencode/agents/orchestrator.md:1-56`.
  - **Searches with `grep_content`** ran on the main checkout at develop. It does not search hidden directories. They covered:
    - ADR-015 Rule 2, O6 and S3/S4/S6;
    - plan-182;
    - `.gitlab-ci.yml`, for the job layout and for any `allow_failure`;
    - register v25, the headings and § 1, § 5 and § 6.1;
    - the VERDICT and finding rows of T829, T832, T835 (and its addendum), T837, T840, T842, T844, T847, T852, T856, T860, T862, T867 and T881;
    - `implementation/platforms/opencode.json`.
  - **Read in full:** `docs/artifacts/security-confirmation-t871-sec-t660-t665-v1.md`.
  - **Read in part:** `docs/artifacts/security-review-t820-release-v11-v1.md:1-80`, the model for this review.
- **Facts from the orchestrator and from records, not checked by this review:**
  - T870's audit results (`mcp-pin-audit-next-v1.md`), as Addendum 2 and K-17 summarise them: no HIGH, and `audit --audit-level high --signatures` exits 0 with no `--accept`.
  - The orchestrator's own checks of T880 (Addendum 3).
  - The v11.0.0 probe pipeline facts that T820 cites.
- **Not run by me:**
  - `npm audit`, `pip-audit`, `audit-mcp-pins.py`, `verify-release-docs.py` and the test suites;
  - a secret scan of the range (I have no `poc-security-audit` tool in this session);
  - `git log` or `git diff` of `v11.0.0..release/v12.0.0`.
- **Not opened:** `tests/golden/held-out/`, secrets, credential and token files, and the user's settings files.

## 1. Scope

1. **The security of the delta `v11.0.0..release/v12.0.0`**, through the merged review records named in the brief, T870 and T881.
2. **The release document's security claims** (`docs/releases/v12.0.0.md`), the K-16 Conditions lines included.
3. **That the probe tag `v12.0.0-gate.1` publishes nothing**, from `.gitlab-ci.yml` read as a file.

I made no history diff, so "no control weakened" rests on the reviews and the spot checks below, **(unverified as history)**.

## 2. Summary

- **Risk level:** MEDIUM. Two accepted `SECURITY:MEDIUM` findings ship, SEC-T660-01 and SEC-T665-01. Nothing is above MEDIUM.
- **Findings of this review:**
  - 0 CRITICAL, 0 HIGH, 0 MEDIUM.
  - 1 LOW, new: SEC-T877-01 (record accuracy in M-1).
  - 2 observations with no grade.
- **No Immutable Security Constraint is breached** (§ 4).
- **No required control is omitted, removed, disabled or weakened** by the reviewed changes. They tighten controls:
  - the Opencode deny-only keys;
  - the `task` allowlist for the orchestrators;
  - the token-directory denies;
  - the Brave and `filesystem` pins;
  - `rsync --checksum` in the installer;
  - the `build.py` refusals;
  - the `context-retriever` refusals and redaction;
  - the CA-chain hardening;
  - `sync-wiki.py` refusing redirects;
  - the pin-age rule;
  - a pin gate with no `--accept`;
  - the CI-lock audit.
- **Status:** CONDITIONAL_PASS. A shipped accepted MEDIUM allows CONDITIONAL_PASS at best.

## 3. Assessment of the delta

### 3.1 Review records in the range

| Review | Verdict (by search) | Open above LOW after it? |
|---|---|---|
| T829, T832, T835 (+ addendum), batch I | PASS | No |
| T837, Opencode permission | PASS | No |
| T840, Opencode read | CONDITIONAL_PASS. It raised SEC-T840-01 (MEDIUM). | No. SEC-T840-01 is fixed by T841 and T843 (T844 row 49: "Fixed"; T847 row 96: "Fixed", resolution observed on 1.19.2; a refused call is unverified, K-20). |
| T842, Opencode deny | CONDITIONAL_PASS. SEC-T840-01 reduced, and it raised SEC-T842-01 (MEDIUM). | No. SEC-T842-01 is fixed by T843 (T844 row 48, T847 row 97). |
| T844, Opencode task | PASS | No |
| T847, Opencode live | PASS | No |
| T852, Brave 2.1.5 | PASS | No. SEC-T702-09 is fixed. |
| T856, batch AA | PASS | No |
| T860, batch X | CONDITIONAL_PASS | No. Register v25 § 1 says "Open above LOW: nothing". |
| T862, batch AB | PASS | No |
| T867, batch X text | PASS | No |
| T881, CI lock | PASS. SEC-T881-01 is LOW and fixed; SEC-T881-02 is LOW and tracked. | No |

- **Register v25 records no open or tracked id above LOW** (§ 1:20 and § 5:159). Its only accepted MEDIUMs are SEC-T660-01 and SEC-T665-01 (§ 6.1:171).
- **T870:**
  - No HIGH, and no `--accept` is in use.
  - The two young-pin exceptions are recorded exceptions, not risk acceptances (register § 6.1).
  - One CI-lock CVE, which T881 graded LOW and T880 fixed.

**Answer to brief item 1:** no finding above LOW is open other than SEC-T660-01 and SEC-T665-01.

### 3.2 Spot checks of controls (direct reads)

- **`implementation/platforms/opencode.json:17-21`:**
  - `permissionDenyUnlessGranted` maps `execute`→`bash`, `edit`→`edit`, `web`→`webfetch`/`websearch` and `agent`→`task`.
  - The read and external-directory denies are keyed on `execute`.
  - These match M-1, A-02 and A-04.
- **`.opencode/agents/orchestrator.md:4-54` (release worktree):**
  - `gitlab_*: deny` comes before the named GitLab allows.
  - The non-held servers are denied, along with the six Playwright tools.
  - `task` has `"*": deny` plus exactly the 14 subagents of its `agents:` list.
  - These match A-03 and M-1.
- **The 13/26 counts and the other generated files** were not re-counted **(unverified here)**. The document itself labels the counts as register v20's.

### 3.3 Did any fix weaken a control?

- No weakening was found in the records or the spot checks.
- One point is a record inaccuracy, not a weakening: `edit` is written as an allow (SEC-T877-01).
  - In the generated file, `edit: allow` (orchestrator.md:6) gives the same effect as Opencode's default.
  - Because the agent's own rules come last, it overrides a stricter global `edit` rule of the user's for agents that hold `edit`.
  - Whether v11.0.0's `tools: {edit: true}` had the same effect is **(unverified)**. I therefore do not grade this as a weakening.

## 4. Immutable Security Constraints (`.claude/rules/security-guidelines.md`)

| # | Constraint | Holds? | Basis |
|---|---|---|---|
| 1 | No secrets in source control | Yes, per the records | No review in the range reports a committed secret. I ran no secret scan of the range **(unverified by me)**. |
| 2 | No real PII in test data | Yes | The range adds no test data with personal data, per the reviews. Not scanned by me. |
| 3 | No disabled security checks | Yes | The delta adds checks (§ 2). The pin gate drops `--accept` and does not loosen. No `allow_failure` on the tag gates (`.gitlab-ci.yml`: `allow_failure` appears only on `markdown-links`, `main-develop-drift-check` and `wiki-sync`). |
| 4 | No unvalidated external input | Yes | `build.py` `--project-id` against the derived remote (M-6); `context-retriever` remote handling with timeouts and redaction (M-7); `sync-wiki.py` refuses 3xx (B-10). |
| 5 | No privilege escalation paths | Yes | The Opencode `task` allowlist and the deny-only keys narrow what agents can do. `edit: allow` mirrors a tool the source already grants; it grants nothing new (SEC-T877-01 concerns its documentation). |
| 6 | No unencrypted sensitive data at rest | Yes, with the accepted residual | The token is held in memory from an encrypted store (the orchestrator's fact, T871). The swap and hibernation residual is SEC-T665-01, accepted for v12.0.0. The environment-mode warning stays in K-24. |

## 5. Status of each accepted MEDIUM (`docs/releases/v12.0.0.md`, K-16 and the Conditions lines, lines 184-192)

I rule only on whether each record is complete, not on the user's decision. The slots are those of ADR-011 (one release only), ADR-012 row B3 as extended by ADR-015 (row C2, Rule 1, Rule 2, O6), ADR-016 (condition 4, D2, O-A, O-B) and v11.0.0's form (T820 § 3).

### SEC-T660-01: **complete**

| Slot | In the record | Ruling |
|---|---|---|
| User's words, verbatim and dated | "Accept for v12.0.0 (Recommended)", 2026-11-19, question dialog | Met. Matches plan-182:200 word for word. |
| Grade and release | `SECURITY:MEDIUM`, release=v12.0.0 | Met |
| Plan as shown: owner and fix | Owner the user (isolation) and devops-engineer (documentation), unchanged; fix "none possible in the harness" | Met. Matches plan-182:203-204. |
| Who can close it outside the harness (Rule 1) | The user, by running the agents or the `gitlab` server under an isolated OS user, container or VM holding only the scoped credential and no `glab` or git token. GitLab and the client vendors could only mitigate it (T871). | Met. Matches T871 "Who can close it". See observation O-1. |
| Plain statement | "No harness fix exists" | Met |
| Confirming review named and dated, before the question (ADR-016 condition 4, D2, O-B) | T871, `security-confirmation-t871-sec-t660-t665-v1.md`, 2026-11-19, "a new review for v12.0.0", confirms T812 still holds, and "came before the question, put on 2026-11-19" | Met. T871 § Dated statements. plan-182:196-198 records that the question came after T871 and cited it with its date (O-A). |
| Review date as the deadline | 2027-01-28, "not a fix date, still ahead on 2026-11-19; v12.0.0 must ship before it" | Met on 2026-11-19. Stays met only if the tag comes before 2027-01-28 (C-2). |
| Opencode scope, item 49 | K-16, line 185 gives (a) to (d) as T871 restated them; the Conditions line names "item 49 (c), (d)" as narrowed and not closed | Met. Matches T871's table. |
| Next-release clause | A new acceptance at the next release that ships it, or sooner if the deadline moves later or passes, or the fix changes | Met |
| History clause (ADR-015 Rule 2) | The v8.0.0 deadline passed at the latest on 2026-11-01 and was cured by the v11.0.0 acceptance of 2026-11-13. "No plan deadline for this finding has passed since v11.0.0." | Met. Rule 2 requires the statement only for a passed deadline. None has passed since v11.0.0, so the history clause is advisable, not required. It is accurate per T871 and T820. |
| v11.0.0 acceptance does not carry over | Line 182: "The v11.0.0 acceptance does not carry over; the acceptance below is new." | Met (ADR-011, ADR-015 S3) |

### SEC-T665-01: **complete**

| Slot | In the record | Ruling |
|---|---|---|
| Words, date, grade, release | The same question and answer, 2026-11-19, `SECURITY:MEDIUM`, v12.0.0 | Met |
| Plan, owner, fix | As for SEC-T660-01 | Met |
| Who can close it outside the harness | Isolation plus encrypted or disabled swap and hibernation, credited to T871 and to the plan as shown | Met. Matches T871 and plan-182:204. |
| T871 named, dated, before the question | Yes | Met |
| Review date | 2027-01-28 | Met (C-2) |
| Opencode scope | Not repeated in this line. K-16:186 gives the residual. | Met. T871 states the same scope as SEC-T660-01 for the read residual, and K-16 carries it for both. |
| Passed deadline | "It never had an earlier deadline, and its v11.0.0 plan's deadline has not passed" | Met, per T871 |

**Placement (as T820 C-1):** the `## RELEASE VERDICT` block is still all `pending`. T878 must carry these two lines unchanged into the verdict's Conditions (C-1).

## 6. Document-claims check

| Claim | Location | Ruling |
|---|---|---|
| SEC-T840-01 shipped in v11.0.0 and is fixed in v12.0.0 | Highlights :40, A-02 :52, M-1 :85, X-01 :156, K-16 :185 | **Correct.** Fixed per T844 and T847. "Never accepted" is consistent: the finding post-dates the v11.0.0 tag and no acceptance exists. |
| SEC-T702-09 fixed by Brave 2.1.5; K-28 closed; no `--accept` | :43, M-4 :106, :194, K-28 :200 | **Correct** per T852 (PASS) and T870 (Addendum 2). The rollback note (:275) correctly says the v11.0.0 acceptance does not cover a rollback. |
| SEC-T756-07 fixed by `filesystem` 2.4.0 | M-4 :107, X-05, K-17 | Correct per T870 (not re-run) |
| M-1: shell, edit, web and delegation denies | :85 | Correct as to the denies. **Incorrect** in "These keys are never written as an allow": `edit` is in `permissionKeys` and is written `edit: allow` (orchestrator.md:6). See **SEC-T877-01**. |
| M-1: orchestrators limited to the 14 subagents | :86 | Correct (orchestrator.md:38-54). `poc-orchestrator` was not read **(unverified here)**. |
| M-1: token directory, and what it does not cover | :87, K-42 | Correct. It matches opencode.json:20-21 and T871 (d). It is honestly labelled defense in depth, not a boundary. |
| M-1: "Your own rules do not re-grant" | :89 | Correct, and consistent with AGENTS.md (agent rules last; `OPENCODE_CONFIG_CONTENT` observed on 1.19.2; the managed configuration by source reading only). |
| M-1: what is observed | :90 | Correct, and honestly marked: the resolution is observed; a refused call or launch is unverified (K-20). |
| Unverified statements | K-20 :232, M-2 :97, M-3 :101, M-4 :107-108, K-32, K-36, K-38, K-43 | Present and appropriately marked. K-20 lists the new M-1 denies under the live check, and K-15 (:203) reopens if that check fails. |
| K-36 and K-32, the probe and the runner | :207-208 | Correct as written. The probe's routing and deletion are marked **(unverified at writing)**. |
| X-11 / SEC-T881-01 graded LOW | :166 | Correct per T881 |

## 7. Probe tag `v12.0.0-gate.1` (`.gitlab-ci.yml:267-339`, file reading only)

- **Rules.** `release-docs-gate`, `main-develop-drift-gate` and `release` share the rule `$CI_COMMIT_TAG =~ /^v[0-9]+\.[0-9]+\.[0-9]+(-[A-Za-z0-9.-]+)?$/`. The probe tag matches it, so all three jobs are created.
- **`release` has `needs: ["release-docs-gate", "main-develop-drift-gate"]`** (:319). It has no `when:` (so the default is `on_success`), and neither gate has `allow_failure`. So `release` runs only if both gates succeed, and it is skipped when either fails.
- **Why the gates are expected to fail:**
  - `release-docs-gate` runs `verify-release-docs.py --tag "${CI_COMMIT_TAG}"`, and the document's verdict fields are `pending` (:242-265).
  - `main-develop-drift-gate` runs `check-release-tag-tree.py` against `origin/main`. Before the release merge, `main` does not carry the release tree.
  - How either script maps a `-gate.1` suffix to the document was not traced **(unverified)**. T820 records, as the orchestrator's fact, that both gates failed at the v11.0.0 probe and that `release` was skipped.
- **Publishing.** Only `release` calls `publish-release.py` (:333), with `CI_JOB_TOKEN`. So, by the file, the probe publishes nothing while either gate fails.
- **What a file reading cannot show:**
  - a manual retry of `release`, or a later pipeline change;
  - whether any other job runs on a tag. I did not read `.gitlab-ci.yml:1-266` in the worktree **(unverified here)**.
- **Before the real tag:** the probe tag must be deleted (K-32, C-3).

## 8. Findings

| ID | Severity | OWASP | Location | Description | Remediation | Status |
|----|----------|-------|----------|-------------|-------------|--------|
| SEC-T877-01 | SECURITY:LOW | A05 (record accuracy about a security control) | `docs/releases/v12.0.0.md:85` (M-1, first bullet); evidence `implementation/platforms/opencode.json:17`, `.opencode/agents/orchestrator.md:6` | M-1 says the five keys "are never written as an allow, so an agent that holds the tool keeps Opencode's default for it". `edit` is in `permissionKeys` and is generated as `edit: allow` for an agent whose source holds `edit`. The effect equals Opencode's default allow. But the agent's own rules come last, so a user's global or project `edit: ask` or `deny` is silently overridden for those agents, which the bullet implies does not happen. It understates an override; it creates no new access. | Before T878's freeze, reword it. Example: "`bash`, `webfetch`, `websearch` and `task` are never written as an allow. `edit` is written as `edit: allow` for an agent whose source holds it, and, as the agent's own rule, it overrides a global or project `edit: ask` or `deny` of yours (as for the MCP allows in `AGENTS.md`)." If it is not fixed before the freeze, track it as LOW in register v26. | Open, new |

**Observations, no grade:**

- **O-1.** The Conditions line for SEC-T660-01 fills "Who could close it outside the harness" with T871's wording ("running the agents, or the `gitlab` MCP server", "no `glab` or git token"). The plan shown (plan-182:204) said "holds only the scoped token". The line credits T871 for this text, and the substance is the same. The slot is the confirming review's, not the plan's, so the record stays complete.
- **O-2.** T871 marked as unverified whether Rule 2 requires repeating an already-cured deadline. ADR-015:83 reads: "When an accepted MEDIUM's plan deadline has already passed … The release document must say that the old deadline passed." No deadline has passed since v11.0.0, so the history clause is not required for v12.0.0. Keeping it is harmless and accurate.

## VERDICT: CONDITIONAL_PASS

### Findings Summary
| Severity | Count | Resolved | Remaining |
|----------|-------|----------|-----------|
| CRITICAL | 0 | 0 | 0 |
| HIGH | 0 | 0 | 0 |
| MEDIUM | 2 (SEC-T660-01, SEC-T665-01, shipped accepted for v12.0.0 only) | 0 | 2 (accepted) |
| LOW | 1 new (SEC-T877-01) | 0 | 1 |

### Justification

- No CRITICAL or HIGH finding exists.
- No Immutable Security Constraint is breached.
- No required control is omitted, removed, disabled or weakened in the reviewed changes.
- The two shipped MEDIUMs carry complete acceptance records under ADR-011, ADR-015 and ADR-016. T871 named and dated them, before the question, with the user's words verbatim and the review date 2027-01-28.
- A shipped accepted MEDIUM allows CONDITIONAL_PASS at best (`validation-gates` § Verdict Rules).
- SEC-T877-01 is LOW.

### Conditions (for T878's Gate Verdicts row: "Security: CONDITIONAL_PASS (T877)")

- **C-1** SEC-T660-01 and SEC-T665-01: T878 carries the two K-16 Conditions lines (`docs/releases/v12.0.0.md:191-192`) unchanged into the `## RELEASE VERDICT` Conditions. Owner: release-manager. Deadline: before the freeze.
- **C-2** SEC-T660-01 and SEC-T665-01: the tag `v12.0.0` is pushed before 2027-01-28. Otherwise the user decides again and the document states the passed date (K-41). Owner: the user and the orchestrator. Deadline: 2027-01-28.
- **C-3** Probe tag: `v12.0.0-gate.1` is deleted before `v12.0.0` is pushed, and `git ls-remote --tags origin` shows no `gate` ref before and after the push (K-32). All three tag jobs show runner #59129270, or SEC-T741-17 reopens (K-36). Owner: the user (deletion) and the orchestrator (check). Deadline: at the tag.
- **C-4** SEC-T877-01: fix the M-1 wording before the freeze, or track it as LOW in register v26. Owner: release-manager. Deadline: freeze, or the next register.
- **C-5** K-40: if the release-time `age` run is before about 2026-11-24 and 2026-11-25, it uses only the two recorded `--allow-young` exceptions, and any pin bump voids them. Owner: the orchestrator. Deadline: at the release-time run.

### Blockers (if FAIL)
- None.

### OWASP Coverage
| Category | Reviewed | Findings |
|----------|----------|----------|
| A01: Broken Access Control | Yes (Opencode permission maps, task allowlist, token-directory denies) | 0 (SEC-T660-01 accepted) |
| A02: Cryptographic Failures | Yes (CA-chain control, by record) | 0 |
| A03: Injection | Yes (context-retriever remotes, build.py, by record) | 0 |
| A04: Insecure Design | Yes (accepted-MEDIUM records, release gating) | 0 |
| A05: Security Misconfiguration | Yes (release document claims, CI tag jobs) | 1 (SEC-T877-01, LOW) |
| A06: Vulnerable Components | Yes (T870, T852, T881, by record; not re-run) | 0 new (SEC-T881-01 LOW fixed) |
| A07: Auth Failures | Yes (GitLab token handling, T871) | 0 (SEC-T665-01 accepted) |
| A08: Data Integrity Failures | Yes (needs/rules of release job, pin gate, CI lock) | 0 new (SEC-T881-02 LOW tracked) |
| A09: Logging & Monitoring | Yes (redaction of remote messages, by record) | 0 |
| A10: SSRF | Yes (sync-wiki.py redirects, by record) | 0 |

## Not verified

- The history `v11.0.0..release/v12.0.0`. There was no shell and no diff.
- A secret scan of the range.
- `poc-orchestrator.md` and the 13/26 counts in the generated files.
- `.gitlab-ci.yml:1-266` in the worktree.
- How the gate scripts treat the `-gate.1` suffix.
- T870's audit runs.
- Opencode refused calls and launches live (K-20).
- Whether v11.0.0's `tools: {edit: true}` overrode a global `edit` rule.
