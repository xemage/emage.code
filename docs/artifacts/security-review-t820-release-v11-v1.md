# Artifact: security-review-t820-release-v11-v1.md

> Immutable once produced; revisions bump `<N>`.

# Security Review T820: release-level security re-check, v11.0.0

## Metadata

- **Date:** 2026-11-13
- **Reviewer:** security-engineer, read-only. I had no shell and no write tool, made no GitLab call and used no token.
- **Task:** T820 (plan-161 § Task Decomposition item 8, wave 3). The user's words, as relayed by the orchestrator, option labels verbatim: plan-161 "Approve (Recommended)"; version "v11.0.0, MAJOR (Recommended)".
- **Where I read:**
  - The release worktree `/home/emage/Code/emage/worktrees/release-v11.0.0` (branch `release/v11.0.0`, tip `67222765`), read directly.
  - `grep_content` refused the worktree root, so every search ran on the main checkout at develop `81520c31`. Per the orchestrator, that checkout differs from the release branch only by the release commits. So search results for `servers.yaml`, the lock files, `install.sh` and the Node-floor grep are develop's. The files I read directly in the worktree were `.gitlab-ci.yml` 245-324, `install.sh` 183-200 and `PREREQUISITES.md` 1-6 and 222-229.
- **Inputs read:**
  - `docs/tasks/task-T820.md`; `docs/plans/plan-161-release-v11.md` (item 8, Addenda 1 to 3); `docs/plans/plan-160-v11-confirmation-sec-t660-t665.md` (§ Outcome); `docs/plans/plan-159-release-gate-runner-tag.md:46-56` (by search)
  - `docs/releases/v11.0.0.md` (T816), all of it
  - `docs/artifacts/security-review-t812-v11-no-harness-fix-v1.md`, `security-review-t825-v11-prep-v1.md` and `brave-audit-acceptance-v4.md` (§ Metadata, § What is accepted, § Conditions), all read in full
  - By search: `security-review-t811-release-gate-runner-v1.md`, `release-v11-audit-v1.md` (B-1 to B-13 and line 137), and `security-review-release-v10-v1.md`. That last file is T762's review. **The brief's path `security-review-t762-*.md` does not exist.**
  - The ADRs, by search: ADR-015 (Rule 1, Rule 2, O1 to O7, C1, C2) and ADR-016 (D1 to D4, O-A to O-D, line 69)
  - `implementation/knowledge/skills/validation-gates/SKILL.md:62-120` (§ Verdict Rules, Release Gate inputs); `implementation/knowledge/agents/release-manager.md:183`
  - `implementation/PREREQUISITES.md:4`, `:227`
  - `docs/releases/v8.0.0.md:239, 256, 260, 261, 275, 297, 300`, `v9.0.0.md:232, 240, 283, 287` and `v10.0.0.md:197, 199, 293, 297` (by search for SEC-T660-01)
  - Spot checks of controls: `scripts/install.sh:183-200`, `:1607-1608`; `.gitlab-ci.yml:252-324`; `implementation/knowledge/mcp/servers.yaml:75, 93, 112, 142`; both `implementation/runtime/{security,memory}/requirements-mcp-server{,.lock}.txt`; `implementation/runtime/memory/requirements.txt`
- **External read (2026-11-13):** `https://registry.npmjs.org/@brave/brave-search-mcp-server/latest` returned version `2.1.4`.
- **Facts from the orchestrator, not checked by this review:**
  - Probe tag pipeline 3066689514 ran both gate jobs on runner #59129270, system ID `s_7371c6d24bcc`, GitLab Runner 19.5.3.
  - The jobs used the pinned `python:3.12-alpine@sha256:e064671c…` from a fresh clone.
  - Both jobs failed as expected, `release` was skipped and nothing was published.
  - The full suite passed at develop `2938d368` (2744 OK, skipped=25).
  - The release document's gate fails only on the 16 pending verdict values.
- **Not run by me:** `pip-audit`, because the `run_pip_audit` tool returned "executable not found: 'pip-audit'" for both locks. Also not run: `scripts/audit-mcp-pins.py`, the test suites and `verify-release-docs.py`. For those I rely on T814, T824, T825 and the orchestrator.
- **Not opened:** `tests/golden/held-out/`, secrets, credential files and the user's settings files.

## 1. Summary

