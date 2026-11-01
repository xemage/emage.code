"""T676 (SEC-T675-08 and SEC-T675-10 remainders) -- scripts/publish-release.py.

Pins that T675 left to a later task, each with a mutation proof (the guard is removed from a copy of the
source, the copy is loaded, and the matching condition must then FAIL):

  - a bare `?` or `#` in --api-v4-url is refused (urlsplit reports an empty query, so only the explicit text check
    catches it);
  - a redirect of ANY status the stdlib follows (301, 302, 303, 307, 308) is refused and the token is not re-sent;
  - a release document that is a symlink to a SIBLING file inside docs/releases is refused;
  - a commit subject loses C1 controls and invisible/bidirectional formatting characters (SEC-T675-10); Markdown
    characters are kept on purpose;
  - T685 (SEC-T676-12): U+034F and the Khmer inherent vowels U+17B4/U+17B5 are in the class too; emoji keep every code
    point (ZWJ and the variation selector are stripped, which is cosmetic); the NUL framing is asserted over several
    real commits, one with a lone CR and one with other line separators, as an exact list through the real run_git.
"""
from __future__ import annotations

import http.server
import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import types
import unittest
import urllib.request
from pathlib import Path
from unittest import mock

from tests._helpers.repo import repo_root

SCRIPT = repo_root() / "scripts" / "publish-release.py"


def load(source: str | None = None, name: str = "publish_release_t676") -> types.ModuleType:
    text = SCRIPT.read_text(encoding="utf-8") if source is None else source
    module = types.ModuleType(name)
    module.__file__ = str(SCRIPT)
    sys.modules[name] = module
    exec(compile(text, str(SCRIPT), "exec"), module.__dict__)  # noqa: S102 -- our own script / a mutation of it
    return module


def mutated(old: str, new: str) -> types.ModuleType:
    text = SCRIPT.read_text(encoding="utf-8")
    assert text.count(old) == 1, f"mutation anchor must occur exactly once: {old!r}"
    return load(text.replace(old, new), "publish_release_t676_mutant")


PR = load()


class TestBareQueryAndFragment(unittest.TestCase):
    BARE = ("https://gitlab.com/api/v4?", "https://gitlab.com/api/v4#", "https://gitlab.com/api/v4?#",
            "https://gitlab.com/api/v4#?")

    def test_a_bare_question_mark_or_hash_is_refused(self):
        for url in self.BARE:
            with self.subTest(url=url):
                self.assertIn("query or a fragment", PR._api_url_problem(url, "gitlab.com") or "")

    def test_the_clean_url_is_accepted(self):
        self.assertIsNone(PR._api_url_problem("https://gitlab.com/api/v4", "gitlab.com"))

    def test_mutation_dropping_the_text_check_is_detected(self):
        mutant = mutated('if parts.query or parts.fragment or "?" in api_v4_url or "#" in api_v4_url:',
                         "if parts.query or parts.fragment:")
        problems = {mutant._api_url_problem(u, "gitlab.com") for u in ("https://gitlab.com/api/v4?",
                                                                        "https://gitlab.com/api/v4#")}
        # urlsplit reports an empty query and fragment, so the path check fires instead of the query check
        for problem in problems:
            self.assertNotIn("query or a fragment", problem or "")


class _Handler(http.server.BaseHTTPRequestHandler):
    seen: list = []
    status = 302
    redirect_to: str | None = None

    def do_GET(self):  # noqa: N802
        type(self).seen.append(self.headers.get("PRIVATE-TOKEN"))
        if self.redirect_to:
            self.send_response(self.status)
            self.send_header("Location", self.redirect_to)
            self.end_headers()
        else:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"{}")

    def log_message(self, *args):
        pass


