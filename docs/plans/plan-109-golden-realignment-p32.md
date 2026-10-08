# plan-109 — Root refresh 8, and the golden realignment after P32 (FU-P32-G) under a user-approved v18

**Created:** 2026-10-08
**Based on:** the user's decisions of 2026-10-08 ("Root refresh 8: yes, please"; "Approving v18 baseline");
`docs/plans/plan-108-path-conventions.md` §5; `docs/artifacts/path-conventions-v3.md` §6.
**Scopes:** `T597`.

## 1. Root refresh 8

The eighth `--projections-only` refresh followed the plan-082 §2 procedure. It was rehearsed first:
- `docs/` and `implementation/` stayed byte-identical;
- the changed paths equalled the 52 declared paths.

It refreshed those 52 paths, left stale by T596, and drift is now 0. It is recorded in MR !517 and needs no ledger
row.

## 2. FU-P32-G: T597

T597 realigns five open golden cases with the merged P32 convention, under a file-scoped `protected-paths-v1.md` §5
grant:
- **Required:** `new-feature-plan-doc-compliant` (glob, fixture name and brief) and
  `new-project-plan-doc-and-lifecycle-states` (quotes, comment and fixture name).
- **Optional, folded in so a single v18 covers them:** the `new-poc` fixture name, the
  `plan-required-sections-compliant` brief (O4), and the `validate-workflow` fixture re-copy after P-10.

The only `check()` change is the `new-feature` glob, which keeps the same strength. A discrimination run is required.
No case result changes.

**The user pre-approved v18 on 2026-10-08.** The orchestrator writes it only after independently verifying T597:
- quotes are verbatim;
- renames are content-identical;
- the discrimination run passes;
- results and scorecard are unchanged;
- exactly two hash failures.
