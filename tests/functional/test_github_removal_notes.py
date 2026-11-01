"""T685 (SEC-T676-13) -- the upgrade notes for the removed `github` MCP server carry two sentences.

A GitHub server that an adopter keeps under their own name has no generated denial on Opencode and Gemini CLI, so the
notes must tell them to use a fine-grained read-only token, and to revoke or unset GITHUB_PERSONAL_ACCESS_TOKEN once
they no longer use one. The same two sentences are carried in the T679 migration item (section 3a) so that the v9.0.0
release document gets them. Mutation proofs: the check is run on a text with a sentence removed or weakened.
"""
from __future__ import annotations

import unittest

from tests._helpers.repo import repo_root

ROOT = repo_root()
DOCS = ("implementation/PREREQUISITES.md", "docs/wiki/mcp-servers.md", "docs/tasks/task-T679.md")
SENTENCE_1 = ("A GitHub server that you keep under your own name is outside every generated denial on Opencode and Gemini CLI "
              "(those denials name the generated servers only), so give it a fine-grained, read-only token.")
SENTENCE_2 = "If you no longer use a GitHub server, revoke or unset `GITHUB_PERSONAL_ACCESS_TOKEN`."


def problems(text: str) -> list[str]:
    return [f"missing: {s[:50]}..." for s in (SENTENCE_1, SENTENCE_2) if s not in text]


class TestNotes(unittest.TestCase):
    def test_every_upgrade_note_carries_both_sentences(self):
        for rel in DOCS:
            with self.subTest(rel=rel):
                self.assertEqual(problems((ROOT / rel).read_text(encoding="utf-8")), [])

    def test_the_sentences_sit_next_to_the_github_removal_not_elsewhere(self):
        for rel in DOCS[:2]:
            text = (ROOT / rel).read_text(encoding="utf-8")
            at = text.index(SENTENCE_1)
            window = text[max(0, at - 700):at]
            self.assertIn("github-mine", window, rel)  # right after the "copy your entry under your own name" advice

    def test_the_notes_still_say_what_the_update_does(self):
        text = (ROOT / "docs/wiki/mcp-servers.md").read_text(encoding="utf-8")
        self.assertIn("`install.sh --update` removes only the generator-owned name `github`", text)

    def test_mutation_a_removed_or_weakened_sentence_is_detected(self):
        text = (ROOT / DOCS[0]).read_text(encoding="utf-8")
        self.assertTrue(problems(text.replace(SENTENCE_1, "")))
        self.assertTrue(problems(text.replace(SENTENCE_2, "")))
        self.assertTrue(problems(text.replace("fine-grained, read-only token", "token")))
        self.assertTrue(problems(text.replace("revoke or unset", "keep")))


if __name__ == "__main__":
    unittest.main()
