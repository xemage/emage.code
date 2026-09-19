"""Regression tests for implementation/scripts/check-maturity.py (T432).

Proves, per task-T432's acceptance criteria 1/2/3:
  1. a component claiming a level it does not satisfy fails with a message
     naming the specific unmet criterion, and
  2. a component satisfying every stated criterion for its claimed level
     passes, and
  3. the checker runs against the real, current 77-component registry
     without crashing and reports the true pass/fail distribution.
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

from tests._helpers.repo import repo_root


def _load_module():
    module_path = repo_root() / "implementation" / "scripts" / "check-maturity.py"
    spec = importlib.util.spec_from_file_location("check_maturity", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load check-maturity module")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


RAILS_BLOCK = textwrap.dedent(
    """
    ## Rails
    **Inputs**: a widget id.
    **Out of scope**: does not delete widgets.
    **Failure mode**: reports an error and exits non-zero.
    """
)


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _scaffold(tmp: Path) -> Path:
    """Build a minimal synthetic repo tree the checker can run against."""
    real_repo = repo_root()
    _write(tmp / ".gitlab-ci.yml", "stages: []\n")
    _write(
        tmp / "AGENTS.md",
        "## Skill Workflow (mandatory)\n\n"
        "| Situation | Required skill |\n|---|---|\n"
        "| Demo | `demo-skill` |\n\n"
        "## Code Standards\n- nothing here.\n\n"
        "## Security\n- nothing here.\n",
    )
    impl = tmp / "implementation"
    (impl / "scripts").mkdir(parents=True)
    for name in ("generate-registry.py",):
        src = real_repo / "implementation" / "scripts" / name
        (impl / "scripts" / name).write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    schemas_src = real_repo / "implementation" / "knowledge" / "schemas"
    for schema_file in schemas_src.glob("*.schema.json"):
        dest = impl / "knowledge" / "schemas" / schema_file.name
        _write(dest, schema_file.read_text(encoding="utf-8"))
    for sub in ("agents", "commands", "instructions"):
        (impl / "knowledge" / sub).mkdir(parents=True, exist_ok=True)
    (impl / "knowledge" / "skills").mkdir(parents=True, exist_ok=True)
    _write(tmp / "docs" / "tasks" / "active-tasks.md", "# Active Tasks\n\n| ID | Title | Owner | Status | Priority | Depends on | Last update |\n|---|---|---|---|---|---|---|\n")
    _write(tmp / "docs" / "tasks" / "completed-tasks.md", "# Completed Tasks\n\n| ID | Title | Owner | Done on | Outcome / artifact |\n|---|---|---|---|---|\n")
    _write(tmp / "docs" / "wiki" / "overview.md", "# Overview\n")
    (tmp / "tests" / "golden" / "open").mkdir(parents=True)
    (tmp / "tests" / "golden" / "held-out").mkdir(parents=True)
    (tmp / "tests" / "functional").mkdir(parents=True)
    return impl


class TestCheckMaturityPureHelpers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def test_rails_check_passes_for_well_formed_section(self):
        self.assertIsNone(self.mod._rails_check(RAILS_BLOCK))

    def test_rails_check_fails_when_heading_absent(self):
        reason = self.mod._rails_check("no rails here")
        self.assertIn("missing a `## Rails`", reason)

    def test_rails_check_fails_when_label_empty(self):
        broken = "## Rails\n**Inputs**:\n**Out of scope**: none.\n**Failure mode**: errors.\n"
        reason = self.mod._rails_check(broken)
        self.assertIn("Inputs", reason)

    def test_deprecation_check_requires_notice_when_deprecated(self):
        reason = self.mod._deprecation_check("deprecated", "no notice body", set())
        self.assertIn("no `## Deprecation Notice`", reason)

    def test_deprecation_check_rejects_notice_on_non_deprecated(self):
        body = "## Deprecation Notice\n**Reason**: retired.\n**Removal target**: v1.0.0\n"
        reason = self.mod._deprecation_check("beta", body, set())
        self.assertIn("not `deprecated`", reason)

    def test_deprecation_check_passes_with_removal_target(self):
        body = "## Deprecation Notice\n**Reason**: superseded.\n**Removal target**: v6.16.0\n"
        self.assertIsNone(self.mod._deprecation_check("deprecated", body, set()))

    def test_deprecation_check_passes_with_resolvable_replacement(self):
        body = "## Deprecation Notice\n**Reason**: superseded.\n**Replacement**: new-thing\n"
        self.assertIsNone(self.mod._deprecation_check("deprecated", body, {"new-thing"}))

    def test_documented_check_rejects_character_padding_attack(self):
        """Reproduces the exact T432 adversarial-review finding: a wiki line
        whose remainder clears the raw 40-non-whitespace-character floor
        purely via a run of one repeated filler character, with zero real
        word content, used to be accepted as "documented". It must now fail.
        """
        padding_line = "skillify " + "x" * 45
        reason = self.mod._documented_check(
            "skill", "skillify", "", self._ctx_with_wiki_line(padding_line)
        )
        self.assertIsNotNone(reason, "character-padding line should not count as documentation")
        self.assertIn("not documented in docs/wiki/**", reason)

    def test_documented_check_rejects_repeated_word_padding_attack(self):
        """A follow-up variation on the same attack: repeating one real word
        many times instead of one character. Must also fail -- otherwise the
        distinct-word gate would be trivially bypassable.
        """
        padding_line = "skillify " + "blah " * 10
        reason = self.mod._documented_check(
            "skill", "skillify", "", self._ctx_with_wiki_line(padding_line)
        )
        self.assertIsNotNone(reason, "single-word-repeated padding should not count as documentation")

    def test_documented_check_passes_for_genuine_prose_description(self):
        """A legitimate, hand-written wiki description -- real, varied,
        vowel-bearing prose, not padding -- must still pass. The hardened
        heuristic must not introduce false negatives on real documentation.
        """
        real_line = (
            "skillify walks a maintainer through turning ad-hoc repeated "
            "steps into a reusable, documented skill for this project."
        )
        reason = self.mod._documented_check(
            "skill", "skillify", "", self._ctx_with_wiki_line(real_line)
        )
        self.assertIsNone(reason, f"genuine prose should pass documentation check, got: {reason}")

    def _ctx_with_wiki_line(self, line: str):
        """Build a minimal Context whose only wiki file is a single line,
        for isolated testing of `_documented_check`/`_documented_in_wiki`.
        """
        tmp = Path(tempfile.mkdtemp())
        wiki_path = tmp / "home.md"
        _write(wiki_path, line + "\n")
        return self.mod.Context(
            repo_root=tmp,
            source_root=tmp,
            schemas_dir=tmp,
            entries=[],
            command_agent={},
            agent_commands={},
            agent_ids=set(),
            command_ids=set(),
            all_ids=set(),
            golden_cases=[],
            active_rows=[],
            completed_rows=[],
            wiki_files=[wiki_path],
            agents_md_text="",
            other_agent_files={},
            other_command_files={},
            functional_test_files=[],
            golden_expect_files=[],
        )


class TestCheckMaturitySyntheticRegistry(unittest.TestCase):
    def test_stable_claim_missing_every_addition_fails_naming_criteria(self):
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            impl = _scaffold(tmp)
            _write(
                impl / "knowledge" / "agents" / "broken-agent.md",
                "---\nname: \"Broken Agent\"\ndescription: \"A broken agent for testing.\"\n"
                "maturity: stable\n---\n\nNo rails, no evidence, no references.\n",
            )
            mod = _load_module()
            ctx = mod.build_context(impl)
            self.assertEqual(len(ctx.entries), 1, "fixture should contain exactly one component")
            component = mod._build_component(ctx.entries[0], ctx.source_root)
            failures = mod.check_component(component, ctx)
            joined = "\n".join(failures)
            self.assertIn("experimental->beta #2", joined)
            self.assertIn("beta->stable #4", joined)
            self.assertIn("beta->stable #5", joined)
            self.assertIn("beta->stable #6", joined)

    def test_stable_claim_satisfying_every_criterion_passes(self):
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            impl = _scaffold(tmp)

            _write(
                impl / "knowledge" / "commands" / "demo-command.md",
                "---\ndescription: \"Runs the demo workflow end to end.\"\n"
                "agent: \"demo-agent\"\nmaturity: stable\n---\n"
                + RAILS_BLOCK
                + "\nSee instruction `demo-instruction` for the routing rule.\n",
            )
            _write(
                impl / "knowledge" / "agents" / "demo-agent.md",
                "---\nname: \"Demo Agent\"\ndescription: \"Owns the demo command end to end.\"\n"
                "maturity: stable\n---\n"
                + RAILS_BLOCK,
            )
            _write(
                impl / "knowledge" / "instructions" / "demo-instruction.md",
                "---\ndescription: \"Rules for demo routing behaviour.\"\nmaturity: stable\n---\n"
                + RAILS_BLOCK,
            )
            _write(
                impl / "knowledge" / "skills" / "demo-skill" / "SKILL.md",
                "---\nname: \"demo-skill\"\ndescription: \"How to run the demo procedure.\"\n"
                "maturity: stable\n---\n"
                + RAILS_BLOCK,
            )
            repo_root_tmp = tmp
            _write(
                repo_root_tmp / "tests" / "golden" / "open" / "demo-case" / "case.yaml",
                "id: demo-case\ncommand: /demo-command\nstatus: expected_pass\ntags: []\n",
            )
            _write(
                repo_root_tmp / "tests" / "functional" / "test_demo_evidence.py",
                "# maturity-evidence: instruction/demo-instruction\n"
                "# maturity-evidence: skill/demo-skill\n",
            )
            _write(
                repo_root_tmp / "docs" / "tasks" / "completed-tasks.md",
                "# Completed Tasks\n\n| ID | Title | Owner | Done on | Outcome / artifact |\n"
                "|---|---|---|---|---|\n"
                "| T900 | Demo shipped work | demo-agent | 2026-09-10 | `docs/artifacts/demo-artifact.md` |\n",
            )
            _write(repo_root_tmp / "docs" / "artifacts" / "demo-artifact.md", "# Demo Artifact\n")
            _write(
                repo_root_tmp / "docs" / "wiki" / "overview.md",
                "# Overview\n\n"
                "- demo-agent owns the full demo workflow end to end for this fixture.\n"
                "- demo-command runs the demo workflow end to end for this fixture repo.\n"
                "- demo-instruction governs demo routing rules used across this fixture repo.\n"
                "- demo-skill documents how the demo procedure runs across this fixture repo.\n",
            )

            mod = _load_module()
            ctx = mod.build_context(impl)
            components = [mod._build_component(e, ctx.source_root) for e in ctx.entries]
            results = {c.id: mod.check_component(c, ctx) for c in components}
            for ident, failures in results.items():
                self.assertEqual(failures, [], f"{ident} unexpectedly failed: {failures}")

    def test_deprecated_with_notice_passes_without_notice_fails(self):
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            impl = _scaffold(tmp)
            _write(
                impl / "knowledge" / "agents" / "good-bye.md",
                "---\nname: \"Good Bye\"\ndescription: \"A retired agent kept for testing.\"\n"
                "maturity: deprecated\n---\n\n"
                "## Deprecation Notice\n**Reason**: superseded by a newer agent.\n"
                "**Removal target**: v7.0.0\n",
            )
            _write(
                impl / "knowledge" / "agents" / "no-notice.md",
                "---\nname: \"No Notice\"\ndescription: \"A retired agent missing its notice.\"\n"
                "maturity: deprecated\n---\n\nNothing here.\n",
            )
            mod = _load_module()
            ctx = mod.build_context(impl)
            components = {e["id"]: mod._build_component(e, ctx.source_root) for e in ctx.entries}
            self.assertEqual(mod.check_component(components["good-bye"], ctx), [])
            failures = mod.check_component(components["no-notice"], ctx)
            self.assertTrue(any("Deprecation Notice" in f for f in failures))


class TestCheckMaturityRealRepo(unittest.TestCase):
    def test_real_registry_runs_clean_at_experimental_baseline(self):
        proc = subprocess.run(
            ["python3", "implementation/scripts/check-maturity.py", "--root", "implementation"],
            cwd=repo_root(),
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("79 components checked, 0 failing", proc.stdout)
        self.assertIn("agent/experimental: 8 pass, 0 fail", proc.stdout)
        self.assertIn("agent/stable: 20 pass, 0 fail", proc.stdout)
        self.assertIn("command/experimental: 19 pass, 0 fail", proc.stdout)
        self.assertIn("instruction/experimental: 2 pass, 0 fail", proc.stdout)
        self.assertIn("instruction/stable: 4 pass, 0 fail", proc.stdout)
        self.assertIn("skill/experimental: 19 pass, 0 fail", proc.stdout)
        self.assertIn("skill/stable: 7 pass, 0 fail", proc.stdout)


if __name__ == "__main__":
    unittest.main()
