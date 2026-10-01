"""Command audience path lint (T557, plan-088 / plan-087 P23).

T556 made every command declare ``audience: authoring | target | both``. This
test makes the declaration *checked*: a command that ships to installed target
projects (``both`` or ``target``) must not name a path that exists in this
repository but that an installed target never receives.

Like the root parity gate (``test_root_install_parity.py``, T543) the installer
is the oracle, so there is no hand-maintained list of "authoring-only paths":
one fresh ``scripts/install.sh --platform all`` (never ``--update``, never into
the repository) runs into a temporary directory, and every reference is
resolved against both trees. ``--platform all`` is the *largest* install, so a
path absent from it is absent from every install -- the gate is exact for
"never receives" and deliberately silent on "receives only with some platforms".

``authoring`` commands (today only ``/prepare-release``) are exempt: they are
declared never to run in a target, so naming authoring-only paths is their job.

Extraction rule -- what counts as a path-like reference
-------------------------------------------------------
The whole body after the frontmatter is scanned, prose and code alike (a
superset of "backticked tokens containing ``/``"; the extra prose tokens are
alternations like ``yes/no`` that resolve nowhere and so can never be flagged):

* a token is a maximal run of non-whitespace, where a ``<placeholder>`` counts
  as one unit even if it contains spaces (``agent/<Assigned agent>/<Task ID>``);
* wrapping Markdown/prose punctuation is stripped (backticks, ``*``, brackets,
  quotes, trailing ``.,;:!?``) -- a *leading* ``.`` is kept (``.claude/``);
* the token must contain ``/``; URLs (``://``), absolute paths and slash
  commands (a leading ``/``: ``/discover-skills``, ``/...``) and anything with a
  ``..`` segment are ignored;
* a ``<placeholder>`` matches one or more characters within one path segment,
  ``*`` zero or more within one segment, and a whole ``**`` segment any depth;
  placeholders and ``*`` also match dot-names, so ``<platform>/skills`` reaches
  ``.claude/skills`` (that is what the commands mean by it).

Resolution rule -- where a reference points
-------------------------------------------
A reference resolves in a tree if it matches an existing file or directory
under any of three bases: the root, ``implementation/`` and
``implementation/knowledge/``. The commands cite paths in exactly these three
frames -- root-relative (``implementation/registry/index.json``),
``implementation/``-relative (``packs/installed/`` -- P22,
``registry/summary.md``) and knowledge-relative (``commands/plan.md``,
``skills/<name>/SKILL.md``) -- and a root-only rule would let the last two
frames dangle silently in *both* audiences, i.e. never be flagged. The same
three bases are applied to the fresh install, so the comparison is like for
like: an installed target has a real ``implementation/`` directory too
(``implementation/runtime/``), and a reference resolving under any base there
is not a leak.

One exclusion on the repository side: this repository's own root ``docs/`` is
project *state* (its ledger, plans, checkpoints), produced by running these
very commands, and the installer treats ``docs/`` as project-owned
(merge-preserve-existing; the parity gate's ``NOT_ROOT_OWNED``). So a
*templated* reference (one with a placeholder or ``*``) does not count as
existing just because this repository's ``docs/`` holds an instance of it --
``docs/plans/plan-<ID>.md`` names a file the command creates in whatever
project runs it. A *literal* reference into ``docs/`` still counts, so a shipped
command naming one of this repository's own artifacts is flagged.

A reference is a **violation** when it resolves in the repository and not in
the fresh install. Known violations are *declared* in
``tests/_baselines/command-audience-paths.json`` as ``{command, path, reason}``.
The gate is bidirectional, exactly like the parity gate: an undeclared
violation fails, and a declared entry that is no longer a violation fails, so
the declaration can neither hide a new leak nor outlive its repair.

Print the current violation set with::

    python3 -m tests.functional.test_command_audience_paths --print-violations
"""
from __future__ import annotations

import json
import os
import re
import sys
import tempfile
import unittest
from pathlib import Path

