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
            _write_passing_components(tmp, impl)

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


def _write_passing_components(tmp: Path, impl: Path) -> None:
    """Populate the scaffold with one `stable` component per category that
    satisfies every criterion, so a test can vary exactly one thing (for the
    ledger tests below: the task ledger) and attribute any resulting failure
    to that variation alone.
    """
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


def _write_ledger(tmp: Path, rows: str) -> None:
    """Replace the scaffold's empty active-tasks.md with the given table rows."""
    _write(
        tmp / "docs" / "tasks" / "active-tasks.md",
        "# Active Tasks\n\n"
        "| ID | Title | Owner | Status | Priority | Depends on | Last update |\n"
        "|---|---|---|---|---|---|---|\n" + rows,
    )


# A brief that *references* components the way the repo's own conventions force
# it to: the mandated agent-worktree branch name spells out an agent id between
# slashes, and instructions are cited by filename. Neither `/` nor `.` is a word
# character, so the pre-T516 free-text scan read both as accusations.
CITING_BRIEF = """# T901 — Decide something that cites its inputs

**Status:** pending
**Owner:** Demo Agent
**Priority:** P1
**Depends on:** —
**Affects:** {affects}

## Working agreement

Branch from `develop` in a worktree named `agent/demo-agent/T901`, per the Git Workflow rules.

## Inputs

- `.claude/rules/demo-instruction.md` — the routing rules this decision must respect.
- `/demo-command`'s declared contract.
- `.claude/skills/demo-skill/SKILL.md` — the procedure to follow.
"""


class TestLedgerDefectDeclaredField(unittest.TestCase):
    """Section 3.5's ledger half reads a declared `**Affects:**` field (T516)."""

    def _fixture(self, tmp: Path, rows: str, briefs: dict) -> Path:
        impl = _scaffold(tmp)
        _write_passing_components(tmp, impl)
        _write_ledger(tmp, rows)
        for task_id, text in briefs.items():
            _write(tmp / "docs" / "tasks" / f"task-{task_id}.md", text)
        return impl

    def _results(self, impl: Path) -> dict:
        mod = _load_module()
        ctx = mod.build_context(impl)
        components = [mod._build_component(e, ctx.source_root) for e in ctx.entries]
        return {c.id: mod.check_component(c, ctx) for c in components}

    def test_citing_a_branch_name_or_instruction_filename_does_not_demote(self):
        """Regression, task-T516 section 2: an open P1 brief that spells out its
        own mandated branch name and cites an instruction by filename must not
        block the components it merely names. Fails against the pre-T516
        free-text scan, which flagged demo-agent, demo-instruction, demo-command
        and demo-skill on this exact fixture.
        """
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            impl = self._fixture(
                tmp,
                "| T901 | Decide something that cites its inputs | demo-agent | pending | P1 | — | 2026-09-24 |\n",
                {"T901": CITING_BRIEF.format(affects="—")},
            )
            for ident, failures in self._results(impl).items():
                self.assertEqual(failures, [], f"{ident} blocked by a mere citation: {failures}")

    def test_title_mentioning_a_component_does_not_demote(self):
        """The ledger `Title` scan is dropped (task-T516 section 5.3): a title is
        one table cell with no room to rephrase, and it can no longer add a hit
        the brief did not declare. Fails against the pre-T516 Title scan.
        """
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            impl = self._fixture(
                tmp,
                "| T901 | Write docs for demo-agent and demo-skill | demo-agent | pending | P1 | — | 2026-09-24 |\n",
                {"T901": CITING_BRIEF.format(affects="—")},
            )
            for ident, failures in self._results(impl).items():
                self.assertEqual(failures, [], f"{ident} blocked by a ledger title: {failures}")

    def test_declared_component_is_still_blocked(self):
        """A genuine indictment must still block -- and only what is declared."""
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            impl = self._fixture(
                tmp,
                "| T901 | Decide something that cites its inputs | demo-agent | pending | P1 | — | 2026-09-24 |\n",
                {"T901": CITING_BRIEF.format(affects="agent/demo-agent, instruction/demo-instruction")},
            )
            results = self._results(impl)
            for ident in ("demo-agent", "demo-instruction"):
                joined = "\n".join(results[ident])
                self.assertIn("T901", joined, f"{ident} should be blocked by its declaration")
                self.assertIn("`**Affects:**`", joined)
            self.assertEqual(results["demo-skill"], [], "an undeclared component must not be blocked")
            self.assertEqual(results["demo-command"], [], "an undeclared component must not be blocked")

    def test_missing_field_on_p1_brief_fails_loudly(self):
        """The one hard constraint (task-T516 section 5.1/5.2): a P0/P1 brief with
        no declaration must abort the run naming the brief, never pass quietly.
        """
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            brief = CITING_BRIEF.format(affects="—").replace("**Affects:** —\n", "")
            impl = self._fixture(
                tmp,
                "| T901 | Decide something that cites its inputs | demo-agent | pending | P1 | — | 2026-09-24 |\n",
                {"T901": brief},
            )
            mod = _load_module()
            with self.assertRaises(mod.LedgerDeclarationError) as caught:
                mod.build_context(impl)
            message = str(caught.exception)
            self.assertIn("task-T901.md", message)
            self.assertIn("mandatory", message)

    def test_missing_field_makes_the_cli_exit_non_zero_with_no_report(self):
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            brief = CITING_BRIEF.format(affects="—").replace("**Affects:** —\n", "")
            impl = self._fixture(
                tmp,
                "| T901 | Decide something that cites its inputs | demo-agent | pending | P1 | — | 2026-09-24 |\n",
                {"T901": brief},
            )
            script = repo_root() / "implementation" / "scripts" / "check-maturity.py"
            proc = subprocess.run(
                ["python3", str(script), "--root", str(impl)],
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc.returncode, 2, proc.stdout + proc.stderr)
            self.assertIn("task-T901.md", proc.stderr)
            self.assertNotIn("components checked", proc.stdout)

    def test_p2_brief_need_not_declare_and_never_blocks(self):
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            brief = CITING_BRIEF.format(affects="—").replace("**Affects:** —\n", "")
            brief = brief.replace("**Priority:** P1", "**Priority:** P2")
            impl = self._fixture(
                tmp,
                "| T901 | Decide something that cites its inputs | demo-agent | pending | P2 | — | 2026-09-24 |\n",
                {"T901": brief},
            )
            for ident, failures in self._results(impl).items():
                self.assertEqual(failures, [], f"{ident} blocked by a P2 row: {failures}")

    def test_unknown_component_id_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            impl = self._fixture(
                tmp,
                "| T901 | Decide something that cites its inputs | demo-agent | pending | P1 | — | 2026-09-24 |\n",
                {"T901": CITING_BRIEF.format(affects="agent/demo-agnet")},
            )
            mod = _load_module()
            with self.assertRaises(mod.LedgerDeclarationError) as caught:
                mod.build_context(impl)
            self.assertIn("names no existing component", str(caught.exception))

    def test_malformed_entry_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            impl = self._fixture(
                tmp,
                "| T901 | Decide something that cites its inputs | demo-agent | pending | P1 | — | 2026-09-24 |\n",
                {"T901": CITING_BRIEF.format(affects="demo-agent")},
            )
            mod = _load_module()
            with self.assertRaises(mod.LedgerDeclarationError) as caught:
                mod.build_context(impl)
            self.assertIn("malformed entry", str(caught.exception))


