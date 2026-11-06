# plan-144 — Tracked-debt register v11

**Created:** 2026-11-06
**Based on:** `docs/artifacts/tracked-debt-register-v10.md` (573 ids), `docs/plans/plan-142-verdict-check-tokens.md` § Outcome, `docs/plans/plan-143-batch-s-rest.md` § Outcome, `docs/artifacts/security-review-t748-batch-t-v1.md`, `docs/artifacts/security-review-t751-batch-s-rest-v1.md`. The user's answer of 2026-11-06, verbatim: "\"v11 go".
**Scopes:** `T752`.

## Goal

Plans 142 and 143 closed batch T and most of batch S and opened new ids that only their review records track. A second gate probe ran after them. v11 takes all of that over, so a release can start from one current list.

## Facts since plan-143 (the orchestrator's record)

These facts appear in no other artifact, so this section is their source.

**The second gate probe (2026-11-06).** The user answered, verbatim: "probe go". Annotated tag `v9.0.0-gate.2` on `035bf433`, a commit on top of `9c7f2fad` that was never merged and whose branch was never pushed. It changed only the three marker files and added a release document copied from v9.0.0. Before the push, the docs gate and the drift check passed locally and the tree check exited 1. Pipeline 3038460622 ended `failed`, as designed. Runner 19.5.2.

| Job | Id | Result |
|---|---:|---|
| `release-docs-gate` | 17821516208 | success, 9.7 s: `rm -rf .git "${CI_PROJECT_DIR}.tmp"` ran, pip and the gate ran through `scripts/run-allowlisted.py`, and the runner's cleanup showed no error |
| `main-develop-drift-gate` | 17821516209 | failed as designed: `apk`, both fetches under `--keep CI_JOB_TOKEN` and the drift check passed through the script, then `check-release-tag-tree.py` refused the tag |
| `release` | 17821516210 | skipped; no GitLab Release was created |

What the probe does not prove:
- **The credential path.** The project's visibility is `public` (read through the API on 2026-11-06), so the fetches may be anonymous. They show that the allowlist does not break a fetch here, not that `--keep CI_JOB_TOKEN` is needed or works.
- **That the credential is gone.** The log shows the removal ran. That it was the right path rests on source reading of the runner, and the flag `FF_GIT_URLS_WITHOUT_TOKENS` on this runner is unknown.
- **The `timeout`,** which was not reached.
- **The `release` job and its clone setting,** which did not run. `scripts/publish-release.py` has changed since v9.0.0, so the `CHANGELOG.md` entry below `[Unreleased]` (D-T710-2) and the escaped references are still unobserved.
- **The parser's version.** The install is quiet; the hashes are what tie it to the lock.

**The probe tags.** Both `v9.0.0-gate.1` and `v9.0.0-gate.2` were still on the remote when this plan was written, and only the web interface can delete a protected tag. The local tags are deleted. A pre-release sorts below its core version, so `resolve_previous_tag` still returns `v9.0.0` for `v10.0.0`.

