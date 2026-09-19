# Terminal-Bench 2 — Frozen Iteration Subset (T418)

**Frozen:** 2026-08-13
**File:** `docs/benchmarks/tb-subset.json`
**Based on:** `docs/plans/plan-035-roadmap-v7-ground-up.md` §2.2.1, §2.4 Phase 1's "Registered
interpretation of the delta" block; `docs/tasks/task-T418.md`;
`docs/checkpoints/checkpoint-017-t417-harbor-oracle-smoke-complete.md`.

This document is the required prose rationale that accompanies `tb-subset.json` (JSON has no
comment syntax, so the narrative lives here). Read this before consuming or auditing the JSON
file — it explains *why* each task is or isn't in the subset without needing to re-derive the
reasoning.

## 1. How the full 89-task list was enumerated (and a note on the local cache)

T417's prior oracle runs (5-task smoke + 25-task extended run) left
`~/.cache/harbor/tasks/packages/terminal-bench/` populated with **30** task directories — the
union of the two runs' task selections, not the full dataset. T418's brief anticipated the full
89-task set would already be cached there; it was not (this is exactly the scenario the brief's
own Blocker Protocol names: "the local Harbor task cache is missing or incomplete"). Per the
brief's own sanctioned fallback ("via whatever `harbor` CLI listing command exists, if you
reinstall/reuse a venv per T417's brief"), a Harbor 0.21.0 venv was reinstalled (same method as
T417: `python3 -m venv` outside the repo worktree, `pip install harbor` inside it) and
`harbor dataset download terminal-bench/terminal-bench-2 --export -o <scratch-dir>` was run. This
performs shallow git sparse-checkouts of the 89 task packages' definition files
(`task.toml`, `README.md`, `instruction.md`, `environment/`, `tests/`, `solution/`) — it does
**not** build or run any Docker container, and no Docker command was invoked at any point in this
task. This produced an authoritative, network-fetched list of exactly 89 task directory names,
which is the source of every task name and `category` value in `tb-subset.json`.

Classified per the brief's Blocker Protocol: `type: technical`, `severity: minor` — cache was
incomplete (30/89), resolved without escalation using the brief's own pre-approved non-Docker
fallback. Not treated as a blocker requiring orchestrator intervention.

## 2. Category scheme

Rather than inventing a new taxonomy, this subset uses **Terminal-Bench's own `category` field**,
read verbatim from each task's `[metadata]` table in `task.toml` (e.g.
`crack-7z-hash`'s `task.toml` has `category = "security"`). This is more auditable than a
custom scheme because it does not depend on this task's judgment of what a task "is about" — it's
the dataset authors' own classification.

The full 89-task dataset spans **16 distinct categories**:

| Category | Tasks in full 89-task dataset | Tasks in this subset |
|---|---|---|
| software-engineering | 26 | 4 |
| system-administration | 9 | 2 |
| security | 8 | 2 |
| scientific-computing | 8 | 2 |
| data-science | 8 | 2 |
| file-operations | 5 | 2 |
| debugging | 5 | 2 |
| model-training | 4 | 1 |
| mathematics | 4 | 1 |
| data-processing | 4 | 1 |
| machine-learning | 3 | 1 |
| video-processing | 1 | 1 |
| personal-assistant | 1 | 1 |
| optimization | 1 | 1 |
| games | 1 | 1 |
| data-querying | 1 | 1 |
| **Total** | **89** | **25** |

## 3. Sampling rationale

- **Why ~25, not more/fewer:** matches plan-035 §2.2.1's own cost discipline ("Iterate on a fixed
  stratified subset (~25 tasks)... run the full suite only for release baselines"). At `k ≥ 3` per
  arm, 25 tasks × 2 arms × `k=3` = 150 task-runs per measurement — a workable size given T417's
  observed ~112s/task oracle runtime (≈4.7h wall-clock upper bound per measurement at that rate,
  before any economy-model/parallelism speedup from T41B). 89 tasks at the same `k` and arm count
  would be ~3.6x that cost for marginal stratification benefit once every category is already
  represented.
