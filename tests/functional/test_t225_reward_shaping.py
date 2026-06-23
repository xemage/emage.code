"""Functional tests for Task T225: Reward Shaping."""
from __future__ import annotations

import importlib.util
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

# Add implementation directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "implementation" / "adapters"))

# Import from reward_shaping module via importlib spec (mirrors T224 style)
reward_shaping_path = (
    Path(__file__).parent.parent.parent
    / "implementation" / "adapters" / "sia-target" / "reward_shaping.py"
)
spec = importlib.util.spec_from_file_location("reward_shaping", reward_shaping_path)
reward_shaping = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reward_shaping)

# Register in sys.modules for patching
sys.modules["reward_shaping"] = reward_shaping

# Extract functions
resolve_weights = reward_shaping.resolve_weights
compute_merge_signal = reward_shaping.compute_merge_signal
compute_eval_component = reward_shaping.compute_eval_component
shape_reward = reward_shaping.shape_reward
shape_reward_for_session = reward_shaping.shape_reward_for_session


class TestComponentDerivation(unittest.TestCase):
    """Test suite for deriving the merge signal and eval component."""

    def test_merge_signal_success(self) -> None:
        """merged=True yields +1.0."""
        self.assertEqual(compute_merge_signal({"merged": True}), 1.0)

    def test_merge_signal_failure(self) -> None:
        """merged=False yields -1.0."""
        self.assertEqual(compute_merge_signal({"merged": False}), -1.0)

    def test_merge_signal_missing_flag(self) -> None:
        """Missing 'merged' flag is treated as failure (-1.0)."""
        self.assertEqual(compute_merge_signal({"trajectory_id": "x"}), -1.0)

    def test_merge_signal_none(self) -> None:
        """None merge_result is treated as failure (-1.0)."""
        self.assertEqual(compute_merge_signal(None), -1.0)

    def test_eval_component_zero_boundary(self) -> None:
        """overall_score 0.0 maps to -1.0."""
        self.assertEqual(compute_eval_component(0.0), -1.0)

    def test_eval_component_half_boundary(self) -> None:
        """overall_score 0.5 maps to 0.0 (neutral midpoint)."""
        self.assertEqual(compute_eval_component(0.5), 0.0)

    def test_eval_component_one_boundary(self) -> None:
        """overall_score 1.0 maps to +1.0."""
        self.assertEqual(compute_eval_component(1.0), 1.0)

    def test_eval_component_missing_is_neutral(self) -> None:
        """None metric yields neutral 0.0 contribution."""
        self.assertEqual(compute_eval_component(None), 0.0)

    def test_eval_component_clamps_above_range(self) -> None:
        """Metric > 1.0 is clamped to 1.0 -> component +1.0."""
        self.assertEqual(compute_eval_component(1.5), 1.0)

    def test_eval_component_clamps_below_range(self) -> None:
        """Metric < 0.0 is clamped to 0.0 -> component -1.0."""
        self.assertEqual(compute_eval_component(-0.5), -1.0)

    def test_eval_component_non_finite_is_neutral(self) -> None:
        """NaN/inf metric yields neutral 0.0 contribution."""
        self.assertEqual(compute_eval_component(float("nan")), 0.0)
        self.assertEqual(compute_eval_component(float("inf")), 0.0)

    def test_eval_component_non_numeric_is_neutral(self) -> None:
        """Non-numeric metric yields neutral 0.0 without raising (mirrors T224)."""
        self.assertEqual(compute_eval_component("not-a-number"), 0.0)


class TestWeightResolution(unittest.TestCase):
    """Test suite for weight resolution and normalization."""

    def test_default_weights(self) -> None:
        """Defaults are 0.5 / 0.5 and sum to 1.0."""
        weights = resolve_weights()
        self.assertAlmostEqual(weights["w_merge"], 0.5)
        self.assertAlmostEqual(weights["w_eval"], 0.5)
        self.assertAlmostEqual(weights["w_merge"] + weights["w_eval"], 1.0)

    def test_explicit_weights_are_normalized(self) -> None:
        """Explicit weights are normalized to sum to 1.0."""
        weights = resolve_weights(w_merge=3.0, w_eval=1.0)
        self.assertAlmostEqual(weights["w_merge"], 0.75)
        self.assertAlmostEqual(weights["w_eval"], 0.25)

    def test_env_var_override(self) -> None:
        """Environment variables override defaults."""
        with patch.dict(os.environ, {
            "REWARD_SHAPING_W_MERGE": "0.2",
            "REWARD_SHAPING_W_EVAL": "0.8",
        }):
            weights = resolve_weights()
        self.assertAlmostEqual(weights["w_merge"], 0.2)
        self.assertAlmostEqual(weights["w_eval"], 0.8)

    def test_explicit_overrides_env(self) -> None:
        """Explicit args take priority over env vars."""
        with patch.dict(os.environ, {
            "REWARD_SHAPING_W_MERGE": "0.9",
            "REWARD_SHAPING_W_EVAL": "0.1",
        }):
            weights = resolve_weights(w_merge=0.5, w_eval=0.5)
        self.assertAlmostEqual(weights["w_merge"], 0.5)
        self.assertAlmostEqual(weights["w_eval"], 0.5)

    def test_both_zero_restores_defaults(self) -> None:
        """Both weights 0.0 falls back to defaults to avoid divide-by-zero."""
        weights = resolve_weights(w_merge=0.0, w_eval=0.0)
        self.assertAlmostEqual(weights["w_merge"], 0.5)
        self.assertAlmostEqual(weights["w_eval"], 0.5)

    def test_negative_weight_raises(self) -> None:
        """Negative weights are rejected."""
        with self.assertRaises(ValueError):
            resolve_weights(w_merge=-1.0, w_eval=0.5)

    def test_non_finite_weight_raises(self) -> None:
        """Non-finite weights are rejected."""
        with self.assertRaises(ValueError):
            resolve_weights(w_merge=float("inf"), w_eval=0.5)

    def test_invalid_env_weight_raises(self) -> None:
        """Non-numeric env var weight raises ValueError."""
        with patch.dict(os.environ, {"REWARD_SHAPING_W_MERGE": "not-a-number"}):
            with self.assertRaises(ValueError):
                resolve_weights()


