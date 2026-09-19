#!/usr/bin/env python3
"""expect.py for new-feature-real-artifact-versioning-drift (known_failing / tracked_defect).

Contract under test: implementation/knowledge/commands/new-feature.md Phase 3 step 8 --
artifact filenames must match "<artifact-name>-v<major>.<minor>.md". Checked against two real
docs/artifacts/*.md files. Expected to return False today -- see brief.md.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

VERSIONED_NAME_RE = re.compile(r"^.+-v\d+\.\d+\.md$")


def check(case_dir: Path) -> bool:
    artifacts_dir = case_dir / "fixture" / "docs" / "artifacts"
    if not artifacts_dir.is_dir():
        return False
    candidates = sorted(artifacts_dir.glob("*.md"))
    if len(candidates) < 2:
        return False
    return all(VERSIONED_NAME_RE.match(f.name) for f in candidates)


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} <case_dir>", file=sys.stderr)
        return 2
    return 0 if check(Path(sys.argv[1]).resolve()) else 1


if __name__ == "__main__":
    sys.exit(main())
