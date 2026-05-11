"""Scan tracked files for accidentally committed secrets.

We check tracked files only (via `git ls-files`), so test artifacts under .git/
or local-only files don't trigger.

Patterns intentionally conservative — false positives are noisy. Add a
specific exclusion via SECRET_SCAN_ALLOWLIST below if a hit is a known false
positive (always justify in the MR description).
"""
from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path

from tests._helpers.repo import repo_root


# (regex, label)
PATTERNS = [
    (re.compile(r"glpat-[A-Za-z0-9_-]{20,}"), "GitLab Personal Access Token"),
    (re.compile(r"gloas-[A-Za-z0-9_-]{20,}"), "GitLab OAuth token"),
    (re.compile(r"glprt-[A-Za-z0-9_-]{20,}"), "GitLab Project Access Token"),
    (re.compile(r"ghp_[A-Za-z0-9]{36,}"), "GitHub Personal Access Token"),
    (re.compile(r"gho_[A-Za-z0-9]{36,}"), "GitHub OAuth token"),
    (re.compile(r"AKIA[0-9A-Z]{16}"), "AWS Access Key ID"),
    (re.compile(r"sk-[A-Za-z0-9]{32,}"), "OpenAI / Anthropic-style secret key"),
    (re.compile(r"-----BEGIN (RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"), "Private key"),
    (re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}"), "Slack token"),
    (re.compile(r"AIza[A-Za-z0-9_-]{35}"), "Google API key"),
]

# Files whose content is allowed to mention these patterns (e.g. test files
# that intentionally search for them). Use forward-slash relative paths.
ALLOWLIST = {
    "tests/functional/test_secret_scan.py",
    # v1 docs contain example placeholder tokens (`glpat-xxxxxxxxxxxxxxxxxxxx`
    # etc.). v1 is frozen — we don't edit it, but the placeholders are clearly
    # not real secrets.
    "v1/implementation/.opencode/QUICKSTART.md",
}


def _tracked_files() -> list[Path]:
    proc = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=repo_root(), capture_output=True, check=True,
    )
    return [
        repo_root() / name.decode("utf-8")
        for name in proc.stdout.split(b"\x00")
        if name
    ]


def _is_text(path: Path) -> bool:
    try:
        with path.open("rb") as fh:
            chunk = fh.read(2048)
        if b"\x00" in chunk:
            return False
        chunk.decode("utf-8")
        return True
    except (UnicodeDecodeError, FileNotFoundError, PermissionError):
        return False


class TestSecretScan(unittest.TestCase):
    def test_no_secrets_in_tracked_files(self):
        findings: list[str] = []
        for path in _tracked_files():
            rel = str(path.relative_to(repo_root())).replace("\\", "/")
            if rel in ALLOWLIST:
                continue
            if not path.is_file() or not _is_text(path):
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except (FileNotFoundError, PermissionError):
                continue
            for regex, label in PATTERNS:
                m = regex.search(text)
                if m:
                    findings.append(f"{rel}: {label} matched ({m.group(0)[:12]}…)")
        self.assertFalse(
            findings,
            msg=(
                "Potential secrets found in tracked files:\n  "
                + "\n  ".join(findings)
                + "\n\nIf one of these is a known false positive, add the path "
                "to ALLOWLIST in tests/functional/test_secret_scan.py and "
                "justify it in the MR description."
            ),
        )


if __name__ == "__main__":
    unittest.main()
