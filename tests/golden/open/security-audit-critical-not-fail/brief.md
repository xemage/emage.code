# Case: security-audit-critical-not-fail (known_failing / tracked_defect)

## Command under test
`/security-audit`

## Brief (illustrative — not executed live)
"Perform a security audit on the legacy export endpoint." A CRITICAL finding is found (no auth
check on data export), but the auditor concludes `CONDITIONAL_PASS` on the reasoning that a
compensating network-level control mitigates it today.

## What this checks
`implementation/knowledge/commands/security-audit.md`'s closing sentence, verbatim: "If any
CRITICAL findings exist, the verdict MUST be FAIL." This is an unconditional rule with no stated
exception for compensating controls.

## Pass condition (as specified — deliberately not met by the fixture)
If `**CRITICAL findings**` is greater than 0, `**Status**` must be `FAIL`.

## Why this is known_failing today
`fixture/audit.md` has `CRITICAL findings: 1` and `Status: CONDITIONAL_PASS` — a direct,
unambiguous violation of the command's own stated rule. This is deliberately constructed to
demonstrate the violation (no real historical `/security-audit` output exists to source it from
per the corpus survey noted in `security-audit-owasp-matrix-compliant/brief.md`), but the
scenario itself is realistic and plausible: an auditor reasoning about compensating controls is
exactly the kind of judgment call that could produce this exact contract violation in practice.

## Category
`tracked_defect` — this is a genuine, fixable violation of an unambiguous rule (either the
auditor's verdict is wrong given the rule as written, or the rule needs an explicit
compensating-control exception clause — either way, a concrete, trackable fix is implied).
