"""Indexing pipeline entry point: parse -> validate -> chunk -> enrich ->
embed -> write. See `docs/artifacts/indexing-pipeline-v1.md` for the full
design and `memory-scope-model-v1.md` §10 for the contract this implements.

CLI usage:

    python3 -m implementation.runtime.memory.build \\
        --project-id em-age/emage.code \\
        --own-repo-root . \\
        --general-repo-root . \\
        --shared-source-root ../sia \\
        --output-dir implementation/runtime/memory/_index/em-age-emage.code

`--project-id` is always explicit (memory-scope-model-v1.md §4.1: "never
inferred from the content being indexed"). It must already be the id the
server derives from the workspace's git remote: lower case, `<org>/<repo>`
(T790, QA-T760-02). Any other spelling is refused, not rewritten: the
query-time filter compares exactly, so an index built under `Acme/Widget`
would answer nothing. `--shared-source-root` may be repeated zero or more
times.
"""
from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from pathlib import Path

from implementation.runtime.memory import scanner
from implementation.runtime.memory.chunker import chunk_body
from implementation.runtime.memory.context_retriever import is_derived_project_id
from implementation.runtime.memory.embed import PRIMARY_MODEL, LocalEmbedder, embed_chunks
from implementation.runtime.memory.enrich import build_chunk_records
from implementation.runtime.memory.index_writer import write_index
from implementation.runtime.memory.schema import ChunkRecord, ParsedEntry, RejectionRecord, SourceLocation
from implementation.runtime.memory.validate import (
    FrontmatterParseError,
    split_frontmatter,
    to_entry_frontmatter,
    validate_entry,
)


PROJECT_ID_FORM = (
    "the lower-case <org>/<repo> id that the server derives from the git remote 'origin' "
    "(for example em-age/emage.code)"
)


def project_id_problem(project_id: str) -> str | None:
    """None when `project_id` is in the derived form, else the refusal message (T790, QA-T760-02).
    The value is refused, never lower-cased or trimmed here (security-guidelines § Input Validation)."""
    if isinstance(project_id, str) and is_derived_project_id(project_id):
        return None
    return f"project id must be {PROJECT_ID_FORM}; got {str(project_id)[:80]!r}"


def _project_id_arg(value: str) -> str:
    problem = project_id_problem(value)
    if problem:
        raise argparse.ArgumentTypeError(problem)
    return value


@dataclass(frozen=True)
class BuildConfig:
    project_id: str
    own_repo_root: Path
    general_repo_root: Path
    output_dir: Path
    shared_source_roots: tuple[scanner.ScanRoot, ...] = field(default_factory=tuple)
    embedding_model: str = PRIMARY_MODEL

    def __post_init__(self) -> None:
        # The same refusal for a caller that does not come through the CLI: no index is built under
        # a project id the server can never derive.
        problem = project_id_problem(self.project_id)
        if problem:
            raise ValueError(problem)


@dataclass
class BuildResult:
    chunks: list[ChunkRecord]
    rejections: list[RejectionRecord]
    manifest: dict
    # Repo-relative paths of project-scope entries whose `project_id` differs from the build's own
    # only by letter case (T790). They are indexed under their own spelling, as before, and the
    # query-time filter never returns them; `main` names them on stderr.
    case_mismatched_paths: list[str] = field(default_factory=list)


def build_index(config: BuildConfig) -> BuildResult:
    own_root = scanner.ScanRoot(config.own_repo_root, config.project_id)
    general_root = scanner.ScanRoot(config.general_repo_root, "general-harness-source")

    entries, rejections = collect_entries(own_root, general_root, config)
    all_raw_chunks = [(entry, chunk_body(entry.body)) for entry in entries]
    records = [rec for entry, raws in all_raw_chunks for rec in build_chunk_records(entry, raws)]

    embedder = LocalEmbedder(model_name=config.embedding_model)
    embedded = embed_chunks(records, embedder)

    counts = _BuildCounts(len(entries), len(embedded), len(rejections))
    manifest = _build_manifest(config, embedder, counts)
    mismatched = case_mismatched_paths(entries, config.project_id)
    return BuildResult(chunks=embedded, rejections=rejections, manifest=manifest, case_mismatched_paths=mismatched)


