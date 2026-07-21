"""Functional tests for Task T230: Trainer Bridge — Parquet → GRPO/SFT Dataset."""
from __future__ import annotations

import importlib.util
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

# ---------------------------------------------------------------------------
# Module loading (mirrors T224/T225 pattern)
# ---------------------------------------------------------------------------
_bridge_path = (
    Path(__file__).parent.parent.parent
    / "implementation" / "adapters" / "sia-target" / "trainer_bridge.py"
)
_spec = importlib.util.spec_from_file_location("trainer_bridge", _bridge_path)
trainer_bridge = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(trainer_bridge)
sys.modules["trainer_bridge"] = trainer_bridge

read_trajectories = trainer_bridge.read_trajectories
build_grpo_dataset = trainer_bridge.build_grpo_dataset
build_sft_dataset = trainer_bridge.build_sft_dataset
build_dataset = trainer_bridge.build_dataset


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_parquet(path: Path, rows: list[dict]) -> None:
    """Write a minimal Parquet file from a list of row dicts."""
    if not rows:
        table = pa.table({
            "workspace_uuid": pa.array([], type=pa.string()),
            "rollout_session_id": pa.array([], type=pa.string()),
        })
        pq.write_table(table, str(path))
        return

    # Build column arrays from row dicts; use None for missing fields.
    all_keys: list[str] = list({k for row in rows for k in row})
    columns: dict[str, list] = {k: [row.get(k) for row in rows] for k in all_keys}
    table = pa.table(columns)
    pq.write_table(table, str(path))


def _make_record(
    session_id: str = "sess-001",
    prompt: list[int] | None = None,
    sampled: list[int] | None = None,
    shaped_reward: float | None = None,
    evaluation_reward: float | None = None,
    workspace_uuid: str = "ws-001",
) -> dict:
    return {
        "workspace_uuid": workspace_uuid,
        "rollout_session_id": session_id,
        "prompt_token_ids": prompt or [1, 2, 3],
        "sampled_token_ids": sampled or [4, 5],
        "logprobs": [-0.1, -0.2],
        "finish_reason": "stop",
        "timestamp_ns": 1_000_000_000,
        "shaped_reward": shaped_reward,
        "evaluation_reward": evaluation_reward,
    }


# ---------------------------------------------------------------------------
# Test classes
# ---------------------------------------------------------------------------

class TestReadTrajectoriesEmpty(unittest.TestCase):
    """read_trajectories — edge cases with empty/missing stores."""

    def test_missing_store_returns_empty(self) -> None:
        """Non-existent store_path returns []."""
        result = read_trajectories("/tmp/_does_not_exist_t230_x7z9")
        self.assertEqual(result, [])

    def test_empty_directory_returns_empty(self) -> None:
        """Directory with no .parquet files returns []."""
        with tempfile.TemporaryDirectory() as tmp:
            result = read_trajectories(tmp)
        self.assertEqual(result, [])

    def test_directory_with_non_parquet_files_returns_empty(self) -> None:
        """Only non-.parquet files → returns []."""
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "data.csv").write_text("a,b\n1,2\n")
            result = read_trajectories(tmp)
        self.assertEqual(result, [])


class TestReadTrajectoriesMissingColumns(unittest.TestCase):
    """read_trajectories — missing columns default to None."""

    def test_missing_reward_columns_default_to_none(self) -> None:
        """Records without reward columns have None for those fields."""
        with tempfile.TemporaryDirectory() as tmp:
            pq_path = Path(tmp, "data.parquet")
            # Write only minimal columns
            table = pa.table({
                "workspace_uuid": ["ws-1"],
                "rollout_session_id": ["sess-1"],
                "prompt_token_ids": [[1, 2]],
                "sampled_token_ids": [[3, 4]],
            })
            pq.write_table(table, str(pq_path))
            records = read_trajectories(tmp)

        self.assertEqual(len(records), 1)
        self.assertIsNone(records[0]["shaped_reward"])
        self.assertIsNone(records[0]["evaluation_reward"])
        self.assertIsNone(records[0]["logprobs"])

    def test_all_optional_fields_present_when_in_file(self) -> None:
        """All standardised fields are read when present."""
        with tempfile.TemporaryDirectory() as tmp:
            pq_path = Path(tmp, "full.parquet")
            row = _make_record(shaped_reward=0.5)
            _write_parquet(pq_path, [row])
            records = read_trajectories(tmp)

        self.assertEqual(len(records), 1)
        rec = records[0]
        self.assertEqual(rec["rollout_session_id"], "sess-001")
        self.assertEqual(rec["shaped_reward"], 0.5)
        self.assertEqual(rec["prompt_token_ids"], [1, 2, 3])

    def test_missing_all_optional_columns(self) -> None:
        """A table with only uuid + session id yields records with None elsewhere."""
        with tempfile.TemporaryDirectory() as tmp:
            pq_path = Path(tmp, "minimal.parquet")
            table = pa.table({"workspace_uuid": ["x"], "rollout_session_id": ["y"]})
            pq.write_table(table, str(pq_path))
            records = read_trajectories(tmp)

        self.assertEqual(len(records), 1)
        for field in ("prompt_token_ids", "sampled_token_ids", "shaped_reward",
                       "evaluation_reward", "logprobs", "finish_reason", "timestamp_ns"):
            self.assertIsNone(records[0][field])


