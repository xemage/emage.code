# T516 — Narrow the §3.5 defect-check from free-text scan to a declared field

**ID:** T516
**Owner:** Backend Developer
**Status:** pending
**Priority:** P2
**Tier:** standard
**Depends on:** —
**Affects:** —
**Created:** 2026-09-24
**Completed:** —
**Based on:** docs/plans/plan-067-t516-defect-check-declared-field.md

> **Priority note — read before editing this brief.** `P2` is assigned on merit (§6) and has a side
> effect: `P2` rows are not scanned by the very check this task fixes, so this brief may name
> component ids literally as examples. **That is safe only at `P2`.** If this task is ever
> re-prioritised to `P0`/`P1`, every literal id below must first be converted to display form, or
> this brief will demote the components it merely cites — which is the bug itself.

## 1. Objective

`_ledger_defect()` in `implementation/scripts/check-maturity.py` decides whether a component has an
open defect by regex-scanning the entire free text of every active `P0`/`P1` task brief for the
component's id. It cannot distinguish *"this component is broken"* from *"this document is worth
reading."*

Replace the free-text scan with an explicitly declared field in the brief, and update §3.5 of
`docs/artifacts/maturity-promotion-criteria-v1.md` to match. Mentioning a component must stop being
the same act as indicting it.

## 2. Evidence — two failures, both hit while drafting one brief

The matcher uses `(?<![\w-])<id>(?![\w-])`. Neither `/` nor `.` is in `[\w-]`, so:

1. **The mandated branch convention is self-blocking.** The Git Workflow rules require agent
   branches named `agent/<agent-name>/<task-id>`. Written into a brief, `agent/solution-architect/T515`
   matches the id `solution-architect` and blocks that agent's own promotion claim — so *any*
   `P0`/`P1` brief that documents its own branch name per the mandated convention demotes its owner.
2. **An instruction cannot be cited by filename.** Citing `.claude/rules/git-workflow.md` matches
   `instruction/git-workflow`, demoting a `stable` instruction for the offence of being referenced.
   The same holds for `coding-standards.md`, `security-guidelines.md` and `poc-guidelines.md` — the
   four documents briefs most need to cite.

Both were confirmed by running the script against a real draft, not by reading the regex. Both were
worked around by rephrasing in `T515`; that workaround is invisible to whoever writes the next brief
and will be rediscovered by trial and error each time.

This stayed latent because almost every agent was `experimental` until `T514`. With 25 agents,
4 instructions and 7 skills now `stable`, it is routine.

## 3. Scope

**In scope**

