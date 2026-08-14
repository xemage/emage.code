# Protected Paths — v1

**Based on:** `docs/plans/plan-035-roadmap-v7-ground-up.md` §2.4 Phase 1, Layer 1 table, T416
row, and §2's risk table entry: *"Held-out set leaks into improvement work | Medium | Critical |
T412 path guard + T463 evaluator-hash check + T416 write-scope exclusion. Three independent
controls."*

**Refs:** T416. Closes plan-035's Layer 1 (T410–T416).

## 1. What this document declares

Two paths in this repository are **protected**, effective from T416's merge onward:

- `tests/golden/**`
- `scripts/scorecard.py`

"Protected" means: **no agent definition may edit these paths as part of normal improvement-task
work, full stop.** These are the golden-suite evaluator's own interface and held-out data — the
thing improvement work is *graded against*, not a thing improvement work may itself change to make
its own results look better. This is the same reasoning that motivated the `open`/`held-out` split
and the isolation guard built at T412 (`tests/functional/test_golden_held_out_isolation.py`);
T416 extends that discipline from "don't leak held-out content" to "don't edit the evaluator
itself."

## 2. Why three controls, not one

Per plan-035's risk table, "held-out set leaks into improvement work" is rated Medium likelihood /
Critical impact, and the plan deliberately assigns it **three independent controls** rather than
relying on any single one:

1. **T412's path guard** (`tests/functional/test_golden_held_out_isolation.py`) — catches
   functional access to `tests/golden/held-out/` and bare mentions of real held-out case IDs
   anywhere outside `tests/golden/`, already merged and enforced.
2. **T463's evaluator-hash check** (not yet built, a later task, out of scope here) — will detect
   if the evaluator's on-disk content silently drifts from a known-good hash, a tamper-evidence
   control independent of whether the drift was intentional or accidental.
3. **T416 — this document, its per-agent pointers, and its static guard** — the write-scope
   exclusion: agent instructions declare these paths out of bounds, and a repo-wide test proves
   the declaration is present and consistent across every agent definition.

Each control catches a different failure mode. This document only implements control 3. It does
not by itself prevent a determined or malfunctioning agent from writing to `tests/golden/expect.py`
— see §4 ("What this does *not* do") below.

## 3. Standing exception: orchestrator read/audit access

Freezing **write** scope does not freeze **read** scope for the orchestrator. The orchestrator
retains standing read access to `tests/golden/**` and `scripts/scorecard.py` for audit and
verification purposes — this is not a loophole, it is a distinct and still-needed capability that
has already been exercised repeatedly during Phase 1 Layer 1:

- T412's adversarial probes (deliberately reproducing violations to prove the guard catches them
  before restoring the clean state)
- T413/T414/T415's grep-based verification of scorecard and taxonomy output against real held-out
  case IDs
- The cross-task narrative-leak audit performed ahead of this task (see
  `docs/checkpoints/checkpoint-018-phase1-layer1-golden-suite-complete.md`, "Audit detail")

Read/audit access is orthogonal to write-scope exclusion: an agent (including the orchestrator)
may read these paths to verify, evaluate, or reproduce a guard result. What is prohibited is
**editing** them as part of normal improvement-task work.

## 4. What this does *not* do (scope boundary)

This is a **declarative + auditable** control, not a git-level enforcement mechanism:

- There is no commit-time or diff-time hook that blocks a literal edit to `tests/golden/expect.py`
  or `scripts/scorecard.py`. Building one would require distinguishing "which agent role authored
  this diff" at the git level, which this environment has no mechanism for, and is out of scope
  for T416 (a "small" task per plan-035).
- The trust model mirrors this repo's other conventions that rely on written policy plus review
  discipline rather than a bot — most directly, `.claude/rules/git-workflow.md`'s "Protected
  Branches" section, which documents that `main`/`develop` are protected *on the remote* (GitLab
  branch protection is the actual enforcement there) but the branching/worktree/MR discipline
  around them is convention-plus-review, not automated for every rule in that document (e.g. the
  "no `--amend` after push" rule has no bot enforcing it either).
- Concretely here: enforcement is (a) every agent definition's own instructions telling it not to
  touch these paths, (b) a static guard (`tests/functional/test_protected_paths_declared.py`)
  proving that instruction is present in every agent definition and that the two protected paths
  still exist on disk, and (c) ordinary code review (Tech Lead / orchestrator) catching any
  violation that instruction-following alone didn't prevent, the same way any other architecture
  or convention violation would be caught in this repo.

## 5. Exception path for genuine future maintenance

Freezing these paths must not make a genuine future need — a real bug found in an `expect.py`, or
a legitimately new golden case — impossible to address. The exception path is:

1. **Never a silent edit.** No agent executing unrelated improvement-task work may edit
   `tests/golden/**` or `scripts/scorecard.py` as an incidental part of that work, regardless of
   how minor the change appears.
2. **Always a named, authorized task.** Any change to these paths requires an explicit task brief
   (`docs/tasks/task-<NNN>.md`) that names this exception explicitly — i.e. the brief must state
   that it is authorized to modify a protected path and cite this document (`protected-paths-v1.md`)
   as the reason that authorization is required. The brief is authored by the orchestrator (or, per
   this repo's protocol, explicitly requested by the user) — not invented unilaterally by a
   dispatched agent mid-task.
3. **Ordinary review still applies.** Once authorized, the change goes through the same
   branch/worktree/MR/Tech-Lead-review flow as any other change in this repo
   (`.claude/rules/git-workflow.md`) — the exception authorizes *that a change to a protected path
   may be proposed*, it does not bypass review.

A future orchestrator picking up such a need has a concrete process to follow here, rather than
having to invent one under time pressure.

## 6. Verification

- `tests/functional/test_protected_paths_declared.py` confirms every one of the 27
  `implementation/knowledge/agents/*.md` source files contains the protected-paths pointer, and
  that both protected paths exist on disk (`tests/golden/` as a directory, `scripts/scorecard.py`
  as a file) — see that file for the synthetic-fixture and real-tree test coverage.
- `implementation/scripts/sync.mjs` regenerates every platform's agent projection from the 27
  source files; the pointer therefore appears in every platform projection folder
  (`.claude/agents/`, `.cursor/`, `.gemini/`, `.opencode/`, `.pi/`, `.github/`, `.cline/`) without
  hand-editing any of them.