- **Risk level:** MEDIUM. Three accepted `SECURITY:MEDIUM` findings ship. Nothing is above MEDIUM.
- **Findings of this review:**
  - 0 CRITICAL, 0 HIGH, 0 MEDIUM.
  - 1 LOW, new: SEC-T820-01.
  - 2 observations with no grade.
- **Shipped MEDIUMs, accepted for v11.0.0 only:** SEC-T660-01, SEC-T665-01 and SEC-T702-09. The record of each in the release document is complete (§ 3).
- **What I checked across the delta** (B-1 to B-13, T812, T814, T825):
  - **No Immutable Security Constraint is breached** (§ 4).
  - **No required control is omitted, removed, disabled or weakened.** The code changes in the delta tighten controls: removed-platform refusals before any write, index-build refusals and userinfo redaction, the patched `opentelemetry-api`, per-line Node floors, the CA-chain jobs and the release-gate runner tag.
- **Status:** CONDITIONAL_PASS. Under `validation-gates` § Verdict Rules, a shipped `SECURITY:MEDIUM` allows CONDITIONAL_PASS at best.

## 2. Findings

| ID | Severity | OWASP | Location | Description | Remediation | Status |
|----|----------|-------|----------|-------------|-------------|--------|
| SEC-T820-01 | SECURITY:LOW | A05 (record accuracy about a security control) | `docs/releases/v11.0.0.md:220` (K-36), `:222` (K-32) | K-36 still says "**The release-gate runner has never run a job (plan-159).**" Per the orchestrator's facts (plan-161 Addendum 3), the probe pipeline 3066689514 ran both gate jobs on runner #59129270, system ID `s_7371c6d24bcc`. K-32 still says a probe tag "if one is pushed". The error understates what was proven, so it creates no false assurance. Even so, the record about SEC-T741-17's control is stale. | Before T821's freeze, if T819 agrees, reword K-36. Example: "Probe tag `v11.0.0-gate.1` (pipeline 3066689514, the orchestrator's record) ran `release-docs-gate` and `main-develop-drift-gate` on runner #59129270 (system ID `s_7371c6d24bcc`, GitLab Runner 19.5.3) with the pinned image. Both failed as designed, and nothing was published. The `release` job has not run on this runner. That this system ID is `gitlab-runner-16028` is **(unverified)**." In K-32, say the probe was pushed and that its deletion is **(unverified)**. If this is not fixed before the freeze, track it as LOW. | Open, new |

**Observations, no grade:**
- **O-1 (K-16, `v11.0.0.md:200`):** the sentence "Whether v9.0.0 carried the same deadline is **(unverified)**" can now be answered.
  - `docs/releases/v9.0.0.md` names SEC-T660-01 at lines 232, 240, 283 and 287. None of those lines carries a new acceptance, user words or a deadline for it. Line 232 says only "accepted by the user".
  - So the passed deadline is the v8.0.0 plan's, and the old acceptance was given for v8.0.0, exactly as K-16 says.
  - The release manager may replace the "(unverified)" with this reading. Leaving it in place does not make the record incomplete.
- **O-2:** the brief's input path `docs/artifacts/security-review-t762-*.md` does not exist. T762's review is `docs/artifacts/security-review-release-v10-v1.md`, and I used that file.

## 3. Ruling on each accepted MEDIUM record (`docs/releases/v11.0.0.md`, Known Issues)

I rule only on whether each record is complete, not on the user's decision. The slots are those of `release-manager.md:183`, `validation-gates` § Verdict Rules, ADR-011, ADR-012, ADR-015 (Rule 1, Rule 2, O1, O5) and ADR-016 (D1, D2, O-A, O-B).

### SEC-T660-01 (K-16, lines 195-202): **complete**

