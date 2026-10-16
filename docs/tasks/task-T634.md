# T634 — Superseding note for ADR-008's contradictory status block and a single severity-scale reference (audit C-8)

**ID:** T634
**Owner:** solution-architect
**Status:** done
**Priority:** P1
**Tier:** judgment
**Depends on:** —
**Affects:** —
**Created:** 2026-10-14
**Completed:** —
**Based on:**
- `docs/plans/plan-121-release-v8-wave-2.md` (Task Decomposition item for T634)
- `docs/decisions/ADR-008-knowledge-document-authority.md` (the status block), `docs/decisions/` (the supersession convention: accepted ADRs are immutable, superseded decisions link to the replacement per `AGENTS.md` § Decision Log)
- `docs/artifacts/release-v8-audit-v1.md` C-8 and the Migration table M-6; the severity scales: bug severity, blocker (`critical|major|minor`), PoC debt (`critical|medium|low`), `SECURITY:*`, code-review (Must Fix/Should Fix/Nice to Have), `validation-gates`
- The user's approval of plan-121 on 2026-10-14 (AskUserQuestion, verbatim option label): "Approve as written (Recommended)", together with the decisions quoted in `docs/plans/plan-121-release-v8-wave-2.md` (header).

## 1. What and why

ADR-008's Status block says both "Accepted. The user approved it on 2026-10-02" and "Drafted for the user's acceptance ... Until it is accepted, no ruling may cite it as authority". An accepted ADR is immutable, so propose the smallest honest fix per `AGENTS.md` § Decision Log: a superseding note or a successor ADR that records the accepted status and states what is unchanged. Draft the exact text and the file name. Also draft one reference table of the coexisting severity/grade scales (names, values, what each grades, where defined, how they map or do not map) for a doc the orchestrator names. Decision only; held for the user. ONE question if a choice is needed (supersede in place via note vs a new ADR number), with a recommendation.

## 2. Output

`docs/artifacts/adr-008-status-and-severity-scales-v1.md`.

## 3. Constraints

- You have no shell (or only read-only commands where the brief says so). Do not commit, push or merge; the orchestrator does. Do not edit `.claude/`, `.github/` or other derived platform folders.
- **Write access:** your artifact(s) named in §2, plus this brief's `**Status:**` line (set it to `in_review`).
- Never open `tests/golden/held-out/` unless this brief explicitly authorizes it; never write a held-out case id anywhere (brief, report, commit message, branch name, ledger row, artifact); never write a golden case name unless that case has a `tests/golden/open/` directory. Run `python3 -m unittest tests.functional.test_golden_held_out_isolation` on every artifact before it is committed.
- No `.env*` or credential files; do not read the user's local `.claude/settings.json` or `.vscode/mcp.json`.
- Mark anything you did not re-read **(unverified)**.

## 4. Acceptance criteria

1. Exactly one file with `Based on:`; the exact held text is given.
2. No accepted text is edited.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
