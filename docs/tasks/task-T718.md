# T718 — Batch D: rulings and proposed ADR-011 (TD-T713-01)

**ID:** T718
**Owner:** solution-architect
**Status:** done
**Priority:** P1
**Tier:** standard
**Depends on:** —
**Affects:** —
**Created:** 2026-11-01
**Completed:** 2026-11-01
**Based on:**
- `docs/plans/plan-127-batch-d-knowledge-and-rulings.md` (task T718)
- The user's answer of 2026-11-01, verbatim: "D go"
- `docs/checkpoints/checkpoint-040-release-v9.0.0.md`; `docs/artifacts/tracked-debt-register-v4.md` (batch D rows; descriptions in v1 to v3)

## 1. What and why

(solution-architect): one rulings artifact, `docs/artifacts/rulings-batch-d-v1.md`, plus a proposed ADR for TD-T713-01.
   - **TD-T713-01.** Draft `docs/decisions/ADR-011-user-accepted-medium-at-release.md` with **Status: Proposed**. It weighs at least these options, with a recommendation:
     - (a) item 2 allows a `SECURITY:MEDIUM` to ship only under the user's explicit, recorded and time-bound acceptance, with a remediation plan; `security-guidelines.md` already asks for "a documented remediation plan before merge";
     - (b) item 2 stays as written, and v8.0.0 and v9.0.0 are recorded as user overrides of the policy;
     - (c) a separate override clause that names who may override and what must be recorded.
     The ADR names every knowledge file its acceptance would change: `release-manager.md` § Release Gate Policy, `validation-gates` § Verdict Rules, `prepare-release.md` step 9, and any other place that repeats the rule. Only the user accepts it (ADR-008).
   - **TD-T687-02 to -04.** Rule on the three severity-scale gaps in `docs/wiki/severity-and-grade-scales.md` § Known gaps item 5:
     - `qa-engineer` `P0`-`P3` against `AGENTS.md` `P0`-`P2`;
     - the unnamed scale in `release-workflow` § Hotfix Workflow ("critical or high");
     - the third casing of S5 and V1 in `security-engineer`.
     Each ruling gives the exact replacement text and the defining document under ADR-008.
   - **SEC-T693-02, -03, -05, -06, -09.** Rule on the release-gate wording, giving the exact replacement text:
     - -02: the effect on the verdict of a missing or FAIL independent-check row;
     - -03: one name for the checker in `orchestrator.md:218` and `release-manager.md:46,175`;
     - -05: the scope of "the document";
     - -06: Phase 5, where deployment comes before the Release Gate;
     - -09: list the fields that may change after the independent check, instead of naming the whole `## RELEASE VERDICT` section.
   - **SEC-T693-04.** Rule on the knowledge-text part, and draft the command part (`prepare-release.md`: the verdict block records a commit) as an option for the user. A command change needs the user under ADR-007.
   - *Acceptance:*
     - every id has a ruling, with exact text and file:line;
     - every ruling cites its authority (ADR-007, ADR-008, `AGENTS.md`), or says that the user must decide;
     - ADR-011 is Proposed and cannot be used as authority before the user accepts it.

## 2. Output

The changes or artifacts stated in section 1, and a closing report: per id, done (file:line) or not done (with the reason).

## 3. Constraints

- You have no shell. The orchestrator gives you a worktree path; edit files only inside it. Knowledge edits go under `implementation/knowledge/` only, never in a projection (`.claude/`, `.github/`, `implementation/.<platform>/` and so on). The orchestrator commits, runs `sync.mjs`, `generate-registry.py` and the gates, and merges. Do not edit `docs/tasks/active-tasks.md`, `completed-tasks.md` or any brief's Status line.
- Never open `tests/golden/held-out/`; never write a held-out case id. Never read any `.env*` or credential file, or the user's local `.claude/settings*.json` and `.vscode/mcp.json`. Mark anything you did not verify **(unverified)**.

## 4. Acceptance criteria

- every id has a ruling, with exact text and file:line;
     - every ruling cites its authority (ADR-007, ADR-008, `AGENTS.md`), or says that the user must decide;
     - ADR-011 is Proposed and cannot be used as authority before the user accepts it.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
