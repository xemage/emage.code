"""Trial-record store (T458 Objective #3).

An append-only JSONL file, one `TrialRecord` per line, mirroring this repo's
existing deterministic-JSONL convention
(`implementation/runtime/memory/index_writer.py`). The store's location is
always caller-supplied -- this module has no default path and does not write
anywhere under `tests/golden/**` or any other protected path.

This does not attempt to retroactively re-encode the 28 historical trials
(`task-T484.md` through `task-T494.md`) -- per `task-T458.md`'s own
Constraints, that is optional, disclosed scope, not required. The store
works for new trials regardless of whether any historical ones are ever
backfilled into it.
"""
from __future__ import annotations

import json
from pathlib import Path

from implementation.runtime.golden_harness.schema import TrialRecord


def append_trial(store_path: Path, record: TrialRecord) -> None:
    """Append one trial record as a JSON line. Creates `store_path`'s parent
    directory and the file itself if either doesn't exist yet."""
    store_path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(record.to_dict(), sort_keys=True)
    with store_path.open("a", encoding="utf-8") as fh:
        fh.write(line + "\n")


def load_trials(store_path: Path) -> list[TrialRecord]:
    """Read every trial record back from `store_path`. Returns an empty list
    if the file doesn't exist yet (an unstarted store is not an error)."""
    if not store_path.exists():
        return []
    text = store_path.read_text(encoding="utf-8")
    return [TrialRecord.from_dict(json.loads(line)) for line in text.splitlines() if line.strip()]


def trials_for_case(trials: list[TrialRecord], case_id: str, arm: str | None = None) -> list[TrialRecord]:
    """Filter an already-loaded trial list to one case (and optionally one
    arm), sorted by `k_index`. Pure/in-memory -- callers combine this with
    `load_trials()` rather than this module re-reading the file per query."""
    matches = [t for t in trials if t.case_id == case_id and (arm is None or t.arm == arm)]
    return sorted(matches, key=lambda t: t.k_index)


def next_k_index(trials: list[TrialRecord], case_id: str, arm: str) -> int:
    """The next 1-based `k_index` to use for a new trial of (case_id, arm),
    computed from the highest `k_index` already recorded for that pair."""
    existing = trials_for_case(trials, case_id, arm)
    if not existing:
        return 1
    return existing[-1].k_index + 1
