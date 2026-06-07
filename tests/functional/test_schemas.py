"""Validate that every agent / skill / command / instruction frontmatter
matches its JSON schema under implementation/knowledge/schemas/."""
from __future__ import annotations

import json
import unittest

import jsonschema

from tests._helpers.frontmatter import parse_file
from tests._helpers.repo import (
    knowledge_root,
    list_agents,
    list_commands,
    list_instructions,
    list_skills,
)


def _load_schema(name: str) -> dict:
    return json.loads((knowledge_root() / "schemas" / f"{name}.schema.json").read_text())


# Instructions don't ship with a strict schema; we enforce a minimal contract.
INSTRUCTION_REQUIRED = {"description"}
INSTRUCTION_ALLOWED = {"description", "applyTo"}


class TestSchemaCompliance(unittest.TestCase):
    def test_at_least_one_of_each_kind(self):
        self.assertGreater(len(list_agents()), 0, "no agents found")
        self.assertGreater(len(list_skills()), 0, "no skills found")
        self.assertGreater(len(list_commands()), 0, "no commands found")
        self.assertGreater(len(list_instructions()), 0, "no instructions found")

    def test_agent_frontmatter(self):
        schema = _load_schema("agent")
        for path in list_agents():
            with self.subTest(agent=path.name):
                fm, _ = parse_file(path)
                jsonschema.validate(fm, schema)
                self.assertEqual(
                    fm.get("name", "").strip().lower().replace(" ", "-"),
                    path.stem.lower(),
                    msg=f"{path.name}: frontmatter `name` should match filename slug",
                )

    def test_skill_frontmatter(self):
        schema = _load_schema("skill")
        for path in list_skills():
            with self.subTest(skill=path.parent.name):
                fm, _ = parse_file(path)
                jsonschema.validate(fm, schema)
                self.assertEqual(
                    fm["name"], path.parent.name,
                    msg=f"{path}: frontmatter `name` must equal directory name",
                )

    def test_command_frontmatter(self):
        schema = _load_schema("command")
        for path in list_commands():
            with self.subTest(command=path.name):
                fm, _ = parse_file(path)
                jsonschema.validate(fm, schema)

    def test_instruction_frontmatter(self):
        for path in list_instructions():
            with self.subTest(instruction=path.name):
                fm, _ = parse_file(path)
                missing = INSTRUCTION_REQUIRED - set(fm)
                self.assertFalse(missing, f"{path.name}: missing required keys {missing}")
                extra = set(fm) - INSTRUCTION_ALLOWED
                self.assertFalse(extra, f"{path.name}: unexpected keys {extra}")

    def test_descriptions_are_meaningful(self):
        """Descriptions must be at least 10 chars (per schema) and not just placeholder text."""
        forbidden = {"todo", "tbd", "fixme", "lorem ipsum", "..."}
        for kind, paths in (
            ("agent", list_agents()),
            ("skill", list_skills()),
            ("command", list_commands()),
            ("instruction", list_instructions()),
        ):
            for path in paths:
                with self.subTest(kind=kind, file=path.name):
                    fm, _ = parse_file(path)
                    desc = (fm.get("description") or "").strip().lower()
                    self.assertGreaterEqual(len(desc), 10, f"{path}: description too short")
                    for bad in forbidden:
                        self.assertNotIn(
                            bad, desc,
                            msg=f"{path}: placeholder text '{bad}' in description",
                        )


if __name__ == "__main__":
    unittest.main()
