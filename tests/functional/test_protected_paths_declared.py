"""Repo-wide static guard: every agent source file must declare the T416 protected-paths
policy (`tests/golden/**` and `scripts/scorecard.py` are out of write scope for all agents),
and the two protected paths must actually exist on disk.

Refs T416; plan-035's risk table names this as the third of three independent controls
protecting held-out-set integrity for the rest of the roadmap (T412's path guard and T463's
evaluator-hash check -- not yet built -- are the other two).

Mirrors the established repo-wide static-guard pattern in
`tests/functional/test_link_integrity.py`, `tests/functional/test_check_version_consistency.py`,
and `tests/functional/test_golden_held_out_isolation.py`: walk the relevant files, flag
violations, hard-fail with every violation listed, and prove both a clean-pass and a
violation-detected direction via temp-directory/synthetic fixtures rather than only asserting
the real tree is currently clean.

## What this guard checks (and does not check)

Two checks, both declarative/auditable, per the design in
`docs/artifacts/protected-paths-v1.md` §4 ("What this does *not* do"):

- **Check A -- pointer presence.** Every `implementation/knowledge/agents/*.md` source file
  must contain the literal path token `docs/artifacts/protected-paths-v1.md` (the canonical
  policy doc reference) somewhere in its body. This is the guard's actual future value: if a
  28th agent is added later without the pointer, this check fails loudly and names the file.
- **Check B -- protected paths exist.** `tests/golden/` (a directory) and `scripts/scorecard.py`
  (a file) must actually exist on disk -- a sanity check that the thing being declared "frozen"
  is real, not a stale/aspirational reference.

This guard does **not** attempt commit-time or diff-time enforcement of the freeze itself (i.e.
it does not detect *if* someone edits `tests/golden/expect.py`) -- that is explicitly out of
scope for T416, see `docs/artifacts/protected-paths-v1.md` §4. It only proves the *declaration*
is present and consistent everywhere, and that the declared paths are real.

## Synthetic fixtures only

Per T412's held-out isolation discipline (still binding, read-only, during this task): no
fixture in this file references any real held-out case content or ID. Fixtures use synthetic
agent names/bodies and a synthetic protected-path token, mirroring
`test_golden_held_out_isolation.py`'s own `TestFindViolationsSyntheticFixtures` pattern.
"""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tests._helpers.repo import list_agents, repo_root

POLICY_DOC_TOKEN = "docs/artifacts/protected-paths-v1.md"


def find_agents_missing_pointer(agents_dir: Path) -> list[str]:
    """Scan every `*.md` file directly under `agents_dir` for `POLICY_DOC_TOKEN`. Returns a
    sorted list of file names (not full paths) missing the pointer. Pure / read-only."""
    missing: list[str] = []
    for agent_file in sorted(agents_dir.glob("*.md")):
        text = agent_file.read_text(encoding="utf-8", errors="ignore")
        if POLICY_DOC_TOKEN not in text:
            missing.append(agent_file.name)
    return sorted(missing)


def protected_paths_exist(root: Path) -> tuple[bool, bool]:
    """Returns (golden_dir_exists, scorecard_file_exists) for the two paths declared
    protected by `docs/artifacts/protected-paths-v1.md`."""
    golden_ok = (root / "tests" / "golden").is_dir()
    scorecard_ok = (root / "scripts" / "scorecard.py").is_file()
    return golden_ok, scorecard_ok


