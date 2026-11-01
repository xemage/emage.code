# plan-127 — LOW batch D: knowledge text and rulings

**Created:** 2026-11-01
**Based on:**
- `docs/artifacts/tracked-debt-register-v4.md` § 5 (batch D, 18 ids)
- `docs/artifacts/tracked-debt-register-v1.md` to `-v3.md`, which describe the ids
- `docs/checkpoints/checkpoint-040-release-v9.0.0.md`
- the user's answer of 2026-11-01, verbatim: "D go"

**Scopes:** `T718`, `T719`, `T720`, `T721`.

## Goal

1. Close the knowledge-text LOW items.
2. Rule on the release-gate and severity-scale wording.
3. Settle TD-T713-01 with the user before the next release. TD-T713-01 is the conflict between Release Gate Policy item 2 ("a `SECURITY:MEDIUM` finding is fixed before the release ships") and the two releases that shipped one by the user's recorded decision (v8.0.0: SEC-T660-01; v9.0.0: SEC-T702-09).

## Task Decomposition

1. **T718** (solution-architect): one rulings artifact, `docs/artifacts/rulings-batch-d-v1.md`, plus a proposed ADR for TD-T713-01.
   - **TD-T713-01.** Draft `docs/decisions/ADR-011-user-accepted-medium-at-release.md` with **Status: Proposed**. It weighs at least these options, with a recommendation:
     - (a) item 2 allows a `SECURITY:MEDIUM` to ship only under the user's explicit, recorded and time-bound acceptance, with a remediation plan; `security-guidelines.md` already asks for "a documented remediation plan before merge";
     - (b) item 2 stays as written, and v8.0.0 and v9.0.0 are recorded as user overrides of the policy;
     - (c) a separate override clause that names who may override and what must be recorded.
     The ADR names every knowledge file its acceptance would change: `release-manager.md` § Release Gate Policy, `validation-gates` § Verdict Rules, `prepare-release.md` step 9, and any other place that repeats the rule. Only the user accepts it (ADR-008).
   - **TD-T687-02 to -04.** Rule on the three severity-scale gaps in `docs/wiki/severity-and-grade-scales.md` § Known gaps item 5:
     - `qa-engineer` `P0`-`P3` against `AGENTS.md` `P0`-`P2`;
     - the unnamed scale in `release-workflow` § Hotfix Workflow ("critical or high");
     - the third casing of S5 and V1 in `security-engineer`.
     Each ruling gives the exact replacement text and the defining document under ADR-008.
   - **SEC-T693-02, -03, -05, -06, -09.** Rule on the release-gate wording, giving the exact replacement text:
     - -02: the effect on the verdict of a missing or FAIL independent-check row;
     - -03: one name for the checker in `orchestrator.md:218` and `release-manager.md:46,175`;
     - -05: the scope of "the document";
     - -06: Phase 5, where deployment comes before the Release Gate;
     - -09: list the fields that may change after the independent check, instead of naming the whole `## RELEASE VERDICT` section.
   - **SEC-T693-04.** Rule on the knowledge-text part, and draft the command part (`prepare-release.md`: the verdict block records a commit) as an option for the user. A command change needs the user under ADR-007.
   - *Acceptance:*
     - every id has a ruling, with exact text and file:line;
     - every ruling cites its authority (ADR-007, ADR-008, `AGENTS.md`), or says that the user must decide;
     - ADR-011 is Proposed and cannot be used as authority before the user accepts it.
2. **T719** (technical-writer): the knowledge edits that need no ruling. Runs in parallel with T718.
   - RO621-N-3: `implementation/knowledge/agents/scrum-master.md:32,85` omits `priority::critical`, which `gitlab-management` defines.
   - TD-T671-P16: `implementation/knowledge/commands/batch.md:28` declares no character set for `<slug>`. Use the slug rule the repo already uses elsewhere, and cite it.
   - TD-T671-T538: `implementation/knowledge/skills/dependency-graphing/SKILL.md:36-38` colours `in_progress` blue and `in_review` yellow, the reverse of `commands/team-status.md:34-38`. Align the skill to the commands.
   - TD-T671-T554: `implementation/knowledge/commands/discover-skills.md:34`, step 6, merges `packs/installed/` registry entries that no pack format contains. Under ADR-007 this is a command text, so ask whether the edit needs the user, or propose to leave it and say why.
   - SEV-T690-03: the VS Code part of `docs/wiki/mcp-servers.md`. It lacks (unverified) labels for the trust-dialog wording, `type` for stdio and the `code .` recipe, and it does not address multi-root workspaces.
   - *Acceptance:* each item edited, or reported with a reason. The orchestrator runs `sync.mjs`, `generate-registry.py` and all gates.
