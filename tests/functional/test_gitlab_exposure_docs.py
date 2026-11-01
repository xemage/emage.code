"""T683 -- anchored documentation assertions for the Developer-level exposure sentence and the Reporter profile.

Based on docs/artifacts/gitlab-per-role-token-design-v1.md (section 8 and the work item),
docs/artifacts/security-review-t674-doc-corrections-v1.md and the user's decision of 2026-10-22 on T681
("A: status quo + exposure sentence (Recommended)" and "Yes, document it (Recommended)").

T674 wrote, in implementation/PREREQUISITES.md, section "### GitLab token":

- the Developer-level exposure bullet and the per-role bullet in the rules of "#### Scope and role";
- the section "#### Reporter profile";

and, in docs/wiki/mcp-servers.md, the bullet "One token, and a Developer-level one ..." with the pointer to the
Reporter profile. This file pins each of them to the section that holds it (no whole-file regex), derives the
three roles that hold `create_merge_request` from the agent sources instead of hard-coding them, and proves with
in-memory mutations that deleting a sentence, a label or a section, or moving a sentence into another section,
makes the corresponding check fail.

The pins of tests/functional/test_gitlab_token_handling.py (the one `| Use |` table, the posture table, ...) and the
three GitLab-grants paragraphs (tests/functional/test_mcp_grant_pins.py) are not repeated here.

Static inspection only; no network, no token. Nothing here says the documented chain was run: the documents label
it unverified, and these tests pin the label.
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

from tests._helpers.frontmatter import parse_file
from tests._helpers.repo import implementation_root, knowledge_root, repo_root

REPO = repo_root()
PREREQUISITES = implementation_root() / "PREREQUISITES.md"
WIKI = REPO / "docs" / "wiki" / "mcp-servers.md"
AGENTS_DIR = knowledge_root() / "agents"

MR_TOOL = "mcp__gitlab__create_merge_request"

TOKEN_HEADING = "### GitLab token"
RULES_HEADING = "#### Scope and role"
REPORTER_HEADING = "#### Reporter profile"
TOKEN_TYPE_HEADING = "#### Token type"
WIKI_TOKEN_HEADING = "## GitLab token"

EXPOSURE_LEAD = "- **A Developer-level `api` token is more than a merge-request token (SEC-T665-07).**"
PER_ROLE_LEAD = "- **The token is not per role, and a token per role is not offered.**"
CEILING_LEAD = "- **The role sets the ceiling, not the scope.**"
WIKI_LEAD = "- **One token, and a Developer-level one if you use the merge-request roles.**"
REPORTER_LEADS = {
    "what": "- **What it is.**",
    "stops": "- **What stops working.**",
    "keeps": "- **What keeps working.**",
    "ceiling": "- **What the role ceiling gives you.**",
    "readonly": "- **It is not a read-only token.**",
    "unchanged": "- **What it does not change.**",
}


# ------------------------------------------------------------------------------------------ helpers ----

def _section(text: str, heading: str) -> str:
    """The text of `heading` up to the next heading of the same or a higher level ('' if it is absent)."""
    level = len(heading) - len(heading.lstrip("#"))
    match = re.search(rf"^{re.escape(heading)}\s*$", text, re.M)
    if not match:
        return ""
    rest = text[match.end():]
    end = re.search(rf"^#{{1,{level}}} ", rest, re.M)
    return rest[: end.start()] if end else rest


def _line(section: str, lead: str) -> str:
    """The one line of `section` that starts with `lead` ('' if it is absent)."""
    for line in section.splitlines():
        if line.startswith(lead):
            return line
    return ""


def _without_section(text: str, heading: str) -> str:
    """`text` with `heading` and its body removed (in-memory mutation helper)."""
    match = re.search(rf"^{re.escape(heading)}\s*$", text, re.M)
    assert match, heading
    rest = text[match.end():]
    level = len(heading) - len(heading.lstrip("#"))
    end = re.search(rf"^#{{1,{level}}} ", rest, re.M)
    return text[: match.start()] + (rest[end.start():] if end else "")


def _holders(agents_dir: Path = AGENTS_DIR) -> list[str]:
    """The agents whose source tool list holds `create_merge_request` (derived, never hard-coded)."""
    out = []
    for path in sorted(agents_dir.glob("*.md")):
        if MR_TOOL in (parse_file(path)[0].get("tools") or []):
            out.append(path.stem)
    return out


def _named_holders(text: str) -> list[list[str]]:
    """Each list of backticked names in front of 'hold `create_merge_request`' (e.g. 'A, B and C hold ...')."""
    found = []
    for match in re.finditer(r"((?:`[a-z][a-z-]*`(?:, | and )?)+) hold `create_merge_request`", text):
        found.append(sorted(re.findall(r"`([a-z][a-z-]*)`", match.group(1))))
    return found


def _slug(heading: str) -> str:
    """GitLab's anchor for a heading: lower case, spaces to hyphens, punctuation dropped."""
    text = heading.lstrip("#").strip().lower()
    return re.sub(r"\s", "-", re.sub(r"[^\w\s-]", "", text))


