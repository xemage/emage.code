"""Function-size guard for the shipped tooling (T677; TL-T649-01, TD-T671-FN1).

AGENTS.md "Code Standards" caps a function at 50 lines. The shipped tooling
files below (the installer, the sync engine, the merge and release helpers)
were refactored under T677 to meet that cap; this test keeps them there.

Length is physical: from the line that opens the function (its ``def``,
``function`` or ``name() {`` line) to the line that closes it, inclusive, so
blank lines, comments and docstrings count. Python functions are measured with
``ast`` (decorators are not counted; a redefined name is measured under
``name@line`` too, so the earlier body is not hidden).

JavaScript and Bash functions are measured line by line (T715, SEC-T677-01): a
function opens on a recognised header line at any indentation and closes at the
next line that starts with the same indentation followed by ``}``. Nested
functions are measured on their own (they also count towards the enclosing one).
Recognised Bash headers: ``name() {``, ``name () {``, ``function name {``,
``function name() {``, and each of them with ``{`` alone on the next line; the
bodies of here-documents (``<<EOF``, ``<<'EOF'``, ``<<-EOF``) are skipped, so a
``}`` inside one does not end a function. Recognised JavaScript headers:
``function`` declarations (``export``, ``async``, generators), ``const``/``let``/
``var`` bindings of a function expression or a block-bodied arrow, object
properties of the same, and class or object methods whose parameters fit on the
header line. A header whose braces balance on its own line is a one-line
function. A function that never closes fails the guard (``ValueError``) instead
of being dropped, and a repeated name is measured under ``name@line``.

Not closed by a line-based guard (residual, reported in T715): a ``}`` at the
function's indentation inside a multi-line JavaScript template literal or string
still ends the function early (telling a template literal from a backtick inside
a regular-expression literal needs a JavaScript lexer); a method whose
parameters span several lines, an anonymous callback (counted only as part of
its enclosing function), a Bash function whose body is a subshell
``name() ( ... )``, and code formatted with the closing brace at a different
indentation than its header (then the guard fails closed as unclosed).

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
        "the --help text: quoted heredocs and printf lines, no command substitution and no control flow "
        "(T723, SEC-T677-03, pinned by test_allowlisted_usage_holds_no_logic); TD-T671-FN1 ignores it"
    ),
}
# A line of the allowlisted `usage` outside its heredocs (T723, SEC-T677-03): only these shapes.
_USAGE_LINE = re.compile(r"^(?:usage\(\) \{|\}|[ \t]*#.*|[ \t]*cat <<'EOF'|[ \t]*printf '[^'$`]*'(?: \"\$\{SUPPORTED_PLATFORMS\[@\]\}\")?)$")

_JS_FUNC_VALUE = r"(?:async[ \t]+)?(?:function\b|(?:\([^)]*\)|[A-Za-z_$][\w$]*)[ \t]*=>[ \t]*\{[ \t]*$)"
_JS_STARTS = (
    re.compile(r"^(?P<indent>[ \t]*)(?:export[ \t]+)?(?:default[ \t]+)?(?:async[ \t]+)?function\b[ \t]*\*?[ \t]*"
               r"(?P<name>[A-Za-z_$][\w$]*)[ \t]*\("),
    re.compile(r"^(?P<indent>[ \t]*)(?:export[ \t]+)?(?:const|let|var)[ \t]+(?P<name>[A-Za-z_$][\w$]*)[ \t]*=[ \t]*"
               + _JS_FUNC_VALUE),
    re.compile(r"^(?P<indent>[ \t]+)(?P<name>[A-Za-z_$][\w$]*)[ \t]*:[ \t]*" + _JS_FUNC_VALUE),
    re.compile(r"^(?P<indent>[ \t]+)(?:static[ \t]+)?(?:async[ \t]+)?\*?(?:(?:get|set)[ \t]+)?"
               r"(?P<name>#?[A-Za-z_$][\w$]*)[ \t]*\([^)]*\)[ \t]*\{[ \t]*$"),
)
_JS_NOT_METHODS = frozenset({"if", "for", "while", "switch", "catch", "with", "function", "return", "else", "do"})
_SH_START = re.compile(
    r"^(?P<indent>[ \t]*)(?:function[ \t]+(?P<kw>[A-Za-z_][\w:.-]*)(?:[ \t]*\([ \t]*\))?"
    r"|(?P<plain>[A-Za-z_][\w:.-]*)[ \t]*\([ \t]*\))[ \t]*\{[ \t]*(?:#.*)?$"
)
_SH_HEADER_ONLY = re.compile(r"^[ \t]*(?:function[ \t]+[A-Za-z_][\w:.-]*(?:[ \t]*\([ \t]*\))?"
                             r"|[A-Za-z_][\w:.-]*[ \t]*\([ \t]*\))[ \t]*$")
_SH_HEREDOC = re.compile(r"(?<!<)<<(?!<)(?P<dash>-?)[ \t]*(?P<q>['\"]?)(?P<word>[A-Za-z_][A-Za-z0-9_]*)(?P=q)")


def _record(sizes: dict[str, tuple[int, int]], name: str, start: int, end: int) -> None:
    """Store one function; a name seen before is stored as ``name@start`` so no body is hidden."""
    key = name if name not in sizes else f"{name}@{start}"
    sizes[key] = (start, end - start + 1)


def _python_sizes(text: str) -> dict[str, tuple[int, int]]:
    """Return {qualified name: (start line, length)} for every Python function."""
    sizes: dict[str, tuple[int, int]] = {}
    tree = ast.parse(text)

    def visit(node: ast.AST, prefix: str) -> None:
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                name = prefix + child.name
                _record(sizes, name, child.lineno, child.end_lineno)
                visit(child, name + ".")
            elif isinstance(child, ast.ClassDef):
                visit(child, prefix + child.name + ".")
            else:
                visit(child, prefix)

    visit(tree, "")
    return sizes


def _js_start(line: str) -> tuple[str, str] | None:
    """``(name, indent)`` when ``line`` opens a JavaScript function, else None."""
    for pattern in _JS_STARTS:
        match = pattern.match(line)
        if match and match.group("name") not in _JS_NOT_METHODS:
            return match.group("name"), match.group("indent")
    return None


def _sh_start(line: str) -> tuple[str, str] | None:
    """``(name, indent)`` when ``line`` opens a Bash function with ``{`` on the same line, else None."""
    match = _SH_START.match(line)
    if not match:
        return None
    return match.group("kw") or match.group("plain"), match.group("indent")


def _sh_code_lines(text: str) -> list[tuple[int, str]]:
    """Numbered Bash lines without here-document bodies; a header followed by a lone ``{`` is joined to it."""
    lines = text.splitlines()
    code: list[tuple[int, str]] = []
    pending: list[tuple[str, str]] = []  # (delimiter, dash) of here-documents opened on the last code line
    index = 0
    while index < len(lines):
        line = lines[index]
        index += 1
        if pending:
            word, dash = pending[0]
            if (line.lstrip("\t") if dash else line) == word:
                pending.pop(0)
            continue
        if _SH_HEADER_ONLY.match(line) and index < len(lines) and lines[index].strip() == "{":
            code.append((index, line.rstrip() + " {"))
            index += 1
            continue
        code.append((index, line))
        if not line.lstrip().startswith("#"):
            pending = [(m.group("word"), m.group("dash")) for m in _SH_HEREDOC.finditer(line)]
    return code


def _braced_sizes(lines: list[tuple[int, str]], start_of) -> dict[str, tuple[int, int]]:
    """Sizes of the functions ``start_of`` recognises; each ends at the next ``<its indent>}`` line."""
    sizes: dict[str, tuple[int, int]] = {}
    stack: list[tuple[str, int, str]] = []  # (name, start line, indent)
    for number, line in lines:
        if stack:
            name, start, indent = stack[-1]
            if line.startswith(indent) and line[len(indent):].startswith("}"):
                stack.pop()
                _record(sizes, name, start, number)
                continue
        found = start_of(line)
        if found and not ("{" in line and line.count("{") == line.count("}")):
            stack.append((found[0], number, found[1]))
    if stack:
        name, start, _ = stack[-1]
        raise ValueError(f"function {name} opened at line {start} is never closed")
    return sizes


def measure_text(relpath: str, text: str) -> dict[str, tuple[int, int]]:
    """Measure the functions of one file by its extension."""
    if relpath.endswith(".py"):
        return _python_sizes(text)
    if relpath.endswith(".mjs"):
        return _braced_sizes(list(enumerate(text.splitlines(), start=1)), _js_start)
    if relpath.endswith(".sh"):
        return _braced_sizes(_sh_code_lines(text), _sh_start)
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

    def test_allowlisted_usage_holds_no_logic(self):
        """T723 (SEC-T677-03): the reason "no logic" stays true -- no command substitution, no control flow."""
        text = (repo_root() / "scripts" / "install.sh").read_text(encoding="utf-8")
        body = re.search(r"^usage\(\) \{\n.*?^\}\n", text, re.S | re.M).group(0)
        outside = re.sub(r"^[ \t]*cat <<'EOF'\n.*?^EOF\n", "cat <<'EOF'\n", body, flags=re.S | re.M)
        self.assertNotIn("<<EOF", outside.replace("<<'EOF'", ""), "an unquoted heredoc expands $(...)")
        for line in outside.splitlines():
            self.assertRegex(line, _USAGE_LINE)
        self.assertNotRegex("  printf '%s' \"$(join_bar a b)\"", _USAGE_LINE)

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


def _body(prefix: str, count: int = 60) -> str:
    return "\n".join(f"{prefix}x{i}={i}" for i in range(count))


class TestMeasuredShapes(unittest.TestCase):
    """T715 (SEC-T677-01): each shape the old column-0 measurer missed is now measured.

    Each sample holds one 62-line function named ``big``; the old measurer reported nothing
    (or a short length) for every one of them.
    """

    def assertBig(self, relpath: str, text: str, minimum: int = 62) -> None:
        sizes = measure_text(relpath, text)
        self.assertIn("big", sizes, sizes)
        self.assertGreaterEqual(sizes["big"][1], minimum, sizes)

    def test_bash_header_shapes(self):
        body = _body("  ")
        for header in ("function big {", "function big() {", "big () {", "big()\n{", "function big\n{",
                       "  big() {"):
            with self.subTest(header=header):
                indent = "  " if header.startswith("  ") else ""
                self.assertBig("s.sh", f"{header}\n{body}\n{indent}}}\n", minimum=61)

    def test_bash_heredoc_brace_does_not_end_the_function(self):
        for opener, closer in (("<<EOF", "EOF"), ("<<'EOF'", "EOF"), ('<< "END"', "END"), ("<<-EOF", "\tEOF")):
            with self.subTest(opener=opener):
                text = f"big() {{\n  cat {opener}\n}}\n{closer}\n{_body('  ')}\n}}\nafter() {{\n  :\n}}\n"
                sizes = measure_text("s.sh", text)
                self.assertEqual(sizes["big"], (1, 65), sizes)
                self.assertIn("after", sizes)

    def test_bash_here_string_and_one_liners_are_not_misread(self):
        text = "one() { echo hi; }\nbig() {\n  x=$(cat <<< \"$y\")\n" + _body("  ") + "\n}\n"
        sizes = measure_text("s.sh", text)
        self.assertEqual(sorted(sizes), ["big"])
        self.assertEqual(sizes["big"][1], 63)

    def test_javascript_shapes(self):
        body = _body("    ")
        for header, closer in (
            ("const big = (a, b) => {", "};"),
            ("export const big = async x => {", "};"),
            ("let big = function (a) {", "};"),
            ("  big: ({ server }) => {", "  },"),
            ("  async big(a, b) {", "  }"),
            ("  static big() {", "  }"),
            ("  function big(a) {", "  }"),
            ("export default async function* big(a) {", "}"),
        ):
            with self.subTest(header=header):
                self.assertBig("s.mjs", f"{header}\n{body}\n{closer}\n", minimum=61)

    def test_javascript_nested_function_is_measured_on_its_own(self):
        text = "function outer() {\n  function big() {\n" + _body("    ") + "\n  }\n  return big;\n}\n"
        sizes = measure_text("s.mjs", text)
        self.assertEqual(sizes["big"], (2, 62))
        self.assertEqual(sizes["outer"], (1, 65))

    def test_javascript_control_flow_and_one_liners_are_not_functions(self):
        text = ("function f(x) {\n  if (x) {\n    g();\n  }\n  for (const y of x) {\n  }\n}\n"
                "const id = (v) => { return v; };\nfunction g() { return 1; }\n")
        self.assertEqual(sorted(measure_text("s.mjs", text)), ["f"])

    def test_a_redefined_name_does_not_hide_the_earlier_body(self):
        samples = {
            "s.py": f"def big():\n{_body('    ')}\n    return 1\n\n\ndef big():\n    return 2\n",
            "s.sh": f"big() {{\n{_body('  ')}\n}}\nbig() {{\n  :\n}}\n",
            "s.mjs": f"function big() {{\n{_body('  ')}\n}}\nfunction big() {{\n  return 1;\n}}\n",
        }
        for relpath, text in samples.items():
            with self.subTest(relpath=relpath):
                sizes = measure_text(relpath, text)
                self.assertGreater(sizes["big"][1], MAX_LINES, sizes)
                self.assertEqual(len([k for k in sizes if k.split("@")[0] == "big"]), 2, sizes)
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "s.py").write_text(samples["s.py"], encoding="utf-8")
            self.assertEqual(len(oversized(Path(tmp), relpaths=("s.py",), allowlist={})), 1)

    def test_an_unclosed_function_fails_closed(self):
        for relpath, text in (
            ("s.sh", "big() {\n  :\n"),
            ("s.sh", "big() {\n  cat <<EOF\n}\n"),
            ("s.mjs", "function big() {\n  return 1;\n"),
            ("s.mjs", "function big() {\n  return 1;\n  }\n"),
        ):
            with self.subTest(text=text):
                with self.assertRaisesRegex(ValueError, "big opened at line 1 is never closed"):
                    measure_text(relpath, text)


if __name__ == "__main__":
    unittest.main()
