# Golden Task Suite Format — v1

**Status:** Proposed (author-only; not yet independently reviewed — see blocker report)
**Based on:** `docs/plans/plan-035-roadmap-v7-ground-up.md` §2.4 Phase 1 (Layer 1, T410 row +
Phase 1 acceptance criteria), `docs/tasks/task-T410.md`, `docs/checkpoints/checkpoint-016-*.md`,
`docs/checkpoints/checkpoint-017-*.md`.
**Owner:** solution-architect
**Consumers:** T411 (qa-engineer, authors 20 cases), T412 (qa-engineer, `open/`/`held-out/`
split), T413 (devops-engineer, `scripts/scorecard.py`), T414 (release-manager, baseline
publication), T415 (evaluation-agent, failure taxonomy), T416 (tech-lead, freeze).

## 1. Why this exists (Gate G1)

`tests/performance/` (see `tests/performance/test_team_health.py`) checks that the *harness
scaffolding* is healthy: task lifecycle validity, plan coverage, checkpoint cadence, commit
hygiene. It does not check whether any of the five user-facing commands
(`/new-feature`, `/code-review`, `/plan`, `/security-audit`, `/prepare-release`) actually produce
correct output. Gate G1 requires an eval that can fail a real component on *outcome*, not just on
process health. `tests/golden/` is that eval. It does not replace or duplicate
`tests/performance/` — confirmed by reading both; no scope overlap found (dependency blocker not
triggered).

## 2. The central design decision: execution model

### 2.1 The tension

The plan states two hard constraints that pull in opposite directions:

1. `expect.py` returns **binary pass/fail**, **no LLM-judged scoring** (plan-035 §2.4 Phase 1,
   T410 row).
2. T413's acceptance criteria (same section) require: "Re-running on an unchanged tree produces
   an identical golden scorecard (**deterministic**)."

A case whose `expect.py` invokes a live agent/model completion in-process (e.g. actually running
`/new-feature` end-to-end against a live Claude Code session inside the test) is not
run-to-run deterministic (model sampling, latency, transient infra failures) and is too slow/costly
to run repeatedly at suite scale (target: 20+ cases, run on every scorecard invocation, run in CI).
A case that only asserts static, never-changing repo state tests nothing real and cannot fail a
real component.

### 2.2 Decision

**Each case's `expect.py` performs deterministic, scripted validation of a given end state. It
never itself invokes a live, sampling model completion.** A case is three things:

- `brief.md` — the task/prompt a user or agent would be given. This documents *intent* and is
  also the literal input a human or agent uses to *author* the case's fixtures (an offline,
  one-time step, not part of the automated/repeated run path). It may later be reused as the
  literal input to a live agent run in a *separate* system (e.g. if T411 or a future task wants to
  exercise a case against a live Claude Code session as an authoring aid, or Terminal-Bench-style
  capability measurement) — but the golden suite's own CI-safe, repeatable execution path
  (`scripts/scorecard.py`, T413) MUST NOT require a live model call to produce a result.
- `fixture/` — the starting repo/workspace state the case operates against, and/or (for cases
  that validate a fixed correct output rather than a scripted transformation) the pre-authored
  "what correct output looks like" end state itself.
- `expect.py` — a script that deterministically checks whether the *given* end state (either the
  fixture as checked in, or the fixture after a deterministic, scripted, non-LLM transformation
  performed by `expect.py` itself, e.g. regex/AST parsing, file-existence checks, structured-field
  extraction) satisfies the case's pass condition.

This makes the suite closer to **golden-file / property-based testing of each command's rails**
— declared preconditions, required output structure (file existence, required sections, required
fields in a VERDICT block, protected-path respect, artifact-versioning-convention compliance) —
than to **live capability benchmarking of raw model output**. Terminal-Bench (Layer 2, T417–T41C)
already covers raw agentic capability measurement at the terminal-task level; this suite's job is
to cover the 76-component harness's own rails and command surface, which Terminal-Bench cannot
see (it has no concept of `/prepare-release`'s RELEASE VERDICT block or `/plan`'s Task Creation
Precondition).

### 2.3 Why this resolves the tension, not just avoids it

- **Determinism**: satisfied by construction — `expect.py` is a pure function of `case_dir`'s
  on-disk content at call time (see §4.2 purity rules). Re-running `scripts/scorecard.py` on an
  unchanged tree calls the same `check()` functions against the same bytes and gets the same
  answer, always.
- **No LLM-judged scoring**: satisfied by construction — nothing in the automated run path asks a
  model to grade output. Pass/fail is determined by scripted parsing (string/regex/AST/structured
  field checks), which is binary.