class TestReadTrajectoriesValid(unittest.TestCase):
    """read_trajectories — valid Parquet files are read correctly."""

    def test_multiple_files_merged(self) -> None:
        """Records from multiple .parquet files are merged into one list."""
        with tempfile.TemporaryDirectory() as tmp:
            for i in range(3):
                _write_parquet(
                    Path(tmp, f"shard_{i}.parquet"),
                    [_make_record(session_id=f"sess-{i}", shaped_reward=float(i))],
                )
            records = read_trajectories(tmp)
        self.assertEqual(len(records), 3)

    def test_recursive_glob(self) -> None:
        """Files nested in subdirectories are discovered."""
        with tempfile.TemporaryDirectory() as tmp:
            sub = Path(tmp, "2024", "01")
            sub.mkdir(parents=True)
            _write_parquet(sub / "data.parquet", [_make_record(shaped_reward=0.3)])
            records = read_trajectories(tmp)
        self.assertEqual(len(records), 1)

    def test_field_types_preserved(self) -> None:
        """Token id lists are returned as Python lists."""
        with tempfile.TemporaryDirectory() as tmp:
            _write_parquet(
                Path(tmp, "t.parquet"),
                [_make_record(prompt=[10, 20, 30], sampled=[40, 50], shaped_reward=0.7)],
            )
            records = read_trajectories(tmp)
        self.assertIsInstance(records[0]["prompt_token_ids"], list)
        self.assertIsInstance(records[0]["sampled_token_ids"], list)


class TestBuildGrpoDataset(unittest.TestCase):
    """build_grpo_dataset — format, filtering, and stats."""

    def setUp(self) -> None:
        self.tmp = tempfile.mkdtemp()

    def tearDown(self) -> None:
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _load_jsonl(self, filename: str) -> list[dict]:
        out_file = Path(self.tmp) / filename
        with out_file.open() as fh:
            return [json.loads(line) for line in fh if line.strip()]

    def test_output_file_created(self) -> None:
        """grpo_dataset.jsonl is created in output_path."""
        trajectories = [_make_record(shaped_reward=0.4)]
        build_grpo_dataset(trajectories, self.tmp)
        self.assertTrue((Path(self.tmp) / "grpo_dataset.jsonl").exists())

    def test_grpo_fields_present(self) -> None:
        """Each GRPO entry has required fields."""
        trajectories = [_make_record(shaped_reward=0.5)]
        build_grpo_dataset(trajectories, self.tmp)
        rows = self._load_jsonl("grpo_dataset.jsonl")
        self.assertEqual(len(rows), 1)
        row = rows[0]
        for field in ("prompt_token_ids", "completion_token_ids", "reward", "session_id"):
            self.assertIn(field, row)

    def test_negative_rewards_included_in_grpo(self) -> None:
        """Negative rewards are included in GRPO (all rewards used for RL)."""
        trajectories = [
            _make_record(session_id="a", shaped_reward=-0.5),
            _make_record(session_id="b", shaped_reward=0.8),
        ]
        result = build_grpo_dataset(trajectories, self.tmp)
        self.assertEqual(result["count"], 2)

    def test_missing_reward_excluded_from_grpo(self) -> None:
        """Records with no reward field are excluded."""
        trajectories = [
            _make_record(session_id="a", shaped_reward=None, evaluation_reward=None),
            _make_record(session_id="b", shaped_reward=0.6),
        ]
        result = build_grpo_dataset(trajectories, self.tmp)
        self.assertEqual(result["count"], 1)

    def test_session_grouping_keeps_best_reward(self) -> None:
        """Multiple records per session → only the one with highest reward is kept."""
        trajectories = [
            _make_record(session_id="shared", shaped_reward=0.2),
            _make_record(session_id="shared", shaped_reward=0.9),
            _make_record(session_id="shared", shaped_reward=-0.3),
        ]
        result = build_grpo_dataset(trajectories, self.tmp)
        rows = self._load_jsonl("grpo_dataset.jsonl")
        self.assertEqual(result["count"], 1)
        self.assertAlmostEqual(rows[0]["reward"], 0.9)

    def test_reward_stats_correctness(self) -> None:
        """reward_stats min/max/mean are correct."""
        trajectories = [
            _make_record(session_id="s1", shaped_reward=-1.0),
            _make_record(session_id="s2", shaped_reward=0.0),
            _make_record(session_id="s3", shaped_reward=1.0),
        ]
        result = build_grpo_dataset(trajectories, self.tmp)
        stats = result["reward_stats"]
        self.assertAlmostEqual(stats["min"], -1.0)
        self.assertAlmostEqual(stats["max"], 1.0)
        self.assertAlmostEqual(stats["mean"], 0.0)

    def test_empty_trajectories_grpo_count_zero(self) -> None:
        """Empty trajectory list → count=0."""
        result = build_grpo_dataset([], self.tmp)
        self.assertEqual(result["count"], 0)

    def test_reward_fallback_to_evaluation_reward(self) -> None:
        """evaluation_reward is used when shaped_reward is None."""
        trajectories = [_make_record(shaped_reward=None, evaluation_reward=0.7)]
        result = build_grpo_dataset(trajectories, self.tmp)
        self.assertEqual(result["count"], 1)
        rows = self._load_jsonl("grpo_dataset.jsonl")
        self.assertAlmostEqual(rows[0]["reward"], 0.7)


