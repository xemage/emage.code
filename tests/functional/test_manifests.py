"""Validate platform manifests under implementation/platforms/."""
from __future__ import annotations

import json
import unittest

from tests._helpers.repo import implementation_root, list_platform_manifests


REQUIRED_KEYS = {"platform", "displayName", "outputDir", "fileMap", "frontmatter"}
KNOWN_FILE_KINDS = {"agents", "commands", "instructions", "skills"}


class TestPlatformManifests(unittest.TestCase):
    def test_at_least_four_platforms(self):
        manifests = list_platform_manifests()
        names = [p.stem for p in manifests]
        for required in ("github", "gemini", "opencode", "cursor", "claude-code"):
            self.assertIn(required, names, f"missing platform manifest: {required}")

    def test_manifests_parse_and_have_required_keys(self):
        for manifest_path in list_platform_manifests():
            with self.subTest(platform=manifest_path.stem):
                data = json.loads(manifest_path.read_text())
                missing = REQUIRED_KEYS - set(data)
                self.assertFalse(missing, f"{manifest_path.name}: missing keys {missing}")
                # outputDir must be a relative path (not absolute, not '..')
                output_dir = data["outputDir"]
                self.assertFalse(
                    output_dir.startswith("/") or output_dir.startswith(".."),
                    f"{manifest_path.name}: outputDir must be relative ({output_dir!r})",
                )

    def test_filemap_kinds_are_known(self):
        for manifest_path in list_platform_manifests():
            data = json.loads(manifest_path.read_text())
            file_map = data.get("fileMap", {})
            unknown = set(file_map) - KNOWN_FILE_KINDS
            with self.subTest(platform=manifest_path.stem):
                self.assertFalse(
                    unknown,
                    f"{manifest_path.name}: unknown fileMap kinds {unknown}",
                )

    def test_extras_paths_exist(self):
        for manifest_path in list_platform_manifests():
            data = json.loads(manifest_path.read_text())
            for extra in data.get("extras") or []:
                src = implementation_root() / extra["from"]
                with self.subTest(platform=manifest_path.stem, extra=extra["from"]):
                    self.assertTrue(
                        src.exists(),
                        f"{manifest_path.name}: extras[].from does not exist: {src}",
                    )


if __name__ == "__main__":
    unittest.main()
