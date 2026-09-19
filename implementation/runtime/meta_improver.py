"""`@meta-improver`: failure-cluster -> diff-proposal generator (T503,
`plan-035` nominal T462, `plan-055` `T462-equiv`).

## What this module is, and the one property that matters most

This module consumes classified failure data (T501's
`implementation.runtime.golden_harness.failure_taxonomy.FailureTaxonomy`) and
emits `DiffProposal` objects: pure, inert data describing a *suggested* change
to this repo's own harness surface (agent/skill/command/instruction
definitions) -- never an applied edit. See `docs/artifacts/meta-improver-v1.md`
for the full design write-up; this docstring states the load-bearing
guarantee only.

**This module is architecturally incapable of writing to any real repository
file.** Not "it doesn't currently call a write function" -- there is no
filesystem-mutating call anywhere in this module's source at all: no
write-mode `open()`, no `Path.write_text`/`write_bytes`/`unlink`, no
`os.remove`/`rename`/`replace`, no `shutil.*`, no `subprocess`/`os.system`
call of any kind. `tests/functional/test_meta_improver.py`'s
`TestNoFilesystemMutation` class proves this two independent ways: a static
AST scan of this module's own source (so a future edit that reintroduces a
write call fails a test, not just a code-review glance), and a behavioral
before/after repo-snapshot test that runs the full real pipeline (real T501
taxonomy -> real clusters -> real proposals) and asserts the on-disk repo is
byte-identical afterwards.

T464-equiv (the human MR gate) does not exist yet -- there is currently no
downstream consumer that could safely apply a proposal even if this module
produced one capable of self-applying. This module therefore has no `apply()`,
no `write()`, no method anywhere on `DiffProposal` or any object it returns
that touches the filesystem for anything other than the read-only lookups
needed to build a proposal's `base_content` (see `_select_target`).

## `@meta-improver`, a Python module, not a registered subagent

Per `docs/tasks/task-T503.md`'s own disclosed scoping decision: `@meta-improver`
is this importable module (a plain function-call API), not a new
`implementation/knowledge/agents/meta-improver.md` registered Claude subagent.
Proving "architecturally incapable of writing" is far more tractable for a
plain Python library -- the question reduces to "does this module's own
source code ever call a filesystem-mutating function", checked directly by
AST -- than for a registered agent definition whose safety would depend on a
`tools:` YAML grant never being loosened later. No `sync.mjs`/
`generate-registry.py` run, no platform-projection file, and no
`implementation/registry/` entry is part of this module's build.
"""
from __future__ import annotations

import difflib
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath

from implementation.runtime.golden_harness.failure_taxonomy import FailureTaxonomy

# implementation/runtime/meta_improver.py -> implementation/runtime ->
# implementation -> repo root. Mirrors kill_switch.py's own REPO_ROOT
# derivation exactly.
REPO_ROOT = Path(__file__).resolve().parents[2]

# The four allowed harness-surface file classes this module may ever target
# (Objective point 2). This is this repo's actual harness surface -- agent
# definitions, skills, commands, instructions -- never application code, and
# never the two paths `docs/artifacts/protected-paths-v1.md` declares
# protected (`tests/golden/**`, `scripts/scorecard.py`): a proposal is data
# about *how the harness should change*, and the golden suite is the thing
# harness changes are graded against, not a thing this module may itself
# propose changing. See `docs/artifacts/meta-improver-v1.md` SS2 for the full
# "why these four and no others" reasoning.
TARGET_CLASS_AGENT = "agent"
TARGET_CLASS_SKILL = "skill"
TARGET_CLASS_COMMAND = "command"
TARGET_CLASS_INSTRUCTION = "instruction"

_TARGET_CLASS_PATTERNS: tuple[tuple[str, PurePosixPath], ...] = (
    (TARGET_CLASS_AGENT, "implementation/knowledge/agents"),
    (TARGET_CLASS_SKILL, "implementation/knowledge/skills"),
    (TARGET_CLASS_COMMAND, "implementation/knowledge/commands"),
    (TARGET_CLASS_INSTRUCTION, "implementation/knowledge/instructions"),
)