class TestEveryRedirectStatusIsRefused(unittest.TestCase):
    CODES = (301, 302, 303, 307, 308)

    def serve(self, handler):
        server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        return f"http://127.0.0.1:{server.server_address[1]}"

    def pair(self, code):
        target = type("Target", (_Handler,), {"seen": [], "redirect_to": None})
        origin = type("Origin", (_Handler,), {"seen": [], "status": code,
                                              "redirect_to": self.serve(target) + "/leak"})
        return target, origin, self.serve(origin)

    def test_no_redirect_status_is_followed_and_the_token_is_never_resent(self):
        for code in self.CODES:
            with self.subTest(code=code):
                target, origin, url = self.pair(code)
                with self.assertRaisesRegex(PR.ReleasePublishError, f"failed: {code}"):
                    PR.gitlab_request("GET", url + "/x", "tok-fake")
                self.assertEqual(origin.seen, ["tok-fake"])
                self.assertEqual(target.seen, [])

    def test_control_the_default_opener_follows_every_one_of_them(self):
        for code in self.CODES:
            with self.subTest(code=code):
                target, _origin, url = self.pair(code)
                with mock.patch.object(PR, "OPENER", urllib.request.build_opener()):
                    PR.gitlab_request("GET", url + "/x", "tok-fake")
                self.assertEqual(target.seen, ["tok-fake"], "the stdlib follows this status and re-sends the header")

    def test_mutation_following_redirects_is_detected(self):
        mutant = mutated("        return None  # the caller then sees the 3xx as an HTTPError",
                         "        return super().redirect_request(req, fp, code, msg, headers, newurl)")
        target, _origin, url = self.pair(307)
        mutant.gitlab_request("GET", url + "/x", "tok-fake")
        self.assertEqual(target.seen, ["tok-fake"])  # the mutant leaks the token to the redirect target


