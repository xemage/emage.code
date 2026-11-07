# Artifact: independent-check-t763-v1.md

> Immutable once produced; revisions bump `<N>`.

Based on: `docs/releases/v10.0.0.md` at `cd803b28`; `docs/artifacts/qa-release-v10-v1.md`; `docs/artifacts/security-review-release-v10-v1.md`; `implementation/knowledge/agents/release-manager.md:46`. The Tech Lead's report to the orchestrator of 2026-11-07, as given.

**Verdict: PASS at `cd803b28`.** Nothing must change before the tag, so this check does not need re-running on account of my findings. They are two LOW items, both trackable.

For the `Independent check` row: `PASS at cd803b28, by tech-lead`. I authored and edited none of the release files.

**This PASS does not cover one thing:** whether the four acceptance lines match the questions actually asked. I can't see that exchange (BLK-T762-02), and security condition 1 gives the comparison to the top-level session, including the "asks for a fix" sentence, which the security reviewer took from your brief alone. Please do that comparison before you rely on the row.

### What I ran
All runs were on a throwaway target or in my scratch subfolder, each under `timeout`. The worktree stayed clean, HEAD stayed at `cd803b28`, and only my subfolder `t763-check` was deleted. No assistant, `docker`, mutation or full suite.

| Run | Exit | Result |
|---|---|---|
| `pip install --require-hashes` of `ci/requirements-release.txt` in a venv | 0 | `markdown-it-py` 4.2.0, the locked version |
| `verify-release-docs.py --tag v10.0.0` | **1** | **Exactly nine `pending` lines, nothing else:** `Release:`, Status, Open blockers, Quality gates passed, Quality gates failed, Blocker IDs, Timestamp, Issued at commit, Independent check |
| `install.sh --platform claude-code`, remote `https://gitlab.example.invalid/Acme/Widget.git` | 0 | |
| Install note's dependency line, memory `requirements-mcp-server.txt` | 0 | |
| M-2's rebuild with those dependencies only | **1** | `ModuleNotFoundError: No module named 'yaml'`, as M-2 says |
| M-2's dependency line, `requirements.txt`, same venv | 0 | |
| M-2's rebuild, `--project-id acme/widget`, `--output-dir .../_index/acme-widget`, entry `project_id: acme/widget` | 0 | `wrote 1 chunks` |
| Stdio client with `.mcp.json`'s generated args (`initialize`, `tools/list`, `retrieve`) | 0 | `retrieve` listed, `isError` false, **the chunk returned** |
| `--project-id Acme/Widget`, entry lower case: build, then `retrieve` | 0 | Chunk **returned** |
| `--project-id acme/widget`, entry `project_id: Acme/Widget`: build, then `retrieve` | 0 | `wrote 1 chunks`, `"result": []`, `isError` false |

### Results by point
1. **My findings: applied correctly.**
   - -01 is in step 1, -02 in M-2, -03 at `README.md` and `docs/wiki/implementation-guide.md`.
   - -05 is at line 36, -06 is M-2's nested-group sentence, -07 is in K-18, -09 is at line 81.
   - **-04's order holds:** all seven lines outside the closed list are filled. I recounted 6 `F-`, 12 `X-` and 5 `A-` entries by script, matching 6, 12 and 5.
2. **QA-T760-01 to -08 and SEC-T762-01 to -03: applied as their records say, with no claim beyond what was run.**
   - I traced each new M-2 and M-3 claim to QA's record: the moved index, the kept entry not started, and the start with `HOME` set to the target.
   - `build.py` has no diff from v9.0.0. `install.sh:1225` and `:1693` hold.
   - K-35 separates what was run (Gemini) from what was read (Opencode, Pi, Cline), and says the same holds at v9.0.0. I did not re-run K-35.
   - The (unverified) marks stay on a move from a real v9 index, on no assistant having run, and on the kept entry not being started.
