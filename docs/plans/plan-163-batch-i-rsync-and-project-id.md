# plan-163 — Batch I part: the installer's equal-size skip (TD-T774-01) and the build's project-id check (QA-T818-03)

**Created:** 2026-11-14
**Based on:**
- `docs/artifacts/tracked-debt-register-v17.md` § 5 (batch I) and § 6.2 item 45
- `docs/artifacts/qa-gate-release-v11-v1.md` (QA-T818-01, QA-T818-03)
- `docs/artifacts/security-review-t820-release-v11-addendum-v1.md` § 1 and § 2
- `docs/releases/v11.0.0.md` (M-5, M-6, K-39)

**Scopes:** `T828`, `T829`.

## User decision (2026-11-14, verbatim)

The orchestrator listed the LOW batches and recommended batch I's installer fix for TD-T774-01, with QA-T818-03 alongside ("Tell me a batch letter, or "I go" for the installer fix"). The user answered:

> I go

The orchestrator reads this as the word for those two items of batch I, not for all 25. The other batch I ids, TL-T819-04 among them, stay tracked.

## Facts the user reported since register v17 (the orchestrator's record)

- **A-21: closed.** The project's only CI variable is `WIKI_TOKEN` (Protected, Masked, Expanded). The project is in the user's namespace, so there are no group variables. Instance variables cannot be checked on gitlab.com. On `gitlab-runner-16028`, `grep` for `feature_flags`, `FF_GIT_URLS_WITHOUT_TOKENS`, `tls-ca-file`, `helper_image` and `environment` in `config.toml` printed nothing. The `gitlab-runner-16027` config the user pasted earlier had none of these either. So SEC-T756-02 stays LOW.
- **A-22: done.** The user deleted the `gemini` auto-approve entry in their own `.vscode/settings.json`. `grep -n -i gemini .claude/settings.json` found nothing, and both files parse. SEC-T780-06 is fixed on the user's report.

## Goal

1. **TD-T774-01 / QA-T818-01** (`SECURITY:LOW`, regrade trigger in register v17 item 45). `scripts/install.sh` copies trees with `rsync -a` (`:926`, and `:976` with `--delete`). rsync's quick check skips a file whose size and mtime equal the target's, so a changed file of the same size can be left stale. QA reproduced this with the `opentelemetry-api` lock files. After the fix, a changed file is always copied, whatever its size and mtime.
2. **QA-T818-03** (`SECURITY:LOW`). `implementation/runtime/memory/build.py` checks only the form of `--project-id`. A wrong lower-case id gives a silently empty index. The installer's printed note (`scripts/install.sh:1746`) says "the build refuses any other", which overstates the check. After the fix, the build refuses an id that differs from the one derived from the workspace's `origin` remote, and the note is true.

## Task Decomposition

1. **T828** (backend-developer): both fixes, with tests. Brief: `docs/tasks/task-T828.md`.
2. **T829** (security-engineer, read-only): review T828. Brief: `docs/tasks/task-T829.md`.
3. **The orchestrator:** the gates, the full suite in a clean worktree, the merge request, and the merge, pinned and squashed on a green pipeline. If root drift appears, a root refresh needs the user's approval.

## Constraints

- No `docker`. Never open `tests/golden/held-out/`. `tests/golden/**` and `scripts/scorecard.py` are protected. Never read secrets or the user's settings files.
- The `--ignore-existing` copy at `install.sh:1171` keeps its meaning: it never overwrites an existing file.

## Outcome

**Done on 2026-11-14.**

- **T828** (backend-developer), commits `c9f282f9` and `f721814a`.
  - **Fix 1.** `--checksum` is added to the rsync calls of `copy_tree_into` and `sync_tree_into`. `merge_tree_preserve_existing` (`--ignore-existing`) is unchanged. A new regression test is `tests/functional/test_install_equal_size_copy.py`: without the fix it failed in 5 rsync subtests, and with the fix it passes.
  - **Fix 2.** `build.py` `main` refuses, with exit 2 and nothing written, a `--project-id` that differs from `derive_project_id(--own-repo-root)`, or any id when there is no `origin` remote. The messages are redacted. There are 6 new tests. The installer note and the memory README are corrected.
- **T829** (security-engineer): `docs/artifacts/security-review-t829-batch-i-v1.md`, **PASS**.
  - TD-T774-01 / QA-T818-01 and QA-T818-03 are **fixed**.
  - The regrade trigger of register v17 item 45 is retired, and the residue "three unidentified files" is obsolete.
  - The next release document may drop K-39 and M-6's check and workaround.
  - **New, LOW, tracked in batch I:**
    - SEC-T829-01: `derive_project_id` does not catch `TimeoutExpired`. Pre-existing.
    - SEC-T829-02: `_redacted` misses userinfo with a raw `/`. Pre-existing and contrived.
  - **SEC-T829-03** (the new `install.sh` comment's `--dry-run` and cost claims) is **fixed** by the orchestrator, with the wording T829 proposed. Not re-reviewed: the orchestrator's ruling. It is a comment-only change.

**Status for register v18, also from § Facts:** A-21 closed; A-22 done; SEC-T780-06 fixed on the user's report; SEC-T756-02 stays LOW.

**The orchestrator's own verification:** the gates, the full suite in a clean worktree, and the pipeline. The results are recorded in the merge request.

**Root drift:** none.

**Budgets:**

| Task | Used (about) | Budget |
|---|---|---|
| T828 | 151k | 100k |
| T829 | 127k | 60k |
