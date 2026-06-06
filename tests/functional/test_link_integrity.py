"""Markdown link integrity (mirrors the CI lint stage but as a unit test).

Strips fenced + inline code spans before checking, so example markdown links
inside code don't trigger false positives.
"""
from __future__ import annotations

import os
import re
import unittest
from pathlib import Path

from tests._helpers.repo import repo_root


# Skip these path segments entirely
SKIP_PARTS = ("node_modules", ".vscode-server", "archive", "wiki")
# Skip archive/ (frozen releases) and docs/wiki/ (GitLab slug links)
def _is_skipped(path: Path) -> bool:
    rel = path.relative_to(repo_root())
    parts = rel.parts
    if "node_modules" in parts:
        return True
    if parts and parts[0] == "archive":
        return True
    if len(parts) >= 2 and parts[0] == "docs" and parts[1] == "wiki":
        return True
    # Root-level platform mirror dirs are downstream copies of the canonical
    # mirrors under archive/v2/implementation/. Auditing them would just duplicate
    # findings against the source-of-truth mirrors. Skip.
    if parts and parts[0] in {".github", ".gemini", ".opencode", ".cursor"}:
        return True
    return False


LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
FENCE_RE = re.compile(r"```.*?```", re.DOTALL)
INLINE_RE = re.compile(r"`[^`\n]*`")


def _broken_links() -> list[tuple[str, str]]:
    broken: list[tuple[str, str]] = []
    for md in repo_root().rglob("*.md"):
        if _is_skipped(md):
            continue
        text = md.read_text(encoding="utf-8", errors="ignore")
        text = FENCE_RE.sub("", text)
        text = INLINE_RE.sub("", text)
        base = md.parent
        for m in LINK_RE.finditer(text):
            target = m.group(2).strip()
            if target.startswith(("http://", "https://", "mailto:", "#", "tel:")):
                continue
            clean = target.split("#")[0].split("?")[0]
            if not clean:
                continue
            full = (base / clean).resolve()
            if not full.exists():
                broken.append((str(md.relative_to(repo_root())), target))
    return broken


class TestLinkIntegrity(unittest.TestCase):
    def test_no_broken_intra_repo_markdown_links(self):
        broken = _broken_links()
        self.assertFalse(
            broken,
            msg="Broken markdown links:\n  " + "\n  ".join(f"{f} -> {t}" for f, t in broken),
        )


if __name__ == "__main__":
    unittest.main()
