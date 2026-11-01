"""T685 -- the example images in the knowledge templates are supported ones.

The devops-engineer agent and the ci-cd-pipeline skill show `image:` and `FROM` lines that adopters copy. They showed
node:20-alpine and alpine:3.19, both end of life. The end-of-life rules are the ones of the repository's own pipeline
(tests/functional/test_ci_hash_pins.py, eol_image_problems); a template example needs no digest, so that finding is
dropped. Mutation proofs run the check on the old examples.
"""
from __future__ import annotations

import re
import unittest

from tests._helpers.repo import repo_root
from tests.functional.test_ci_hash_pins import eol_image_problems

KNOWLEDGE = repo_root() / "implementation" / "knowledge"
FILES = ("agents/devops-engineer.md", "skills/ci-cd-pipeline/SKILL.md")


def image_references(text: str) -> list[str]:
    return re.findall(r"^\s*image:\s*(\S+)", text, re.M) + re.findall(r"^FROM\s+(\S+)", text, re.M)


def template_problems(text: str) -> list[str]:
    refs = image_references(text)
    found = eol_image_problems("\n".join(f"image: {r}" for r in refs))
    return [p for p in found if "no digest" not in p]


class TestKnowledgeTemplateImages(unittest.TestCase):
    def test_no_knowledge_file_shows_an_end_of_life_image(self):
        for path in sorted(KNOWLEDGE.rglob("*.md")):
            with self.subTest(path=str(path.relative_to(KNOWLEDGE))):
                self.assertEqual(template_problems(path.read_text(encoding="utf-8")), [])

    def test_the_two_templates_show_the_supported_lines(self):
        agent = (KNOWLEDGE / FILES[0]).read_text(encoding="utf-8")
        skill = (KNOWLEDGE / FILES[1]).read_text(encoding="utf-8")
        node = [r for r in image_references(agent) if r.startswith("node:")]
        self.assertEqual(node, ["node:24-alpine"] * 3)  # the CI default and the two Dockerfile stages
        self.assertEqual(image_references(skill), ["alpine:3.24"])
        for text in (agent, skill):
            for old in ("node:20", "alpine:3.19"):
                self.assertNotIn(old, text)

    def test_mutation_the_old_examples_are_detected(self):
        agent = (KNOWLEDGE / FILES[0]).read_text(encoding="utf-8")
        skill = (KNOWLEDGE / FILES[1]).read_text(encoding="utf-8")
        self.assertTrue(any("Node 20" in p for p in template_problems(agent.replace("node:24-alpine", "node:20-alpine"))))
        self.assertTrue(any("Alpine 3.19" in p for p in template_problems(skill.replace("alpine:3.24", "alpine:3.19"))))
        self.assertTrue(any("Node 23" in p for p in template_problems(agent.replace("node:24-alpine", "node:23-alpine"))))
        self.assertTrue(any("Python 3.9" in p for p in template_problems("FROM python:3.9-alpine AS x\n")))

    def test_the_digest_finding_is_not_a_template_problem(self):
        self.assertEqual(template_problems("image: node:24-alpine\nFROM python:3.12-alpine AS x\n"), [])


if __name__ == "__main__":
    unittest.main()
