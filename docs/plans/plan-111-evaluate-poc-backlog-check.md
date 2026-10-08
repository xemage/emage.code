# plan-111 — Root refresh 9, and the evaluate-poc backlog check (P44) under a user-approved v19

**Created:** 2026-10-08
**Based on:** the user's decisions of 2026-10-08 ("Root refresh 9: yes please"; "Approving v19 basline");
`docs/artifacts/poc-skill-command-overlaps-v1.md` (P44).
**Scopes:** `T600`.

## 1. Root refresh 9

The ninth `--projections-only` refresh followed the plan-082 §2 procedure.
- **Rehearsal first.** `docs/` and `implementation/` stayed byte-identical, and the changed paths equalled the 26
  declared paths.
- **Result.** It refreshed those 26 paths, which T599 had left stale, so drift is now 0.
- **Record.** It is in MR !525 and needs no ledger row.

## 2. P44: T600

The orchestrator verified two defects in the open case `evaluate-poc-verdict-debt-reconciliation` on `develop`
`edd426e`:
1. **The backlog check is narrower than the contract.**
   - `expect.py` counts only numbered backlog lines.
   - `/evaluate-poc` step 6 declares no format, and the `poc-evaluation` skill's § 6 template is a table.
   - So a conforming table backlog fails the check.
2. **The brief overstates the checklist rule.** It says "when and only when", but step 10 and `check()` both say "if".

T600 widens only the backlog count, so it accepts numbered items or table rows. Strength stays the same: one backlog
heading and at least 5 items. A discrimination run is required. T600 also corrects the brief's wording. No case
result changes, and no non-golden test loads this case.

**The user pre-approved v19 on 2026-10-08.** The orchestrator writes it only after independently verifying T600:
- the AST differs only in `_backlog_size` and the docstring;
- the discrimination run holds;
- the result and the scorecard are unchanged;
- there are exactly two hash failures.