- **Why not strict proportional allocation:** a pure proportional split (26/89 × 25 ≈ 7.3 tasks
  for `software-engineering` alone) would let one category dominate nearly a third of the subset,
  which the brief explicitly warns against ("sample ~25 across groups so no single family
  dominates the subset"). Allocation used here is a capped/floor scheme instead: every one of the
  16 categories gets **at least 1** task (so every family present in the full dataset is
  represented, not just the four-category minimum the acceptance criteria require), and the two
  largest categories (`software-engineering`, all others ≥ 8 tasks) are capped at 2–4 rather than
  their proportional 3–7, so the largest single category (`software-engineering`, 4/25 = 16%) is
  well below its 29% share of the full dataset.
- **Within-category task choice:** where a category offered multiple candidates, preference was
  given to (a) tasks already exercised in T417's oracle runs (`docs/benchmarks/environment.md`),
  since their oracle-pass/fail behavior is already documented context for later interpretation
  (`caffe-cifar-10`, `crack-7z-hash`, `install-windows-3-11`, `rstan-to-pystan`, `dna-assembly`,
  `protein-assembly`, `db-wal-recovery`, `overfull-hbox`, `log-summary-date-ranges`,
  `feal-linear-cryptanalysis`, `video-processing` were all part of T417's 25-task run and are
  reused here deliberately, per the brief's explicit "you are not required to exclude or include
  these based on that alone, but note if you do either" — noted here: they are *included*, on the
  grounds that having a prior oracle data point for ~44% of the subset is useful cross-reference
  context for T41A, not a reason to avoid them), and (b) sub-theme diversity within a category
  (e.g. within `software-engineering`: an interpreter-construction task, a git-forensics task, a
  networked-service-build task, and a package-server task, rather than four near-duplicate build
  tasks).

## 4. `predicted_effect` tagging rationale

Per plan-035 §2.4 Phase 1's registered interpretation block (frozen at authoring time, quoted in
full in `tb-subset.json`'s `predicted_effect_definition` field): the projection is predicted to
move Terminal-Bench primarily on tasks requiring **multi-step planning before execution**, and to
be neutral on **single-command or lookup tasks**. This tagging is committed now, before any T41A
run exists, and — per the registered block's own terms — is not to be revisited after seeing
results.

Applying that test per task in this subset:

- **Tagged `positive` (16 of 25):** tasks where the agent must design an approach before acting —
  building a component from scratch (`make-mips-interpreter`, `kv-store-grpc`, `pypi-server`),
  multi-step forensic/recovery work (`git-leak-recovery`, `db-wal-recovery`,
  `custom-memory-heap-crash`), install/configuration sequences with multiple dependent steps
  (`install-windows-3-11`, `configure-git-webserver`), vulnerability
  identify-then-patch-then-verify work (`fix-code-vulnerability`), multi-stage scientific
  pipelines (`dna-assembly`, `protein-assembly`), an implemented cryptanalytic attack
  (`feal-linear-cryptanalysis`), a training pipeline requiring environment setup before the run
  (`caffe-cifar-10`), a multi-stage media pipeline (`video-processing`), and problems that are
  themselves planning/optimization problems (`constraints-scheduling`, `portfolio-optimization`).
- **Tagged `neutral` (9 of 25):** tasks judged closer to invoking one existing tool or performing a
  largely mechanical lookup/conversion — a single cracking-tool invocation
  (`crack-7z-hash`), a load-and-predict inference call (`hf-model-inference`), a mostly mechanical
  syntax translation rather than novel design (`rstan-to-pystan`), a format conversion
  (`gcode-to-text`), a narrow one-line-fix class of bug (`overfull-hbox`), running an existing
  training script without pipeline construction (`train-fasttext`), a data extraction/aggregation
  script (`log-summary-date-ranges`), invoking a chess-move-search tool/engine rather than
  designing one (`chess-best-move`), and writing a single (if intricate) query against a known
  schema (`sparql-university`).
- Several tagging calls are genuinely borderline and are recorded as such rather than silently
  resolved: `rstan-to-pystan`, `train-fasttext`, and `sparql-university` could reasonably be argued
  either way; they were placed on the `neutral` side specifically to avoid over-predicting
  `positive` (an initial draft pass tagged 19/25 positive, which was judged too skewed to give the
  eventual `predicted_effect: positive` cohort meaningful contrast against a `neutral` control
  group at T41A time — see plan-035's decision-rule step "Check the `predicted_effect: positive`
  tasks in isolation" — and was revised to the current 16/9 split before freezing).

## 5. What this file is not

Per plan-035 §2.4 Phase 1's "Consequences of a null delta, pre-committed": this subset is frozen
once committed. It will not be re-cut, re-stratified, or extended after T41A's first run for any
reason, including to search for a positive result. Any future change to the iteration subset must
be a new, dated successor artifact, not an edit of `tb-subset.json`.

## 6. Docker usage confirmation

No Docker container, image pull, or `docker` CLI command was run at any point while producing
`tb-subset.json` or this document. The only network operation performed was
`harbor dataset download ... --export`, a git sparse-checkout of task-definition files (metadata,
tests, instructions — not container images).