3. **T720** (technical-writer): apply the T718 rulings, and ADR-011 once the user has decided. Also update § Known gaps of `docs/wiki/severity-and-grade-scales.md`. Depends on T718 and on the user's decisions on TD-T713-01 and the SEC-T693-04 command part. *Acceptance:* the text matches each ruling exactly, and every place ADR-011 names is changed or left as ruled.
4. **T721** (devops-engineer), SEC-T693-08: `tests/functional/test_release_self_review_text.py` pins the release-gate text. It must also pin `release-manager.md:229` and `orchestrator.md:129` and the final T720 wording, and confirm the projection list. Depends on T720. *Acceptance:* the new pins fail on a broken copy of the text; all gates and the suite pass.

## Orchestrator items

- **TD-T671-legacy.** The orchestrator re-reads the older parked remarks P4, P7, P10 to P12 and CT rows T539, T544, T547 and T565, and records a status for each in this plan's outcome. P14 and P15 sit in protected goldens and stay parked: they need a grant, and none is asked for here.
- **SEC-T693-07** stays accepted by ruling (v3 § 7.2), with no edit.

## User decisions

1. **TD-T713-01**: accept ADR-011, choosing one of its options, or reject it.
2. **SEC-T693-04, command part**: change `prepare-release.md` as T718 proposes, or leave it.
3. **Root refresh**: T719 and T720 change knowledge projections. The root install is refreshed only with the user's explicit approval at that point.

## Constraints

- Subagents never merge, tag or release. The orchestrator merges on `mergeable` with a green pipeline and a pinned sha.
- Never open `tests/golden/held-out/`, and never write a held-out case id.
- The technical writer and the solution architect have no shell. The orchestrator commits their work and runs `sync.mjs`, `generate-registry.py` and the gates.
- Every knowledge edit is made under `implementation/knowledge/`, never in a projection.

## Outcome (2026-11-01)

- **Tasks.** T718 to T721 are done.
- **User decisions** (2026-11-01, AskUserQuestion, verbatim):
  - TD-T713-01: "(a) Time-bound acceptance (Recommended)", with the end date "Until the next release". ADR-011 is Accepted.
  - SEC-T693-04, command part: "O1: both fields (Recommended)". This is ruling R10.
- **Batch-D ids.**
  - Closed: RO621-N-3, TD-T671-P16, -T538, -T554, SEV-T690-03, TD-T687-02 to -04, SEC-T693-02 to -06, -08, -09, TD-T713-01.
  - Unchanged: SEC-T693-07, accepted by ruling, with no edit.
- **TD-T671-legacy**, re-read by the orchestrator:
  - Obsolete:
    - P4: the term `skills/local` occurs nowhere.
    - P7: one `_replace_one` remains, in `scripts/render_installed_agents.py`.
  - Fixed:
    - P9 by T566.
    - P11 by T563 and T595.
    - P12 by T563 (P29).
    - The T544 remark is TD-T671-P16, closed by T719.
  - Still open, tracked-LOW: P10. `/new-project` uses `APPROVED`/`APPROVED_WITH_CHANGES`/`REJECTED`; `plan-approve-execute` uses Approve/Revise/Reject.
  - Still parked: P14, P15 and the remarks of CT rows T539 and T565. They sit in protected goldens and need a grant.
- **Security review.** `docs/artifacts/security-review-t718-t720-batch-d-v1.md`.
  - The first review was CONDITIONAL_PASS. Its one MEDIUM, SEC-T720-01, was fixed in `06a48087`, and the re-check gave PASS.
  - Tracked LOW: SEC-T720-02 to -08.
- **New tracked LOW, TD-T720-01.** `release-workflow/SKILL.md` lines 116 ("No critical or high bugs") and 170 ("Confirm the issue is critical") name no severity scale. R8 closed the same gap for lines 171 and 232.
- **Root drift.** 58 projection paths are declared in `tests/_baselines/root-install-drift.json`. A root refresh needs the user's approval.
- **Token use against budget:**
  - T718 about 281k (80k).
  - T719 about 130k (50k).
  - T720 about 90k (60k).
  - T721 about 108k (60k).
  - The security review about 153k (60k).