class TestAffectsParsing(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()
        cls.known = {"agent/demo-agent", "command/demo-command", "skill/demo-skill"}

    def test_em_dash_means_no_component_affected(self):
        self.assertEqual(self.mod._parse_affects("—", self.known), (set(), []))

    def test_plain_hyphen_is_also_accepted_as_none(self):
        self.assertEqual(self.mod._parse_affects("-", self.known), (set(), []))

    def test_multiple_entries_parse(self):
        declared, errors = self.mod._parse_affects(
            "agent/demo-agent, `command/demo-command`", self.known
        )
        self.assertEqual(errors, [])
        self.assertEqual(declared, {"agent/demo-agent", "command/demo-command"})

    def test_empty_value_is_an_error(self):
        _, errors = self.mod._parse_affects("", self.known)
        self.assertTrue(errors)

    def test_dash_cannot_be_combined_with_entries(self):
        _, errors = self.mod._parse_affects("—, agent/demo-agent", self.known)
        self.assertTrue(any("cannot be combined" in e for e in errors))

    def test_unknown_category_is_rejected(self):
        _, errors = self.mod._parse_affects("widget/demo-agent", self.known)
        self.assertTrue(any("malformed entry" in e for e in errors))

    def test_mentions_helper_is_unchanged(self):
        """`_mentions()` must keep matching ids inside paths -- criterion (d)'s
        `_referenced_in_agents_or_commands()` depends on exactly that. T516
        fixed the caller, not the shared helper.
        """
        self.assertTrue(self.mod._mentions("branch agent/demo-agent/T901", "demo-agent"))
        self.assertTrue(self.mod._mentions("see `.claude/rules/git-workflow.md`", "git-workflow"))
        self.assertFalse(self.mod._mentions("see demo-agentic things", "demo-agent"))


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
        self.assertIn("agent/experimental: 2 pass, 0 fail", proc.stdout)
        self.assertIn("agent/stable: 26 pass, 0 fail", proc.stdout)
        self.assertIn("command/experimental: 18 pass, 0 fail", proc.stdout)
        self.assertIn("command/stable: 1 pass, 0 fail", proc.stdout)
        self.assertIn("instruction/experimental: 2 pass, 0 fail", proc.stdout)
        self.assertIn("instruction/stable: 4 pass, 0 fail", proc.stdout)
        self.assertIn("skill/experimental: 19 pass, 0 fail", proc.stdout)
        self.assertIn("skill/stable: 7 pass, 0 fail", proc.stdout)


if __name__ == "__main__":
    unittest.main()
