#!/usr/bin/env python3
"""`scripts/scorecard.py` — golden suite runner (T413).

Discovers every golden case under `tests/golden/` (both `open/` and `held-out/`),
loads each case's `expect.py` via `importlib.util.spec_from_file_location` and calls
`module.check(case_dir)` directly (no subprocess — see
`docs/artifacts/golden-suite-format-v1.md` §4.1, the load-bearing contract this
script builds against), and emits a machine-readable JSON scorecard plus a
human-readable Markdown rendering *derived from* that JSON (see `render_markdown()`
below — a pure function of the JSON structure, not independently-authored prose).

This script is pre-allowlisted (by this exact path) in
`tests/functional/test_golden_held_out_isolation.py` to reference
`tests/golden/held-out/` — running both `open/` and `held-out/` cases in one place is
its whole job (see that guard's module docstring, "Allowlist" section, and
`docs/artifacts/golden-suite-format-v1.md` §3.1). This script is otherwise a pure
reader of `tests/golden/`: it MUST NOT write anything under that tree (not even a
cache file); all outputs go under `docs/benchmarks/`.

## Discovery

Per format spec §3.1: recursively glob for `expect.py` files under `tests/golden/`,
treat each `expect.py`'s parent directory as `case_dir`. Any path component starting
with `_` is excluded (this excludes `tests/golden/_example-scaffold/`, and any future
underscore-prefixed non-case directory). Discovery does not assume a fixed nesting
depth, so it is transparent to the `open/`/`held-out/` split (or any future
restructuring) without hardcoding either directory name.

## `case_dir` classification (open / held-out / other)

The `open`/`held-out` breakdown (format spec §3.1, plan-035 Phase 1 acceptance
criteria) is derived from whether `"open"` or `"held-out"` appears as a literal path
*component* immediately under `tests/golden/` in the case's relative path — this is a
read of the case's own location for reporting purposes, not a discovery-time filter
(discovery itself, per the paragraph above, never hardcodes either name). A case
directly under `tests/golden/<case-id>/` with neither `open/` nor `held-out/` as its
parent is classified `"other"` (the format spec's transitional flat layout, §3, not
expected in the current tree but not an error condition either — reported plainly
rather than silently dropped or crashing).

## Held-out case-ID redaction in output artifacts

`docs/benchmarks/scorecard-v6.12.0.json`/`.md` live outside `tests/golden/`, so unlike
this script's own source file (allowlisted by exact path in
`tests/functional/test_golden_held_out_isolation.py`), the *output* artifacts are not
exempt from that guard's Check B (any file outside `tests/golden/` that mentions a
held-out case ID as a whole token is flagged — see that module's docstring). Emitting
real held-out case IDs (or their `case_dir` paths, which contain the ID as a path
component) into these artifacts would be exactly the leak the guard exists to catch:
descriptive case IDs like `code-review-real-verdict-format-drift` reveal what a
held-out case tests, and this scorecard is precisely the kind of file "future
improvement work" (per this task's own brief, "Coordination note" /
"open/held-out breakdown" section) would read. The brief's own reasoning — "T414's
baseline and any future improvement work [can] distinguish suite-wide health from
held-out-only health **without either side needing to read the other's case content
directly**" — means the output artifacts must carry held-out *aggregate* health, not
held-out *case identity*.

Resolution (a design choice within this script's own file ownership, not an edit to
the guard's allowlist, which is out of scope per the task brief): `open/` cases are
reported with their real `id` and `case_dir` in full. `held-out/` cases are reported
with every field *except* identity — `command`, `status`, `known_failing_category`,
`bucket`, and `actual_result` are all real and visible (none of those single out
*which* case it is, only its category/outcome), but `id` and `case_dir` are replaced
with a deterministic anonymized label (`held-out-case-<n>`, `n` assigned by sorting
the real IDs — stable across runs, satisfying the determinism requirement below,
without ever emitting the real ID string). This keeps the per-case audit trail
(bucket/category/outcome counts are independently verifiable by summing the redacted
rows) while never writing a held-out case's real identity into a file the isolation
guard does not exempt. See `redact_held_out_identities()`.

## Determinism design decision (resolves the same tension as
docs/artifacts/golden-suite-format-v1.md §2.3)

Phase 1's acceptance criterion: "Re-running on an unchanged tree produces an
identical golden scorecard (deterministic)." Taken completely literally, embedding a
wall-clock `generated_at` timestamp anywhere in the JSON would make every run
byte-different regardless of whether any case's actual pass/fail content changed —
trivially failing the letter of the criterion while satisfying none of its intent
(the intent is that *results* are reproducible, not that the file never records when
it was produced).

**Decision (approach 2 from the task brief): split the JSON into two top-level keys,
`"content"` and `"run_metadata"`.** `"content"` holds everything that is a pure
function of the golden suite tree's on-disk bytes at call time: per-case results,
aggregate counts, the open/held-out breakdown. `"run_metadata"` holds exactly one
field, `generated_at` (ISO-8601 UTC), plus `schema_version` and `runner` for
self-description. A caller doing a strict determinism check hashes/compares only
`content`; `run_metadata.generated_at` is expected and allowed to differ between
runs. This is proven below, not just asserted — see this script's own module-level
`__main__` invocation history and the task's completion report, which runs this
script twice against an unchanged tree and diffs the two JSON outputs, confirming
only `run_metadata.generated_at` differs.

This mirrors the format spec's own resolution pattern (§2.3): don't avoid the
tension, resolve it by construction — `content` is a pure function of `case_dir`
bytes, exactly as `expect.py`'s own purity rules (§4.2) require of each case.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from types import ModuleType
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover - environment guard, not a case failure
    raise SystemExit(
        "scripts/scorecard.py requires PyYAML (`pip install pyyaml`) to parse case.yaml files"
    ) from exc

SCHEMA_VERSION = "golden-scorecard-v1"
GOLDEN_VERSION_LABEL = "v6.12.0"  # Phase 1's pre-registered release label (plan-035 §2.4).


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def golden_root() -> Path:
    return repo_root() / "tests" / "golden"


def discover_case_dirs(root: Path) -> list[Path]:
    """Recursively find every `expect.py` under `root`, excluding any path whose
    relative-to-`root` parts include a component starting with `_`. Returns sorted
    `case_dir` paths (each `expect.py`'s parent). Discovery-only — does not hardcode
    `open`/`held-out`/any other directory name (format spec §3.1)."""
    case_dirs: list[Path] = []
    for expect_path in root.rglob("expect.py"):
        rel = expect_path.relative_to(root)
        if any(part.startswith("_") for part in rel.parts):
            continue
        case_dirs.append(expect_path.parent)
    return sorted(case_dirs)


def classify_location(case_dir: Path, root: Path) -> str:
    """`"open"` / `"held-out"` / `"other"` — see module docstring's "case_dir
    classification" section."""
    rel_parts = case_dir.relative_to(root).parts
    if rel_parts and rel_parts[0] in ("open", "held-out"):
        return rel_parts[0]
    return "other"


def load_case_yaml(case_dir: Path) -> dict[str, Any]:
    case_yaml_path = case_dir / "case.yaml"
    with case_yaml_path.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict):
        raise ValueError(f"{case_yaml_path} did not parse to a mapping")
    return data


