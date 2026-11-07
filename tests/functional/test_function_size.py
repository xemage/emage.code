"""Function-size guard for the shipped tooling (T677; TL-T649-01, TD-T671-FN1).

AGENTS.md "Code Standards" caps a function at 50 lines. The shipped tooling
files below (the installer, the sync engine, the merge and release helpers)
were refactored under T677 to meet that cap; this test keeps them there, and
it keeps every tracked ``.mjs``, ``.js`` and ``.cjs`` file there too (T732).

Length is physical: from the line that opens the function to the line that
closes it, inclusive, so blank lines, comments and docstrings count. Python
functions are measured with ``ast`` (decorators are not counted; a redefined
name is measured under ``name@line`` too, so the earlier body is not hidden).

JavaScript is measured with a real parser (T732, SEC-T677-01): the Node script
``ci/js/measure-functions.mjs`` parses each file with acorn, pinned to an exact
version in ``ci/js/package.json`` and integrity-locked in
``ci/js/package-lock.json`` (install: ``npm ci --ignore-scripts --prefix
ci/js``; update rule: ``ci/js/README.md``). It reports every function
declaration and expression, arrow function, object or class method, getter,
setter and class-field function, anonymous ones (callbacks, IIFEs) as
``(anonymous)``; a nested function is measured on its own and also counts
towards the enclosing one; a method starts at its key. A file that does not
parse fails the guard (``ValueError``). This closes the T715 residuals of the
line measurer: a ``}`` inside a template literal, string or comment, methods
whose parameters span lines, anonymous callbacks, expression-bodied arrows,
class fields, member assignments, a closing brace at another indentation
(``TestParserClosesResiduals`` proves each against the old line measurer,
which is kept here only as that baseline). When node or the pinned acorn is
missing, every JavaScript test fails under CI (env ``CI`` set) and skips
locally with the reason; the Python and Bash checks still run.

Bash functions are measured line by line (T715): a function opens on a
recognised header line at any indentation and closes at the next line that
starts with the same indentation followed by ``}``. Recognised headers:
``name() {``, ``name () {``, ``function name {``, ``function name() {``, and
each of them with ``{`` alone on the next line; here-document bodies
(``<<EOF``, ``<<'EOF'``, ``<<-EOF``) are skipped, so a ``}`` inside one does not
end a function. A function that never closes fails the guard (``ValueError``),
and a repeated name is measured under ``name@line``. Not closed for Bash: a
function whose body is a subshell ``name() ( ... )``, and a closing brace at a
different indentation than its header (then the guard fails closed as
unclosed).

Scope is the files in ``SHIPPED_TOOLING`` plus every tracked JavaScript file.
The repository-wide ``implementation/runtime/**`` Python functions are accepted
debt (TD-T671-FN2) and are out of scope here.
"""
from __future__ import annotations

import ast
import json
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from tests._helpers.repo import repo_root

MAX_LINES = 50
JS_SUFFIXES = (".mjs", ".js", ".cjs")
JS_DIR = "ci/js"
JS_MEASURER = f"{JS_DIR}/measure-functions.mjs"
JS_INSTALL = f"npm ci --ignore-scripts --prefix {JS_DIR}"
JS_TIMEOUT_SECONDS = 60