def classify_target_path(target_path: str) -> str:
    """Return the target-file class (`"agent"`/`"skill"`/`"command"`/
    `"instruction"`) for `target_path`, a repo-root-relative POSIX path.
    Raises `ValueError` -- never silently accepts -- if `target_path` is
    absolute, contains a `..` path-traversal segment, or does not fall under
    exactly one of the four allowed directories with the expected filename
    shape (`agents/*.md`, `skills/*/SKILL.md`, `commands/*.md`,
    `instructions/*.md`).

    This is a pure string/path computation -- no filesystem access, so it can
    reject a disallowed path (including the two protected paths
    `docs/artifacts/protected-paths-v1.md` declares:
    `tests/golden/**` and `scripts/scorecard.py`) before any I/O ever
    happens, and before `DiffProposal.__post_init__` (the only caller in this
    module) constructs a proposal object at all.
    """
    candidate = PurePosixPath(target_path)
    if candidate.is_absolute():
        raise ValueError(f"target_path must be repo-root-relative, got absolute path {target_path!r}")
    if ".." in candidate.parts:
        raise ValueError(f"target_path must not contain '..' path-traversal segments: {target_path!r}")

    parts = candidate.parts
    if len(parts) == 4 and tuple(parts[:3]) == ("implementation", "knowledge", "agents") and parts[3].endswith(".md"):
        return TARGET_CLASS_AGENT
    if (
        len(parts) == 5
        and tuple(parts[:3]) == ("implementation", "knowledge", "skills")
        and parts[4] == "SKILL.md"
    ):
        return TARGET_CLASS_SKILL
    if len(parts) == 4 and tuple(parts[:3]) == ("implementation", "knowledge", "commands") and parts[3].endswith(".md"):
        return TARGET_CLASS_COMMAND
    if (
        len(parts) == 4
        and tuple(parts[:3]) == ("implementation", "knowledge", "instructions")
        and parts[3].endswith(".md")
    ):
        return TARGET_CLASS_INSTRUCTION

    raise ValueError(
        f"target_path {target_path!r} is not an allowed harness-surface file. "
        "Allowed classes: implementation/knowledge/agents/*.md, "
        "implementation/knowledge/skills/*/SKILL.md, "
        "implementation/knowledge/commands/*.md, "
        "implementation/knowledge/instructions/*.md."
    )


@dataclass(frozen=True)
class DiffProposal:
    """A single, reviewable diff proposal. Pure, inert data -- see module
    docstring's "one property that matters most". Exposes exactly one
    computational (not I/O) helper, `diff_text()`, and nothing else beyond
    plain field access.

    Fields:
      target_path: repo-root-relative POSIX path of the file this proposal
        would change if a human reviewer accepted and applied it.
      target_file_class: derived automatically from `target_path` at
        construction time via `classify_target_path` -- never supplied by
        the caller, so it can never drift from what `target_path` actually
        is. `init=False`.
      rationale: human-readable explanation of why this change is proposed
        and why this target file was selected.
      base_content: the target file's real content *at proposal-generation
        time* (a snapshot, not a live reference -- this proposal object
        holds no path handle and performs no later re-read).
      proposed_content: the full proposed new content of the target file.
      based_on: the triggering `FailureRecord.case_id` values this proposal
        is based on -- a reference by id into `FailureTaxonomy`, never a
        duplicate copy of the records' own data.
      cluster_cause / cluster_behavior / cluster_mechanism: the triggering
        cluster's axis triple, carried for a reviewer's convenience (also
        recoverable via `based_on` + `FailureTaxonomy.get()`).
    """

    target_path: str
    rationale: str
    base_content: str
    proposed_content: str
    based_on: tuple[str, ...]
    cluster_cause: str
    cluster_behavior: str
    cluster_mechanism: str
    target_file_class: str = field(init=False)

    def __post_init__(self) -> None:
        # Objective point 2's first-layer defense-in-depth: raise, don't
        # silently accept, for any disallowed target path. `object.__setattr__`
        # is the standard pattern for a frozen dataclass to set a field
        # derived from other fields inside __post_init__.
        object.__setattr__(self, "target_file_class", classify_target_path(self.target_path))
        if not self.based_on:
            raise ValueError("DiffProposal.based_on must reference at least one triggering case_id")
        if self.proposed_content == self.base_content:
            raise ValueError("DiffProposal.proposed_content must differ from base_content")

    def diff_text(self) -> str:
        """A real unified-diff representation of `base_content` ->
        `proposed_content`, for a human reviewer. Pure computation over the
        two content strings already held by this object (`difflib`, stdlib,
        in-memory) -- performs no I/O, reads no file, writes nothing."""
        return "".join(
            difflib.unified_diff(
                self.base_content.splitlines(keepends=True),
                self.proposed_content.splitlines(keepends=True),
                fromfile=self.target_path,
                tofile=self.target_path,
            )
        )


