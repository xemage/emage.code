"""Focused tests for release note classification logic."""
from __future__ import annotations

import importlib.util
import unittest

from tests._helpers.repo import repo_root


def _load_publish_release_module():
    module_path = repo_root() / "scripts" / "publish-release.py"
    spec = importlib.util.spec_from_file_location("publish_release", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load publish-release module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestPublishReleaseClassification(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.publish_release = _load_publish_release_module()

    def test_conventional_subjects_map_to_expected_sections(self):
        grouped = self.publish_release.classify_subjects(
            [
                "feat(api): add release endpoint",
                "fix(ci): correct release gate bootstrap",
                "docs: update release runbook",
            ]
        )
        self.assertIn("add release endpoint", grouped["Features"])
        self.assertIn("correct release gate bootstrap", grouped["Bug Fixes"])
        self.assertIn("update release runbook", grouped["Documentation"])

    def test_merge_bugfix_subject_is_classified_as_bug_fix(self):
        grouped = self.publish_release.classify_subjects(
            ["Merge branch 'bugfix/39-release-docs-gate-python-bootstrap' into 'develop'"]
        )
        self.assertIn(
            "merge bugfix/39-release-docs-gate-python-bootstrap into develop",
            grouped["Bug Fixes"],
        )
        self.assertEqual(grouped["Other"], [])

    def test_release_branch_subject_is_classified_as_chore(self):
        grouped = self.publish_release.classify_subjects(["release/v2.0.2"])
        self.assertIn("release branch release/v2.0.2", grouped["Chores"])
        self.assertEqual(grouped["Other"], [])


if __name__ == "__main__":
    unittest.main()
