# Failure pattern: `runtime-service-not-functional` (Terminal-Bench)

**Scheme:** `docs/artifacts/failure-taxonomy-v1.md` §8 (T409 extension)
**Source:** Harbor/Terminal-Bench trajectories (local k=3 run, `tb-delta-20260814T111217Z`).
**Task type:** genuine task-level failure (`exception_info: null`, `reward == 0.0`).

## Axis classification

| Axis | Value | Status |
|---|---|---|
| `cause` | `agent-incomplete-task-execution` | **new** (same value as `required-output-artifact-absent.md` — see below) |
| `behavior` | `runtime-service-not-functional` | **new** (added to `failure-taxonomy-v1.md` §3.2) |
| `mechanism` | `live-system-unreachable-or-erroring` | **new** (added to §3.3) |

## Why this is a distinct pattern

Every case here has the agent leaving behind *some* setup work (proto files generated, a web
server config written, a Windows VM installed, a package pushed to a local index, a model
directory downloaded) — this is not "nothing was produced" (that's
`required-output-artifact-absent.md`). But at verification time, whatever the agent stood up is
not actually **live and functioning**: a connection is refused, an HTTP probe returns no response,
a subprocess exits non-zero, a control-plane socket is missing, or a downloaded artifact fails to
actually load. The failure is discovered only when the verifier *exercises* the system at runtime,
not by inspecting a static file. This is a materially different observable shape from a static
value being wrong (`incorrect-computed-output-value.md`) or a static file being absent
(`required-output-artifact-absent.md`), so neither existing nor other newly-added `behavior`/
`mechanism` values fit without forcing.

`cause` reuses `agent-incomplete-task-execution` (same as `required-output-artifact-absent.md`):
the underlying "why" is the same in both patterns — the agent's session did not reach a working
end state — but the two patterns differ in *how* that incompleteness is observable (total absence
of a file vs. presence of a non-functional system). This mirrors how the existing golden scheme
already lets one `cause` value (`established-practice-drift`) span three different `behavior`
values; the same independence holds here.

## Real cases (local k=3 run, `tb-delta-20260814T111217Z`)

| Task | Trial (arm/hash) | What failed at runtime |
|---|---|---|
| `configure-git-webserver` | arm-A `EUnKCNp`, arm-A `LY5aEQP`, arm-A `pMHJuJX`, arm-B `aNxqcxX`, arm-B `h3DC9Wm`, arm-B `uPKHiy9` | `verify.sh` reports "❌ TEST FAILED: Web server returned HTTP 000" — the web server the agent was required to configure never responds to a live HTTP probe (a preceding `expect` script also shows `git not installed`, consistent with the setup never fully completing). |
| `kv-store-grpc` | arm-A `RFPENtd`, arm-A `m6spyPr`, arm-A `yhChGbh`, arm-B `3R7qbwv`, arm-B `vg3ZD5E` | `grpc._channel._InactiveRpcError: ... Connection refused` on `test_real_grpc_server_running` — proto generation and protocol-handshake checks pass, but no live gRPC server is actually listening on the required port at verification time. |
| `install-windows-3-11` | arm-A `2b22LFX`, arm-A `BfZe5QW`, arm-B `9yGsRo9`, arm-B `LhwTVuy`, arm-B `eYhp3L5` | `socat ... UNIX-CONNECT:/tmp/qemu-monitor.sock: No such file or directory` — the QEMU monitor control socket the automated keyboard-input test depends on is not present, so the live VM cannot be driven/verified even though core install-file checks passed. |
| `pypi-server` | arm-A `4rt932R` | `pip install --index-url http://localhost:8080/simple vectorops==0.1.0` exits non-zero — the local PyPI server the agent was required to stand up does not correctly serve the package on request. |
| `hf-model-inference` | arm-A `LJVquVs`, arm-A `s7f6WHU`, arm-B `5bqsBf4`, arm-B `aJK4XBd` | `AutoModelForSequenceClassification.from_pretrained(...)` fails at load time — the model directory exists on disk (`os.path.exists` passes) but is not a functioning, loadable model (config `model_type` not recognized by the installed `transformers` version), so a live inference call cannot succeed even though the on-disk artifact is present. |

21 distinct trials across 5 task names, all `exception_info: null`, all `reward: 0.0`.

## Representative verbatim evidence (`kv-store-grpc`, arm-A trial `RFPENtd`)

```
E           grpc._channel._InactiveRpcError: <_InactiveRpcError of RPC that terminated with:
E           	status = StatusCode.UNAVAILABLE
E           	details = "failed to connect to all addresses; last error: UNKNOWN: ipv4:127.0.0.1:5328:
Failed to connect to remote host: connect: Connection refused (111)"
...
PASSED ../tests/test_outputs.py::test_grpc_protocol_handshake
FAILED ../tests/test_outputs.py::test_real_grpc_server_running - AssertionError...
FAILED ../tests/test_outputs.py::test_grpc_server_functionality - grpc._channel...
```

Source: `tb-delta-20260814T111217Z-arm-A/kv-store-grpc__RFPENtd/verifier/test-stdout.txt`
(local worktree `t407-tb-delta`, T407's original k=3 run).