SHIPPED_TOOLING = (
    "implementation/scripts/sync.mjs",
    "scripts/install.sh",
    "scripts/merge-mcp-json.py",
    "scripts/merge-task-docs.py",
    "scripts/verify-release-docs.py",
    "scripts/render_installed_agents.py",
    JS_MEASURER,
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

# The T715 line measurer for JavaScript. Not used by the guard any more (T732); kept only as the
# baseline that TestParserClosesResiduals proves the parser beats, shape by shape.
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


class JsParserUnavailable(RuntimeError):
    """node or the pinned acorn is not installed, so JavaScript cannot be measured."""


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


def js_parser_missing(root: Path | None = None) -> str | None:
    """Why JavaScript cannot be measured (node or the pinned acorn missing), or None when it can."""
    base = (root or repo_root()) / JS_DIR
    if shutil.which("node") is None:
        return "node is not on PATH"
    pin = json.loads((base / "package.json").read_text(encoding="utf-8"))["dependencies"]["acorn"]
    installed = base / "node_modules" / "acorn" / "package.json"
    if not installed.is_file():
        return f"acorn {pin} is not installed; run `{JS_INSTALL}`"
    version = json.loads(installed.read_text(encoding="utf-8")).get("version")
    if version != pin:
        return f"acorn {version} is installed but {JS_DIR}/package.json pins {pin}; run `{JS_INSTALL}`"
    return None


def require_js_parser(case: unittest.TestCase) -> None:
    """A missing JavaScript parser fails the test under CI (env ``CI`` set) and skips it locally."""
    missing = js_parser_missing()
    if missing is None:
        return
    if os.environ.get("CI"):
        case.fail(f"JavaScript parser missing under CI: {missing}")
    case.skipTest(f"JavaScript functions not measured (local skip; CI fails): {missing}")


def _js_sizes(relpath: str, text: str) -> dict[str, tuple[int, int]]:
    """Sizes reported by ci/js/measure-functions.mjs (acorn) for one JavaScript source."""
    missing = js_parser_missing()
    if missing is not None:
        raise JsParserUnavailable(missing)
    argv = [shutil.which("node"), str(repo_root() / JS_MEASURER), "--stdin", relpath]
    proc = subprocess.run(argv, input=text, capture_output=True, text=True, encoding="utf-8",
                          timeout=JS_TIMEOUT_SECONDS, check=False)
    if proc.returncode != 0:
        raise ValueError(f"{relpath}: the JavaScript parser rejected the file: {proc.stderr.strip()}")
    sizes: dict[str, tuple[int, int]] = {}
    for entry in json.loads(proc.stdout):
        _record(sizes, entry["name"], entry["startLine"], entry["endLine"])
    return sizes


def _js_start(line: str) -> tuple[str, str] | None:
    """``(name, indent)`` when ``line`` opens a JavaScript function (T715 line measurer), else None."""
    for pattern in _JS_STARTS:
        match = pattern.match(line)
        if match and match.group("name") not in _JS_NOT_METHODS:
            return match.group("name"), match.group("indent")
    return None


def _line_js_sizes(text: str) -> dict[str, tuple[int, int]]:
    """The T715 line-based JavaScript measurer, kept only as the baseline of the residual fixtures."""
    return _braced_sizes(list(enumerate(text.splitlines(), start=1)), _js_start)


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
    if relpath.endswith(JS_SUFFIXES):
        return _js_sizes(relpath, text)
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


def split_js(relpaths) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """``(other files, JavaScript files)``, so the Python and Bash checks run without the parser."""
    js = tuple(p for p in relpaths if p.endswith(JS_SUFFIXES))
    return tuple(p for p in relpaths if p not in js), js


def tracked_javascript(root: Path) -> tuple[str, ...]:
    """Every git-tracked ``.mjs``, ``.js`` and ``.cjs`` file (``tests/golden/`` is never read)."""
    argv = ["git", "-C", str(root), "ls-files", "-z", "--", *(f"*{suffix}" for suffix in JS_SUFFIXES)]
    out = subprocess.run(argv, capture_output=True, check=True, timeout=JS_TIMEOUT_SECONDS).stdout
    names = (name.decode("utf-8") for name in out.split(b"\0") if name)
    return tuple(sorted(name for name in names if not name.startswith("tests/golden/")))


def _problems_message(problems: list[str]) -> str:
    return "functions over the 50-line standard:\n" + "\n".join(problems)


class TestFunctionSize(unittest.TestCase):
    def test_shipped_tooling_functions_within_limit(self):
        other, js = split_js(SHIPPED_TOOLING)
        problems = oversized(repo_root(), relpaths=other)
        self.assertEqual(problems, [], _problems_message(problems))
        require_js_parser(self)
        problems = oversized(repo_root(), relpaths=js)
        self.assertEqual(problems, [], _problems_message(problems))

    def test_every_tracked_javascript_file_within_limit(self):
        require_js_parser(self)
        files = tracked_javascript(repo_root())
        self.assertIn("implementation/scripts/sync.mjs", files)
        self.assertIn(JS_MEASURER, files)
        problems = oversized(repo_root(), relpaths=files)
        self.assertEqual(problems, [], _problems_message(problems))

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
        other, js = split_js(SHIPPED_TOOLING)
        for index, relpath in enumerate(other + js):
            if index == len(other):
                require_js_parser(self)
            sizes = measure_text(relpath, (root / relpath).read_text(encoding="utf-8"))
            self.assertGreater(len(sizes), 3, f"{relpath}: the measurer found almost no functions")

    def test_mutation_oversized_function_is_detected(self):
        """A copy of each file type with one oversized function must fail (JavaScript last: it may skip)."""
        body = "\n".join(f"    x{i} = {i}" for i in range(60))
        samples = {
            "sample.py": f"def big():\n{body}\n    return 1\n",
            "sample.sh": "big() {\n" + "\n".join(f"  x{i}={i}" for i in range(60)) + "\n}\n",
            "sample.mjs": "function big() {\n" + "\n".join(f"  const x{i} = {i};" for i in range(60)) + "\n}\n",
        }
        allowed = {(relpath, "big"): "x" for relpath in samples}
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for relpath, text in samples.items():
                (root / relpath).write_text(text, encoding="utf-8")
                if relpath.endswith(JS_SUFFIXES):
                    require_js_parser(self)
                self.assertEqual(len(oversized(root, relpaths=(relpath,), allowlist={})), 1, relpath)
                self.assertEqual(oversized(root, relpaths=(relpath,), allowlist=allowed), [], relpath)

    def test_boundary_exactly_50_lines_passes(self):
        text = "def ok():\n" + "\n".join(f"    x{i} = {i}" for i in range(49)) + "\n"
        self.assertEqual(_python_sizes(text)["ok"][1], 50)
        text += "    y = 1\n"
        self.assertEqual(_python_sizes(text)["ok"][1], 51)


class TestJsParserAvailability(unittest.TestCase):
    """T732: a missing parser fails under CI and skips locally with its reason; nothing is silent."""

    def test_missing_parser_fails_under_ci(self):
        with mock.patch(f"{__name__}.js_parser_missing", return_value="node is not on PATH"), \
                mock.patch.dict(os.environ, {"CI": "true"}):
            with self.assertRaisesRegex(self.failureException, "missing under CI: node is not on PATH"):
                require_js_parser(self)

    def test_missing_parser_skips_locally_with_the_reason(self):
        with mock.patch(f"{__name__}.js_parser_missing", return_value="acorn 8.19.0 is not installed"), \
                mock.patch.dict(os.environ):
            os.environ.pop("CI", None)
            with self.assertRaisesRegex(unittest.SkipTest, r"local skip; CI fails\): acorn 8\.19\.0 is not"):
                require_js_parser(self)

    def test_measuring_javascript_without_the_parser_raises(self):
        with mock.patch(f"{__name__}.js_parser_missing", return_value="node is not on PATH"):
            with self.assertRaisesRegex(JsParserUnavailable, "node is not on PATH"):
                measure_text("s.mjs", "function f() {}\n")

    def test_reasons_name_the_install_command_and_a_version_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp, mock.patch(f"{__name__}.shutil.which", return_value="/bin/node"):
            base = Path(tmp) / JS_DIR
            base.mkdir(parents=True)
            (base / "package.json").write_text('{"dependencies": {"acorn": "8.19.0"}}', encoding="utf-8")
            self.assertIn(JS_INSTALL, js_parser_missing(Path(tmp)))
            (base / "node_modules" / "acorn").mkdir(parents=True)
            (base / "node_modules" / "acorn" / "package.json").write_text('{"version": "8.18.0"}', encoding="utf-8")
            self.assertIn("8.18.0 is installed but ci/js/package.json pins 8.19.0", js_parser_missing(Path(tmp)))
        with mock.patch(f"{__name__}.shutil.which", return_value=None):
            self.assertEqual(js_parser_missing(), "node is not on PATH")


class TestJsParserSupplyChain(unittest.TestCase):
    """T732: acorn is pinned exactly, integrity-locked, has no dependencies and installs without scripts."""

    def setUp(self):
        self.base = repo_root() / JS_DIR
        self.package = json.loads((self.base / "package.json").read_text(encoding="utf-8"))
        self.lock = json.loads((self.base / "package-lock.json").read_text(encoding="utf-8"))

    def test_package_json_is_private_and_pins_one_exact_version(self):
        self.assertIs(self.package.get("private"), True)
        self.assertEqual(list(self.package["dependencies"]), ["acorn"])
        self.assertRegex(self.package["dependencies"]["acorn"], r"^\d+\.\d+\.\d+$")
        for key in ("devDependencies", "optionalDependencies", "peerDependencies", "scripts"):
            self.assertNotIn(key, self.package)

    def test_lockfile_carries_integrity_hashes_and_matches_the_pin(self):
        self.assertEqual(self.lock.get("lockfileVersion"), 3)
        packages = self.lock["packages"]
        self.assertEqual(sorted(packages), ["", "node_modules/acorn"], "a new dependency needs a review")
        acorn = packages["node_modules/acorn"]
        self.assertEqual(acorn["version"], self.package["dependencies"]["acorn"])
        self.assertRegex(acorn["integrity"], r"^sha512-[A-Za-z0-9+/]{86}==$")
        self.assertEqual(acorn["resolved"], f"https://registry.npmjs.org/acorn/-/acorn-{acorn['version']}.tgz")
        self.assertFalse(acorn.get("hasInstallScript", False))

    def test_ci_installs_the_parser_with_ignore_scripts_before_the_suite(self):
        ci = (repo_root() / ".gitlab-ci.yml").read_text(encoding="utf-8")
        job = re.search(r"^unit-tests:\n(?:[ \t].*\n|\n)+", ci, re.M).group(0)
        self.assertIn(f"    - {JS_INSTALL} --no-audit --no-fund\n", job)
        self.assertLess(job.index(JS_INSTALL), job.index("python3 tests/run.py"))
        for line in ci.splitlines():
            if re.search(r"\bnpm\s+(?:ci|install|i)\b", line) and not line.lstrip().startswith("#"):
                self.assertIn("--ignore-scripts", line, line)

    def test_node_modules_is_ignored(self):
        ignored = (repo_root() / ".gitignore").read_text(encoding="utf-8").splitlines()
        self.assertIn("node_modules/", ignored)


def _body(prefix: str, count: int = 60) -> str:
    return "\n".join(f"{prefix}x{i}={i}" for i in range(count))


class TestMeasuredShapes(unittest.TestCase):
    """T715 (SEC-T677-01): each Bash shape the old column-0 measurer missed is now measured."""

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

    def test_a_redefined_name_does_not_hide_the_earlier_body(self):
        samples = {
            "s.py": f"def big():\n{_body('    ')}\n    return 1\n\n\ndef big():\n    return 2\n",
            "s.sh": f"big() {{\n{_body('  ')}\n}}\nbig() {{\n  :\n}}\n",
        }
        for relpath, text in samples.items():
            with self.subTest(relpath=relpath):
                sizes = measure_text(relpath, text)
                self.assertGreater(sizes["big"][1], MAX_LINES, sizes)
                self.assertEqual(len([k for k in sizes if k.split("@")[0] == "big"]), 2, sizes)
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "s.py").write_text(samples["s.py"], encoding="utf-8")
            self.assertEqual(len(oversized(Path(tmp), relpaths=("s.py",), allowlist={})), 1)

    def test_an_unclosed_bash_function_fails_closed(self):
        for text in ("big() {\n  :\n", "big() {\n  cat <<EOF\n}\n"):
            with self.subTest(text=text):
                with self.assertRaisesRegex(ValueError, "big opened at line 1 is never closed"):
                    measure_text("s.sh", text)