| Slot | In the record | Ruling |
|---|---|---|
| User's words, verbatim and dated | "Accept for v11.0.0 (Recommended)", 2026-11-13, question dialog. The question is quoted in plan-160 § Outcome, and the answer of 2026-11-12 is marked superseded | Met. Matches plan-160:44-49 word for word |
| Id and grade | SEC-T660-01, `SECURITY:MEDIUM` | Met |
| Release asked about | v11.0.0 | Met. The question (plan-160:44) says "For release v11.0.0" |
| Plan as shown: owner and fix | Owner the user (isolation) and devops-engineer (documentation); fix "none possible in the harness" | Met. Same as the question. Owner unchanged, so no current-owner slot is needed |
| Rule 1 / condition 1: outside closer | The user, by isolation: an OS user, container or VM holding only the scoped credential and no `glab` or git token | Met. Same as T812 |
| Condition 2: plain statement | "**No harness fix exists**" | Met |
| Condition 3: review date as the deadline (O1) | 2027-01-28, stated as "the plan's deadline, not a fix date" | Met |
| Condition 4: confirming review before the question (D1, O-B, D2/O-C) | T812, dated 2026-11-13, "a new review for v11.0.0". It came before the question of 2026-11-13, which cites it | Met. T812 is a new review for this release with dated statements (T812 § Dated statements). plan-160 § Outcome records that the question came after T812, and the question as quoted names T812 and its date, so the O-A citing duty is also met |
| Deadline still ahead | 2027-01-28 is after 2026-11-13. The record says v11.0.0 must ship before it, and that a new acceptance is needed at the next release | Met on 2026-11-13. It stays met only if the tag comes before 2027-01-28 (condition C-2) |
| Rule 2 / O5: passed deadline, its date, release of the old acceptance | "the sprint after v8.0.0", at the latest 2026-11-01. Old acceptance given for v8.0.0: "Accept the risk, plan after the release (Recommended)", 2026-10-15 (`v8.0.0.md:261`). Kept separate from the 2027-01-28 review | Content met. I verified `v8.0.0.md:261` (the words and the date) and `:300` (the deadline). **Placement:** ADR-015 O5 puts this statement in the verdict's Conditions line, which does not exist yet (`## RELEASE VERDICT` is all `pending`). K-16 is the correct source, and T821 must carry it into the Conditions line (C-1) |

### SEC-T665-01 (K-16, same record): **complete**

The same slots are met with the same text. The record also says the passed-deadline statement does not apply, because the finding never had an earlier deadline (T812:98, T756 line 27 as T812 cites it). Met.

### SEC-T702-09 (K-28, lines 203-208): **complete**

| Slot | In the record | Ruling |
|---|---|---|
| User's words, verbatim and dated | Three answers: 2026-11-12 (plan-155) twice, and 2026-11-13 (plan-158), with the questions quoted in v4 § Metadata | Met. Each quotation matches `brave-audit-acceptance-v4.md:14, :19, :26` character for character |
| Id, grade, release | SEC-T702-09, `SECURITY:MEDIUM`, v11.0.0 | Met. v4:11 asks about v11.0.0 |
| Plan as shown | Owner devops-engineer; fix: bump to the first Brave release above 2.1.4 | Met. Same as v4:22 and :30 |
| Rule 1 / ADR-016 | Not applicable, because the fix is a version bump | Correct |
| Deadline still ahead | 2027-01-30 or the first Brave release above 2.1.4, whichever is first | Met on 2026-11-13. **I read npm myself: `latest` = 2.1.4 on 2026-11-13.** It stays met only while that holds at the tag (C-2) |
| Lapse rule | "If the acceptance lapses before the tag, the Brave HIGH findings block the release" | Present and correct |
| Count claim | "seven known advisories, five graded high by npm" | Matches v4's table: 5 high, 2 moderate |

### Other release-document claims checked

- **K-15:** closed by removal; see § 5.
- **K-18:** "No open or tracked id is above LOW". This uses the fixed wording of SEC-T762-02. TD-T697-07, a MEDIUM, is correctly stated as not shipped and not accepted.
- **M-6 and Install line 31:** the per-line Node minimums are correct.
- **M-6 upgrade lines:**
  - Both lock paths exist in a target. The installer copies `implementation/runtime/memory` and `implementation/runtime/security` into `$TARGET` (`install.sh:1607-1608`).
  - Both locks pin `opentelemetry-api==1.45.2` at line 244.
  - A `==` pin under `pip install -r` replaces an installed 1.45.1. That is my reading of pip's behaviour; the lines were not run, and the document already marks them **(unverified)**.
- **Rollback:** "SEC-T814-01 returns" on a rollback is disclosed. Correct.

## 4. Immutable Security Constraints

