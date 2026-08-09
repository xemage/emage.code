"""Functional tests for scripts/install.sh."""
from __future__ import annotations

import json
import shutil
import subprocess
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


if __name__ == "__main__":
    unittest.main()