class TestBuildSftDataset(unittest.TestCase):
    """build_sft_dataset — positive-reward filtering and format."""

    def setUp(self) -> None:
        self.tmp = tempfile.mkdtemp()

    def tearDown(self) -> None:
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _load_jsonl(self, filename: str) -> list[dict]:
        with (Path(self.tmp) / filename).open() as fh:
            return [json.loads(line) for line in fh if line.strip()]

    def test_negative_rewards_excluded_by_default(self) -> None:
        """Records with reward < 0.0 are not in SFT dataset."""
        trajectories = [
            _make_record(session_id="neg", shaped_reward=-0.5),
            _make_record(session_id="pos", shaped_reward=0.5),
        ]
        result = build_sft_dataset(trajectories, self.tmp)
        self.assertEqual(result["count"], 1)
        rows = self._load_jsonl("sft_dataset.jsonl")
        self.assertEqual(rows[0]["session_id"], "pos")

    def test_zero_reward_included_by_default(self) -> None:
        """Reward == 0.0 meets the default threshold and is included."""
        trajectories = [_make_record(shaped_reward=0.0)]
        result = build_sft_dataset(trajectories, self.tmp)
        self.assertEqual(result["count"], 1)

    def test_custom_min_reward_threshold(self) -> None:
        """custom min_reward=0.5 excludes records below threshold."""
        trajectories = [
            _make_record(session_id="low", shaped_reward=0.3),
            _make_record(session_id="high", shaped_reward=0.8),
        ]
        result = build_sft_dataset(trajectories, self.tmp, min_reward=0.5)
        self.assertEqual(result["count"], 1)
        self.assertEqual(result["reward_threshold"], 0.5)

    def test_sft_fields_present(self) -> None:
        """Each SFT entry has input_token_ids, output_token_ids, session_id."""
        trajectories = [_make_record(shaped_reward=0.6)]
        build_sft_dataset(trajectories, self.tmp)
        rows = self._load_jsonl("sft_dataset.jsonl")
        row = rows[0]
        for field in ("input_token_ids", "output_token_ids", "session_id"):
            self.assertIn(field, row)

    def test_missing_reward_excluded_from_sft(self) -> None:
        """Records with no reward are excluded (None < 0.0 threshold treated as missing)."""
        trajectories = [
            _make_record(session_id="no-reward", shaped_reward=None, evaluation_reward=None),
            _make_record(session_id="has-reward", shaped_reward=0.4),
        ]
        result = build_sft_dataset(trajectories, self.tmp)
        self.assertEqual(result["count"], 1)

    def test_empty_trajectories_sft_count_zero(self) -> None:
        """Empty trajectory list → count=0."""
        result = build_sft_dataset([], self.tmp)
        self.assertEqual(result["count"], 0)

    def test_output_file_created(self) -> None:
        """sft_dataset.jsonl is created in output_path."""
        build_sft_dataset([], self.tmp)
        self.assertTrue((Path(self.tmp) / "sft_dataset.jsonl").exists())


