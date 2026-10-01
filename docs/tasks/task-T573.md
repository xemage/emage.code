# T573 — Apply the gate-verdict consistency edits (T572 FU-1)

**ID:** T573
**Owner:** Backend Developer
**Status:** in_review
**Priority:** P2
**Tier:** mechanical
**Affects:** skill/code-review, skill/testing-strategy, skill/project-planning, agent/tech-lead, agent/orchestrator
**Depends on:** T572
**Created:** 2026-10-01
**Based on:** `docs/artifacts/gate-verdict-consistency-v1.md` §10 (edits E1–E7), §11 and §13 (the orchestrator's rulings);
`docs/plans/plan-096-gate-definition-consistency.md`.

## 1. What and why

T572 ruled that the repository's gate-verdict formats can be reconciled without ranking any document over another:
- The one-line `[VERDICT]` markers *accompany* the canonical `validation-gates` block.
- Gate names map onto that skill's five kinds.
- `project-planning` must stop calling plan approval a validation gate, following the user's P36 decision.

The orchestrator accepted the rulings in §13.2. This task applies **E1–E7 exactly as specified**. Nothing is left
to decide.

## 2. The edits

Apply each edit from artifact §10 by matching its exact **before** text and replacing it with its exact **after**
text. Copy both from the artifact's fences programmatically; do not retype them. Before applying, assert that each
before-block occurs exactly once. If one does not match, stop and report.

Where an edit is an **insertion**, its fence label says so. Insert it at the stated anchor, and assert that the anchor
occurs exactly once.

Check the result by content, not by counting diff hunks. For each file, applying every before→after pair to
develop's version must reproduce your file exactly.

The files:
- `implementation/knowledge/skills/code-review/SKILL.md`
- `implementation/knowledge/skills/testing-strategy/SKILL.md`
- `implementation/knowledge/skills/project-planning/SKILL.md`
- `implementation/knowledge/agents/tech-lead.md`
- `implementation/knowledge/agents/orchestrator.md`

## 3. Regenerate and declare

1. Run `node implementation/scripts/sync.mjs --root implementation` **and**
   `python3 implementation/scripts/generate-registry.py`.
2. Run `python3 -m tests.functional.test_root_install_parity --print-drift`. Add **exactly** the reported root paths
   to the `drift` list in `tests/_baselines/root-install-drift.json`. That list is **empty** on develop after the
   second refresh, so it will hold only this task's paths. Never hand-edit the top-level platform folders.

## 4. Verify, don't assume

- `sync.mjs --check` and `generate-registry.py --check` are clean, and the root parity gate is green.
- `gate=plan-review` and "Approval is a validation gate" have **0** hits under `implementation/knowledge/`.
- `implementation/knowledge/skills/validation-gates/SKILL.md` and `implementation/knowledge/commands/validate-workflow.md`
  are **byte-unchanged**.
- The audience lint passes.
- `check-maturity.py --root implementation` reports 79 components, 0 failing, with an **unchanged** distribution:
  agents 26/2, commands 14/5, skills 7/19.
- `scorecard.py --check` is OK (34/26/0), and the digests still match **v15**.
- `validate-tasks.py` passes.
- `python3 tests/run.py`: check the exit code, with output redirected to a file and never piped to `tail`. The
  baseline is **904 OK**.

## 5. Constraints

- **Write scope:**
  - the five source files, at the artifact's sites only;
  - the regenerated `implementation/.<platform>/` mirrors and `implementation/registry/`;
  - the `drift` list in `tests/_baselines/root-install-drift.json`;
  - this brief's `**Status:**` line.
- **Do not touch `tests/golden/**`, and do not open it.** Any search that covers `tests/` must prune
  `tests/golden/held-out` before traversal (plan-093 §5).
- Do not touch `scripts/scorecard.py`, the evaluator-hash files, `validation-gates`, or any command.
- Commit locally as one commit. **Do not push. Never run `glab mr merge` or any merge/approve API.** There is no
  exception to this. Hand everything back.

## 6. Blocker protocol

Report blockers as `technical` | `dependency` | `unclear_requirements` | `external`, with severity `critical` |
`major` | `minor`. If an artifact before-text no longer matches, report it rather than working around it.
