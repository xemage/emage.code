"""Phase 6 kill-switch primitive (T502, `plan-035` nominal T466).

`docs/tasks/task-T502.md`'s own scoping note applies here verbatim: Phase 6's
eventual closed loop (a future weakness-miner, diff-proposal generator, and
validation/promotion step) does not exist yet, so this module cannot wire a
halt check into a real loop-runner today. What it *does* build is the
generic, reusable primitive itself -- a durable, file-based halt signal any
future Phase 6 loop-runner can import and check before acting -- proven
correct here, in isolation, independent of code that doesn't exist yet. See
`docs/artifacts/phase6-kill-switch-v1.md` for the full design writeup
including the resume-path decision.

Two properties, both proven by `tests/functional/test_kill_switch.py`, not
merely asserted here:

1. Halt is detectable. `halt()` sets a durable, process-independent signal
   (a sentinel file); `is_halted()` reports it, importable by any future code
   with no dependency on anything outside this module.
2. A halted state cannot self-resume. `is_halted()` is a pure read: it never
   creates, modifies, or deletes the sentinel file, no matter how many times
   or in what order it is called, and applies no time-based expiry -- it is
   a bare existence check. This module deliberately exposes **no** resume,
   clear, or reset function of any kind (decision (a) in the task brief's
   Objective section 2): a halted signal is cleared only by a human manually
   deleting the sentinel file, an action entirely outside this module's own
   code path. See the documentation artifact for the justification.

Mirrors `implementation/runtime/golden_harness/trial_store.py`'s
"always caller-supplied, no default path that writes anywhere under a
protected path" discipline: every function here accepts an explicit path (or
an environment-variable override), never silently writing somewhere a caller
did not ask for beyond the documented default.
"""
from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path

# implementation/runtime/kill_switch.py -> implementation/runtime -> implementation -> repo root.
REPO_ROOT = Path(__file__).resolve().parents[2]

# `tmp/` is already excluded by the repo root `.gitignore` ("Logs / temp"
# section), so the default sentinel path never risks an accidental commit
# without this task needing to touch `.gitignore` itself (out of this task's
# file-ownership scope per `docs/tasks/task-T502.md`'s Constraints section).
DEFAULT_HALT_FILE = REPO_ROOT / "tmp" / "kill-switch" / "HALT"

# Overrides the default sentinel path when set, so a real deployment can
# point the signal at whatever durable location it prefers without editing
# this module.
ENV_VAR = "KILL_SWITCH_FILE"


def resolve_halt_file(explicit_path: str | Path | None = None) -> Path:
    """Resolve the sentinel-file path to use: an explicit argument wins,
    then the `KILL_SWITCH_FILE` environment variable, then the documented
    default (`DEFAULT_HALT_FILE`). Pure function -- performs no I/O."""
    if explicit_path is not None:
        return Path(explicit_path)
    env_value = os.environ.get(ENV_VAR)
    if env_value:
        return Path(env_value)
    return DEFAULT_HALT_FILE


def halt(path: str | Path | None = None, *, reason: str | None = None) -> Path:
    """Set the halt signal: create (or overwrite) the sentinel file at the
    resolved path, recording the UTC timestamp and an optional human-supplied
    reason. Durable and process-independent by construction -- it is a real
    file on disk, not in-memory state -- so a separate process invoked later
    (e.g. a future loop-runner's own startup check) observes the same signal.

    Calling `halt()` again while already halted is safe and idempotent with
    respect to the halted state (still halted afterwards); it simply
    refreshes the recorded timestamp/reason.
    """
    target = resolve_halt_file(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).isoformat()
    lines = [f"halted_at={timestamp}"]
    if reason:
        lines.append(f"reason={reason}")
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return target


def is_halted(path: str | Path | None = None) -> bool:
    """Report whether the halt signal is currently set at the resolved path.

    Read-only by construction: this function performs no write, delete, or
    mtime-based expiry check of any kind against `path`. It must remain a
    bare existence check forever -- adding any clearing side effect here
    would violate this module's own "cannot self-resume" guarantee, which
    `tests/functional/test_kill_switch.py` proves by calling this function
    repeatedly and confirming the sentinel file is never removed.
    """
    target = resolve_halt_file(path)
    return target.exists()