def load_expect_module(case_dir: Path) -> ModuleType:
    """Load `expect.py` via `importlib.util.spec_from_file_location`, mirroring
    `tests/functional/test_check_version_consistency.py`'s `_load_module()` pattern
    (format spec §4.1's explicit precedent). No subprocess, no shelling out."""
    expect_path = case_dir / "expect.py"
    # Module name must be unique per case to avoid sys.modules collisions across
    # cases that might otherwise share a bare "expect" name.
    module_name = f"golden_expect_{case_dir.name.replace('-', '_')}"
    spec = importlib.util.spec_from_file_location(module_name, expect_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load expect.py module from {expect_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_case(case_dir: Path, root: Path) -> dict[str, Any]:
    """Run a single case end to end: load case.yaml + expect.py, call check(),
    classify pass/fail/regression. Never raises for an ordinary case failure — a
    case whose expect.py itself raises is recorded as `actual_result: "error"` with
    the exception message captured, distinct from a clean False, so a runner bug and
    a genuine False are never conflated (format spec's check(case_dir) -> bool
    contract does not define exception behavior, so a raise is treated as neither
    pass nor fail but its own explicit state — an `unclear_requirements`-class
    reading documented here per the task's blocker protocol)."""
    meta = load_case_yaml(case_dir)
    case_id = meta.get("id", case_dir.name)
    status = meta.get("status")
    command = meta.get("command")
    known_failing_category = meta.get("known_failing_category")

    result: dict[str, Any] = {
        "id": case_id,
        "command": command,
        "location": classify_location(case_dir, root),
        "case_dir": case_dir.relative_to(root.parent).as_posix(),
        "status": status,
        "known_failing_category": known_failing_category,
    }

    try:
        module = load_expect_module(case_dir)
        actual = bool(module.check(case_dir))
        result["actual_result"] = "pass" if actual else "fail"
        result["error"] = None
    except Exception as exc:  # noqa: BLE001 - deliberately broad, see docstring
        result["actual_result"] = "error"
        result["error"] = f"{type(exc).__name__}: {exc}"
        actual = False

    # Bucket classification (format spec §4.4 / task brief acceptance criterion 5):
    # - expected_pass + actual pass -> "pass"
    # - expected_pass + actual fail/error -> "regression" (distinct bucket, never
    #   folded into known-failing)
    # - known_failing + actual fail/error -> "known_failing" (expected)
    # - known_failing + actual pass -> "unexpected_pass" (a known-failing case that
    #   now passes -- worth surfacing distinctly too, since it means the tracked
    #   defect/capability gap may have been fixed without updating case.yaml)
    if status == "expected_pass":
        result["bucket"] = "pass" if actual else "regression"
    elif status == "known_failing":
        result["bucket"] = "known_failing" if not actual else "unexpected_pass"
    else:
        result["bucket"] = "unrecognized_status"

    return result


def redact_held_out_identities(cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Replace `id`/`case_dir` with a deterministic anonymized label for every
    `held-out` case, in place on copies of the case dicts. See module docstring's
    "Held-out case-ID redaction in output artifacts" section — required because
    these output artifacts are not exempt from
    `tests/functional/test_golden_held_out_isolation.py`'s Check B the way this
    script's own source file is. Ordering is by the real `id` (sorted), so the
    label assignment is stable/deterministic across runs without ever emitting the
    real ID string."""
    held_out_order = sorted(c["id"] for c in cases if c["location"] == "held-out")
    label_by_real_id = {real_id: f"held-out-case-{i + 1}" for i, real_id in enumerate(held_out_order)}

    redacted: list[dict[str, Any]] = []
    for c in cases:
        c = dict(c)
        if c["location"] == "held-out":
            c["id"] = label_by_real_id[c["id"]]
            c["case_dir"] = "tests/golden/held-out/<redacted>"
        redacted.append(c)
    return redacted


def build_content(root: Path) -> dict[str, Any]:
    """The deterministic half of the scorecard — a pure function of the golden
    suite tree's on-disk bytes at call time. See module docstring's determinism
    section."""
    case_dirs = discover_case_dirs(root)
    cases = [run_case(case_dir, root) for case_dir in case_dirs]

    # Aggregate summary is computed from the real (unredacted) cases -- bucket
    # counts don't depend on identity -- then held-out identities are redacted
    # before the per-case list is included in the output content.
    summary = summarize(cases)
    cases = redact_held_out_identities(cases)
    return {
        "cases": cases,
        "summary": summary,
    }


def summarize(cases: list[dict[str, Any]]) -> dict[str, Any]:
    def count(pred) -> int:
        return sum(1 for c in cases if pred(c))

    by_location: dict[str, dict[str, int]] = {}
    for location in ("open", "held-out", "other"):
        loc_cases = [c for c in cases if c["location"] == location]
        if location == "other" and not loc_cases:
            continue
        by_location[location] = {
            "total": len(loc_cases),
            "pass": sum(1 for c in loc_cases if c["bucket"] == "pass"),
            "regression": sum(1 for c in loc_cases if c["bucket"] == "regression"),
            "known_failing": sum(1 for c in loc_cases if c["bucket"] == "known_failing"),
            "unexpected_pass": sum(1 for c in loc_cases if c["bucket"] == "unexpected_pass"),
            "tracked_defect": sum(
                1
                for c in loc_cases
                if c["bucket"] == "known_failing" and c["known_failing_category"] == "tracked_defect"
            ),
            "capability_gap": sum(
                1
                for c in loc_cases
                if c["bucket"] == "known_failing" and c["known_failing_category"] == "capability_gap"
            ),
        }

    return {
        "total_cases": len(cases),
        "total_pass": count(lambda c: c["bucket"] == "pass"),
        "total_fail": count(lambda c: c["bucket"] in ("regression", "known_failing")),
        "regressions": count(lambda c: c["bucket"] == "regression"),
        "known_failing": count(lambda c: c["bucket"] == "known_failing"),
        "tracked_defect": count(
            lambda c: c["bucket"] == "known_failing" and c["known_failing_category"] == "tracked_defect"
        ),
        "capability_gap": count(
            lambda c: c["bucket"] == "known_failing" and c["known_failing_category"] == "capability_gap"
        ),
        "unexpected_pass": count(lambda c: c["bucket"] == "unexpected_pass"),
        "unrecognized_status": count(lambda c: c["bucket"] == "unrecognized_status"),
        "by_location": by_location,
    }


def build_scorecard(root: Path) -> dict[str, Any]:
    content = build_content(root)
    run_metadata = {
        "schema_version": SCHEMA_VERSION,
        "runner": "scripts/scorecard.py",
        "golden_version": GOLDEN_VERSION_LABEL,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    return {"run_metadata": run_metadata, "content": content}


def render_markdown(scorecard: dict[str, Any]) -> str:
    """Render Markdown *from* the JSON structure — a pure function of `scorecard`,
    no independent authoring of facts. This is the only place prose is generated;
    every number below is read from `scorecard`, never recomputed or restated by
    hand."""
    meta = scorecard["run_metadata"]
    summary = scorecard["content"]["summary"]
    cases = scorecard["content"]["cases"]

    lines: list[str] = []
    lines.append(f"# Golden Suite Scorecard — {meta['golden_version']}")
    lines.append("")
    lines.append(
        f"Generated by `{meta['runner']}` at `{meta['generated_at']}` "
        f"(schema `{meta['schema_version']}`)."
    )
    lines.append("")
    lines.append(
        "Determinism scope: this Markdown is rendered from `docs/benchmarks/"
        f"scorecard-{meta['golden_version']}.json`'s `content` key only. `run_metadata."
        "generated_at` is expected to differ between runs; `content` is a pure function "
        "of the golden suite tree's on-disk bytes and is expected to be byte-identical "
        "across runs on an unchanged tree."
    )
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append("| Metric | Count |")
    lines.append("|---|---|")
    lines.append(f"| Total cases | {summary['total_cases']} |")
    lines.append(f"| Pass | {summary['total_pass']} |")
    lines.append(f"| Fail (regression + known_failing) | {summary['total_fail']} |")
    lines.append(f"| **Regressions** (expected_pass, now failing) | {summary['regressions']} |")
    lines.append(f"| Known-failing (expected) | {summary['known_failing']} |")
    lines.append(f"| — tracked_defect | {summary['tracked_defect']} |")
    lines.append(f"| — capability_gap | {summary['capability_gap']} |")
    lines.append(f"| Unexpected pass (known_failing now passing) | {summary['unexpected_pass']} |")
    if summary["unrecognized_status"]:
        lines.append(f"| Unrecognized status | {summary['unrecognized_status']} |")
    lines.append("")

    lines.append("## Open / held-out breakdown")
    lines.append("")
    lines.append("| Location | Total | Pass | Regressions | Known-failing | tracked_defect | capability_gap | Unexpected pass |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for location, stats in summary["by_location"].items():
        lines.append(
            f"| {location} | {stats['total']} | {stats['pass']} | {stats['regression']} | "
            f"{stats['known_failing']} | {stats['tracked_defect']} | {stats['capability_gap']} | "
            f"{stats['unexpected_pass']} |"
        )
    lines.append("")

    lines.append("## Per-case results")
    lines.append("")
    lines.append("| ID | Command | Location | Status | Bucket | Actual | Category |")
    lines.append("|---|---|---|---|---|---|---|")
    for c in cases:
        category = c["known_failing_category"] or "—"
        lines.append(
            f"| {c['id']} | {c['command']} | {c['location']} | {c['status']} | "
            f"{c['bucket']} | {c['actual_result']} | {category} |"
        )
    lines.append("")

    regressions = [c for c in cases if c["bucket"] == "regression"]
    if regressions:
        lines.append("## Regressions detail")
        lines.append("")
        for c in regressions:
            lines.append(f"- `{c['id']}` ({c['command']}, {c['location']}): {c.get('error') or 'check() returned False'}")
        lines.append("")

    return "\n".join(lines) + "\n"


def main() -> int:
    root = repo_root()
    golden_dir = golden_root()
    scorecard = build_scorecard(golden_dir)

    json_path = root / "docs" / "benchmarks" / f"scorecard-{GOLDEN_VERSION_LABEL}.json"
    md_path = root / "docs" / "benchmarks" / f"scorecard-{GOLDEN_VERSION_LABEL}.md"

    json_path.write_text(json.dumps(scorecard, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(render_markdown(scorecard), encoding="utf-8")

    summary = scorecard["content"]["summary"]
    print(
        f"scorecard: {summary['total_cases']} cases, {summary['total_pass']} pass, "
        f"{summary['regressions']} regressions, {summary['known_failing']} known_failing "
        f"(tracked_defect={summary['tracked_defect']}, capability_gap={summary['capability_gap']})"
    )
    print(f"wrote {json_path.relative_to(root)}")
    print(f"wrote {md_path.relative_to(root)}")
    return 1 if summary["regressions"] else 0


if __name__ == "__main__":
    sys.exit(main())
