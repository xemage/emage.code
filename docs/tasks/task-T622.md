# T622 — Plan the re-evaluation and promotion of orchestrator and tech-lead, and the golden realignment under baseline v21

**ID:** T622
**Owner:** solution-architect
**Status:** pending
**Priority:** P1
**Tier:** judgment
**Depends on:** —
**Affects:** —
**Created:** 2026-10-09
**Completed:** —
**Based on:**
- `docs/plans/plan-120-release-v8-readiness.md`
- `docs/artifacts/maturity-promotion-criteria-v2.md` (§3.1 agent criteria, §3.5 defect check), `agent-promotion-rerun-v1.md`, `promotion-rule-v1.md`, `phase3-wave3-promotion-v1.md`, `command-promotion-readiness-v1.md`
- `docs/artifacts/protected-paths-v1.md` (§5 file-scoped grants), `docs/artifacts/evaluator-hash-check-v1.md`, `docs/artifacts/evaluator-hash-known-good-v20.json`, `implementation/runtime/golden_harness/evaluator_hash.py`
- `tests/golden/README.md`, the open cases with `status: known_failing` (`code-review-conditional-pass-conditions-gap`, `prepare-release-conditional-pass-conditions-gap`, `prepare-release-real-verdict-missing`, `plan-real-doc-header-drift`, `skillify-skill-file-template-drift`, `security-audit-critical-not-fail`) and `tests/golden/open/new-project-plan-doc-and-lifecycle-states/brief.md` (stale version-format quote at `:65-66`)
- `docs/artifacts/remaining-verdict-renderings-v1.md` §8 (P41 O3: `prepare-release-real-verdict-missing` reads its verdict from a release checkpoint while `/prepare-release` now puts it in the release notes document; ADR-007 branch 2 shape)
- `docs/decisions/ADR-007-command-contract-authority.md`, `ADR-008-knowledge-document-authority.md`
- The user's decisions of 2026-10-09 on the release-readiness question (verbatim): "1. A  2. A  3. A  4. approving baseline v21 - plan re-evaluation and steps to bring them out of experimental  5. C  6 B" (point numbers refer to the orchestrator's message listing six open points: 1 breaking changes and migration notes = release-level audit and Migration section; 2 release-level gates and sign-offs = the full sequence; 3 CI release job's third release-notes.md = fix first; 4 maturity = the user authorizes evaluator baseline v21 and asks for a re-evaluation plan and the steps to bring `orchestrator` and `tech-lead` out of `experimental`; 5 known residuals = fix all first; 6 plumbing = API fallback plan for branch and tag steps).

## 1. What and why

`orchestrator` and `tech-lead` are the only two `experimental` agents. The user authorized baseline v21 and asked for a re-evaluation plan and the steps to bring them out of `experimental`. Re-evaluate from the live repository (do not trust the old artifacts): for each of the two agents, which `beta`/`stable` criteria of §3.1 hold and which fail today, with evidence (the command(s) they own, the golden cases scored for those commands and their `status`, the open `P0`/`P1` defects that name the agent in `**Affects:**`, wiki and cross-reference checks). For every blocking `known_failing` case (and the others listed): classify it (`tracked_defect`: fixable by correcting a command/skill/agent text or the case's own contract; `capability_gap`: the evaluated model cannot comply and text changes will not fix it) with the evidence for the classification, and propose the minimum honest step to clear or re-classify it WITHOUT weakening a test to force a pass: fix the knowledge text, correct a golden case contract under a file-scoped grant (P41 O3 and the stale brief quote are the known ones), re-run the evaluation, or document why a capability gap does not block promotion under the criteria as written (a criteria change is a user decision, not yours). Then specify the golden realignment: the exact files per step, the order, the protected-paths §5 grant text(s) for the user to approve, the exact procedure and checks to create `evaluator-hash-known-good-v21.json` (digest of `tests/golden` and `scripts/scorecard.py`) and repoint `evaluator_hash.py`, the scorecard expectations (cases, pass/known_failing counts) before and after, and how held-out isolation stays intact (never open `tests/golden/held-out/`; held-out case ids are not written anywhere). Finally the promotion steps (frontmatter `maturity:`, `# maturity-evidence` tags if used, registry/mirror regeneration, `check-maturity`), the tasks (owner, size, dependencies) that implement them, and the risks. Decision and plan only: apply nothing. If a step needs a user decision (criteria change, a case that cannot honestly pass), put it in ONE consolidated user question with options and a recommendation each.

## 2. Output

`docs/artifacts/promotion-and-golden-realignment-plan-v1.md`: current criteria status table for both agents, case-by-case classification, the step list with grants and v21 procedure, the proposed task list, risks, the consolidated user question and a summary table.

## 3. Constraints

- **Read access:** the whole repo, except `tests/golden/held-out/`, `.env*`, and any credential or key file. Never open `tests/golden/held-out/`; never write a golden case name unless that case has a `tests/golden/open/` directory.
- **Write access:** your artifact, plus this brief's `**Status:**` line (set it to `in_review`).
- You have no shell. Do not commit, push or merge. Do not edit `.claude/`, `.github/` or the other derived platform folders.
- Quote verbatim, mark omissions with "…", and mark anything you did not re-read **(unverified)**.

## 4. Acceptance criteria

1. Exactly one file is written, with `Based on:`.
2. Every blocking criterion for both agents has evidence and a step or an explicit user decision.
3. No golden or knowledge file is edited; no golden case name appears unless it has a `tests/golden/open/` directory; held-out ids are not named.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