def _need(findings: list[str], label: str, ok: bool) -> None:
    if not ok:
        findings.append(label)


def _all(text: str, label: str, findings: list[str], *patterns: str) -> None:
    for pattern in patterns:
        _need(findings, f"{label}: {pattern}", re.search(pattern, text) is not None)


# --------------------------------------------------------------------------------- finding functions ----

def exposure_findings(prereq: str) -> list[str]:
    """The Developer-level exposure bullet, anchored to the rules of 'Scope and role'."""
    token = _section(prereq, TOKEN_HEADING)
    rules = _section(token, RULES_HEADING)
    found: list[str] = []
    bullet = _line(rules, EXPOSURE_LEAD)
    _need(found, "exposure: bullet missing from 'Scope and role'", bool(bullet))
    _need(found, "exposure: bullet appears more than once in 'Scope and role'", rules.count(EXPOSURE_LEAD) <= 1)
    # one place only: no other section of the document carries the sentence
    elsewhere = prereq.count("A Developer-level `api` token is more than a merge-request token")
    _need(found, "exposure: sentence appears outside 'Scope and role' or more than once", elsewhere == 1)
    if not bullet:
        return found
    _all(bullet, "exposure", found,
         r"can push commits to branches that are not protected",
         r"create tags that no protected-tag rule covers",
         r"start pipelines on those branches",
         r"runs that branch's `\.gitlab-ci\.yml` on your runners",
         r"every unprotected CI/CD variable",
         r"Branch protection on `main` and `develop` does not stop this",
         r"your GitLab configuration, outside the harness",
         # the protected-branch question carries its own label
         r"push or merge to protected branches depends on[^.\n]{0,120}\(unverified\)",
         # the chain as a whole carries the bold label
         r"the chain as a whole was not run \*\*\(unverified\)\*\*")
    return found


def per_role_findings(prereq: str, holders: list[str]) -> list[str]:
    """The per-role bullet and the role-ceiling bullet (which names the holders), in 'Scope and role'."""
    rules = _section(_section(prereq, TOKEN_HEADING), RULES_HEADING)
    found: list[str] = []
    bullet = _line(rules, PER_ROLE_LEAD)
    _need(found, "per-role: bullet missing from 'Scope and role'", bool(bullet))
    if bullet:
        _all(bullet, "per-role", found,
             r"There is one `gitlab` entry",
             r"every agent with `execute` runs as you and can read it",
             r"on 2026-10-22 \(\"A: status quo \+ exposure sentence \(Recommended\)\"",
             r"two server entries, no MCP merge-request creation and per-role tokens were not chosen",
             r"For a lower-privilege token, see \"Reporter profile\"")
        _need(found, "per-role: bullet must say a token per role is NOT offered", "a token per role is not offered" in bullet)
    ceiling = _line(rules, CEILING_LEAD)
    _need(found, "ceiling: bullet missing from 'Scope and role'", bool(ceiling))
    if ceiling:
        named = _named_holders(ceiling)
        _need(found, "ceiling: names of the create_merge_request holders differ from the agent sources",
              named == [sorted(holders)])
        _all(ceiling, "ceiling", found, r"hold `create_merge_request`, which needs \*\*Developer\*\*")
    return found


