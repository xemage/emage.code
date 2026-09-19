# Example scaffold case — proves the golden-suite contract

This is **not** one of the 20 real golden cases T411 will author, and it is **not** counted
toward the suite's pass/fail baseline. It exists solely to mechanically prove that the
`expect.py` contract defined in `docs/artifacts/golden-suite-format-v1.md` actually
discriminates a passing fixture from a failing one, rather than trivially always returning
`True`.

## Brief (illustrative — not executed live)

A user asks emage.code to mark a tracked widget's status as done in
`fixture/workspace/STATUS.md`.

## Pass condition

`fixture/workspace/STATUS.md` contains a line that reads exactly `Status: DONE`.
