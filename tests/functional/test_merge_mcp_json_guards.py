"""SEC-T680-01, -05, -07, -08, -09 -- the generic guards of scripts/merge-mcp-json.py.

Moved from test_pi_optional_variables.py by ADR-013 D4 (T771): these guards serve every MCP format, so they stay
when the classes of the removed platform go. They pin the credential-literal WARNING and its classification (SEC-T680-01, -07, -08),
the literal-path note, terminal-safe names in every note (SEC-T680-05) and the naming of a hand-edited entry
under a pruned name (SEC-T680-09).

Local `python3` runs on temporary directories; no network, no token.
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

from tests._helpers.repo import repo_root

REPO = repo_root()
MERGER = REPO / "scripts" / "merge-mcp-json.py"


def _merge(source: Path, dest: Path, *flags: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(MERGER), "--source", str(source), "--dest", str(dest), *flags],
                          capture_output=True, text=True, check=False)


def _load_merger():
    spec = importlib.util.spec_from_file_location("merge_mcp_json_t680", MERGER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


MERGER_MODULE = _load_merger()


class LiteralCredentialClassificationTests(unittest.TestCase):
    """SEC-T680-07, -08: what counts as a placeholder, and how the check is bounded."""

    def test_only_a_whole_single_reference_is_a_placeholder(self):
        placeholders = ["${A}", "$A", "{env:A}", "Bearer ${A}", "!pass show x", "", "${A_1}", "Basic $TOK"]
        for value in placeholders:
            with self.subTest(value=value):
                self.assertFalse(MERGER_MODULE.holds_literal_credential("MY_TOKEN", value))

    def test_bypass_attempts_are_literals(self):
        literals = ["${VAR:-glpat-FAKEFAKE}", "pa$word", "ab$cd", "$3cr3t-token", "$ecret-x9", "${A}${B}",
                    "${A} tail", "Bearer abc", "glpat-FAKE", "${A", "$", "${}", "{env:A}x",
                    "two words ${A}", "${A:-}", "$A$B"]
        for value in literals:
            with self.subTest(value=value):
                self.assertTrue(MERGER_MODULE.holds_literal_credential("MY_TOKEN", value))

    def test_the_credential_name_list(self):
        for name in ("MY_TOKEN", "api_key", "CLIENT_SECRET", "DB_PASSWORD", "DB_PASSWD", "Authorization", "X_AUTH",
                     "SESSION_COOKIE", "BEARER", "AWS_CREDENTIALS"):
            with self.subTest(name=name):
                self.assertTrue(MERGER_MODULE.holds_literal_credential(name, "abc-literal"))
        for name in ("GITLAB_TOOLS", "LOG_LEVEL", "HOME"):
            with self.subTest(name=name):
                self.assertFalse(MERGER_MODULE.holds_literal_credential(name, "abc-literal"))

    def test_a_long_value_is_a_literal_and_the_check_is_fast(self):
        self.assertTrue(MERGER_MODULE.holds_literal_credential("MY_TOKEN", "$" + "A" * 5000))
        for value in ("${" * 2_000_000, "$" * 4_000_000, "Bearer " * 600_000, "{env:" * 1_000_000 + "}"):
            started = time.monotonic()
            self.assertTrue(MERGER_MODULE.holds_literal_credential("MY_TOKEN", value))
            self.assertLess(time.monotonic() - started, 2.0)

    def test_a_multi_megabyte_value_through_the_whole_merge_is_fast(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        source, dest = Path(tmp.name) / "s.json", Path(tmp.name) / "d.json"
        source.write_text(json.dumps({"mcpServers": {"srv": {"env": {"A": "${A}"}}}}), encoding="utf-8")
        dest.write_text(json.dumps({"mcpServers": {"srv": {"env": {"MY_TOKEN": "${" * 2_000_000}}}}), encoding="utf-8")
        started = time.monotonic()
        result = _merge(source, dest)
        self.assertLess(time.monotonic() - started, 2.0)
        self.assertEqual(result.returncode, 0, result.stderr[:300])
        self.assertIn("WARNING", result.stderr)
        self.assertLess(len(result.stderr), 2000, "the value must not be echoed")


class LiteralPathTests(unittest.TestCase):
    def merge_env(self, extra: dict) -> subprocess.CompletedProcess:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        source, dest = Path(tmp.name) / "s.json", Path(tmp.name) / "d.json"
        source.write_text(json.dumps({"mcpServers": {"srv": {"env": {"A": "${A}"}}}}), encoding="utf-8")
        dest.write_text(json.dumps({"mcpServers": {"srv": {"env": {"A": "${A}", **extra}}}}), encoding="utf-8")
        result = _merge(source, dest)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result

    def test_a_file_or_path_named_key_gets_the_non_alarming_note(self):
        for key in ("GITLAB_PERSONAL_ACCESS_TOKEN_FILE", "MY_TOKEN_PATH", "secret.file", "api-key-path"):
            with self.subTest(key=key):
                result = self.merge_env({key: "/home/user/.config/gitlab-mcp/token"})
                self.assertNotIn("WARNING", result.stderr)
                self.assertNotIn("revoke", result.stderr)
                self.assertIn(f"mcpServers.srv.env.{key} holds a literal path; fine, but it is read by the server "
                              f"only if the token variable is empty", result.stderr)
                self.assertNotIn(".config/gitlab-mcp", result.stderr)

    def test_other_names_still_warn(self):
        for key in ("MY_TOKEN_BACKUP", "MY_TOKENFILE", "FILE_TOKEN"):
            with self.subTest(key=key):
                result = self.merge_env({key: "abc-literal"})
                self.assertIn("WARNING", result.stderr)
                self.assertIn("revoke the token", result.stderr)


class TerminalSafeNamesTests(unittest.TestCase):
    """SEC-T680-05: every name sink goes through format_names -> printable (T682 N-1)."""

    EVIL = "x\x1b[31m\nforged: line\u202e"

    def run_merge(self, source: dict, dest: dict, *extra: str) -> subprocess.CompletedProcess:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        s, d = Path(tmp.name) / "s.json", Path(tmp.name) / "d.json"
        s.write_text(json.dumps(source), encoding="utf-8")
        d.write_text(json.dumps(dest), encoding="utf-8")
        self.sidecar_dir = Path(tmp.name)
        return subprocess.run([sys.executable, str(MERGER), "--source", str(s), "--dest", str(d), *extra],
                              capture_output=True, text=True, check=False)

    def assert_safe(self, err: str, escaped: str):
        self.assertIn(escaped, err)
        self.assertEqual([ch for ch in err if not (ch.isprintable() or ch == "\n")], [], repr(err))
        self.assertNotIn("\nforged: line", err)

    def test_dropped_literal_and_literal_path_notes(self):
        evil = self.EVIL
        source = {"mcpServers": {"srv": {"env": {"A": "${A}"}}}}
        dest = {"mcpServers": {"srv": {"env": {"A": "${A}", evil + "_TOKEN": "literal-x", evil + "_FILE": "/p",
                                               evil + "_OLD": "${env:OLD}"}}}}
        result = self.run_merge(source, dest)
        self.assertEqual(result.returncode, 0, result.stderr)
        for suffix in ("_TOKEN", "_FILE", "_OLD"):
            self.assert_safe(result.stderr, ascii(f"mcpServers.srv.env.{evil}{suffix}"))

    def test_pruned_and_pruned_differs_notes(self):
        evil = self.EVIL
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        (root / "s.json").write_text(json.dumps({"mcpServers": {"keep": {}}}), encoding="utf-8")
        (root / "d.json").write_text(json.dumps({"mcpServers": {"keep": {}, evil: {"url": "https://x.invalid/mcp"}}}),
                                     encoding="utf-8")
        (root / "d.sc.json").write_text(json.dumps({"schemaVersion": 1, "generatorOwnedKeys": ["keep", evil]}), encoding="utf-8")
        (root / "s.sc.json").write_text(json.dumps({"schemaVersion": 1, "generatorOwnedKeys": ["keep"]}), encoding="utf-8")
        result = subprocess.run([sys.executable, str(MERGER), "--source", str(root / "s.json"), "--dest", str(root / "d.json"),
                                 "--old-sidecar", str(root / "d.sc.json"), "--new-sidecar", str(root / "s.sc.json")],
                                capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assert_safe(result.stderr, f"pruned the retired generator server {ascii(evil)}")
        self.assert_safe(result.stderr, f"{ascii(evil)} differs from the generated entry")

    def test_bootstrap_kept_note(self):
        evil = self.EVIL
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        (root / "s.json").write_text(json.dumps({"mcpServers": {"keep": {}}}), encoding="utf-8")
        (root / "d.json").write_text(json.dumps({"mcpServers": {"keep": {}, evil: {}}}), encoding="utf-8")
        (root / "s.sc.json").write_text(json.dumps({"schemaVersion": 1, "generatorOwnedKeys": ["keep"]}), encoding="utf-8")
        result = subprocess.run([sys.executable, str(MERGER), "--source", str(root / "s.json"), "--dest", str(root / "d.json"),
                                 "--old-sidecar", str(root / "missing.sc.json"), "--new-sidecar", str(root / "s.sc.json")],
                                capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assert_safe(result.stderr, f"kept your server(s) {ascii(evil)},")

    def test_force_prune_offenders(self):
        result = self.run_merge({"mcpServers": {"a": {}}}, {"mcpServers": {"a": {}}}, "--force-prune-keys", self.EVIL)
        self.assertEqual(result.returncode, 1)
        self.assert_safe(result.stderr, f"named '{ascii(self.EVIL)}'")

    def test_every_name_sink_uses_format_names(self):
        text = MERGER.read_text(encoding="utf-8")
        body = text[text.index("def print_notes"):]
        self.assertNotIn("printable(", body, "print_notes and main() must call format_names, not printable")
        self.assertNotIn("', '.join(", body)
        self.assertIn("printable(name) for name in sorted(set(names))", text)


class PrunedEntryTests(unittest.TestCase):
    """SEC-T680-09: a hand-edited entry under a pruned name is named, never printed."""

    def prune(self, entries: dict, wrapper: str = "mcpServers") -> subprocess.CompletedProcess:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        (root / "s.json").write_text(json.dumps({wrapper: {"keep": {}}}), encoding="utf-8")
        (root / "d.json").write_text(json.dumps({wrapper: {"keep": {}, **entries}}), encoding="utf-8")
        (root / "d.sc.json").write_text(json.dumps({"schemaVersion": 1, "generatorOwnedKeys": ["keep", *entries]}), encoding="utf-8")
        (root / "s.sc.json").write_text(json.dumps({"schemaVersion": 1, "generatorOwnedKeys": ["keep"]}), encoding="utf-8")
        result = subprocess.run([sys.executable, str(MERGER), "--source", str(root / "s.json"), "--dest", str(root / "d.json"),
                                 "--old-sidecar", str(root / "d.sc.json"), "--new-sidecar", str(root / "s.sc.json")],
                                capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(list(json.loads((root / "d.json").read_text(encoding="utf-8"))[wrapper]), ["keep"])
        return result

    def test_a_hand_edited_same_name_entry_is_named_and_its_content_is_not_printed(self):
        result = self.prune({
            "hindsight": {"url": "https://hindsight-secret-host.invalid/mcp"},
            "cwso": {"url": "${env:CWSO_MCP_URL}", "headers": {"Authorization": "Bearer ${env:CWSO_BEARER_TOKEN}"}},
        })
        self.assertIn("pruned the retired generator server cwso, hindsight", result.stderr)
        self.assertIn("hindsight differs from the generated entry; its old content is not kept", result.stderr)
        self.assertNotIn("cwso differs", result.stderr)
        self.assertNotIn("hindsight-secret-host", result.stderr + result.stdout)

    def test_a_header_edit_and_a_non_object_entry_count_as_edited(self):
        result = self.prune({"a": {"url": "${X}", "headers": {"Authorization": "Bearer literal-token"}},
                             "b": "not an object", "c": {"url": "${X}", "env": []}})
        self.assertIn("a, b, c differs from the generated entry", result.stderr)
        self.assertNotIn("literal-token", result.stderr)

    def test_an_unedited_entry_is_pruned_without_the_differs_note(self):
        result = self.prune({"hindsight": {"url": "${HINDSIGHT_MCP_URL}"}})
        self.assertIn("pruned the retired generator server hindsight", result.stderr)
        self.assertNotIn("differs", result.stderr)

    # QA-T707-01: Opencode writes `{env:NAME}` without `$` (sync.mjs emitMcpOpencode).
    def test_an_unedited_opencode_entry_is_pruned_without_the_differs_note(self):
        result = self.prune({
            "github": {"type": "local", "command": ["npx", "-y", "some-server"],
                       "environment": {"GITHUB_PERSONAL_ACCESS_TOKEN": "{env:GITHUB_PERSONAL_ACCESS_TOKEN}"}},
            "cwso": {"type": "remote", "url": "{env:CWSO_MCP_URL}",
                     "headers": {"Authorization": "Bearer {env:CWSO_BEARER_TOKEN}"}},
        }, wrapper="mcp")
        self.assertIn("pruned the retired generator server cwso, github", result.stderr)
        self.assertNotIn("differs", result.stderr)

    def test_an_edited_opencode_entry_still_gets_the_differs_note(self):
        result = self.prune({
            "github": {"type": "local", "command": ["npx"], "environment": {"GITHUB_PERSONAL_ACCESS_TOKEN": "ghp-literal"}},
            "cwso": {"type": "remote", "url": "https://cwso-secret-host.invalid/{env:X}"},
            "hf": {"type": "remote", "url": "{env:HF_URL}", "headers": {"Authorization": "Bearer {env:A} {env:B}"}},
            "odd": {"type": "local", "environment": {"A": "{env:A", "B": "$${env:B}"}},
            "same": {"type": "local", "environment": {"A": "{env:A}"}},
        }, wrapper="mcp")
        self.assertIn("pruned the retired generator server cwso, github, hf, odd, same", result.stderr)
        self.assertIn("cwso, github, hf, odd differs from the generated entry", result.stderr)
        self.assertNotIn("ghp-literal", result.stderr + result.stdout)
        self.assertNotIn("cwso-secret-host", result.stderr + result.stdout)


if __name__ == "__main__":
    unittest.main()
