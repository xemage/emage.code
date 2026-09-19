#!/usr/bin/env python3
"""Version-consistency gate for emage.code (Gate G0 — Truth).

Parses the canonical "Latest release: vX.Y.Z" marker from README.md (the same marker
string `scripts/verify-release-docs.py` already treats as this repo's canonical version
signal), then scans the rest of the repository's non-archived Markdown files for any
`vX.Y.Z`-shaped version string that is numerically OLDER than that canonical version.

Stale version claims in docs make every downstream inference an agent makes when
reading those docs unreliable, so this script exits non-zero — with a per-file,
per-line report of exactly what was found and where — whenever such drift exists.

Excluded by path prefix (historical-record locations that legitimately reference old
version numbers by design — a release note for v6.0.1 is supposed to say v6.0.1):
    docs/releases/
    docs/checkpoints/
    docs/archiv/
    docs/tasks/
    docs/plans/
    docs/artifacts/
    CHANGELOG.md

A bare `vX.Y.Z` string is only treated as a "current state" claim (and therefore
eligible to be flagged) when it also passes a narrow context gate: it must be either
(a) within roughly 80 characters of a case-insensitive current-state signal phrase
("current release", "latest release", "current state", "release:"), or (b) part of a
markdown link/path targeting `docs/releases/vX.Y.Z.md`. This keeps illustrative semver
examples elsewhere in the docs (branch-naming examples, semver walkthroughs, etc.) from
being flagged as if they were live version claims.

Usage:
    python3 scripts/check-version-consistency.py
    python3 scripts/check-version-consistency.py --root /path/to/repo
    python3 scripts/check-version-consistency.py --marker-file README.md

This script is read-only: it never edits any file, it only reads and reports.

Exit codes:
    0  no version references older than the canonical marker were found
    1  stale version reference(s) found, or the canonical marker could not be parsed
    2  usage/environment error (e.g. the marker file does not exist)
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

MARKER_PREFIX = "Latest release:"

# Matches version strings shaped like vX.Y.Z, with an optional pre-release/build
# suffix (e.g. v6.10.0, v1.2.0-rc1). Word-bounded so it doesn't match inside longer
# tokens.
VERSION_RE = re.compile(r"\bv(\d+)\.(\d+)\.(\d+)(?:-[A-Za-z0-9.]+)?\b")

# Historical-record path prefixes that legitimately reference old version numbers by
# design. Per docs/tasks/task-T400.md and its 2026-08-12 addendum — do not widen or
# narrow without updating that task brief's rationale. docs/tasks/, docs/plans/, and
# docs/artifacts/ were added in the addendum: all three are immutable/append-only
# historical-record conventions per AGENTS.md (task ledger archive, versioned plan
# artifacts, versioned artifacts more broadly), structurally identical to the original
# four exclusions.
EXCLUDED_PREFIXES = (
    "docs/releases/",
    "docs/checkpoints/",
    "docs/archiv/",
    "docs/tasks/",
    "docs/plans/",
    "docs/artifacts/",
    "CHANGELOG.md",
)

# Case-insensitive "current state" signal phrases. A bare version string is only a
# candidate finding if one of these appears within CONTEXT_WINDOW_CHARS of the match
# (measured across the whole file, not just the current line, since a version and its
# introducing phrase can be split across a line wrap — see e.g.
# implementation/README.md's "current release stream\n(**v6.0.1**)").
SIGNAL_PHRASES = (
    "current release",
    "latest release",
    "current state",
    "release:",
)
CONTEXT_WINDOW_CHARS = 80

# A version string embedded in (or immediately adjacent to) a markdown link/path
# targeting a specific docs/releases/vX.Y.Z.md file is always a "current state" claim
# in its own right — it's presenting that release doc as *the* relevant one for this
# context — even with no signal phrase nearby.
RELEASES_LINK_TEMPLATE = "docs/releases/{version}.md"

DEFAULT_ROOT = Path(__file__).resolve().parent.parent


def is_excluded(rel_path: Path) -> bool:
    """True if rel_path (relative to the scan root) falls under an excluded prefix."""
    rel_posix = rel_path.as_posix()
    return any(rel_posix.startswith(prefix) for prefix in EXCLUDED_PREFIXES)


def find_marker_version(marker_text: str) -> tuple[str, tuple[int, int, int]] | None:
    """Return (raw version string, (major, minor, patch)) from a 'Latest release:'
    line, or None if no such line/version is found."""
    for line in marker_text.splitlines():
        stripped = line.strip()
        if not stripped.startswith(MARKER_PREFIX):
            continue
        match = VERSION_RE.search(stripped)
        if match:
            key = (int(match.group(1)), int(match.group(2)), int(match.group(3)))
            return match.group(0), key
    return None


def _is_current_state_claim(text: str, start: int, end: int, version: str) -> bool:
    """True if the version match at text[start:end] passes the "current state" context
    gate: a nearby signal phrase, or participation in a docs/releases/vX.Y.Z.md link."""
    window_start = max(0, start - CONTEXT_WINDOW_CHARS)
    window_end = min(len(text), end + CONTEXT_WINDOW_CHARS)
    window = text[window_start:window_end].lower()
    if any(phrase in window for phrase in SIGNAL_PHRASES):
        return True

    releases_link = RELEASES_LINK_TEMPLATE.format(version=version)
    # A slightly wider window is fine here too — the link text/href pair in a markdown
    # link (`[docs/releases/vX.Y.Z.md`](../docs/releases/vX.Y.Z.md)`) can be a bit
    # longer than the generic signal-phrase window.
    link_window = text[window_start:window_end]
    return releases_link in link_window


def scan_file(path: Path, canonical_key: tuple[int, int, int]) -> list[tuple[int, str]]:
    """Return [(line_number, matched_version_string), ...] for every version string in
    `path` that is numerically older than canonical_key AND passes the "current state"
    context gate (see module docstring / `_is_current_state_claim`)."""
    findings: list[tuple[int, str]] = []
    text = path.read_text(encoding="utf-8", errors="ignore")
    for match in VERSION_RE.finditer(text):
        key = (int(match.group(1)), int(match.group(2)), int(match.group(3)))
        if key >= canonical_key:
            continue
        if not _is_current_state_claim(text, match.start(), match.end(), match.group(0)):
            continue
        line_no = text.count("\n", 0, match.start()) + 1
        findings.append((line_no, match.group(0)))
    return findings


def find_markdown_files(root: Path) -> list[Path]:
    """All non-excluded *.md files under root, skipping .git entirely."""
    files: list[Path] = []
    for path in sorted(root.rglob("*.md")):
        if ".git" in path.parts:
            continue
        rel = path.relative_to(root)
        if is_excluded(rel):
            continue
        files.append(path)
    return files


def scan_repository(
    root: Path, marker_path: Path
) -> tuple[str | None, dict[Path, list[tuple[int, str]]]]:
    """Read-only scan. Returns (canonical_raw_version_or_None, {rel_path: findings})."""
    marker_text = marker_path.read_text(encoding="utf-8", errors="ignore")
    found = find_marker_version(marker_text)
    if found is None:
        return None, {}
    canonical_raw, canonical_key = found

    drift: dict[Path, list[tuple[int, str]]] = {}
    for path in find_markdown_files(root):
        findings = scan_file(path, canonical_key)
        if findings:
            drift[path.relative_to(root)] = findings
    return canonical_raw, drift


def evaluate(
    canonical_raw: str | None, drift: dict[Path, list[tuple[int, str]]]
) -> tuple[int, list[str]]:
    """Pure evaluation. Returns (exit_code, message_lines)."""
    lines: list[str] = []
    if canonical_raw is None:
        lines.append(
            f"version-consistency: could not parse '{MARKER_PREFIX} vX.Y.Z' marker"
        )
        return 1, lines

    if not drift:
        lines.append(
            f"version-consistency: PASS — canonical version is {canonical_raw}; "
            "no older version references found outside the exclusion list"
        )
        return 0, lines

    lines.append(
        f"version-consistency: FAIL — canonical version is {canonical_raw}; "
        "found references to older versions:"
    )
    for rel_path in sorted(drift):
        for line_no, version in drift[rel_path]:
            lines.append(
                f"  {rel_path.as_posix()}:{line_no}: found {version} "
                f"(older than canonical {canonical_raw})"
            )
    return 1, lines


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=DEFAULT_ROOT,
        help="Repository root to scan (default: repo root inferred from this script's location)",
    )
    parser.add_argument(
        "--marker-file",
        type=Path,
        default=Path("README.md"),
        help="Path, relative to --root, containing the canonical "
        "'Latest release: vX.Y.Z' marker (default: README.md)",
    )
    args = parser.parse_args(argv)

    root = args.root.resolve()
    marker_path = root / args.marker_file
    if not marker_path.is_file():
        print(f"version-consistency: marker file not found: {marker_path}", file=sys.stderr)
        return 2

    canonical_raw, drift = scan_repository(root, marker_path)
    exit_code, lines = evaluate(canonical_raw, drift)
    for line in lines:
        print(line)
    print(f"VERSION CONSISTENCY: {'PASS' if exit_code == 0 else 'FAIL'}")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
