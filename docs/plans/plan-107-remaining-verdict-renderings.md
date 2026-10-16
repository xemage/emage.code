# plan-107 — Remaining verdict renderings and editorial items (P41, G3–G9)

**Created:** 2026-10-08
**Based on:** the user's instruction of 2026-10-08, "Continue with the next best step" (the recommended step was
P41); `docs/artifacts/gate-verdict-consistency-v1.md` §13.3; `docs/plans/plan-106-golden-residual-staleness.md` §3.
**Scopes:** `T593`, `T594`.

## 1. Why now

P41 is the last parked item from the gate-verdict review (T572). The rulings since then (P39, P40/P43, FU-6/FU-7,
SEC-T586-07, O1) have settled the verdict criteria and the security grading. That leaves the renderings, the release
executor (G4), the release-notes path (G5), the second vocabularies (G6) and the `project-planning` defects (G7).

## 2. Sequence

1. **T593 (solution-architect, P2, decision only):** one artifact with a D5 record per item G3–G9.
2. **Orchestrator verification.** If any amendment touches security criteria, a **Security Engineer review** follows.
3. **The user decides** every P5 escalation, including any command change (G4 is likely).
4. **Implementation** is a separate task. If it changes a golden quote or fixture, it also needs a protected-path
   grant and a user-authorized v18.

## 3. Not in scope

- All earlier rulings are inputs.
- The plan-path parts of G5 and G7 may be deferred to P32.
- P33, P44 and L4/X5 stay parked.

## 4. Outcome (2026-10-08)

- **T593 ruling** (`remaining-verdict-renderings-v1.md`). The orchestrator verified it: 92/92 quotes are verbatim,
  all nine Before anchors are unique, and the held-out isolation test passes. The artifact names no golden case that
  lacks an open directory.
  - **G3** (the six renderings) is jointly satisfiable. It gets accompanying notes E-Q1 (`qa-engineer`), E-S1
    (`security-engineer`) and E-R1 (`release-manager`). `/code-review`, `/security-audit` and `release-workflow` are
    unchanged.
  - **G5** (release-notes path): the two paths do not conflict. Choosing a convention joins **P32**.
  - **G6**: E-G6a (`code-review` § Feedback Format) and E-G6b (`tech-lead`). The second vocabulary takes the gate
    values. An open question becomes a blocker, not a verdict.
  - **G7**: E-G7a (task creation by the orchestrator, the 7-column row, priorities `P0`–`P2`) and E-G7b (lifecycle
    states from `AGENTS.md`). The plan path joins **P32**.
  - **G8 and G9** remain noted only.
- **User decision** (2026-10-08, verbatim option label): Q-G4 **"Orchestrator runs, RM decides (Recommended)"**, i.e.
  option 1. This means C-G4a and C-G4b in the experimental `/prepare-release` command (`Release manager:
  release-manager`; `@release-manager` issues the verdict), plus the same field value in `docs/releases/_template.md`.
  E-R1 is released.
- **Security review: not required.** No edit changes a security criterion. E-S1 only states how the
  `security-engineer` verdict renderings relate to the canonical block.
- **Golden coupling: none.** No quote, fixture read or result changes. One fixture field in
  `prepare-release-conditional-pass-conditions-gap/fixture/release-notes.md` (`Release manager`) becomes stale, but no
  check reads it. Refreshing it would need a grant and a v18, so it is not done (O5).
- **Parked observations** (artifact §8.4):
  - O1: on the `orchestrator.md:259` path, the release manager prepares and gates its own release.
  - O2: `scrum-master` has the same conflict with the Task Protocol as G7.
  - O3: `prepare-release-real-verdict-missing` reads the release verdict from a checkpoint. A golden change would need
    a grant.
  - O4: E7's pointer at `orchestrator.md:249` leads to `:205`'s looser wording.
  - O5: the stale fixture field noted above.
- **Next: T594** (backend-developer, P2) applies the nine edits.

## 5. Completion (2026-10-08)

- **T594 is merged** (MR !510, `develop` `6c0c8f0`). The nine edits are applied verbatim and verified independently.
  P41 is closed, except for the parts deferred to P32 and the parked observations O1–O5.
- **Root drift** is 44 declared paths. The next root refresh needs the user's approval.
- The queue is empty, and plan-107 is complete.
