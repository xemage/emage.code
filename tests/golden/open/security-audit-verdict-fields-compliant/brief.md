# Case: security-audit-verdict-fields-compliant

## Command under test
`/security-audit`

## Brief (illustrative — not executed live)
"Perform a full security audit on the payments-gateway-service." Full-project audit, no findings.

## What this checks
`implementation/knowledge/commands/security-audit.md` §"Verdict Output", with a focus distinct
from `security-audit-owasp-matrix-compliant` (which only checks field *presence*) and
`security-audit-coverage-consistency` (which checks matrix-row-count vs. declared coverage
consistency): this case checks **value-level format strictness** of the individual VERDICT
fields — `Status` restricted to the declared enum, `Timestamp` is a well-formed ISO-8601
string, and `Blocker IDs` is `none` (not merely present-but-empty) when `Status` is `PASS`, on
a full (10/10) audit specifically.

## Pass condition
`fixture/audit.md` has all 10 OWASP matrix rows, a `## VERDICT` block with all 9 required
fields, `Status` in `{PASS, CONDITIONAL_PASS, FAIL}`, `OWASP coverage` reads exactly `10/10`,
`Timestamp` matches `YYYY-MM-DDTHH:MM:SSZ`, and `Blocker IDs` reads `none` given `Status: PASS`.

## Provenance
Hand-authored. See `security-audit-owasp-matrix-compliant/brief.md` for the corpus-survey note
(no real `/security-audit`-shaped output exists in this repo's history).
