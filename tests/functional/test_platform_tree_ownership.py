"""Orphan-tree guard (T662, ADR-010 D6/D7).

``sync.mjs`` removes and rewrites an output directory only for a platform whose
manifest exists, and ``sync.mjs --check`` and the root-parity gate compare only
files they would generate themselves. After a platform manifest is deleted, a
leftover or regrown ``.<platform>/`` tree is therefore invisible to every other
gate. This test closes that gap: a directory that carries a
``.generated-manifest.json`` must be the ``outputDir`` of a platform manifest
whose ``platform`` equals the one the directory's own manifest declares.

``.cursor`` (support removed in v9.0.0, ADR-010) is also asserted untracked by name,
at the repository root and under ``implementation/``, so that a revert is loud. The
by-name check uses ``git ls-files``: a tracked ``.cursor`` fails, while a ``.cursor``
that only exists locally and untracked (a developer's own Cursor IDE folder) does not.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from tests._helpers.repo import implementation_root, repo_root

MANIFEST_NAME = ".generated-manifest.json"
REMOVED_PLATFORM_DIRS = (".cursor",)


def owned_output_dirs(platforms_dir: Path) -> dict[str, str]:
    """outputDir -> platform, from every ``platforms/*.json`` not starting with ``_``."""
    owned: dict[str, str] = {}
    for path in sorted(platforms_dir.glob("*.json")):
        if path.name.startswith("_"):
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        owned[data["outputDir"].strip("/")] = data["platform"]
    return owned


def find_orphan_trees(base: Path, platforms_dir: Path) -> list[str]:
    """Names of the ``.<dir>`` children of ``base`` that carry a generated manifest
    but are not owned by a platform manifest (wrong directory or wrong platform)."""
    owned = owned_output_dirs(platforms_dir)
    orphans: list[str] = []
    for child in sorted(base.iterdir()):
        marker = child / MANIFEST_NAME
        if not child.name.startswith(".") or not child.is_dir() or not marker.is_file():
            continue
        try:
            platform = json.loads(marker.read_text(encoding="utf-8")).get("platform")
        except (OSError, ValueError):
            platform = None
        if owned.get(child.name) != platform:
            orphans.append(child.name)
    return orphans


class TestPlatformTreeOwnership(unittest.TestCase):
    def test_no_orphan_generated_tree_in_implementation(self) -> None:
        impl = implementation_root()
        self.assertEqual(find_orphan_trees(impl, impl / "platforms"), [])

    def test_no_orphan_generated_tree_at_the_repository_root(self) -> None:
        self.assertEqual(
            find_orphan_trees(repo_root(), implementation_root() / "platforms"), [])

    def test_every_manifest_output_dir_has_its_generated_tree(self) -> None:
        """The converse: a manifest without a tree (or a renamed outputDir) is caught too."""
        impl = implementation_root()
        for output_dir, platform in owned_output_dirs(impl / "platforms").items():
            with self.subTest(platform=platform):
                marker = json.loads((impl / output_dir / MANIFEST_NAME).read_text(encoding="utf-8"))
                self.assertEqual(marker["platform"], platform)

    def test_cursor_is_not_tracked_at_either_level(self) -> None:
        git = shutil.which("git")
        probe = None
        if git:
            probe = subprocess.run([git, "-C", str(repo_root()), "rev-parse", "--is-inside-work-tree"],
                                   capture_output=True, text=True, check=False)
        if not git or probe is None or probe.returncode != 0:
            reason = "git is not available or this is not a git checkout; cannot check tracked files"
            if os.environ.get("CI"):
                self.fail(reason + " (CI must run this check)")
            self.skipTest(reason)
        for base in (repo_root(), implementation_root()):
            for name in REMOVED_PLATFORM_DIRS:
                rel = (base / name).relative_to(repo_root()).as_posix()
                with self.subTest(path=rel):
                    listed = subprocess.run([git, "-C", str(repo_root()), "ls-files", "--", rel],
                                            capture_output=True, text=True, check=True).stdout
                    self.assertEqual(listed.strip(), "",
                                     f"{rel} is tracked: Cursor support was removed (ADR-010)")
        self.assertNotIn("cursor", owned_output_dirs(implementation_root() / "platforms").values())
        self.assertFalse((implementation_root() / "platforms" / "cursor.json").exists())


class TestOrphanGuardIsLoadBearing(unittest.TestCase):
    """The guard fails on a scratch copy that regains a Cursor tree (ADR-010 Validation 4)."""

    def _scratch(self, tmp: Path) -> tuple[Path, Path]:
        platforms = tmp / "platforms"
        platforms.mkdir()
        (platforms / "pi.json").write_text(
            json.dumps({"platform": "pi", "outputDir": ".pi"}), encoding="utf-8")
        (platforms / "_manifest.schema.json").write_text("{}", encoding="utf-8")
        (tmp / ".pi").mkdir()
        (tmp / ".pi" / MANIFEST_NAME).write_text(json.dumps({"platform": "pi"}), encoding="utf-8")
        return tmp, platforms

    def test_clean_scratch_copy_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base, platforms = self._scratch(Path(tmp))
            self.assertEqual(find_orphan_trees(base, platforms), [])

    def test_regrown_cursor_tree_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base, platforms = self._scratch(Path(tmp))
            (base / ".cursor").mkdir()
            (base / ".cursor" / MANIFEST_NAME).write_text(
                json.dumps({"platform": "cursor", "files": []}), encoding="utf-8")
            self.assertEqual(find_orphan_trees(base, platforms), [".cursor"])

    def test_tree_claimed_by_the_wrong_platform_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base, platforms = self._scratch(Path(tmp))
            (base / ".pi" / MANIFEST_NAME).write_text(
                json.dumps({"platform": "cursor"}), encoding="utf-8")
            self.assertEqual(find_orphan_trees(base, platforms), [".pi"])

    def test_unreadable_manifest_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base, platforms = self._scratch(Path(tmp))
            (base / ".pi" / MANIFEST_NAME).write_text("not json", encoding="utf-8")
            self.assertEqual(find_orphan_trees(base, platforms), [".pi"])


if __name__ == "__main__":
    unittest.main()
