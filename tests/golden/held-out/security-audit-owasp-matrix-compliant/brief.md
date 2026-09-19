# Case: security-audit-owasp-matrix-compliant

## Command under test
`/security-audit`

## Brief (illustrative — not executed live)
"Perform a security audit on the user-profile-service." Audit finds two non-critical issues.

## What this checks
`implementation/knowledge/commands/security-audit.md` §"OWASP Coverage Matrix" (all 10 rows
`A01`-`A10` present) and §"Verdict Output" (`## VERDICT` block with `Status`, `CRITICAL
findings`, `HIGH findings`, `MEDIUM findings`, `LOW findings`, `OWASP coverage`, `Blocker IDs`,
`Auditor`, `Timestamp` fields).

## Pass condition
`fixture/audit.md` contains a matrix row for every `A01`-`A10` category, and a `## VERDICT`
section with all nine required fields present.

## Provenance
Hand-authored. No real `/security-audit`-shaped output (full `A01`-`A10` matrix + `## VERDICT`
block) exists anywhere in this repo's history — a corpus survey (`grep -rl "OWASP coverage"
docs/`, `grep -rl "^| A01" docs/`) found zero real matches outside this suite's own format spec.
Real security review work in this repo is instead captured informally in checkpoints/task briefs
(e.g. `docs/checkpoints/checkpoint-009-phase2-pattern-b-gate3-ready.md`) without this structured
shape, which is why every `/security-audit` case in this suite is hand-authored rather than
sourced from history.
