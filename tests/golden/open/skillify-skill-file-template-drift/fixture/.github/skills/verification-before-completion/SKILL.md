---
name: "verification-before-completion"
description: "Evidence before success claims. Use before marking tasks done, committing, opening MRs, or declaring fixes complete."
---

# Verification Before Completion

## Rails
**Inputs**: An imminent `done` status transition, commit, push, MR creation,
validation-gate `PASS` verdict, or a claim that a bug fix/refactor is
complete — per `AGENTS.md`'s mandatory Skill Workflow table, "marking work
done, commit, MR, release" requires this skill before the claim is made.

**Out of scope**: Does not define what the underlying task's acceptance
criteria are (those come from the task brief or `maturity-promotion-
criteria-v1.md`-style artifacts) — this skill only governs how a completion
claim about them must be evidenced, not what the criteria themselves say.

**Failure mode**: A completion claim made without a fresh command's exit
code and output is a violation of the Iron Rule ("NO COMPLETION CLAIMS
WITHOUT FRESH VERIFICATION EVIDENCE"); per Orchestrator Enforcement, the
orchestrator must reject the `done` transition when the task brief's
verification steps lack recorded evidence in the checkpoint or task comment.

## Purpose

Prevent false completion claims. Every status assertion must cite fresh command output.

## When to Use

- Before marking a task `done` in `docs/tasks/active-tasks.md`
- Before commit, push, or MR creation
- Before validation gate `PASS` verdicts
- After bug fixes or refactors
- Before release or deployment steps

## Iron Rule

```
NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE
```

## Gate Procedure

```
1. IDENTIFY — what command proves the claim?
2. RUN     — full command in current workspace state
3. READ    — exit code + complete output
4. VERIFY  — output supports the claim?
5. CLAIM   — state result with evidence (command + outcome)
```

## Claim → Evidence Map

| Claim | Required evidence |
|-------|-------------------|
| Tests pass | Test runner: 0 failures |
| Linter clean | Linter: 0 errors on changed paths |
| Build succeeds | Build command: exit 0 |
| Bug fixed | Original reproduction now passes |
| No drift | `verify.mjs`: OK |
| Release ready | `verify-release-docs.py --tag X`: passed |
| Gate PASS | Checklist filled with command output |

## Red Flags — Stop

- "Should work", "probably fixed", "seems fine"
- Satisfaction before running verification
- Trusting agent self-report without VCS or test output
- Citing a previous run from an earlier session

## emage.code Standard Commands

```bash
# Validation super-gate (implementation changes)
python3 implementation/scripts/check.py --root implementation --required

# Projection drift
node implementation/scripts/verify.mjs --root implementation

# Repository test suite
python3 tests/run.py

# Release docs (maintainers)
python3 scripts/verify-release-docs.py --tag vX.Y.Z
```

## Orchestrator Enforcement

The orchestrator must reject `done` transitions when the task brief lists
verification steps that lack recorded evidence in the checkpoint or task comment.
