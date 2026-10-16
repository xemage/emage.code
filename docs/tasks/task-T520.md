# T520 — Execute ADR-007 verdicts A, B, D and H-1

**ID:** T520
**Owner:** Backend Developer
**Status:** done
**Priority:** P1
**Tier:** judgment
**Affects:** command/plan, command/new-feature, command/security-audit
**Depends on:** —
**Created:** 2026-09-25
**Completed:** 2026-09-25
**Based on:** docs/plans/plan-070-t520-t521-adr-007-execution.md

## 1. PROTECTED-PATH AUTHORIZATION — read first

**This task is explicitly authorized to modify protected paths under `tests/golden/**`, and cites
`docs/artifacts/protected-paths-v1.md` §5.2 as the reason that authorization is required.**

The authorization is **file-scoped**. It covers exactly these paths and nothing else:

| Path | Permitted change |
|---|---|
| `tests/golden/open/plan-required-sections-compliant/expect.py` | the `*-plan.md` glob only |
| `tests/golden/open/plan-required-sections-compliant/fixture/docs/plans/<file>` | rename only |
| `tests/golden/open/new-feature-checkpoint-line-compliant/{expect.py,fixture/,brief.md,case.yaml}` | full re-purpose |
| `tests/golden/open/new-feature-real-checkpoint-format-drift/{expect.py,case.yaml}` | status flip if it passes |
| `tests/golden/open/security-audit-critical-not-fail/{case.yaml,brief.md}` | category + reason + Category section |
| the H-1 held-out case's `case.yaml` | status flip only |

`scripts/scorecard.py` is **not** authorized and must not be touched. Any other path under
`tests/golden/**` is **not** authorized. If you believe you need one, stop and report a blocker —
per §5.1 this authorization is not extensible by the agent holding it.

## 2. Objective

`ADR-007` (merged, `docs/decisions/ADR-007-command-contract-authority.md`) decided which side of six
contract-vs-corpus conflicts is authoritative. `docs/artifacts/command-contract-resolution-v1.md`
records per-case verdicts, the files each touches, and the paired sibling's fate.

**Execute verdicts A, B, D and H-1.** Verdict C is a separate task (`T521`) because it touches no
protected path. Verdict H-2 requires no action now.

Read both documents in full before editing anything. They are the specification; this brief is
scope, authorization and cautions.

## 3. The four verdicts, and the trap in each

**A — `/plan`, split verdict.** Amend `implementation/knowledge/commands/plan.md` step 5's **path
only** (`docs/plans/<slug>-plan.md` → the `plan-<ID>` form the same file's "Task Creation
Precondition" already states). **Do not touch the six section names** — that half is "fix the
corpus", contract unchanged. Then update the paired sibling `plan-required-sections-compliant`: both
its `expect.py` glob **and** its fixture filename. The six-header check, ordering and mermaid
requirements are untouched. The defect case **stays `known_failing`** — its fixture is a frozen copy
of a shipped document and can never pass. Do not try to make it pass.

**B — `/new-feature`, the one where the zero-sum trap genuinely bites.** Amend `new-feature.md`
Phase 3 step 7 to require a checkpoint per `AGENTS.md` § Checkpoint Protocol. Then **re-purpose** the
sibling `new-feature-checkpoint-line-compliant`: its fixture is itself non-conforming under the
amended contract, so it needs a new fixture *and* a new `check()`, not a re-fixture.

> **Critical caution, and the single most likely way to get this wrong.** Derive the replacement
> check from **`AGENTS.md`'s five-item list** (completed tasks, key decisions, blockers, token
> metrics, next steps) — **not** from `docs/checkpoints/_template.md`'s heading set. The defect
> case's fixture uses `## Summary` where the template says `## Phase summary`, and has no
> `## Maturity distribution` (added later by `T437`). A template-derived check would fail that
> fixture and simply relocate the drift one level down.

**D — `/security-audit`, the only verdict that unblocks a promotion.** A two-field reclassification:
`known_failing_category: tracked_defect` → `capability_gap` in `case.yaml`, plus the reason text and
the `brief.md` Category section. **No command file changes** — the rule must not be amended, because
`security-guidelines.md` independently requires CRITICAL to block. The case stays `known_failing`.

> Because this is the verdict that moves a promotion, the resolution artifact records a reviewer's
> counter-reading (that `capability_gap` over-claims, since the "capability" is a door
> `security-guidelines.md` deliberately closed). You are not being asked to re-litigate it — execute
> the recorded verdict — but if executing it changes your mind, **say so in your report** rather than
> deviating silently.