def reporter_findings(prereq: str, holders: list[str]) -> list[str]:
    """The Reporter profile section: present once, inside the GitLab token section, with its six statements."""
    found: list[str] = []
    _need(found, "reporter: heading must appear exactly once in the document",
          len(re.findall(rf"^{re.escape(REPORTER_HEADING)}\s*$", prereq, re.M)) == 1)
    token = _section(prereq, TOKEN_HEADING)
    section = _section(token, REPORTER_HEADING)
    _need(found, "reporter: section missing from the 'GitLab token' section", bool(section.strip()))
    if not section.strip():
        return found
    lines = {key: _line(section, lead) for key, lead in REPORTER_LEADS.items()}
    for key, line in lines.items():
        _need(found, f"reporter: bullet '{key}' missing", bool(line))
    # what it is: per project, the bound
    _all(lines["what"], "reporter/what", found,
         r"Planner or Reporter",
         r"The role holds per project",
         r"project or group access token",
         r"dedicated user")
    # what stops working: the derived holders, the refusal, the label, the hand-over
    stops = lines["stops"]
    _need(found, "reporter/stops: the roles named differ from the agent sources", _named_holders(stops) == [sorted(holders)])
    _all(stops, "reporter/stops", found,
         r"the one tool that needs Developer",
         r"Planner or Reporter token a `create_merge_request` call fails with an authorization error from GitLab",
         r"\*\*\(unverified: [^)]*not run[^)]*\)\*\*",
         r"hand the merge request to the top-level session")
    # what the role ceiling gives you: the cells that stay unverified
    _all(lines["ceiling"], "reporter/ceiling", found,
         r"the merge row, the label and milestone rows and the release row of the table are marked so",
         r"whether a Planner or Reporter token can create a branch is not established here \*\*\(unverified\)\*\*",
         r"The chain as a whole was not run")
    # not read-only
    _all(lines["readonly"], "reporter/readonly", found,
         r"still reads the whole project",
         r"Only the role limits it, not the scope")
    # the residual stays
    _all(lines["unchanged"], "reporter/unchanged", found,
         r"Every agent with `execute` can still read the token",
         r"SEC-T660-01 residual stays: mitigated, not closed")
    # the decision is recorded next to the profile
    _all(section, "reporter/decision", found,
         r"2026-10-22",
         r"\"A: status quo \+ exposure sentence \(Recommended\)\"",
         r"\"Yes, document it \(Recommended\)\"")
    return found


def table_label_findings(prereq: str) -> list[str]:
    """The merge, label/milestone and release cells of the table stay marked unverified."""
    rules = _section(_section(prereq, TOKEN_HEADING), RULES_HEADING)
    found: list[str] = []
    for prefix in ("| Update an issue; create or edit labels and milestones", "| Merge a merge request", "| Create a release"):
        row = _line(rules, prefix)
        _need(found, f"table: row '{prefix}' missing", bool(row))
        _need(found, f"table: row '{prefix}' is not marked unverified", "unverified" in row)
    return found


def wiki_findings(wiki: str, prereq: str, holders: list[str]) -> list[str]:
    """The wiki bullet in the 'In short' list of the GitLab token section, with the pointer to the profile."""
    found: list[str] = []
    section = _section(wiki, WIKI_TOKEN_HEADING)
    bullet = _line(section, WIKI_LEAD)
    _need(found, "wiki: bullet missing from the 'GitLab token' section", bool(bullet))
    _need(found, "wiki: bullet appears outside the 'GitLab token' section", wiki.count(WIKI_LEAD) == 1)
    if not bullet:
        return found
    _need(found, "wiki: the roles named differ from the agent sources", _named_holders(bullet) == [sorted(holders)])
    _all(bullet, "wiki", found,
         r"which needs Developer",
         r"can push to unprotected branches, create tags and start pipelines that run code on your runners",
         r"a token per role is not offered \(decision of 2026-10-22\)",
         r"\*\*Reporter profile\*\*",
         r"`create_merge_request` is expected to fail with an authorization error; unverified, not run",
         r"that token is not read-only",
         r"the role holds per project",
         # the pointer: a link whose target is the PREREQUISITES anchor of the section
         r"\]\([^)\s]*implementation/PREREQUISITES\.md#reporter-profile\)")
    _need(found, "wiki: the pointer's anchor does not match the heading of PREREQUISITES.md",
          _slug(REPORTER_HEADING) == "reporter-profile" and bool(_section(prereq, REPORTER_HEADING)))
    return found


