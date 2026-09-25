# Case: security-audit-critical-not-fail (known_failing / capability_gap)

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
`capability_gap` — **reclassified from `tracked_defect` at T520**, per `ADR-007` branch 4
("no corpus at all"). See `docs/artifacts/command-contract-resolution-v1.md` §3 row D.

This is not a contract-vs-corpus conflict, so neither of the two fixes the old `tracked_defect`
classification implied is available:

- **There is no corpus to fix.** No real `/security-audit` output exists in this repo's history;
  this fixture was hand-authored *in order to* violate the rule. `tests/golden/README.md` defines
  `tracked_defect` as "a known, expected-to-be-fixed bug", and nothing in the repository is
  broken here.
- **The rule must not be amended.** `security-guidelines.md`'s Security Review Workflow
  independently requires `SECURITY:CRITICAL` findings to block merge, and its Immutable Security
  Constraints forbid disabling a security control for convenience. Adding a compensating-control
  exception clause is therefore not an available fix.

What the case actually demonstrates is that the command's VERDICT surface gives an auditor **no
way to record "CRITICAL present, mitigated by a compensating control"** other than by breaking
the rule — a deliberate demonstration that the command surface does not support something, which
is `README.md`'s `capability_gap` definition. The case stays `known_failing` permanently and
correctly: the only ways to make it pass are to edit the fixture's `Status` to `FAIL` (which
deletes the demonstration and duplicates `security-audit-verdict-fields-compliant`) or to relax
`expect.py` (forbidden by `ADR-007` §5).

**Recorded counter-reading.** A reviewer may reasonably object that `capability_gap` still
over-claims: the "capability" is one `security-guidelines.md` deliberately refuses, so it is a
closed door rather than a gap. Under that reading the honest answer is that this suite's
two-flavour vocabulary has no slot for a negative/counter-example fixture — there is no way to
say "`check()` correctly returning `False` *is* the pass condition." Taking that reading instead
would require a third flavour in `tests/golden/README.md` and a corresponding change to
`maturity-promotion-criteria-v1.md` §3.5. `capability_gap` is the truthful classification
available under today's vocabulary; the third flavour is tracked as an `ADR-007` follow-up.