from tests._helpers.repo import knowledge_root, repo_root
from tests.functional.test_root_install_parity import run_fresh_install

BASELINE = repo_root() / "tests" / "_baselines" / "command-audience-paths.json"
COMMANDS_DIR = knowledge_root() / "commands"
AUDIENCES = {"authoring", "target", "both"}
CHECKED_AUDIENCES = {"target", "both"}  # `authoring` is exempt by declaration
BASES = ("", "implementation", "implementation/knowledge")
PROJECT_STATE_DIR = "docs"  # see "One exclusion" in the module docstring
SKIP_NAMES = {".git", "__pycache__", "node_modules"}

_FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n(.*)\Z", re.S)
_AUDIENCE_RE = re.compile(r"^audience:\s*(\S+)\s*$", re.M)
_TOKEN_RE = re.compile(r"(?:<[^<>\n]*>|[^\s<])+")
_PLACEHOLDER_RE = re.compile(r"<[^<>\n]*>")
_LEAD_STRIP = "`*_([{\"'"
_TRAIL_STRIP = "`*_)]}\"'.,;:!?"


def parse_command(path: Path) -> tuple[str, str]:
    """Return ``(audience, body)``; a missing or unknown audience is an error."""
    match = _FRONTMATTER_RE.match(path.read_text(encoding="utf-8"))
    if match is None:
        raise AssertionError(f"{path.name}: no frontmatter")
    audience = _AUDIENCE_RE.search(match.group(1))
    if audience is None or audience.group(1) not in AUDIENCES:
        raise AssertionError(f"{path.name}: missing or invalid `audience:` (T556)")
    return audience.group(1), match.group(2)


def _normalise(token: str) -> str | None:
    token = token.lstrip(_LEAD_STRIP).rstrip(_TRAIL_STRIP)
    if "/" not in token or "://" in token or token.startswith("/"):
        return None
    if ".." in token.split("/"):
        return None
    return token


def extract_references(body: str) -> set[str]:
    """Path-like references in a command body (module docstring rule)."""
    refs = (_normalise(t) for t in _TOKEN_RE.findall(body))
    return {r for r in refs if r}


def _segment_matcher(segment: str):
    if segment == "**" or not (_PLACEHOLDER_RE.search(segment) or "*" in segment):
        return segment
    parts = []
    for piece in re.split(r"(<[^<>\n]*>|\*)", segment):
        if piece == "*":
            parts.append(".*")
        elif _PLACEHOLDER_RE.fullmatch(piece):
            parts.append(".+")
        else:
            parts.append(re.escape(piece))
    return re.compile("".join(parts))


def is_templated(ref: str) -> bool:
    return bool(_PLACEHOLDER_RE.search(ref)) or "*" in ref


def _children(base: Path):
    try:
        return [e for e in os.scandir(base) if e.name not in SKIP_NAMES]
    except (FileNotFoundError, NotADirectoryError):
        return []


def _match(base: Path, segments: list) -> bool:
    if not segments:
        return base.exists()
    head, rest = segments[0], segments[1:]
    if head == "**":
        if _match(base, rest):
            return True
        return any(e.is_dir() and _match(Path(e.path), segments) for e in _children(base))
    if isinstance(head, str):
        return _match(base / head, rest)
    return any(head.fullmatch(e.name) and _match(Path(e.path), rest)
               for e in _children(base))


def resolves(tree: Path, ref: str, *, project_state_counts: bool = True) -> bool:
    """True if ``ref`` names an existing file/dir under any base of ``tree``."""
    segments = [_segment_matcher(s) for s in ref.split("/") if s]
    for base in BASES:
        full = ([*base.split("/")] if base else []) + segments
        if not project_state_counts and full and full[0] == PROJECT_STATE_DIR:
            continue
        if _match(tree, full):
            return True
    return False


def command_name(path: Path) -> str:
    return "/" + path.stem