**H-1 — held-out.** Amend one clause in one command file per the case's own `known_failing_reason`,
then flip that case's `case.yaml` status. Both its fixtures already conform, so **no fixture change**
and it should flip to `expected_pass`.

## 4. Held-out discipline — non-negotiable

`tests/functional/test_golden_held_out_isolation.py` Check B forbids any file outside
`tests/golden/held-out/` from naming a held-out case ID as a whole token. It will fail the build.

- Never write a held-out case ID into a commit message, a brief, a report, or any file outside that
  directory.
- The resolution artifact deliberately withholds which commands H-1 and H-2 belong to, and states
  promotion impact **jointly** for the pair so no verdict is pinned to a command. **Preserve that.**
  You may read the case to do the work; you may not disclose its identity in anything you write.
- Note that this brief's `**Affects:**` field lists only the three non-held-out commands, for the
  same reason. That omission is deliberate and is not an oversight to correct.

## 5. Do NOT promote anything

Verdict D is expected to let `security-engineer` clear agent criteria 3 and 7, and
`/security-audit` clear command criterion 7. **This task must not change any `maturity:` value.**

Two reasons. First, scope: executing a verdict and acting on its consequence are different tasks.
Second, mechanics: this brief is `P1` and declares `command/security-audit` in `**Affects:**`, so
that component stays blocked from the ledger side until **this row archives**. Promotion is a
follow-up after closure, exactly as `T515`/`T516` sequenced.

Do run `check-maturity.py` and **report** what became promotable. The resolution artifact says
explicitly not to take its promotion predictions on faith — it also flags that `/security-audit` may
still be blocked by command criterion 6 (a full sentence under `docs/wiki/**`), which `T515` did not
verify. Check that and report it either way.

## 6. Constraints

1. **Never relax a check to make a case pass.** Re-authoring a *hand-authored* fixture to a corrected
   contract is permitted and is not relaxation; loosening a regex or dropping a required field is.
2. **Three of the six cases are expected to stay red** (A, C, H-2). That is the correct outcome, not
   an incomplete job. Do not reclassify them away to tidy the board — `ADR-007` §5 calls that out as
   evading branch 3b.
3. Do not touch `implementation/knowledge/mcp/servers.yaml`, `scripts/scorecard.py`, or any path
   outside §1's table plus the named command files.
4. Do not edit any frozen fixture that is a verbatim copy of a shipped artifact.

## 7. Verification

```
python3 implementation/scripts/check-maturity.py
python3 docs/tasks/validate-tasks.py
python3 -m pytest tests/functional -q          # baseline 722 passed, 23 skipped
python3 scripts/scorecard.py                    # run it; do not modify it
```

Also run each touched golden case directly (`python3 tests/golden/<path>/expect.py
tests/golden/<path>`) and paste the exit codes. For every case whose status you flip, show the
before/after run proving the flip is real rather than asserted.

## 8. Acceptance criteria

- [ ] A, B, D, H-1 executed per the resolution artifact; C and H-2 untouched.
- [ ] B's replacement check derived from `AGENTS.md`, demonstrably passing the drift case's fixture.
- [ ] A's sibling updated in both glob and fixture filename; its header/ordering/mermaid checks intact.
- [ ] Every status flip evidenced by a before/after `expect.py` run.
- [ ] No `maturity:` value changed anywhere.
- [ ] No path touched outside §1's table and the named command files.
- [ ] No held-out case ID anywhere outside `tests/golden/held-out/`.
- [ ] `check-maturity.py` result reported, including whether `/security-audit` clears criterion 6.
- [ ] Test count not reduced.

## 9. Working agreement

Branch from `develop` in a worktree, named per the agent-worktree convention in the Git Workflow
rules under `.claude/rules/`. Do not work in the primary checkout. Conventional Commits. **Do not
merge your own branch and do not push to `develop` or `main`** — there is no "the verdicts were
already decided", "CI is green", or "low-risk" exception. Hand the branch back; the orchestrator
opens the MR.

`git push` is hitting a known GitLab-side transient (`"erase" is an invalid operation`, or
`HTTP Basic: Access denied`) that clears with elapsed time, not retries — observed up to ~45 minutes.
Do not run `glab auth` anything and do not change any `git config credential.*` setting. If it keeps
failing, commit everything and hand back an `external` blocker.

## 10. Blocker protocol

Report blockers as `technical` | `dependency` | `unclear_requirements` | `external`, with severity
`critical` | `major` | `minor`. Max 2 retries, then escalate.

If executing a verdict reveals the verdict is wrong, **stop and report it**. `ADR-007` is a merged
decision; overturning one is a decision task, not something to improvise mid-execution. A partial
delivery with one verdict honestly blocked is a better outcome than four verdicts where one was
forced.
