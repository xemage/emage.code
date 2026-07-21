"""Ensure key docs reference valid instruction file paths."""

from __future__ import annotations

import re
import unittest
from pathlib import Path

from tests._helpers.repo import repo_root


CODE_SPAN_RE = re.compile(r"`([^`]+)`")
INSTRUCTION_PATH_RE = re.compile(r"(?:^|/)(?:instructions/[^\s`]+\.md)")


class TestInstructionReferenceIntegrity(unittest.TestCase):
    def test_key_docs_instruction_paths_exist(self) -> None:
        targets = [
            Path("AGENTS.md"),
            Path("implementation/AGENTS.md"),
            Path("implementation/SECURITY.md"),
        ]

        missing: list[str] = []
        root = repo_root()

        for rel in targets:
            text = (root / rel).read_text(encoding="utf-8", errors="ignore")
            for code_span in CODE_SPAN_RE.findall(text):
                if not INSTRUCTION_PATH_RE.search(code_span):
                    continue

                candidate_root = (root / code_span).resolve()
                candidate_file_relative = (root / rel.parent / code_span).resolve()
                if not candidate_root.exists() and not candidate_file_relative.exists():
                    missing.append(f"{rel}: {code_span}")

        self.assertFalse(
            missing,
            msg="Broken instruction references:\n  " + "\n  ".join(missing),
        )


if __name__ == "__main__":
    unittest.main()
