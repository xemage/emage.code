# plan-108 — Root refresh 7, and the path conventions (P32)

**Created:** 2026-10-08
**Based on:** the user's decisions of 2026-10-08 ("Root refresh: yes, please"; "Next item: continue as
recommended"); `docs/plans/plan-107-remaining-verdict-renderings.md` §4 (G5 and the G7 plan path → P32);
`docs/plans/plan-092-poc-contract-amendments.md` §4 (P32).
**Scopes:** `T595`, `T596`.

## 1. Root refresh 7

The seventh `--projections-only` refresh followed the plan-082 §2 procedure. It was rehearsed first: `docs/` and
`implementation/` stayed byte-identical, and the changed paths equalled the 44 declared paths. It refreshed those 44
paths, left stale by T594, and drift is now 0. It is recorded in MR !512 and needs no ledger row.

## 2. Sequence for P32

1. **T595** (solution-architect, P2, decision only): D5 records for (a) the production plan path and (b) the
   release-notes duplication, plus user questions for every P5 escalation, with the candidate edits held verbatim.
2. Orchestrator verification.
3. The user decides each escalation, including any command change.
4. Implementation as a separate task. If it changes a golden quote or fixture, it needs a grant and a
   user-authorized v18.

## 3. Not in scope

The following stay parked:
- P33;
- P44;
- L4/X5;
- the plan-106 §3 note;
- P41 observations O1–O5.

## 4. Outcome (2026-10-08)

- **The T595 ruling** is `path-conventions-v1.md` → `-v2.md` → `-v3.md`; v3 is the implementation input.
  - (a) Under `/new-feature`, Step C decided the command's path. Everything else turned on the undefined `<ID>`, so it
    escalated under P5 as Q-P32a.
  - (b) Step A holds. The convention question escalated as Q-P32b.
- **The user's decisions** (2026-10-08, verbatim option labels):
  - Q-P32a: **"plan-<NNN>-<slug>.md (Recommended)"**, option 1, including the PoC track. The slug may contain dots,
    matching the release plans.
  - Q-P32b: **"One, at docs/releases/ (Recommended)"**, option 1.
- **Orchestrator verification:**
  - 64 quotes were checked mechanically, and the 4 multi-segment quotes were checked by hand.
  - All 108 real plans conform to the decided form.
  - No `docs/artifacts/release-notes-v*.md` exists, and the CI scripts use `docs/releases/`.
  - No non-golden test asserts any changed string.
  - The orchestrator found a sixth plan-path variant (`validation-gates:92`), which was added as P-10 in v3.
  - v3's 13 applications land once each across 10 files. Held-out isolation passes.
- **Security review:** not required, because no security criterion is touched.
- **Next: T596** (backend-developer, P2) applies v3's edits P-1 to P-10 and R-1 to R-3. No golden result changes.
- **FU-P32-G.** The golden realignment needs a protected-path grant and a user-authorized **v18**, which is not yet
  authorized:
  - `new-feature-plan-doc-compliant`: glob, fixture name and brief;
  - `new-project-plan-doc-and-lifecycle-states`: brief and docstring;
  - optional re-copies.

  It goes to the user after T596.
- **Parked:** observations O1–O6 (v3 §8). O1 is the version-suffix question, which includes the template's
  `plan-<slug>-v2.md` revision line.

## 5. Completion (2026-10-08)

- **T596 is merged** (MR !515, `develop` `2cf54ec`). The 13 edits are applied verbatim and were verified
  independently.
- **Erratum to `path-conventions-v3.md`.** §7 row 33 expects `## RELEASE VERDICT` in release-workflow at 1 line /
  1 occurrence after R-2. The correct count is 1 line / 2 occurrences: R-2's text names it twice on one line.
- **Root drift** is 52 declared paths. The next root refresh needs the user's approval.
- **Open: FU-P32-G**, the golden realignment. It covers:
  - the `new-feature-plan-doc-compliant` glob, fixture name and brief;
  - the `new-project-plan-doc-and-lifecycle-states` brief quote and docstring;
  - optional fixture re-copies.

  It needs a protected-path grant and a v18 that the user has not yet authorized.
- The queue is empty, and plan-108 is complete.