def case_mismatched_paths(entries: list[ParsedEntry], project_id: str) -> list[str]:
    """Paths of the project-scope entries whose `project_id` equals `project_id` when both are
    case-folded but is not the same string. Paths only, never entry content."""
    return [
        entry.location.relative_path
        for entry in entries
        if entry.frontmatter.scope == "project"
        and entry.frontmatter.project_id != project_id
        and (entry.frontmatter.project_id or "").casefold() == project_id.casefold()
    ]


@dataclass(frozen=True)
class _ScanTarget:
    """One (repo root, expected scope) pair to ingest — bundled so the
    ingest functions below stay within this repo's max-4-parameters
    convention.
    """

    root: scanner.ScanRoot
    expected_scope: str


@dataclass
class _IngestState:
    config: BuildConfig
    entries: list[ParsedEntry] = field(default_factory=list)
    rejections: list[RejectionRecord] = field(default_factory=list)


def collect_entries(own_root, general_root, config: BuildConfig) -> tuple[list[ParsedEntry], list[RejectionRecord]]:
    """Scan + validate stage only (no chunking/embedding). Exposed as its own
    function — not just an implementation detail of `build_index` — because
    it is the stage acceptance criteria 3/4 (structural repo-boundary
    partitioning) are tested against directly, without paying the embedding
    model's cost/latency in every test run.
    """
    state = _IngestState(config=config)
    _ingest(_ScanTarget(own_root, "project"), scanner.scan_project_scope(own_root), state)
    _ingest(_ScanTarget(general_root, "general"), scanner.scan_general_scope(general_root), state)
    for source_root in config.shared_source_roots:
        _ingest(_ScanTarget(source_root, "shared"), scanner.scan_shared_scope(source_root), state)
    return state.entries, state.rejections


def _ingest(target: _ScanTarget, paths: list[Path], state: _IngestState) -> None:
    commit = scanner.resolve_commit(target.root.repo_root)
    for path in paths:
        _ingest_one(path, target, commit, state)


def _ingest_one(path: Path, target: _ScanTarget, commit: str, state: _IngestState) -> None:
    root = target.root
    rel_path = str(path.relative_to(root.repo_root))
    fm_dict, body, error = _parse_or_none(path)
    if error:
        state.rejections.append(RejectionRecord(rel_path, root.repo_id, commit, error, None))
        return
    fm = to_entry_frontmatter(fm_dict)
    reason = validate_entry(fm)
    if reason:
        state.rejections.append(RejectionRecord(rel_path, root.repo_id, commit, reason, fm.scope))
        return
    if not _is_includable(fm, target.expected_scope, state.config.project_id):
        return  # e.g. a shared-source repo's entry not naming this project; not a rejection
    location = SourceLocation(str(root.repo_root), root.repo_id, rel_path, commit)
    state.entries.append(ParsedEntry(fm, body, location))


def _parse_or_none(path: Path) -> tuple[dict, str, str | None]:
    try:
        text = path.read_text(encoding="utf-8")
        fm_dict, body = split_frontmatter(text)
        return fm_dict, body, None
    except (FrontmatterParseError, OSError, UnicodeDecodeError) as exc:
        return {}, "", str(exc)


def _is_includable(fm, expected_scope: str, project_id: str) -> bool:
    """The `include(entry, P)` predicate — memory-scope-model-v1.md §4.1.
    `expected_scope` is already structurally guaranteed by which subdirectory
    the scanner walked (project/general/shared); this only applies the
    remaining, scope-specific admission rule.
    """
    if fm.scope != expected_scope:
        return False  # malformed cross-listing; treat as not-found, not a reject
    if fm.scope == "shared":
        allowed = fm.shared_consumers.projects
        return project_id in allowed or allowed == ("*",)
    return True