@dataclass(frozen=True)
class FailureCluster:
    """A group of failure records sharing one `(cause, behavior, mechanism)`
    axis triple (see `cluster_by_axes`'s docstring for why this grouping was
    chosen). `case_ids` is sorted for determinism; a cluster of size 1 is a
    valid, expected output, not an error."""

    cause: str
    behavior: str
    mechanism: str
    case_ids: tuple[str, ...]


def cluster_by_axes(taxonomy: FailureTaxonomy) -> tuple[FailureCluster, ...]:
    """Group every record in `taxonomy` by its `(cause, behavior, mechanism)`
    triple (`FailureRecord.axes()`).

    Design decision (T461 deferred "clustering" as this task's own call):
    grouping by the shared axis triple is the minimal, well-defined choice
    that requires no new logic beyond what `FailureTaxonomy.filter_by`
    already supports (`filter_by(cause=..., behavior=..., mechanism=...)`
    returns exactly one cluster's membership), and it directly reflects this
    repo's own three-axis scheme (`docs/artifacts/failure-taxonomy-v1.md`) --
    two failures with the same cause/behavior/mechanism are, by that
    scheme's own definition, the same kind of failure, and a diff proposal
    generated from them is proposing to fix one recurring pattern rather than
    an arbitrary grab-bag of unrelated ones. See
    `docs/artifacts/meta-improver-v1.md` SS3 for the full write-up, including
    alternatives considered.

    Returns clusters sorted by `(cause, behavior, mechanism)` for a
    deterministic, testable order. A cluster is emitted for every distinct
    triple present, including triples with exactly one member -- a singleton
    cluster is valid, expected output.
    """
    groups: dict[tuple[str, str, str], list[str]] = {}
    for record in taxonomy.all_records():
        groups.setdefault(record.axes(), []).append(record.case_id)

    clusters = [
        FailureCluster(cause=cause, behavior=behavior, mechanism=mechanism, case_ids=tuple(sorted(case_ids)))
        for (cause, behavior, mechanism), case_ids in groups.items()
    ]
    return tuple(sorted(clusters, key=lambda cluster: (cluster.cause, cluster.behavior, cluster.mechanism)))


def _axis_keywords(cluster: FailureCluster) -> tuple[str, ...]:
    """Deterministic keyword tokens derived from a cluster's axis values:
    every hyphen-separated word across `cause`/`behavior`/`mechanism`,
    lowercased, deduplicated, order-preserving. E.g.
    `cause="undefined-structured-convention"` contributes
    `"undefined"`, `"structured"`, `"convention"`."""
    seen: list[str] = []
    for axis_value in (cluster.cause, cluster.behavior, cluster.mechanism):
        for word in axis_value.lower().split("-"):
            if word and word not in seen:
                seen.append(word)
    return tuple(seen)


def _iter_candidate_target_files(repo_root: Path) -> tuple[Path, ...]:
    """Every real, on-disk file under the four allowed target-file classes,
    repo-root-relative-path order (deterministic). Read-only glob -- lists
    directory entries, does not open or mutate any of them."""
    knowledge = repo_root / "implementation" / "knowledge"
    candidates: list[Path] = []
    candidates += sorted((knowledge / "agents").glob("*.md"))
    candidates += sorted((knowledge / "skills").glob("*/SKILL.md"))
    candidates += sorted((knowledge / "commands").glob("*.md"))
    candidates += sorted((knowledge / "instructions").glob("*.md"))
    return tuple(candidates)


def _select_target(cluster: FailureCluster, repo_root: Path) -> tuple[str, str, int]:
    """Target-selection heuristic (Objective point 4): score every candidate
    file under the four allowed classes by how many of the cluster's
    hyphen-derived axis keywords appear as a case-insensitive substring of
    that file's content; pick the highest-scoring file, breaking ties by the
    lexicographically smallest repo-relative POSIX path (deterministic).

    If every candidate scores 0 (no keyword overlap at all -- not observed
    against the real, current knowledge base, but a real fallback is still
    required so this function always returns *some* allowed target rather
    than raising), fall back to the lexicographically smallest file under
    `implementation/knowledge/instructions/` -- deterministic, always
    present (that directory is never empty in this repo), and instructions
    are this repo's most general "how work here is done" surface, the most
    plausible home for a pattern with no clearer, more specific match.

    Returns `(repo_root_relative_posix_target_path, base_content, score)`.
    """
    keywords = _axis_keywords(cluster)
    best_path: Path | None = None
    best_score = -1
    best_content = ""

    for candidate in _iter_candidate_target_files(repo_root):
        content = candidate.read_text(encoding="utf-8")
        lowered = content.lower()
        score = sum(1 for keyword in keywords if keyword in lowered)
        if score > best_score:
            best_score = score
            best_path = candidate
            best_content = content

    if best_path is None:
        raise RuntimeError(
            "no candidate target files found under any of the four allowed "
            "harness-surface directories -- an empty knowledge base is not "
            "a supported repo state for this module"
        )

    if best_score <= 0:
        fallback_candidates = sorted((repo_root / "implementation" / "knowledge" / "instructions").glob("*.md"))
        if not fallback_candidates:
            raise RuntimeError("fallback target directory implementation/knowledge/instructions/*.md is empty")
        best_path = fallback_candidates[0]
        best_content = best_path.read_text(encoding="utf-8")
        best_score = 0

    relative = best_path.relative_to(repo_root).as_posix()
    return relative, best_content, best_score


