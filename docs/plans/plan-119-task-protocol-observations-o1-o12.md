# plan-119 — Rule the twelve observations of the T615 task-protocol ruling (O-1..O-12)

**Created:** 2026-10-09
**Based on:** the user's instruction of 2026-10-09, "Continue with the twelve observations";
`docs/artifacts/task-protocol-skill-conflicts-ruling-v1.md` §7 (O-1..O-12) and §4.6;
the user's decisions of 2026-10-09 on the same class of conflict (T607, T613, T615: the orchestrator writes the ledger; seven ledger columns; `AGENTS.md` names win over agents, skills and commands).
**Scopes:** `T617`, `T618`.

## 1. Why now

T615 listed twelve observations and ruled none. Several are real conflicts of the same shape the user has been deciding (blocker severity
scale, a command's checkpoint name, `done` rows assumed in the active ledger, passive follow-up logging). Others are Step A readings, a
typo, or lookalikes. One decision-only task sorts all twelve so nothing stays ambiguous.

## 2. Sequence

1. **T617** (solution-architect, decision only): one artifact, a disposition for every observation, D5 records for the real conflicts, and at most one consolidated user question.
2. Orchestrator verification; the user decides; a separate implementation task applies the approved edits, then one user-approved root refresh.
   O-2 touches a command that the golden suite covers: if it needs a protected-path grant or an evaluator baseline v21, the user decides that explicitly.

## 3. Not in scope

R-1, the other plan-112 §2 notes, the held-out check, the stale golden quote. O-11 is a ledger note in `docs/tasks/active-tasks.md`, which belongs to the orchestrator; T617 reports on it but the orchestrator tidies it.

## 4. Outcome of the ruling (2026-10-09)

T617 gave every observation a disposition (`task-protocol-observations-ruling-v1.md`). The user chose every recommended option (verbatim labels: groups 1+2 "Amend both (Recommended)"; group 3 "Apply all (Recommended)"; groups 4+5 "Apply all clean-ups (Recommended)", with O-8 left unedited; O-11 "Move to an archive file (Recommended)"). T618 (backend-developer) applies the 17 fences across 11 files; one user-approved root refresh follows. O-11 was done by the orchestrator in the same MR as the scoping: the old ledger notes moved verbatim to `docs/tasks/ledger-notes-archive.md`.
