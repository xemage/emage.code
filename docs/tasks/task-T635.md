# T635 — Resolve the T625 review conditions C1-C3 (and the cheap Nice-to-Have items) for the release job

**ID:** T635
**Owner:** devops-engineer
**Status:** pending
**Priority:** P1
**Tier:** standard
**Depends on:** T625
**Affects:** —
**Created:** 2026-10-14
**Completed:** —
**Based on:**
- `docs/plans/plan-121-release-v8-wave-2.md` (Addendum: T635)
- `docs/artifacts/code-review-t619-v1.md` (Should Fix 1-3 = conditions C1-C3; Nice to Have N1-N5)
- `scripts/publish-release.py`, `scripts/dry-run-publish-release.py`, `tests/functional/test_publish_release.py`, `.gitlab-ci.yml`
- The user's approval of plan-121 on 2026-10-14 (AskUserQuestion, verbatim option label): "Approve as written (Recommended)"; follow-up created from the T625 review conditions C1-C3 (`docs/artifacts/code-review-t619-v1.md`).

## 1. What and why

The Tech Lead's `/code-review` of T619 returned `CONDITIONAL_PASS`: the conditions are due before the Release gate for v8.0.0 (C1 also before the v8.0.0 tag is pushed). Resolve:

- **C1:** the branch that strips a release document's own `# Release <tag>` title (`publish-release.py` around `:197-198`) is never exercised: add a test and a dry-run rehearsal with a template-shaped document (`# Release v1.2.3` as its first line) that asserts the description has exactly one top-level title line; the dry run on a copy of the real v8.0.0 document is repeated when it exists (a later release task). Do not change `docs/releases/_template.md`; if the template and the stripper disagree, report it.
- **C2:** `run_dry_run` in `scripts/dry-run-publish-release.py` takes five parameters; reduce to four (bundle `repo`, `source_dir`, `copy_changelog` into a small frozen dataclass or drop `repo`).
- **C3:** the three tests that assert the base `RuntimeError` (`test_publish_release.py` around `:165`, `:216`, `:226`) must assert the specific message (`assertRaisesRegex`) or the exact class.
- **Nice to Have, take the cheap ones:** N1 (assert `TAG_RE.pattern` equals the CI rule extracted from `.gitlab-ci.yml`), N2 (`os.chdir(work)` for the dry run, restored in `finally`; split on the real `"\n\n---\n\n"` separator), N3 (a trailing `--` after the revision in `git log`; validate `project_id.isdigit()` and `api_v4_url.startswith("https://")`; the token stays in argv for now, SEC-T619-05 stays tracked), N4 (a PUT-path test for `create_or_update_release`). N5 is a process note, nothing to do.

Constraints that must stay true: the description text and API calls for a valid tag are unchanged; no new network, shell or write surface; the dry run stays offline; never create, push or delete a tag or release; never use or print `WIKI_TOKEN`.

## 2. Output

The changed script/test files, a short report with the dry-run output (default and template-shaped), the gate results and the suite summary line.

## 3. Constraints

- Work in your own worktree/branch; one Conventional Commit ending with `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`. Do not push; do not merge; do not edit `docs/tasks/active-tasks.md`, `completed-tasks.md` or any brief's Status line; no root refresh.
- Gates to report: `sync.mjs --check`, `generate-registry.py --check`, `check-maturity.py --root implementation`, `scorecard.py --check` (34/26/0), `docs/tasks/validate-tasks.py`, the evaluator hash (baseline v20 unchanged), the held-out isolation test, and the full suite `python3 tests/run.py` redirected to a file.
- Never open `tests/golden/held-out/`; no `.env*` or credential files.

## 4. Acceptance criteria

1. C1-C3 resolved with tests that fail on a mutation (removing the strip branch fails the C1 test).
2. The cheap Nice-to-Have items done or listed as not done with the reason.
3. All gates and the full suite pass. A Security Engineer reviews the diff (the orchestrator dispatches it).

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