def _render_addition(cluster: FailureCluster) -> str:
    """The proposed diff content: a "Known failure pattern" note citing the
    cluster's axis values and triggering case IDs (Objective point 4's
    documented default generation shape)."""
    case_list = ", ".join(f"`{case_id}`" for case_id in cluster.case_ids)
    return (
        "\n\n## Known failure pattern (meta-improver proposal)\n\n"
        "_Proposed automatically by `@meta-improver` "
        "(`implementation/runtime/meta_improver.py`) from a cluster of "
        "classified failure records. This is a proposal only -- it has not "
        "been applied, and this generator has no mechanism to apply it "
        "itself. Review before merging._\n\n"
        f"- **Cause:** `{cluster.cause}`\n"
        f"- **Behavior:** `{cluster.behavior}`\n"
        f"- **Mechanism:** `{cluster.mechanism}`\n"
        f"- **Triggering case(s):** {case_list}\n"
    )


def generate_proposal(cluster: FailureCluster, *, repo_root: Path | None = None) -> DiffProposal:
    """Generate a `DiffProposal` for one `FailureCluster` -- the "emits"
    mechanism (Objective point 4). Deterministic and rule-based/template:
    selects a target file via `_select_target`'s keyword-overlap heuristic,
    then appends a "Known failure pattern" note (`_render_addition`) citing
    the cluster's axis values and triggering case IDs. No live LLM dispatch
    of any kind -- see `docs/artifacts/meta-improver-v1.md` SS4 for why a
    template-based generator was judged sufficient for this task's scope.

    `repo_root` defaults to this module's own resolved repo root
    (`REPO_ROOT`) but is caller-overridable, mirroring
    `FailureTaxonomy.load`'s own "never hardcodes a repo-root path"
    convention -- useful for tests exercising a synthetic knowledge base.
    """
    root = repo_root if repo_root is not None else REPO_ROOT
    target_path, base_content, score = _select_target(cluster, root)
    addition = _render_addition(cluster)
    proposed_content = base_content.rstrip("\n") + addition + "\n"

    rationale = (
        f"{len(cluster.case_ids)} classified failure record(s) "
        f"({', '.join(cluster.case_ids)}) share the axis triple "
        f"cause={cluster.cause!r}, behavior={cluster.behavior!r}, "
        f"mechanism={cluster.mechanism!r}. Target file {target_path!r} was "
        f"selected by keyword-overlap score {score} against the cluster's "
        f"axis-derived keywords {_axis_keywords(cluster)!r} among candidate "
        "files in the four allowed harness-surface classes (see "
        "classify_target_path)."
    )

    return DiffProposal(
        target_path=target_path,
        rationale=rationale,
        base_content=base_content,
        proposed_content=proposed_content,
        based_on=cluster.case_ids,
        cluster_cause=cluster.cause,
        cluster_behavior=cluster.behavior,
        cluster_mechanism=cluster.mechanism,
    )


def generate_proposals(taxonomy: FailureTaxonomy, *, repo_root: Path | None = None) -> tuple[DiffProposal, ...]:
    """Convenience wrapper: cluster `taxonomy` (`cluster_by_axes`) and
    generate one `DiffProposal` per resulting cluster (`generate_proposal`),
    in the same deterministic cluster order. This is the module's full
    end-to-end pipeline entry point, used directly by the orchestrator's own
    live end-to-end validation pass (`docs/tasks/task-T503.md` "Split
    ownership") and by `tests/functional/test_meta_improver.py`'s real-data
    functional and behavioral no-write-side-effect tests."""
    clusters = cluster_by_axes(taxonomy)
    return tuple(generate_proposal(cluster, repo_root=repo_root) for cluster in clusters)
