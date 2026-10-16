# plan-080 — The authority layer is wrong, and the queue is not converging

**Created:** 2026-09-26
**Based on:** `docs/artifacts/skillify-output-path-resolution-v1.md`; `docs/tasks/task-T532.md`;
`docs/tasks/task-T530.md`; `docs/plans/plan-079-install-sync-gap.md` §3.
**Scopes:** `T545`, `T546`, `T547`, `T548`.

## 1. What T532 turned up, and why it is not four unrelated findings

T532 was dispatched to adjudicate one hardcoded path in one experimental command. It returned a
verdict on that path — and four findings that are the same finding at different altitudes.

The repository has **two audiences** (the emage.code authoring checkout, and any project that ran
`install.sh`) and **no vocabulary for the distinction**. Every defect below is a consequence:

| # | Finding | Task | Altitude |
|---|---|---|---|
| 1 | `AGENTS.md` § Knowledge Base bullet 2 omits `.claude/` from the hand-edit prohibition and names the wrong program for the trees it governs | `T545` | the **authority** that decides these cases |
| 2 | No command declares its audience; `/discover-skills` and `/handoff`, both `stable`, name paths `install.sh` never installs | `T546` | the **class** |
| 3 | Four commands cite `04-protocols.md`, which exists nowhere | `T547` | an **instance** with a different cause — a citation nobody checked |
| 4 | The skillify golden checker's docstring quotes the pre-T532 path clause | `T548` | the **evidence layer** trailing its own subject |

Finding 1 is ordered first (P1) because it is the text T527, T532 and prospectively T543 and T546 all
cite. T532 had to rest its verdict on bullet 1 rather than bullet 2 precisely because bullet 2 was
unusable — a workaround, documented as one, not a repair.

## 2. The measurement that makes this concrete

After T532's single-command knowledge change, the **repo-root** projections went stale by
**48 / 30 / 30 lines** (`.claude/commands/skillify.md`, `.claude/skills/skillify/SKILL.md`,
`.github/skills/skillify/SKILL.md`) while `sync.mjs --check` reported "no drift across 577 files" and
`generate-registry.py --check` reported "registry is up to date". **Both gates were green and both
were right about what they inspect.** Neither inspects the trees the tooling in this repository
actually reads.

That is `T543`, already scoped, and this measurement raises its urgency above its P2. It also sharpens
its statement: "refreshed by no generator" is more precisely *"refreshed only by
`scripts/install.sh --update`, which the installer refuses to run at the repository root without that
flag and whose own warning says it destroys local edits."* The only sanctioned refresh path is a
destructive one.

## 3. The convergence problem, stated plainly

`plan-079` §3 recorded that the queue had held at **6 active for three rounds** because every task
reports defects rather than working around them. This plan takes it to **10**.

That is the system working as designed and it is also a trend that does not terminate. Two rounds of
honest reporting have each produced more findings than they closed. The arithmetic:

- **Closed this round:** T530, T532 (both in review, MRs !412 and !413).
- **Opened this round:** T545, T546, T547, T548.
- **Net:** +2, and the four new rows are on average *larger* than the two closed.

**The phase will not converge by executing findings as they arrive.** Each adjudication is sound and
each finding is real; the problem is that the corpus is being audited for the first time, and a
first-pass audit of 79 components generates findings faster than one task per round can absorb them.

### What actually closes this

Not more tasks. One of:

1. **Batch the mechanical residue.** `T547` (four dangling citations) and `T548` (one docstring) are
   `mechanical` tier. Several of the standing P2 rows are too. These do not each need a round.
2. **Answer the class, then stop finding instances.** `T546` is the only task here that, once
   decided, makes future instances non-findings — a declared `audience:` field turns "is this path
   right?" from a judgment call into a schema check. It is P2 and it is the highest-leverage row in
   the queue. **That mismatch is worth the user's attention.**
3. **Accept a standing-debt register.** Some findings are real, small, and not worth a task each.
   There is no mechanism for recording one without opening a row, so every finding becomes a row.
   `TECHNICAL-DEBT.md` exists but is legacy and unused by this workflow.

**Recommendation:** do (2) next — dispatch `T546` ahead of the mechanical rows despite its P2 — and
put (3) to the user, because it is a workflow change and not the orchestrator's to make.

## 4. A deliberate, contestable priority choice, surfaced not buried

`T546` names `command/discover-skills`, `command/handoff` and `command/prepare-release` in its
`**Affects:**` field at **P2**. `check-maturity.py:_ledger_defect` filters on
`DECLARED_PRIORITIES = {"P0","P1"}` **before** reading `**Affects:**`, so at P2 the declaration is
recorded but inert — criteria 3 and 7 never see it.

**At P1 the maturity gate would go red for two commands currently claiming `stable`**, plus their
owning agents. Verified empirically on the scoping branch: with the rows as written, 79 components, 0
failing.

The orchestrator chose P2 on the reasoning that both commands were promoted against criteria that did
not include audience-portability — the `stable` claim was not fraudulent, a new criterion emerged.
**That reasoning is contestable.** An unperformable step 1 in a `stable` command is a real defect, and
a user could reasonably want it red. The change is one character in one column. **It is the user's
call and it is recorded here so it is a decision rather than an omission** — the more so because the
orchestrator has previously stated this repository's P2 rule backwards in four merged documents.

## 5. Sequencing

```
T545 (P1, AGENTS.md)          ─── independent, no contention
T546 (audience decision)      ─── no Bash owner, artifact only, no contention
T547 (04-protocols)           ─── implementation/knowledge/ → registry contention
T548 (skillify checker)       ─── tests/golden/ → evaluator-hash contention
                                   AND blocked on !412 + !413 merging
```

Contention rules, unchanged: at most one open task touching `implementation/knowledge/` (registry and
projection contention) and at most one touching `tests/golden/**` (evaluator-hash contention).

`T547` contends with **`T538`** (also `implementation/knowledge/`). `T548` contends with **`T539`** and
**`T544`** (all `tests/golden/**`). So of the ten active rows, at most **four** can run concurrently,
and `T548` cannot start at all until both open MRs land.

`T545` and `T546` are the only two rows in the queue with **no** contention against anything. That is
a second reason to run them next, independent of §3's leverage argument.

## 6. What this plan does not do

- Does not amend `AGENTS.md`, `command.schema.json`, any manifest, `install.sh` or any command file.
- Does not touch `tests/golden/**` or `scripts/scorecard.py`.
- Does not refresh the evaluator-hash baseline — `T530`'s change drifts `tests_golden` and the **v9**
  refresh is pending explicit user authorization, the ninth such request.
- Does not resolve §3's item 3 (a standing-debt register), which is a workflow change for the user.
- Does not change any priority. §4 records the argument; it does not act on it.
