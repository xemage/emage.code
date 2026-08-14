# Case: security-audit-coverage-consistency

## Command under test
`/security-audit`

## Brief (illustrative — not executed live)
"Perform a security audit on the internal admin CLI's authentication and authorization paths
only." A deliberately scoped (not full-project) audit.

## What this checks
`implementation/knowledge/commands/security-audit.md` §"Verdict Output": `OWASP coverage: <n>/10
categories assessed`. This case checks internal self-consistency of that field — a scoped audit
is legitimate (the command's §"Audit Scope" is user-directed, "on: {{input}}"), but the declared
`n` in the coverage field must match the number of OWASP category rows actually present in the
matrix, whatever that number is. This is a real, checkable property distinct from "did it cover
all 10" (a scoped audit correctly does not).

## Pass condition
The `n` in `**OWASP coverage**: n/10 categories assessed` equals the count of distinct `A0X`/`A10`
rows present in the matrix.

## Provenance
Hand-authored (see `security-audit-owasp-matrix-compliant/brief.md` for the corpus-survey note
that no real `/security-audit` output exists in this repo's history to source from).
