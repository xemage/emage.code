"""Repo-wide static guard: `tests/golden/held-out/` must never be referenced from any
file outside itself (Refs T412; plan-035's risk table names this as the first of three
independent controls protecting held-out-set integrity for the rest of the roadmap --
T463's evaluator-hash check and T416's write-scope exclusion are the other two).

Mirrors the established repo-wide static-guard pattern in
`tests/functional/test_link_integrity.py` and
`tests/functional/test_check_version_consistency.py`: walk the repo, flag violations,
hard-fail with every violation listed, and prove both a clean-pass and a
violation-detected direction via temp-directory fixtures rather than only asserting the
real tree is currently clean.

## What "referenced" means here (the design decision this module encodes)

Two independent, narrowly-scoped checks:

- **Check A -- functional access.** Any `.py` file outside `tests/golden/held-out/`
  whose source text contains the literal path token `tests/golden/held-out` -- i.e. code
  that could import, `open()`, or `Path()`-construct its way into reading held-out
  content. Scoped to Python source only (T412 brief bullet 1: "Any Python
  import/open()/Path(...) string literal ..."). Deliberately a broad substring match
  rather than an AST-restricted one -- narrowing to exact `import`/`open`/`Path` call
  syntax would be trivially evadable (string concatenation, f-strings, `getattr`
  indirection) and the precedent guards this mirrors use similarly broad static
  detection, not full static analysis.
- **Check B -- specific held-out case-ID mention.** Any file outside `tests/golden/`
  *as a whole* (not merely outside `tests/golden/held-out/`) that mentions one of the
  held-out set's actual case IDs as a whole token. This catches doc/markdown references
  to specific held-out content (T412 brief bullet 2) without requiring a literal path
  string.

## Where the "outside tests/golden/held-out/" boundary is actually drawn, and why

The acceptance criterion says "never referenced from any file outside
`tests/golden/held-out/`." Applied completely literally, Check B would also flag
`tests/golden/open/*/brief.md` files that name a held-out sibling case ID in a "see
also"/provenance note -- and several real ones do, e.g.
`tests/golden/open/security-audit-verdict-fields-compliant/brief.md` names
`security-audit-owasp-matrix-compliant` (a held-out case) as a "distinct from" reference,
and `tests/golden/open/new-feature-plan-doc-compliant/brief.md` names
`new-feature-real-artifact-versioning-drift` (also held-out) as a sibling absence-of-
precedent case. These were authored at T411, before the open/held-out split existed, and
T412's own acceptance criterion 1 requires the move to be byte-identical -- editing this
content to scrub cross-references is out of scope and would silently redefine what T411's
authored cases said.

More importantly, these are not the leak this control exists to prevent. Per plan-035's
risk table, the threat is "held-out set leaks into improvement work" -- an
*improvement-task* file (an agent/skill/knowledge/script/doc file used to design or grade
an improvement to a command surface) reading or naming held-out content to game the
held-out evaluation. A golden case's own `brief.md` citing a sibling case by ID as design
precedent is the suite's internal bookkeeping, not an improvement-task file. So Check B is
scoped to "outside `tests/golden/` entirely" -- everything under `tests/golden/` (both
`open/` and `held-out/`) is exempt from the case-ID-mention check, while Check A's
functional-access check still applies inside `tests/golden/open/` (if a future case's
`expect.py` tried to actually import/open/Path-reference `held-out/`, that would still be
flagged -- only the bare-identifier-mention check is narrowed).

## Allowlist

- `scripts/scorecard.py` (T413, not yet built) is exempt from both checks -- running both
  `open/` and `held-out/` cases is its whole job (T412 brief "Coordination note").
  Allowlisted by path now so T413's author builds against this exemption rather than
  inventing a separate one.
- `tests/golden/README.md` and `tests/golden/_manifest-t411.md` are exempt -- they are the
  golden suite's own governance/bookkeeping surface, and T412's brief requires them to
  name the held-out split (case IDs + location + reasoning) explicitly.
- This file is exempt from its own scan -- it necessarily names all six held-out case IDs
  and the held-out path token in order to define and test the checks above.

## The chosen open/held-out split

Held out (6/20, 30%): `code-review-verdict-compliant`,
`code-review-real-verdict-format-drift`, `new-feature-real-artifact-versioning-drift`,
`plan-approval-marker-gap`, `prepare-release-verdict-compliant`,
`security-audit-owasp-matrix-compliant`. Spans all 5 command surfaces (2 `/code-review`,
1 each of the other 4 -- not concentrated in one surface), balanced 3 `expected_pass` /
3 `known_failing` (covering both `known_failing_category` values: `tracked_defect` and
`capability_gap`), and mixes real-artifact-grounded with hand-authored provenance. Full
reasoning: `tests/golden/_manifest-t411.md`'s "open/held-out split (T412)" section.
"""
from __future__ import annotations

