# Case: validate-tasks-fail-lines-verbatim

## Command under test
`/validate-tasks`

## Brief (illustrative — not executed live)
"Validate the task ledger before writing the checkpoint." The command is run twice: once against a
ledger that is clean, and once against a ledger carrying violations, and each run is reported back
to the user.

## What this checks
`implementation/knowledge/commands/validate-tasks.md`, the two exit-code bullets of its body
(the command has no numbered phases; these two bullets are its entire declared reporting
contract), verbatim:

> - Exit 0 → report "TASK LEDGER: PASS".
> - Exit 1 → report every `FAIL C<n>` line verbatim, then propose one fix per
>   violation. Do NOT auto-fix C5, C6, or C8 — ask the user which ledger is correct.

Both branches are exercised, because the interesting failure mode is branch-specific: an agent
that summarizes ("3 violations found, all ledger-overlap issues") instead of reproducing each
`FAIL C<n>` line **verbatim** satisfies a reader but silently drops the codes and line numbers the
next agent needs. The word "verbatim" is the load-bearing term and it is what this case asserts.

## Pass condition
- `fixture/pass-run/` (`exit-code.txt` = `0`): `report.md` contains the literal string
  `TASK LEDGER: PASS`, and contains no `FAIL C<n>` line.
- `fixture/fail-run/` (`exit-code.txt` = `1`): every line of `validator-output.txt` matching
  `^FAIL C\d+: ` (there are 5) appears **verbatim** in `report.md`; at least one such line exists
  (a vacuously empty violation set cannot pass); `report.md` does not contain `TASK LEDGER: PASS`;
  and — because C5, C6 and C8 violations are all present — `report.md` contains the contract's own
  phrase `which ledger is correct` (matched case-insensitively), which is the clause's
  declared substitute for auto-fixing.

The `which ledger is correct` string is quoted from the contract sentence itself rather than
invented as a report format: the command does not declare a report template, so this case asserts
only the literal words the contract puts in the agent's mouth, not a layout. It is matched
case-insensitively for the same reason — the phrase reads mid-sentence in the contract but
naturally starts a sentence in a report, and letter case is not something the contract declares.
The `FAIL C<n>` lines, by contrast, are matched **byte-exactly**, because `verbatim` is precisely
what that clause requires.

## Provenance
**Validator output: real, both runs.** Neither `validator-output.txt` was hand-written.

- `fixture/pass-run/validator-output.txt` is the verbatim stdout of
  `python3 docs/tasks/validate-tasks.py` run from this repository's root against this repository's
  own real ledger (exit 0, `TASK LEDGER: PASS (3 active, 321 completed)`).
- `fixture/fail-run/validator-output.txt` is the verbatim stdout of the same real validator run
  against the seeded ledger shipped alongside it at `fixture/fail-run/ledger/docs/tasks/`
  (reproduce with `cd fixture/fail-run/ledger && python3 <repo>/docs/tasks/validate-tasks.py`;
  exit 1, 5 violations).

**The seeded ledger is hand-authored, and it has to be.** A corpus survey
(`python3 docs/tasks/validate-tasks.py`) returns exit 0 / `TASK LEDGER: PASS` against this repo's
real ledger, and `tests/functional` enforces that it keeps doing so — so no real exit-1 run exists
in this repository to source the failing branch from, and one had to be constructed. The seeded
ledger uses synthetic IDs `T901`–`T904` that exist in no real ledger. It was deliberately shaped so
that all three of the no-auto-fix codes (C5, C6, C8) fire, which is what makes the third clause of
the contract sentence checkable at all.

**The two `report.md` files are hand-authored**, as the agent-side output under test. They are the
only part of this case constructed to satisfy the check; the truth they are checked against is the
real validator's own bytes.
