# ADR-009 — adr-008-acceptance-record

> Filename: `ADR-009-adr-008-acceptance-record.md` (zero-padded sequential, kebab-case slug).

- **Status**: Accepted. The user approved it on 2026-10-15 ("Accept ADR-009 as written (Recommended)"). It was proposed on 2026-10-14.
- **Date**: 2026-10-15
- **Decider(s)**: solution-architect drafted it. Acceptance is reserved to the user.
- **Tasks**: T634 (this draft). T581 (ADR-008 and its acceptance). T623 (release audit finding C-8).
- **Requirements**: `docs/decisions/ADR-008-knowledge-document-authority.md` header lines 5-10 at develop `4c5b43e`; `docs/artifacts/release-v8-audit-v1.md` C-8; `AGENTS.md` § Decision Log; `docs/tasks/completed-tasks.md` T581 row.
- **Extends**: ADR-008, its Status block only.
- **Supersedes**: only the draft-era Status bullets of ADR-008, at lines 6-10 of the file as of develop `4c5b43e`: "Drafted for the user's acceptance ...", "Until it is accepted, no ruling may cite it as authority.", and "Revised to incorporate ... The final text is still subject to the user's acceptance." Nothing else.

## Context

ADR-008's Status block says at line 5, "Accepted. The user approved it on 2026-10-02 ("Accept ADR-008 (Recommended)") ...", and at lines 6-10 that it was "Drafted for the user's acceptance", that "Until it is accepted, no ruling may cite it as authority", and that "The final text is still subject to the user's acceptance". The first is the state after acceptance, and the others are the state before it. ADR-008 § Follow-ups said to record the acceptance in the header through a normal MR. Line 5 is that record, and the draft-era bullets were left beside it. The release audit named the result (`release-v8-audit-v1.md` C-8). An accepted ADR is immutable and a change needs a superseding ADR (`AGENTS.md` § Decision Log; ADR-008 line 5).

## Decision

1. **ADR-008 is Accepted.** The user accepted it on 2026-10-02 (ADR-008 line 5; `completed-tasks.md` T581 row: "The user accepted ADR-008.").
2. **The draft-era bullets at ADR-008 lines 6-10 have no force.** They describe the draft before acceptance and stay in the file as history. Where they differ from line 5, line 5 governs.
3. **Other draft-era sentences are read the same way.** These are ADR-008 § Decider(s) "Acceptance is reserved to the user", § Tasks "T581 is this draft" and "Once accepted, it makes the parked items P40 and P43 schedulable", and § Follow-ups "The final text still needs the user's acceptance". They describe the draft process and are history. They do not make ADR-008 provisional.
4. **Every ruling that cited ADR-008 as authority on or after 2026-10-02 stands.** None is reopened or re-derived by this ADR.
5. **Unchanged.** The text of ADR-008 is not edited by this ADR. ADR-008 stays `Accepted`, dated 2026-10-02, and it still extends ADR-007 and supersedes nothing in it. Its Decision, D1-D5, P1-P5, Order of application, user decisions Q1-Q3, Alternatives, Consequences and Validation are unchanged. No file under `implementation/knowledge/` changes.
6. **Reading rule.** For the status of ADR-008, read its line 5 together with this ADR. A reader who finds lines 6-10 first should treat them as superseded by ADR-009.

## Alternatives considered

| Option | Pros | Cons | Why not chosen |
|--------|------|------|----------------|
| A. Append a status note inside ADR-008 | A reader of ADR-008 sees the correction | Edits an accepted ADR; ADR-008 line 5 says a change needs a superseding ADR; no precedent | Not chosen |
| B. Mark ADR-008 `superseded by ADR-009` | Uses the template's status vocabulary | Reads as if P1-P5 were replaced | Not chosen |
| C. Leave it and note it in the v8.0.0 release document | No new record | The next reader of ADR-008 still finds a contradiction, and `:8` can be quoted against a later ruling | Not chosen |

## Consequences

- **Positive**: one authoritative statement that ADR-008 is accepted; no ruling is exposed to the `:8` sentence; ADR-008 stays byte-for-byte as accepted.
- **Negative**: a number is spent on a clerical correction. ADR-008 read alone still shows the contradictory bullets.
- **Risks introduced**: a reader who never opens ADR-009 still sees the contradiction. *Mitigation:* the audit and the v8.0.0 release document point to ADR-009; the user may additionally approve an append-only pointer in ADR-008 if wanted (not part of this ADR).
- **Follow-ups**: none to knowledge files. T634 is the only task.

## Validation

1. `git diff` of the implementing MR shows only the new ADR-009 file (plus ledger/checkpoint bookkeeping); `ADR-008-knowledge-document-authority.md` is unchanged.
2. ADR-009's quoted lines match ADR-008 at the commit named in Supersedes.
3. No ruling or ledger row changes.
