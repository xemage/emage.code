# Artifact: independent-check-t821-v1.md

> Immutable once produced; revisions bump `<N>`.

Based on:
- `docs/releases/v11.0.0.md` at `4ca11fa3` (the release tip where the release manager prepared the verdict, T821);
- the version marker commit `caa6cae0` (T815);
- `docs/plans/plan-160-v11-confirmation-sec-t660-t665.md` § Outcome;
- `docs/artifacts/security-review-t812-v11-no-harness-fix-v1.md` (lines 96, 98);
- `docs/artifacts/brave-audit-acceptance-v4.md` § Metadata;
- `docs/artifacts/security-review-t820-release-v11-v1.md` § 3;
- `implementation/knowledge/agents/release-manager.md:46` (item 5, the closed list);
- `implementation/knowledge/skills/validation-gates/SKILL.md:70` (§ Verdict Rules);
- my own review `docs/artifacts/tech-lead-release-v11-v1.md` (T819, `48c97514`).

The shape follows `docs/artifacts/independent-check-t763-v1.md`. The user's words (2026-11-13, option labels verbatim): plan-161 "Approve (Recommended)"; version "v11.0.0, MAJOR (Recommended)".

**Result: PASS at `4ca11fa3`.** Nothing must change before the tag. My one finding is LOW and can be tracked.

For the `Independent check` row: `PASS at 4ca11fa3, by tech-lead`. I have authored and edited none of the v11.0.0 release files. That covers the release document, the version marker files and the changelog. My only v11.0.0 artifacts are the T819 review and this check.

### What I ran

Everything ran in my scratchpad subfolder `t821`, each command under `timeout`. The worktree stayed clean, apart from this file, and HEAD stayed at `4ca11fa3`. I ran no `docker`, no mutation, no install and no suite.

| Run | Exit | Result |
|---|---|---|
| `pip install --require-hashes --only-binary=:all: -r ci/requirements-release.txt` in a fresh venv | 0 | `markdown-it-py` 4.2.0, the locked version |
| `verify-release-docs.py --tag v11.0.0` on that venv | **1** | **Exactly five `pending` lines, nothing else:** `- Release: pending` (Gate Verdicts), and `Status`, `Timestamp`, `Issued at commit`, `Independent check` (RELEASE VERDICT) |
| `scripts/check-version-consistency.py` | 0 | |
| Entry counts in the document | | F-01 to F-04 (4), X-01 to X-07 (7), A-01 to A-06 (6). These equal the filled values 4, 7 and 6, and none of these entries changed since `48c97514` |

### Results by point

1. **The prepared CONDITIONAL_PASS follows from the rules.** The three gate rows are CONDITIONAL_PASS: Implementation and Architecture from T819 by v10.0.0's mapping, Integration from T818, and Security from T820 with its addendum. None is FAIL. Three `SECURITY:MEDIUM` findings ship under the user's acceptance. Under § Verdict Rules, a shipped accepted MEDIUM yields CONDITIONAL_PASS at best, so CONDITIONAL_PASS is the most the verdict can be.
   - The Gate Inputs table names this check as "tech-lead, who has authored and edited no release file" and records its commit as "to be entered". Item 5 allows that row to change after the check.
   - The five pending values are all on the closed list of `release-manager.md:46`. Status, Timestamp, Issued at commit, Independent check and the `Release:` line may be filled after this check without making it stale.
   - Version and the three counts are already final.
2. **The three accepted-MEDIUM Conditions lines are complete**, slot by slot against T820 § 3.
   - **SEC-T660-01 meets every slot.**
     - The user's words "Accept for v11.0.0 (Recommended)", the date 2026-11-13 and the question dialog are given. The question is cited from plan-160 § Outcome, and the answer of 2026-11-12 is marked superseded.
     - Grade and release are given, and the plan as shown (owner the user and devops-engineer, "unchanged"; fix "none possible in the harness").
     - The four ADR-016 conditions are all there:
       1. the outside closer;
       2. the plain statement;
       3. the review date 2027-01-28 as the plan's deadline;
       4. T812, dated 2026-11-13 and new for v11.0.0, "came before the question, put on 2026-11-13".
     - The deadline is still ahead, with "v11.0.0 must ship before it".
     - The passed deadline is stated **in the line itself** (ADR-015 O5): "the sprint after v8.0.0", at the latest 2026-11-01. The acceptance it belonged to was for v8.0.0 ("Accept the risk, plan after the release (Recommended)", 2026-10-15, `v8.0.0.md:261`), and the line notes that v9.0.0 carried no new acceptance (T820 O-1).
   - **SEC-T665-01 meets the same slots.** It has no earlier deadline, and the line says so (T812:98). See TL-T821-01 for one wording point.
   - **SEC-T702-09 meets every slot.** The line has:
     - the three answers verbatim with their dates and plans, matching v4 § Metadata as I compared them in T819;
     - grade, release, and the plan (owner devops-engineer, "unchanged"; fix: the bump);
     - that ADR-016 does not apply to a bump;
     - forced stdio and the v4 record;
     - the deadline 2027-01-30 or the first Brave release above 2.1.4.
   - The other Conditions lines have an owner, a mitigation and a deadline each: T820 C-2 to C-4, T818 C1 to C3, the re-run on the final tree, SEC-T786-01, A-21 and the LOW list for register v17.