@dataclass(frozen=True)
class _BuildCounts:
    entry_count: int
    chunk_count: int
    rejection_count: int


def _build_manifest(config: BuildConfig, embedder: LocalEmbedder, counts: _BuildCounts) -> dict:
    return {
        "project_id": config.project_id,
        "embedding_model": embedder.model_name,
        "embedding_dim": embedder.dim,
        "entry_count": counts.entry_count,
        "chunk_count": counts.chunk_count,
        "rejection_count": counts.rejection_count,
        "index_format_version": 1,
    }


def _parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--project-id", required=True, type=_project_id_arg,
                   help=f"{PROJECT_ID_FORM}; any other spelling is refused")
    p.add_argument("--own-repo-root", required=True, type=Path)
    p.add_argument("--general-repo-root", required=True, type=Path)
    p.add_argument("--shared-source-root", action="append", default=[], type=Path)
    p.add_argument("--output-dir", required=True, type=Path)
    p.add_argument("--embedding-model", default=PRIMARY_MODEL)
    p.add_argument(
        "--check-against", type=Path, default=None,
        help="Rebuild into a temp dir and diff against this existing index dir "
             "(mirrors implementation/scripts/sync.mjs --check / "
             "generate-registry.py --check's zero-drift-check convention) "
             "instead of writing --output-dir. Exit code 1 if any diff is found.",
    )
    return p.parse_args(argv)


def _config_from_args(args: argparse.Namespace) -> BuildConfig:
    shared_roots = tuple(
        scanner.ScanRoot(root.resolve(), root.resolve().name) for root in args.shared_source_root
    )
    return BuildConfig(
        project_id=args.project_id,
        own_repo_root=args.own_repo_root.resolve(),
        general_repo_root=args.general_repo_root.resolve(),
        output_dir=args.output_dir,
        shared_source_roots=shared_roots,
        embedding_model=args.embedding_model,
    )


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv if argv is not None else sys.argv[1:])
    config = _config_from_args(args)
    if args.check_against:
        return _run_check(config, args.check_against)
    result = build_index(config)
    _warn_case_mismatches(result, config.project_id)
    write_index(config.output_dir, result.chunks, result.rejections, result.manifest)
    print(f"wrote {len(result.chunks)} chunks, {len(result.rejections)} rejections to {config.output_dir}")
    return 0


def _warn_case_mismatches(result: BuildResult, project_id: str) -> None:
    for rel_path in result.case_mismatched_paths:
        print(
            f"warning: {rel_path!r}: its project_id differs from --project-id {project_id!r} only by "
            "letter case; retrieve will not return this entry",
            file=sys.stderr,
        )


def _run_check(config: BuildConfig, existing_dir: Path) -> int:
    """`--check-against <dir>`: rebuild into a fresh temp dir and diff against
    an already-written index — the rebuild-determinism check acceptance
    criterion 5 requires, in the same `--check`-style shape this repo's
    `sync.mjs --check`/`generate-registry.py --check` already establish.
    """
    import tempfile

    from implementation.runtime.memory.index_writer import diff_index_dirs

    result = build_index(config)
    _warn_case_mismatches(result, config.project_id)
    with tempfile.TemporaryDirectory() as tmp:
        fresh_dir = Path(tmp) / "rebuild"
        write_index(fresh_dir, result.chunks, result.rejections, result.manifest)
        diffs = diff_index_dirs(existing_dir, fresh_dir)
    if diffs:
        print(f"DRIFT DETECTED ({len(diffs)} diffs):")
        for d in diffs:
            print(f"  {d}")
        return 1
    print(f"no drift: rebuild matches {existing_dir} (within vector tolerance)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