import re
import tempfile
import unittest
from pathlib import Path

from tests._helpers.repo import repo_root

HELD_OUT_PATH_TOKEN = "tests/golden/held-out"

# Exempt from both checks -- see module docstring "Allowlist".
EXEMPT_RELATIVE_PATHS = frozenset({
    "scripts/scorecard.py",
    "tests/golden/README.md",
    "tests/golden/_manifest-t411.md",
    "tests/functional/test_golden_held_out_isolation.py",
})

# Directories never worth walking (mirrors test_link_integrity.py's SKIP_PARTS).
_SKIP_DIR_NAMES = {".git", "node_modules", "__pycache__", ".vscode-server"}


def _is_skipped_dir(parts: tuple[str, ...]) -> bool:
    if any(part in _SKIP_DIR_NAMES for part in parts):
        return True
    if parts and parts[0] == "archive":
        return True
    return False


def _held_out_case_ids(root: Path) -> list[str]:
    held_out_dir = root / "tests" / "golden" / "held-out"
    if not held_out_dir.is_dir():
        return []
    return sorted(p.name for p in held_out_dir.iterdir() if p.is_dir())


def _iter_candidate_files(root: Path):
    """Yield (path, rel) for every file under root except held-out/'s own content and
    the skipped noise directories."""
    held_out_dir = (root / "tests" / "golden" / "held-out").resolve()
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        try:
            rel = p.relative_to(root)
        except ValueError:
            continue
        if _is_skipped_dir(rel.parts):
            continue
        resolved = p.resolve()
        if resolved == held_out_dir or held_out_dir in resolved.parents:
            continue
        yield p, rel


def _read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return None


def _is_inside_golden_dir(rel: Path) -> bool:
    parts = rel.parts
    return len(parts) >= 2 and parts[0] == "tests" and parts[1] == "golden"


def find_violations(root: Path) -> list[tuple[str, str]]:
    """Scan `root` for references to `tests/golden/held-out/` from any file outside
    that directory, per the two checks documented in this module's docstring. Returns
    a list of (relative_posix_path, reason) violations. Pure / read-only: makes no
    writes and mutates nothing under `root`."""
    case_id_patterns = [
        (cid, re.compile(r"(?<![\w-])" + re.escape(cid) + r"(?![\w-])"))
        for cid in _held_out_case_ids(root)
    ]
    violations: list[tuple[str, str]] = []
    for path, rel in _iter_candidate_files(root):
        rel_posix = rel.as_posix()
        if rel_posix in EXEMPT_RELATIVE_PATHS:
            continue
        text = _read_text(path)
        if text is None:
            continue

        # Check A -- functional access from Python source, repo-wide (except held-out/
        # itself, already excluded by _iter_candidate_files).
        if path.suffix == ".py" and HELD_OUT_PATH_TOKEN in text:
            violations.append(
                (rel_posix, f"Python source references path '{HELD_OUT_PATH_TOKEN}'")
            )
            continue

        # Check B -- specific held-out case-ID mention, scoped to outside
        # tests/golden/ entirely (see docstring "Where the boundary is drawn").
        if _is_inside_golden_dir(rel):
            continue
        for cid, pattern in case_id_patterns:
            if pattern.search(text):
                violations.append((rel_posix, f"mentions held-out case ID '{cid}'"))
                break
    return violations