| # | Result |
|---|---|
| 1 No secrets in source control | No breach found. A high-confidence pattern search (`glpat-`, `AKIA`, `sk-ant-`, `ghp_`, PEM private keys) over `docs/`, `implementation/`, `scripts/` and `ci/` matched only two documented placeholders, in `checkpoint-003-tests.md:47` and `security-review-t686-release-job-token-v1.md:35`. This is a pattern search, not proof of absence |
| 2 No real PII in test data | Nothing in the delta adds test or demo data with personal information (not searched) |
| 3 No disabled security checks | Not breached. The release gates are intact (`.gitlab-ci.yml:252-324`: hash-locked install, allowlisted environment, `rm -rf .git`, clean clone, dedicated tag). The Pi and Gemini removals retire platforms, not checks |
| 4 No unvalidated external input | Not breached. B-5 and B-6 add validation |
| 5 No privilege escalation paths | Not breached. The `gitlab` pin `@2.2.5` and `GITLAB_PERMISSION_MODE: modify` are unchanged (`servers.yaml:75, :93`), and no grant was added |
| 6 No unencrypted sensitive data at rest | Not breached. Token handling is unchanged (T812, plan-160:36) |

## 5. Status of the named ids at this release

| Id | Grade | Status at v11.0.0 | Evidence |
|---|---|---|---|
| SEC-T814-01 | LOW (A06) | **Fixed in this release** (minted and fixed) | Both locks pin `opentelemetry-api==1.45.2` at line 244 (read on develop). The release document records it in X-04, M-6 and K-17. pip-audit was not re-run by me (tool missing), so this relies on T825 and the orchestrator |
| SEC-T825-01 | LOW (A06) | **(b) done; (a) open, tracked-LOW** | M-6 carries the upgrade lines, and they are valid in a target. Both `requirements-mcp-server.txt` files still have only the `httpx2>=2.12.0` floor and no `opentelemetry-api` floor (read). That is tracked as debt under the user's LOW policy |
| SEC-T825-02 | LOW (A06) | **Fixed; reviewed now, PASS** | `PREREQUISITES.md:4` reads "Node.js 22 (22.23.5 or later), 24 (24.22.3 or later) or 26 (26.13.1 or later) … odd-numbered and end-of-life lines (18, 20, 23, 25) are not supported". `:227` reads "v22 ≥ 22.23.5, v24 ≥ 24.22.3, or v26 ≥ 26.13.1". Both match T825's example. The single-floor reading is gone, and removing the duplicate end-of-life sentence lost nothing |
| SEC-T784-01 | LOW (A06) | **Closed (fixed)** | PREREQUISITES and the release document (line 31, M-6) name the per-line minimums. My search over all `*.md` files and `package.json` `engines` found no live user-facing "Node 18+" floor, only historical plans and artifacts. `ci/js` is CI only |
| SEC-T741-17 | (as registered) | **Repository half closed (T811). Runtime half partly observed, still open until T822 step 3** | `tags: ["release-gate"]` is on all three tag jobs (`.gitlab-ci.yml:255, :282, :306`, read). The probe shows the two gates on #59129270 (orchestrator's fact). `release` has not run there. That `s_7371c6d24bcc` is `gitlab-runner-16028` is **(unverified)**. If any of the three jobs of the real tag runs elsewhere, the finding reopens |
| SEC-T811-01 | MEDIUM | Resolved by the user's action, as the user reported ("Already done", plan-159:48, :55) | Not verified against GitLab. One system ID in the probe is consistent with a single manager, but is not proof |
| K-15 / SEC-T657-01 / SEC-T658-01 | MEDIUM | **Closed by removal at v11.0.0. No acceptance is needed and none is recorded** | `install.sh:191-198` refuses `pi` and `gemini` in any letter case with exit 1 before any write (read). The trigger to reopen is still open: the Opencode live check (K-20, A-7, SEC-T658-02). v10.x trees left in a project are frozen and not tool-restricted, which is disclosed in K-37, M-1 and M-2 |

SEC-T762-04, raised at v10.0.0, is ruled by ADR-015 and ADR-016 and is closed.

## 6. Recommendations (priority order)

1. **T821:** write the `### Conditions` line of each of the three MEDIUMs with every slot of § 3. For SEC-T660-01, the passed-deadline statement goes in the Conditions line itself (ADR-015 O5), not only in K-16.
2. **Before T821's freeze:** fix SEC-T820-01 (K-36 and K-32 wording); optionally apply O-1.
3. **On the tag day (T822):**
   - confirm the date is before 2027-01-28;
   - confirm npm `latest` for Brave is still 2.1.4;
   - re-run `python3 scripts/audit-mcp-pins.py audit --audit-level high` with v4's seven `--accept` entries, which must exit 0;
   - watch that all three tag jobs run on #59129270.
4. **Next register (v17):**
   - SEC-T814-01: minted and fixed;
   - SEC-T825-01 (a): tracked-LOW;
   - SEC-T825-02 and SEC-T784-01: fixed;
   - SEC-T820-01, if it is not fixed;
   - SEC-T741-17: its outcome from T822.

