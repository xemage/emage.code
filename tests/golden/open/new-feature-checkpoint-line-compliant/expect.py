#!/usr/bin/env python3
"""expect.py for new-feature-checkpoint-line-compliant.

Contract under test: implementation/knowledge/commands/new-feature.md Phase 3 step 7 -- a
"[CHECKPOINT] id=feature-<slug> | done=[...] | in_flight=[...] | blocked=[...] |
artifact_refs=[...] | next=[...]" line in docs/checkpoints/checkpoint-feature-<slug>.md.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REQUIRED_KEYS = ["done", "in_flight", "blocked", "artifact_refs", "next"]
LINE_RE = re.compile(r"^\[CHECKPOINT\]\s+id=feature-\S+.*$", re.MULTILINE)


def check(case_dir: Path) -> bool:
    ckpt_dir = case_dir / "fixture" / "docs" / "checkpoints"
    if not ckpt_dir.is_dir():
        return False
    candidates = sorted(ckpt_dir.glob("checkpoint-feature-*.md"))
    if len(candidates) != 1:
        return False
    text = candidates[0].read_text(encoding="utf-8")

    match = LINE_RE.search(text)
    if not match:
        return False
    line = match.group(0)

    return all(re.search(rf"\b{re.escape(key)}=", line) for key in REQUIRED_KEYS)


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} <case_dir>", file=sys.stderr)
        return 2
    return 0 if check(Path(sys.argv[1]).resolve()) else 1


if __name__ == "__main__":
    sys.exit(main())
