# Case: code-review-fail-blocker-details

## Command under test
`/code-review`

## Brief (illustrative — not executed live)
"Review the payment webhook handler against `payment-webhook-v1.0.md`." Review finds a missing
signature-verification check — a real blocker.

## What this checks
`implementation/knowledge/commands/code-review.md` §"Review Checklist" item 7 and §"Verdict
Output": "If status is `fail`, include blocker details, owner, and retry attempt guidance."

## Pass condition
`fixture/review.md`'s `## VERDICT` has `Status: FAIL` and a non-empty `Blocker IDs` field, AND
the document contains, outside the VERDICT block itself, explicit blocker detail text mentioning
an owner and retry guidance (checked via presence of `**Owner**:` and a case-insensitive mention
of "retry").

## Provenance
Hand-authored — no real `/code-review`-shaped FAIL verdict with blocker detail exists in this
repo's history to source from (this repo's real gate-failure records use the QA/Tech-Lead
"Blockers" table convention from `AGENTS.md` instead — see `code-review-real-verdict-format-
drift` for that real convention applied to this same contract).
