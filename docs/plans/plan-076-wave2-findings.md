# plan-076 — the four defects golden wave 2 surfaced

**Status: scoped 2026-09-26, awaiting approval to dispatch.**
Based on: `docs/tasks/task-T528.md`, `docs/tasks/task-T534.md`;
`docs/decisions/ADR-007-command-contract-authority.md`;
`docs/artifacts/protected-paths-v1.md` §5; `AGENTS.md` § Task Protocol.

## 0. Why these get rows now

Wave 2 found four real defects and correctly fixed none of them — each was outside its grant. They
are recorded here as tasks rather than left in a ledger note, because `T518`'s closure established
the rule this project keeps relearning: **a hand-fix plus a ledger note is not a fix**, and the user
has previously had to ask explicitly for carried defects to be given tasks.

| # | Defect | Task |
|---|---|---|
| 1 | `/batch` step 5's manifest cannot be written into the file step 5 names | **`T535`** |
| 2 | `/sprint-status` declares no colour for `in_review` | **`T536`** |
| 3 | `validate-tasks.py` never reads the `Depends on` cell | **`T537`** |
| 4 | the `skillify` case's `brief.md` contradicts its own `expect.py` | **folded into `T530`** |

Defect 4 is folded rather than given its own row because `T530` already exists to fix exactly this
class — a golden case's `brief.md` disagreeing with its own case after a contract change — and was
already widened once for the same reason. A third row would be ceremony.

## 1. `T535` — the `/batch` conflict, and why it is an adjudication not a patch

`batch.md` step 5 declares a five-field manifest — *"Unit ID, description, assigned agent, branch,
status"* — written into `docs/tasks/active-tasks.md`. `AGENTS.md` § Task Protocol pins that file to
exactly `ID`, `Title`, `Owner`, `Status`, `Priority`, `Depends on`, `Last update`, and
`docs/tasks/validate-tasks.py` hard-fails any other cell count.

**Four of step 5's five fields map onto that schema. `branch` maps onto nothing, and the two spare
columns are taken.** So the manifest cannot be written where step 5 says to write it. A second
collision sits behind it: `U<n>` unit IDs fail `ID_RE = ^T\d{3,}$`, and `bug-report.md` records that
non-`T` rows are silently deleted by `install.sh --update`.

**`AGENTS.md` outranks a command file**, so `ADR-007` **branch 1** may genuinely fire — amend the
command. But that is not obviously right either: a batch of parallel units plausibly *needs*
somewhere to record branches, and "delete the requirement" may be the wrong repair. The honest
options include a separate manifest document, an `active-tasks.md` schema change (which is an
`AGENTS.md` amendment and a much larger decision), or dropping `branch` on the grounds that
`agent/<name>/<task-id>` already makes the branch derivable.

**`T535` decides. It is explicitly not told which way.** A task that arrives at "amend the command to
drop `branch`" having argued it on the merits is a good outcome; one that arrives there because it
was the smallest edit is not.

## 2. `T536` — a stable component with an unexercised contract gap

`sprint-status.md` step 8's first bullet declares four node sources — `pending`, `in_progress`,
`blocked`, `in_review` — and its colour bullet declares only three non-`done` colours
(`done=green, in_progress=yellow, blocked=red, pending=gray`). **A sprint containing an `in_review`
task therefore has a node the contract requires drawn and gives no way to colour.**

**This needs stating plainly, because it is a limitation of the ladder and not only of the command:
`/sprint-status` was promoted to `stable` by `T534` while carrying this gap.** Its golden case passes
honestly — the case's fixture ledger has four rows, all `pending`, and its single `in_review`
occurrence is the status-legend line, not a data row (verified). So the gap is real and **the only
golden case for that command cannot reach it**.

That is not a reason to un-promote: the case is honest, the criteria were met, and wave 2's
implementer was right to refuse to build an `in_review` fixture *purely* to turn the case red —
choosing a fixture to manufacture a failure is the mirror image of choosing one to manufacture a
pass. But it does mean **`stable` here certifies "passes the cases that exist", not "has no known
contract gaps"**, and this is the first concrete instance where those differ. Worth remembering
before treating a `stable` label as stronger than it is.

`T536` fixes the contract. Whether the case should then be extended to exercise it is a **second,
separate question** the task must answer rather than assume — extending it touches a protected path.

## 3. `T537` — a validator that silently accepts a dangling dependency

`docs/tasks/validate-tasks.py:203` destructures a row as
`task_id, _, _, status, priority, _, last_update = row.cells`. **The sixth cell — `Depends on` — is
discarded and never read**, and no check in the validator's inventory resolves a dependency against
the known ID set.

So a row whose `Depends on` names a task in neither ledger passes `PASS` silently. This matters more
than it looks: the ledger's dependency edges are what `/sprint-status` reconstructs its DAG from, and
`plan-074` §3's queue ordering leaned on them. An unvalidated edge is a dependency nobody is
checking.

`T537` adds the check. **Two traps, both to be verified rather than assumed:**

1. **It must not fire on the real ledger.** Run it against the live tree before and after; if it
   reports violations on rows that are actually fine, the check is wrong, not the ledger.
2. **A dependency may legitimately point into `completed-tasks.md`** — that is the normal case for a
   satisfied dependency, and `T532` currently depends on the completed `T531`. Resolving only
   against `active-tasks.md` would flag every satisfied dependency as dangling.

## 4. What none of these do

**None promotes anything.** All three are `P2`, so per `T524`'s correction they do not enter criteria
3/7's open-defect scan and cannot block the promotions they might enable. `T535` may make `/batch`
promotable; that is a separate component-state task, as `T526` and `T534` were.

`T536` and `T537` touch no protected path. `T535` touches none either unless its verdict reaches the
golden case, in which case its grant is conditional and narrow — the same shape `T527` used, which
correctly stopped at `expect.py` and reported a blocker rather than widening itself.