class TestFindViolationsSyntheticFixtures(unittest.TestCase):
    """Proves find_violations() both catches a real violation and passes on a clean
    tree, using temp-directory fixtures -- mirrors
    test_check_version_consistency.py's TestScanRepositoryFixtures pattern (not just
    asserting the real repo tree happens to be clean right now)."""

    @staticmethod
    def _make_repo(tmp: Path, case_ids: tuple[str, ...] = ("synthetic-held-case",)) -> None:
        held_out_dir = tmp / "tests" / "golden" / "held-out"
        for cid in case_ids:
            case_dir = held_out_dir / cid
            case_dir.mkdir(parents=True)
            (case_dir / "expect.py").write_text("def check(case_dir):\n    return True\n")
            (case_dir / "case.yaml").write_text(f"id: {cid}\nstatus: expected_pass\n")
            (case_dir / "brief.md").write_text(f"# {cid}\n")
        (tmp / "tests" / "golden" / "open").mkdir(parents=True, exist_ok=True)

    def test_clean_tree_has_no_violations(self):
        with tempfile.TemporaryDirectory() as tmp_s:
            tmp = Path(tmp_s)
            self._make_repo(tmp)
            (tmp / "scripts").mkdir()
            (tmp / "scripts" / "unrelated.py").write_text("print('hello')\n")
            (tmp / "docs").mkdir()
            (tmp / "docs" / "notes.md").write_text("Nothing to see here.\n")
            self.assertEqual(find_violations(tmp), [])

    def test_python_path_reference_outside_held_out_is_flagged(self):
        with tempfile.TemporaryDirectory() as tmp_s:
            tmp = Path(tmp_s)
            self._make_repo(tmp)
            (tmp / "scripts").mkdir()
            (tmp / "scripts" / "improve.py").write_text(
                "from pathlib import Path\n"
                "p = Path('tests/golden/held-out/synthetic-held-case/expect.py')\n"
            )
            violations = find_violations(tmp)
            self.assertEqual([v[0] for v in violations], ["scripts/improve.py"])
            self.assertIn(HELD_OUT_PATH_TOKEN, violations[0][1])

    def test_doc_mention_of_case_id_outside_golden_dir_is_flagged(self):
        with tempfile.TemporaryDirectory() as tmp_s:
            tmp = Path(tmp_s)
            self._make_repo(tmp)
            (tmp / "docs").mkdir()
            (tmp / "docs" / "improvement-notes.md").write_text(
                "Design inspired by the synthetic-held-case golden case.\n"
            )
            violations = find_violations(tmp)
            self.assertEqual([v[0] for v in violations], ["docs/improvement-notes.md"])
            self.assertIn("synthetic-held-case", violations[0][1])

    def test_case_id_mention_inside_open_dir_is_not_flagged(self):
        # Mirrors the real repo's pre-existing T411-authored sibling cross-references
        # inside tests/golden/open/*/brief.md -- internal suite bookkeeping, not an
        # improvement-task file reading held-out content. See docstring.
        with tempfile.TemporaryDirectory() as tmp_s:
            tmp = Path(tmp_s)
            self._make_repo(tmp)
            sibling = tmp / "tests" / "golden" / "open" / "sibling-case"
            sibling.mkdir(parents=True)
            (sibling / "brief.md").write_text(
                "See synthetic-held-case for related provenance notes.\n"
            )
            self.assertEqual(find_violations(tmp), [])

    def test_scorecard_py_is_exempt_even_when_referencing_held_out(self):
        with tempfile.TemporaryDirectory() as tmp_s:
            tmp = Path(tmp_s)
            self._make_repo(tmp)
            (tmp / "scripts").mkdir()
            (tmp / "scripts" / "scorecard.py").write_text(
                "import glob\n"
                "cases = glob.glob('tests/golden/**/expect.py', recursive=True)\n"
                "# also touches tests/golden/held-out/synthetic-held-case directly\n"
            )
            self.assertEqual(find_violations(tmp), [])

    def test_non_python_path_mention_of_generic_held_out_dir_is_not_flagged(self):
        # Mirrors docs/artifacts/golden-suite-format-v1.md and
        # docs/plans/plan-035-roadmap-v7-ground-up.md in the real repo: both describe
        # the *generic* tests/golden/held-out/ layout convention in prose without
        # naming any specific real case ID. That is architecture documentation, not a
        # leak, and Check A is intentionally Python-only so this doesn't false-trigger.
        with tempfile.TemporaryDirectory() as tmp_s:
            tmp = Path(tmp_s)
            self._make_repo(tmp)
            (tmp / "docs").mkdir()
            (tmp / "docs" / "format-spec.md").write_text(
                "Cases nest under tests/golden/held-out/<case-id>/ after the split.\n"
            )
            self.assertEqual(find_violations(tmp), [])


class TestRealRepoTreeIsClean(unittest.TestCase):
    """The guard actually executing against the real, current repo tree -- proves
    acceptance criterion 3's second direction (passes on the clean real tree) and
    criterion 5 (this test runs as part of tests/run.py, not skipped)."""

    def test_real_repo_has_no_held_out_violations(self):
        violations = find_violations(repo_root())
        self.assertEqual(
            violations,
            [],
            msg="held-out isolation violated:\n  "
            + "\n  ".join(f"{f}: {reason}" for f, reason in violations),
        )

    def test_held_out_dir_has_the_expected_six_cases(self):
        # Sanity check the scan target isn't accidentally empty -- a guard that
        # trivially passes because there's nothing to find would be worthless.
        self.assertEqual(
            _held_out_case_ids(repo_root()),
            [
                "code-review-real-verdict-format-drift",
                "code-review-verdict-compliant",
                "new-feature-real-artifact-versioning-drift",
                "plan-approval-marker-gap",
                "prepare-release-verdict-compliant",
                "security-audit-owasp-matrix-compliant",
            ],
        )


if __name__ == "__main__":
    unittest.main()
