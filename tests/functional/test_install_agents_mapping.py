"""Validate installer rewrites AGENTS.md to platform-correct paths."""

from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from tests._helpers.repo import repo_root


class TestInstallAgentsMapping(unittest.TestCase):
    def _run_install(self, target: Path, platform: str) -> str:
        installer = repo_root() / "scripts" / "install.sh"
        subprocess.run(
            ["bash", str(installer), "--target", str(target), "--platform", platform],
            check=True,
            cwd=str(repo_root()),
        )
        return (target / "AGENTS.md").read_text(encoding="utf-8")

    def test_github_install_rewrites_agents_paths(self) -> None:
        with tempfile.TemporaryDirectory(prefix="emage-install-gh-") as tmp:
            content = self._run_install(Path(tmp), "github")

        self.assertIn("`.github/skills/`", content)
        self.assertIn("`.github/instructions/coding-standards.instructions.md`", content)
        self.assertIn("`.github/instructions/security-guidelines.instructions.md`", content)
        self.assertIn("`.vscode/mcp.json`", content)

    def test_cursor_install_rewrites_agents_paths(self) -> None:
        with tempfile.TemporaryDirectory(prefix="emage-install-cursor-") as tmp:
            content = self._run_install(Path(tmp), "cursor")

        self.assertIn("`.cursor/skills/`", content)
        self.assertIn("`.cursor/rules/coding-standards.mdc`", content)
        self.assertIn("`.cursor/rules/security-guidelines.mdc`", content)
        self.assertIn("`.cursor/mcp.json`", content)

    def test_claude_code_install_rewrites_agents_paths(self) -> None:
        with tempfile.TemporaryDirectory(prefix="emage-install-claude-") as tmp:
            content = self._run_install(Path(tmp), "claude-code")

        self.assertIn("`.claude/skills/`", content)
        self.assertIn("`.claude/rules/coding-standards.md`", content)
        self.assertIn("`.claude/rules/security-guidelines.md`", content)
        self.assertIn("`.mcp.json`", content)

    def test_all_platform_install_includes_projection_map(self) -> None:
        with tempfile.TemporaryDirectory(prefix="emage-install-all-") as tmp:
            content = self._run_install(Path(tmp), "all")

        self.assertIn("`.github/skills/`", content)
        self.assertIn("`.cursor/skills/`", content)
        self.assertIn("`.gemini/skills/`", content)
        self.assertIn("`.opencode/skills/`", content)
        self.assertIn("`.pi/skills/`", content)
        self.assertIn("`.claude/skills/`", content)
        self.assertIn("`.vscode/mcp.json`", content)
        self.assertIn("`.gemini/settings.json`", content)
        self.assertIn("`.opencode/opencode.json`", content)


if __name__ == "__main__":
    unittest.main()
