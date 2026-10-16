# T561 — Golden wave 3: cases for `/team-status`, `/validate-workflow`, `/new-poc`, `/poc-demo`, `/evaluate-poc`

**ID:** T561
**Owner:** QA Engineer
**Status:** done
**Priority:** P2
**Tier:** judgment
**Affects:** —
**Depends on:** —
**Created:** 2026-10-01
**Based on:** `docs/plans/plan-072-phase9-golden-case-coverage.md` (§1–§5, wave 3); `docs/plans/plan-090-golden-wave-3.md`;
`docs/artifacts/golden-suite-format-v1.md`; `docs/decisions/ADR-007-command-contract-authority.md`;
`docs/plans/plan-084-round-close-and-fired-triggers.md` §4 (P9, P12).

## 1. What and why

These five commands are the **only** commands with no golden case, and all five are `experimental`. Waves 1
(T525) and 2 (T528) covered the other fourteen. **Read `plan-072` §1 before anything else** — it is the reason
this task is shaped the way it is: an agent asked to author cases that unblock promotions has every incentive
to author trivially-passing ones.

## 2. The rules — from `plan-072` §1, binding

1. **Every case quotes a specific clause of its command's declared contract** verbatim in `brief.md`'s
   "What this checks" section. A case that cannot name its clause is not a case.
2. **A `known_failing` outcome is correct.** If an honest case comes out red, it ships red and that command does
   not promote. `ADR-007` §5 — never resolve by relaxing a check — binds authoring as it binds fixing.
3. **An all-green wave is a suspicious result, not a target.** Waves 1 and 2 each had exactly one honest red
   case, and each blocked exactly one promotion while the greens passed clean — the strongest evidence that the
   greens were earned.
4. **This task promotes nothing.** Maturity changes are a separate task.

## 3. Grounding — and two findings you must not paper over

| Command | Corpus | Notes |
|---|---|---|
| `/team-status` | thin / none | Step 7 draws a Mermaid DAG with a declared `Color code:` (T538 made it match `/sprint-status`). Note P19: the `dependency-graphing` skill uses a *different* palette — out of scope for this case, but don't be surprised. |
| `/validate-workflow` | thin / none | **P9:** step 6 requires every gate to emit a VERDICT, but plan approval emits Approve/Revise/Reject and the architecture briefing is defined nowhere as a verdict gate, so the command **likely always FAILs**. An honest case may well be red — that is a finding, report it. |
| `/new-poc` | **none** — zero `POC-DEBT-SCORECARD.md` exist anywhere | **P12:** the debt scorecard is specified in two places — `new-poc` step 11 says `docs/decisions/poc-debt-<slug>.md`; `poc-guidelines` says `POC-DEBT-SCORECARD.md` in the PoC root. That is a contract conflict (ADR-007 branch 1 territory). **Do not resolve it.** If your case's clause depends on it, report the conflict and choose a clause that doesn't, or ship the case red with the conflict as its reason. |
| `/poc-demo`, `/evaluate-poc` | **none** | Hand-authored counter-examples; `plan-072` §2 places the PoC three in `ADR-007` branch 4 territory. |

Hand-authored fixtures are allowed (`golden-suite-format-v1.md` §2.2), but the case's **Provenance** section
must state that no real corpus exists and how you checked.

## 4. Case anatomy — follow the existing suite

`case.yaml` (`id`, `command`, `status`, `tags`; plus `known_failing_reason` and `known_failing_category` if red),
`brief.md` (Command under test / Brief — illustrative, not executed live / What this checks / Pass condition /
Provenance), `expect.py` (≈50 lines, `check(case_dir: Path) -> bool` plus `main()`, a **pure function of bytes
under `case_dir`** — no `__file__` anchoring, no live model call, no reads outside `case_dir`; see
`golden-suite-format-v1.md` §4.2), and `fixture/`. Read three or four existing cases under `tests/golden/open/`
first and match them.

**Prove each checker discriminates:** for every case, show in a temp copy that a fixture violating the quoted
clause returns the opposite result. A checker that returns the same answer for a conforming and a violating
fixture is not a checker. Confirm each mutation actually applied before trusting its result.

## 5. PROTECTED-PATH AUTHORIZATION — `protected-paths-v1.md` §5

**This task, T561, is the authorizing task** to **create exactly five new case directories** under
`tests/golden/open/`, one per command above, named `<command>-<short-slug>` (e.g.
`team-status-dag-colour-code`). Inside each, you may create `case.yaml`, `brief.md`, `expect.py` and
`fixture/**`.

**Not authorized:** any existing case, `tests/golden/held-out/` (do not open it), `scripts/scorecard.py`, and the
evaluator-hash baseline. You may not extend this grant; report and stop instead.

## 6. Scorecard and hash

- Adding cases changes the case count, so **regenerating the scorecard is required**: run
  `python3 scripts/scorecard.py` (write mode) once, after all five cases are committed, and **commit**
  `docs/benchmarks/scorecard-v6.12.0.{json,md}`. Confirm held-out rows stay redacted
  (`held-out-case-<n>` / `<redacted>`). Then `scorecard.py --check` must pass.
- **Exactly two evaluator-hash tests will go red. Do NOT refresh the baseline** or touch
  `docs/artifacts/evaluator-hash-known-good-v*.json` / `evaluator_hash.py`. Report both digests **post-commit**
  against **v12** (`tests_golden` `42264ed6…`); `scripts_scorecard` must be byte-identical to v12.
- Run `tests/functional/test_golden_held_out_isolation.py` and the audience lint.

## 7. Git and constraints

One commit per case, plus one for the scorecard. Commit locally; **do not push; never merge or approve
anything.** Write scope: the five new directories, `docs/benchmarks/scorecard-v6.12.0.{json,md}`, and this
brief's `**Status:**` line. Nothing else — **no command file**, even if a case exposes a defect in it.

## 8. Verification

`python3 tests/run.py` (exit code; redirect to a file, never pipe to `tail`) showing **exactly** the two
evaluator-hash failures (baseline 904 OK); every new case's `check()` result and its discrimination
demonstration; `scorecard.py --check`; `validate-tasks.py`; `check-maturity.py --root implementation` (it must
stay 79/0 — new red cases on `experimental` commands block nothing).

## 9. Blocker protocol

`technical` | `dependency` | `unclear_requirements` | `external`; `critical` | `major` | `minor`. **If anything in
this brief is wrong, report it rather than working around it.**
