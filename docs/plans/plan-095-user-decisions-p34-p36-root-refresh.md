# plan-095 — Three user decisions: accept ADR-007 (P34), close P36, refresh the repo root

**Created:** 2026-10-01
**Based on:** the user's answers of 2026-10-01; `docs/plans/plan-093-validate-workflow-repair.md` §4 (P36);
`docs/plans/plan-092-poc-contract-amendments.md` §4 (P34); `docs/plans/plan-082-root-refresh-and-followups.md` §2 (the refresh procedure).
**Scopes:** no task rows. Each item below is a recorded user decision executed directly by the orchestrator through an MR,
following the precedent for the one-off refresh in plan-082 §2.

## 1. P34: ADR-007 accepted

ADR-007's header changes from `proposed` to **Accepted**, with the user's approval and today's date. The stale `Tasks`
line is corrected to name the tasks that implemented and applied the ADR. The body is unchanged. From now on, rulings
under ADR-007 rest on an accepted decision, not on its use as a procedure (see `poc-contract-resolution-v1.md` §9.1,
which described the earlier workaround). Changing it now needs a superseding ADR.

The part of P34 about **agent-definition authority** (FU-D, an ADR ranking agent and skill definitions) is **not** decided
here. The T542/FU-C precedent, extended to skill files in `poc-skills-alignment-v1.md` §10.2, remains the working
basis. That part stays parked as **P34b**, with the trigger: a ruling that cannot rest on a file's own self-description.

## 2. P36: closed

**Decision: `/validate-workflow` does not check plan approval.** Plan approval is the user's Approve / Revise / Reject
decision, not a VERDICT-producing gate. Checking it falls outside validating the automated gates. T566's ruling stands
as merged (step 5's closing sentence), and no command or golden change follows.

## 3. Root refresh: second `--projections-only` run

The user approved it. Following plan-082 §2:
- The refresh was **rehearsed** on a disposable detached worktree at `a81c965`, using that worktree's own
  `scripts/install.sh`. Exit 0. `docs/` and `implementation/` were byte-identical before and after. Exactly the 63 declared
  paths changed, with nothing extra or missing. `--print-drift` then returned `[]`.
- The real refresh is a separate MR on `chore/root-refresh-2`. It reproduced the same 63 paths and left `docs/tasks/`
  byte-identical. In the same MR the declared drift list in `tests/_baselines/root-install-drift.json` is emptied, so
  the parity gate proves the refresh is complete.

From here on, every knowledge change again declares its root paths, or refreshes the root, in the same MR.