class TestShapedReward(unittest.TestCase):
    """Test suite for the blended shaped reward and session record."""

    def test_deterministic_output(self) -> None:
        """Same inputs produce identical output across repeated calls."""
        merge = {"merged": True}
        evaluation = {"overall_score": 0.73}
        first = shape_reward_for_session(merge, evaluation)
        second = shape_reward_for_session(merge, evaluation)
        self.assertEqual(first, second)

    def test_merge_success_high_eval_positive(self) -> None:
        """Successful merge + high eval yields strongly positive reward."""
        record = shape_reward_for_session({"merged": True}, {"overall_score": 1.0})
        # 0.5 * 1.0 + 0.5 * 1.0 = 1.0
        self.assertEqual(record["shaped_reward"], 1.0)
        self.assertEqual(record["merge_signal"], 1.0)
        self.assertEqual(record["eval_component"], 1.0)

    def test_merge_failure_low_eval_negative(self) -> None:
        """Failed merge + low eval yields strongly negative reward."""
        record = shape_reward_for_session({"merged": False}, {"overall_score": 0.0})
        # 0.5 * -1.0 + 0.5 * -1.0 = -1.0
        self.assertEqual(record["shaped_reward"], -1.0)
        self.assertEqual(record["merge_signal"], -1.0)
        self.assertEqual(record["eval_component"], -1.0)

    def test_merge_success_eval_failure_cancels(self) -> None:
        """Merge success but worst eval cancels to 0 under equal weights."""
        record = shape_reward_for_session({"merged": True}, {"overall_score": 0.0})
        # 0.5 * 1.0 + 0.5 * -1.0 = 0.0
        self.assertEqual(record["shaped_reward"], 0.0)

    def test_missing_eval_uses_merge_only(self) -> None:
        """Missing eval metric leaves merge signal weighted by w_merge."""
        record = shape_reward_for_session({"merged": True}, None)
        # eval component neutral (0); 0.5 * 1.0 + 0.5 * 0.0 = 0.5
        self.assertEqual(record["eval_component"], 0.0)
        self.assertEqual(record["shaped_reward"], 0.5)
        self.assertIsNone(record["eval_metric"])

    def test_out_of_range_eval_clamped(self) -> None:
        """Out-of-range eval metric is clamped before blending."""
        record = shape_reward_for_session({"merged": True}, {"overall_score": 2.0})
        # clamp(2.0)->1.0 -> component 1.0; reward 1.0
        self.assertEqual(record["eval_component"], 1.0)
        self.assertEqual(record["shaped_reward"], 1.0)

    def test_reward_always_within_bounds(self) -> None:
        """Shaped reward stays within [-1, 1] across a grid of inputs."""
        for merged in (True, False):
            for score in (0.0, 0.25, 0.5, 0.75, 1.0, 1.5, -0.5):
                for wm, we in ((0.5, 0.5), (0.9, 0.1), (0.1, 0.9), (1.0, 0.0)):
                    record = shape_reward_for_session(
                        {"merged": merged}, {"overall_score": score},
                        w_merge=wm, w_eval=we
                    )
                    self.assertGreaterEqual(record["shaped_reward"], -1.0)
                    self.assertLessEqual(record["shaped_reward"], 1.0)

    def test_weight_configurability_changes_blend(self) -> None:
        """Heavier eval weight shifts reward toward the eval component."""
        merge = {"merged": False}  # merge_signal = -1.0
        evaluation = {"overall_score": 1.0}  # eval_component = +1.0
        eval_heavy = shape_reward_for_session(merge, evaluation, w_merge=0.0, w_eval=1.0)
        merge_heavy = shape_reward_for_session(merge, evaluation, w_merge=1.0, w_eval=0.0)
        self.assertEqual(eval_heavy["shaped_reward"], 1.0)
        self.assertEqual(merge_heavy["shaped_reward"], -1.0)

    def test_record_contains_expected_fields(self) -> None:
        """Session record exposes all documented fields."""
        record = shape_reward_for_session({"merged": True}, {"overall_score": 0.6})
        for key in ("shaped_reward", "merge_signal", "eval_component",
                    "eval_metric", "weights"):
            self.assertIn(key, record)
        self.assertIn("w_merge", record["weights"])
        self.assertIn("w_eval", record["weights"])

    def test_pure_shape_reward_clamps(self) -> None:
        """Pure shape_reward clamps an out-of-bounds blend to [-1, 1]."""
        # Non-normalized weights could exceed bounds; clamp guards it.
        self.assertEqual(shape_reward(1.0, 1.0, 2.0, 2.0), 1.0)
        self.assertEqual(shape_reward(-1.0, -1.0, 2.0, 2.0), -1.0)


if __name__ == "__main__":
    unittest.main()