class TestSymlinkToASiblingDocument(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.releases = Path(self._tmp.name) / "docs" / "releases"
        self.releases.mkdir(parents=True)
        (self.releases / "v1.2.2.md").write_text("# Release v1.2.2\nolder body\n", encoding="utf-8")
        (self.releases / "v1.2.3.md").symlink_to("v1.2.2.md")  # a sibling INSIDE docs/releases

    def load_brief(self, module):
        with mock.patch.object(module, "ROOT", Path(self._tmp.name)):
            return module.load_release_brief("v1.2.3")

    def test_a_symlink_to_a_sibling_release_document_is_refused(self):
        with self.assertRaisesRegex(PR.ReleasePublishError, "regular file under docs/releases"):
            self.load_brief(PR)

    def test_mutation_allowing_symlinks_inside_the_directory_is_detected(self):
        mutant = mutated("releases_dir.is_symlink() or brief_path.is_symlink() or not",
                         "releases_dir.is_symlink() or not")
        self.assertIn("older body", self.load_brief(mutant))  # the mutant publishes the OTHER release's text


class TestSubjectSanitising(unittest.TestCase):
    ENV = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.invalid", "GIT_COMMITTER_NAME": "t",
           "GIT_COMMITTER_EMAIL": "t@example.invalid", "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull}

    def subjects(self, module, *log_subjects: str) -> list[str]:
        framed = "".join(subject + "\x00" for subject in log_subjects)  # what `git log --pretty=%s%x00` prints
        with mock.patch.object(module, "run_git", lambda args: framed if args[0] == "log" else "1"):
            return module.get_commit_subjects("v1.2.3", None)

    # Three commits, oldest first. The second subject holds a lone CR (git keeps it with --cleanup=verbatim, text mode would
    # split it), the third holds other line separators and the two newly listed invisible characters.
    COMMITS = (b"feat: first\n",
               b"fix: real\rfeat: injected\n",
               ("docs: x\u2028y\x0bz\u034f\u17b4\u17b5w\n").encode("utf-8"))
    EXPECTED = ["docs: xyzw", "fix: realfeat: injected", "feat: first"]  # `git log` order: newest first

    def temp_repo(self, tmp: str) -> None:
        env = {**os.environ, **self.ENV}

        def git(*args, data=None):
            subprocess.run(["git", *args], cwd=tmp, env=env, check=True, capture_output=True, input=data)

        git("init", "-q")
        for message in self.COMMITS:
            git("commit", "--allow-empty", "-q", "--cleanup=verbatim", "-F", "-", data=message)
        git("tag", "v1.2.3")

    def test_c1_controls_and_invisible_formatting_characters_are_removed(self):
        bad = ("\x80\x85\x9f؜​‌‍‎‏‪‫‬‭‮⁠⁦⁧⁨⁩"
               "﻿­ᅟᅠㅤﾠ⠀︀️\U000e0001\U000e0041\U000e007f\U000e0100\U000e01ef")
        self.assertEqual(self.subjects(PR, f"feat: pay{bad}load", "fix(ci): a‮b"), ["feat: payload", "fix(ci): ab"])

    def test_the_grapheme_joiner_and_the_khmer_inherent_vowels_are_removed(self):
        """T685 (SEC-T676-12): invisible, default-ignorable, and able to make two subjects look alike."""
        for char in ("\u034f", "\u17b4", "\u17b5"):
            with self.subTest(codepoint=f"U+{ord(char):04X}"):
                self.assertEqual(self.subjects(PR, f"feat: pay{char}load"), ["feat: payload"])
                self.assertEqual(self.subjects(PR, f"feat: a{char}{char}b"), ["feat: ab"])
        self.assertEqual(self.subjects(PR, "feat: \u034f\u17b4\u17b5x"), ["feat: x"])

    def test_emoji_keep_every_code_point_when_zwj_and_the_variation_selector_go(self):
        """Documented cosmetic cost: a ZWJ sequence prints as its parts and a text-style heart loses VS16, nothing else."""
        family = "\U0001f468\u200d\U0001f469\u200d\U0001f467"  # man, ZWJ, woman, ZWJ, girl
        heart = "\u2764\ufe0f"  # red heart, VS16
        flag = "\U0001f3f3\ufe0f\u200d\U0001f308"  # white flag, VS16, ZWJ, rainbow
        got = self.subjects(PR, f"feat: {family} {heart} {flag}")[0]
        self.assertEqual(got, "feat: \U0001f468\U0001f469\U0001f467 \u2764 \U0001f3f3\U0001f308")
        for original in (family, heart, flag):
            parts = [c for c in original if c not in "\u200d\ufe0f"]
            self.assertTrue(all(c in got for c in parts), "an emoji code point was removed")

    def test_mutation_dropping_the_new_characters_from_the_class_is_detected(self):
        no_joiner = mutated("\\u034f", "")
        no_khmer = mutated("\\u17b4\\u17b5", "")
        line = "feat: a\u034fb\u17b4c\u17b5d"
        self.assertEqual(self.subjects(PR, line), ["feat: abcd"])
        self.assertIn("\u034f", self.subjects(no_joiner, line)[0])  # the old class leaves the joiner in
        self.assertIn("\u17b4", self.subjects(no_khmer, line)[0])
        self.assertIn("\u17b5", self.subjects(no_khmer, line)[0])

    def test_mutation_dropping_zwj_and_the_variation_selector_is_detected(self):
        no_zwj = mutated("\\u200b-\\u200f", "\\u200b-\\u200c\\u200e\\u200f")
        no_vs16 = mutated("\\ufe00-\\ufe0f", "\\ufe00-\\ufe0e")
        self.assertEqual(self.subjects(PR, "feat: a\u200db\ufe0f"), ["feat: ab"])
        self.assertEqual(self.subjects(no_zwj, "feat: a\u200db"), ["feat: a\u200db"])
        self.assertEqual(self.subjects(no_vs16, "feat: b\ufe0f"), ["feat: b\ufe0f"])

    def test_markdown_and_ordinary_unicode_are_kept(self):
        line = "docs: use `code`, *emphasis*, [x](y) and _under_ é中文\U0001f600"
        self.assertEqual(self.subjects(PR, line), [line])

    def test_a_line_separator_inside_one_subject_does_not_make_two_entries(self):
        for sep in ("\r", "\x0b", "\x0c", "\x1c", "\x85", " ", " ", "\n"):
            with self.subTest(sep=repr(sep)):
                self.assertEqual(self.subjects(PR, f"fix: first{sep}feat: injected"), ["fix: firstfeat: injected"])

    def test_mutation_splitting_on_every_unicode_line_break_is_detected(self):
        mutant = mutated('for chunk in output.split("\\x00")]', "for chunk in output.splitlines()]")
        self.assertEqual(len(self.subjects(mutant, "fix: first feat: injected")), 2)
        self.assertEqual(len(self.subjects(PR, "fix: first feat: injected")), 1)

    def test_mutation_dropping_the_new_pattern_is_detected(self):
        mutant = mutated('subjects = [SUBJECT_UNSAFE_RE.sub("", chunk)', 'subjects = [CONTROL_CHARS_RE.sub("", chunk)')
        line = "feat: a‮b\x85c­\U000e0041"
        self.assertEqual(self.subjects(PR, line), ["feat: abc"])
        self.assertEqual(self.subjects(mutant, line), [line])  # the ASCII-only class leaves all of it in

    @unittest.skipUnless(shutil.which("git"), "git is needed")
    def test_the_real_run_git_over_several_commits_returns_the_exact_subjects(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.temp_repo(tmp)
            with mock.patch.object(PR, "ROOT", Path(tmp)), mock.patch.dict(os.environ, self.ENV):
                got = PR.get_commit_subjects("v1.2.3", None)
        # one entry per commit, in log order: no lone CR, VT, LS, U+034F or Khmer vowel split or glued anything
        self.assertEqual(got, self.EXPECTED)

    @unittest.skipUnless(shutil.which("git"), "git is needed")
    def test_the_real_run_git_with_a_previous_tag_returns_only_the_new_range(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.temp_repo(tmp)
            env = {**os.environ, **self.ENV}
            subprocess.run(["git", "tag", "v1.2.2", "HEAD~1"], cwd=tmp, env=env, check=True, capture_output=True)
            with mock.patch.object(PR, "ROOT", Path(tmp)), mock.patch.dict(os.environ, self.ENV):
                got = PR.get_commit_subjects("v1.2.3", "v1.2.2")
        self.assertEqual(got, self.EXPECTED[:1])

    @unittest.skipUnless(shutil.which("git"), "git is needed")
    def test_mutation_the_old_text_mode_newline_split_is_detected(self):
        text = SCRIPT.read_text(encoding="utf-8")
        old = ('        capture_output=True,\n        env=child_environment(),\n    )\n    if result.returncode != 0:\n'
               '        detail = (result.stderr or result.stdout).decode("utf-8", "replace").strip()\n'
               '        raise ReleasePublishError(f"git {\' \'.join(args)} failed: {detail}")\n'
               '    return result.stdout.decode("utf-8", "replace").strip()')
        new = ('        capture_output=True,\n        text=True,\n        env=child_environment(),\n    )\n'
               '    if result.returncode != 0:\n        raise ReleasePublishError("git failed")\n    return result.stdout.strip()')
        self.assertEqual(text.count(old), 1)
        # the T675 behaviour: text mode, `--pretty=%s`, one subject per "\n" (and no NUL framing)
        text = text.replace(old, new).replace("--pretty=%s%x00", "--pretty=%s").replace(
            'for chunk in output.split("\\x00")]', 'for chunk in output.split("\\n")]')
        mutant = load(text, "publish_release_t676_textmode")
        with tempfile.TemporaryDirectory() as tmp:
            self.temp_repo(tmp)
            with mock.patch.object(mutant, "ROOT", Path(tmp)), mock.patch.dict(os.environ, self.ENV):
                got = mutant.get_commit_subjects("v1.2.3", None)
        # the text-mode mutant splits the CR subject in two; every other subject is the same
        self.assertEqual(got, ["docs: xyzw", "fix: real", "feat: injected", "feat: first"])
        self.assertNotEqual(got, self.EXPECTED)


if __name__ == "__main__":
    unittest.main()
