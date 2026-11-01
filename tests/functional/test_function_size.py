"""Function-size guard for the shipped tooling (T677; TL-T649-01, TD-T671-FN1).

AGENTS.md "Code Standards" caps a function at 50 lines. The shipped tooling
files below (the installer, the sync engine, the merge and release helpers)
were refactored under T677 to meet that cap; this test keeps them there.

Length is physical: from the line that opens the function (its ``def``,
``function`` or ``name() {`` line) to the line that closes it, inclusive, so
blank lines, comments and docstrings count. Python functions are measured with
``ast`` (decorators are not counted), JavaScript and Bash functions by their
top-level opening line and the next column-0 closing brace.

Scope is exactly the files in ``SHIPPED_TOOLING``. The repository-wide
``implementation/runtime/**`` functions are accepted debt (TD-T671-FN2) and are
out of scope here.
"""
from __future__ import annotations

import ast
import re
import tempfile
import unittest
from pathlib import Path

from tests._helpers.repo import repo_root

MAX_LINES = 50

SHIPPED_TOOLING = (
    "implementation/scripts/sync.mjs",
    "scripts/install.sh",
    "scripts/merge-mcp-json.py",
    "scripts/merge-task-docs.py",
    "scripts/verify-release-docs.py",
    "scripts/render_installed_agents.py",
)

# (file, function) -> reason. Keep this list short and justified.
ALLOWLIST = {
    ("scripts/install.sh", "usage"): (
        "the --help text (a block of echo lines), no logic; TD-T671-FN1 ignores it"
    ),
}

_JS_START = re.compile(r"^(?:export\s+)?(?:async\s+)?function\s+([A-Za-z_$][\w$]*)\s*\(")
_SH_START = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)\(\)\s*\{\s*$")


def _python_sizes(text: str) -> dict[str, tuple[int, int]]:
    """Return {qualified name: (start line, length)} for every Python function."""
    sizes: dict[str, tuple[int, int]] = {}
    tree = ast.parse(text)

    def visit(node: ast.AST, prefix: str) -> None:
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                name = prefix + child.name
                sizes[name] = (child.lineno, child.end_lineno - child.lineno + 1)
                visit(child, name + ".")
            elif isinstance(child, ast.ClassDef):
                visit(child, prefix + child.name + ".")
            else:
                visit(child, prefix)

    visit(tree, "")
    return sizes


def _braced_sizes(text: str, start_re: re.Pattern[str]) -> dict[str, tuple[int, int]]:
    """Return sizes of column-0 functions that end at the next column-0 brace."""
    sizes: dict[str, tuple[int, int]] = {}
    name = None
    start = 0
    for number, line in enumerate(text.splitlines(), start=1):
        if name is None:
            match = start_re.match(line)
            if match:
                name, start = match.group(1), number
        elif line.startswith("}"):
            sizes[name] = (start, number - start + 1)
            name = None
    return sizes


def measure_text(relpath: str, text: str) -> dict[str, tuple[int, int]]:
    """Measure the functions of one file by its extension."""
    if relpath.endswith(".py"):
        return _python_sizes(text)
    if relpath.endswith(".mjs"):
        return _braced_sizes(text, _JS_START)
    if relpath.endswith(".sh"):
        return _braced_sizes(text, _SH_START)
    raise ValueError(f"unsupported file type: {relpath}")


def oversized(root: Path, relpaths=SHIPPED_TOOLING, allowlist=None) -> list[str]:
    """Return one message per function over MAX_LINES that is not allowlisted."""
    allowed = ALLOWLIST if allowlist is None else allowlist
    problems = []
    for relpath in relpaths:
        text = (root / relpath).read_text(encoding="utf-8")
        for name, (start, length) in measure_text(relpath, text).items():
            if length > MAX_LINES and (relpath, name) not in allowed:
                problems.append(f"{relpath}:{start} {name} is {length} lines (max {MAX_LINES})")
    return problems


class TestFunctionSize(unittest.TestCase):
    def test_shipped_tooling_functions_within_limit(self):
        problems = oversized(repo_root())
        self.assertEqual(problems, [], "functions over the 50-line standard:\n" + "\n".join(problems))

    def test_allowlist_entries_exist_and_are_needed(self):
        root = repo_root()
        for (relpath, name), reason in ALLOWLIST.items():
            self.assertTrue(reason.strip(), f"allowlist entry {name} has no reason")
            sizes = measure_text(relpath, (root / relpath).read_text(encoding="utf-8"))
            self.assertIn(name, sizes, f"allowlisted {relpath}:{name} no longer exists")
            self.assertGreater(
                sizes[name][1], MAX_LINES,
                f"allowlisted {relpath}:{name} is within the limit; remove it from ALLOWLIST",
            )

    def test_every_tooling_file_is_measured(self):
        root = repo_root()
        for relpath in SHIPPED_TOOLING:
            sizes = measure_text(relpath, (root / relpath).read_text(encoding="utf-8"))
            self.assertGreater(len(sizes), 3, f"{relpath}: the measurer found almost no functions")

    def test_mutation_oversized_function_is_detected(self):
        """A copy of each file type with one oversized function must fail."""
        body = "\n".join(f"    x{i} = {i}" for i in range(60))
        samples = {
            "sample.py": f"def big():\n{body}\n    return 1\n",
            "sample.mjs": "function big() {\n" + "\n".join(f"  const x{i} = {i};" for i in range(60)) + "\n}\n",
            "sample.sh": "big() {\n" + "\n".join(f"  x{i}={i}" for i in range(60)) + "\n}\n",
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for relpath, text in samples.items():
                (root / relpath).write_text(text, encoding="utf-8")
            problems = oversized(root, relpaths=tuple(samples), allowlist={})
            self.assertEqual(len(problems), 3, problems)
            allowed = {("sample.py", "big"): "x", ("sample.mjs", "big"): "x", ("sample.sh", "big"): "x"}
            self.assertEqual(oversized(root, relpaths=tuple(samples), allowlist=allowed), [])

    def test_boundary_exactly_50_lines_passes(self):
        text = "def ok():\n" + "\n".join(f"    x{i} = {i}" for i in range(49)) + "\n"
        self.assertEqual(_python_sizes(text)["ok"][1], 50)
        text += "    y = 1\n"
        self.assertEqual(_python_sizes(text)["ok"][1], 51)


if __name__ == "__main__":
    unittest.main()
