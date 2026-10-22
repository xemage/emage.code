"""`scripts/merge-mcp-json.py` robustness (T672): SEC-006, SEC-007, SEC-T658-05 (b) (c).

* an unreadable or non-JSON destination, source or sidecar is one line naming the file, exit 1 and
  nothing written -- never a traceback (and `--validate-only` is what install.sh runs up front);
* a user value the generator replaces (a `permission` rule, a `hooks` value) and a user key kept
  inside a generator-owned server's `env`/`headers` are reported on stderr, by name only;
* the destination and its sidecar are written through a temp file and `os.replace`.
"""
from __future__ import annotations

import importlib.util
import io
import json
import os
import stat
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

from tests._helpers.repo import repo_root

SCRIPT = repo_root() / "scripts" / "merge-mcp-json.py"
_spec = importlib.util.spec_from_file_location("merge_mcp_json_t672", SCRIPT)
merge = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(merge)


def _run(*argv: str) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with mock.patch("sys.argv", ["merge-mcp-json.py", *argv]), redirect_stdout(out), redirect_stderr(err):
        code = merge.main()
    return code, out.getvalue(), err.getvalue()


class TestMergeMcpJsonRobustness(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(prefix="emage-t672-merge-")
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name)

    def write(self, name: str, data) -> Path:
        path = self.tmp / name
        path.write_text(data if isinstance(data, str) else json.dumps(data, indent=2) + "\n", encoding="utf-8")
        return path

    # -- invalid input ---------------------------------------------------------------------
    def test_invalid_destination_is_one_line_naming_the_file(self) -> None:
        dest = self.write("dest.json", '{"a": 1, // comment\n}')
        source = self.write("source.json", {"a": 2})
        before = dest.read_bytes()
        code, _out, err = _run("--source", str(source), "--dest", str(dest))
        self.assertEqual(code, 1)
        self.assertEqual(len(err.strip().splitlines()), 1, err)
        self.assertIn(f"merge-mcp-json: {dest} is not valid JSON (", err)
        self.assertIn("nothing was written", err)
        self.assertNotIn("Traceback", err)
        self.assertEqual(dest.read_bytes(), before)

    def test_invalid_source_and_sidecars_are_refused_the_same_way(self) -> None:
        dest = self.write("dest.json", {"a": 1})
        for label, source_text, old_sidecar, new_sidecar in (
            ("source", "{nope", {"generatorOwnedKeys": []}, {"generatorOwnedKeys": []}),
            ("old sidecar", '{"a": 2}', "[1, 2]", {"generatorOwnedKeys": []}),
            ("new sidecar", '{"a": 2}', {"generatorOwnedKeys": []}, {"generatorOwnedKeys": "gitlab"}),
        ):
            with self.subTest(label):
                source = self.write("source.json", source_text)
                old = self.write("old.provenance.json", old_sidecar)
                new = self.write("new.provenance.json", new_sidecar)
                before = dest.read_bytes()
                code, _out, err = _run("--source", str(source), "--dest", str(dest),
                                       "--old-sidecar", str(old), "--new-sidecar", str(new))
                self.assertEqual(code, 1, err)
                self.assertNotIn("Traceback", err)
                self.assertEqual(dest.read_bytes(), before)

    def test_validate_only(self) -> None:
        good = self.write("good.json", {"a": 1})
        bad = self.write("bad.json", "{")
        sidecar = self.write("good.json.provenance.json", {"schemaVersion": 1, "generatorOwnedKeys": ["x"]})
        self.assertEqual(_run("--validate-only", "--dest", str(good), "--old-sidecar", str(sidecar))[0], 0)
        self.assertEqual(_run("--validate-only", "--dest", str(good),
                              "--old-sidecar", str(self.tmp / "missing.json"))[0], 0)
        code, _out, err = _run("--validate-only", "--dest", str(bad))
        self.assertEqual(code, 1)
        self.assertIn(f"{bad} is not valid JSON", err)
        sidecar.write_text("[]", encoding="utf-8")
        code, _out, err = _run("--validate-only", "--dest", str(good), "--old-sidecar", str(sidecar))
        self.assertEqual(code, 1)
        self.assertIn("is not a provenance sidecar", err)

    # -- notes -----------------------------------------------------------------------------
    def test_replaced_permission_rule_is_noted_and_an_equal_one_is_not(self) -> None:
        source = self.write("source.json", {"permission": {"playwright_a": "deny", "playwright_b": "deny"}})
        dest = self.write("dest.json", {"permission": {"playwright_a": "allow", "playwright_b": "deny", "x": "ask"}})
        code, _out, err = _run("--source", str(source), "--dest", str(dest))
        self.assertEqual(code, 0, err)
        self.assertEqual(err.strip().splitlines(),
                         [f"merge-mcp-json: note: {dest}: replaced your value for permission.playwright_a"])
        self.assertEqual(json.loads(dest.read_text())["permission"]["x"], "ask")

    def test_string_permission_shorthand_is_kept_as_a_wildcard(self) -> None:
        source = self.write("source.json", {"permission": {"playwright_a": "deny"}})
        dest = self.write("dest.json", {"permission": "allow"})
        code, _out, err = _run("--source", str(source), "--dest", str(dest))
        self.assertEqual((code, err), (0, ""))
        self.assertEqual(json.loads(dest.read_text())["permission"], {"*": "allow", "playwright_a": "deny"})

    def test_replaced_hooks_value_is_noted(self) -> None:
        source = self.write("source.json", {"hooks": {"AfterTool": [{"id": "generated"}]}})
        dest = self.write("dest.json", {"hooks": {"AfterTool": [{"id": "mine"}], "BeforeTool": []}})
        _code, _out, err = _run("--source", str(source), "--dest", str(dest))
        self.assertIn("replaced your value for hooks.AfterTool", err)
        self.assertNotIn("BeforeTool", err)

    def test_kept_env_and_headers_keys_are_noted_by_name_never_by_value(self) -> None:
        source = self.write("source.json", {"mcpServers": {"gitlab": {"command": "npx", "env": {"A": "${A}"}}}})
        dest = self.write("dest.json", {"mcpServers": {
            "gitlab": {"env": {"A": "x", "MY_SECRET_NAME": "s3cr3t-value"}},
            "own": {"env": {"ONLY_MINE": "v"}}}})
        code, _out, err = _run("--source", str(source), "--dest", str(dest))
        self.assertEqual(code, 0)
        self.assertIn("kept your key mcpServers.gitlab.env.MY_SECRET_NAME", err)
        self.assertNotIn("s3cr3t-value", err)
        self.assertNotIn("ONLY_MINE", err, "a server the generator does not own is not reported")
        merged = json.loads(dest.read_text())["mcpServers"]["gitlab"]["env"]
        self.assertEqual(merged["MY_SECRET_NAME"], "s3cr3t-value", "the key is still kept")

    def test_merge_json_without_notes_is_unchanged(self) -> None:
        """The signature the root-parity gate uses: merge_json(dest, source)."""
        self.assertEqual(merge.merge_json({"a": {"b": 1, "c": 2}}, {"a": {"b": 3}}), {"a": {"b": 3, "c": 2}})

    # -- atomic writes ---------------------------------------------------------------------
    def test_failed_replace_leaves_the_old_file_and_no_temp_file(self) -> None:
        source = self.write("source.json", {"a": 2})
        dest = self.write("dest.json", {"a": 1})
        before = dest.read_bytes()
        with mock.patch.object(merge.os, "replace", side_effect=OSError("disk gone")):
            code, _out, err = _run("--source", str(source), "--dest", str(dest))
        self.assertEqual(code, 1)
        self.assertEqual(len(err.strip().splitlines()), 1, err)
        self.assertIn("OSError: disk gone", err)
        self.assertNotIn("Traceback", err)
        self.assertEqual(dest.read_bytes(), before)
        self.assertEqual(sorted(p.name for p in self.tmp.iterdir()), ["dest.json", "source.json"])

    # -- SEC-T672-01: the temp file is never more readable than the file it replaces ---------------
    def test_temp_file_has_the_old_mode_before_any_content_is_written_and_a_random_name(self) -> None:
        dest = self.write("dest.json", {"a": 1, "env": {"TOKEN": "secret-value"}})
        dest.chmod(0o600)
        seen: dict = {}
        real_fchmod, real_replace = os.fchmod, os.replace
        def fchmod(fd, mode):
            seen["size_at_fchmod"] = os.fstat(fd).st_size
            seen["mode_before_fchmod"] = stat.S_IMODE(os.fstat(fd).st_mode)
            return real_fchmod(fd, mode)
        def replace(src, dst):
            seen["mode_at_replace"] = stat.S_IMODE(os.stat(src).st_mode)
            seen["tmp_name"] = os.path.basename(src)
            return real_replace(src, dst)
        with mock.patch.object(merge.os, "fchmod", side_effect=fchmod), \
             mock.patch.object(merge.os, "replace", side_effect=replace):
            merge.atomic_write_text(dest, '{"env": {"TOKEN": "secret-value"}}\n')
        self.assertEqual(seen["size_at_fchmod"], 0, "the mode must be set before the first byte is written")
        self.assertEqual(seen["mode_before_fchmod"], 0o600)
        self.assertEqual(seen["mode_at_replace"], 0o600, "no wider than the old file")
        self.assertNotIn(str(os.getpid()), seen["tmp_name"], "a predictable temp name")
        self.assertTrue(seen["tmp_name"].startswith(".dest.json.") and seen["tmp_name"].endswith(".tmp"))
        self.assertEqual(stat.S_IMODE(dest.stat().st_mode), 0o600)

    def test_new_file_gets_the_umask_mode_and_a_failed_write_leaves_no_temp_file(self) -> None:
        old = os.umask(0o027)
        self.addCleanup(os.umask, old)
        fresh = self.tmp / "fresh.json"
        merge.atomic_write_text(fresh, "{}\n")
        self.assertEqual(stat.S_IMODE(fresh.stat().st_mode), 0o640)
        with mock.patch.object(merge.os, "replace", side_effect=RuntimeError("boom")):
            with self.assertRaises(RuntimeError):
                merge.atomic_write_text(fresh, "{}\n")
        self.assertEqual(sorted(p.name for p in self.tmp.iterdir()), ["fresh.json"])

    # -- SEC-T658-05 (c) follow-ups -----------------------------------------------------------------
    def test_non_object_top_level_is_noted(self) -> None:
        source = self.write("source.json", {"mcpServers": {}})
        dest = self.write("dest.json", "[1, 2]")
        code, _out, err = _run("--source", str(source), "--dest", str(dest))
        self.assertEqual(code, 0)
        self.assertIn("the top level of your file is not a JSON object, so the whole file was replaced", err)
        self.assertEqual(json.loads(dest.read_text()), {"mcpServers": {}})

    def test_without_an_old_sidecar_the_kept_servers_are_named_with_a_pointer(self) -> None:
        source = self.write("source.json", {"mcpServers": {"gitlab": {}}})
        dest = self.write("dest.json", {"mcpServers": {"gitlab": {}, "zeta": {"command": "z"}, "alpha": {}}})
        new = self.write("source.json.provenance.json", {"schemaVersion": 1, "generatorOwnedKeys": ["gitlab"]})
        old = self.tmp / "dest.json.provenance.json"
        code, _out, err = _run("--source", str(source), "--dest", str(dest),
                               "--old-sidecar", str(old), "--new-sidecar", str(new))
        self.assertEqual(code, 0)
        lines = [ln for ln in err.splitlines() if "no provenance sidecar" in ln]
        self.assertEqual(len(lines), 1, err)
        self.assertIn("kept your server(s) alpha, zeta, which the generated config does not contain", lines[0])
        self.assertIn("--force-prune-keys <name>", lines[0])
        self.assertNotIn('"command"', err)

    def test_with_an_old_sidecar_that_note_is_not_printed(self) -> None:
        source = self.write("source.json", {"mcpServers": {"gitlab": {}}})
        dest = self.write("dest.json", {"mcpServers": {"gitlab": {}, "zeta": {}}})
        new = self.write("source.json.provenance.json", {"schemaVersion": 1, "generatorOwnedKeys": ["gitlab"]})
        old = self.write("dest.json.provenance.json", {"schemaVersion": 1, "generatorOwnedKeys": ["gitlab"]})
        _code, _out, err = _run("--source", str(source), "--dest", str(dest),
                                "--old-sidecar", str(old), "--new-sidecar", str(new))
        self.assertNotIn("no provenance sidecar", err)

    # -- SEC-T672-07 --------------------------------------------------------------------------------
    def test_nan_and_infinity_are_not_json(self) -> None:
        for text in ('{"a": NaN}', '{"a": Infinity}', '{"a": -Infinity}'):
            with self.subTest(text=text):
                dest = self.write("dest.json", text)
                code, _out, err = _run("--validate-only", "--dest", str(dest))
                self.assertEqual(code, 1)
                self.assertIn("is not valid JSON", err)
                self.assertIn("is not valid JSON", _run("--source", str(dest), "--dest", str(dest))[2])

    def test_a_deeply_nested_file_is_one_line_not_a_traceback(self) -> None:
        dest = self.write("dest.json", "[" * 200000 + "]" * 200000)
        code, _out, err = _run("--validate-only", "--dest", str(dest))
        self.assertEqual(code, 1)
        self.assertEqual(len(err.strip().splitlines()), 1)
        self.assertIn("is not valid JSON", err)

    def test_an_unexpected_os_error_is_one_line(self) -> None:
        source = self.write("source.json", {"a": 2})
        dest = self.write("dest.json", {"a": 1})
        with mock.patch.object(merge, "atomic_write_text", side_effect=PermissionError(13, "denied")):
            code, _out, err = _run("--source", str(source), "--dest", str(dest))
        self.assertEqual(code, 1)
        self.assertEqual(len(err.strip().splitlines()), 1, err)
        self.assertIn("PermissionError", err)

    @unittest.skipIf(os.geteuid() == 0, "root ignores directory permissions")
    def test_validate_only_refuses_a_directory_that_cannot_be_written(self) -> None:
        sub = self.tmp / "ro"
        sub.mkdir()
        dest = sub / "dest.json"
        dest.write_text("{}", encoding="utf-8")
        sub.chmod(0o555)
        self.addCleanup(sub.chmod, 0o755)
        code, _out, err = _run("--validate-only", "--dest", str(dest))
        self.assertEqual(code, 1)
        self.assertIn("not writable; nothing was written", err)
        sub.chmod(0o755)
        self.assertEqual(_run("--validate-only", "--dest", str(dest))[0], 0)

    def test_written_file_keeps_the_mode_of_the_old_one(self) -> None:
        source = self.write("source.json", {"a": 2})
        dest = self.write("dest.json", {"a": 1})
        dest.chmod(0o640)
        self.assertEqual(_run("--source", str(source), "--dest", str(dest))[0], 0)
        self.assertEqual(stat.S_IMODE(dest.stat().st_mode), 0o640)
        self.assertEqual(json.loads(dest.read_text()), {"a": 2})

    def test_sidecar_is_replaced_after_the_destination(self) -> None:
        source = self.write("source.json", {"mcpServers": {"new": {}}})
        dest = self.write("dest.json", {"mcpServers": {"old": {}}})
        old = self.write("dest.json.provenance.json", {"schemaVersion": 1, "generatorOwnedKeys": ["old"]})
        new = self.write("source.json.provenance.json", {"schemaVersion": 1, "generatorOwnedKeys": ["new"]})
        calls: list[str] = []
        real = os.replace
        def spy(src, dst):
            calls.append(Path(dst).name)
            return real(src, dst)
        with mock.patch.object(merge.os, "replace", side_effect=spy):
            code, _out, _err = _run("--source", str(source), "--dest", str(dest),
                                    "--old-sidecar", str(old), "--new-sidecar", str(new))
        self.assertEqual(code, 0)
        self.assertEqual(calls, ["dest.json", "dest.json.provenance.json"])
        self.assertEqual(json.loads(old.read_text())["generatorOwnedKeys"], ["new"])
        self.assertEqual(json.loads(dest.read_text()), {"mcpServers": {"new": {}}})

    def test_dry_run_writes_nothing(self) -> None:
        source = self.write("source.json", {"a": 2})
        dest = self.write("dest.json", {"a": 1})
        code, out, _err = _run("--source", str(source), "--dest", str(dest), "--dry-run")
        self.assertEqual(code, 0)
        self.assertIn("DRY-RUN: merge", out)
        self.assertEqual(json.loads(dest.read_text()), {"a": 1})
        self.assertEqual(sorted(p.name for p in self.tmp.iterdir()), ["dest.json", "source.json"])


if __name__ == "__main__":
    unittest.main()
