# Failure pattern: `incorrect-computed-output-value` (Terminal-Bench)

**Scheme:** `docs/artifacts/failure-taxonomy-v1.md` §8 (T409 extension)
**Source:** Harbor/Terminal-Bench trajectories, not `tests/golden/**` — see
`docs/benchmarks/failures/README.md` for the source-provenance note.
**Task type:** genuine task-level failure (`exception_info: null`,
`verifier_result.rewards.reward == 0.0`) — infrastructure/harness failures are excluded from this
scheme; see `docs/benchmarks/failures/README.md` §"Infrastructure-failure exclusion".

## Axis classification

| Axis | Value | Status |
|---|---|---|
| `cause` | `agent-incorrect-domain-computation` | **new** (added to §3.1 of `failure-taxonomy-v1.md`) |
| `behavior` | `incorrect-computed-output-value` | **new** (added to §3.2) |
| `mechanism` | `wrong-value-vs-ground-truth` | **new** (added to §3.3) |

## Why this is a distinct pattern, not a forced reuse

Every case below produces a **fully-formed, correctly-shaped, well-formatted required output
artifact** — the right file exists, at the right path, with the right structure/fields — but one
or more of the *values inside it* is simply factually wrong when compared against an independently
computed ground-truth answer. This is different in kind from:

- `required-section-absent` / `whole-block-absence` (existing golden-suite values, reused
  elsewhere in this extension for §"required-output-artifact-absent.md") — those cases have
  **no** output at all; these cases have a complete, well-formed output that is simply *incorrect*.
- `value-violates-invariant` / `cross-field-invariant-violation` (existing golden-suite values,
  reused elsewhere in this extension for §"invariant-violation-in-generated-artifact.md") — those
  cases fail an *internally declared cross-field rule* (values contradict each other or an
  explicit constraint stated in the task); these cases pass every internal
  well-formedness/consistency check and fail purely because the verifier compares the produced
  value(s) to an externally known correct answer and finds a mismatch.

None of the three existing `cause` values fit either: all three (`undefined-structured-convention`,
`established-practice-drift`, `rule-violation-no-exception-clause`) describe *document-contract
authoring* mismatches (a spec says X, the artifact does something else structurally). Here the
agent understood the contract and the required output shape perfectly — it attempted the
underlying technical/domain task (chess analysis, image-frame timing detection, log arithmetic,
G-code decoding, database WAL decryption, SPARQL querying) and got the substantive answer wrong.
That is a new, genuinely distinct root cause: `agent-incorrect-domain-computation`.

## Real cases (local k=3 run, `tb-delta-20260814T111217Z`, unless noted)

| Task | Trial (arm/hash) | What the verifier expected vs. got |
|---|---|---|
| `chess-best-move` | arm-A `76RBoFA`, arm-A `DRP5pCV`, arm-A `RF6AbwS`, arm-B `3tsiFVa`, arm-B `qPkQtpn`, arm-B `v7o3QHX` | `move.txt` required to contain `{g2g4, e2e4}` (both checkmate-in-one moves); agent wrote `c3e4` — a plausible-looking but non-mating move. |
| `gcode-to-text` | arm-A `2Jzm98H`, arm-A `ZGo9F5g`, arm-A `s4Pc3ZU`, arm-B `ByBsQmK`, arm-B `ZNCemD7` | `out.txt` required to equal `flag{gc0d3_iz_ch4LLenGiNg}`; agent wrote `Embossed text` — the file exists and is well-formed, the decoded content is wrong. |
| `log-summary-date-ranges` | arm-A `PB6eRAz`, arm-B `SXHBCp3` | Output CSV has the correct header and row count (structurally valid), but a specific `(period, severity)` count cell is wrong — expected `370`, agent computed `414`. |
| `video-processing` | arm-A `3BhXVEi`, arm-A `DRyzdmw`, arm-B `6TxyWTx`, arm-B `6qXZLvu`, arm-B `NafWWmZ` | `output.toml` has the required fields (`jump_takeoff_frame_number`, `jump_land_frame_number`), but the computed frame number (`29`) falls far outside the expected inclusive range (`[219, 223]`) — a wrong computed value, not a missing/malformed field. |
| `db-wal-recovery` | arm-A `PLLsp9o`, arm-A `wcyyiiM`, arm-B `Mr3Zr88`, arm-B `YEwnbR7`, arm-B `vHyRevz` | `recovered.json` passes 5 of 7 checks (exists, valid JSON, structure, sorted, no duplicate IDs) but the WAL-applied value for one record is wrong (`100` instead of the expected post-WAL value `150`) — the WAL decryption/application step produced a wrong value, not an absent one. |
| `sparql-university` | arm-B `4WHmMEa`, arm-B `c5QCxQA` | Query file exists and runs without error (`test_sparql_runs_without_error` passes), but `test_sparql_query_results` fails — the SPARQL query itself returns incorrect result rows. |
| `rstan-to-pystan` *(remote source, `tb-delta-20260907T203448Z-arm-B`)* | arm-B `TFqBMv2` | `alpha_est.csv`/`rho_est.csv` exist, parse, and pass 4 of 6 checks (`test_r_rstan_not_installed`, `test_output_files_exist`, `test_sigma_estimation_accuracy`, `test_beta_estimation_accuracy`); `test_alpha_estimation_accuracy` fails (`alpha posterior mean 1.1029545992647702` outside `[1.08, 1.1]`) and `test_rho_estimation_accuracy` fails (`rho[2] posterior mean 1.5156673509613854` outside `[1.49, 1.51]`) — well-formed output, wrong statistical-fit values. |
| `train-fasttext` *(remote source, `tb-delta-20260908T001726Z-arm-A`)* | arm-A `UKRXPtU` | `/app/model.bin` exists and loads (unlike the other 3 `train-fasttext` trials, see `required-output-artifact-absent.md`), but `test_accuracy` fails (`0.600325 <= 0.62` threshold) and `test_model_size` fails (`661644996 <= 157286400` cap) — a well-formed, loadable model with wrong computed values, not a missing artifact. |

20 distinct trials across 8 task names, all `exception_info: null`, all
`verifier_result.rewards.reward: 0.0`. (Fix-pass addition, 2026-09-08: `rstan-to-pystan` and one
`train-fasttext` trial — see `docs/artifacts/failure-taxonomy-v1.md` §8.6 for why these were
missing from the first pass and how they were found.)

## Representative verbatim evidence (`chess-best-move`, arm-A trial `76RBoFA`)

```
>       assert sorted(move) == sorted(["g2g4", "e2e4"]), "File is wrong"
E       AssertionError: File is wrong
E       assert ['c3e4'] == ['e2e4', 'g2g4']
```

Source: `tb-delta-20260814T111217Z-arm-A/chess-best-move__76RBoFA/verifier/test-stdout.txt`
(local worktree `t407-tb-delta`, T407's original k=3 run).
