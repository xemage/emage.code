---
name: rapid-prototyping
description: "Create pragmatic scaffolding and integration patterns for fast proof-of-concept delivery."
maturity: experimental
---

# Rapid Prototyping

## Rails
**Inputs**: A PoC repository to bootstrap or a minimal architecture slice to build (§ When to use), for a hypothesis documented before any code is written (`poc-guidelines.md` § Hypothesis-First Validation, Rule 1).

**Out of scope**: Does not scan for `POC-DEBT` tags or write the debt scorecard (the technical-debt-tracking skill scans for them, § Mandatory Debt Tagging), and does not run the PoC evaluation (the poc-evaluation skill). Does not write checkpoint files: its `[CHECKPOINT]` line is reported to the orchestrator, which writes the checkpoints (`AGENTS.md` § Checkpoint Protocol).

**Failure mode**: When the PoC time-box expires, report the `[CHECKPOINT]` line with whatever evidence exists. A hypothesis not validated by then is `invalidated`, and a partial result is `invalidated` with `next=` naming a follow-up PoC with refined criteria (§ Hypothesis Validation Checkpoint Format; `poc-guidelines.md` Rules 3–4). A shortcut found without a `POC-DEBT` tag is flagged as a review finding (§ Mandatory Debt Tagging, Enforcement).

## When to use
- Bootstrapping PoC repositories
- Creating minimal architecture slices

## Outputs
- Minimal project structure
- Fast run instructions
- Scope boundaries for what not to build

---

## Protocol-Aware Enhancements

### Mandatory Debt Tagging

All PoC code MUST tag known shortcuts, workarounds, and deferred quality concerns using the standard debt tag format:

```html
<!-- POC-DEBT: description of the shortcut or deferred concern -->
```

**Placement rules:**
- Place the tag directly above or inline with the code that embodies the shortcut.
- For architectural shortcuts, place the tag in the relevant architecture or design document.
- For configuration shortcuts (e.g., hardcoded values, disabled security), place the tag in the config file.

**Examples:**
```python
# <!-- POC-DEBT: No input validation — add comprehensive validation before production -->
def create_user(data):
    return db.users.insert(data)

# <!-- POC-DEBT: Using in-memory store — replace with persistent database before production -->
cache = {}
```

```yaml
# <!-- POC-DEBT: CORS allow-all — restrict origins before production -->
cors:
  origin: "*"
```

**Enforcement:**
- Every file in a PoC that contains a shortcut MUST have at least one `POC-DEBT` tag.
- The technical-debt-tracking skill scans for these tags during PoC evaluation.
- An untagged shortcut discovered during review is flagged as a review finding. The missing tag is a 🟡 Should Fix finding. The shortcut itself is graded like any other finding on the code-review skill's § Severity Guide, so a shortcut that is a bug, security issue or data loss risk is a 🔴 Must Fix finding. These labels grade review findings, not debt: the technical-debt-tracking skill assigns the debt severity when it merges the finding into the debt ledger (§ POC-DEBT Tag Scanning Procedure, Step 3).

### PoC Artifact Versioning

PoC artifacts follow the standard immutable versioning convention:

```
docs/artifacts/poc-{name}-v1.md
docs/artifacts/poc-{name}-v2.md
```

**PoC artifact structure:**
```markdown
# PoC: {Name} v{N}

## Version: {N}
## Date: {YYYY-MM-DD}
## Status: in-progress | complete | evaluated

## Hypothesis
[What this PoC is testing]

## Success Criteria
- [ ] Criterion 1
- [ ] Criterion 2

## Technology Stack
[Technologies selected, referencing tech-eval-v{N} if applicable]

## Scope Boundaries
### In scope:
- [what the PoC will demonstrate]

### Explicitly out of scope:
- [what the PoC will NOT build]

## Known Debt
[Summary of POC-DEBT tags — auto-populated during evaluation]

## Run Instructions
[How to run the PoC]
```

### Hypothesis Validation Checkpoint Format

At the conclusion of prototyping (or at significant milestones), report a hypothesis validation checkpoint line to the orchestrator:

```
[CHECKPOINT] id=poc-{name}-validation | hypothesis="{hypothesis text}" | evidence=[{evidence items}] | debt_tags={count} | verdict=validated|invalidated|in_progress | artifact_refs=[poc-{name}-v{N}] | next=[{next steps}]
```

This line is a status report, not a checkpoint file. Checkpoints (`docs/checkpoints/checkpoint-<SEQ>-<phase>.md`) are written by the orchestrator at every phase boundary (`AGENTS.md` § Checkpoint Protocol). Include the line in your report to the orchestrator (`AGENTS.md` § Task Protocol: "Agents report completion and blockers"). The orchestrator carries what it needs from the line into the checkpoint for that phase.

**Verdict values:** `in_progress` is allowed only at a milestone checkpoint, before any of the checkpoint triggers below has fired. At a trigger, the verdict is binary: `validated` or `invalidated` (`poc-guidelines.md` § Hypothesis-First Validation, Rule 4). A hypothesis not validated when the time-box expires is `invalidated` (Rule 3). A partial result is `invalidated`, and `next=` names a follow-up PoC with refined criteria.

**Evidence items** should be specific and measurable:
- "API response time < 200ms for 95th percentile" ✅
- "Integration with {service} successful via SDK v{X}" ✅
- "It seems to work" ❌ (too vague)

**Checkpoint triggers:**
- All success criteria have been tested (regardless of outcome).
- A showstopper is discovered that invalidates the hypothesis.
- The PoC time-box expires (document whatever evidence exists).