def checked_commands(commands_dir: Path = COMMANDS_DIR) -> list[tuple[Path, str]]:
    """``(path, body)`` of every command whose audience reaches a target."""
    out = []
    for path in sorted(commands_dir.glob("*.md")):
        audience, body = parse_command(path)
        if audience in CHECKED_AUDIENCES:
            out.append((path, body))
    return out


def find_violations(commands: list[tuple[Path, str]], repo: Path,
                    fresh: Path) -> set[tuple[str, str]]:
    """``(command, path)`` pairs resolving in ``repo`` but not in ``fresh``."""
    found: set[tuple[str, str]] = set()
    for path, body in commands:
        for ref in extract_references(body):
            in_repo = resolves(repo, ref, project_state_counts=not is_templated(ref))
            if in_repo and not resolves(fresh, ref):
                found.add((command_name(path), ref))
    return found


def current_violations() -> set[tuple[str, str]]:
    with tempfile.TemporaryDirectory(prefix="emage-audience-paths-") as tmp:
        fresh = Path(tmp) / "fresh"
        run_fresh_install(fresh)
        return find_violations(checked_commands(), repo_root(), fresh)


def load_declared(baseline: Path = BASELINE) -> set[tuple[str, str]]:
    entries = json.loads(baseline.read_text(encoding="utf-8"))["violations"]
    for entry in entries:
        if set(entry) != {"command", "path", "reason"} or not entry["reason"].strip():
            raise AssertionError(f"malformed baseline entry: {entry}")
    return {(e["command"], e["path"]) for e in entries}


def gate_message(actual: set, declared: set) -> str | None:
    """The failure message for ``actual`` vs ``declared``, or None if they agree."""
    undeclared, cured = sorted(actual - declared), sorted(declared - actual)
    if not (undeclared or cured):
        return None
    return (
        "Commands declared `audience: both|target` name paths a fresh "
        "`install.sh --platform all` never ships, in ways "
        "tests/_baselines/command-audience-paths.json does not declare.\n"
        f"  Undeclared violations (fix the command, or declare with a reason): {undeclared}\n"
        f"  Declared but no longer violations (remove): {cured}\n"
        "List them with: python3 -m tests.functional.test_command_audience_paths "
        "--print-violations"
    )


