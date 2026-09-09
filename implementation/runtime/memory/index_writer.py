"""Derived-index writer — on-disk format documented in
`docs/artifacts/indexing-pipeline-v1.md`.

Three files per build, written under `<output_dir>/`:

  index.jsonl        one JSON object per chunk, deterministically sorted
  rejections.jsonl    one JSON object per §5 rejection, deterministically sorted
  manifest.json        deterministic build summary (no timestamps/PIDs/paths
                        that would vary run-to-run) — this is what makes the
                        rebuild-determinism check (`--check`) meaningful.

Vectors are compared with a numerical tolerance, not byte-identity, in
`diff_index_dirs` — see that function's docstring for why.
"""
from __future__ import annotations

import dataclasses
import json
from pathlib import Path

from implementation.runtime.memory.schema import ChunkRecord, RejectionRecord

VECTOR_TOLERANCE = 1e-6


def _chunk_sort_key(chunk: ChunkRecord) -> tuple:
    return (chunk.path, chunk.line_range, chunk.chunk_id)


def _rejection_sort_key(rec: RejectionRecord) -> tuple:
    return (rec.repo_id, rec.source_path)


def _chunk_to_json(chunk: ChunkRecord) -> dict:
    d = dataclasses.asdict(chunk)
    if d.get("shared_consumers") is not None:
        d["shared_consumers"] = {
            "projects": list(chunk.shared_consumers.projects),
            "platforms": list(chunk.shared_consumers.platforms),
        }
    d["parents"] = list(chunk.parents)
    d["imports"] = list(chunk.imports)
    d["tags"] = list(chunk.tags)
    d["line_range"] = list(chunk.line_range)
    d["vector"] = list(chunk.vector)
    return d


def write_index(output_dir: Path, chunks: list[ChunkRecord], rejections: list[RejectionRecord],
                 manifest: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_jsonl(output_dir / "index.jsonl", sorted(chunks, key=_chunk_sort_key), _chunk_to_json)
    _write_jsonl(output_dir / "rejections.jsonl", sorted(rejections, key=_rejection_sort_key),
                 dataclasses.asdict)
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8",
    )


def _write_jsonl(path: Path, records: list, to_json) -> None:
    lines = [json.dumps(to_json(r), sort_keys=True) for r in records]
    path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")


def _read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    return [json.loads(line) for line in text.splitlines() if line.strip()]


def diff_index_dirs(a: Path, b: Path) -> list[str]:
    """Compare two build outputs for "functionally-equivalent" rebuild
    reproduction (acceptance criterion 5): every non-vector field must be
    byte-identical; vector fields may differ up to `VECTOR_TOLERANCE`
    (ONNX Runtime CPU inference is not guaranteed bit-stable across
    process runs when multi-threaded reduction ops are involved — see
    `docs/artifacts/indexing-pipeline-v1.md` for the measured delta this
    repo actually observes). Returns a list of human-readable diffs; empty
    means the two builds are equivalent under this rule.
    """
    diffs = []
    diffs += _diff_jsonl(_read_jsonl(a / "index.jsonl"), _read_jsonl(b / "index.jsonl"), "index.jsonl")
    diffs += _diff_jsonl(_read_jsonl(a / "rejections.jsonl"), _read_jsonl(b / "rejections.jsonl"),
                          "rejections.jsonl")
    return diffs


def _diff_jsonl(a_records: list[dict], b_records: list[dict], label: str) -> list[str]:
    if len(a_records) != len(b_records):
        return [f"{label}: record count differs ({len(a_records)} vs {len(b_records)})"]
    diffs = []
    for i, (a_rec, b_rec) in enumerate(zip(a_records, b_records)):
        diffs += _diff_record(a_rec, b_rec, f"{label}[{i}]")
    return diffs


def _diff_record(a_rec: dict, b_rec: dict, label: str) -> list[str]:
    diffs = []
    keys = set(a_rec) | set(b_rec)
    for key in sorted(keys):
        if key == "vector":
            diffs += _diff_vector(a_rec.get(key), b_rec.get(key), label)
        elif a_rec.get(key) != b_rec.get(key):
            diffs.append(f"{label}.{key}: {a_rec.get(key)!r} != {b_rec.get(key)!r}")
    return diffs


def _diff_vector(a_vec, b_vec, label: str) -> list[str]:
    if a_vec is None or b_vec is None:
        return [] if a_vec == b_vec else [f"{label}.vector: one side missing"]
    if len(a_vec) != len(b_vec):
        return [f"{label}.vector: length differs ({len(a_vec)} vs {len(b_vec)})"]
    max_delta = max((abs(x - y) for x, y in zip(a_vec, b_vec)), default=0.0)
    if max_delta > VECTOR_TOLERANCE:
        return [f"{label}.vector: max abs delta {max_delta} exceeds tolerance {VECTOR_TOLERANCE}"]
    return []
