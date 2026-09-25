# plan-070 — T520 and T521: executing ADR-007

**Status: scoped 2026-09-25, awaiting approval to dispatch.**
Based on: `docs/decisions/ADR-007-command-contract-authority.md`, `docs/artifacts/command-contract-resolution-v1.md`, `docs/plans/plan-064-roadmap-v8-breadth-and-utility.md` Phase 9.

## 0. Why now

`T515` decided; nothing has acted. `ADR-007` and its resolution table are merged, and the table is
specified to the level of "which files a follow-up would touch" per case. Executing it is
`plan-064` Phase 9's critical path and the largest remaining piece of the phase.

## 1. The split, and why it is drawn here

Six verdicts. They divide cleanly on **whether protected paths are involved**:

| Task | Verdicts | Protected paths |
|---|---|---|
| `T520` | A, B, D, H-1 | **yes** — file-scoped authorization |
| `T521` | C | **no** |
| — | H-2 | no action required now |

Keeping C out of `T520` keeps that task's protected-path authorization as narrow as it can be. This
matters: `protected-paths-v1.md` §5.2 requires the authorization to be explicit and named, and §5.1
forbids the holding agent from extending it. A narrower grant is a better grant, and C would have
widened it for no benefit — C touches a command file and a template, nothing frozen.

The two tasks are independent and may run in either order.

## 2. What makes `T520` a `judgment` tier rather than `mechanical`

The resolution table names the files, so it looks mechanical. Three things are not:

1. **B re-purposes a case rather than re-fixturing it.** The sibling's fixture is itself
   non-conforming under the amended contract, so it needs a new fixture *and* a new `check()`. This
   is the only one of the six where the zero-sum trap genuinely bites.
2. **B's replacement check has a specific wrong answer that looks right.** Derived from
   `docs/checkpoints/_template.md`'s headings it would fail the drift case's own fixture — which uses
   `## Summary` where the template says `## Phase summary` and predates `## Maturity distribution`
   (added by `T437`) — and would relocate the drift one level down rather than removing it. The check
   must come from `AGENTS.md`'s five-item list. The brief states this as its most prominent caution.
3. **Three of six cases are meant to stay red.** A, C and H-2 end `known_failing` by design. An
   implementer optimising for a green board would reclassify them, which `ADR-007` §5 names as
   evading branch 3b.

## 3. Promotion is deliberately excluded from both tasks

Verdict D is expected to clear `security-engineer`'s last blocker. Neither task promotes anything.

Scope reason: executing a verdict and acting on its consequence are separate. Mechanical reason:
`T520` is `P1` and declares `command/security-audit` in `**Affects:**`, so that component stays
blocked from the ledger side until `T520`'s row archives — the same sequencing `T515` and `T516`
used. Promotion is a follow-up task after closure.

Both briefs require running `check-maturity.py` and **reporting** what became promotable, and repeat
the resolution artifact's own instruction not to take its promotion predictions on faith. The
artifact additionally flags that `/security-audit` may still be blocked by command criterion 6 (a
full sentence under `docs/wiki/**`), which `T515` never verified; `T520` must check and report that
either way.

## 4. Ownership

`T520` → **Backend Developer**. It owns zero commands, which matters here: one of the two held-out
cases belongs to a `tech-lead`-owned command, so Tech Lead is conflicted on H-1. Backend Developer
also has `Bash`, which this task needs.

`T521` → **Release Manager**. Thematically right for release-document structure, has `Bash`, and does
not own `/prepare-release` (that command's declared agent is `orchestrator`), so it is disinterested
in the promotion its work affects.

## 5. Held-out discipline

`T520` reads held-out cases and edits one `case.yaml`. Its brief states the isolation rule
explicitly, notes that the resolution artifact withholds which commands H-1 and H-2 belong to and
states their promotion impact **jointly** so no verdict is pinned to a command, and instructs that
this be preserved in everything the implementer writes — commit messages and reports included.

`T520`'s `**Affects:**` field lists only the three non-held-out commands for that reason. The brief
says so, so a future reader does not "correct" the omission.

## 6. Expected end state

2 of 6 cases green, 1 reclassified and no longer blocking, 3 correctly still red. One experimental
agent (`security-engineer`) becomes promotable; `orchestrator` and `tech-lead` do not. `tracked_defect`
count goes 6 → 3, which keeps `T411`'s ≥5 `known_failing` floor (3 + 3 `capability_gap`) but narrows
the margin — Phase 9's 14 new cases must carry the replacement difficulty.

## 7. What remains in Phase 9 afterwards

Author 14 golden cases for the uncovered commands (the phase's larger pole, unstarted); decide the
two capability gaps; re-run command promotion readiness; promote whatever `T520` reports as earned.
