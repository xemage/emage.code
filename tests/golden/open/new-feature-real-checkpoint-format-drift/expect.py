#!/usr/bin/env python3
"""expect.py for new-feature-real-checkpoint-format-drift.

Contract under test: implementation/knowledge/commands/new-feature.md Phase 3 step 7 -- the
checkpoint written after implementation completes must follow `AGENTS.md` § Checkpoint Protocol:
stored at docs/checkpoints/checkpoint-<SEQ>-<phase>.md, and containing the five elements
`AGENTS.md` itself names, in the order it names them: completed tasks, key decisions, blockers,
token metrics, next steps.

The required-element list is derived from `AGENTS.md` § Checkpoint Protocol ("Include: completed
tasks, key decisions, blockers, token metrics, next steps"), NOT from
docs/checkpoints/_template.md's full heading set -- the template carries sections (`## Phase
summary`, `## Maturity distribution`) that `AGENTS.md` does not mandate and that pre-T437
checkpoints do not have.

Applied here to a real checkpoint from this repo's history
(docs/checkpoints/checkpoint-017-t417-harbor-oracle-smoke-complete.md). Its hand-authored sibling
new-feature-checkpoint-line-compliant runs the identical check against a hand-authored checkpoint.

See docs/artifacts/golden-suite-format-v1.md §4 for the check(case_dir) -> bool contract.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

# `AGENTS.md` § Checkpoint Protocol: `docs/checkpoints/checkpoint-<SEQ>-<phase>.md`.
FILENAME_RE = re.compile(r"^checkpoint-\d+-[A-Za-z0-9][A-Za-z0-9._-]*\.md$")

# The five elements `AGENTS.md` § Checkpoint Protocol names, in the order it names them. Each
# heading regex tolerates a qualifier ("## Blockers (active)", "## Completed tasks (this phase)")
# but still requires the named element to be present as its own section.
REQUIRED_ELEMENTS = [
    ("completed tasks", re.compile(r"^#{2,6} +.*\bcompleted tasks\b.*$", re.IGNORECASE | re.MULTILINE)),
    ("key decisions", re.compile(r"^#{2,6} +.*\bkey decisions\b.*$", re.IGNORECASE | re.MULTILINE)),
    ("blockers", re.compile(r"^#{2,6} +.*\bblockers?\b.*$", re.IGNORECASE | re.MULTILINE)),
    (
        "token metrics",
        re.compile(r"^#{2,6} +.*\btoken (?:metrics|usage|budget)\b.*$", re.IGNORECASE | re.MULTILINE),
    ),
    ("next steps", re.compile(r"^#{2,6} +.*\bnext steps\b.*$", re.IGNORECASE | re.MULTILINE)),
]

ANY_HEADING_RE = re.compile(r"^#{1,6} +\S.*$", re.MULTILINE)


def _section_body(text: str, heading_end: int) -> str:
    """Text between the end of a heading line and the start of the next heading (or EOF)."""
    nxt = ANY_HEADING_RE.search(text, heading_end)
    return text[heading_end : nxt.start()] if nxt else text[heading_end:]


def check(case_dir: Path) -> bool:
    """True iff exactly one checkpoint fixture exists, its filename follows `AGENTS.md`'s
    checkpoint-<SEQ>-<phase>.md convention, and it carries all five `AGENTS.md`-mandated
    elements as non-empty sections, in the declared order."""
    ckpt_dir = case_dir / "fixture" / "docs" / "checkpoints"
    if not ckpt_dir.is_dir():
        return False
    candidates = sorted(ckpt_dir.glob("*.md"))
    if len(candidates) != 1:
        return False
    if not FILENAME_RE.match(candidates[0].name):
        return False
    text = candidates[0].read_text(encoding="utf-8")

    positions: list[int] = []
    for _name, pattern in REQUIRED_ELEMENTS:
        match = pattern.search(text)
        if match is None:
            return False
        if not _section_body(text, match.end()).strip():
            return False
        positions.append(match.start())

    return positions == sorted(positions)


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} <case_dir>", file=sys.stderr)
        return 2
    return 0 if check(Path(sys.argv[1]).resolve()) else 1


if __name__ == "__main__":
    sys.exit(main())