3. **M-2 as written works.** On a mixed-case remote with `.claude/`, the dependency line and the rebuild both succeed and a real retrieval returns the chunk. See TL-T763-01 on which value matters.
4. **Conditions block: correct.**
   - The four accepted lines match § "Text for T763's Conditions block" exactly (script comparison), apart from `risk_accepted_by=@user` in a code span.
   - No bare `@name` is left outside code, and the reviewer's note on a missed review is absent.
   - Every gate condition is carried or applied:
     - **QA:** C1 and C2 applied, C3 listed.
     - **Tech Lead:** C-1 applied, with -03 listed as your decision. C-2 is listed. -08, -10, -11, -12 and -13 are listed.
     - **Security:** -04 and -05 are listed, and conditions 2 and 3 are listed, with all five items of condition 2 present. Condition 1 is the comparison above.
   - **Still owed before the tag:** telling the user about TL-T761-03.
5. **Gate Verdicts rows: honest and clear.**
   - The paragraph and the Architecture row both say that no separate architecture gate ran and that the row follows v9's mapping only.
   - The Implementation row compresses my area results slightly; that is fair.
6. **Reader from v9: nothing misleading enough to hold the tag.** Backup comes first, `--projections-only` is warned against in the document and now in the README and the guide, and the Rollback Plan is consistent. Findings are below.

**Changes after this check.** Your list is exactly the closed list of `release-manager.md:46` and exactly the gate's nine lines, plus the verdict text. The verdict text may hold only the opening paragraph, Gate Inputs, Justification, Conditions, Blockers, Changelog Preview and the user's decisions. **Any other change makes this check stale.**

### Findings
Neither needs to change before the tag. If you edit the file again for another reason, add both, because outside the closed list that edit makes this check stale anyway.

| ID | Severity | Location | Finding | Fix |
|---|---|---|---|---|
| TL-T763-01 | LOW, track | `docs/releases/v10.0.0.md`, M-2's "Use lower case" sentence; `docs/artifacts/tech-lead-release-v10-v1.md` TL-T761-02; `docs/artifacts/qa-release-v10-v1.md` QA-T760-02 | **The value that causes the empty result is the entry's `project_id`, not `--project-id`.** My TL-T761-02 got this wrong, from reading alone, and my artifact is immutable. The document's advice is still safe and complete, because it says lower case in all three, and QA's run used `Acme/Widget` for both. It does blur which value matters. `--project-id` still counts for shared scope (`build.py:148`, read). | Next register: correct the record. Next edit: "in your entries' `project_id`, which is what the server compares". |
| TL-T763-02 | LOW, track | `docs/releases/v10.0.0.md`, M-2 "Action" | M-2 has no pointer to K-35. A reader on an install without `.claude/` follows M-2 and `retrieve` still fails. It is not a regression, since v9 behaves the same per QA, and K-35 states it plainly. | Next edit: "On an install without `.claude/`, see K-35." |

### What I marked (unverified)
1. The acceptance words and question text against the real exchange (see above).
2. K-35 itself, and the behaviour of the Opencode, Pi and Cline entries: QA's run and reading, not mine.
3. QA's other runs that I traced to its record and did not repeat, including M-3's server start and `git ls-remote` for K-32.
4. Retrieval through a real assistant, and a move from an index really built by a v9 install.
5. All tag-pipeline behaviour, as in `docs/artifacts/tech-lead-release-v10-v1.md`.
6. The diff's remaining text beyond the points above. I read the whole diff, but K-29's and K-34's technical claims stay T762's.

No blockers. I changed nothing in the repository.

[VERDICT] gate=code-review | result=PASS | reviewer=tech-lead | artifact_ref=docs/releases/v10.0.0.md@cd803b28 | date=2026-11-07

## Orchestrator's note

The comparison this check leaves to the top-level session, the acceptance lines against the questions as asked, is recorded in `docs/artifacts/security-review-release-v10-v1.md` § "Orchestrator's record after this report".
