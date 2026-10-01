---
name: "technical-debt-tracking"
description: "Document PoC shortcuts and production remediation plans using a consistent debt ledger."
---

# Technical Debt Tracking

## Categories
- Security
- Architecture
- Testing
- Data quality
- Operations

## Required fields
- Debt item
- Severity
- Impact
- Estimated remediation effort
- Risk if deferred
- Recommended owner
- Suggested target sprint

## Scorecard Requirements
- The Technical Debt Scorecard is `POC-DEBT-SCORECARD.md` in the PoC root, in the structure `poc-guidelines.md` § Debt Scorecard defines. This skill adds sections to it; it does not define a second scorecard.
- Mark each item as: `must_fix_pre_prod`, `can_defer_post_ga`, or `monitor_only`. A `critical` item is always `must_fix_pre_prod`.
- Include top remediation sequence for the first production sprint.

---

## Protocol-Aware Enhancements

### POC-DEBT Tag Scanning Procedure

This skill is responsible for scanning codebases for `POC-DEBT` tags placed by the rapid-prototyping skill. The scanning procedure:

**Step 1: Discover all debt tags**
```bash
# Scan all project files for POC-DEBT tags
grep -rn "POC-DEBT:" --include="*.py" --include="*.ts" --include="*.js" --include="*.yaml" --include="*.yml" --include="*.md" --include="*.json" --include="*.html" --include="*.css" .
```

**Step 2: Parse each tag into a structured debt item**

For each discovered tag, extract:
- **File path** and **line number** where the tag appears
- **Description** from the tag content
- **Category** (infer from context: Security, Architecture, Testing, Data quality, Operations)
- **Severity** (assign based on risk assessment — see Debt Item Format below)

**Step 3: Cross-reference with evaluation findings**

Merge POC-DEBT scan results with:
- Code review findings (🔴 Must Fix and 🟡 Should Fix items)
- PoC evaluation refactoring backlog items
- Security scan findings

**Step 4: Produce consolidated debt ledger, then the scorecard**

Output the full debt ledger as a versioned artifact (see below). Then write `POC-DEBT-SCORECARD.md` from it (see Technical Debt Scorecard below). Every `POC-DEBT` tag found in Step 1 must appear in the scorecard's Debt Inventory (`poc-guidelines.md` Scorecard Rule 1). The ledger is this skill's working register and does not substitute for the scorecard.

**Automation note:** This scan should be triggered:
- At the conclusion of every PoC (before evaluation)
- Before any production handoff
- As part of the QA validation gate

### Debt Item Format

Each debt item in the ledger uses the following structured format:

```markdown
### DEBT-{ID}: {Short title}

- **Category:** Security | Architecture | Testing | Data quality | Operations
- **Severity:** critical | medium | low
- **Impact:** [What breaks or degrades if this debt is not addressed]
- **Effort:** S (small, indicatively < 4h) | M (medium, indicatively 4-16h) | L (large, indicatively 16h+)
- **Risk if deferred:** [What happens if we ship without fixing this]
- **Source:** POC-DEBT tag | code-review finding | security scan | poc-evaluation
- **Source location:** {file}:{line} (if from code)
- **Recommended owner:** {role}
- **Target sprint:** {sprint-name} | pre-production | post-GA
- **Disposition:** must_fix_pre_prod | can_defer_post_ga | monitor_only
- **Created:** {YYYY-MM-DD}
- **Status:** open | in-progress | resolved | accepted-risk
```

**Severity assignment guide** (tiers and meanings from `poc-guidelines.md` § Debt Scorecard):

| Severity | Meaning | Criteria |
|----------|---------|----------|
| **critical** | Must fix before production | Security vulnerability, data loss risk, compliance violation, missing error handling on critical paths, architectural violation that blocks scaling |
| **medium** | Should fix before production | Performance degradation under load, missing tests for important paths, hardcoded configuration, suboptimal patterns |
| **low** | Nice to have | Code style issues, minor optimization opportunities, documentation gaps |

A `critical` item always takes disposition `must_fix_pre_prod`: `poc-guidelines.md` defines Critical as "must fix before production", so it cannot be deferred or only monitored.

