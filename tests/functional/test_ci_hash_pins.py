"""T676 (SEC-T675-09, SEC-T675-03, SEC-T646-04, SEC-014) -- hash-locked Python packages and supported CI images.

Four contracts, each with a mutation proof (the guard's input is damaged in memory and the checker must
then report an error):

  1. every `pip install` in .gitlab-ci.yml is `--require-hashes -r ci/requirements-*.txt`, with no extra
     package, index, find-links or editable argument (the unit-tests job binds the host Docker socket);
  2. every lock file (`ci/*.txt`, `implementation/runtime/*/requirements-mcp-server.lock.txt`) pins every
     entry to `==` with at least one sha256 hash, holds every direct requirement of its input file at a
     version the input allows, and the two runtime locks are identical;
  3. `httpx2` is at least 2.12.0 (GHSA-8xx6-hgc6-gc2m) in both runtime requirement files and every lock;
  4. no CI image is end of life (Node <= 20 or an odd Node major, Alpine <= 3.21, Python <= 3.9; table dated
     2026-10-22), and every image still carries its sha256 digest.
"""
from __future__ import annotations

import datetime as dt
import re
import shlex
import unittest

import yaml

from tests._helpers.repo import repo_root

ROOT = repo_root()
CI_YML = ROOT / ".gitlab-ci.yml"
LOCKS = {
    "ci/requirements-ci.txt": "ci/requirements-ci.in",
    "ci/requirements-gate.txt": "ci/requirements-gate.in",
    "implementation/runtime/security/requirements-mcp-server.lock.txt":
        "implementation/runtime/security/requirements-mcp-server.txt",
    "implementation/runtime/memory/requirements-mcp-server.lock.txt":
        "implementation/runtime/memory/requirements-mcp-server.txt",
}
HTTPX2_FLOOR = (2, 12, 0)
ENTRY = re.compile(r"^(?P<name>[A-Za-z0-9][A-Za-z0-9._-]*)==(?P<version>[0-9][0-9A-Za-z.!+_-]*)(?P<marker>\s*;[^\\]*)?\s*\\?$")
HASH = re.compile(r"^\s+--hash=sha256:[0-9a-f]{64}\s*\\?$")
INPUT_REQ = re.compile(r"^(?P<name>[A-Za-z0-9][A-Za-z0-9._-]*)\s*(?P<op>==|>=)?\s*(?P<version>[0-9][0-9A-Za-z.]*)?\s*$")
FORBIDDEN_PIP_FLAGS = ("-i", "--index-url", "--extra-index-url", "-f", "--find-links", "--trusted-host",
                       "-e", "--editable", "--no-deps", "--pre", "--no-index", "--break-system-packages")


