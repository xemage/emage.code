# Phase 6 Kill Switch — v1

**Based on:** `docs/tasks/task-T502.md` (`plan-035-roadmap-v7-ground-up.md`'s nominal T466,
`docs/plans/plan-055-phase6-closed-loop-rescoped-detailed-planning.md` §4's `T466-equiv` row,
`docs/artifacts/phase6-sia-readiness-audit-v1.md` §4).

**Refs:** T502. Builds the standalone kill-switch primitive for Phase 6's eventual closed loop.

## 1. What this document declares

This repository now has a real, tested, standalone kill-switch primitive:

- `implementation/runtime/kill_switch.py` — the importable library (`halt()`, `is_halted()`,
  `resolve_halt_file()`).
- `implementation/scripts/kill-switch.py` — the documented CLI wrapper (`halt`, `status`
  subcommands).
- `tests/functional/test_kill_switch.py` — the committed test proving both required properties
  below.

## 2. Why this exists, and its scope boundary

Phase 6's eventual closed loop (a future weakness-miner, diff-proposal generator, and
validation/promotion step) does not exist yet — none of it is built, per
`docs/artifacts/phase6-sia-readiness-audit-v1.md` and `plan-055`'s re-scoping. This task
therefore cannot wire a halt check into a real loop-runner today, because there is no
loop-runner to wire into.

What this **does** build is the generic, reusable primitive itself: a durable, file-based halt
signal any future Phase 6 loop-runner can import and check before acting, built and proven
correct in isolation. This is a deliberate scoping decision (mirroring T501's own disclosed
scoping decision in its sibling brief), not an oversight — the hard part (an actual closed loop
to halt) is out of scope for every Phase 6 task dispatched so far, including this one.

