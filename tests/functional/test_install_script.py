"""Functional tests for scripts/install.sh."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tests._helpers.repo import repo_root


class TestInstallScript(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bash = shutil.which("bash")
        if not cls.bash:
            raise unittest.SkipTest("bash not available on PATH")

    def _run_install(self, target: Path, platform: str = "pi", update: bool = False) -> subprocess.CompletedProcess[str]:
        args = [
            self.bash,
            str(repo_root() / "scripts" / "install.sh"),
            "--target",
            str(target),
            "--platform",
            platform,
        ]
        if update:
            args.append("--update")
        return subprocess.run(
            args,
            cwd=repo_root(),
            capture_output=True,
            text=True,
            check=False,
        )

    def test_install_merges_into_existing_platform_and_docs_dirs(self):
        implementation_pi = repo_root() / "implementation" / ".pi"

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            target.mkdir()
            (target / ".pi").mkdir()
            (target / "docs").mkdir()
            (target / ".pi" / "keep-pi.txt").write_text("existing", encoding="utf-8")
            (target / "docs" / "keep-docs.txt").write_text("existing", encoding="utf-8")

            proc = self._run_install(target, platform="pi")
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

            self.assertFalse(
                (target / ".pi" / ".pi").exists(),
                "install must not nest platform files under .pi/.pi",
            )
            self.assertFalse(
                (target / "docs" / "docs").exists(),
                "install must not nest docs under docs/docs",
            )
            self.assertTrue((target / ".pi" / "keep-pi.txt").is_file())
            self.assertTrue((target / "docs" / "keep-docs.txt").is_file())
            self.assertTrue((target / "AGENTS.md").is_file())

            # Sanity: installed tree contains at least one file from implementation/.pi
            installed_names = {p.name for p in implementation_pi.rglob("*") if p.is_file()}
            copied_names = {p.name for p in (target / ".pi").rglob("*") if p.is_file()}
            self.assertTrue(
                installed_names & copied_names,
                "expected install to copy files from implementation/.pi into target/.pi",
            )

    def test_update_requires_existing_install(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            target.mkdir()

            proc = self._run_install(target, platform="pi", update=True)
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("AGENTS.md", proc.stderr)

    def test_update_removes_stale_platform_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            target.mkdir()
            (target / "AGENTS.md").write_text("# existing", encoding="utf-8")
            (target / ".pi").mkdir()
            (target / ".pi" / "stale-agent.md").write_text("remove me", encoding="utf-8")

            proc = self._run_install(target, platform="pi", update=True)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertFalse((target / ".pi" / "stale-agent.md").exists())
            self.assertIn("Updated emage.code", proc.stdout)

    def test_update_preserves_merged_docs(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            target.mkdir()
            (target / "AGENTS.md").write_text("# existing", encoding="utf-8")
            (target / "docs").mkdir()
            (target / "docs" / "custom-task.md").write_text("keep me", encoding="utf-8")

            proc = self._run_install(target, platform="pi", update=True)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertTrue((target / "docs" / "custom-task.md").is_file())

    def test_update_preserves_task_ledger_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            target.mkdir()
            (target / "AGENTS.md").write_text("# existing", encoding="utf-8")
            tasks = target / "docs" / "tasks"
            tasks.mkdir(parents=True)
            (tasks / "completed-tasks.md").write_text(
                "\n".join(
                    [
                        "# Completed Tasks",
                        "",
                        "Append-only log.",
                        "",
                        "| ID | Title | Owner | Done on | Outcome / artifact |",
                        "|----|-------|-------|---------|--------------------|",
                        "| T042 | CI gates | devops-engineer | 2026-05-24 | .gitlab-ci.yml |",
                        "",
                    ]
                ),
                encoding="utf-8",
            )
            (tasks / "active-tasks.md").write_text(
                "\n".join(
                    [
                        "# Active Tasks",
                        "",
                        "| ID | Title | Owner | Status | Priority | Depends on | Last update |",
                        "|----|-------|-------|--------|----------|-----------|-------------|",
                        "| T099 | Open item | orchestrator | in_progress | P0 | — | 2026-06-12 |",
                        "",
                        "> Keep this note.",
                    ]
                ),
                encoding="utf-8",
            )

            proc = self._run_install(target, platform="pi", update=True)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

            completed = (tasks / "completed-tasks.md").read_text(encoding="utf-8")
            active = (tasks / "active-tasks.md").read_text(encoding="utf-8")
            self.assertIn("| T042 | CI gates |", completed)
            self.assertIn("| T099 | Open item |", active)
            self.assertIn("Append-only log. Entries move here", completed)
            self.assertIn("Per-task briefs live alongside", active)
            self.assertNotIn("> Keep this note.", active)

    def test_claude_code_install_places_root_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            target.mkdir()

            proc = self._run_install(target, platform="claude-code")
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertTrue((target / "CLAUDE.md").is_file())
            self.assertTrue((target / ".mcp.json").is_file())
            self.assertTrue((target / ".claude" / "agents").is_dir())

    # -- .vscode/mcp.json (github) / .mcp.json (claude-code) merge-on-update --

    def test_fresh_install_plain_copies_mcp_json(self):
        """Baseline: a non-`--update` install must byte-for-byte copy the
        generated MCP JSON file rather than merging (nothing to merge with, no
        dest file exists yet)."""
        implementation_vscode_mcp = repo_root() / "implementation" / ".vscode" / "mcp.json"
        implementation_root_mcp = repo_root() / "implementation" / ".mcp.json"

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            target.mkdir()
            proc = self._run_install(target, platform="github")
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            installed = (target / ".vscode" / "mcp.json").read_text(encoding="utf-8")
            source = implementation_vscode_mcp.read_text(encoding="utf-8")
            self.assertEqual(
                installed,
                source,
                "fresh (non --update) install must plain-copy .vscode/mcp.json byte-for-byte",
            )

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            target.mkdir()
            proc = self._run_install(target, platform="claude-code")
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            installed = (target / ".mcp.json").read_text(encoding="utf-8")
            source = implementation_root_mcp.read_text(encoding="utf-8")
            self.assertEqual(
                installed,
                source,
                "fresh (non --update) install must plain-copy .mcp.json byte-for-byte",
            )

    def test_update_preserves_unknown_mcp_server_key_github(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            target.mkdir()

            proc = self._run_install(target, platform="github")
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

            mcp_path = target / ".vscode" / "mcp.json"
            self.assertTrue(mcp_path.is_file())
            data = json.loads(mcp_path.read_text(encoding="utf-8"))
            data["servers"]["my-custom-server"] = {"url": "https://example.invalid/mcp"}
            data["inputs"] = [
                {
                    "id": "fake_token",
                    "type": "promptString",
                    "description": "Synthetic test placeholder, not a real credential",
                    "password": True,
                }
            ]
            mcp_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

            proc2 = self._run_install(target, platform="github", update=True)
            self.assertEqual(proc2.returncode, 0, proc2.stdout + proc2.stderr)

            updated = json.loads(mcp_path.read_text(encoding="utf-8"))
            self.assertEqual(
                updated["servers"].get("my-custom-server"),
                {"url": "https://example.invalid/mcp"},
                "unknown pre-existing server key must survive --update merge",
            )
            self.assertEqual(
                updated.get("inputs"),
                [
                    {
                        "id": "fake_token",
                        "type": "promptString",
                        "description": "Synthetic test placeholder, not a real credential",
                        "password": True,
                    }
                ],
                "unknown top-level key ('inputs') must survive --update merge",
            )

    def test_update_refreshes_generator_known_mcp_keys_github(self):
        implementation_mcp = repo_root() / "implementation" / ".vscode" / "mcp.json"
        source_context7 = json.loads(implementation_mcp.read_text(encoding="utf-8"))["servers"]["context7"]

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            target.mkdir()

            proc = self._run_install(target, platform="github")
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

            mcp_path = target / ".vscode" / "mcp.json"
            data = json.loads(mcp_path.read_text(encoding="utf-8"))
            # Corrupt a generator-known key so a successful --update proves the
            # merge actually refreshes it, rather than just leaving dest as-is.
            data["servers"]["context7"] = {"type": "http", "url": "https://stale.example.invalid/mcp"}
            mcp_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

            proc2 = self._run_install(target, platform="github", update=True)
            self.assertEqual(proc2.returncode, 0, proc2.stdout + proc2.stderr)

            updated = json.loads(mcp_path.read_text(encoding="utf-8"))
            self.assertEqual(
                updated["servers"]["context7"],
                source_context7,
                "generator-known server key must be refreshed to match the generated source on --update",
            )

    def test_update_preserves_unknown_mcp_server_key_claude_code(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            target.mkdir()

            proc = self._run_install(target, platform="claude-code")
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

            mcp_path = target / ".mcp.json"
            self.assertTrue(mcp_path.is_file())
            data = json.loads(mcp_path.read_text(encoding="utf-8"))
            data["mcpServers"]["my-custom-server"] = {"url": "https://example.invalid/mcp"}
            data["inputs"] = [
                {
                    "id": "fake_token",
                    "type": "promptString",
                    "description": "Synthetic test placeholder, not a real credential",
                    "password": True,
                }
            ]
            mcp_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

            proc2 = self._run_install(target, platform="claude-code", update=True)
            self.assertEqual(proc2.returncode, 0, proc2.stdout + proc2.stderr)

            updated = json.loads(mcp_path.read_text(encoding="utf-8"))
            self.assertEqual(
                updated["mcpServers"].get("my-custom-server"),
                {"url": "https://example.invalid/mcp"},
                "unknown pre-existing server key must survive --update merge",
            )
            self.assertEqual(
                updated.get("inputs"),
                [
                    {
                        "id": "fake_token",
                        "type": "promptString",
                        "description": "Synthetic test placeholder, not a real credential",
                        "password": True,
                    }
                ],
                "unknown top-level key ('inputs') must survive --update merge",
            )

    def test_update_refreshes_generator_known_mcp_keys_claude_code(self):
        implementation_mcp = repo_root() / "implementation" / ".mcp.json"
        source_context7 = json.loads(implementation_mcp.read_text(encoding="utf-8"))["mcpServers"]["context7"]

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            target.mkdir()

            proc = self._run_install(target, platform="claude-code")
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

            mcp_path = target / ".mcp.json"
            data = json.loads(mcp_path.read_text(encoding="utf-8"))
            # Corrupt a generator-known key so a successful --update proves the
            # merge actually refreshes it, rather than just leaving dest as-is.
            data["mcpServers"]["context7"] = {"type": "http", "url": "https://stale.example.invalid/mcp"}
            mcp_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

            proc2 = self._run_install(target, platform="claude-code", update=True)
            self.assertEqual(proc2.returncode, 0, proc2.stdout + proc2.stderr)

            updated = json.loads(mcp_path.read_text(encoding="utf-8"))
            self.assertEqual(
                updated["mcpServers"]["context7"],
                source_context7,
                "generator-known server key must be refreshed to match the generated source on --update",
            )

    # -- .cursor/mcp.json / .gemini/settings.json / .opencode/opencode.json /
    #    .pi/mcp.json / .cline/mcp.json merge-on-update (T377) --

    def test_cursor_mcp_json_merge_on_update(self):
        implementation_mcp = repo_root() / "implementation" / ".cursor" / "mcp.json"
        source_data = json.loads(implementation_mcp.read_text(encoding="utf-8"))
        source_context7 = source_data["mcpServers"]["context7"]

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            target.mkdir()

            # (a) fresh install: byte-identical plain copy
            proc = self._run_install(target, platform="cursor")
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            mcp_path = target / ".cursor" / "mcp.json"
            self.assertEqual(
                mcp_path.read_text(encoding="utf-8"),
                implementation_mcp.read_text(encoding="utf-8"),
                "fresh (non --update) install must plain-copy .cursor/mcp.json byte-for-byte",
            )

            # inject an unknown server key + corrupt a generator-known key
            data = json.loads(mcp_path.read_text(encoding="utf-8"))
            data["mcpServers"]["my-custom-server"] = {"url": "https://example.invalid/mcp"}
            data["mcpServers"]["context7"] = {"url": "https://stale.example.invalid/mcp"}
            mcp_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

            # (d) a stale non-MCP file elsewhere in the same tree
            stale = target / ".cursor" / "stale-agent-that-should-be-deleted.md"
            stale.write_text("remove me", encoding="utf-8")

            proc2 = self._run_install(target, platform="cursor", update=True)
            self.assertEqual(proc2.returncode, 0, proc2.stdout + proc2.stderr)

            updated = json.loads(mcp_path.read_text(encoding="utf-8"))
            # (b) unknown key survives
            self.assertEqual(
                updated["mcpServers"].get("my-custom-server"),
                {"url": "https://example.invalid/mcp"},
                "unknown pre-existing server key must survive --update merge",
            )
            # (c) generator-known key refreshed
            self.assertEqual(
                updated["mcpServers"]["context7"],
                source_context7,
                "generator-known server key must be refreshed to match the generated source on --update",
            )
            # (d) stale non-MCP file in the same tree still correctly deleted —
            # proves the exclude is scoped to exactly mcp.json, not the whole tree
            self.assertFalse(
                stale.exists(),
                "--update must still stale-clean the rest of .cursor/ via rsync --delete; "
                "only mcp.json is exempted",
            )

    def test_gemini_settings_json_merge_on_update(self):
        implementation_mcp = repo_root() / "implementation" / ".gemini" / "settings.json"
        source_data = json.loads(implementation_mcp.read_text(encoding="utf-8"))
        source_context7 = source_data["mcpServers"]["context7"]

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            target.mkdir()

            # (a) fresh install: byte-identical plain copy
            proc = self._run_install(target, platform="gemini")
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            mcp_path = target / ".gemini" / "settings.json"
            self.assertEqual(
                mcp_path.read_text(encoding="utf-8"),
                implementation_mcp.read_text(encoding="utf-8"),
                "fresh (non --update) install must plain-copy .gemini/settings.json byte-for-byte",
            )

            # inject an unknown server key + corrupt a generator-known key
            # (gemini's context7 entry uses "httpUrl", not "url" — corrupt the
            # actual key present in the generated shape so the merge's
            # per-key "source wins on scalar leaves" rule fully overwrites it,
            # rather than leaving a stray "url" key the recursive merge would
            # otherwise correctly treat as unrelated dest-only content)
            data = json.loads(mcp_path.read_text(encoding="utf-8"))
            data["mcpServers"]["my-custom-server"] = {"url": "https://example.invalid/mcp"}
            data["mcpServers"]["context7"] = {"httpUrl": "https://stale.example.invalid/mcp"}
            mcp_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

            # (d) a stale non-MCP file elsewhere in the same tree
            stale = target / ".gemini" / "stale-agent-that-should-be-deleted.md"
            stale.write_text("remove me", encoding="utf-8")

            proc2 = self._run_install(target, platform="gemini", update=True)
            self.assertEqual(proc2.returncode, 0, proc2.stdout + proc2.stderr)

            updated = json.loads(mcp_path.read_text(encoding="utf-8"))
            # (b) unknown key survives
            self.assertEqual(
                updated["mcpServers"].get("my-custom-server"),
                {"url": "https://example.invalid/mcp"},
                "unknown pre-existing server key must survive --update merge",
            )
            # (c) generator-known key refreshed
            self.assertEqual(
                updated["mcpServers"]["context7"],
                source_context7,
                "generator-known server key must be refreshed to match the generated source on --update",
            )
            # (d) stale non-MCP file in the same tree still correctly deleted —
            # proves the exclude is scoped to exactly settings.json, not the whole tree
            self.assertFalse(
                stale.exists(),
                "--update must still stale-clean the rest of .gemini/ via rsync --delete; "
                "only settings.json is exempted",
            )
            # gemini-specific: sibling non-MCP 'hooks' key must survive untouched
            self.assertEqual(
                updated.get("hooks"),
                source_data.get("hooks"),
                "gemini's non-MCP 'hooks' key must be unaffected by the mcpServers merge",
            )

    def test_opencode_opencode_json_merge_on_update(self):
        implementation_mcp = repo_root() / "implementation" / ".opencode" / "opencode.json"
        source_data = json.loads(implementation_mcp.read_text(encoding="utf-8"))
        source_context7 = source_data["mcp"]["context7"]

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            target.mkdir()

            # (a) fresh install: byte-identical plain copy
            proc = self._run_install(target, platform="opencode")
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            mcp_path = target / ".opencode" / "opencode.json"
            self.assertEqual(
                mcp_path.read_text(encoding="utf-8"),
                implementation_mcp.read_text(encoding="utf-8"),
                "fresh (non --update) install must plain-copy .opencode/opencode.json byte-for-byte",
            )

            # inject an unknown server key + corrupt a generator-known key
            data = json.loads(mcp_path.read_text(encoding="utf-8"))
            data["mcp"]["my-custom-server"] = {"url": "https://example.invalid/mcp"}
            data["mcp"]["context7"] = {"url": "https://stale.example.invalid/mcp"}
            mcp_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

            # (d) a stale non-MCP file elsewhere in the same tree
            stale = target / ".opencode" / "stale-agent-that-should-be-deleted.md"
            stale.write_text("remove me", encoding="utf-8")

            proc2 = self._run_install(target, platform="opencode", update=True)
            self.assertEqual(proc2.returncode, 0, proc2.stdout + proc2.stderr)

            updated = json.loads(mcp_path.read_text(encoding="utf-8"))
            # (b) unknown key survives
            self.assertEqual(
                updated["mcp"].get("my-custom-server"),
                {"url": "https://example.invalid/mcp"},
                "unknown pre-existing server key must survive --update merge",
            )
            # (c) generator-known key refreshed
            self.assertEqual(
                updated["mcp"]["context7"],
                source_context7,
                "generator-known server key must be refreshed to match the generated source on --update",
            )
            # (d) stale non-MCP file in the same tree still correctly deleted —
            # proves the exclude is scoped to exactly opencode.json, not the whole tree
            self.assertFalse(
                stale.exists(),
                "--update must still stale-clean the rest of .opencode/ via rsync --delete; "
                "only opencode.json is exempted",
            )
            # opencode-specific: sibling non-MCP keys must survive untouched
            self.assertEqual(updated.get("$schema"), source_data.get("$schema"))
            self.assertEqual(updated.get("instructions"), source_data.get("instructions"))

    def test_pi_mcp_json_merge_on_update(self):
        implementation_mcp = repo_root() / "implementation" / ".pi" / "mcp.json"
        source_data = json.loads(implementation_mcp.read_text(encoding="utf-8"))
        source_context7 = source_data["mcpServers"]["context7"]

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            target.mkdir()

            # (a) fresh install: byte-identical plain copy
            proc = self._run_install(target, platform="pi")
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            mcp_path = target / ".pi" / "mcp.json"
            self.assertEqual(
                mcp_path.read_text(encoding="utf-8"),
                implementation_mcp.read_text(encoding="utf-8"),
                "fresh (non --update) install must plain-copy .pi/mcp.json byte-for-byte",
            )

            # inject an unknown server key + corrupt a generator-known key
            data = json.loads(mcp_path.read_text(encoding="utf-8"))
            data["mcpServers"]["my-custom-server"] = {"url": "https://example.invalid/mcp"}
            data["mcpServers"]["context7"] = {"url": "https://stale.example.invalid/mcp"}
            mcp_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

            # (d) a stale non-MCP file elsewhere in the same tree
            stale = target / ".pi" / "stale-agent-that-should-be-deleted.md"
            stale.write_text("remove me", encoding="utf-8")

            proc2 = self._run_install(target, platform="pi", update=True)
            self.assertEqual(proc2.returncode, 0, proc2.stdout + proc2.stderr)

            updated = json.loads(mcp_path.read_text(encoding="utf-8"))
            # (b) unknown key survives
            self.assertEqual(
                updated["mcpServers"].get("my-custom-server"),
                {"url": "https://example.invalid/mcp"},
                "unknown pre-existing server key must survive --update merge",
            )
            # (c) generator-known key refreshed
            self.assertEqual(
                updated["mcpServers"]["context7"],
                source_context7,
                "generator-known server key must be refreshed to match the generated source on --update",
            )
            # (d) stale non-MCP file in the same tree still correctly deleted —
            # proves the exclude is scoped to exactly mcp.json, not the whole tree
            self.assertFalse(
                stale.exists(),
                "--update must still stale-clean the rest of .pi/ via rsync --delete; "
                "only mcp.json is exempted",
            )

    def test_cline_mcp_json_merge_on_update(self):
        implementation_mcp = repo_root() / "implementation" / ".cline" / "mcp.json"
        source_data = json.loads(implementation_mcp.read_text(encoding="utf-8"))
        source_context7 = source_data["mcpServers"]["context7"]

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            target.mkdir()

            # (a) fresh install: byte-identical plain copy
            proc = self._run_install(target, platform="cline")
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            mcp_path = target / ".cline" / "mcp.json"
            self.assertEqual(
                mcp_path.read_text(encoding="utf-8"),
                implementation_mcp.read_text(encoding="utf-8"),
                "fresh (non --update) install must plain-copy .cline/mcp.json byte-for-byte",
            )

            # inject an unknown server key + corrupt a generator-known key
            data = json.loads(mcp_path.read_text(encoding="utf-8"))
            data["mcpServers"]["my-custom-server"] = {"url": "https://example.invalid/mcp"}
            data["mcpServers"]["context7"] = {"url": "https://stale.example.invalid/mcp"}
            mcp_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

            # (d) a stale non-MCP file elsewhere in the same tree
            stale = target / ".cline" / "stale-agent-that-should-be-deleted.md"
            stale.write_text("remove me", encoding="utf-8")

            proc2 = self._run_install(target, platform="cline", update=True)
            self.assertEqual(proc2.returncode, 0, proc2.stdout + proc2.stderr)

            updated = json.loads(mcp_path.read_text(encoding="utf-8"))
            # (b) unknown key survives
            self.assertEqual(
                updated["mcpServers"].get("my-custom-server"),
                {"url": "https://example.invalid/mcp"},
                "unknown pre-existing server key must survive --update merge",
            )
            # (c) generator-known key refreshed
            self.assertEqual(
                updated["mcpServers"]["context7"],
                source_context7,
                "generator-known server key must be refreshed to match the generated source on --update",
            )
            # (d) stale non-MCP file in the same tree still correctly deleted —
            # proves the exclude is scoped to exactly mcp.json, not the whole tree
            self.assertFalse(
                stale.exists(),
                "--update must still stale-clean the rest of .cline/ via rsync --delete; "
                "only mcp.json is exempted",
            )

    # -- T391: provenance sidecar (ADR-002 §1-4) -- both pruning directions,
    #    the bootstrap default, and the --force-prune-keys bridge --

    def _run_merge_mcp_json(self, *cli_args: str) -> subprocess.CompletedProcess[str]:
        """Invoke scripts/merge-mcp-json.py directly (not via install.sh), for
        tests that need full control over --source/--dest/--old-sidecar/
        --new-sidecar/--force-prune-keys content that install.sh's real
        generated files under implementation/ cannot provide."""
        return subprocess.run(
            [sys.executable, str(repo_root() / "scripts" / "merge-mcp-json.py"), *cli_args],
            cwd=repo_root(),
            capture_output=True,
            text=True,
            check=False,
        )

    def _assert_retired_key_pruned_and_sidecar_survives(self, platform: str, mcp_rel: str, wrapper_key: str) -> None:
        """Shared body for the per-tree-platform proof: a synthetic key hand-
        added to both the dest MCP file's server map and the dest sidecar's
        generatorOwnedKeys (simulating a prior generation that owned it, now
        retired) is pruned on `--update`. This can only fire if the dest
        sidecar survived install_tree_into()'s `sync_tree_into()`/
        `rsync -a --delete` pass intact (ADR-002 "Risks introduced"): if the
        exclude wiring for this platform were broken, the sidecar would be
        deleted before merge_or_copy_mcp_json() ever reads it, the merge would
        silently fall back to the bootstrap (no-history) case, and the
        synthetic key would incorrectly survive instead of being pruned."""
        implementation_mcp = repo_root() / "implementation" / mcp_rel
        implementation_sidecar = implementation_mcp.parent / f"{implementation_mcp.name}.provenance.json"

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            target.mkdir()

            proc = self._run_install(target, platform=platform)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

            mcp_path = target / mcp_rel
            sidecar_path = mcp_path.parent / f"{mcp_path.name}.provenance.json"
            self.assertTrue(
                sidecar_path.is_file(),
                f"fresh install must plain-copy the {platform} provenance sidecar alongside its MCP file",
            )

            data = json.loads(mcp_path.read_text(encoding="utf-8"))
            data[wrapper_key]["synthetic-retiring-server"] = {"url": "https://retired.example.invalid/mcp"}
            mcp_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

            sidecar = json.loads(sidecar_path.read_text(encoding="utf-8"))
            sidecar["generatorOwnedKeys"] = sorted(
                set(sidecar["generatorOwnedKeys"]) | {"synthetic-retiring-server"}
            )
            sidecar_path.write_text(json.dumps(sidecar, indent=2) + "\n", encoding="utf-8")

            proc2 = self._run_install(target, platform=platform, update=True)
            self.assertEqual(proc2.returncode, 0, proc2.stdout + proc2.stderr)

            updated = json.loads(mcp_path.read_text(encoding="utf-8"))
            self.assertNotIn(
                "synthetic-retiring-server",
                updated[wrapper_key],
                f"retired generator-owned key must be pruned on --update for platform={platform} "
                "using real two-generation sidecar history (old sidecar hand-edited to record it, "
                "new/source sidecar without it); this also proves the provenance sidecar for "
                f"{mcp_rel} survived the rsync --delete tree-sync pass, since the diff could only "
                "fire if the hand-edited old sidecar was actually read intact",
            )

            refreshed_sidecar = json.loads(sidecar_path.read_text(encoding="utf-8"))
            source_sidecar = json.loads(implementation_sidecar.read_text(encoding="utf-8"))
            self.assertEqual(
                refreshed_sidecar,
                source_sidecar,
                "--old-sidecar's path must be refreshed with --new-sidecar's exact content "
                "after a successful merge, seeding history for the next --update",
            )

    def test_update_preserves_hand_added_key_absent_from_sidecar_generator_owned_keys(self):
        """Proof class (a): a synthetic hand-added key with no sidecar entry
        survives `--update` when a sidecar is present, and is never recorded
        as generator-owned before or after -- the mechanism requires positive
        evidence of generator ownership, not merely the absence of a prune."""
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            target.mkdir()

            proc = self._run_install(target, platform="github")
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

            mcp_path = target / ".vscode" / "mcp.json"
            sidecar_path = target / ".vscode" / "mcp.json.provenance.json"
            self.assertTrue(
                sidecar_path.is_file(), "fresh install must plain-copy the provenance sidecar too"
            )

            sidecar_before = json.loads(sidecar_path.read_text(encoding="utf-8"))
            self.assertNotIn(
                "my-hand-added-server",
                sidecar_before.get("generatorOwnedKeys", []),
                "a key the generator never emitted must not appear in generatorOwnedKeys before --update",
            )

            data = json.loads(mcp_path.read_text(encoding="utf-8"))
            data["servers"]["my-hand-added-server"] = {"url": "https://example.invalid/mcp"}
            mcp_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

            proc2 = self._run_install(target, platform="github", update=True)
            self.assertEqual(proc2.returncode, 0, proc2.stdout + proc2.stderr)

            updated = json.loads(mcp_path.read_text(encoding="utf-8"))
            self.assertEqual(
                updated["servers"].get("my-hand-added-server"),
                {"url": "https://example.invalid/mcp"},
                "a hand-added key with no sidecar entry must survive --update byte-for-byte "
                "when a sidecar is present",
            )

            sidecar_after = json.loads(sidecar_path.read_text(encoding="utf-8"))
            self.assertNotIn(
                "my-hand-added-server",
                sidecar_after.get("generatorOwnedKeys", []),
                "a hand-added key must never be recorded as generator-owned after --update either",
            )

    def test_update_bootstrap_no_prior_sidecar_preserves_dest_only_key(self):
        """Proof class (d): with the sidecar file physically absent beforehand
        (not merely stale), simulating an already-installed project from
        before this mechanism existed, `--update` still preserves every
        dest-only key exactly as it did before this mechanism existed."""
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            target.mkdir()

            proc = self._run_install(target, platform="github")
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

            mcp_path = target / ".vscode" / "mcp.json"
            sidecar_path = target / ".vscode" / "mcp.json.provenance.json"
            self.assertTrue(sidecar_path.is_file())

            sidecar_path.unlink()
            self.assertFalse(sidecar_path.exists(), "sidecar must be physically absent before this --update")

            data = json.loads(mcp_path.read_text(encoding="utf-8"))
            data["servers"]["my-hand-added-server"] = {"url": "https://example.invalid/mcp"}
            mcp_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

            proc2 = self._run_install(target, platform="github", update=True)
            self.assertEqual(proc2.returncode, 0, proc2.stdout + proc2.stderr)

            updated = json.loads(mcp_path.read_text(encoding="utf-8"))
            self.assertEqual(
                updated["servers"].get("my-hand-added-server"),
                {"url": "https://example.invalid/mcp"},
                "with no prior sidecar at all (bootstrap default), every dest-only key must "
                "survive --update exactly as it did before this mechanism existed",
            )

    def test_update_prunes_retired_generator_owned_key_via_sidecar_history_cursor(self):
        """Proof class (b), platform cursor. Also one of the 5 required
        per-tree-platform sidecar-survival assertions (ADR-002 "Risks
        introduced")."""
        self._assert_retired_key_pruned_and_sidecar_survives("cursor", ".cursor/mcp.json", "mcpServers")

    def test_update_prunes_retired_generator_owned_key_via_sidecar_history_gemini(self):
        """Sidecar-survival assertion for platform gemini (ADR-002 "Risks introduced")."""
        self._assert_retired_key_pruned_and_sidecar_survives("gemini", ".gemini/settings.json", "mcpServers")

    def test_update_prunes_retired_generator_owned_key_via_sidecar_history_opencode(self):
        """Sidecar-survival assertion for platform opencode (ADR-002 "Risks introduced")."""
        self._assert_retired_key_pruned_and_sidecar_survives("opencode", ".opencode/opencode.json", "mcp")

    def test_update_prunes_retired_generator_owned_key_via_sidecar_history_pi(self):
        """Sidecar-survival assertion for platform pi (ADR-002 "Risks introduced")."""
        self._assert_retired_key_pruned_and_sidecar_survives("pi", ".pi/mcp.json", "mcpServers")

    def test_update_prunes_retired_generator_owned_key_via_sidecar_history_cline(self):
        """Sidecar-survival assertion for platform cline (ADR-002 "Risks introduced")."""
        self._assert_retired_key_pruned_and_sidecar_survives("cline", ".cline/mcp.json", "mcpServers")

    def test_update_never_prunes_a_key_source_still_emits_despite_stale_sidecar(self):
        """Proof class (c) -- the critical over-pruning guard. Even if the
        diff between --old-sidecar and --new-sidecar naively marks a key as
        retired (because a corrupted/stale --new-sidecar omits a key the
        generator still genuinely emits), `prune_names_recursive` re-checks
        the key's presence against the actual --source JSON content at that
        same nested path before ever deleting it. A key `source` still emits
        must survive -- refreshed, never pruned -- regardless of what any
        sidecar says (ADR-002 §4.c and non-negotiable property #4)."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            dest = tmp_path / "dest.json"
            source = tmp_path / "source.json"
            old_sidecar = tmp_path / "old.provenance.json"
            new_sidecar = tmp_path / "new.provenance.json"

            stale_context7 = {"type": "http", "url": "https://stale.example.invalid/mcp"}
            fresh_context7 = {"type": "http", "url": "https://mcp.context7.com/mcp"}

            dest.write_text(
                json.dumps(
                    {
                        "mcpServers": {
                            "context7": stale_context7,
                            "cwso": {"url": "https://cwso.invalid/mcp"},
                        }
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )
            # `source` genuinely still emits context7 at the same nested path.
            source.write_text(
                json.dumps({"mcpServers": {"context7": fresh_context7}}, indent=2),
                encoding="utf-8",
            )
            # Old sidecar recorded context7 as generator-owned in a prior generation.
            old_sidecar.write_text(
                json.dumps({"schemaVersion": 1, "generatorOwnedKeys": ["context7"]}, indent=2),
                encoding="utf-8",
            )
            # New (stale/inconsistent) sidecar omits context7 -- as if it were
            # generated against a corrupted intermediate state -- so the naive
            # old-minus-new diff would mark context7 "retired" even though
            # `source` still genuinely emits it.
            new_sidecar.write_text(
                json.dumps({"schemaVersion": 1, "generatorOwnedKeys": []}, indent=2),
                encoding="utf-8",
            )

            proc = self._run_merge_mcp_json(
                "--source", str(source),
                "--dest", str(dest),
                "--old-sidecar", str(old_sidecar),
                "--new-sidecar", str(new_sidecar),
            )
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

            merged = json.loads(dest.read_text(encoding="utf-8"))
            self.assertEqual(
                merged["mcpServers"].get("context7"),
                fresh_context7,
                "a key `source` still emits must never be pruned regardless of what a stale/"
                "inconsistent sidecar diff claims -- it must be refreshed to the current "
                "generated content instead of deleted",
            )
            self.assertEqual(
                merged["mcpServers"].get("cwso"),
                {"url": "https://cwso.invalid/mcp"},
                "an unrelated hand-added dest-only key must be unaffected by this scenario",
            )

    def test_force_prune_keys_bridge_prunes_only_named_keys_and_errors_on_non_dest_only(self):
        """Proof class (e): the one-time --force-prune-keys bridge prunes
        exactly its named dest-only key(s); an unnamed hand-added key survives
        untouched even when the flag is used; naming a key that is not
        actually dest-only (still present in source) causes a non-zero exit
        and no partial write to --dest."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            dest = tmp_path / "dest.json"
            source = tmp_path / "source.json"

            real_context7 = {"type": "http", "url": "https://mcp.context7.com/mcp"}
            dest_data = {
                "mcpServers": {
                    "context7": real_context7,
                    "e2b": {"url": "https://retired-e2b.example.invalid/mcp"},
                    "cwso": {"url": "https://cwso.invalid/mcp"},
                }
            }
            source_data = {"mcpServers": {"context7": real_context7}}
            dest.write_text(json.dumps(dest_data, indent=2), encoding="utf-8")
            source.write_text(json.dumps(source_data, indent=2), encoding="utf-8")

            proc = self._run_merge_mcp_json(
                "--source", str(source), "--dest", str(dest), "--force-prune-keys", "e2b",
            )
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

            merged = json.loads(dest.read_text(encoding="utf-8"))
            self.assertNotIn(
                "e2b", merged["mcpServers"], "the exact named force-prune key must be pruned"
            )
            self.assertEqual(
                merged["mcpServers"].get("cwso"),
                {"url": "https://cwso.invalid/mcp"},
                "an unnamed hand-added dest-only key must survive untouched even when the "
                "force-prune bridge is used",
            )
            self.assertEqual(merged["mcpServers"].get("context7"), real_context7)

            # -- error case: naming a key that is not actually dest-only --
            dest2 = tmp_path / "dest2.json"
            dest2_data = {
                "mcpServers": {
                    "context7": real_context7,
                    "cwso": {"url": "https://cwso.invalid/mcp"},
                }
            }
            dest2.write_text(json.dumps(dest2_data, indent=2), encoding="utf-8")
            dest2_before = dest2.read_text(encoding="utf-8")

            proc2 = self._run_merge_mcp_json(
                "--source", str(source), "--dest", str(dest2), "--force-prune-keys", "context7",
            )
            self.assertNotEqual(
                proc2.returncode,
                0,
                "naming a key that is not genuinely dest-only (still present in source) must "
                "cause a non-zero exit",
            )
            self.assertIn("context7", proc2.stderr)

            dest2_after = dest2.read_text(encoding="utf-8")
            self.assertEqual(
                dest2_before,
                dest2_after,
                "an errored --force-prune-keys invocation must not write anything to --dest",
            )


if __name__ == "__main__":
    unittest.main()
