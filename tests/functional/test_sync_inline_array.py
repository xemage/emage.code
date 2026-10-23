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
import os
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


class YamlDivergenceTests(unittest.TestCase):
    """T672 (TL-T649-04): what YAML reads differently from this reader is refused, not mis-read."""

    _generated_args = SplitInlineArrayTests._generated_args
    _refused = SplitInlineArrayTests._refused

    REFUSED = {
        "[]": "empty inline array",
        '["a", "b",]': "trailing comma",
        "[a, b,]": "trailing comma",
        '["a",, "b"]': "empty item",
        "[a: b]": "mapping or collection",
        "[a:]": "mapping or collection",
        "[{}]": "mapping or collection",
        "[[x]]": "mapping or collection",
        "[{a: b}]": "mapping or collection",
        "[a, {b: c}]": "mapping or collection",
        "[*a]": "YAML indicator",
        "[&a x]": "YAML indicator",
        "[!t x]": "YAML indicator",
        "[|x]": "YAML indicator",
        "[>x]": "YAML indicator",
        "[@x]": "YAML indicator",
        "[%x]": "YAML indicator",
        "[`x]": "YAML indicator",
    }
    ACCEPTED = {
        "[a:b]": ["a:b"],
        '["a: b"]': ["a: b"],
        "['{}']": ["{}"],
        '[ "x" , y ]': ["x", "y"],
        "[a#b]": ["a#b"],
        '["", x]': ["", "x"],
        "[a, b]  # note": ["a", "b"],
        '["a # b", c] # d': ["a # b", "c"],
        "[a#b] # c": ["a#b"],
    }

    def test_each_refused_form_is_a_stop_with_its_own_message(self):
        for line, message in self.REFUSED.items():
            with self.subTest(line=line):
                self.assertIn(message, self._refused(line))

    def test_each_refused_form_really_differs_in_yaml(self):
        for line in self.REFUSED:
            with self.subTest(line=line):
                try:
                    parsed = yaml.safe_load(line)
                except yaml.YAMLError:
                    continue
                naive = [part.strip() for part in line[1:-1].split(",")]
                self.assertNotEqual(parsed, naive, "YAML agrees with the naive split: not a hazard")

    def test_a_comment_after_an_array_is_not_part_of_it(self):
        """T672 (TL-T649-09): `args: [a, b]  # note` used to be read as a scalar string."""
        self.assertEqual(self._generated_args("[a, b]   # note [x]"), ["a", "b"])

    def test_each_accepted_form_equals_yaml_safe_load(self):
        for line, expected in self.ACCEPTED.items():
            with self.subTest(line=line):
                self.assertEqual(yaml.safe_load(line), expected)
                self.assertEqual(self._generated_args(line), expected)


def _run_sync_with_manifests(manifests: dict[str, dict], extra_args: tuple[str, ...] = (), prepare=None,
                             root_arg=None, sync: Path = SYNC) -> tuple[subprocess.CompletedProcess, Path]:
    """`prepare(tmp)` runs before the generator (extra directories), `root_arg(tmp)` builds a --root
    spelling, `sync` is the script to run (T682: a relative path is a copy inside the scratch root)."""
    tmp = Path(tempfile.mkdtemp(prefix="t672-sync-"))
    (tmp / "platforms").mkdir()
    for sub in ("mcp", "instructions", "skills", "agents", "commands"):
        (tmp / "knowledge" / sub).mkdir(parents=True)
    (tmp / "knowledge" / "mcp" / "servers.yaml").write_text(_entry("[a]"), encoding="utf-8")
    base = json.loads(CLINE_MANIFEST.read_text(encoding="utf-8"))
    for name, patch in manifests.items():
        manifest = json.loads(json.dumps(base))
        manifest["platform"], manifest["outputDir"] = name, f".{name}"
        # Cline's rootRelative instructions directory is a removal target too: one per manifest (T682 N-5)
        manifest["fileMap"]["instructions"]["dir"] = f".{name}-rules"
        patch(manifest)
        (tmp / "platforms" / f"{name}.json").write_text(json.dumps(manifest), encoding="utf-8")
    if prepare is not None:
        prepare(tmp)
    root = root_arg(tmp) if root_arg is not None else str(tmp)
    script = sync if sync.is_absolute() else tmp / sync
    proc = subprocess.run(["node", str(script), "--root", root, *extra_args], capture_output=True, text=True,
                          check=False)
    return proc, tmp


