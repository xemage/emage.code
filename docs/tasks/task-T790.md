# T790 — Fix the code behind QA-T760-01 to -03 (`context-retriever`)

**ID:** T790
**Owner:** backend-developer
**Status:** done
**Priority:** P1
**Tier:** standard
**Depends on:** —
**Affects:** —
**Created:** 2026-11-12
**Completed:** 2026-11-12
**Based on:**
- `docs/plans/plan-151-context-retriever-code-residue.md` (task T790)
- The user's instruction of 2026-11-12, verbatim: "Continue with the next best step"
- `docs/artifacts/qa-release-v10-v1.md` (QA-T760-01, -02, -03; C1); `docs/artifacts/tracked-debt-register-v13.md` § 5 batch Z

## 1. What and why

Fix the three code residues as specified in plan-151 § Task Decomposition item 1: the printed install note, the refusal of a `--project-id` that is not in the derived lower-case form, and a per-platform `--platform-root` in the generated entries.

## 2. Output

Commits on `agent/backend-developer/T790` in `../worktrees/agent-backend-developer-T790`, and a report: what changed, the test results, the declared root drift paths, and any deviation.

## 3. Constraints

As plan-151 § Constraints. `scope_filter.py` does not change. No top-level platform folder and no file under `tests/golden/` changes.

## 4. Acceptance criteria

- QA's three reproductions no longer fail the way `qa-release-v10-v1.md` records.
- `node implementation/scripts/sync.mjs --root implementation --check` and `python3 implementation/scripts/generate-registry.py --check` pass.
- `CI=true python3 tests/run.py` passes.

## Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