# ------------------------------------------------------------------------------------------ tests ----

class _DocTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.prereq = PREREQUISITES.read_text(encoding="utf-8")
        cls.wiki = WIKI.read_text(encoding="utf-8")
        cls.holders = _holders()

    def replaced(self, text: str, old: str, new: str = "") -> str:
        """In-memory mutation; fails the test if the mutation did not apply (a no-op would prove nothing)."""
        self.assertIn(old, text, f"mutation target not found: {old[:60]!r}")
        mutated = text.replace(old, new, 1)
        self.assertNotEqual(mutated, text)
        return mutated

    def assertFinds(self, findings: list[str], needle: str):
        self.assertTrue(any(needle in f for f in findings), f"no finding contains {needle!r}: {findings}")


class DerivedHoldersTests(_DocTest):
    def test_the_three_holders_come_from_the_agent_sources(self):
        self.assertEqual(len(self.holders), 3, self.holders)
        for slug in self.holders:
            self.assertTrue((AGENTS_DIR / f"{slug}.md").is_file())

    def test_the_helper_reads_each_named_list_and_rejects_a_changed_one(self):
        self.assertEqual(_named_holders("`b`, `a` and `c` hold `create_merge_request`, x"), [["a", "b", "c"]])
        self.assertEqual(_named_holders("nothing here"), [])


class ExposureSentenceTests(_DocTest):
    def test_the_exposure_sentence_is_in_the_scope_and_role_rules_and_complete(self):
        self.assertEqual(exposure_findings(self.prereq), [])

    def test_the_sentence_is_a_bullet_of_the_rules_not_of_the_table_or_another_section(self):
        token = _section(self.prereq, TOKEN_HEADING)
        rules = _section(token, RULES_HEADING)
        self.assertEqual(rules.count(EXPOSURE_LEAD), 1)
        rules_start = token.index(rules)
        self.assertLess(token.index("| Use "), rules_start + len(rules))
        for other in (REPORTER_HEADING, TOKEN_TYPE_HEADING, "#### What this does not protect"):
            self.assertNotIn("more than a merge-request token", _section(token, other), other)
        self.assertNotIn("more than a merge-request token", self.wiki)

    def test_deleting_the_sentence_fails_the_anchor(self):
        mutated = self.replaced(self.prereq, _line(self.prereq, EXPOSURE_LEAD) + "\n")
        self.assertFinds(exposure_findings(mutated), "bullet missing")

    def test_moving_the_sentence_to_another_section_fails_the_anchor(self):
        bullet = _line(self.prereq, EXPOSURE_LEAD)
        removed = self.replaced(self.prereq, bullet + "\n")
        for target in (TOKEN_TYPE_HEADING, REPORTER_HEADING, "#### Per-client posture"):
            with self.subTest(target=target):
                moved = self.replaced(removed, target + "\n", f"{target}\n\n{bullet}\n")
                self.assertTrue(exposure_findings(moved))
                self.assertFinds(exposure_findings(moved), "bullet missing from 'Scope and role'")

    def test_duplicating_the_sentence_is_noticed(self):
        bullet = _line(self.prereq, EXPOSURE_LEAD)
        doubled = self.replaced(self.prereq, bullet + "\n", bullet + "\n" + bullet + "\n")
        self.assertTrue(exposure_findings(doubled))

    def test_deleting_each_claim_fails_its_assertion(self):
        bullet = _line(self.prereq, EXPOSURE_LEAD)
        claims = {
            "push to unprotected branches": "It can push commits to branches that are not protected, ",
            "tags": "create tags that no protected-tag rule covers, ",
            "pipelines": "and start pipelines on those branches. ",
            "runner code": "runs that branch's `.gitlab-ci.yml` on your runners, ",
            "unprotected variables": "with every unprotected CI/CD variable and the job token, ",
            "branch protection": "Branch protection on `main` and `develop` does not stop this: it protects those branches, not the runners. ",
            "outside the harness": "these are your GitLab configuration, outside the harness",
        }
        for name, sentence in claims.items():
            with self.subTest(claim=name):
                mutated = self.replaced(self.prereq, sentence)
                self.assertTrue(exposure_findings(mutated), name)

    def test_deleting_either_unverified_label_fails_its_assertion(self):
        protected = self.replaced(self.prereq, " (unverified). Limit it with protected variables", ". Limit it with protected variables")
        self.assertFinds(exposure_findings(protected), "protected branches depends on")
        chain = self.replaced(self.prereq, "the chain as a whole was not run **(unverified)**", "the chain as a whole was not run")
        self.assertFinds(exposure_findings(chain), "the chain as a whole was not run")

    def test_a_label_that_is_present_but_not_bold_fails_the_chain_assertion(self):
        mutated = self.replaced(self.prereq, "was not run **(unverified)**", "was not run (unverified)")
        self.assertFinds(exposure_findings(mutated), "the chain as a whole was not run")