_B = _body("    ")
# (source, name, start line, length): every function shape the parser must report.
JS_SHAPES = (
    (f"const big = (a, b) => {{\n{_B}\n}};\n", "big", 1, 62),
    (f"export const big = async x => {{\n{_B}\n}};\n", "big", 1, 62),
    (f"let big = function (a) {{\n{_B}\n}};\n", "big", 1, 62),
    (f"const o = {{\n  big: ({{ server }}) => {{\n{_B}\n  }},\n}};\n", "big", 2, 62),
    (f"const o = {{\n  *big() {{\n{_B}\n  }},\n}};\n", "big", 2, 62),
    (f"class A {{\n  async big(a, b) {{\n{_B}\n  }}\n}}\n", "big", 2, 62),
    (f"class A {{\n  static big() {{\n{_B}\n  }}\n}}\n", "big", 2, 62),
    (f"class A {{\n  static get big() {{\n{_B}\n  }}\n}}\n", "big", 2, 62),
    (f"class A {{\n  set big(v) {{\n{_B}\n  }}\n}}\n", "big", 2, 62),
    (f"class A {{\n  #big() {{\n{_B}\n  }}\n}}\n", "#big", 2, 62),
    (f"export default async function* big(a) {{\n{_B}\n}}\n", "big", 1, 62),
)


