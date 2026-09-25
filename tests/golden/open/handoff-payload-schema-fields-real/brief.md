# Case: handoff-payload-schema-fields-real

## Command under test
`/handoff`

## Brief (illustrative — not executed live)
"Hand this session off — the repo sync is done and T458's infrastructure requirements need to
carry over." A resumable handoff artifact is produced for the next session.

## What this checks
`implementation/knowledge/commands/handoff.md` `## Instructions` steps 3 and 4, verbatim:

> 3. **Draft handoff payload** conforming to `implementation/runtime/handoff/schema-v1.json`:
>    - `fromAgent`: current role (usually `orchestrator`)
>    - `toAgent`: next agent or `orchestrator` for resume
>    - `taskId`: primary active task ID
>    - `intent`: `delegate` | `request-review` | `request-data` | `escalate`
>    - `payload`: objective, files touched, open questions
>    - `constraints`: `writablePaths`, `forbiddenActions`, `maxToolCalls`, `deadlineUtc`
>    - `trace`: `checkpointRef`, `correlationId`
> 4. **Write artifacts**:
>    - JSON: `docs/checkpoints/handoff-<handoffId>.json`
>    - Human summary: `docs/checkpoints/handoff-<handoffId>.md`

and the `## Security` section's first bullet, verbatim:

> - Never include secrets, tokens, or `.env` contents in handoff payloads.

Step 3 says "conforming to `implementation/runtime/handoff/schema-v1.json`", so the schema is part
of the clause, not a separate contract. The schema ships in the fixture and the check is **driven
from it** rather than from a hardcoded field list — required top-level keys, the `intent` enum, the
`additionalProperties: false` exact key sets on `constraints` and `trace`, and the declared
`pattern` regexes for `handoffId`/`taskId`/`fromAgent`/`toAgent`/`schemaVersion`. This matters
because step 3's own bullet list is a *subset* of what the schema requires (it never mentions
`schema`, `schemaVersion` or `timestamp`), so a check built only from the bullets would pass a
payload the declared schema rejects.

Step 4's contribution is the one a single-file check would miss: the `<handoffId>` in **both**
filenames must be the same value as the JSON's own `handoffId` field, and both artifacts must
exist. A handoff that writes only the JSON, or names the pair after something other than the ID it
carries, is not resumable by the next session — which is the whole point of the command.

## Pass condition
`fixture/docs/checkpoints/` contains exactly one `handoff-*.json`; its `handoffId` field equals the
`<handoffId>` component of its own filename; the sibling `handoff-<handoffId>.md` exists and is
non-empty; the JSON satisfies every schema constraint listed above as read out of
`fixture/implementation/runtime/handoff/schema-v1.json`; and no key anywhere inside `payload`
matches `token|password|api[_-]?key|authorization|secret`.

## Provenance
**Fully real.** All three fixture files are byte-identical copies of files already in this
repository:

- `docs/checkpoints/handoff-8ed4088b-3207-4e61-b6f5-6e66e2691167.json`
- `docs/checkpoints/handoff-8ed4088b-3207-4e61-b6f5-6e66e2691167.md`
- `implementation/runtime/handoff/schema-v1.json`

A corpus survey (`ls docs/checkpoints/handoff-*`) found two real handoff pairs,
`725b7925-…` and `8ed4088b-…`; the latter is the more recent and supersedes the former by its own
first line. Both were independently confirmed to pass
`implementation/runtime/handoff/validator.py`'s `validate_handoff_payload()` (`ok=True`,
`errors=[]`), so this case documents a genuinely already-satisfied instance of the contract rather
than one constructed to pass — the same grounding pattern as
`plan-task-creation-precondition-real`. The secret-key regex is copied from that validator's own
`SECRET_KEY_RE` so the security clause is enforced the same way the runtime enforces it.