**A flaky test, TD-T746-01 (the orchestrator's id, never graded by a reviewer).** `test_temp_file_has_the_old_mode_before_any_content_is_written_and_a_random_name` (`tests/functional/test_merge_mcp_json_robustness.py:169`) asserts that the process id is not in the temp file's name. In CI the process id was `49` and the random name `.dest.json._4498eko.tmp` held it, so `unit-tests` failed once on MR !649 (job 17812330179). A retry on the same commit passed. Measured over 20,000 `mkstemp` names: about 0.5% per run with a two-digit process id. The MR changed only files under `docs/`.

**Agents used the remote Docker host, unasked.** T750, as T728 did, ran containers through `docker`. `DOCKER_HOST` points at `ssh://root@10.10.160.11`, which also runs the user's `portainer` and `hindsight`. After T750 and after plan-143's merge only those two containers exist there. The orchestrator's brief did not forbid it. It told the user. Later briefs forbid `docker` unless the user approved it.

## Task Decomposition

1. **T752** (tech-lead): write `docs/artifacts/tracked-debt-register-v11.md`, a delta on v10. Keep v10's section numbering where a section still applies. Do not repeat a row for an id that did not change: v10 and earlier stay the record of its text.
   - **Ids that changed since v10.** One row each, with the citation. Closed by plan-142: SEC-T739-07. Closed by plan-143: SEC-T745-01 to -11, the rest of TD-T739-01. SEC-T741-17 stays open in part: its dedicated runner tag needs a runner, which is the user's to provide.
   - **Ids that did not change.** Account for every other v10 `open`, `tracked-LOW` and `accepted` id, compactly, as "Unchanged".
   - **One row for every new id, with the review record's grade and final status.** Take the status from the later source: review T751 § Q7 and plan-143 § Outcome change what review T748 left.
     - SEC-T748-01 to -13. Fixed in review T748: -01, -02, -10, -11. Closed on the gate's route by plan-143: -02, -13. Narrowed by plan-143: -04, -12. Say what each one still leaves.
     - SEC-T751-01 to -09. Fixed in `6c58244b`, not re-read by the reviewer: -02, -03, -04.
     - TD-T746-01, above.
     - Search the lines added in `06b903aa..9c7f2fad` for any other id an artifact mints.
   - **The user's decisions since v10, quoted verbatim:** "T go"; "Sgo"; "probe go"; "\"v11 go". Each row claims only what these plans record.
   - **The orchestrator's rulings since v10**, marked as not the user's: plan-142 § Outcome and review T748's rulings 1 to 5; plan-143 § Outcome (the exact skip paths, refusing the nesting limit, the temp directory in the removal, stopping fix rounds on LOW).
   - **Corrections for the orchestrator's errors recorded there.** Plan-142's design and first fix, plan-143's two design errors, and the two invalid or unconfirmed runs stay on the record. Do not soften them.
   - **Mark what GitLab's Markdown API observed** (review T751, closing section) against the findings it touches. It is the Markdown API; a Release description stays **(unverified)**.
   - **The open items as batches.** Keep I, J, K, L, M, N, P, Q, R, F and U with their v10 scope.
     - **T** ends: its one id is closed.
     - **S** keeps SEC-T741-17 only, and it waits on the user's runner.
     - **V, new:** the release gate after plans 142 and 143: SEC-T748-03, -04, -05, -06, -07, -08, -09, -12 and SEC-T751-01, -05, -06, -07, -08, -09, which is 14. Mark any order you give as your suggestion. No source binds V to a release. Note what the orchestrator's run says about SEC-T751-06.
     - **W, new:** TD-T746-01.
     - The route of SEC-T735-06 and -07 is still to be settled before batch R; carry that.
     - Re-read the current lines of batch N ids that point into `scripts/verify-release-docs.py` and `tests/functional/test_ci_hash_pins.py`: plans 142 and 143 moved them. Do not re-rule them; report any id they made stale.
   - **Next release checklist:** carry v10 § 6.2 and change only what these plans changed.
     - **Item 14:** the second probe ran the docs gate's new lines. Keep watching at the next tag, and say what remains.
     - **Item 21 retires:** the `unset` line and `GATE_CREDENTIALS` are gone. Say what replaces it: the allowlist in `scripts/run-allowlisted.py`, and a test that holds it equal to `release`'s.
     - **Item 22 widens:** a release document may hold no HTML other than comments, anywhere, not only before its Cursor item.
     - **Add:** the gate's other limits, with their values: 131072 characters and the parser's nesting limit. Prose such as `<your-project>` outside code is refused. A placeholder in a code span passes, so replace it with its value.
     - **Add:** `scripts/run-allowlisted.py` is code that every gate command passes through, and no pin reads it, so a change to it is for code review.
     - **Add:** the first real tag pipeline's watch list, `CONTRIBUTING.md`'s rehearsal, with the probe's limits above.
     - **Add:** no `docker` in an agent's brief unless the user approved it.
     - Re-read every line citation in § 6.2 that points into `scripts/verify-release-docs.py`, `.gitlab-ci.yml` or `tests/functional/test_ci_hash_pins.py`.
   - **Dates:** carry v10 § 6.3.
   - **User actions:** carry v10 § 7. A-19 widens to both probe tags. Check it with `git ls-remote --tags` when you write, and say what you found. Add: a dedicated runner, for SEC-T741-17.
   - **What stays unverified:** carry v10 § 8, drop what the second probe or the Markdown API settled, and add the probe's limits above and the two reviews' lists. Keep separate what a real job proved, what GitLab's APIs proved, and what is hand trace.
   - *Acceptance:*
     - every v10 id that was open, tracked-LOW or accepted is accounted for, and every new id has a row;
     - each status claim can be traced, or is marked **(unverified)**;
     - the counts add up and no open item is above LOW, or the register says so. Expected from the sources, to be checked and not assumed: 596 ids, 469 fixed, 46 accepted, 6 obsolete, 1 open, 74 tracked-LOW; batches I 10, J 1, K 7, L 5, M 12, N 8, P 1, Q 3, R 4, S 1, V 14, W 1, F 2, U 6, which is 75. Report any difference with the reason;
     - `validate-tasks.py`, `test_link_integrity` and the team-health tests pass.

## Constraints

- The tech lead is read-only on source. T752 writes only the artifact.
- No `docker` command. Do not read the CWSO repository. Its statuses carry over from v10.
- Never open `tests/golden/held-out/`; a recursive search over `tests/` needs `--exclude-dir=held-out`. Read no `.env*` or credential file.
- Run no mutation, and no full suite. A test run has a time limit.
- Subagents never merge. The orchestrator verifies the artifact and merges on a green pipeline.

## Outcome (2026-11-06)

- **T752 is done.** The register is `docs/artifacts/tracked-debt-register-v11.md`. It holds 596 ids, 573 from v10 and 23 new:

  | Status | Ids |
  |---|---:|
  | fixed | 469 |
  | accepted | 46 |
  | obsolete | 6 |
  | open | 1 (K-20) |
  | tracked-LOW | 74 |

- **Batches:** I 10, J 1, K 7, L 5, M 12, N 8, P 1, Q 3, R 4, S 1, V 14, W 1, F 2, U 6, which is 75. Batch T has ended. No open item is above LOW; TD-T746-01 has no reviewer's grade. The counts match this plan's expectation.
- **The orchestrator's check.** A separate parser of the section 5 tables of v10 and v11 gives the same size for every batch but S and T, and V and W are new. Each of the 23 new ids, SEC-T739-07, A-19 and A-20 has one row.
- **A correction of the orchestrator's record: SEC-T751-06 is real.** Review T751's closing section and plan-143's report said its hold "did not reproduce". The Tech Lead's run showed it does. The orchestrator then found why its own run was wrong: it wrote the crafted text into `docs/releases/v9.0.0.md`, which `install.sh` points to, and on that document the gate stops before `check_links`. Measured again on `cf9ab809`, whole gate, on a copy, with a memory cap, on a document no pointer names:

  | Text | Result |
  |---|---|
  | `[` x 131072, the pointed `v9.0.0.md` | exit 1 in 0.10 s |
  | `[` x 131072, unpointed | exit 1 in 7.89 s |
  | `[` x 262144, unpointed | exit 1 in 30.14 s |
  | `[` x 1048576, unpointed | over 100 s, stopped |

  So this resolves what the register marks **(unverified)** on the 0.1 s. `check_links` is outside the size cap, so a large document holds the job until `timeout: 10 minutes` and fails closed. The grade stays LOW. The merged review record stays as written, and this section is its correction.
- **Rulings on what the tech lead flagged.**
  - **SEC-T748-13 stays `fixed`,** closed on the gate's route. No caller reaches it outside `check_release_brief`, which refuses first, and the row says what a direct call keeps.
  - **`--help`'s "put it in a code span"** stands: it is about literal prose such as `<your-project>`.
  - **A-19's second tag.** The user asked for the probe knowing the tag is theirs to delete; the row's **(unverified)** can stand until it is gone.
- **The tech lead reports two careless acts in the shared scratchpad:** it overwrote a file `count.py` and removed a directory `copy/`, both of the orchestrator's earlier throwaway work and none of it in the repository.
- **Open for the user, not ruled here.** Whether any of batch V runs before the next tag; the route of SEC-T735-06 and -07, before batch R; A-19; A-20.
- **Token use.** T752 used about 204k tokens (the harness's count, which includes context) against a budget of 120k.