class PerRoleBulletTests(_DocTest):
    def test_the_per_role_bullet_says_a_token_per_role_is_not_offered_and_records_the_decision(self):
        self.assertEqual(per_role_findings(self.prereq, self.holders), [])

    def test_deleting_the_bullet_or_the_decision_fails(self):
        self.assertFinds(per_role_findings(self.replaced(self.prereq, _line(self.prereq, PER_ROLE_LEAD) + "\n"), self.holders),
                         "per-role: bullet missing")
        decision = '("A: status quo + exposure sentence (Recommended)"; option A of the T681 design'
        mutated = self.replaced(self.prereq, decision, "(option A of the T681 design")
        self.assertFinds(per_role_findings(mutated, self.holders), "per-role")
        date = self.replaced(self.prereq, "The user decided on 2026-10-22 (", "The user decided on 2026-10-21 (")
        self.assertFinds(per_role_findings(date, self.holders), "per-role")

    def test_turning_the_refusal_into_an_offer_fails(self):
        mutated = self.replaced(self.prereq, "a token per role is not offered", "a token per role is offered")
        self.assertTrue(per_role_findings(mutated, self.holders))
        lead_only = self.replaced(self.prereq, "The token is not per role, and a token per role is not offered.**",
                                  "The token is not per role.**")
        self.assertTrue(per_role_findings(lead_only, self.holders))

    def test_the_shell_exposure_sentence_must_stay(self):
        mutated = self.replaced(self.prereq, "every agent with `execute` runs as you and can read it, whether or not it holds a GitLab tool",
                                "no agent can read it")
        self.assertFinds(per_role_findings(mutated, self.holders), "every agent with `execute`")

    def test_the_ceiling_bullet_names_the_holders_of_the_agent_sources(self):
        for slug in self.holders:
            with self.subTest(removed=slug):
                fewer = [h for h in self.holders if h != slug]
                self.assertFinds(per_role_findings(self.prereq, fewer), "differ from the agent sources")
        self.assertFinds(per_role_findings(self.prereq, self.holders + ["qa-engineer"]), "differ from the agent sources")

    def test_renaming_a_holder_in_the_ceiling_bullet_fails(self):
        mutated = self.replaced(self.prereq, "`orchestrator`, `poc-orchestrator` and `release-manager` hold `create_merge_request`, which needs **Developer**",
                                "`orchestrator` and `poc-orchestrator` hold `create_merge_request`, which needs **Developer**")
        self.assertFinds(per_role_findings(mutated, self.holders), "differ from the agent sources")