This document does **not** claim any current code path calls `is_halted()` — there is nothing
in this repository yet that would call it. That wiring is future Phase 6 work (T462-equiv/
T463-equiv's eventual loop-runner), not this task's.

## 3. The documented command

```bash
# Set the halt signal (uses the default sentinel path unless overridden):
python3 implementation/scripts/kill-switch.py halt [--file PATH] [--reason TEXT]

# Check current halt state (exit code 1 when HALTED, 0 when NOT HALTED):
python3 implementation/scripts/kill-switch.py status [--file PATH]
```

`halt` is the single, documented command that sets the signal, per `plan-035`'s own literal
wording ("one documented command halts the loop"). `status` is a read-only convenience wrapper
around `is_halted()` for humans and future scripts; it never modifies the signal.

Programmatically, any future code imports the library directly:

```python
from implementation.runtime.kill_switch import is_halted

if is_halted():
    ...  # a future loop-runner would stop here, once one exists
```

## 4. Where the halt signal lives

A sentinel file, resolved in this precedence order:

1. An explicit path argument (`--file` on the CLI, or a direct argument to `halt()`/`is_halted()`
   in code).
2. The `KILL_SWITCH_FILE` environment variable, if set.
3. The documented default: `<repo root>/tmp/kill-switch/HALT`.

The default lives under `tmp/`, which the repo root `.gitignore`'s "Logs / temp" section already
excludes (`tmp/`) — so the default sentinel path never risks an accidental commit, without this
task needing to touch `.gitignore` itself (`.gitignore` is outside this task's file-ownership
scope per `docs/tasks/task-T502.md`'s Constraints section).

The signal is a real file on disk (containing a UTC timestamp and an optional reason string),
not in-memory process state — durable and process-independent by construction. This is proven
directly by `tests/functional/test_kill_switch.py`'s `TestKillSwitchCli` cases, which set the
halt signal via one subprocess invocation of the CLI and detect it via a second, entirely
separate subprocess invocation.

## 5. Resume-path decision (required, not left implicit)

**Decision: (a) — no programmatic resume path exists in this deliverable at all.**

There is no `resume`, `clear`, or `reset` function in `implementation/runtime/kill_switch.py`,
and no corresponding subcommand in `implementation/scripts/kill-switch.py`. The only way to clear
a halt signal is a human manually deleting the sentinel file (e.g. `rm tmp/kill-switch/HALT`),
entirely outside any tool this task builds.

### Justification

- **A kill switch that can clear itself through its own tooling is a weaker kill switch.** The
  whole point of this primitive (per `plan-035`'s literal acceptance criterion, "cannot
  self-resume") is that once triggered, resuming requires a distinct, deliberate, out-of-band
  human action — not a flag or subcommand that could be scripted, defaulted, or invoked
  accidentally by whatever process the switch was meant to stop.
- **Zero surface area for the "never clears it" guarantee to regress.** Because no clearing code
  path exists anywhere in this module, `is_halted()` cannot accidentally grow a side effect that
  weakens the guarantee in a future edit — there is no resume code to audit, keep correct, or
  accidentally wire into the wrong place.
- **A file-delete is already the simplest, most auditable manual action available.** No new
  tooling, permissions model, or secondary confirmation flow is needed; deleting a known,
  documented path is a standard, low-risk operational action any human with repo/filesystem
  access can already perform and reason about.
- **Consistent with this repo's own precedent for declarative-plus-review controls.**
  `docs/artifacts/protected-paths-v1.md` §4 documents that repo's write-scope exclusion as
  "declarative and auditable... not a git-level enforcement mechanism," relying on written policy
  plus review discipline rather than automated tooling for the control's own boundary. The same
  reasoning applies here: the boundary between "halted" and "resumed" is enforced by there being
  no automated path across it, not by trusting a resume command to be used carefully.

If a future need arises for an automated resume path (e.g. an on-call rotation wanting a
single auditable command instead of a manual file delete), that is a new, explicitly-scoped
follow-up task, not a silent addition to this module — consistent with `docs/artifacts/
protected-paths-v1.md` §5's "never a silent edit, always a named, authorized task" precedent for
changing a standing operational control.

## 6. What this does *not* do (scope boundary)

- **No loop-runner exists yet, so nothing calls `is_halted()` today.** This task builds and
  proves the primitive in isolation; wiring it into an actual halt check is a future Phase 6
  task's job once a loop-runner exists.
- **No automatic expiry of any kind.** `is_halted()` is a bare existence check — it never
  inspects the sentinel file's mtime or applies a TTL. A halt set once stays set indefinitely
  until a human deletes the file. `tests/functional/test_kill_switch.py`'s
  `test_no_automatic_expiry_even_with_a_very_old_timestamp` proves this by backdating the
  sentinel file's mtime by a year and confirming `is_halted()` still reports `True`.
- **No dependency on `implementation/sia/`, T501's module, or any other Phase 6 code.** Every
  test in `tests/functional/test_kill_switch.py` exercises only this task's own deliverable
  (`kill_switch.py` and `kill-switch.py`), directly proving the standalone requirement.
- **Not a git-level or process-level enforcement mechanism.** This module does not, and cannot by
  itself, force any hypothetical future loop-runner to actually check `is_halted()` before
  acting — that discipline belongs to whatever future code calls this primitive, the same way
  `docs/artifacts/protected-paths-v1.md`'s write-scope exclusion relies on agent instructions and
  review rather than a git hook.

## 7. Verification

- `tests/functional/test_kill_switch.py` — 15 tests covering: halt sets a detectable signal;
  the signal persists across a real process boundary (CLI subprocess sets it, a separate CLI
  subprocess detects it); repeated `is_halted()`/`status` calls never clear the signal; repeated
  `halt()` calls stay halted; no automatic expiry even with a backdated mtime; the module and CLI
  expose no resume/clear/reset function or subcommand; invoking a literal `resume` subcommand
  fails with a non-zero exit (there is none); path resolution precedence (explicit > env var >
  default); the default sentinel path lives under the already-`.gitignore`d `tmp/`.
- Run directly: `python3 -m unittest tests.functional.test_kill_switch -v`.
- Included automatically in `python3 tests/run.py` (discovered under `tests/functional/`).
