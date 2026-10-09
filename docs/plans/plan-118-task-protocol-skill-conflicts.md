# plan-118 — Rule the task-protocol conflicts in four skills (T613 §7 observations)

**Created:** 2026-10-09
**Based on:** the user's instruction of 2026-10-09, "Continue with the four-skill ruling";
`docs/artifacts/task-protocol-and-checkpoint-name-ruling-v1.md` §7 (observations) and §4.3;
the user's decisions of 2026-10-09 on the same class of conflict (T607 O5, T613 S1/S2: the orchestrator writes the ledger, entries use the seven ledger columns).
**Scopes:** `T615`, `T616`.

## 1. Why now

The Scrum Master and checkpoint-name conflicts are ruled and applied. The same ruling's observations list four skills with the same
shape: they let an agent write the ledger, or assume ledger fields and values that `AGENTS.md` does not define. Ruling them completes
the task-protocol alignment the user has been deciding.

## 2. Sequence

1. **T615** (solution-architect, decision only): one artifact with D5 records and at most one user question.
2. Orchestrator verification; the user decides; a separate implementation task applies the approved edits, then one user-approved root refresh.

## 3. Not in scope

R-1, the other plan-112 §2 notes, the held-out check, the stale golden quote.

## 4. Outcome of the ruling (2026-10-09)

T615 found no tier-1 conflict (the `BlockedBy`/`Blocks` columns are not a P5 case: only `AGENTS.md:14` speaks to the columns and lists seven; the user's T613 S2 decision settles the schema). The user chose every recommended option (verbatim labels: items 1, 5, 6 "Apply all three (Recommended)"; item 2 "Apply all (Recommended)"; item 3 "Apply (Recommended)"; item 4 "Apply (Recommended)"). T616 (backend-developer) applies the 20 fences; one user-approved root refresh follows. Further observations O-1..O-12 (blocker severity scale, `prepare-release.md:29` checkpoint name, `release-workflow` and `orchestrator.md:146` presupposing `done` rows in the active ledger, passive follow-up logging in four skills, and others) stay unruled.
