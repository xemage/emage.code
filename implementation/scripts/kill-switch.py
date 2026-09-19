#!/usr/bin/env python3
"""CLI entry point for the Phase 6 kill switch (T502, `plan-035` nominal
T466). Thin wrapper around `implementation/runtime/kill_switch.py`'s library
functions -- see that module and `docs/artifacts/phase6-kill-switch-v1.md`
for the full design and the resume-path decision.

Usage:
    python3 implementation/scripts/kill-switch.py halt [--file PATH] [--reason TEXT]
    python3 implementation/scripts/kill-switch.py status [--file PATH]

`halt` is the one documented command that sets the halt signal
(`plan-035`'s own literal wording: "one documented command halts the loop").
`status` is a read-only convenience wrapper around `is_halted()` for humans
and scripts to check current state; it never modifies the signal.

There is no `resume` / `clear` / `reset` subcommand in this tool, by design.
Once set, the halt signal is cleared only by a human manually deleting the
sentinel file (default: `tmp/kill-switch/HALT`, or wherever `--file` /
`KILL_SWITCH_FILE` points) -- entirely outside this script's own code path.
See the documentation artifact's "Resume-path decision" section for the
justification.

Exit codes: `halt` exits 0 on success. `status` exits 0 when NOT halted and 1
when HALTED, so it composes directly with shell conditionals
(`kill-switch.py status || echo "halted, stopping"`).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
REPO_ROOT = HERE.parents[2]
sys.path.insert(0, str(REPO_ROOT))

from implementation.runtime.kill_switch import halt, is_halted, resolve_halt_file  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="kill-switch.py",
        description="Phase 6 kill-switch: set or check a durable halt signal. "
                     "No resume/clear subcommand exists in this tool by design.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    halt_parser = sub.add_parser("halt", help="Set the halt signal.")
    halt_parser.add_argument(
        "--file", default=None,
        help="Sentinel file path (default: KILL_SWITCH_FILE env var, else tmp/kill-switch/HALT).",
    )
    halt_parser.add_argument("--reason", default=None, help="Optional human-readable reason recorded in the signal file.")

    status_parser = sub.add_parser("status", help="Report whether the halt signal is currently set.")
    status_parser.add_argument(
        "--file", default=None,
        help="Sentinel file path (default: KILL_SWITCH_FILE env var, else tmp/kill-switch/HALT).",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "halt":
        target = halt(args.file, reason=args.reason)
        print(f"HALTED: signal set at {target}")
        return 0

    if args.command == "status":
        target = resolve_halt_file(args.file)
        halted = is_halted(args.file)
        print(f"{'HALTED' if halted else 'NOT HALTED'} ({target})")
        return 1 if halted else 0

    return 2  # pragma: no cover -- argparse `required=True` prevents this.


if __name__ == "__main__":
    raise SystemExit(main())
