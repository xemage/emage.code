# T623 — Release-level audit of v7.0.1..develop: breaking and behaviour changes for the v8.0.0 migration notes

**ID:** T623
**Owner:** tech-lead
**Status:** pending
**Priority:** P1
**Tier:** standard
**Depends on:** —
**Affects:** —
**Created:** 2026-10-09
**Completed:** —
**Based on:**
- `docs/plans/plan-120-release-v8-readiness.md`
- `git log v7.0.1..develop` (about 409 commits), `docs/tasks/completed-tasks.md` (tasks T514..T618 completed since v7.0.1; read the rows after the v7.0.1 content), `docs/releases/v7.0.0.md` and `v7.0.1.md` (structure and the Breaking changes precedent)
- `implementation/knowledge/skills/release-workflow/SKILL.md` (changelog format, gate checklist) and `implementation/knowledge/commands/prepare-release.md`
- `docs/decisions/` (ADRs since v7.0.1), `docs/artifacts/` security reviews and rulings from 2026-09-19 onward
- The user's decisions of 2026-10-09 on the release-readiness question (verbatim): "1. A  2. A  3. A  4. approving baseline v21 - plan re-evaluation and steps to bring them out of experimental  5. C  6 B" (point numbers refer to the orchestrator's message listing six open points: 1 breaking changes and migration notes = release-level audit and Migration section; 2 release-level gates and sign-offs = the full sequence; 3 CI release job's third release-notes.md = fix first; 4 maturity = the user authorizes evaluator baseline v21 and asks for a re-evaluation plan and the steps to bring `orchestrator` and `tech-lead` out of `experimental`; 5 known residuals = fix all first; 6 plumbing = API fallback plan for branch and tag steps).

## 1. What and why

The user wants a major release (v8.0.0), which needs a migration guide. You are reviewing, not changing code (`AGENTS.md` § Validation Gates: review agents MUST NOT modify code during review). Produce the release-level inventory of what changed since v7.0.1 for adopters of the installed harness: (a) **breaking or behaviour-changing changes** (tool grants removed or added to an agent; new or changed MCP servers and the client configuration they need, for example the `poc-security-audit` server and the client-owned allow rule `mcp__poc-security-audit__*` and the Python `mcp` dependency; changed severity scale, ledger columns and statuses, artifact/checkpoint/plan naming, installer behaviour, command contracts, golden/scorecard contract, scripts); (b) new features; (c) fixes; (d) improvements/docs/internal. For each entry: what changed, who is affected (which platform projections, which adopter action is needed), evidence (task IDs, MR numbers, file paths, ADR or artifact), and whether it is breaking for a downstream install (yes/no/unclear, with the reason). Separate what you verified (files read, diffs inspected) from what you inferred from titles. Draft the **Migration section** text for `docs/releases/v8.0.0.md` (actions in order: `--update`, client settings, dependencies, renamed conventions) and a **Known issues** list. Also list open concerns for the release gates (anything you saw that looks inconsistent: stale version claims, release-process documents that disagree, scripts that would fail on a major bump). Do not write the release notes themselves; do not touch version files. Tasks merged after today will be covered by an addendum; note the last task and commit you covered.

## 2. Output

`docs/artifacts/release-v8-audit-v1.md`: coverage statement (range, last task and commit), the categorized inventory, the drafted Migration section and Known issues, the open concerns for the gates, and an explicit list of what you did not verify.

## 3. Constraints

- **Read access:** the whole repo, except `tests/golden/held-out/`, `.env*`, and any credential or key file. Never open `tests/golden/held-out/`; never write a golden case name unless that case has a `tests/golden/open/` directory.
- **Write access:** your artifact, plus this brief's `**Status:**` line (set it to `in_review`). You may use read-only shell commands (`git log`, `git diff`, `grep`); do not modify any other file. Do not commit, push or merge.
- Quote verbatim, mark omissions with "…", and mark anything you did not re-read **(unverified)**.

## 4. Acceptance criteria

1. Exactly one file is written (plus this brief's `**Status:**` line set to `in_review`), with `Based on:`.
2. Every breaking-candidate entry names evidence and an adopter action; verified and inferred items are separated.
3. No source, script, version or release file is modified; no commit, push or merge.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
