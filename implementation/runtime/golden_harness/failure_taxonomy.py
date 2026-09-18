"""Query API over the T415/T409 failure taxonomy (T501 Objective #1-2).

`docs/artifacts/failure-taxonomy-v1.md` defines a real, tested three-axis
`cause x behavior x mechanism` scheme and `docs/benchmarks/failures/**`
classifies 15 real failure records against it (9 golden-suite `known_failing`
cases, flat files directly under that directory; 6 Terminal-Bench failure
patterns, under its `terminal-bench/` subdirectory -- see that directory's own
`README.md` for the two source-specific index tables). Until this module,
that classification existed only as human-readable Markdown -- nothing in
this repo could query "give me every record with `cause: X`" programmatically.
This module makes it a queryable library import: nothing more.

## Parsing approach (documented per this task's own brief, `task-T501.md`
## Objective #1's "document which you chose and why")

Each of the 15 `.md` files is parsed **directly**, not `README.md`'s index
tables. `README.md` is a derived summary of the same 15 files (its own text
says so: "Scheme definition ... see `docs/artifacts/failure-taxonomy-v1.md`");
parsing the per-case files directly means this module's output can never
silently drift from the authoritative source `failure-taxonomy-v1.md` and the
per-case files themselves were built against, even if a future edit to
`README.md` fell out of sync with them. Every per-case file (both the 9
golden-suite files and the 6 Terminal-Bench pattern files, confirmed by direct
read before writing this module) carries the same one structural element this
parser depends on: an "Axis classification" Markdown table with rows shaped
```
| `cause` | `<value>` |
```
(golden-suite files: exactly two columns; Terminal-Bench files: a third
`Status` column noting whether the value is new/reused -- this parser only
reads the second column, so the extra column is transparent to it). Golden
suite files additionally carry a `` `known_failing_category` (T410 axis): `` line;
Terminal-Bench pattern files do not (T410's `tracked_defect`/`capability_gap`
split is a golden-suite-only concept, see `failure-taxonomy-v1.md` SS2) so
`known_failing_category` is `None` for Terminal-Bench records.

The test suite (`tests/functional/test_golden_harness_failure_taxonomy.py`)
cross-checks a sample of this module's parsed output against `README.md`'s own
index-table values as an independent consistency check, without making the
module itself depend on `README.md`'s structure.

## Explicit scope boundary -- read this before extending this module

This module makes the **15 currently-committed, already-classified** failure
records queryable. It deliberately does **not** build any mechanism for a
future golden-suite run or Terminal-Bench delta harness invocation (T417-T419)
to add new failures to, or re-classify existing ones within, this taxonomy
over time -- see `task-T501.md`'s "A disclosed scoping decision, not an
oversight" section for the full reasoning. That is a separate, not-yet-scoped
future increment. The intended future consumer of this module is a
not-yet-built diff-proposal generator / weakness-clustering agent
(`plan-055`'s `T462-equiv`, `@meta-improver`) -- this module does not build
any part of that either; it stops at "the taxonomy is a queryable library
import."
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

SOURCE_GOLDEN_SUITE = "golden-suite"
SOURCE_TERMINAL_BENCH = "terminal-bench"
ALLOWED_SOURCES = frozenset({SOURCE_GOLDEN_SUITE, SOURCE_TERMINAL_BENCH})

_AXIS_NAMES = ("cause", "behavior", "mechanism")
_AXIS_ROW_RE = re.compile(
    r"^\|\s*`(cause|behavior|mechanism)`\s*\|\s*`([^`]+)`\s*\|", re.MULTILINE
)
_KNOWN_FAILING_CATEGORY_RE = re.compile(
    r"`known_failing_category`[^\n`]*:\*\*\s*`([^`]+)`"
)
_TITLE_RE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)


@dataclass(frozen=True)
class FailureRecord:
    """One classified failure record (one `docs/benchmarks/failures/**` file).

    `case_id` is the file's stem (e.g. `code-review-conditional-pass-
    conditions-gap` for the golden-suite file of that name, or
    `incorrect-computed-output-value` for the Terminal-Bench pattern file) --
    unique across both sources, since no golden-suite file and Terminal-Bench
    pattern file currently share a stem (checked by `FailureTaxonomy.load`,
    which raises if a future addition ever collides).
    """

    case_id: str
    source: str
    title: str
    relative_path: str
    cause: str
    behavior: str
    mechanism: str
    known_failing_category: str | None = None
    is_held_out: bool = False

    def axes(self) -> tuple[str, str, str]:
        """The `(cause, behavior, mechanism)` triple, in scheme order."""
        return (self.cause, self.behavior, self.mechanism)


def _parse_record(path: Path, *, source: str, relative_to: Path) -> FailureRecord:
    text = path.read_text(encoding="utf-8")

    axes: dict[str, str] = {}
    for axis_name, value in _AXIS_ROW_RE.findall(text):
        axes.setdefault(axis_name, value)
    missing = [name for name in _AXIS_NAMES if name not in axes]
    if missing:
        raise ValueError(
            f"{path}: missing required axis classification row(s) {missing}"
        )

    title_match = _TITLE_RE.search(text)
    title = title_match.group(1) if title_match else path.stem

    kfc_match = _KNOWN_FAILING_CATEGORY_RE.search(text)
    known_failing_category = kfc_match.group(1) if kfc_match else None

    case_id = path.stem
    return FailureRecord(
        case_id=case_id,
        source=source,
        title=title,
        relative_path=path.relative_to(relative_to).as_posix(),
        cause=axes["cause"],
        behavior=axes["behavior"],
        mechanism=axes["mechanism"],
        known_failing_category=known_failing_category,
        is_held_out=case_id.startswith("held-out-case-"),
    )


class FailureTaxonomy:
    """In-memory, queryable view over the parsed failure records.

    Immutable once built (`load()`/`__init__` are the only ways to populate
    it) -- consumers get a query API, not a way to mutate the underlying
    classification."""

    def __init__(self, records: list[FailureRecord]) -> None:
        self._records: tuple[FailureRecord, ...] = tuple(records)
        by_id: dict[str, FailureRecord] = {}
        for record in self._records:
            if record.case_id in by_id:
                raise ValueError(f"duplicate case_id across sources: {record.case_id!r}")
            by_id[record.case_id] = record
        self._by_id = by_id

    @classmethod
    def load(cls, failures_dir: Path) -> "FailureTaxonomy":
        """Parse every classified failure record under `failures_dir`
        (caller-supplied, mirroring `scoring.find_golden_case_dir`'s
        `golden_root` parameter -- this module never hardcodes a repo-root
        path itself). Expects the real `docs/benchmarks/failures/` layout:
        golden-suite files directly in `failures_dir` (`README.md` excluded),
        Terminal-Bench pattern files under `failures_dir / "terminal-bench"`.
        """
        golden_files = sorted(
            p for p in failures_dir.glob("*.md") if p.name != "README.md"
        )
        terminal_bench_dir = failures_dir / "terminal-bench"
        terminal_bench_files = (
            sorted(terminal_bench_dir.glob("*.md"))
            if terminal_bench_dir.is_dir()
            else []
        )

        records = [
            _parse_record(p, source=SOURCE_GOLDEN_SUITE, relative_to=failures_dir)
            for p in golden_files
        ]
        records += [
            _parse_record(p, source=SOURCE_TERMINAL_BENCH, relative_to=failures_dir)
            for p in terminal_bench_files
        ]
        return cls(records)

    def all_records(self) -> tuple[FailureRecord, ...]:
        """Every classified failure record, golden-suite and Terminal-Bench
        combined, in the order they were loaded (golden-suite files first,
        alphabetically, then Terminal-Bench pattern files, alphabetically)."""
        return self._records

    def get(self, case_id: str) -> FailureRecord:
        """The full record for a given case/file id. Raises `LookupError` if
        no record with that id exists (never returns `None` silently)."""
        try:
            return self._by_id[case_id]
        except KeyError:
            raise LookupError(f"no failure record with case_id={case_id!r}") from None

    def filter_by(
        self,
        *,
        cause: str | None = None,
        behavior: str | None = None,
        mechanism: str | None = None,
        source: str | None = None,
    ) -> tuple[FailureRecord, ...]:
        """Records matching every given (non-`None`) filter, AND-combined.
        Calling with no filters returns every record (same as `all_records()`).
        """
        results: tuple[FailureRecord, ...] = self._records
        if cause is not None:
            results = tuple(r for r in results if r.cause == cause)
        if behavior is not None:
            results = tuple(r for r in results if r.behavior == behavior)
        if mechanism is not None:
            results = tuple(r for r in results if r.mechanism == mechanism)
        if source is not None:
            results = tuple(r for r in results if r.source == source)
        return results

    def __len__(self) -> int:
        return len(self._records)
