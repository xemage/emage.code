# Failure pattern: `produced-code-fails-to-build` (Terminal-Bench)

**Scheme:** `docs/artifacts/failure-taxonomy-v1.md` §8 (T409 extension)
**Source:** Harbor/Terminal-Bench trajectory — **remote-only source**, `10.10.160.11:/root/emage-code-t407/jobs/tb-delta-20260907T162617Z-arm-A/`
(Design A's successful pass #1 of 3, per `docs/tasks/task-T407.md`'s "Artifact reconciliation"
note — this trial is not copied into this repo; read via read-only SSH per this task's brief).
**Task type:** genuine task-level failure (`exception_info: null`, `reward == 0.0`).

## Axis classification

| Axis | Value | Status |
|---|---|---|
| `cause` | `agent-incomplete-task-execution` | **new** (same value as `required-output-artifact-absent.md` and `runtime-service-not-functional.md`) |
| `behavior` | `produced-code-fails-to-build` | **new** (added to `failure-taxonomy-v1.md` §3.2) |
| `mechanism` | `build-toolchain-error` | **new** (added to §3.3) |

## Why this is a distinct pattern

The agent submitted a source file (`user.cpp`), but it never even reaches the point where its
runtime behavior, correctness, or memory safety could be evaluated: the **compiler/linker step
itself fails** before any of the task's actual checks (crash-freedom, no memory leaks) can run.
This is earlier in the pipeline than every other pattern in this extension —
`incorrect-computed-output-value.md` and `invariant-violation-in-generated-artifact.md` both
require the artifact to at least exist and be evaluable; `required-output-artifact-absent.md`
is about a file never being written at all (no build step involved, since the tasks in that
pattern don't require compilation); `runtime-service-not-functional.md` is about a system that
builds/starts but doesn't behave correctly live. A build/link failure is a distinct, earlier-stage
observable shape, so it warrants its own `behavior`/`mechanism` pair rather than being folded into
any of the above.

`cause` reuses `agent-incomplete-task-execution` — the same reasoning as the other two patterns
that share this value: the agent's submitted work never reached a working end state (here,
"working" means "compiles at all"), which is the same underlying "why" regardless of whether the
observable symptom is a missing file, a non-functional live service, or (as here) a build failure.

## Real case (remote source, Design A run `tb-delta-20260907T162617Z`, arm A)

| Task | Trial (arm/hash) | What failed |
|---|---|---|
| `custom-memory-heap-crash` | arm-A `kYz3evQ` | `test_program_compiles_release` (and 4 other dependent checks) fail with a linker error: `ld: ... multiple definition of 'operator new(unsigned long)'` — the agent's `user.cpp` redefines global `operator new`/`operator delete` overloads that are already defined in the harness's `main.cpp`, so the release build never links. |

1 trial cited from the remote source. Note: this same task (`custom-memory-heap-crash`) passed
with `reward: 1.0` in all 3 trials of the **local** k=3 run (`tb-delta-20260814T111217Z`, both
arms) — this specific build-failure mode is an example of trial-to-trial variance surfaced only by
the **remote Design A source**, concretely demonstrating why this task draws on both sources
rather than treating the local k=3 run as sufficient on its own.

## Representative verbatim evidence

```
E           Failed: Failed to compile release build:
E           STDOUT:
E           STDERR: /usr/bin/ld: /tmp/ccJRABc2.o: in function `operator new(unsigned long)':
E           user.cpp:(.text+0x0): multiple definition of `operator new(unsigned long)';
/tmp/cc8b8RX1.o:main.cpp:(.text+0xd0): first defined here
...
=========================== short test summary info ============================
PASSED ../tests/test_outputs.py::test_protected_files_not_modified
FAILED ../tests/test_outputs.py::test_program_compiles_debug - Failed: Failed...
FAILED ../tests/test_outputs.py::test_program_compiles_release - Failed: Fail...
FAILED ../tests/test_outputs.py::test_debug_build_runs_without_crash - Failed...
FAILED ../tests/test_outputs.py::test_release_build_runs_without_crash - Fail...
FAILED ../tests/test_outputs.py::test_no_memory_leaks_with_valgrind - Failed:...
========================= 5 failed, 1 passed in 3.64s ==========================
```

Source: `/root/emage-code-t407/jobs/tb-delta-20260907T162617Z-arm-A/custom-memory-heap-crash__kYz3evQ/verifier/test-stdout.txt`
on host `10.10.160.11`, read via read-only SSH (no Docker/Harbor commands were run on that host —
this task only read pre-existing `result.json`/`verifier/test-stdout.txt` files from prior T407
runs).