class TestJavaScriptShapes(unittest.TestCase):
    """T732: the acorn measurer reports every JavaScript function shape with its exact span."""

    def setUp(self):
        require_js_parser(self)

    def test_javascript_shapes(self):
        for text, name, start, length in JS_SHAPES:
            with self.subTest(text=text.splitlines()[:2]):
                self.assertEqual(measure_text("s.mjs", text).get(name), (start, length))

    def test_javascript_nested_function_is_measured_on_its_own(self):
        text = "function outer() {\n  function big() {\n" + _body("    ") + "\n  }\n  return big;\n}\n"
        sizes = measure_text("s.mjs", text)
        self.assertEqual(sizes["big"], (2, 62))
        self.assertEqual(sizes["outer"], (1, 65))

    def test_control_flow_is_not_a_function_and_one_liners_are_one_line(self):
        text = ("function f(x) {\n  if (x) {\n    g();\n  }\n  for (const y of x) {\n  }\n}\n"
                "const id = (v) => { return v; };\nfunction g() { return 1; }\n"
                "const t = `function fake() {\n}`;\n")
        self.assertEqual(measure_text("s.mjs", text), {"f": (1, 7), "id": (8, 1), "g": (9, 1)})

    def test_a_redefined_name_does_not_hide_the_earlier_body(self):
        text = f"const a = {{\n  big() {{\n{_body('    ')}\n  }},\n}};\nconst b = {{ big() {{ return 1; }} }};\n"
        sizes = measure_text("s.mjs", text)
        self.assertEqual(sizes["big"], (2, 62))
        self.assertEqual(sizes["big@65"], (65, 1))

    def test_a_file_that_does_not_parse_fails_closed(self):
        for relpath, text in (("s.mjs", "function big() {\n  return 1;\n"), ("s.cjs", "export const x = 1;\n")):
            with self.subTest(relpath=relpath):
                where = re.escape(relpath)
                with self.assertRaisesRegex(ValueError, rf"^{where}: the JavaScript parser rejected the file: "
                                                        rf"{where}:\d+:\d+: "):
                    measure_text(relpath, text)

    def test_source_type_by_extension(self):
        script = "with (o) { var f = function () {}; }\n"  # `with` is a syntax error in a module
        self.assertEqual(measure_text("s.js", script), {"f": (1, 1)})
        self.assertEqual(measure_text("s.cjs", "return function g() {};\n"), {"g": (1, 1)})
        with self.assertRaisesRegex(ValueError, "rejected"):
            measure_text("s.mjs", script)