class ManifestsAreValidatedBeforeTheFirstWriteTests(unittest.TestCase):
    """T672 (SEC-T658-07 b, TL-T649-03): a bad manifest sorted AFTER a good one writes nothing."""

    def _assert_nothing_written(self, patch) -> str:
        proc, tmp = _run_sync_with_manifests({"aaa": lambda m: None, "zzz": patch})
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        self.assertNotEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertFalse((tmp / ".aaa").exists(), "the good manifest was written before the bad one was read")
        self.assertFalse((tmp / ".zzz").exists())
        return proc.stdout + proc.stderr

    def test_unknown_mcp_tool_name_style(self):
        def patch(m):
            m["frontmatter"]["agents"] = {"tools": "array", "mcpToolNames": "bogus"}
        self.assertIn("Unknown mcpToolNames style", self._assert_nothing_written(patch))

    def test_root_relative_target_outside_the_root(self):
        def patch(m):
            m["fileMap"]["instructions"] = {"dir": "../escape", "ext": ".md", "rootRelative": True}
        self.assertIn("Refusing rootRelative fileMap target", self._assert_nothing_written(patch))

    def test_every_manifest_derived_path_must_stay_strictly_under_the_root(self):
        """T672 (SEC-T672-08): outputDir "." would `rm -rf` the whole root; the rest would write outside it."""
        import uuid
        escape = f"t672-escape-{uuid.uuid4().hex}.json"  # never a name another run could have left behind
        cases = {
            "outputDir is the root": lambda m: m.update(outputDir="."),
            "outputDir is the parent": lambda m: m.update(outputDir=".."),
            "outputDir climbs out": lambda m: m.update(outputDir="a/../.."),
            "outputDir is absolute": lambda m: m.update(outputDir="/tmp/t672-never"),
            "mcp.outputFile climbs out": lambda m: m["mcp"].update(outputFile=f"../../{escape}"),
            "extras.to climbs out": lambda m: m.update(extras=[{"from": "_extras/x", "to": "../escape"}]),
            "skills.dir climbs out": lambda m: m["fileMap"]["skills"].update(dir="../../escape"),
            "skills.dir is absolute": lambda m: m["fileMap"]["skills"].update(dir="/tmp/t672-never"),
            "instructions.dir climbs out": lambda m: m["fileMap"]["instructions"].update(dir="../../escape"),
        }
        for label, patch in cases.items():
            with self.subTest(label):
                proc, tmp = _run_sync_with_manifests({"aaa": lambda m: None, "zzz": patch})
                self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
                self.assertNotEqual(proc.returncode, 0, proc.stdout + proc.stderr)
                self.assertIn("Refusing", proc.stdout + proc.stderr)
                self.assertFalse((tmp / ".aaa").exists(), "the good manifest was written first")
                self.assertTrue((tmp / "knowledge" / "mcp" / "servers.yaml").is_file(), "the root was emptied")
                self.assertFalse((tmp.parent / escape).exists())
                self.addCleanup((tmp.parent / escape).unlink, missing_ok=True)

    # -- T682 N-4 / N-5 ----------------------------------------------------------------------------
    def test_an_absolute_root_is_normalised(self):
        """N-4: "<tmp>/x/../" and "<tmp>//" name the root, and are not refused as "outside" it."""
        for label, spell in (("dot-dot and trailing slash", lambda t: f"{t}/x/../"),
                             ("doubled slash", lambda t: f"{t}//"),
                             ("dot segment", lambda t: f"{t}/./")):
            with self.subTest(label):
                proc, tmp = _run_sync_with_manifests({"aaa": lambda m: None}, root_arg=spell)
                self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
                self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
                self.assertTrue((tmp / ".aaa" / "mcp.json").is_file())

    def _assert_refused(self, manifests, message, **kwargs):
        proc, tmp = _run_sync_with_manifests(manifests, **kwargs)
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        self.assertNotEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn(message, proc.stdout + proc.stderr)
        self.assertFalse((tmp / ".aaa").exists(), "a manifest was written before the refusal")
        self.assertTrue((tmp / "knowledge" / "mcp" / "servers.yaml").is_file(), "a generator input was deleted")
        return tmp

    def test_an_output_tree_must_not_overlap_a_generator_input(self):
        """N-5: outputDir "knowledge" (or inside it, or above `_extras`) would be `rm -rf`-ed before it is read."""
        def make(*dirs):
            def prepare(tmp):
                for d in dirs:
                    (tmp / d).mkdir(parents=True, exist_ok=True)
            return prepare
        for output_dir in ("knowledge", "platforms", "_extras", "scripts", "runtime", "knowledge/sub",
                           "runtime/x/y", "scripts/out"):
            with self.subTest(outputDir=output_dir):
                self._assert_refused({"aaa": lambda m: None, "zzz": lambda m, d=output_dir: m.update(outputDir=d)},
                                     "overlaps the generator input", prepare=make("_extras", "scripts", "runtime"))
        with self.subTest("outputDir contains an input passed with --extras"):
            tmp = self._assert_refused({"aaa": lambda m: None, "zzz": lambda m: m.update(outputDir="ex")},
                                       "overlaps the generator input", prepare=make("ex/tras"),
                                       extra_args=("--extras=ex/tras",))
            self.assertTrue((tmp / "ex" / "tras").is_dir())
        with self.subTest("the rootRelative instructions directory is a removal target too"):
            self._assert_refused({"aaa": lambda m: None, "zzz": lambda m: m["fileMap"]["instructions"].update(dir="knowledge")},
                                 "overlaps the generator input")

    def test_the_generators_own_directory_is_an_input(self):
        def copy_sync(tmp):
            (tmp / "tools").mkdir()
            shutil.copy(SYNC, tmp / "tools" / "sync.mjs")
        for output_dir in ("tools", "tools/out"):
            with self.subTest(outputDir=output_dir):
                self._assert_refused({"aaa": lambda m: None, "zzz": lambda m, d=output_dir: m.update(outputDir=d)},
                                     "overlaps the generator input", prepare=copy_sync, sync=Path("tools/sync.mjs"))

    def test_output_trees_of_two_manifests_must_not_overlap(self):
        cases = {
            "equal": lambda m: m.update(outputDir=".aaa"),
            "inside": lambda m: m.update(outputDir=".aaa/sub"),
            "same rootRelative directory": lambda m: m["fileMap"]["instructions"].update(dir=".aaa-rules"),
            "rootRelative inside the other output tree": lambda m: m["fileMap"]["instructions"].update(dir=".aaa/rules"),
        }
        for label, patch in cases.items():
            with self.subTest(label):
                self._assert_refused({"aaa": lambda m: None, "zzz": patch}, " overlaps ")

    # -- T684 SEC-T682-04 ----------------------------------------------------------------------------
    def test_the_mcp_files_must_not_overlap_a_generator_input(self):
        """A manifest whose mcp.outputFile (or its .provenance.json) lands in an input would overwrite it."""
        cases = {
            "the servers file itself": "../knowledge/mcp/servers.yaml",
            "a new file in knowledge": "../knowledge/new.json",
            "a manifest": "../platforms/aaa.json",
            "inside scripts": "../scripts/x.json",
            "inside runtime": "../runtime/a/b.json",
            "inside _extras": "../_extras/x.json",
            "climbing back in": "../.zzz/../knowledge/mcp/servers.yaml",
        }
        for label, output_file in cases.items():
            with self.subTest(label):
                tmp = self._assert_refused(
                    {"aaa": lambda m: None, "zzz": lambda m, o=output_file: m["mcp"].update(outputFile=o)},
                    "overlaps the generator input",
                    prepare=lambda tmp: [(tmp / d).mkdir(exist_ok=True) for d in ("scripts", "runtime", "_extras")])
                self.assertEqual((tmp / "knowledge" / "mcp" / "servers.yaml").read_text(encoding="utf-8"), _entry("[a]"))
        with self.subTest("only the provenance sidecar lands in an input"):
            self._assert_refused(
                {"aaa": lambda m: None, "zzz": lambda m: m["mcp"].update(outputFile="../out.json")},
                "overlaps the generator input", extra_args=("--extras=out.json.provenance.json",))

    def test_a_different_case_or_a_symlink_does_not_hide_an_overlap(self):
        """The comparison uses the physical, case-folded form of both sides."""
        def link(name, to):
            def prepare(tmp):
                os.symlink(tmp / to, tmp / name, target_is_directory=True)
            return prepare
        def link_file(tmp):
            os.symlink(tmp / "knowledge" / "mcp" / "servers.yaml", tmp / "lnk.json")
        def dangling(tmp):
            os.symlink(tmp / "knowledge" / "not-yet", tmp / ".zzz")
        def two_hops(tmp):
            os.symlink(tmp / "knowledge", tmp / "hop1")
            os.symlink(tmp / "hop1", tmp / "hop2")
        def input_is_a_link(tmp):
            shutil.move(str(tmp / "knowledge"), str(tmp / "real-k"))
            os.symlink(tmp / "real-k", tmp / "knowledge", target_is_directory=True)
        cases = {
            "outputDir is the real directory behind a symlinked input": ({"outputDir": "real-k"}, input_is_a_link),
            "outputDir upper-case": ({"outputDir": "Knowledge"}, None),
            "outputDir inside an upper-case input": ({"outputDir": "KNOWLEDGE/sub"}, None),
            "mcp file in an upper-case input": ({"mcp": "../Knowledge/x.json"}, None),
            "outputDir is a symlink to knowledge": ({"outputDir": "link"}, link("link", "knowledge")),
            "outputDir inside a symlink to knowledge": ({"outputDir": "link/sub"}, link("link", "knowledge")),
            "outputDir is a dangling symlink into knowledge": ({"outputDir": ".zzz"}, dangling),
            "outputDir behind two symlinks": ({"outputDir": "hop2"}, two_hops),
            "mcp file below a symlink to knowledge": ({"mcp": "../link/mcp/servers.yaml"}, link("link", "knowledge")),
            "mcp file is a symlink to the servers file": ({"mcp": "../lnk.json"}, link_file),
            "rootRelative instructions dir is a symlink to knowledge":
                ({"rules": "link"}, link("link", "knowledge")),
        }
        for label, (change, prepare) in cases.items():
            def patch(m, change=change):
                if "outputDir" in change:
                    m["outputDir"] = change["outputDir"]
                if "mcp" in change:
                    m["mcp"]["outputFile"] = change["mcp"]
                if "rules" in change:
                    m["fileMap"]["instructions"]["dir"] = change["rules"]
            with self.subTest(label):
                tmp = self._assert_refused({"aaa": lambda m: None, "zzz": patch}, "overlaps the generator input",
                                           prepare=prepare)
                self.assertEqual((tmp / "knowledge" / "mcp" / "servers.yaml").read_text(encoding="utf-8"), _entry("[a]"))
                self.assertEqual(os.listdir(tmp / "knowledge" / "mcp"), ["servers.yaml"])

    def test_an_output_tree_reached_through_a_symlink_to_another_output_tree_is_refused(self):
        def prepare(tmp):
            os.symlink(tmp / ".aaa", tmp / "alias", target_is_directory=True)    # dangling until .aaa exists
        self._assert_refused({"aaa": lambda m: None, "zzz": lambda m: m.update(outputDir="alias/sub")}, " overlaps ",
                             prepare=prepare)

    def test_a_root_spelled_through_a_symlink_is_not_refused(self):
        """No false positive: inputs and targets are both compared in their physical form."""
        def spelled(tmp):
            lnk = Path(str(tmp) + "-lnk")
            os.symlink(tmp, lnk, target_is_directory=True)
            self.addCleanup(lnk.unlink, missing_ok=True)
            return str(lnk)
        proc, tmp = _run_sync_with_manifests({"aaa": lambda m: None, "zzz": lambda m: None}, root_arg=spelled)
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertTrue((tmp / ".zzz" / "mcp.json").is_file())

    def test_a_unicode_normalisation_difference_does_not_hide_an_overlap(self):
        """NFC "caf\u00e9" (the input) and NFD "cafe\u0301/sub" (the output) are one place on some file systems."""
        self._assert_refused({"aaa": lambda m: None, "zzz": lambda m: m.update(outputDir="cafe\u0301/sub")},
                             "overlaps the generator input", extra_args=("--extras=caf\u00e9",))

    @unittest.skipIf(os.geteuid() == 0, "root can read a directory without permission bits")
    def test_a_target_below_an_unreadable_directory_is_refused_not_skipped(self):
        def prepare(tmp):
            (tmp / "closed").mkdir()
            (tmp / "closed").chmod(0)
            self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)    # runs after the chmod below
            self.addCleanup((tmp / "closed").chmod, 0o755)
        self._assert_refused({"aaa": lambda m: None, "zzz": lambda m: m.update(outputDir="closed/sub")},
                             "cannot resolve", prepare=prepare)

    def test_an_unresolvable_target_is_refused_not_skipped(self):
        def prepare(tmp):
            for name in ("a", "b"):
                os.symlink(tmp / ("b" if name == "a" else "a"), tmp / name)
        self._assert_refused({"aaa": lambda m: None, "zzz": lambda m: m.update(outputDir="a/x")}, "Refusing", prepare=prepare)

    def test_an_extras_source_must_stay_under_the_extras_directory(self):
        """N-5: `extras.from` was asserted against ROOT, so "../knowledge/..." was read as an extra."""
        for source in ("_extras/../knowledge/mcp/servers.yaml", "../knowledge/mcp/servers.yaml", "_extras/.."):
            with self.subTest(source):
                self._assert_refused(
                    {"aaa": lambda m: None,
                     "zzz": lambda m, s=source: m.update(extras=[{"from": s, "to": "copy"}])},
                    "extras.from of zzz outside or equal to", prepare=lambda tmp: (tmp / "_extras").mkdir())

    def test_only_the_manifest_schema_may_start_with_an_underscore(self):
        proc, tmp = _run_sync_with_manifests({"aaa": lambda m: None, "_other": lambda m: None})
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        self.assertNotEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("only _manifest.schema.json may start with an underscore", proc.stdout + proc.stderr)
        self.assertFalse((tmp / ".aaa").exists())

    def test_the_manifest_schema_is_skipped(self):
        proc, tmp = _run_sync_with_manifests({"aaa": lambda m: None, "_manifest.schema": lambda m: None})
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertTrue((tmp / ".aaa").is_dir())
        self.assertFalse((tmp / "._manifest.schema").exists())

    def test_two_good_manifests_are_both_written(self):
        proc, tmp = _run_sync_with_manifests({"aaa": lambda m: None, "zzz": lambda m: None})
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertTrue((tmp / ".aaa" / "mcp.json").is_file())
        self.assertTrue((tmp / ".zzz" / "mcp.json").is_file())


if __name__ == "__main__":
    unittest.main()