class TestBuildDatasetEndToEnd(unittest.TestCase):
    """build_dataset — end-to-end integration with temp Parquet store."""

    def setUp(self) -> None:
        self.store = tempfile.mkdtemp()
        self.output = tempfile.mkdtemp()

    def tearDown(self) -> None:
        import shutil
        shutil.rmtree(self.store, ignore_errors=True)
        shutil.rmtree(self.output, ignore_errors=True)

    def _write_store(self, rows: list[dict]) -> None:
        _write_parquet(Path(self.store) / "data.parquet", rows)

    def test_end_to_end_combined_result(self) -> None:
        """build_dataset returns grpo + sft + total_trajectories + manifest_path."""
        rows = [
            _make_record(session_id="s1", shaped_reward=0.8),
            _make_record(session_id="s2", shaped_reward=-0.3),
        ]
        self._write_store(rows)
        result = build_dataset(self.store, self.output)

        self.assertIn("grpo", result)
        self.assertIn("sft", result)
        self.assertEqual(result["total_trajectories"], 2)
        self.assertIn("manifest_path", result)

    def test_manifest_json_written(self) -> None:
        """dataset_manifest.json is written to output_path."""
        self._write_store([_make_record(shaped_reward=0.5)])
        build_dataset(self.store, self.output)
        manifest_file = Path(self.output) / "dataset_manifest.json"
        self.assertTrue(manifest_file.exists())
        with manifest_file.open() as fh:
            manifest = json.load(fh)
        self.assertIn("grpo", manifest)
        self.assertIn("sft", manifest)

    def test_manifest_includes_provenance(self) -> None:
        """dataset_manifest.json contains provenance: store_path, output_path, generated_at."""
        self._write_store([_make_record(shaped_reward=0.5)])
        build_dataset(self.store, self.output)
        with (Path(self.output) / "dataset_manifest.json").open() as fh:
            manifest = json.load(fh)
        prov = manifest["provenance"]
        self.assertIn("store_path", prov)
        self.assertIn("output_path", prov)
        self.assertIn("generated_at", prov)

    def test_idempotency_overwrites_not_appends(self) -> None:
        """Calling build_dataset twice does not append — files are overwritten."""
        self._write_store([_make_record(shaped_reward=0.5)])
        build_dataset(self.store, self.output)
        result2 = build_dataset(self.store, self.output)
        # Count should still be 1, not 2
        self.assertEqual(result2["grpo"]["count"], 1)
        self.assertEqual(result2["sft"]["count"], 1)

    def test_empty_store_yields_zero_counts(self) -> None:
        """Empty store → GRPO and SFT both have count=0."""
        result = build_dataset(self.store, self.output)
        self.assertEqual(result["grpo"]["count"], 0)
        self.assertEqual(result["sft"]["count"], 0)
        self.assertEqual(result["total_trajectories"], 0)

    def test_reward_stats_in_manifest(self) -> None:
        """Manifest carries reward_stats under grpo."""
        rows = [
            _make_record(session_id="a", shaped_reward=-0.5),
            _make_record(session_id="b", shaped_reward=0.5),
        ]
        self._write_store(rows)
        build_dataset(self.store, self.output)
        with (Path(self.output) / "dataset_manifest.json").open() as fh:
            manifest = json.load(fh)
        stats = manifest["grpo"]["reward_stats"]
        self.assertAlmostEqual(stats["min"], -0.5)
        self.assertAlmostEqual(stats["max"], 0.5)
        self.assertAlmostEqual(stats["mean"], 0.0)

    def test_sft_only_positive_rewards_from_store(self) -> None:
        """SFT count reflects only positive-reward records from store."""
        rows = [
            _make_record(session_id="pos1", shaped_reward=0.8),
            _make_record(session_id="pos2", shaped_reward=0.3),
            _make_record(session_id="neg1", shaped_reward=-0.6),
        ]
        self._write_store(rows)
        result = build_dataset(self.store, self.output)
        self.assertEqual(result["sft"]["count"], 2)
        self.assertEqual(result["grpo"]["count"], 3)

    def test_grpo_session_deduplication_in_end_to_end(self) -> None:
        """Duplicate session entries in Parquet → single GRPO entry per session."""
        rows = [
            _make_record(session_id="dup", shaped_reward=0.2),
            _make_record(session_id="dup", shaped_reward=0.9),
        ]
        self._write_store(rows)
        result = build_dataset(self.store, self.output)
        self.assertEqual(result["grpo"]["count"], 1)

    def test_empty_reward_stats_when_no_grpo_records(self) -> None:
        """When no records have reward, reward_stats contains None values."""
        rows = [_make_record(shaped_reward=None, evaluation_reward=None)]
        self._write_store(rows)
        result = build_dataset(self.store, self.output)
        stats = result["grpo"]["reward_stats"]
        self.assertIsNone(stats["min"])
        self.assertIsNone(stats["max"])
        self.assertIsNone(stats["mean"])

    def test_custom_min_reward_forwarded(self) -> None:
        """min_reward kwarg is forwarded to build_sft_dataset."""
        rows = [
            _make_record(session_id="low", shaped_reward=0.2),
            _make_record(session_id="high", shaped_reward=0.9),
        ]
        self._write_store(rows)
        result = build_dataset(self.store, self.output, min_reward=0.5)
        self.assertEqual(result["sft"]["count"], 1)
        self.assertEqual(result["sft"]["reward_threshold"], 0.5)


if __name__ == "__main__":
    unittest.main()
