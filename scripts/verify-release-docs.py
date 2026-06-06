#!/usr/bin/env python3
"""Release documentation verification gate for emage.code.

Checks that required documentation exists, includes the current release marker,
contains key usage sections, and has resolvable local/internal links.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

MARKER_FILES = [
    Path("README.md"),
    Path("docs/wiki/README.md"),
    Path("docs/wiki/home.md"),
]

def release_brief_path(tag: str) -> Path:
    return Path("docs/releases") / f"{tag}.md"


REQUIRED_FILES = [
    Path("README.md"),
    Path("CONTRIBUTING.md"),
    Path("docs/wiki/README.md"),
    Path("docs/wiki/home.md"),
    Path("docs/wiki/quick-start.md"),
    Path("docs/wiki/agents-overview.md"),
    Path("docs/wiki/implementation-guide.md"),
    Path("implementation/README.md"),
    Path("scripts/install.sh"),
    Path("docs/releases/_template.md"),
]

SECTION_REQUIREMENTS: dict[Path, list[str]] = {
    Path("README.md"): [
        "## Install",
        "## Quick start",
        "## Use emage.code in practice",
        "## Documentation release contract",
        "### Implementation",
        "scripts/install.sh",
        "docs/releases/",
    ],
    Path("CONTRIBUTING.md"): [
        "## Releasing",
        "### Cutting a release",
        "## Working with implementation",
        "release-docs-gate",
        "verify-release-docs.py",
    ],
    Path("docs/wiki/home.md"): [
        "## Wiki contents",
        "## Project links",
        "implementation-guide",
    ],
    Path("docs/wiki/quick-start.md"): [
        "## 1. Install",
        "## 4. Invoke the orchestrator",
        "/new-project",
        "scripts/install.sh",
    ],
    Path("docs/wiki/README.md"): [
        "## Sync to live Wiki",
        "## Release documentation contract",
        "implementation-guide",
    ],
    Path("docs/wiki/agents-overview.md"): [
        "## v3 note",
        "schema-first runtime model",
    ],
    Path("docs/wiki/implementation-guide.md"): [
        "## Validate",
        "python3 implementation/scripts/check-v3.py",
        "node implementation/scripts/verify-v3.mjs",
        "scripts/install.sh",
    ],
    Path("implementation/README.md"): [
        "## Install",
        "## Validation commands",
        "## Package workflow",
        "## Trigger workflow",
        "## Adapter smoke workflow",
    ],
}

FENCED_CODE_RE = re.compile(r"```.*?```", re.DOTALL)
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def normalize_target(current_file: Path, raw_target: str) -> Path | None:
    target = raw_target.strip()
    if not target:
        return None
    if target.startswith(("http://", "https://", "mailto:", "#", "tel:")):
        return None

    target = target.split("#", 1)[0].split("?", 1)[0].strip()
    if not target:
        return None

    # Wiki slug links such as [Quick Start](quick-start)
    if current_file.parts[:2] == ("docs", "wiki"):
        if "/" not in target and not target.endswith(".md"):
            return ROOT / "docs" / "wiki" / f"{target}.md"

    return (ROOT / current_file.parent / target).resolve()


def strip_code(text: str) -> str:
    text = FENCED_CODE_RE.sub("", text)
    return INLINE_CODE_RE.sub("", text)


def check_links(file_path: Path, errors: list[str]) -> None:
    text = file_path.read_text(encoding="utf-8", errors="ignore")
    visible_text = strip_code(text)

    rel = file_path.relative_to(ROOT)
    for match in LINK_RE.finditer(visible_text):
        raw_target = match.group(1)
        normalized = normalize_target(rel, raw_target)
        if normalized is None:
            continue
        if not normalized.exists():
            errors.append(f"broken link in {rel}: {raw_target}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", required=True, help="Release tag, e.g. v1.0.1")
    args = parser.parse_args()

    marker = f"Latest release: {args.tag}"
    errors: list[str] = []

    release_brief = release_brief_path(args.tag)
    required_for_tag = [*REQUIRED_FILES, release_brief]

    for relative in required_for_tag:
        absolute = ROOT / relative
        if not absolute.is_file():
            errors.append(f"missing required file: {relative}")

    if errors:
        for error in errors:
            print(f"release-docs-verify: {error}")
        return 1

    for relative in MARKER_FILES:
        text = (ROOT / relative).read_text(encoding="utf-8", errors="ignore")
        if marker not in text:
            errors.append(f"missing marker '{marker}' in {relative}")

    for relative, required_snippets in SECTION_REQUIREMENTS.items():
        text = (ROOT / relative).read_text(encoding="utf-8", errors="ignore")
        for snippet in required_snippets:
            if snippet not in text:
                errors.append(f"missing required content in {relative}: {snippet}")

    brief_text = (ROOT / release_brief).read_text(encoding="utf-8", errors="ignore")
    for snippet in ("## Install", "## Highlights", f"Latest release: {args.tag}"):
        if snippet not in brief_text:
            errors.append(f"missing required content in {release_brief}: {snippet}")

    for relative in required_for_tag:
        check_links(ROOT / relative, errors)

    if errors:
        for error in errors:
            print(f"release-docs-verify: {error}")
        return 1

    print("release-docs-verify: all documentation checks passed")
    print(f"release-docs-verify: verified marker '{marker}'")
    return 0


if __name__ == "__main__":
    sys.exit(main())
