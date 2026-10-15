"""T656 (SEC-T655-04) -- the inline-array reader of `implementation/scripts/sync.mjs`.

`splitInlineArray` is the hand-written reader for the `args: [...]` lines of `servers.yaml`.
It must agree with `yaml.safe_load` for every shipped entry, and it must refuse (not silently
mis-read) what it cannot read faithfully: a backslash inside a quoted item, an unclosed quote and
text after a closing quote.

The reader is not exported, so each test runs the real engine (`node sync.mjs --root <tmp>`)
on a scratch root that holds one platform manifest (Cline, which has no agents or skills to
project) and a scratch `servers.yaml`. No network, nothing outside the scratch directory is
written.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

import yaml

from tests._helpers.repo import implementation_root

SYNC = implementation_root() / "scripts" / "sync.mjs"
CLINE_MANIFEST = implementation_root() / "platforms" / "cline.json"
SERVERS_YAML = implementation_root() / "knowledge" / "mcp" / "servers.yaml"


def _run_sync(servers_yaml_text: str) -> tuple[subprocess.CompletedProcess, Path]:
    tmp = Path(tempfile.mkdtemp(prefix="t656-sync-"))
    (tmp / "platforms").mkdir()
    for sub in ("mcp", "instructions", "skills", "agents", "commands"):
        (tmp / "knowledge" / sub).mkdir(parents=True)
    shutil.copy(CLINE_MANIFEST, tmp / "platforms" / "cline.json")
    (tmp / "knowledge" / "mcp" / "servers.yaml").write_text(servers_yaml_text, encoding="utf-8")
    proc = subprocess.run(
        ["node", str(SYNC), "--root", str(tmp)],
        capture_output=True, text=True, check=False,
    )
    return proc, tmp


def _entry(args_line: str) -> str:
    return (
        "servers:\n"
        "  probe:\n"
        "    tags: [core]\n"
        "    transport: stdio\n"
        "    command: npx\n"
        f"    args: {args_line}\n"
    )


class SplitInlineArrayTests(unittest.TestCase):
    def _generated_args(self, args_line: str) -> list[str]:
        proc, tmp = _run_sync(_entry(args_line))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        cfg = json.loads((tmp / ".cline" / "mcp.json").read_text(encoding="utf-8"))
        return cfg["mcpServers"]["probe"]["args"]

    def _refused(self, args_line: str) -> str:
        proc, tmp = _run_sync(_entry(args_line))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        self.assertNotEqual(proc.returncode, 0, "the reader must refuse: " + args_line)
        self.assertFalse((tmp / ".cline" / "mcp.json").exists(), "nothing may be generated")
        return proc.stdout + proc.stderr

    def test_reader_matches_yaml_safe_load_for_every_shipped_entry(self):
        shipped = yaml.safe_load(SERVERS_YAML.read_text(encoding="utf-8"))["servers"]
        proc, tmp = _run_sync(SERVERS_YAML.read_text(encoding="utf-8"))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        generated = json.loads((tmp / ".cline" / "mcp.json").read_text(encoding="utf-8"))["mcpServers"]
        stdio = {k: v for k, v in shipped.items() if v.get("transport") == "stdio"}
        self.assertTrue(stdio)
        for name, entry in stdio.items():
            self.assertEqual(generated[name]["command"], entry["command"], name)
            self.assertEqual(generated[name]["args"], [str(a) for a in entry["args"]], name)

    def test_quoted_item_keeps_commas_semicolons_braces_and_brackets(self):
        value = "a,b;c{1,2}.*;[x]"
        self.assertEqual(self._generated_args(f'["-y", "{value}", plain]'), ["-y", value, "plain"])

    def test_single_quoted_item_is_one_argument(self):
        self.assertEqual(self._generated_args("['a,b', c]"), ["a,b", "c"])

    def test_apostrophe_inside_a_plain_item_is_plain_text(self):
        self.assertEqual(self._generated_args("[don't, x]"), ["don't", "x"])

    def test_backslash_inside_a_double_quoted_item_is_refused(self):
        self.assertIn("backslash", self._refused('["a\\\\b", "c"]'))

    def test_backslash_inside_a_single_quoted_item_is_refused(self):
        self.assertIn("backslash", self._refused("['a\\b']"))

    def test_escaped_quote_inside_a_quoted_item_is_refused(self):
        self.assertIn("backslash", self._refused('["say \\"hi\\"", x]'))

    def test_unclosed_quote_is_refused(self):
        self.assertIn("unclosed quote", self._refused('["-y", "abc, def]'))

    def test_text_after_a_closing_quote_is_refused(self):
        self.assertIn("after the closing quote", self._refused('["a"b, c]'))


if __name__ == "__main__":
    unittest.main()
