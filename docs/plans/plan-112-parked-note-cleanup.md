# plan-112 — Mechanical cleanup of the parked notes (T601) under a user-approved v20

**Created:** 2026-10-08
**Based on:** the user's decisions of 2026-10-08 ("Approving v20 baseline"; "Batch the small notes into one cleanup
task"); the parked notes in plans 106, 109 and 111.
**Scopes:** `T601`.

## 1. In the batch (mechanical)

T601 covers five notes, each of which restates something so it is true again:
- the isolation-test docstring that still says the `new-feature` brief names a held-out sibling;
- a helper test that still uses a `feature-x.md` filename;
- the `evaluate-poc` case brief's discrimination section, which lacks the table probes;
- the `validate-workflow` brief's provenance grep, scoped to an old commit;
- one stale fixture field (`Release manager: orchestrator`) in a case whose check never reads it.

No `check()` and no result changes. Three of the edits touch protected golden briefs or fixtures, so v20 is needed.
The orchestrator writes it after independent verification.

## 2. Not in the batch (each needs a decision or is not worth a root refresh)

| Note | Why it stays parked |
|---|---|
| `coding-standards` `-vN` naming vs `AGENTS.md` (P32 O1) | A conflict inside tier 1. |
| `/new-project` checkpoint and decision naming (P32 O2) | A command against `AGENTS.md`. |
| `/new-feature:25` Scrum Master creates tasks (P32 O5) | A command against the Task Protocol. |
| CI's third `release-notes.md` (P32 O6) | Tooling, not knowledge text. |
| `prepare-release-real-verdict-missing` reads its verdict from a checkpoint (P41 O3) | A golden-case contract question (ADR-007). |
| `orchestrator:249` pointing at `:205` (P41 O4); `scrum-master` task protocol (P41 O2) | Content judgements. |
| Narrator `<type>-vN.md` boilerplate; scan scope; `/evaluate-poc` severity source; category sets (P33 O1, O2, O5, O6) | Ruling needed. |
| `poc-orchestrator:102` indentation (P33 O4) | Cosmetic. Fixing it would force another root refresh; it waits for the next change to that file. |

## 3. Outcome (2026-10-08)

- **T601 merged** (MR !530, `develop` `a418839`), together with evaluator-hash baseline **v20**. The user approved
  v20, and the orchestrator wrote it after verifying the work independently. The five mechanical notes are closed.
- **The queue is empty**, and plan-112 is complete. The notes in §2 stay parked.
