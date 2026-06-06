#!/usr/bin/env python3
"""Smoke runner for v3 experimental adapter prototypes."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

IMPLEMENTATION_ROOT = Path(__file__).resolve().parents[1]
if str(IMPLEMENTATION_ROOT) not in sys.path:
    sys.path.insert(0, str(IMPLEMENTATION_ROOT))

from adapters.antigravity_adapter import FEATURE_FLAG as ANTIGRAVITY_FLAG
from adapters.antigravity_adapter import transform as transform_antigravity
from adapters.base import AdapterEnvelope, adapter_enabled
from adapters.opencode_adapter import FEATURE_FLAG as OPENCODE_FLAG
from adapters.opencode_adapter import transform as transform_opencode


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--adapter", required=True, choices=["antigravity", "opencode"])
    parser.add_argument("--input", required=True)
    return parser.parse_args()


def _load_envelope(path: Path) -> AdapterEnvelope:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return AdapterEnvelope(
        run_id=str(payload["runId"]),
        trigger_id=str(payload["triggerId"]),
        intent=str(payload["intent"]),
        payload=dict(payload.get("payload", {})),
    )


def main() -> int:
    args = parse_args()
    envelope = _load_envelope(Path(args.input).resolve())

    if args.adapter == "antigravity":
        if not adapter_enabled(ANTIGRAVITY_FLAG):
            print("adapter_disabled: antigravity")
            return 2
        result = transform_antigravity(envelope)
    else:
        if not adapter_enabled(OPENCODE_FLAG):
            print("adapter_disabled: opencode")
            return 2
        result = transform_opencode(envelope)

    print(
        json.dumps(
            {
                "adapter": result.adapter,
                "accepted": result.accepted,
                "warnings": result.warnings,
                "output": result.output,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
