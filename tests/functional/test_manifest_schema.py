"""`implementation/platforms/_manifest.schema.json` validates every platform manifest (T672, TD-T671-P8).

Every manifest declares `"$schema": "./_manifest.schema.json"`; before T672 that file did not exist
(a dangling reference in all the manifests). The schema is written from the keys `sync.mjs` reads,
refuses unknown keys, and is kept out of the platform list by its leading underscore.
"""
from __future__ import annotations

import copy
import json
import subprocess
import unittest

import jsonschema

from tests._helpers.repo import implementation_root, list_platform_manifests

PLATFORMS = implementation_root() / "platforms"
SCHEMA_PATH = PLATFORMS / "_manifest.schema.json"


class TestManifestSchema(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        cls.validator = jsonschema.Draft202012Validator(cls.schema)

    def test_schema_is_a_valid_schema(self) -> None:
        jsonschema.Draft202012Validator.check_schema(self.schema)

    def test_every_manifest_references_the_schema_and_validates(self) -> None:
        manifests = list_platform_manifests()
        self.assertGreaterEqual(len(manifests), 6)
        for path in manifests:
            with self.subTest(platform=path.stem):
                data = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(data["$schema"], "./_manifest.schema.json")
                self.assertTrue((path.parent / data["$schema"]).is_file(), "dangling $schema")
                self.assertEqual([e.message for e in self.validator.iter_errors(data)], [])

    def test_schema_is_not_a_platform(self) -> None:
        self.assertNotIn("_manifest.schema", [p.stem for p in list_platform_manifests()])
        registry = subprocess.run(
            ["python3", "-c",
             "import importlib.util,sys;"
             "s=importlib.util.spec_from_file_location('r', sys.argv[1]);m=importlib.util.module_from_spec(s);"
             "s.loader.exec_module(m);print(','.join(m._detect_platforms(__import__('pathlib').Path(sys.argv[2]))))",
             str(implementation_root() / "scripts" / "generate-registry.py"), str(implementation_root().parent)],
            capture_output=True, text=True, check=True).stdout.strip()
        self.assertEqual(registry, "claude-code,cline,gemini,github,opencode,pi")

    def test_only_the_schema_may_start_with_an_underscore(self) -> None:
        """T672 (SEC-T672-10): the registry generator and the test helper stop on any other `_*.json`."""
        import importlib.util
        import tempfile
        from pathlib import Path
        from unittest import mock

        import tests._helpers.repo as helpers

        spec = importlib.util.spec_from_file_location("registry_t672", implementation_root() / "scripts" / "generate-registry.py")
        registry = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(registry)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            platforms = root / "implementation" / "platforms"
            platforms.mkdir(parents=True)
            for name in ("pi.json", "_manifest.schema.json"):
                (platforms / name).write_text("{}", encoding="utf-8")
            self.assertEqual(registry._detect_platforms(root), ["pi"])
            with mock.patch.object(helpers, "implementation_root", return_value=root / "implementation"):
                self.assertEqual([p.name for p in helpers.list_platform_manifests()], ["pi.json"])
            (platforms / "_other.json").write_text("{}", encoding="utf-8")
            with self.assertRaises(SystemExit) as raised:
                registry._detect_platforms(root)
            self.assertIn("only _manifest.schema.json may start with an underscore", str(raised.exception))
            with mock.patch.object(helpers, "implementation_root", return_value=root / "implementation"):
                with self.assertRaises(AssertionError):
                    helpers.list_platform_manifests()

    def test_rel_path_still_accepts_ordinary_paths(self) -> None:
        """N-6 changed the lookahead: names that merely contain dots, and nested paths, stay valid."""
        base = json.loads((PLATFORMS / "claude-code.json").read_text(encoding="utf-8"))
        for value in (".claude", "a/b", "..foo", "a/..b/c", "a.b/c.d", ".clinerules"):
            with self.subTest(value):
                data = copy.deepcopy(base)
                data["outputDir"] = value
                self.assertEqual([e.message for e in self.validator.iter_errors(data)], [])

    def test_the_schema_catches_what_it_is_for(self) -> None:
        base = json.loads((PLATFORMS / "claude-code.json").read_text(encoding="utf-8"))
        mutations = {
            "a typo in a top-level key": lambda d: d.update(outptDir="x"),
            "a typo in a fileMap key": lambda d: d["fileMap"].update({"agentz": {"dir": "x", "ext": ".md"}}),
            "a typo in a frontmatter key": lambda d: d["frontmatter"]["agents"].update(keepKey=["name"]),
            "a typo in an mcp key": lambda d: d["mcp"].update(outputFiles="x"),
            "a missing required key": lambda d: d.pop("outputDir"),
            "an absolute outputDir": lambda d: d.update(outputDir="/etc"),
            "a parent outputDir": lambda d: d.update(outputDir="../x"),
            "the root as outputDir": lambda d: d.update(outputDir="."),
            "the parent itself as outputDir": lambda d: d.update(outputDir=".."),
            "an outputDir that climbs out": lambda d: d.update(outputDir="a/../.."),
            "an outputDir with a dot segment": lambda d: d.update(outputDir="a/./b"),
            "an outputDir that climbs out behind a newline": lambda d: d.update(outputDir="a\n/../.."),
            "an outputDir that is a parent segment behind a newline": lambda d: d.update(outputDir="a\n/.."),
            "a dot segment behind a newline": lambda d: d.update(outputDir="a\nb/./c"),
            "a dir that climbs out behind a newline": lambda d: d["fileMap"]["skills"].update(dir="x\n/../y"),
            "a dir that climbs out": lambda d: d["fileMap"]["skills"].update(dir="../x"),
            "an absolute dir": lambda d: d["fileMap"]["agents"].update(dir="/etc"),
            "an unknown mcp format": lambda d: d["mcp"].update(format="cursor"),
            "an unknown tool-name style": lambda d: d["frontmatter"]["agents"].update(mcpToolNames="dots"),
            "a bad tools mode": lambda d: d["frontmatter"]["agents"].update(tools="list"),
            "an extension without a dot": lambda d: d["fileMap"]["agents"].update(ext="md"),
            "a non-boolean rootRelative": lambda d: d["fileMap"]["instructions"].update(rootRelative="yes"),
        }
        for label, mutate in mutations.items():
            with self.subTest(label):
                data = copy.deepcopy(base)
                mutate(data)
                self.assertTrue(list(self.validator.iter_errors(data)), f"{label} was accepted")


if __name__ == "__main__":
    unittest.main()