def _array(count: int = 60) -> str:
    return "\n".join(f"    {i}," for i in range(count))


# (shape, source, name, start line, length): each residual of the T715 line measurer (module docstring).
RESIDUAL_SHAPES = (
    ("} inside a template literal", f"function big() {{\n  const t = `\n}}\n`;\n{_body('  ')}\n}}\n", "big", 1, 65),
    ("} inside a block comment", f"function big() {{\n  /*\n}}\n  */\n{_body('  ')}\n}}\n", "big", 1, 65),
    ("class method with multi-line parameters",
     f"class A {{\n  big(\n    a,\n    b,\n  ) {{\n{_B}\n  }}\n}}\n", "big", 2, 65),
    ("object method with multi-line parameters",
     f"export const api = {{\n  async big(\n    a\n  ) {{\n{_B}\n  }},\n}};\n", "big", 2, 64),
    ("anonymous callback", f"[1, 2].forEach((item) => {{\n{_body('  ')}\n}});\n", "(anonymous)", 1, 62),
    ("immediately invoked function", f"(function () {{\n{_body('  ')}\n}})();\n", "(anonymous)", 1, 62),
    ("anonymous default export", f"export default function () {{\n{_body('  ')}\n}}\n", "default", 1, 62),
    ("expression-bodied arrow", f"export const big = () =>\n  [\n{_array()}\n  ];\n", "big", 1, 63),
    ("class-field arrow", f"class A {{\n  big = () => {{\n{_B}\n  }};\n}}\n", "big", 2, 62),
    ("member assignment", f"module.exports.big = function (a) {{\n{_body('  ')}\n}};\n", "big", 1, 62),
    ("binding head on its own line", f"const big =\n  function () {{\n{_B}\n  }};\n", "big", 2, 62),
    ("closing brace at another indentation", f"function big() {{\n{_body('  ')}\n  }}\n", "big", 1, 62),
)