- **Still tests something real**: a case is not "static state that never changes" — it validates
  the *actual* command surface's declared contract (e.g., does `/prepare-release`'s output contain
  a `## RELEASE VERDICT` block with a `Status:` field restricted to `PASS | CONDITIONAL_PASS |
  FAIL`? Does `/plan`'s output actually get written to `docs/plans/<slug>-plan.md`? Does
  `/security-audit`'s output include all 10 OWASP rows?). These are genuine, falsifiable
  assertions about harness behavior — a regression in a command's actual output shape or a
  broken/removed protected-path guard will flip a real case from pass to fail. That is a real
  component genuinely failing a real check, satisfying Gate G1's stated purpose ("an outcome eval
  that can fail it").

### 2.4 Audit of the five command surfaces (why one uniform contract suffices)

Read `implementation/knowledge/commands/new-feature.md`, `code-review.md`, `plan.md`,
`security-audit.md`, `prepare-release.md`. All five differ in what a *good* answer looks like
(subjective, not what this suite measures) but every one of them specifies a **structured,
parseable output contract**:

| Command | Structured contract this suite can check |
|---|---|
| `/plan` | Plan doc at `docs/plans/<slug>-plan.md` with required section headers (Goal, Task Decomposition, Dependency Graph, Resource Assignments, Risk Assessment, Open Questions); Task Creation Precondition (no task row added without a referencing plan file) |
| `/code-review` | `## VERDICT` block with `Status: PASS \| CONDITIONAL_PASS \| FAIL`, `Must Fix count`, `Should Fix count`, `Nice to Have count`, `Reviewer`, `Timestamp` fields |
| `/security-audit` | OWASP Top 10 coverage matrix (10 rows, `A01`–`A10`) + `## VERDICT` block with `CRITICAL/HIGH/MEDIUM/LOW findings` counts, `OWASP coverage: n/10` |
| `/prepare-release` | `## RELEASE VERDICT` block with `Version`, `Status`, feature/fix/breaking-change counts, `Quality gates passed/failed` lists |
| `/new-feature` | plan doc at `docs/plans/feature-<slug>.md`, a `[CHECKPOINT]` line with required fields, versioned artifacts under `docs/artifacts/` following `<name>-v<major>.<minor>.md` |

Every one of these is checkable by string/regex/file-existence parsing without judging prose
quality. **No per-family adapter layer is needed** — the outer contract (§4) is uniform across all
five; only the *content* of each case's `expect.py` body differs, which is expected and correct
(that's where case-specific knowledge belongs). This resolves the brief's first blocker-protocol
trigger condition in the negative: the five surfaces are not too heterogeneous for one contract.

## 3. Directory layout

```
tests/golden/
├── README.md                    # practitioner-facing contract (this doc's companion)
├── _example-scaffold/           # THIS task (T410) — proves the contract, not a real case,
│   │                             # not counted toward the suite, excluded from discovery
│   ├── brief.md
│   ├── case.yaml
│   ├── fixture/
│   └── expect.py
├── <case-id>/                   # T411 lands real cases directly here, flat, until T412
│   ├── brief.md
│   ├── case.yaml
│   ├── fixture/
│   └── expect.py
└── ...
```

**After T412** (not built by this task — reserved, see §3.1), the same per-case layout nests one
level deeper under two sibling directories:

```
tests/golden/
├── README.md
├── _example-scaffold/
├── open/
│   └── <case-id>/{brief.md, case.yaml, fixture/, expect.py}
└── held-out/
    └── <case-id>/{brief.md, case.yaml, fixture/, expect.py}
```

### 3.1 Reservation for T412 (open/ vs held-out/)

T412's job is to introduce the `open/` / `held-out/` split and enforce (via a CODEOWNERS-style
guard) that `held-out/` is never read from any improvement-task file outside itself. This format
spec reserves that split point as follows, so T412 requires **zero change to the per-case
contract**:

- **Case discovery is directory-shape-agnostic.** Any tool that discovers cases (T413's
  `scripts/scorecard.py`, this task's own scaffold test) MUST discover cases by recursively
  globbing for `expect.py` files under `tests/golden/`, treating each `expect.py`'s parent
  directory as `case_dir`, and MUST exclude any path component starting with `_` (this excludes
  `_example-scaffold/` and any future underscore-prefixed non-case directory, e.g. a future
  `_templates/`). Discovery MUST NOT assume a fixed nesting depth.
- Because of the rule above, T412 can move real cases from `tests/golden/<case-id>/` to
  `tests/golden/open/<case-id>/` and `tests/golden/held-out/<case-id>/` as a pure directory move —
  no `expect.py`, `case.yaml`, `brief.md`, or `fixture/` content changes, and no change to how
  `scripts/scorecard.py` invokes a case.
- `open/` vs `held-out/` is a **visibility/governance** distinction (who may read a case while
  doing improvement work), not a **contract** distinction. Every case, regardless of which side of
  the split it ends up on, satisfies the identical per-case contract in §4.

## 4. The `expect.py` contract

### 4.1 Canonical interface

```python
def check(case_dir: Path) -> bool:
    """Return True iff case_dir's current on-disk state satisfies this case's pass
    condition. `case_dir` is this case's own directory (the one containing this
    expect.py, brief.md, fixture/, case.yaml)."""
```

This is the **load-bearing** contract. `scripts/scorecard.py` (T413) loads every discovered
`expect.py` via `importlib.util.spec_from_file_location` (mirrors the existing pattern in
`tests/functional/test_check_version_consistency.py`'s `_load_module()`) and calls
`module.check(case_dir)` directly — no subprocess, no shelling out, uniform across every case
regardless of which command it targets.

A `python3 expect.py <case_dir>` CLI entry point (via `if __name__ == "__main__":`, exiting 0 for
`True` / 1 for `False`) is RECOMMENDED for local authoring/debugging convenience, but it is a thin
wrapper around `check()` — not an alternate contract. `scripts/scorecard.py` MUST NOT depend on
the CLI/exit-code path; the import-and-call path is the one and only contract T413 builds against.

### 4.2 Purity rules (required for §2.3's determinism claim to hold)

`check()` MUST:
- be a pure function of the bytes on disk under `case_dir` at call time — same input state, same
  output, every call, forever;
- make no network calls and invoke no live/sampling model completion;
- not depend on wall-clock time, environment variables, random seeds it doesn't itself fix, or
  process/OS state outside `case_dir`;
- not write outside `case_dir` (or a copy of it made by the caller for scratch use), and SHOULD
  avoid writing inside the checked-in `fixture/` at all — if a case needs to validate a scripted
  *transformation*, it should perform that transformation into a temp copy, not mutate the
  checked-in fixture in place (this keeps `git status` clean after every run).

### 4.3 `case.yaml` — per-case metadata

Every case directory contains a `case.yaml` alongside `brief.md`/`fixture/`/`expect.py`:

```yaml
id: <case-id>                     # must equal the directory name
command: /new-feature | /code-review | /plan | /security-audit | /prepare-release
status: expected_pass | known_failing
known_failing_category: tracked_defect | capability_gap   # required iff status == known_failing
known_failing_reason: <free text> # required iff status == known_failing
tags: [optional, free-form, strings]
```

### 4.4 Known-failing marking (for T411)

Three distinct situations this schema must be able to tell apart, per the brief:

1. **Expected to fail today, tracked** (a known bug that will get fixed) → `status:
   known_failing`, `known_failing_category: tracked_defect`, with `known_failing_reason`
   explaining what's broken and (ideally) a task/issue reference.
2. **Should pass, currently broken** (an accidental regression) → this is **not** a
   `known_failing` case at all. It is a case authored with `status: expected_pass` that starts
   returning `False`. `scripts/scorecard.py` (T413) is responsible for surfacing any
   `expected_pass` case that fails as a regression, distinct from the known-failing set — that
   distinction is exactly why `status` is a required, explicit field rather than inferred from the
   pass/fail result alone.
3. **Genuinely documents a capability gap** (a deliberate demonstration that the current command
   surface cannot yet do something, not expected to be fixed soon) → `status: known_failing`,
   `known_failing_category: capability_gap`, with `known_failing_reason` explaining the gap.

T411's "minimum 5 must be known-failing at authoring time" acceptance criterion is satisfied by
`status: known_failing` cases of either category; T413's scorecard MUST report `tracked_defect`
and `capability_gap` counts separately (not collapsed into one "known failures" number) so the
Phase 1 risk ("golden suite authored too easy") stays visible per-category, not just in aggregate.

## 5. Non-goals / residual limitations

- This format does not itself measure raw model capability — that's Terminal-Bench's job
  (Layer 2). A case with a strong `expect.py` can still be gamed by an agent that produces
  structurally-correct-but-substantively-wrong output; the two layers are complementary, not
  substitutes, exactly as plan-035 §2.2 states.
- `brief.md`'s use as a literal live-agent input (§2.2) is explicitly out of scope for this task
  and for the suite's automated run path; if a future task wants that, it is a separate,
  additional execution path layered on top of this format, not a replacement for it.
- This document does not build `scripts/scorecard.py`, the `open/`/`held-out/` split, or any of
  the 20 real cases — those are T413, T412, and T411 respectively. This spec is written so none of
  them requires a redesign of what's defined here.