class TestCommandAudiencePaths(unittest.TestCase):
    def test_every_command_declares_an_audience(self) -> None:
        """Guard against a vacuous gate: commands must parse and most must be checked."""
        commands = sorted(COMMANDS_DIR.glob("*.md"))
        self.assertGreaterEqual(len(commands), 19)
        audiences = {p.stem: parse_command(p)[0] for p in commands}
        self.assertEqual(audiences.get("prepare-release"), "authoring")
        self.assertGreater(len(checked_commands()), len(commands) // 2)

    def test_commands_name_only_installed_paths_modulo_declared(self) -> None:
        message = gate_message(current_violations(), load_declared())
        if message:
            self.fail(message)


class TestCommandAudienceDetector(unittest.TestCase):
    """The detector against synthetic inputs -- proves the gate is load-bearing."""

    @classmethod
    def setUpClass(cls) -> None:
        cls._tmp = tempfile.TemporaryDirectory(prefix="emage-audience-paths-self-")
        cls.fresh = Path(cls._tmp.name) / "fresh"
        run_fresh_install(cls.fresh)

    @classmethod
    def tearDownClass(cls) -> None:
        cls._tmp.cleanup()

    def _commands(self, **files: str) -> Path:
        cmd_dir = Path(self._tmp.name) / f"cmds-{self._testMethodName}"
        cmd_dir.mkdir()
        for stem, text in files.items():
            (cmd_dir / f"{stem}.md").write_text(text, encoding="utf-8")
        return cmd_dir

    def _violations(self, cmd_dir: Path) -> set[tuple[str, str]]:
        return find_violations(checked_commands(cmd_dir), repo_root(), self.fresh)

    def test_extraction_rule(self) -> None:
        body = ("See `implementation/registry/index.json`, (plan/architecture), "
                "`/discover-skills`, https://example.com/x, `../etc/passwd`, "
                "`node implementation/scripts/sync.mjs --root implementation`, "
                "`agent/<Assigned agent>/<Task ID>`, and `.claude/`.")
        self.assertEqual(extract_references(body), {
            "implementation/registry/index.json", "plan/architecture",
            "implementation/scripts/sync.mjs", "agent/<Assigned agent>/<Task ID>",
            ".claude/",
        })

    def test_authoring_only_path_in_both_command_is_flagged(self) -> None:
        cmd_dir = self._commands(leaky="---\naudience: both\n---\n"
                                       "Read `implementation/registry/index.json`.\n")
        self.assertEqual(self._violations(cmd_dir),
                         {("/leaky", "implementation/registry/index.json")})

    def test_target_audience_is_checked_and_authoring_exempt(self) -> None:
        text = "Run `implementation/scripts/sync.mjs`.\n"
        cmd_dir = self._commands(t="---\naudience: target\n---\n" + text,
                                 a="---\naudience: authoring\n---\n" + text)
        self.assertEqual(self._violations(cmd_dir),
                         {("/t", "implementation/scripts/sync.mjs")})

    def test_installed_and_templated_paths_are_not_flagged(self) -> None:
        cmd_dir = self._commands(clean=(
            "---\naudience: both\n---\n"
            "Load `.<platform>/skills/<name>/SKILL.md` or `<platform>/skills/*/SKILL.md`; "
            "validate against `implementation/runtime/handoff/schema-v1.json`; "
            "write `docs/plans/plan-<ID>.md` and `docs/checkpoints/**`; "
            "run `python3 docs/tasks/validate-tasks.py`.\n"))
        self.assertEqual(self._violations(cmd_dir), set())

    def test_relative_frames_are_resolved(self) -> None:
        cmd_dir = self._commands(frames=(
            "---\naudience: both\n---\n"
            "Follow `commands/plan.md` and merge `packs/installed/`.\n"))
        self.assertEqual(self._violations(cmd_dir),
                         {("/frames", "commands/plan.md"),
                          ("/frames", "packs/installed/")})

    def test_literal_reference_into_repo_docs_is_flagged(self) -> None:
        cmd_dir = self._commands(own=(
            "---\naudience: both\n---\n"
            "See `docs/plans/plan-088-audience-lint.md`.\n"))
        self.assertEqual(self._violations(cmd_dir),
                         {("/own", "docs/plans/plan-088-audience-lint.md")})

    def test_missing_audience_is_an_error(self) -> None:
        cmd_dir = self._commands(bare="---\nmaturity: stable\n---\nbody\n")
        with self.assertRaises(AssertionError):
            checked_commands(cmd_dir)

    def test_gate_fails_in_both_directions(self) -> None:
        actual = {("/a", "x/y"), ("/b", "p/q")}
        self.assertIsNone(gate_message(actual, set(actual)))
        undeclared = gate_message(actual, {("/a", "x/y")})
        self.assertIn("Undeclared violations (fix the command, or declare with a "
                      "reason): [('/b', 'p/q')]", undeclared)
        cured = gate_message(actual, actual | {("/c", "bogus/path")})
        self.assertIn("Declared but no longer violations (remove): "
                      "[('/c', 'bogus/path')]", cured)

    def test_baseline_entries_need_a_reason(self) -> None:
        bad = Path(self._tmp.name) / "bad-baseline.json"
        bad.write_text(json.dumps({"violations": [
            {"command": "/a", "path": "x/y", "reason": " "}]}), encoding="utf-8")
        with self.assertRaises(AssertionError):
            load_declared(bad)


def _main(argv: list[str]) -> int:
    if argv != ["--print-violations"]:
        print(__doc__)
        return 2
    rows = [{"command": c, "path": p} for c, p in sorted(current_violations())]
    print(json.dumps(rows, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv[1:]))