def norm(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def version_tuple(version: str) -> tuple[int, ...]:
    return tuple(int(part) for part in re.findall(r"\d+", version.split("+")[0])[:4])


# ---- 1. the CI file ------------------------------------------------------------------------------------

def ci_command_lines(ci_text: str) -> list[str]:
    """Every command line of every script, before_script and after_script block (and `default`)."""
    document = yaml.safe_load(ci_text)
    lines: list[str] = []

    def walk(node: object) -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                if key in ("script", "before_script", "after_script") and isinstance(value, list):
                    for item in value:
                        lines.extend(str(item).splitlines())
                else:
                    walk(value)

    walk(document)
    return [ln.strip() for ln in lines if ln.strip()]


def pip_install_problems(ci_text: str, root=ROOT) -> list[str]:
    """Problems with every pip/uv install invocation in the pipeline; an empty list means all are locked."""
    problems, seen = [], 0
    for line in ci_command_lines(ci_text):
        if not re.search(r"\b(pip3?|uv|pipx)\b\s+(?:\S+\s+)*?(install|sync|add)\b|-m\s+pip\b|\bpip3?\s+download\b", line):
            continue
        if re.match(r"^(#|echo\b)", line):
            continue
        seen += 1
        try:
            tokens = shlex.split(line)
        except ValueError:
            problems.append(f"unparseable pip line: {line!r}")
            continue
        problems.extend(pip_tokens_problems(tokens, line, root))
    if not seen:
        problems.append("no pip install found: the parser would pass a pipeline with none")
    return problems


def pip_tokens_problems(tokens: list[str], line: str, root) -> list[str]:
    if "install" not in tokens or tokens[:1] in (["uv"], ["pipx"]):
        return [f"not a plain `pip install` (uv, pipx and other forms are refused): {line!r}"]
    args = tokens[tokens.index("install") + 1:]
    out = []
    if "--require-hashes" not in args:
        out.append(f"missing --require-hashes: {line!r}")
    if "--only-binary=:all:" not in args:  # SEC-T676-08: an sdist would run its build backend inside the job
        out.append(f"missing --only-binary=:all: (no source builds): {line!r}")
    out.extend(f"forbidden pip flag {a!r}: {line!r}" for a in args if a.split("=")[0] in FORBIDDEN_PIP_FLAGS)
    files = [args[i + 1] for i, a in enumerate(args[:-1]) if a == "-r"]
    if len(files) != 1:
        out.append(f"exactly one `-r ci/requirements-*.txt` is required: {line!r}")
    positional = [a for i, a in enumerate(args) if not a.startswith("-") and (i == 0 or args[i - 1] != "-r")]
    if positional:
        out.append(f"package or path argument outside the lock: {positional!r} in {line!r}")
    for file in files:
        if not re.fullmatch(r"ci/requirements-[a-z]+\.txt", file) or not (root / file).is_file():
            out.append(f"{file!r} is not an existing ci/requirements-*.txt: {line!r}")
    return out


# ---- 2. the lock files ---------------------------------------------------------------------------------

def parse_lock(text: str) -> tuple[dict[str, list[str]], list[str]]:
    """({normalized name: [versions]}, problems). Every entry needs `==` and at least one sha256 hash."""
    entries: dict[str, list[str]] = {}
    problems: list[str] = []
    current: str | None = None
    hashes = 0
    for number, line in enumerate(text.splitlines(), 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if HASH.match(line):
            hashes += 1
            continue
        match = ENTRY.match(line)
        if current is not None and hashes == 0:
            problems.append(f"line {number}: {current} has no sha256 hash")
        if not match:
            problems.append(f"line {number}: not an exact `name==version` entry: {line.strip()!r}")
            current, hashes = None, 0
            continue
        current, hashes = match["name"], 0
        entries.setdefault(norm(match["name"]), []).append(match["version"])
    if current is not None and hashes == 0:
        problems.append(f"{current} has no sha256 hash")
    if not entries:
        problems.append("lock has no entries")
    return entries, problems


def input_requirements(text: str) -> dict[str, tuple[str | None, str | None]]:
    found = {}
    for line in text.splitlines():
        line = line.split("#", 1)[0].strip()
        if not line:
            continue
        match = INPUT_REQ.match(line)
        if not match:
            raise AssertionError(f"input line not understood by the test (extend it): {line!r}")
        found[norm(match["name"])] = (match["op"], match["version"])
    return found


def lock_problems(lock_text: str, input_text: str) -> list[str]:
    entries, problems = parse_lock(lock_text)
    for name, (op, wanted) in input_requirements(input_text).items():
        versions = entries.get(name)
        if not versions:
            problems.append(f"{name} is required by the input file but absent from the lock")
        elif op == "==" and wanted not in versions:
            problems.append(f"{name}=={wanted} required, locked {versions}")
        elif op == ">=" and any(version_tuple(v) < version_tuple(wanted) for v in versions):
            problems.append(f"{name}>={wanted} required, locked {versions}")
    return problems


# ---- 4. images -----------------------------------------------------------------------------------------

def eol_image_problems(ci_text: str) -> list[str]:
    """Images that are end of life on 2026-10-22: Node <= 20 or odd majors, Alpine <= 3.21, Python <= 3.9."""
    problems = []
    for image in re.findall(r"^\s*image:\s*(\S+)\s*$", ci_text, re.M):
        name, _, rest = image.partition(":")
        tag = rest.split("@")[0]
        if "@sha256:" not in image:
            problems.append(f"{image}: no digest")
        if name == "node":
            major = int(re.match(r"\d+", tag).group(0))
            if major <= 20 or major % 2:
                problems.append(f"{image}: Node {major} is end of life or not an LTS line")
        elif name == "alpine" and version_tuple(tag)[:2] <= (3, 21):
            problems.append(f"{image}: Alpine {tag} is end of life")
        elif name == "python" and version_tuple(tag)[:2] <= (3, 9):
            problems.append(f"{image}: Python {tag} is end of life")
    return problems


class TestCiPipInstallsAreHashLocked(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ci = CI_YML.read_text(encoding="utf-8")

    def test_every_pip_install_is_hash_locked(self):
        self.assertEqual(pip_install_problems(self.ci), [])

    def test_the_two_install_lines_use_their_own_locks(self):
        self.assertIn("-r ci/requirements-ci.txt", self.ci)
        self.assertIn("-r ci/requirements-gate.txt", self.ci)
        self.assertNotIn("pip install --no-cache-dir pyyaml", self.ci)

    def test_mutation_a_floating_package_is_detected(self):
        bad = self.ci.replace("--require-hashes --only-binary=:all: -r ci/requirements-gate.txt", "--only-binary=:all: pyyaml jsonschema")
        self.assertTrue(any("require-hashes" in p for p in pip_install_problems(bad)))

    def test_mutation_dropping_require_hashes_is_detected(self):
        bad = self.ci.replace("--require-hashes --only-binary=:all: -r ci/requirements-ci.txt", "--only-binary=:all: -r ci/requirements-ci.txt")
        self.assertTrue(any("missing --require-hashes" in p for p in pip_install_problems(bad)))

    def test_mutation_dropping_only_binary_is_detected(self):
        bad = self.ci.replace(" --only-binary=:all:", "", 1)
        self.assertNotEqual(bad, self.ci)
        self.assertTrue(any("--only-binary" in p for p in pip_install_problems(bad)))
        self.assertEqual(self.ci.count("--only-binary=:all:"), 2)  # both install lines carry it

    def test_mutation_an_extra_package_beside_the_lock_is_detected(self):
        bad = self.ci.replace("-r ci/requirements-ci.txt", "-r ci/requirements-ci.txt requests")
        self.assertTrue(any("outside the lock" in p for p in pip_install_problems(bad)))

    def test_mutation_an_extra_index_and_a_missing_lock_file_are_detected(self):
        bad = self.ci.replace("--require-hashes --only-binary=:all: -r ci/requirements-ci.txt",
                              "--require-hashes --only-binary=:all: --extra-index-url https://x.example -r ci/requirements-ci.txt")
        self.assertTrue(any("forbidden pip flag" in p for p in pip_install_problems(bad)))
        bad = self.ci.replace("ci/requirements-gate.txt", "ci/requirements-nope.txt")
        self.assertTrue(any("not an existing" in p for p in pip_install_problems(bad)))

    def test_mutation_an_added_unlocked_install_line_is_detected(self):
        bad = self.ci.replace("  script:\n    - python3 tests/run.py", "  script:\n    - pip install requests\n    - python3 tests/run.py")
        self.assertNotEqual(bad, self.ci)
        self.assertTrue(pip_install_problems(bad))

    def test_uv_and_pipx_installs_are_refused(self):
        for line in ("uv pip install requests", "pipx install pyyaml"):
            bad = self.ci.replace("  script:\n    - python3 tests/run.py", f"  script:\n    - {line}\n    - python3 tests/run.py")
            self.assertTrue(pip_install_problems(bad), line)

    def test_a_pipeline_without_any_pip_install_is_not_a_pass(self):
        self.assertTrue(pip_install_problems("job:\n  script:\n    - echo hi\n"))


class TestLockFiles(unittest.TestCase):
    def read(self, rel: str) -> str:
        return (ROOT / rel).read_text(encoding="utf-8")

    def test_every_lock_is_complete_and_matches_its_input(self):
        for lock, source in LOCKS.items():
            with self.subTest(lock=lock):
                self.assertEqual(lock_problems(self.read(lock), self.read(source)), [])

    def test_every_lock_documents_its_regeneration_command(self):
        for lock, source in LOCKS.items():
            with self.subTest(lock=lock):
                header = "\n".join(self.read(lock).splitlines()[:3])
                self.assertIn("--generate-hashes", header)
                self.assertIn(source.rsplit("/", 1)[-1], header)

    def test_the_two_runtime_locks_are_identical_and_hold_the_sdk_pin(self):
        security = self.read("implementation/runtime/security/requirements-mcp-server.lock.txt")
        self.assertEqual(security, self.read("implementation/runtime/memory/requirements-mcp-server.lock.txt"))
        pin = re.search(r"^mcp==(\S+)$", self.read("implementation/runtime/security/requirements-mcp-server.txt"), re.M)
        self.assertIn(pin.group(1), parse_lock(security)[0]["mcp"])

    def test_httpx2_is_at_least_the_patched_floor_everywhere(self):
        for rel in ("implementation/runtime/security/requirements-mcp-server.txt",
                    "implementation/runtime/memory/requirements-mcp-server.txt"):
            self.assertRegex(self.read(rel), r"(?m)^httpx2>=2\.12\.0$", rel)
        for lock in LOCKS:
            entries, _ = parse_lock(self.read(lock))
            for version in entries.get("httpx2", []):
                with self.subTest(lock=lock, version=version):
                    self.assertGreaterEqual(version_tuple(version), HTTPX2_FLOOR)

    def test_the_ci_lock_holds_every_package_the_job_used_to_install(self):
        entries, _ = parse_lock(self.read("ci/requirements-ci.txt"))
        for name in ("pyyaml", "jsonschema", "requests", "pyarrow", "cryptography", "mcp"):
            self.assertIn(name, entries)
        self.assertGreaterEqual(version_tuple(entries["cryptography"][0]), (43, 0, 1))

    def test_mutation_an_entry_without_any_hash_is_detected(self):
        lock = self.read("ci/requirements-gate.txt")
        bad = re.sub(r"(?m)^(pyyaml==\S+) \\\n(?:    --hash=\S+(?: \\)?\n)+", r"\1\n", lock)
        self.assertNotEqual(bad, lock)
        problems = lock_problems(bad, self.read("ci/requirements-gate.in"))
        self.assertTrue(any("pyyaml has no sha256 hash" in p for p in problems), problems)

    def test_mutation_a_malformed_hash_is_detected(self):
        lock = self.read("ci/requirements-gate.txt")
        bad = re.sub(r"--hash=sha256:[0-9a-f]{64}", "--hash=sha256:abc", lock)
        self.assertTrue(lock_problems(bad, self.read("ci/requirements-gate.in")))

    def test_mutation_a_range_in_a_lock_is_detected(self):
        lock = self.read("ci/requirements-gate.txt")
        bad = re.sub(r"(?m)^pyyaml==", "pyyaml>=", lock, count=1)
        self.assertTrue(any("not an exact" in p for p in lock_problems(bad, self.read("ci/requirements-gate.in"))))

    def test_mutation_a_requirement_dropped_from_the_lock_is_detected(self):
        lock = self.read("ci/requirements-gate.txt")
        bad = re.sub(r"(?ms)^jsonschema==.*?(?=^\S)", "", lock, count=1)
        self.assertNotEqual(bad, lock)
        self.assertTrue(any("absent from the lock" in p for p in lock_problems(bad, self.read("ci/requirements-gate.in"))))

    def test_mutation_a_stale_lock_version_is_detected(self):
        lock = self.read("ci/requirements-ci.txt")
        bad = re.sub(r"(?m)^mcp==\S+", "mcp==2.1.0", lock, count=1)
        self.assertTrue(any("mcp==2.2.0 required" in p for p in lock_problems(bad, self.read("ci/requirements-ci.in"))))

    def test_mutation_an_unpatched_httpx2_floor_is_detected(self):
        lock = self.read("implementation/runtime/security/requirements-mcp-server.lock.txt")
        bad = re.sub(r"(?m)^httpx2==2\.1[46]\.0", "httpx2==2.5.0", lock)
        self.assertNotEqual(bad, lock)
        problems = lock_problems(bad, self.read("implementation/runtime/security/requirements-mcp-server.txt"))
        self.assertTrue(any("httpx2>=2.12.0 required" in p for p in problems))


EOL_TABLE_DATE = dt.date(2026, 10, 22)  # the day the table in eol_image_problems was written
MAX_REVIEW_AGE_DAYS = 120


def review_problems(ci_text: str, today: dt.date) -> list[str]:
    """The pipeline must say when its images were last reviewed, and that date must be recent and not before the table."""
    match = re.search(r"^# ci_images_reviewed_on: (\d{4}-\d{2}-\d{2})", ci_text, re.M)
    if not match:
        return ["no `# ci_images_reviewed_on: YYYY-MM-DD` line in .gitlab-ci.yml"]
    reviewed = dt.date.fromisoformat(match.group(1))
    out = []
    if (today - reviewed).days > MAX_REVIEW_AGE_DAYS:
        out.append(f"images last reviewed {reviewed}, more than {MAX_REVIEW_AGE_DAYS} days ago: re-check the digests and "
                   f"the end-of-life table in eol_image_problems, then update both dates")
    if reviewed < EOL_TABLE_DATE:
        out.append("ci_images_reviewed_on is older than the end-of-life table")
    if reviewed > today:
        out.append("ci_images_reviewed_on is in the future")
    return out


class TestCiImages(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ci = CI_YML.read_text(encoding="utf-8")

    def test_no_image_is_end_of_life_and_every_image_has_a_digest(self):
        self.assertEqual(eol_image_problems(self.ci), [])

    def test_the_review_date_is_present_and_fresh(self):
        self.assertEqual(review_problems(self.ci, dt.date.today()), [])

    def test_mutation_a_stale_missing_or_future_review_date_is_detected(self):
        reviewed = dt.date(2026, 10, 22)
        self.assertEqual(review_problems(self.ci, reviewed + dt.timedelta(days=120)), [])
        self.assertTrue(review_problems(self.ci, reviewed + dt.timedelta(days=121)))
        self.assertTrue(review_problems(self.ci.replace("ci_images_reviewed_on", "reviewed"), reviewed))
        self.assertTrue(review_problems(self.ci, reviewed - dt.timedelta(days=1)))
        self.assertTrue(review_problems(self.ci.replace("2026-10-22   (tests", "2026-01-01   (tests"), reviewed))

    def test_the_bases_are_the_two_supported_lines(self):
        names = {re.split(r"@", i)[0] for i in re.findall(r"^\s*image:\s*(\S+)\s*$", self.ci, re.M)}
        self.assertEqual(names, {"node:24-alpine", "python:3.12-alpine"})

    def test_mutation_the_old_images_are_detected(self):
        bad = self.ci.replace("node:24-alpine", "node:20-alpine")
        self.assertTrue(any("Node 20" in p for p in eol_image_problems(bad)))
        bad = self.ci.replace("python:3.12-alpine@", "alpine:3.20@", 1)
        self.assertTrue(any("Alpine 3.20" in p for p in eol_image_problems(bad)))
        bad = self.ci.replace("node:24-alpine", "node:23-alpine")
        self.assertTrue(any("Node 23" in p for p in eol_image_problems(bad)))

    def test_mutation_an_image_without_digest_is_detected(self):
        bad = re.sub(r"(image: node:24-alpine)@sha256:[0-9a-f]{64}", r"\1", self.ci)
        self.assertTrue(any("no digest" in p for p in eol_image_problems(bad)))


if __name__ == "__main__":
    unittest.main()