### Promotion Procedure for Debt Items to Production Backlog

When a PoC transitions to production implementation, debt items must be proposed for promotion from the debt ledger to the production task backlog. Per `AGENTS.md` § Task Protocol, "Only orchestrators create/transition tasks": this skill prepares the proposals, and the orchestrator decides on them and creates the tasks.

**Promotion rules:**

| Disposition | Promotion Action |
|-------------|-----------------|
| `must_fix_pre_prod` | Propose a task with priority `P0` and target sprint = current or next |
| `can_defer_post_ga` | Propose a task with priority `P1` and target sprint = post-GA sprint |
| `monitor_only` | Do not propose a task; add to risk register with monitoring criteria |

**Promotion procedure:**

1. Filter the debt ledger for items with disposition `must_fix_pre_prod` and `can_defer_post_ga`.
2. For each item, write a promotion proposal, and report the proposals to the orchestrator:
   ```markdown
   #### Proposal: Resolve DEBT-{debt-id} — {title}
   - **Proposed priority:** {P0 | P1 — per the promotion rules above}
   - **Proposed owner:** {recommended owner from debt item}
   - **Effort:** {S | M | L — from debt item}
   - **Target sprint:** {target sprint from debt item}
   - **Depends on:** [any prerequisites]
   - **Artifact refs:** [debt-ledger-v{N}, poc-{name}-v{N}]
   ```
3. The orchestrator creates each accepted proposal as a task, per `AGENTS.md` § Task Protocol: a row in `docs/tasks/active-tasks.md` with the columns `ID | Title | Owner | Status | Priority | Depends on | Last update`, and a brief at `docs/tasks/task-<ID>.md` (objective, inputs, outputs, acceptance criteria). The orchestrator assigns the sequential ID and may change the proposed priority or owner.
4. Sync created tasks to GitLab issues (see gitlab-management skill).
5. Record `promoted_to=T{ID}` for each created task in the next debt-ledger version (versions are immutable; see below).

**Debt ledger versioning:**
```
docs/artifacts/debt-ledger-v1.md
docs/artifacts/debt-ledger-v2.md
```

Each version is immutable. Create a new version when items are added, resolved, or promoted.

### Technical Debt Scorecard (Enhanced)

The Technical Debt Scorecard is `POC-DEBT-SCORECARD.md` in the PoC root. Write it in the structure `poc-guidelines.md` § Debt Scorecard › Scorecard Format defines — `## Hypothesis`, `## Result`, `## Debt Inventory`, `## Summary`, `## Recommendation` — unchanged and in that order. Count the `## Summary` tiers from the debt ledger's per-item severity. Then append the following sections after `## Recommendation`:

```markdown
## Scorecard Source
- Date: {YYYY-MM-DD}
- Debt ledger: debt-ledger-v{N}

## Severity by Disposition

| Severity | Total | must_fix_pre_prod | can_defer_post_ga | monitor_only |
|----------|-------|-------------------|-------------------|--------------|
| Critical | {N} | {N} | 0 | 0 |
| Medium | {N} | {N} | {N} | {N} |
| Low | {N} | {N} | {N} | {N} |

## Summary by Category

| Category | Total | Critical | Estimated Total Effort |
|----------|-------|----------|----------------------|
| Security | {N} | {N} | {effort} |
| Architecture | {N} | {N} | {effort} |
| Testing | {N} | {N} | {effort} |
| Data quality | {N} | {N} | {effort} |
| Operations | {N} | {N} | {effort} |

## Top Remediation Sequence (First Production Sprint)
1. DEBT-{ID}: {title} — {effort} — {owner}
2. DEBT-{ID}: {title} — {effort} — {owner}
3. DEBT-{ID}: {title} — {effort} — {owner}

## Risk Acceptance Register
[Items with disposition=monitor_only and their monitoring criteria]
```

The scorecard is included as part of the PoC evaluation output and referenced in production handoff checkpoints. The Tech Lead reviews it before the PoC is closed, and no PoC task may be marked complete without it (`poc-guidelines.md` Scorecard Rules 3–4).