## 7. Compliance checklist

- [x] OWASP Top 10 reviewed, for the release delta
- [x] Authentication secure: token handling unchanged (T812)
- [x] Authorization enforced: GitLab grants and mode unchanged
- [x] Input validation complete: B-5 and B-6 tighten it
- [x] Secrets management verified: pattern search, see § 4
- [x] Dependencies audited: through T814 and T825, the locks read, Brave read on npm; pip-audit not re-run by me
- [ ] Security headers configured: not applicable (CLI and stdio)
- [x] Logging appropriate: SEC-T796-01 redaction is in the release

## VERDICT: CONDITIONAL_PASS

### Findings Summary
| Severity | Count | Resolved | Remaining |
|----------|-------|----------|-----------|
| CRITICAL | 0 | 0 | 0 |
| HIGH | 0 | 0 | 0 |
| MEDIUM | 3 (shipped, user-accepted: SEC-T660-01, SEC-T665-01, SEC-T702-09) | 3 for v11.0.0 only (accepted, which counts as resolved for this release) | 0 unaccepted |
| LOW | 5 (SEC-T820-01 new; SEC-T814-01, SEC-T825-01, SEC-T825-02, SEC-T784-01) | 3 (SEC-T814-01, SEC-T825-02, SEC-T784-01) | 2 (SEC-T820-01; SEC-T825-01 (a), tracked) |

### Justification
- No `SECURITY:CRITICAL` or `SECURITY:HIGH` finding is open. No Immutable Security Constraint is breached (§ 4). No required control is omitted, removed, disabled or weakened in the delta: B-1 to B-13, T823, T824 and the SEC-T825-02 wording all tighten or keep controls.
- The three shipped MEDIUMs each have a complete acceptance record (§ 3), including the ADR-016 conditions for SEC-T660-01 and SEC-T665-01 (T812 before the question, cited by it) and the passed-deadline statement for SEC-T660-01.
- Under § Verdict Rules, a shipped medium allows CONDITIONAL_PASS at best. The LOWs are tracked as debt and are not conditions.

### Conditions
- **C-1 (record):** owner=@release-manager (T821); remediation=the RELEASE VERDICT Conditions block carries SEC-T660-01, SEC-T665-01 and SEC-T702-09 with every slot of § 3, and the SEC-T660-01 line states that the old deadline "the sprint after v8.0.0" passed, at the latest 2026-11-01, for the acceptance given for v8.0.0 (ADR-015 O5); deadline=T821, before the tag.
- **C-2 (dates):** owner=orchestrator (T822); remediation=tag before 2027-01-28, while Brave `latest` is 2.1.4 and before 2027-01-30, with the audit command passing on the tag day; otherwise the finding blocks and the user decides again; deadline=the tag.
- **C-3 (SEC-T741-17):** owner=orchestrator (T822 step 3); remediation=all three tag jobs, `release` included, show runner #59129270, or SEC-T741-17 reopens and the release is not treated as routed; deadline=the tag pipeline.

### Blockers
None.

### OWASP Coverage
| Category | Reviewed | Findings |
|----------|----------|----------|
| A01: Broken Access Control | Yes (GitLab grants and mode unchanged; removed-platform refusals) | 0 |
| A02: Cryptographic Failures | Yes (lock hashes per T825; CA-chain jobs present) | 0 |
| A03: Injection | Yes (B-5 placeholder refusal; B-6 project-id refusal) | 0 |
| A04: Insecure Design | Yes (acceptance records, ADR-015 and ADR-016) | 0 |
| A05: Security Misconfiguration | Yes (tag jobs, runner tag, release document claims) | 1 (SEC-T820-01) |
| A06: Vulnerable Components | Yes (SEC-T814-01, Brave, Node floors) | 0 new (SEC-T814-01, SEC-T825-02 and SEC-T784-01 fixed; SEC-T825-01 (a) tracked) |
| A07: Auth Failures | Yes (token posture, T812) | 0 |
| A08: Data Integrity Failures | Yes (hash-locked gate install, clean clone, runner routing) | 0 |
| A09: Logging & Monitoring | Yes (SEC-T796-01 redaction) | 0 |
| A10: SSRF | Yes (Playwright blocked origins unchanged, `servers.yaml:112`; Brave forced stdio, `:142`) | 0 |
