"""Trial-record schema (T458 Objective #3).

Turns a single live trial's outcome into a structured, queryable record instead
of prose scattered across `task-T484.md` through `task-T494.md`. Every field
here is one this repo's 28 real trials already reported by hand -- this module
does not invent new fields, it gives the existing ones a checked schema.

Field meanings (see `docs/artifacts/golden-live-harness-v1.md` for the full
mapping to `plan-048` §7):

- `case_id` / `arm` / `k_index`: identify exactly which trial this is --
  `k_index` is the 1-based trial number within this case's own (case_id, arm)
  pair, e.g. the third control trial of `security-audit-coverage-consistency`
  is `k_index=3`.
- `result`: the real boolean from `check(case_dir)` (scoring.score_scratch_dir).
- `category`: the qualitative rubric category (`"1"`-`"5"`) from `plan-048` §5,
  populated only when a trial's output was actually characterized against that
  rubric -- `None` is a legitimate, common value (most trials, including every
  control trial, are never qualitatively characterized this way).
- `diagnosed_cause`: a short, stable label for *why* a failing trial failed,
  used by `policy.classify_k_plus_outcome` / `policy.is_floor_miss_actionable`
  to detect recurrence (plan-048 §4). `None` for passing trials and for
  failing trials whose cause was never diagnosed.
- `command`: the case's own command surface (e.g. `"/new-feature"`), carried
  for readability/filtering -- informational only, no policy function reads it.
- `provenance` (T510): how this trial's data was produced --
  `"fresh"` (a live dispatch performed for this comparison), `"reused"` (an
  older, already-persisted trial cited from a prior measurement, e.g. a
  `baseline-v*.md` table), or `"unknown"` (not recorded). Defaults to
  `"unknown"` on both construction and deserialization so every
  already-persisted `TrialRecord` predating this field (T507's own cited
  `baseline-v6.17.0-retrieval.md` records included) still deserializes
  without error and without being silently mis-tagged as `"fresh"` or
  `"reused"`. Consumed by `promotion.check_provenance_homogeneity()`, which
  fails closed on `"unknown"` (T509 design, Option C).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

ARM_CONTROL = "control"
ARM_TREATMENT = "treatment"
ALLOWED_ARMS = frozenset({ARM_CONTROL, ARM_TREATMENT})

# plan-048 §5's qualitative rubric, categories 1-5 (see that document's own
# table for the full definition of each category). This module does not
# restate the prose definitions -- it only validates that a recorded category
# is one of the five real values the rubric defines.
ALLOWED_CATEGORIES = frozenset({"1", "2", "3", "4", "5"})

# T510 (T509 design, Option C): a trial's data provenance. "unknown" is the
# safe default for any record that predates this field or that a caller never
# tagged -- `promotion.check_provenance_homogeneity()` treats "unknown" as
# fail-closed (mismatched), never as silently compatible.
PROVENANCE_FRESH = "fresh"
PROVENANCE_REUSED = "reused"
PROVENANCE_UNKNOWN = "unknown"
ALLOWED_PROVENANCES = frozenset({PROVENANCE_FRESH, PROVENANCE_REUSED, PROVENANCE_UNKNOWN})


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


@dataclass(frozen=True)
class TrialRecord:
    """One live trial's outcome. See module docstring for field semantics."""

    case_id: str
    arm: str
    k_index: int
    result: bool
    category: str | None = None
    diagnosed_cause: str | None = None
    command: str | None = None
    provenance: str = PROVENANCE_UNKNOWN
    recorded_at: str = field(default_factory=_utc_now_iso)

    def trial_id(self) -> str:
        """Deterministic id: unique per (case_id, arm, k_index)."""
        return f"{self.case_id}:{self.arm}:{self.k_index}"

    def to_dict(self) -> dict:
        return {
            "trial_id": self.trial_id(),
            "case_id": self.case_id,
            "arm": self.arm,
            "k_index": self.k_index,
            "result": self.result,
            "category": self.category,
            "diagnosed_cause": self.diagnosed_cause,
            "command": self.command,
            "provenance": self.provenance,
            "recorded_at": self.recorded_at,
        }

    @staticmethod
    def from_dict(data: dict) -> "TrialRecord":
        # T510: `provenance` postdates this field's introduction -- any
        # already-persisted record lacking the key (or storing an explicit
        # `None`/empty value) must default to PROVENANCE_UNKNOWN, never be
        # silently mis-tagged as "fresh" or "reused".
        return TrialRecord(
            case_id=data["case_id"],
            arm=data["arm"],
            k_index=data["k_index"],
            result=bool(data["result"]),
            category=data.get("category"),
            diagnosed_cause=data.get("diagnosed_cause"),
            command=data.get("command"),
            provenance=data.get("provenance") or PROVENANCE_UNKNOWN,
            recorded_at=data.get("recorded_at", _utc_now_iso()),
        )


def validate_trial_record(record: TrialRecord) -> list[str]:
    """Return a list of human-readable validation errors; empty means valid.
    Never raises -- callers decide whether a validation failure is fatal."""
    errors: list[str] = []
    if not record.case_id:
        errors.append("case_id must be non-empty")
    if record.arm not in ALLOWED_ARMS:
        errors.append(f"arm must be one of {sorted(ALLOWED_ARMS)}, got {record.arm!r}")
    if record.k_index < 1:
        errors.append(f"k_index must be >= 1, got {record.k_index}")
    if record.category is not None and record.category not in ALLOWED_CATEGORIES:
        errors.append(f"category must be one of {sorted(ALLOWED_CATEGORIES)} or None, got {record.category!r}")
    if record.provenance not in ALLOWED_PROVENANCES:
        errors.append(f"provenance must be one of {sorted(ALLOWED_PROVENANCES)}, got {record.provenance!r}")
    return errors
