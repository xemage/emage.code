# plan-075 — the committed golden scorecard artifact: settling what it is

**Status: scoped 2026-09-26, awaiting approval to dispatch.**
Based on: `scripts/scorecard.py` (its own module docstring); `docs/tasks/task-T525.md`,
`docs/tasks/task-T531.md`, `docs/tasks/task-T521.md` (three independent reports of the same drift);
`docs/artifacts/golden-suite-format-v1.md`; `docs/artifacts/protected-paths-v1.md`.

## 0. Why this needs a task rather than another note

**Three separate implementers hit this and reported it; two of them reached opposite conclusions
about what the file is; and every one of them had to work around it.** That is the definition of a
defect that has outlived its grace period.

`docs/benchmarks/scorecard-v6.12.0.{json,md}` is committed at `total_cases: 20`, `total_pass: 11`,
while a fresh run of `scripts/scorecard.py` on the current tree produces **24 / 16 /
`tracked_defect: 4`**. Every invocation of the script rewrites both files, which means **"expect a
clean `git status`" is unreachable in any brief while this staleness exists** — and that instruction
has appeared in three briefs, all of which had to be worked around by the implementer reverting
`docs/benchmarks/` by hand.

## 1. The disagreement, and its resolution

- **`T525`'s implementer** read it as a **frozen `T414` baseline publication**, restored it, and
  noted that `T498`, `T520` and `T523` had all left it untouched. **The orchestrator agreed at the
  time.**
- **`T531`'s implementer** called it **badly stale**, and proved its own change had zero effect on
  content by regenerating in a throwaway worktree at the base commit and diffing — identical but for
  the timestamp.
- **`T521`'s implementer** independently reported the same drift with the same numbers.

**`T531` and `T521` are right. The orchestrator's agreement with `T525` was wrong.** Three facts
settle it, each checked directly:

1. **`scripts/scorecard.py`'s own docstring** states that `content` "is a pure function of the golden
   suite tree's on-disk bytes and is expected to be byte-identical across runs on an unchanged
   tree." A pure function of the tree is designed to **track** the tree, not to be frozen against it.
2. **Nothing validates the committed copy.** No test under `tests/functional/` or
   `tests/performance/`, and no `.gitlab-ci.yml` job, compares it to a fresh run. It can therefore
   rot silently — and did.
3. **It has exactly one commit**: `b16b382`, the original `T410`–`T415` landing. It has never been
   updated, across a suite that has grown from 20 cases to 24.

**Why the wrong reading was plausible, stated because the mistake is instructive:** one commit plus
three tasks declining to touch it *looks* like a freeze policy. But those three declined because
touching it was **outside their scope**, not because a policy existed. Absence of updates was
mistaken for a decision. A generated file that nothing checks and nobody owns produces exactly the
same evidence as a deliberately frozen one — which is why "who validates this?" is the question that
distinguishes them.

## 2. The decision T533 must make

Three coherent options. The task should choose one and say why, not hedge.

| Option | What it means | Cost |
|---|---|---|
| **A. Track it, and gate it** | Regenerate, commit, and add a CI drift check beside the existing generated-artifact gates | one new CI job; every golden-suite change must regenerate |
| **B. Regenerate once** | Bring it current, add no gate | free now, rots again immediately — this is the status quo's failure mode |
| **C. Untrack it** | `.gitignore` it as a build output | loses the published-baseline property `T414` wanted |

**Recommended: A.** This repo already treats its other generated artifacts exactly that way, and the
precedent is internal and strong: `implementation/registry/` is gated by `check.py --registry` and
the platform projections by `sync-no-diff`. Both exist precisely because a generated file that
nothing checks drifts. The scorecard is the same class of object, and its determinism is *explicitly
designed for* in the script's own docstring — the drift check is the thing that makes that design
claim load-bearing rather than decorative.

**B is the status quo and should be rejected on the record**, because it is what produced this. If
`T533` chooses B anyway, it must say what will catch the next drift.

## 3. Two traps for the implementer

1. **`run_metadata.generated_at` differs on every run by design.** A naive drift gate comparing whole
   files would fail on every pipeline. The gate must compare the **`content` key only** — which is
   exactly the boundary the script's docstring already draws. Getting this wrong produces a gate that
   is either permanently red or that has to be disabled, which is worse than no gate.
2. **`scripts/scorecard.py` is a protected path** (`protected-paths-v1.md`). If the chosen option
   needs the script changed — for example to add a `--check` mode — that requires a **named §5.2
   authorization**, which `T533`'s brief grants narrowly *only* for an additive check mode. Changing
   what the script *measures* is not authorized and is a blocker.

`docs/benchmarks/` itself is **not** protected, so regenerating the artifacts needs no authorization.

## 4. Held-out redaction — do not regress it

`scorecard.py` deliberately redacts held-out case identities from its output artifacts: they live
outside `tests/golden/`, so `test_golden_held_out_isolation.py` Check B applies to them, and
descriptive case IDs would reveal what a held-out case tests. The output carries held-out
**aggregate** health, never held-out **case identity**.

A regenerated artifact must preserve that. **The isolation test is the gate and must pass** — if a
regeneration leaks an ID, that is a critical blocker, not a detail.

## 5. Scope boundary

`T533` does **not** change any golden case, any case's status, or any component's `maturity:`. The
suite's measured outcome is 24 / 16 either way; this task makes the committed record say so. **It
promotes nothing**, and if the numbers move as a result of it, something has gone wrong.
