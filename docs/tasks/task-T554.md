# T554 — `/discover-skills` step 1 loads a registry installed targets never receive

**ID:** T554
**Owner:** QA Engineer
**Status:** done
**Priority:** P2
**Tier:** judgment
**Affects:** —
**Depends on:** T539, T547
**Created:** 2026-09-30
**Based on:** `docs/plans/plan-083-four-decisions-and-batching.md` §1 and §4 (P2, P3 — triggers fired);
`docs/artifacts/command-audience-resolution-v1.md` §6.2; `docs/plans/plan-084-round-close-and-fired-triggers.md` §3.

## 1. Why this exists, and why it is not demotion

`/discover-skills` is `stable`. Step 1 says *"load `implementation/registry/index.json`"* and
`## Rails` **Inputs** names the registry again. `install.sh` never installs `implementation/registry/`,
so in every installed target step 1 cannot be performed.

`plan-083` §1 decided **not** to demote it, on the condition that the repair is dispatched within two
rounds of its trigger firing. The trigger ("golden batch merged and its baseline authorized") fired on
2026-09-30. **This task is that repair.** If it stalls, `plan-083` §1 says demote.

`**Affects:** —` is deliberate. Naming `command/discover-skills` at P0/P1 would make `check.py
--maturity` exit 1 and block every merge (`plan-081` §1); at P2 it would be inert anyway.

## 2. The decided repair — T546 §6.2, read it in full

**Repair the command; do not install the registry.** An installed registry would index 79 components,
none of which exists at its stated path (every `path` is relative to `sourceRoot:
implementation/knowledge`, which targets do not have).

Step 1's purpose is to enumerate the available skills. What exists in **both** audiences and
enumerates them is the **skills tree**: `implementation/knowledge/skills/*/SKILL.md` in the authoring
repository, `.<platform>/skills/*/SKILL.md` in a target. So step 1 becomes a **two-row rule** on the
discriminator "`implementation/registry/index.json` exists", with the registry kept as an **optional
accelerator** where present. Fix `## Rails` **Inputs** in the same edit. Examine step 6's
`packs/installed/`, which T546 could not verify, and report what it is.

## 3. The golden coupling — this is why a QA Engineer owns it

The case `tests/golden/open/discover-skills-registry-grounded-recommendation` has, as its **load-bearing
assertion, step 1 itself**: every skill the output names must resolve to a real `category: skill` entry
in `fixture/implementation/registry/index.json`. Amending step 1 therefore **necessarily** supersedes
what its checker asserts — the T527/T531 and T535/T541 class. Re-derive the checker to the amended
two-row contract **in the same MR as the command change**, so the two never disagree in `develop`.

Say which row the fixture exercises. If you add a target-row fixture (a `.<platform>/skills/` tree),
that is inside the grant below. **ADR-007 §5 forbids resolving this by relaxing the check**: skills
must still resolve against a real enumeration, and the strength of the "no invented skill" assertion
must not drop.

## 4. PROTECTED-PATH AUTHORIZATION — `protected-paths-v1.md` §5

**This task, T554, is the authorizing task** for exactly:

- `tests/golden/open/discover-skills-registry-grounded-recommendation/expect.py`
- `tests/golden/open/discover-skills-registry-grounded-recommendation/brief.md`
- `tests/golden/open/discover-skills-registry-grounded-recommendation/fixture/**` (add, change, remove)
- `tests/golden/open/new-project-plan-doc-and-lifecycle-states/brief.md` — **brief.md only** (§5 below)

**Not authorized:** any `case.yaml`, any other case, anything under `tests/golden/held-out/`,
`scripts/scorecard.py`, and the evaluator-hash baseline. You may not extend this grant yourself; report
and stop if you need more.

## 5. Folded in — `plan-083` P3 (trigger "T547 merged" has fired)

`new-project-plan-doc-and-lifecycle-states/brief.md` quotes `/new-project` step 1 verbatim, including
the line T547 changed (`Reference protocol: 04-protocols.md § Plan-Approve-Execute`). Correct the quote
against `/new-project` as it is in `develop`. That case's `expect.py` and `fixture/` are not in the
grant, and its `check()` must still return **True** — run it and report. Folding it here costs one
baseline authorization instead of two.

## 6. Other constraints

- **Knowledge edit.** You also edit `implementation/knowledge/commands/discover-skills.md`. Then run
  **both** generators (`node implementation/scripts/sync.mjs --root implementation`,
  `python3 implementation/scripts/generate-registry.py`) and **declare the affected repo-root paths** in
  `tests/_baselines/root-install-drift.json` from `python3 -m tests.functional.test_root_install_parity
  --print-drift`, preserving its `_comment`. Expect only `discover-skills` paths to appear.
- **The scorecard:** if any case outcome moves, run `python3 scripts/scorecard.py` (write mode) and
  commit `docs/benchmarks/`; if the regeneration is timestamp-only, revert it.
- **The hash:** exactly two evaluator-hash tests will go red. **Do not refresh the baseline.** Compute
  both digests post-commit and report them against **v10** (`evaluator-hash-known-good-v10.json`);
  `scripts_scorecard` must be byte-identical to v10.
- No held-out case ID in any committed file outside `tests/golden/`; run the isolation test.
- Commit locally; **do not push; never merge or approve anything.**

## 7. Verification

`python3 tests/run.py` (exit code, redirected to a file; exactly the two hash failures), every
`check()` you touched with its observed result, the held-out isolation and scorecard no-drift tests,
`validate-tasks.py`, `check-maturity.py` (`/discover-skills` must keep its `stable` claim),
`check.py --maturity --schemas --registry`, `sync.mjs --check`, `generate-registry.py --check`.

## 8. Blocker protocol

`technical` | `dependency` | `unclear_requirements` | `external`; `critical` | `major` | `minor`.
**If anything in this brief is wrong, report it rather than working around it.** Sixteen consecutive
tasks have found a brief defect.