class TestFindAgentsMissingPointerSyntheticFixtures(unittest.TestCase):
    """Proves find_agents_missing_pointer() both catches an omission and passes on a clean
    fixture tree, using temp-directory fixtures with synthetic agent content -- mirrors
    test_golden_held_out_isolation.py's TestFindViolationsSyntheticFixtures pattern."""

    def test_clean_fixture_tree_has_no_missing_agents(self):
        with tempfile.TemporaryDirectory() as tmp_s:
            agents_dir = Path(tmp_s) / "agents"
            agents_dir.mkdir()
            (agents_dir / "synthetic-agent-one.md").write_text(
                "---\nname: \"Synthetic Agent One\"\n---\n\n"
                "# Synthetic Agent One\n\n## Constraints\n\n"
                "- Protected paths: see `docs/artifacts/protected-paths-v1.md`.\n"
            )
            (agents_dir / "synthetic-agent-two.md").write_text(
                "---\nname: \"Synthetic Agent Two\"\n---\n\n"
                "# Synthetic Agent Two\n\n## Constraints\n\n"
                "- Full policy: `docs/artifacts/protected-paths-v1.md`.\n"
            )
            self.assertEqual(find_agents_missing_pointer(agents_dir), [])

    def test_agent_missing_pointer_is_flagged(self):
        with tempfile.TemporaryDirectory() as tmp_s:
            agents_dir = Path(tmp_s) / "agents"
            agents_dir.mkdir()
            (agents_dir / "synthetic-agent-compliant.md").write_text(
                "---\nname: \"Synthetic Agent Compliant\"\n---\n\n"
                "## Constraints\n\n- See `docs/artifacts/protected-paths-v1.md`.\n"
            )
            (agents_dir / "synthetic-agent-noncompliant.md").write_text(
                "---\nname: \"Synthetic Agent Noncompliant\"\n---\n\n"
                "## Constraints\n\n- No pointer here at all.\n"
            )
            self.assertEqual(
                find_agents_missing_pointer(agents_dir),
                ["synthetic-agent-noncompliant.md"],
            )

    def test_multiple_missing_agents_are_all_listed(self):
        with tempfile.TemporaryDirectory() as tmp_s:
            agents_dir = Path(tmp_s) / "agents"
            agents_dir.mkdir()
            (agents_dir / "synthetic-agent-a.md").write_text("# A\nno pointer\n")
            (agents_dir / "synthetic-agent-b.md").write_text("# B\nno pointer either\n")
            self.assertEqual(
                find_agents_missing_pointer(agents_dir),
                ["synthetic-agent-a.md", "synthetic-agent-b.md"],
            )


class TestProtectedPathsExistSyntheticFixtures(unittest.TestCase):
    """Proves protected_paths_exist() correctly reports presence/absence using a synthetic
    temp-directory tree, not the real repo."""

    def test_both_paths_present(self):
        with tempfile.TemporaryDirectory() as tmp_s:
            tmp = Path(tmp_s)
            (tmp / "tests" / "golden").mkdir(parents=True)
            (tmp / "scripts").mkdir(parents=True)
            (tmp / "scripts" / "scorecard.py").write_text("# synthetic scorecard\n")
            self.assertEqual(protected_paths_exist(tmp), (True, True))

    def test_both_paths_missing(self):
        with tempfile.TemporaryDirectory() as tmp_s:
            tmp = Path(tmp_s)
            self.assertEqual(protected_paths_exist(tmp), (False, False))

    def test_only_golden_dir_present(self):
        with tempfile.TemporaryDirectory() as tmp_s:
            tmp = Path(tmp_s)
            (tmp / "tests" / "golden").mkdir(parents=True)
            self.assertEqual(protected_paths_exist(tmp), (True, False))


class TestRealRepoTreeIsCompliant(unittest.TestCase):
    """The guard actually executing against the real, current repo tree -- proves
    acceptance criterion 2 (all 27 agent source files carry the pointer) and criterion 1's
    "both protected paths are real" requirement, plus criterion 5 (this test runs as part
    of tests/run.py, not skipped)."""

    def test_all_agent_source_files_declare_protected_paths(self):
        agents = list_agents()
        agents_dir = agents[0].parent if agents else (
            repo_root() / "implementation" / "knowledge" / "agents"
        )
        missing = find_agents_missing_pointer(agents_dir)
        self.assertEqual(
            missing,
            [],
            msg="Agent source files missing the protected-paths pointer "
            f"({POLICY_DOC_TOKEN}):\n  " + "\n  ".join(missing),
        )

    def test_agent_source_directory_has_the_expected_28_agents(self):
        # Sanity check the scan target isn't accidentally empty or truncated -- a guard
        # that trivially passes because there's nothing to find would be worthless.
        # Was 27 through T453; T454 added the 28th (`context-retriever.md`) -- this
        # count is expected to be bumped by any future agent addition too, per this
        # file's own module docstring ("if a 28th agent is added later without the
        # pointer, this check fails loudly").
        self.assertEqual(len(list_agents()), 28)

    def test_both_protected_paths_exist_on_disk(self):
        golden_ok, scorecard_ok = protected_paths_exist(repo_root())
        self.assertTrue(golden_ok, msg="tests/golden/ does not exist on disk")
        self.assertTrue(scorecard_ok, msg="scripts/scorecard.py does not exist on disk")

    def test_canonical_policy_doc_exists(self):
        policy_doc = repo_root() / "docs" / "artifacts" / "protected-paths-v1.md"
        self.assertTrue(
            policy_doc.is_file(),
            msg=f"canonical protected-paths doc missing at {policy_doc}",
        )


if __name__ == "__main__":
    unittest.main()
