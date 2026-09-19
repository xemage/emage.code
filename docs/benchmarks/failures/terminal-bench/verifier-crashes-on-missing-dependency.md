# Failure pattern: `verifier-subprocess-crashes-fatally` (Terminal-Bench)

**Scheme:** `docs/artifacts/failure-taxonomy-v1.md` §8 (T409 extension, fix pass)
**Source:** Harbor/Terminal-Bench trajectory — **remote-only source**,
`10.10.160.11:/root/emage-code-t407/jobs/tb-delta-20260907T162617Z-arm-A/` (Design A's successful
pass #1 of 3; this trial is not copied into this repo, read via read-only SSH per this task's
brief, same discipline as `produced-code-fails-to-build.md`'s `custom-memory-heap-crash` case).
**Task type:** genuine task-level failure (`exception_info: null`, `verifier_result.rewards.reward
== 0.0`).

## Axis classification

| Axis | Value | Status |
|---|---|---|
| `cause` | `agent-incomplete-task-execution` | **reused** (same value as `required-output-artifact-absent.md`, `runtime-service-not-functional.md`, `produced-code-fails-to-build.md` — see below) |
| `behavior` | `verifier-subprocess-crashes-fatally` | **new** (added to `failure-taxonomy-v1.md` §3.2) |
| `mechanism` | `fatal-signal-on-missing-input-artifact` | **new** (added to §3.3) |

## Why this is a distinct pattern, not a forced reuse

The task's required training pipeline never produced its intermediate trained-model artifact
(`/app/caffe/examples/cifar10/cifar10_quick_iter_500.caffemodel`) — the same underlying "agent
session did not reach a working end state" root cause as `required-output-artifact-absent.md`.
But the **observable shape at verification time is categorically different** from that pattern:

- `required-output-artifact-absent.md`'s cases are discovered by a **graceful, catchable** Python-
  level check (`os.path.exists`, `open(...)`) that cleanly reports `FileNotFoundError` or an
  `AssertionError` — the verifier process itself completes normally and reports a clean pass/fail.
- Here, the verifier instead **invokes a native binary** (`caffe.bin test ...`) that itself
  attempts to load the missing artifact via its own internal HDF5-loading code path. That load
  failure trips the binary's own fatal-error handling (`glog`'s `LogMessageFatal` /
  `CHECK failed: file_hid >= 0`), which **aborts the whole process with `SIGABRT`**
  (`returncode: -6`) rather than raising anything Python-catchable. The pytest wrapper only
  observes a non-zero/negative `CompletedProcess.returncode`, not a clean assertion about a missing
  file — a fatal crash mid-execution, not an orderly "this doesn't exist" report.
- It also doesn't fit `runtime-service-not-functional.md`: that pattern's cases are about a
  **persistent live service/process** (a webserver, a gRPC server, a VM, a package index, a loaded
  inference model) that the agent stood up and left non-functional, discovered by *exercising* it
  (a connection attempt, an HTTP probe, a load call). `caffe.bin test` is a one-shot batch
  verification subprocess, not a service being probed for liveness — there is no "system" left
  running to be unreachable; there is a single invocation that crashes outright before it can even
  attempt the comparison the task cares about.
- It doesn't fit `produced-code-fails-to-build.md` either: no compilation/link step is involved
  here (`test_caffe_version_and_source` and `test_prototxt_files_exist` both pass — the Caffe
  toolchain itself is fine), and the crash happens well after any build stage, during test
  execution.
- It doesn't fit `incorrect-computed-output-value.md`: no computed value is ever produced to
  compare against ground truth — the process dies before it can report *any* value, correct or
  not.

None of the five existing `behavior`/`mechanism` pairs describe "the verifier's own invoked
external tool aborts via an uncatchable fatal signal before completing evaluation" — this is a
genuinely new observable failure shape, warranting its own pair while reusing the existing
`agent-incomplete-task-execution` `cause` (the underlying "why" — training never finished — is
identical to the other three patterns that already use this `cause` value).

## Real case (remote source, Design A run `tb-delta-20260907T162617Z`, arm A)

| Task | Trial (arm/hash) | What failed |
|---|---|---|
| `caffe-cifar-10` | arm-A `Wq8EjvK` | `caffe.bin test -model .../cifar10_quick_test.prototxt -weights .../cifar10_quick_iter_500.caffemodel` crashes with `SIGABRT` (`returncode: -6`) inside `caffe::Net<>::CopyTrainedLayersFromHDF5()` — an HDF5-open failure (`Couldn't open .../cifar10_quick_iter_500.caffemodel`, `errno=2`) trips a `glog` `LogMessageFatal` check inside the Caffe binary itself. `test_cifar10_model_exists`, `test_cpu_only_training_configured`, `test_training_completed_500_iterations`, and `test_model_accuracy_verification` all fail as a consequence; `test_caffe_version_and_source` and `test_prototxt_files_exist` pass. |

1 distinct trial cited, 1 task name.

## Representative verbatim evidence (`caffe-cifar-10`, arm-A trial `Wq8EjvK`)

```
E         HDF5-DIAG: Error detected in HDF5 (1.10.10) thread 1:
E           #003: ../../../src/H5FDsec2.c line 351 in H5FD__sec2_open(): unable to open file: name = '/app/caffe/examples/cifar10/cifar10_quick_iter_500.caffemodel', errno = 2, error message = 'No such file or directory', flags = 0, o_flags = 0
E             major: File accessibility
E             minor: Unable to open file
E         F20260907 17:15:34.886670 17341 net.cpp:791] Check failed: file_hid >= 0 (-1 vs. 0) Couldn't open /app/caffe/examples/cifar10/cifar10_quick_iter_500.caffemodel
E         *** Check failure stack trace: ***
E             @     0x7a65d7e90063  caffe::Net<>::CopyTrainedLayersFromHDF5()
E             @     0x7a65d7e93d94  caffe::Net<>::CopyTrainedLayersFrom()
...
E       assert -6 == 0
E        +  where -6 = CompletedProcess(args=['/app/caffe/.build_release/tools/caffe.bin', 'test', ...]).returncode

=========================== short test summary info ============================
PASSED ../tests/test_outputs.py::test_caffe_version_and_source
PASSED ../tests/test_outputs.py::test_prototxt_files_exist
FAILED ../tests/test_outputs.py::test_cifar10_model_exists - AssertionError: ...
FAILED ../tests/test_outputs.py::test_cpu_only_training_configured - Assertio...
FAILED ../tests/test_outputs.py::test_training_completed_500_iterations - Ass...
FAILED ../tests/test_outputs.py::test_model_accuracy_verification - Assertion...
========================= 4 failed, 2 passed in 0.27s ==========================
```

Source: `tb-delta-20260907T162617Z-arm-A/caffe-cifar-10__Wq8EjvK/verifier/test-stdout.txt` on host
`10.10.160.11`, read via read-only SSH (no Docker/Harbor commands were run on that host — this
fix pass only read pre-existing `result.json`/`verifier/test-stdout.txt` files from prior T407
runs, same as the rest of this task).
