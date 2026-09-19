# Failure pattern: required output artifact entirely absent (Terminal-Bench)

**Scheme:** `docs/artifacts/failure-taxonomy-v1.md` §8 (T409 extension)
**Source:** Harbor/Terminal-Bench trajectories — local k=3 run (`tb-delta-20260814T111217Z`) plus
3 `train-fasttext` trials from the remote Design A source, added in the 2026-09-08 fix pass (see
`docs/artifacts/failure-taxonomy-v1.md` §8.6).
**Task type:** genuine task-level failure (`exception_info: null`, `reward == 0.0`).

## Axis classification

| Axis | Value | Status |
|---|---|---|
| `cause` | `agent-incomplete-task-execution` | **new** (added to `failure-taxonomy-v1.md` §3.1) |
| `behavior` | `required-section-absent` | **reused from `failure-taxonomy-v1.md` §3.2, unchanged** |
| `mechanism` | `whole-block-absence` | **reused from `failure-taxonomy-v1.md` §3.3, unchanged** |

## Why the existing `behavior`/`mechanism` values transfer as-is

`required-section-absent` is defined in `failure-taxonomy-v1.md` §3.2 as "a declared
section/field-group is completely missing from the document (no partial trace of it anywhere)."
`whole-block-absence` (§3.3) similarly says "no partial container for it exists anywhere in the
document." Read at the level of generality §7 anticipates ("observable document/**output**
shape"), a Terminal-Bench trial whose required deliverable file was never written at all — no
partial file, no directory entry, nothing — is the same observable shape as a golden-suite
document missing a whole required section: total absence, no partial trace. Reusing these two
values rather than minting near-duplicates keeps the taxonomy from fragmenting into
source-specific near-synonyms for the same underlying shape.

`cause`, however, does not reuse any of the 3 existing golden values, all three of which describe
document-*contract-authoring* mismatches (a spec exists, an artifact was produced, and it doesn't
match the spec). In every case below, **no artifact was produced at all** — the agent's own
session ended (ran out of the crypto/reverse-engineering attack, or the automated VM/build step it
depended on never completed) before it ever got to writing the required output. That is a
genuinely different root cause: `agent-incomplete-task-execution` — "the agent's session did not
result in the task being functionally completed," which this extension also uses for the
`runtime-service-not-functional.md` and `produced-code-fails-to-build.md` patterns (see those files
for why the same cause spans different observable shapes, mirroring how
`established-practice-drift` already spans 3 different golden `behavior` values).

## Real cases (local k=3 run, `tb-delta-20260814T111217Z`, unless noted)

| Task | Trial (arm/hash) | Required artifact | Observed |
|---|---|---|---|
| `crack-7z-hash` | arm-A `JXwjRRg`, arm-A `tFECzPa`, arm-B `3GfVeuR`, arm-B `HfE8QY4` | `/app/solution.txt` (extracted password from the 7z archive) | `FileNotFoundError` — file never created. |
| `feal-linear-cryptanalysis` | arm-A `eGkDRSL` | `/app/plaintexts.txt` (decrypted plaintexts from the linear-cryptanalysis attack) | `FileNotFoundError` — file never created. |
| `make-mips-interpreter` | arm-A `aZxGN2n`, arm-A `iwKHm5D`, arm-A `oYeiuW5`, arm-B `7AmNmDJ`, arm-B `av3J6Bt`, arm-B `jNPzqCd` | `/tmp/frame.bmp` (a VM-execution framebuffer capture) | `test_vm_execution` fails with a task-internal `TimeoutError` (the verifier's own wait loop for the VM to run, distinct from a harness-level `AgentTimeoutError` — `exception_info` is `null` for all these trials, confirming this is a genuine task-level outcome, not an infra exception); the downstream `test_frame_bmp_exists` then fails with `FileNotFoundError` because the file the timed-out VM never produced does not exist. |
| `train-fasttext` *(remote source only)* | `tb-delta-20260907T162617Z-arm-B` `omH7FVB`, `tb-delta-20260907T203448Z-arm-B` `c96WNaX`, `tb-delta-20260907T203448Z-arm-A` `n8bk9hZ` | `/app/model.bin` (the trained fastText model) | `ValueError: /app/model.bin cannot be opened for loading!` on `test_accuracy`, then `FileNotFoundError: [Errno 2] No such file or directory: '/app/model.bin'` on `test_model_size` — the model file was never written. **Note:** a 4th `train-fasttext` trial (remote, `tb-delta-20260908T001726Z-arm-A` `UKRXPtU`) does *not* fit this pattern — its `model.bin` exists and loads, but has wrong accuracy/size values; that trial is cited under `incorrect-computed-output-value.md` instead, not here — see that file. |

14 distinct trials across 4 task names, all `exception_info: null`, all `reward: 0.0`. (Fix-pass
addition, 2026-09-08: 3 of `train-fasttext`'s 4 genuinely-failing trials — see
`docs/artifacts/failure-taxonomy-v1.md` §8.6.)

## A note on `make-mips-interpreter`'s internal `TimeoutError`

This pattern's `make-mips-interpreter` cases surface a `TimeoutError` inside the verifier's own
test body (`test_vm_execution`), not the harness-level `AgentTimeoutError` that this extension
excludes as an infrastructure failure elsewhere (see `docs/benchmarks/failures/README.md`
§"Infrastructure-failure exclusion"). The distinguishing signal is `exception_info: null` in
`result.json` — Harbor's own harness reports these as ordinary verifier outcomes, not exceptions
raised by the harness/agent-execution layer. The task's own test suite chose to implement its
"did the VM actually run" check as a timeout, and that timeout is the task-defined verification
mechanism, not a sign that Harbor itself failed to execute the trial. This distinction matters:
misclassifying a task-internal timeout as an infra failure would silently shrink the genuine
task-outcome failure set.

## Representative verbatim evidence (`crack-7z-hash`, arm-A trial `JXwjRRg`)

```
>       assert os.path.exists(solution_path), (
            f"Solution file {solution_path} does not exist."
        )
E       AssertionError: Solution file /app/solution.txt does not exist.
```

Source: `tb-delta-20260814T111217Z-arm-A/crack-7z-hash__JXwjRRg/verifier/test-stdout.txt`
(local worktree `t407-tb-delta`, T407's original k=3 run).