3. **The T826 and T821 edits since my review are correct** (`git diff 48c97514 4ca11fa3 -- docs/releases/v11.0.0.md`). I read each edit. Code is cited where checked; the other claims are recorded observations of other agents.
   - **TL-T819-01 met.** K-36 reports pipeline 3066689514, runner #59129270 (system ID `s_7371c6d24bcc`, 19.5.3), the pinned image that `allowed_images` accepted, both gates failing as designed, and `release` skipped. Its "Not proven" list covers the `release` job, the drift gate's credential path and the host tie **(unverified)**. K-32 names the probe tag and the deletion that must come before `v11.0.0`. Its deletion is **(unverified)**.
   - **TL-T819-02 met** in the Highlights: "with a notice when the folder carries the generator's marker".
   - **M-1 and M-2 cleanup order.** Server removal in `mcp.json` or `settings.json` comes first, because the manifest's `files` list also names the sidecar. Then the `files` deletion, then the manifest. This is consistent with ADR-013 and ADR-014 Appendix A, and keeps their content. QA's run of the order (QA-T818-02) is QA's record, not re-run here.
   - **M-5 is now accurate to the code.** `project_id_problem` (`build.py:51-61`) checks only the form, through `is_derived_project_id`, and does not compare the id with the remote. The installer note at `install.sh:1746` overstates the check, and the document says so.
     - My T819 review (Area 1) and T813's B-6 repeated that overstatement. QA-T818-03 caught it, and the release document is now right.
   - **M-6 lock check.** The glob `implementation/runtime/*/requirements-mcp-server.lock.txt` matches exactly the two lock files. The `touch` workaround is correctly marked **(unverified)**: it is QA's and was not run. The skip comes from the installer's `rsync -a` copy (K-39). That the `touch` cures it is my reading of rsync's quick check, size and mtime **(unverified)**.
   - **K-39** is consistent with M-6 and with the T820 addendum grade (LOW). Which three files were skipped is marked **(unverified)**.
   - **The "about 35 files" sentence** now says the count depends on timestamps (35, 33 or 30) and points to K-39. These are observations by the release manager and by QA, not re-run here.
4. **Version markers (`caa6cae0`):**
   - `README.md` changes `Latest release` and the per-release link to v11.0.0.
   - `docs/wiki/README.md`, `home.md` and `implementation-guide.md` change their markers and links.
   - `implementation/README.md` changes its two markers and its link.

   The nine changed lines replace `v10.0.0` with `v11.0.0` and nothing else. The consistency check exits 0. No source, CI or knowledge file changed between `67222765` (the gates) and `4ca11fa3`, only documents.

### Findings

| ID | Severity | Location | Finding | Fix |
|---|---|---|---|---|
| TL-T821-01 | LOW | `docs/releases/v11.0.0.md:323` (SEC-T665-01 Conditions line) | The outside closer reads "by an isolated OS user, container or VM, with encrypted or disabled swap and hibernation on the host for the at-rest part", after "mitigation=plan as shown". The swap and hibernation clause comes from T812:96. The question shown to the user names only "an isolated OS user, container or VM that you set up" (plan-160 § Outcome). The line is accurate in substance, and ADR-016 condition 1 is met either way, but a reader could take the clause as part of what the user was shown. | Track for register v17. At the next acceptance line for this finding, attribute the clause to T812, for example "(T812:96)". No change is needed before the tag. If the release manager wants to change it, it is Conditions text, which item 5 allows after this check. |

### What I marked (unverified)

- The observations of other agents: the throwaway-target counts, QA's cleanup runs, QA's `--project-id acme/other` run, and the lock-file skip.
- The `touch` workaround.
- The probe tag's deletion, and the tie between the system ID and the host.
- Any pipeline on `release/v11.0.0`: the Gate Inputs row says the same.
- Whether the acceptance lines match the exchange as it took place. I compared them with the records (plan-160 § Outcome, Brave v4 § Metadata), as T820 § 3 did. I did not see the dialog.
- A disclosure carried from T819: one grep there also named the root `.vscode/mcp.json`. It printed no line for that file, and nothing of it was seen. No settings file was read in this check.

[VERDICT] gate=independent-check status=PASS target=release/v11.0.0@4ca11fa3 findings=TL-T821-01
