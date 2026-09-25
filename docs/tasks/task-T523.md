# T523 — Execute ADR-007 verdict H-1: align the held-out checker with the amended contract

**ID:** T523
**Owner:** Backend Developer
**Status:** in_review
**Priority:** P2
**Tier:** mechanical
**Affects:** command/new-feature
**Depends on:** T520 (merged 2026-09-25)
**Created:** 2026-09-25
**Based on:** `docs/decisions/ADR-007-command-contract-authority.md` branch 1;
`docs/artifacts/command-contract-resolution-v1.md` §H-1;
`docs/artifacts/command-promotion-readiness-v1.md` §4;
`docs/artifacts/protected-paths-v1.md` §5;
`docs/plans/plan-071-t523-adr-007-h1-completion.md`.

## 1. PROTECTED-PATH AUTHORIZATION — read first

**This task is explicitly authorized to modify protected paths under `tests/golden/held-out/`, and
cites `docs/artifacts/protected-paths-v1.md` §5;
`docs/plans/plan-071-t523-adr-007-h1-completion.md`.2 as the reason that authorization is required.**

The authorization is **file-scoped**. It covers exactly these files, in exactly one case directory,
and nothing else:

| File | Permitted change |
|---|---|
| `<case>/expect.py` | the version-pattern regex **only**, plus its docstring sentence |
| `<case>/case.yaml` | `status` flip and removal of the two now-obsolete `known_failing_*` keys |
| `<case>/brief.md` | the sentence stating the expected outcome, **only if** it states the old one |

`scripts/scorecard.py` is **not** authorized and must not be touched. No file under
`tests/golden/open/` is authorized. No other held-out case is authorized. **The fixture is not
authorized and must not change** — see §4.

`protected-paths-v1.md` §5.1 forbids you from extending this grant yourself. If you conclude that
more is needed, **stop and report a blocker**. Do not widen the table. `T520` hit exactly this
situation on this exact file and correctly refused; that refusal is why this task exists.

## 2. Identifying the case — without writing its ID anywhere

`tests/functional/test_golden_held_out_isolation.py` **Check B** fails the build if any file outside
`tests/golden/` mentions a held-out case ID as a whole token. That includes this brief, your commit
message, your MR description, and the ledger.

So the case is specified mechanically rather than by name. It is the **unique** directory under
`tests/golden/held-out/` satisfying:

```
grep -rln 'v\\d+\\.\\d+\\.md' tests/golden/held-out/*/expect.py
```

Confirm it returns exactly one path before proceeding. Refer to it in all committed prose as
"the H-1 case" or "the held-out `ADR-007` H-1 case". **Never write its directory name.** After your
change, re-run:

```
python3 -m pytest tests/functional/test_golden_held_out_isolation.py -q
```

That test is the real gate on this constraint — it is not advisory.

## 3. The change

`T520` already amended the command's declared artifact-filename format to the single-integer form,
citing `AGENTS.md` § Artifact Versioning, under `ADR-007` **branch 1** (authority conflict → amend
the contract, because the command contradicted a higher-authority document). That half is merged and
is **not** yours to revisit.

What remains is that the case's `expect.py` still compiles the **pre-amendment** two-part pattern, so
the case cannot pass whatever the command now says. Align it:

- `expect.py`: the compiled version-pattern regex loses its second `\d+` group and the `\.` that
  separates them, so it matches the single-integer form the amended contract declares.
- `expect.py`: the docstring currently says the case is "Expected to return False today". It is no
  longer. Update that sentence and drop the `known_failing` framing.
- `case.yaml`: `status: known_failing` → `status: expected_pass`; delete `known_failing_category`
  and `known_failing_reason`, which describe a defect that no longer exists.
- `brief.md`: update only if it states the old expected outcome. Read it first.

## 4. Do not touch the fixture — this is the trap

The fixture holds two real artifacts copied verbatim from this repo's own `docs/artifacts/`. They
already use the form the amended contract declares. **The fixture is correct and always was** — the
`known_failing_reason` itself records that zero of 43 real artifacts used the two-part form.

Renaming a fixture file to satisfy the checker would invert the case: it would make the suite assert
the form `AGENTS.md` does **not** declare, and `T520` would have to be reverted. Verified before
this brief was written: with the regex aligned and the fixture untouched, both fixture filenames
match and `check()` returns `True`.

`ADR-007` §5 — *never resolve by relaxing a check* — also applies. You are not relaxing the check;
you are pointing it at the contract that is now in force. If you find yourself making the regex
*more* permissive than the amended contract (for example, accepting both forms), that is relaxation
and it is out of scope. Report it as a blocker instead.

## 5. Acceptance criteria

1. `check()` returns `True` for the H-1 case against its **unmodified** fixture.
2. `git status --porcelain` shows changes confined to the §1 table plus `docs/tasks/`. **No fixture
   file appears**, renamed or otherwise.
3. `python3 -m pytest tests/functional/test_golden_held_out_isolation.py -q` passes.
4. `python3 -m pytest tests/functional -q` — no new failures against the pre-change baseline
   (**734 passed, 23 skipped** on `be053dc`).
5. `python3 implementation/scripts/check-maturity.py --root implementation` → `79 components
   checked, 0 failing`. The distribution is unchanged: this task **does not promote anything**.
6. `python3 docs/tasks/validate-tasks.py` → `PASS`.
7. No held-out case ID appears in any file you touch outside `tests/golden/`, including the commit
   message.

## 6. What this task must NOT do

- **Do not promote `command/new-feature`.** Once this merges and the `T523` row archives, that
  component becomes measurably promotable. Promotion is a separate component-state change and gets
  its own task, per `T514`'s and `T522`'s precedent. This row is `P2` and declares
  `**Affects:** command/new-feature`, so that component stays blocked by criterion 3 until it
  archives anyway — the same sequencing `T515`/`T516` and `T520`/`T522` used.
- **Do not touch verdicts A, C or H-2.** A and H-2 are `ADR-007` branch-3b outcomes that stay red
  until the corpus is fixed; C belongs to `T521`.
- **Do not edit `scripts/scorecard.py`** or any `tests/golden/open/` case.

## 7. Blocker protocol

Report blockers with type (`technical` | `dependency` | `unclear_requirements` | `external`) and
severity (`critical` | `major` | `minor`). Max 2 retries, then escalate. Do not silently fail, and do
not widen the §1 authorization table under any circumstances — report instead.
