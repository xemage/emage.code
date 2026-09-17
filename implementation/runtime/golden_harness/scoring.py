"""`expect.py`-reuse scoring module (T458 Objective #2).

Loads a real golden case's real, unmodified `expect.py` and calls its
`check(case_dir)` against a scratch directory built by `scratch.py`, using
the exact `importlib.util.spec_from_file_location` pattern
`scripts/scorecard.py`'s own `load_expect_module()` already uses (reused
verbatim in shape, not imported from `scripts/scorecard.py` -- that file is a
protected path, see `docs/artifacts/protected-paths-v1.md`, and is never
imported from or duplicated logic-wise beyond mirroring this one documented,
public contract from `docs/artifacts/golden-suite-format-v1.md` §4.1).

`golden_case_dir` (the real case directory containing `expect.py`) is always
caller-supplied, never hardcoded here -- this module never spells out the
held-out subdirectory's own path as a literal string and mentions no case ID,
so it needs no allowlist entry in
`tests/functional/test_golden_held_out_isolation.py` (that guard's Check A
only flags Python source that hardcodes such a path).
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType


def load_expect_module(golden_case_dir: Path) -> ModuleType:
    """Load `golden_case_dir / "expect.py"` via
    `importlib.util.spec_from_file_location` -- the same pattern
    `scripts/scorecard.py`'s `load_expect_module()` uses. Raises
    `FileNotFoundError` if no `expect.py` exists there, `RuntimeError` if the
    module cannot be loaded (mirrors `scripts/scorecard.py`'s own error
    shape)."""
    expect_path = golden_case_dir / "expect.py"
    if not expect_path.is_file():
        raise FileNotFoundError(f"no expect.py under {golden_case_dir}")
    module_name = f"golden_harness_expect_{golden_case_dir.name.replace('-', '_')}"
    spec = importlib.util.spec_from_file_location(module_name, expect_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load expect.py module from {expect_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def score_scratch_dir(golden_case_dir: Path, scratch_case_dir: Path) -> bool:
    """Score one trial: load `golden_case_dir`'s real `expect.py` and call
    `check(scratch_case_dir)` -- the same call shape every one of the 28 real
    trials behind `plan-048` already used by hand
    (`task-T484.md`/`task-T493.md` Execution notes;
    `scripts/scorecard.py`'s own `run_case()`). Returns the real boolean;
    raises whatever `check()` itself raises (never silently swallowed -- a
    genuine `expect.py` error is a real, disclosable finding, not a `False`)."""
    module = load_expect_module(golden_case_dir)
    return bool(module.check(scratch_case_dir))


def find_golden_case_dir(case_id: str, golden_root: Path) -> Path:
    """Resolve a case id to its real on-disk directory by recursively
    globbing for `expect.py` under `golden_root` (mirrors
    `scripts/scorecard.py`'s `discover_case_dirs()` -- directory-shape
    agnostic, per `golden-suite-format-v1.md` §3.1, so it works whether the
    case lives under `open/`, `held-out/`, or a future layout, without
    hardcoding either name). Raises `LookupError` if zero or more than one
    match is found."""
    matches = [p.parent for p in golden_root.rglob("expect.py") if p.parent.name == case_id]
    if len(matches) != 1:
        raise LookupError(f"expected exactly one case dir named {case_id!r} under {golden_root}, found {len(matches)}")
    return matches[0]