- `_ledger_defect()` in `check-maturity.py`, and only it.
- A declared field in `docs/tasks/_template.md`, e.g. `**Affects:** <category>/<id>, … | —`.
- §3.5 of `maturity-promotion-criteria-v1.md`.
- A ledger check (`validate-tasks.py`) enforcing §5.2 below.
- Tests in `tests/functional/test_check_maturity.py` (and the ledger validator's tests).

**Explicitly out of scope**

- `_mentions()` itself. It has a second consumer, `_referenced_in_agents_or_commands()`, where
  matching a mention genuinely *is* the intent. Changing the shared helper would break that check.
  Fix the caller, not the helper.
- The golden-case half of §3.5 (`known_failing` / `tracked_defect`). That half keys off structured
  YAML already and has none of this problem. Leave it exactly as is.
- Re-running promotions, or promoting anything. This task changes a gate; it does not walk through
  it. Any component that becomes promotable as a result is a separate task's work.

## 4. Migration surface

**One brief.** The active ledger currently holds a single row (`T515`, `P1`). Completed briefs are
never scanned — `_ledger_defect()` skips rows with status `done`/`cancelled`, and the ledger
invariant keeps terminal rows out of `active-tasks.md` entirely. So the migration is one file today
and grows with every future `P0`/`P1` row. This is the cheapest it will ever be.

`_template.md` already carries precedent for an additive optional field: the `Tier` field (`T440`)
was introduced with explicit "existing briefs remain valid without it" language. Follow that pattern
and cite it.

## 5. Design constraints

1. **The gate must never become silently under-strict.** This is the one hard requirement. The
   obvious implementation — "scan `Affects:` if present, otherwise assume nothing is affected" —
   converts a loud false positive into a silent false negative, which is strictly worse: it lets a
   component with a real open defect claim `stable`. Do not do that.
2. **Therefore: the field is mandatory for `P0`/`P1` briefs, and a missing field is a hard error.**
   A `P0`/`P1` active row whose brief declares no `Affects:` field must make the relevant check
   *fail loudly* with a message naming the brief, not pass quietly. `P2` briefs need not declare it.
   Enforce this in `validate-tasks.py` as a new numbered check, consistent with C1–C10.
3. **Decide the `Title` scan explicitly.** §3.5 currently scans the ledger `Title` as well as the
   brief body. Once `Affects:` is mandatory the title scan is arguably redundant, and it carries the
   same false-positive risk in a field with no room to rephrase. Keep it or drop it — but state
   which and why in your summary. Do not leave it unaddressed.
4. `—` must be a valid value, meaning "this task indicts no component." Many tasks legitimately
   affect nothing: documentation, tooling, this task itself.
5. Validate declared ids. An `Affects:` entry naming a component that does not exist is a typo that
   would silently protect the component it was meant to indict; reject it.
6. §3.5's prose and the implementation must agree when you are done. The current text says a brief
   that "explicitly names" the id — the intent was always indictment; only the implementation
   over-read it. Say so in the revision rather than presenting this as a change of policy.

## 6. Priority rationale

`P2`, honestly. The defect makes the gate **over-strict, never under-strict** — it can block a
promotion that should succeed, but it cannot let through one that should fail. Nothing is currently
mis-promoted, and the workaround holds. It blocks no critical path, which is the definition of `P2`
in this repo's vocabulary. `plan-066` §6 already recorded it as "not urgent"; assigning `P1` here
would contradict that written assessment to make the work look more important than it is.

## 7. Ownership note

Owner is the **Backend Developer** — script, validator and test work, which is squarely its role.

One disclosure: this task loosens a gate that governs the owner's own component, which is already
`stable`. The interest is real but weak and unavoidable — it applies identically to all 25 `stable`
agents, the change cannot promote anything by itself (§3 puts promotion out of scope), and constraint
§5.1 is written specifically so that "loosening" cannot become "weakening." Flagged rather than
left for a reviewer to notice.

## 8. Expected outputs

- Modified `check-maturity.py`, `_template.md`, `maturity-promotion-criteria-v1.md` §3.5,
  `validate-tasks.py`.
- `T515`'s brief migrated to declare its `Affects:` field, and its §8 workaround note removed —
  once the matcher is fixed, the contorted phrasing is no longer needed. If `T515` is still open when
  you run, coordinate through the orchestrator rather than editing another in-flight task's brief
  unilaterally; if it has closed, its brief is a completed artifact and must not be edited at all —
  say which case applied.
- Tests covering: both §2 regressions (branch name, instruction filename), a genuine indictment
  still blocking, a missing field on a `P0`/`P1` brief failing loudly, `—` accepted, and an unknown
  id rejected.

## 9. Acceptance criteria

- [ ] A brief citing `.claude/rules/git-workflow.md` and spelling out `agent/<slug>/<id>` no longer
      demotes anything — with a test that fails against the current implementation.
- [ ] A brief that genuinely declares a component defective still blocks it — with a test.
- [ ] A `P0`/`P1` brief with no `Affects:` field produces a loud failure, not a pass.
- [ ] `_mentions()` is unchanged and `_referenced_in_agents_or_commands()` still behaves identically.
- [ ] `check-maturity.py` reports **0 failing** across all 79 components.
- [ ] `pytest tests/functional` passes with no reduction in test count.
- [ ] The `Title`-scan decision is stated and justified.
- [ ] §3.5's prose matches the implementation.
- [ ] No component's `maturity:` value is changed by this task.

## 10. Working agreement

Branch from `develop` in a worktree, named per the agent-worktree convention in the Git Workflow
rules under `.claude/rules/`. Do not work in the primary checkout. Conventional Commits. Do not merge
your own branch and do not push to `develop` or `main` — hand the branch back and the orchestrator
opens the MR.

## 11. Blocker protocol

Report blockers as `technical` | `dependency` | `unclear_requirements` | `external`, with severity
`critical` | `major` | `minor`. Max 2 retries, then escalate.

If you conclude that the declared-field approach is wrong — for instance that constraint §5.2 makes
briefs too noisy to be worth it — report that as a finding with your reasoning instead of
implementing something you do not believe in. A reasoned "this design is worse than the bug" is a
valid outcome of this task.
