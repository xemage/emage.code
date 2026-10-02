# T576 — Adjudicate the PoC debt-tag examples that model forbidden security shortcuts (P42)

**ID:** T576
**Owner:** Solution Architect
**Status:** done
**Priority:** P2
**Tier:** judgment
**Affects:** —
**Depends on:** —
**Created:** 2026-10-02
**Based on:** `docs/plans/plan-098-poc-security-shortcut-examples.md`; `docs/artifacts/poc-skill-command-overlaps-v1.md` §13 (O1)
and §16.3 (P42).

## 1. What and why

The PoC track tells agents to tag shortcuts with `POC-DEBT`. Its **model examples** include shortcuts that the
repository's security rules forbid outright, even in a PoC:
- "No input validation"
- "disabled security"
- "CORS allow-all"

An agent that copies an example would write code that breaks an Immutable Security Constraint. Decide the repair and
write it down. **Decision only.** Do not edit any instruction, skill, command, agent or golden case.

## 2. Facts verified by the orchestrator on `develop` `0956b1d`

| Site | Maturity | Text |
|---|---|---|
| `instructions/poc-guidelines.md:80–90` § Inline Debt Tags › Examples | **stable**, `applyTo: "**"` | `# <!-- POC-DEBT: No input validation; production must validate all user input -->` above `def create_user(name, email): return db.insert(...)`. Also the "Hardcoded connection string" (`postgresql://localhost:5432/poc_db`, no credential) and "Synchronous call" examples. |
| `instructions/poc-guidelines.md:119` § Debt Scorecard › Scorecard Format (template Debt Inventory) | **stable** | example row `\| 2 \| src/api.py \| 34 \| Validation \| No input validation \| M — add schema validation \|`. The same forbidden shortcut appears again, this time as a model scorecard entry. |
| `skills/rapid-prototyping/SKILL.md:33` (placement rules) | experimental | "For configuration shortcuts (e.g., hardcoded values, **disabled security**), place the tag in the config file." |
| `skills/rapid-prototyping/SKILL.md:35–47` (examples) | experimental | `POC-DEBT: No input validation — add comprehensive validation before production` above `def create_user(data): return db.users.insert(data)`; `POC-DEBT: CORS allow-all — restrict origins before production` with `origin: "*"`; and an "in-memory store" example. |
| `instructions/security-guidelines.md:150–158` § Immutable Security Constraints | **stable**, `applyTo: "**"` | "absolute and cannot be overridden by any agent, configuration, or runtime decision". **3.** "No disabled security checks — Security middleware, input validation, and authentication checks must never be bypassed, even in development or PoC mode." **4.** "No unvalidated external input — Every input from outside the system boundary … must be validated before use." |
| `security-guidelines.md:16–20` (Rails) | stable | "Does not grant any agent authority to disable a security control 'temporarily,' even in PoC or development mode — the Immutable Security Constraints section forbids that outright, **superseding any speed-over-completeness pressure from `poc-guidelines.md`**." |
| `poc-guidelines.md` (Rails, "Out of scope") | stable | "Does not waive the Immutable Security Constraints in `security-guidelines.md` (no exposed secrets, no real PII in demos) merely because a workstream is time-boxed." |

**Authority, as the documents state it.** Both instructions are stable. `security-guidelines` declares that it
supersedes `poc-guidelines` on this point, and `poc-guidelines` declares that it does not waive those constraints.
Their own words settle the precedence, so **no P34b ranking is needed**. Verify this reading yourself.

**Also in scope to check:** `security-guidelines` § API Security, "never `Access-Control-Allow-Origin: *` with
credentials". Decide whether the CORS example breaks a constraint or is only a weaker default. Also decide whether
the "hardcoded connection string" example is acceptable. Constraint 1 forbids secrets; the example carries no
credential.

**Copies that ship to users.** The repo-root `.claude/rules/poc-guidelines.md` and every platform projection carry
the same example, so installed client projects receive it. A fix flows through regeneration plus root-drift
declarations, or through a later user-approved root refresh.

**Golden coupling.** No golden case quotes these example sections. In `tests/golden/open/`, with `held-out` pruned,
the only hit is the `evaluate-poc` case's *fixture report*: a debt row "No input validation or length limit on search
queries", rated CRITICAL. That is an evaluation input recording a violation, not a quote of the guideline. Say
whether your ruling makes that fixture misleading. Any change to it is a protected-path question.

## 3. What to decide

1. **The authority basis**, quoted.
2. **For each example and placement rule:** is it forbidden (breaks a constraint), acceptable, or acceptable with a
   condition? Give exact before/after replacement wording. Replacements must still teach tagging well: a legitimate
   PoC shortcut, specific and paired with its production remedy.
3. **Whether `poc-guidelines` needs a positive rule.** For example: "Shortcuts may never relax the Immutable Security
   Constraints; security work may be *simplified* but not *removed*", with a pointer to `security-guidelines`.
   Specify the wording if so. This is the stable instruction's own text, so be conservative and quote the basis.
4. **Whether the `evaluate-poc` golden fixture needs any change.** Report only; it is a protected path.
5. **A follow-up table** (owner, files, grant yes/no), and a recommendation on **priority**. The orchestrator will
   put P1 versus P2 to the user. P1 would hold `poc-guidelines` below `stable` while the task is open.

## 4. Output

`docs/artifacts/poc-security-shortcut-examples-v1.md`, with these sections:
- authority basis;
- one section per site;
- the positive rule, if any;
- golden coupling;
- follow-ups and priority recommendation;
- corrections to this brief;
- unverified claims;
- findings outside scope.

## 5. Constraints

- **You have no Bash.** Mark unverified claims.
- **Write exactly one file:** the artifact. Hand it back uncommitted. Do not edit this brief.
- **Read-only.** You may read `tests/golden/open/evaluate-poc-verdict-debt-reconciliation/{brief.md,fixture/poc-evaluation.md}`
  only. Open no other golden case, and never open `tests/golden/held-out/`.
- **Do NOT run `glab mr merge` or any merge/approve API, and do not commit or push.**

## 6. Blocker protocol

Report blockers as `technical` | `dependency` | `unclear_requirements` | `external`, with severity `critical` |
`major` | `minor`. If a fact in §2 is wrong, report it rather than working around it.
