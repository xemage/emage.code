---
description: "Validate task ledger integrity. Run before every checkpoint, before every release, and after every install --update."
agent: "orchestrator"
---

Run `python3 docs/tasks/validate-tasks.py` from the project root.

- Exit 0 → report "TASK LEDGER: PASS".
- Exit 1 → report every `FAIL C<n>` line verbatim, then propose one fix per
  violation. Do NOT auto-fix C5, C6, or C8 — ask the user which ledger is correct.

Run this command:
1. Before writing any checkpoint
2. Before `/prepare-release`
3. Immediately after `install.sh --update`

## Rails

**Inputs**: `docs/tasks/active-tasks.md` and `docs/tasks/completed-tasks.md`, validated via `docs/tasks/validate-tasks.py`.
**Out of scope**: Auto-fixing `C5`, `C6`, or `C8` violations — those require asking the user which ledger is correct.
**Failure mode**: On exit code 1, reports every `FAIL C<n>` line verbatim and proposes one fix per violation, rather than summarizing or suppressing any failure.