def _line_measurer_result(text: str, name: str) -> tuple[int, int] | str | None:
    """What the T715 line measurer reports for ``name``: its span, None when absent, or its error."""
    try:
        return _line_js_sizes(text).get(name)
    except ValueError as error:
        return f"ValueError: {error}"


class TestParserClosesResiduals(unittest.TestCase):
    """T732 (SEC-T677-01): the old line measurer misses each residual shape; the parser measures it."""

    def setUp(self):
        require_js_parser(self)

    def test_each_residual_shape_is_missed_by_lines_and_measured_by_the_parser(self):
        for shape, text, name, start, length in RESIDUAL_SHAPES:
            with self.subTest(shape=shape):
                self.assertGreater(length, MAX_LINES)
                self.assertEqual(measure_text("s.mjs", text).get(name), (start, length))
                self.assertNotEqual(_line_measurer_result(text, name), (start, length))

    def test_each_residual_shape_fails_the_guard(self):
        with tempfile.TemporaryDirectory() as tmp:
            for index, (shape, text, name, start, length) in enumerate(RESIDUAL_SHAPES):
                relpath = f"r{index}.mjs"
                (Path(tmp) / relpath).write_text(text, encoding="utf-8")
                with self.subTest(shape=shape):
                    problems = oversized(Path(tmp), relpaths=(relpath,), allowlist={})
                    self.assertIn(f"{relpath}:{start} {name} is {length} lines (max {MAX_LINES})", problems)


if __name__ == "__main__":
    unittest.main()
