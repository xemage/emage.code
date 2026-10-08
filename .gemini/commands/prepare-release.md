---
description: "Prepare a new release with version bump, changelog generation, and release checklist."
agent: "orchestrator"
argument-hint: "Specify version type: major, minor, or patch..."
---

Please prepare a new release:

Release type: {{input}}

## Release Steps

1. Determine the next version number (semantic versioning)
2. **Generate changelog from completed tasks**:
   - Read `docs/tasks/completed-tasks.md` for all tasks completed since last release
   - Group by: Features, Fixes, Breaking Changes, Internal
   - Include task IDs and artifact version references
3. Review all included changes (features, fixes, breaking changes)
4. Create the release checklist
5. Prepare release notes

## Version Management

6. **Manage version artifacts**:
   - Update version in all relevant config files
   - Tag all current artifacts with release version
   - Create a release checkpoint: `docs/checkpoints/checkpoint-release-v<version>.md`, based on
     `docs/checkpoints/_template.md` (including its `## Maturity distribution` section — regenerate
     `implementation/registry/summary.md` via `implementation/scripts/generate-registry.py --root
     implementation` first if stale, then populate the table's category × maturity-level counts
     from the regenerated registry, not from a prior release's numbers)
   - Archive completed tasks from `active-tasks.md` to `completed-tasks.md`

## Release Gate Verdict

7. **Produce a structured release gate VERDICT** in the release notes document from step 5
   (`docs/releases/v<version>.md`) as a top-level `## RELEASE VERDICT` section. That document is
   the block's home — not the release checkpoint from step 6. `docs/releases/_template.md`
   carries the slot, and `scripts/verify-release-docs.py --tag v<version>` checks the section is
   present when the tag is cut. The verdict is issued by `@release-manager`, the Release gate's
   executor (skill `validation-gates` § Gate Types; `orchestrator` agent § Validation Gates):

```
## RELEASE VERDICT

- **Version**: v<major>.<minor>.<patch>
- **Status**: PASS | CONDITIONAL_PASS | FAIL
- **Features included**: <count>
- **Fixes included**: <count>
- **Breaking changes**: <count>
- **Open blockers**: <count>
- **Quality gates passed**: [list gates: code-review, security-audit, test-coverage, ...]
- **Quality gates failed**: [list any failed gates]
- **Blocker IDs**: [if FAIL — list blocking issues with owners]
- **Release manager**: release-manager
- **Timestamp**: <ISO-8601>
```

8. If blocked, include blocker IDs, owners, and escalation path
9. If CONDITIONAL_PASS, list the conditions. The release may ship with each condition tracked as a task for the next release cycle, after the explicit risk acceptance `release-manager` § Release Gate Policy requires. A security finding is never such a condition (skill `validation-gates` § Verdict Rules): a `SECURITY:CRITICAL` or `SECURITY:HIGH` finding blocks the release, and so does a breach of an Immutable Security Constraint or a required security control omitted, removed, disabled or weakened, whatever its grade; a `SECURITY:MEDIUM` finding is fixed before the release ships; a `SECURITY:LOW` finding is not a condition and is tracked as technical debt.

Ensure all quality gates are met before proceeding.

## Rails

**Inputs**: The release type (`{{input}}`: major/minor/patch) and `docs/tasks/completed-tasks.md` since the last release.
**Out of scope**: Tagging or announcing a release while any quality gate (code-review, security-audit, test-coverage) has failed.
**Failure mode**: If a quality gate has failed, the VERDICT is `FAIL`. If a blocker is open, the VERDICT is `FAIL`, or `CONDITIONAL_PASS` with listed conditions only when no security finding is among them (skill `validation-gates` § Verdict Rules), rather than a silent `PASS`.