class ReporterProfileTests(_DocTest):
    def test_the_reporter_profile_is_present_once_and_complete(self):
        self.assertEqual(reporter_findings(self.prereq, self.holders), [])

    def test_the_profile_is_a_subsection_of_the_gitlab_token_section(self):
        token = _section(self.prereq, TOKEN_HEADING)
        self.assertIn(REPORTER_HEADING, token)
        self.assertEqual(self.prereq.count(REPORTER_HEADING + "\n"), 1)
        self.assertEqual(len(re.findall(r"^#+ .*Reporter profile", self.prereq, re.M)), 1)

    def test_deleting_the_section_fails(self):
        mutated = _without_section(self.prereq, REPORTER_HEADING)
        self.assertNotEqual(mutated, self.prereq)
        self.assertFinds(reporter_findings(mutated, self.holders), "heading must appear exactly once")
        self.assertFinds(reporter_findings(mutated, self.holders), "section missing")

    def test_a_second_copy_of_the_heading_fails(self):
        mutated = self.replaced(self.prereq, "#### Token type\n", "#### Reporter profile\n\ntext\n\n#### Token type\n")
        self.assertFinds(reporter_findings(mutated, self.holders), "exactly once")

    def test_renaming_the_heading_fails(self):
        mutated = self.replaced(self.prereq, REPORTER_HEADING + "\n", "#### Low-privilege profile\n")
        self.assertFinds(reporter_findings(mutated, self.holders), "exactly once")

    def test_deleting_each_bullet_fails_its_assertion(self):
        for key, lead in REPORTER_LEADS.items():
            with self.subTest(bullet=key):
                section = _section(_section(self.prereq, TOKEN_HEADING), REPORTER_HEADING)
                mutated = self.replaced(self.prereq, _line(section, lead) + "\n")
                self.assertFinds(reporter_findings(mutated, self.holders), f"bullet '{key}' missing")

    def test_the_three_roles_are_derived_from_the_sources_and_a_change_is_noticed(self):
        self.assertEqual(len(self.holders), 3)
        for slug in self.holders:
            with self.subTest(removed=slug):
                self.assertFinds(reporter_findings(self.prereq, [h for h in self.holders if h != slug]), "differ from the agent sources")
        self.assertFinds(reporter_findings(self.prereq, self.holders + ["scrum-master"]), "differ from the agent sources")

    def test_dropping_a_role_from_the_stops_working_bullet_fails(self):
        mutated = self.replaced(self.prereq, "`orchestrator`, `poc-orchestrator` and `release-manager` hold `create_merge_request`, the one tool",
                                "`orchestrator` and `poc-orchestrator` hold `create_merge_request`, the one tool")
        self.assertFinds(reporter_findings(mutated, self.holders), "reporter/stops: the roles named")

    def test_deleting_each_statement_fails_its_assertion(self):
        cases = {
            "refusal": ("a `create_merge_request` call fails with an authorization error from GitLab", "reporter/stops"),
            "unverified-not-run label": ("**(unverified: documented reading of the permissions page, not run; the exact error is not recorded)**", "reporter/stops"),
            "hand-over": ("Those roles then hand the merge request to the top-level session", "reporter/stops"),
            "not read-only": ("still reads the whole project", "reporter/readonly"),
            "role not scope": ("Only the role limits it, not the scope.", "reporter/readonly"),
            "per project": ("The role holds per project", "reporter/what"),
            "project or group token": ("only a project or group access token, or a dedicated user whose only membership is the target project, bounds the reach to that role",
                                       "reporter/what"),
            "shell reads the token": ("Every agent with `execute` can still read the token", "reporter/unchanged"),
            "residual": ("the SEC-T660-01 residual stays: mitigated, not closed", "reporter/unchanged"),
            "unverified cells": ("the merge row, the label and milestone rows and the release row of the table are marked so", "reporter/ceiling"),
            "branch unverified": ("whether a Planner or Reporter token can create a branch is not established here **(unverified)**", "reporter/ceiling"),
            "chain not run": ("The chain as a whole was not run.", "reporter/ceiling"),
            "decision label": ('"Yes, document it (Recommended)"', "reporter/decision"),
        }
        for name, (sentence, prefix) in cases.items():
            with self.subTest(statement=name):
                section = _section(_section(self.prereq, TOKEN_HEADING), REPORTER_HEADING)
                self.assertIn(sentence, section, "the sentence must be inside the Reporter profile")
                mutated = self.replaced(self.prereq, sentence)
                self.assertFinds(reporter_findings(mutated, self.holders), prefix)

    def test_the_table_cells_stay_marked_unverified(self):
        self.assertEqual(table_label_findings(self.prereq), [])
        for prefix in ("| Update an issue; create or edit labels and milestones", "| Merge a merge request", "| Create a release"):
            with self.subTest(row=prefix):
                row = _line(self.prereq, prefix)
                mutated = self.replaced(self.prereq, row, row.replace("unverified", "confirmed"))
                self.assertTrue(table_label_findings(mutated))


