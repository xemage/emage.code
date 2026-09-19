# `docs/benchmarks/failures/` — failure classification index (golden suite + Terminal-Bench)

Scheme definition (axis meanings, why they're distinct, full case-by-case table): see
`docs/artifacts/failure-taxonomy-v1.md` (T415 §1–7; T409 extension §8). This directory holds one
auditable classification file per source:

- **Golden suite** (this directory, flat files, T415): one file per `known_failing` golden case —
  which case, which `cause`/`behavior`/`mechanism` axis value, and why — mirroring the golden
  suite's own per-case-directory convention (`docs/artifacts/golden-suite-format-v1.md` §3).
- **Terminal-Bench / Harbor trajectories** (`terminal-bench/` subdirectory, T409): one file per
  distinct *failure pattern* (not per-trial —~150+ failing trials across 4 Harbor runs would make
  per-trial files noise), each citing real task names, real trial hashes, and which run/pass they
  came from.

Both sources are classified along the **same three axes**, defined once in
`docs/artifacts/failure-taxonomy-v1.md` §3 — this is the concrete "one taxonomy, two sources"
result plan-035 §2.4's Gate G1 acceptance bullet requires. See §"Combined proof" below.

**Scope — golden suite:** only the `known_failing` bucket (9 cases, per
`docs/benchmarks/scorecard-v6.12.0.json`'s `content.summary.known_failing: 9`, re-verified at
authoring time). `regression` and `unexpected_pass` cases are out of scope — see
`failure-taxonomy-v1.md` §6.

**Held-out cases (golden suite only):** 3 of the 9 are held-out; per the isolation discipline
carried forward from T412/T413/T414, their files use a redacted identity (`held-out-case-<n>`,
same numbering as `docs/benchmarks/scorecard-v6.12.0.json`) and never name their real case ID,
path, or fixture content. See `failure-taxonomy-v1.md` §5. Terminal-Bench trajectories have no
held-out concept — `tests/functional/test_golden_held_out_isolation.py` does not apply to them
(confirmed unaffected by this task; see `docs/artifacts/failure-taxonomy-v1.md` §8, and this
task's own completion report).

**Scope — Terminal-Bench:** only genuine task-level failures (`exception_info: null`,
`verifier_result.rewards.reward == 0.0`) from T407's two Harbor measurement sources (local k=3 run
and remote Design A's 3 successful passes). **Infrastructure/harness failures are explicitly
excluded**, not silently dropped — see "Infrastructure-failure exclusion" below.

## Infrastructure-failure exclusion (Terminal-Bench)

Harbor trials whose `result.json` has a non-`null` `exception_info` (predominantly
`AgentTimeoutError` — the agent's own execution exceeded its time budget before the verifier
could run) are **not** classified under this scheme: they are harness/infra failures, not
task-outcome failures, and the `cause × behavior × mechanism` scheme was built to classify the
latter. Counts:

- Local k=3 run (`tb-delta-20260814T111217Z`, both arms): 38 of 150 trials excluded.
- Remote Design A passes (3 runs × 2 arms): 19 of 150 trials excluded.
- The two fully-failed Design A attempts (100% `RewardFileNotFoundError`/`AgentTimeoutError`, per
  `docs/tasks/task-T407.md`'s closing note) are excluded in their entirety — every trial in those
  attempts is an infra failure by construction and contributes no genuine task-level data.

Full detail: `docs/artifacts/failure-taxonomy-v1.md` §8.3.

## Golden-suite index

| File | Case | Location | `known_failing_category` | `cause` | `behavior` | `mechanism` |
|---|---|---|---|---|---|---|
| `code-review-conditional-pass-conditions-gap.md` | `code-review-conditional-pass-conditions-gap` | open | capability_gap | undefined-structured-convention | required-section-absent | field-level-absence-within-declared-block |
| `new-feature-real-checkpoint-format-drift.md` | `new-feature-real-checkpoint-format-drift` | open | tracked_defect | established-practice-drift | required-marker-line-absent | whole-block-absence |
| `plan-real-doc-header-drift.md` | `plan-real-doc-header-drift` | open | tracked_defect | established-practice-drift | naming-or-format-drift | naming-convention-drift |
| `prepare-release-conditional-pass-conditions-gap.md` | `prepare-release-conditional-pass-conditions-gap` | open | capability_gap | undefined-structured-convention | required-section-absent | field-level-absence-within-declared-block |
| `prepare-release-real-verdict-missing.md` | `prepare-release-real-verdict-missing` | open | tracked_defect | established-practice-drift | required-section-absent | whole-block-absence |
| `security-audit-critical-not-fail.md` | `security-audit-critical-not-fail` | open | tracked_defect | rule-violation-no-exception-clause | value-violates-invariant | cross-field-invariant-violation |
| `held-out-case-1.md` | `held-out-case-1` (redacted) | held-out | tracked_defect | established-practice-drift | naming-or-format-drift | naming-convention-drift |
| `held-out-case-3.md` | `held-out-case-3` (redacted) | held-out | tracked_defect | established-practice-drift | naming-or-format-drift | naming-convention-drift |
| `held-out-case-4.md` | `held-out-case-4` (redacted) | held-out | capability_gap | undefined-structured-convention | required-section-absent | whole-block-absence |

9 files, 9 cases — matches `docs/benchmarks/scorecard-v6.12.0.json`'s `known_failing: 9`.

## Terminal-Bench index (`terminal-bench/` subdirectory, T409)

Sources: T407's local k=3 run (`tb-delta-20260814T111217Z`) and remote Design A's 3 successful
passes (`tb-delta-{20260907T162617Z,20260907T203448Z,20260908T001726Z}`, read via read-only SSH
from `10.10.160.11`, not copied into this repo — see `docs/tasks/task-T407.md`). 157 genuine
task-level failures across **21** task names, grouped into **6** distinct failure patterns. Full
extraction method, exact counts, and infra-exclusion accounting: `docs/artifacts/failure-taxonomy-v1.md`
§8 (corrected 2026-09-08, §8.6 — the original pass's "17 task names / 5 patterns" undercounted by
using only the local source's distinct-task-name count instead of the true local∪remote union).

| File | `cause` | `behavior` | `mechanism` | Reused from golden suite? | Real task names |
|---|---|---|---|---|---|
| `terminal-bench/incorrect-computed-output-value.md` | `agent-incorrect-domain-computation` | `incorrect-computed-output-value` | `wrong-value-vs-ground-truth` | No — all 3 new | `chess-best-move`, `gcode-to-text`, `log-summary-date-ranges`, `video-processing`, `db-wal-recovery`, `sparql-university`, `rstan-to-pystan`†, `train-fasttext`† (1 of 4 trials) |
| `terminal-bench/invariant-violation-in-generated-artifact.md` | `agent-incorrect-domain-computation` | `value-violates-invariant` | `cross-field-invariant-violation` | `behavior`+`mechanism` reused unmodified (also used by golden case `security-audit-critical-not-fail`) | `protein-assembly`, `dna-assembly`, `overfull-hbox` |
| `terminal-bench/required-output-artifact-absent.md` | `agent-incomplete-task-execution` | `required-section-absent` | `whole-block-absence` | `behavior`+`mechanism` reused unmodified (also used by golden cases `prepare-release-real-verdict-missing`, `new-feature-real-checkpoint-format-drift`, `held-out-case-4`) | `crack-7z-hash`, `feal-linear-cryptanalysis`, `make-mips-interpreter`, `train-fasttext`† (3 of 4 trials) |
| `terminal-bench/runtime-service-not-functional.md` | `agent-incomplete-task-execution` | `runtime-service-not-functional` | `live-system-unreachable-or-erroring` | No — all 3 new | `configure-git-webserver`, `kv-store-grpc`, `install-windows-3-11`, `pypi-server`, `hf-model-inference` |
| `terminal-bench/produced-code-fails-to-build.md` | `agent-incomplete-task-execution` | `produced-code-fails-to-build` | `build-toolchain-error` | No — all 3 new | `custom-memory-heap-crash` (remote source only) |
| `terminal-bench/verifier-crashes-on-missing-dependency.md` † | `agent-incomplete-task-execution` | `verifier-subprocess-crashes-fatally` | `fatal-signal-on-missing-input-artifact` | `cause` reused, `behavior`+`mechanism` new | `caffe-cifar-10`† (remote source only) |

† = added in the 2026-09-08 fix pass — see `docs/artifacts/failure-taxonomy-v1.md` §8.6.

6 files, 6 distinct failure patterns, 21 distinct real task names, 71 real trial hashes cited
across the files (representative of 157 total genuine failures — see each file's own trial table
and `docs/artifacts/failure-taxonomy-v1.md` §8.4 for the full-vs-cited accounting).

## Combined proof: "one taxonomy, two sources"

At least one Terminal-Bench failure pattern reuses **each** of the golden suite's non-`required-
marker-line-absent`/`naming-*` `behavior`/`mechanism` values completely unmodified
(`value-violates-invariant`/`cross-field-invariant-violation` and `required-section-absent`/
`whole-block-absence`), demonstrating the same axis value, assigned independently to a golden-suite
case and a Harbor trajectory, describing the same observable failure shape. Where no existing value
fit without forcing a bad fit, new values were added to the *same* three-axis structure — no fourth
axis was introduced (per `docs/artifacts/failure-taxonomy-v1.md` §7's resolved hypothesis and §8).
Both index tables in this README share the same `cause`/`behavior`/`mechanism` column vocabulary,
defined once in `docs/artifacts/failure-taxonomy-v1.md` §3 (as extended by §8) — this is the
concrete artifact that closes Phase 1 Gate G1's "Terminal-Bench and golden failures appear in one
taxonomy" acceptance bullet.
