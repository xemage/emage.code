# T795 — Fix batch O: SEC-T791-02, SEC-T791-03, QA-T792-1 (`context-retriever`)

**ID:** T795
**Owner:** backend-developer
**Status:** done
**Priority:** P2
**Tier:** standard
**Depends on:** —
**Affects:** —
**Created:** 2026-11-12
**Completed:** 2026-11-12
**Based on:**
- `docs/plans/plan-153-context-retriever-low-residue.md` (task T795)
- The user's instruction of 2026-11-12, verbatim: "O go"
- `docs/artifacts/tracked-debt-register-v14.md` § 5 batch O; `docs/artifacts/security-review-t791-context-retriever-v1.md`; `docs/artifacts/qa-recheck-t792-context-retriever-v1.md`

## 1. What and why

Fix the three tracked-LOW ids as plan-153 § Task Decomposition item 1 specifies: a stderr warning by path for every own-repo project-scope entry that names another project, a total `is_derived_project_id` that refuses dot segments, and a printed build command that runs in the printed venv.

## 2. Output

Commits on `agent/backend-developer/T795` in `../worktrees/agent-backend-developer-T795`, and a report: what changed, the test results, any declared root drift paths, any caller whose behaviour changed, and any deviation.

## 3. Constraints

As plan-153 § Constraints. `scope_filter.py` does not change. No top-level platform folder and no file under `tests/golden/` changes.

## 4. Acceptance criteria

- The failures recorded for SEC-T791-02, SEC-T791-03 and QA-T792-1 no longer occur, each with a test and a negative case.
- `node implementation/scripts/sync.mjs --root implementation --check` and `python3 implementation/scripts/generate-registry.py --check` pass.
- `CI=true python3 tests/run.py` passes.

## Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