class WikiPointerTests(_DocTest):
    def test_the_wiki_bullet_exists_and_points_at_the_reporter_profile(self):
        self.assertEqual(wiki_findings(self.wiki, self.prereq, self.holders), [])

    def test_the_bullet_is_in_the_in_short_list_of_the_gitlab_token_section(self):
        section = _section(self.wiki, WIKI_TOKEN_HEADING)
        self.assertIn("In short:", section)
        self.assertGreater(section.index(WIKI_LEAD), section.index("In short:"))
        self.assertEqual(self.wiki.count(WIKI_LEAD), 1)

    def test_the_wiki_still_has_no_scope_table(self):
        # kept with the pin of test_gitlab_token_handling: the table is in PREREQUISITES only
        self.assertEqual(len(re.findall(r"\|\s*Use\s*\|", self.wiki)), 0)

    def test_deleting_the_bullet_fails(self):
        mutated = self.replaced(self.wiki, _line(self.wiki, WIKI_LEAD) + "\n")
        self.assertFinds(wiki_findings(mutated, self.prereq, self.holders), "bullet missing")

    def test_moving_the_bullet_out_of_the_section_fails(self):
        bullet = _line(self.wiki, WIKI_LEAD)
        removed = self.replaced(self.wiki, bullet + "\n")
        moved = self.replaced(removed, "## Playwright server (`playwright`)\n", f"## Playwright server (`playwright`)\n\n{bullet}\n")
        self.assertFinds(wiki_findings(moved, self.prereq, self.holders), "bullet missing")

    def test_removing_the_pointer_or_breaking_its_anchor_fails(self):
        link = "implementation/PREREQUISITES.md#reporter-profile"
        self.assertIn(link, self.wiki)
        for new in ("implementation/PREREQUISITES.md", "implementation/PREREQUISITES.md#reporter-profil",
                    "implementation/PREREQUISITES.md#token-type"):
            with self.subTest(replacement=new):
                mutated = self.replaced(self.wiki, link, new)
                self.assertFinds(wiki_findings(mutated, self.prereq, self.holders), "wiki:")

    def test_a_pointer_to_a_section_that_no_longer_exists_fails(self):
        mutated = _without_section(self.prereq, REPORTER_HEADING)
        self.assertNotEqual(mutated, self.prereq)
        self.assertFinds(wiki_findings(self.wiki, mutated, self.holders), "anchor does not match")

    def test_deleting_each_statement_of_the_bullet_fails(self):
        cases = {
            "exposure": "can push to unprotected branches, create tags and start pipelines that run code on your runners",
            "per-role": "a token per role is not offered (decision of 2026-10-22)",
            "profile name": "the **Reporter profile**",
            "refusal": "`create_merge_request` is expected to fail with an authorization error; unverified, not run",
            "not read-only": "that token is not read-only",
            "per project": "the role holds per project",
        }
        for name, sentence in cases.items():
            with self.subTest(statement=name):
                mutated = self.replaced(self.wiki, sentence)
                self.assertTrue(wiki_findings(mutated, self.prereq, self.holders), name)

    def test_the_wiki_names_the_holders_of_the_agent_sources(self):
        self.assertFinds(wiki_findings(self.wiki, self.prereq, self.holders[:-1]), "differ from the agent sources")


if __name__ == "__main__":
    unittest.main()
