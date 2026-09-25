"""Functional tests for scripts/install.sh."""
from __future__ import annotations

import json
import os
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
            self.assertIn("Append-only log.", completed)
            # T518: these two assertions previously read
            #     assertIn("Per-task briefs live alongside", active)
            #     assertNotIn("> Keep this note.", active)
            # i.e. they asserted that the template's prose replaced the target's
            # own note. That encoded the bug: --update was substituting
            # fresh-install guidance ("this ledger starts EMPTY", "the first real
            # task is T001") for a project's actual record.
            self.assertIn("> Keep this note.", active)
            self.assertNotIn("Per-task briefs live alongside", active)
            self.assertNotIn("ledger starts EMPTY", active)

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


class TestInstallPreservesProjectLocalFiles(unittest.TestCase):
    """T518: `--update` must not delete files the harness never ships.

    `sync_tree_into()` runs `rsync -a --delete`, so any file present in the
    target but absent from `implementation/` was swept on every update. Two real
    cases: `.claude/settings.json` (a host's Bash-permission allowlist, recorded
    in T512 and hit again verbatim in T517) and `.github/workflows/` (the target
    project's own CI). Every test here fails against the pre-T518 script.
    """

    SETTINGS = '{\n  "permissions": {\n    "allow": ["Bash(git status:*)"]\n  }\n}\n'
    SETTINGS_LOCAL = '{\n  "permissions": {\n    "allow": ["Bash(ls:*)"]\n  }\n}\n'
    WORKFLOW = "name: ci\non: [push]\njobs:\n  t:\n    runs-on: ubuntu-latest\n"

    @classmethod
    def setUpClass(cls):
        cls.bash = shutil.which("bash")
        if not cls.bash:
            raise unittest.SkipTest("bash not available on PATH")

    @staticmethod
    def _path_without_rsync(tmp: Path) -> str:
        """A PATH identical to the current one minus rsync.

        CI's `python:3.12-alpine` image has no rsync at all, so install.sh's
        hand-rolled fallback runs there and nowhere else -- which is exactly how
        the T513 `set -e` bug reached production. Shadowing rsync with a stub
        would not do: install.sh dispatches on `command -v rsync`, which a stub
        still satisfies. The binary has to be genuinely absent from PATH.
        """
        farm = tmp / "norsync-bin"
        farm.mkdir(parents=True, exist_ok=True)
        for entry in os.environ.get("PATH", "").split(os.pathsep):
            if not entry or not os.path.isdir(entry):
                continue
            for name in os.listdir(entry):
                if name == "rsync":
                    continue
                link = farm / name
                if link.exists() or link.is_symlink():
                    continue
                try:
                    link.symlink_to(os.path.join(entry, name))
                except OSError:
                    pass
        return str(farm)

    def _run_install(
        self,
        target: Path,
        platform: str = "all",
        update: bool = False,
        path_override: str | None = None,
    ) -> subprocess.CompletedProcess[str]:
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
        env = dict(os.environ)
        if path_override is not None:
            env["PATH"] = path_override
        return subprocess.run(
            args, cwd=repo_root(), capture_output=True, text=True, check=False, env=env
        )

    def _seed(self, target: Path) -> None:
        """A target that already looks like a real project."""
        target.mkdir(parents=True, exist_ok=True)
        (target / "AGENTS.md").write_text("# existing", encoding="utf-8")
        claude = target / ".claude"
        claude.mkdir(exist_ok=True)
        (claude / "settings.json").write_text(self.SETTINGS, encoding="utf-8")
        (claude / "settings.local.json").write_text(self.SETTINGS_LOCAL, encoding="utf-8")
        gh = target / ".github"
        (gh / "workflows").mkdir(parents=True, exist_ok=True)
        (gh / "ISSUE_TEMPLATE").mkdir(parents=True, exist_ok=True)
        (gh / "workflows" / "ci.yml").write_text(self.WORKFLOW, encoding="utf-8")
        (gh / "ISSUE_TEMPLATE" / "bug.md").write_text("name: Bug\n", encoding="utf-8")
        (gh / "CODEOWNERS").write_text("* @org/maintainers\n", encoding="utf-8")
        (gh / "dependabot.yml").write_text("version: 2\n", encoding="utf-8")

    def _assert_all_survived(self, target: Path) -> None:
        self.assertEqual(
            (target / ".claude" / "settings.json").read_text(encoding="utf-8"),
            self.SETTINGS,
            ".claude/settings.json is project-local state with no implementation/ "
            "counterpart; --update must not delete or rewrite it",
        )
        self.assertEqual(
            (target / ".claude" / "settings.local.json").read_text(encoding="utf-8"),
            self.SETTINGS_LOCAL,
            ".claude/settings.local.json is the same class of file as settings.json",
        )
        gh = target / ".github"
        self.assertEqual((gh / "workflows" / "ci.yml").read_text(encoding="utf-8"), self.WORKFLOW)
        self.assertEqual((gh / "ISSUE_TEMPLATE" / "bug.md").read_text(encoding="utf-8"), "name: Bug\n")
        self.assertEqual((gh / "CODEOWNERS").read_text(encoding="utf-8"), "* @org/maintainers\n")
        self.assertEqual((gh / "dependabot.yml").read_text(encoding="utf-8"), "version: 2\n")

    def test_update_preserves_project_local_files_with_rsync(self):
        if not shutil.which("rsync"):
            self.skipTest("rsync not available; the fallback variant covers this host")
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            self._seed(target)
            proc = self._run_install(target, update=True)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self._assert_all_survived(target)

    def test_update_preserves_project_local_files_without_rsync(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            self._seed(target)
            proc = self._run_install(
                target, update=True, path_override=self._path_without_rsync(Path(tmp))
            )
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self._assert_all_survived(target)

    def test_update_still_deletes_stale_harness_files_in_protected_trees(self):
        """The protection must be scoped to named project-local paths, not a
        blanket disable of stale-cleaning in .claude/ and .github/."""
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            self._seed(target)
            stale_claude = target / ".claude" / "stale-agent.md"
            stale_github = target / ".github" / "agents" / "stale-agent.agent.md"
            stale_claude.write_text("remove me", encoding="utf-8")
            stale_github.parent.mkdir(parents=True, exist_ok=True)
            stale_github.write_text("remove me", encoding="utf-8")

            proc = self._run_install(target, update=True)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertFalse(stale_claude.exists(), "--update must still prune stale .claude/ files")
            self.assertFalse(stale_github.exists(), "--update must still prune stale .github/ files")
            self._assert_all_survived(target)

    def test_fresh_install_does_not_delete_pre_existing_project_local_files(self):
        """The no-rsync fallback in copy_tree_into() used to `rm -rf dest/<excl>`
        unconditionally, deleting pre-existing *target* content that was never in
        the source -- the opposite of what rsync --exclude does."""
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            self._seed(target)
            proc = self._run_install(
                target, update=False, path_override=self._path_without_rsync(Path(tmp))
            )
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self._assert_all_survived(target)

    def test_update_help_text_states_the_actual_contract(self):
        proc = subprocess.run(
            [self.bash, str(repo_root() / "scripts" / "install.sh"), "--help"],
            cwd=repo_root(), capture_output=True, text=True, check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn(".claude/settings.json", proc.stdout)
        self.assertIn("workflows", proc.stdout)
        self.assertIn("rewritten beyond its task rows", proc.stdout)
        self.assertIn("project's own record, not the template's", proc.stdout)
        self.assertNotIn("preserves task rows in docs/tasks/*.md", proc.stdout)


class TestInstallPreservesLedgerProse(unittest.TestCase):
    """T518 Defect B, end to end through install.sh.

    Worst precisely when the ledger is healthy: with zero active rows there was
    nothing to preserve, so the template won outright and wrote "This ledger
    starts EMPTY [...] The first real task is `T001`" into a project with
    hundreds of completed tasks. Fails against the pre-T518 script.
    """

    ACTIVE = """# Active Tasks

| ID | Title | Owner | Status | Priority | Depends on | Last update |
|----|-------|-------|--------|----------|-----------|-------------|

> **0 active rows.** This is not a fresh project -- 316 real tasks have already
> run to completion; see `completed-tasks.md`. Do not treat an empty table as
> "no history exists" -- it means no task is currently in flight.

> Status values: `pending` · `in_progress` · `blocked` · `in_review` · `done`

Per-task briefs live alongside this file as `task-T001.md`, `task-T002.md`, …
"""

    COMPLETED = """# Completed Tasks

Append-only log. Entries move here after the orchestrator marks a task `done`.

| ID | Title | Owner | Done on | Outcome / artifact |
|----|-------|-------|---------|--------------------|
| T042 | CI gates | devops-engineer | 2026-05-24 | .gitlab-ci.yml |
"""

    @classmethod
    def setUpClass(cls):
        cls.bash = shutil.which("bash")
        if not cls.bash:
            raise unittest.SkipTest("bash not available on PATH")

    def _update(self, target: Path, path_override: str | None = None):
        env = dict(os.environ)
        if path_override is not None:
            env["PATH"] = path_override
        return subprocess.run(
            [
                self.bash, str(repo_root() / "scripts" / "install.sh"),
                "--target", str(target), "--platform", "pi", "--update",
            ],
            cwd=repo_root(), capture_output=True, text=True, check=False, env=env,
        )

    def _seed(self, target: Path) -> Path:
        target.mkdir(parents=True, exist_ok=True)
        (target / "AGENTS.md").write_text("# existing", encoding="utf-8")
        tasks = target / "docs" / "tasks"
        tasks.mkdir(parents=True, exist_ok=True)
        (tasks / "active-tasks.md").write_text(self.ACTIVE, encoding="utf-8")
        (tasks / "completed-tasks.md").write_text(self.COMPLETED, encoding="utf-8")
        return tasks

    def _assert_preserved(self, tasks: Path) -> None:
        active = (tasks / "active-tasks.md").read_text(encoding="utf-8")
        completed = (tasks / "completed-tasks.md").read_text(encoding="utf-8")
        self.assertEqual(active, self.ACTIVE, "a zero-row ledger must survive byte-identical")
        self.assertEqual(completed, self.COMPLETED, "completed-tasks.md must not regress")
        self.assertNotIn("ledger starts EMPTY", active)
        self.assertIn("| T042 | CI gates |", completed)

    def test_update_preserves_zero_row_ledger_prose(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            tasks = self._seed(target)
            proc = self._update(target)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self._assert_preserved(tasks)

    def test_update_is_idempotent_on_a_populated_ledger(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            tasks = self._seed(target)
            for _ in range(3):
                proc = self._update(target)
                self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self._assert_preserved(tasks)

    def test_update_still_seeds_a_missing_ledger_from_the_template(self):
        """Fresh-install guidance must still reach a target that has no ledger."""
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            target.mkdir(parents=True)
            (target / "AGENTS.md").write_text("# existing", encoding="utf-8")
            proc = self._update(target)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            seeded = (target / "docs" / "tasks" / "active-tasks.md").read_text(encoding="utf-8")
            self.assertEqual(
                seeded,
                (repo_root() / "implementation" / "docs" / "tasks" / "active-tasks.md").read_text(
                    encoding="utf-8"
                ),
            )
            self.assertIn("ledger starts EMPTY", seeded)


if __name__ == "__main__":
    unittest.main()
