"""Unit tests for T234 per-generation cost/latency telemetry module."""
from __future__ import annotations

import time
import unittest

from implementation.runtime.telemetry.generation_telemetry import (
    BudgetConfig,
    GenerationBudgetMonitor,
    GenerationMetrics,
    LatencyTimer,
)


class TestGenerationMetrics(unittest.TestCase):
    def test_total_tokens_sums_prompt_and_sampled(self):
        m = GenerationMetrics(generation=1, prompt_tokens=100, sampled_tokens=50)
        self.assertEqual(m.total_tokens, 150)

    def test_total_latency_sums_proxy_and_sandbox(self):
        m = GenerationMetrics(generation=1, proxy_latency_ms=10.0, sandbox_runtime_ms=20.0)
        self.assertAlmostEqual(m.total_latency_ms, 30.0)

    def test_defaults_are_zero_and_reward_none(self):
        m = GenerationMetrics(generation=1)
        self.assertEqual(m.prompt_tokens, 0)
        self.assertEqual(m.sampled_tokens, 0)
        self.assertEqual(m.proxy_latency_ms, 0.0)
        self.assertEqual(m.sandbox_runtime_ms, 0.0)
        self.assertEqual(m.merge_ops, 0)
        self.assertIsNone(m.reward)

    def test_payload_contains_token_counts_not_raw_text(self):
        m = GenerationMetrics(generation=1, prompt_tokens=100, sampled_tokens=50)
        payload = m.to_telemetry_payload()
        self.assertIn("prompt_tokens", payload)
        self.assertIn("sampled_tokens", payload)
        # Must not include any field that could carry secrets or prompts
        for forbidden in ("prompt_text", "completion_text", "api_key", "secret", "token_ids"):
            self.assertNotIn(forbidden, payload)

    def test_payload_values_match_fields(self):
        m = GenerationMetrics(generation=3, prompt_tokens=80, sampled_tokens=40, reward=0.9)
        p = m.to_telemetry_payload()
        self.assertEqual(p["generation"], 3)
        self.assertEqual(p["prompt_tokens"], 80)
        self.assertEqual(p["sampled_tokens"], 40)
        self.assertAlmostEqual(p["reward"], 0.9)


class TestLatencyTimer(unittest.TestCase):
    def test_measures_elapsed_ms(self):
        with LatencyTimer() as t:
            time.sleep(0.015)
        self.assertGreater(t.elapsed_ms, 5.0)
        self.assertLess(t.elapsed_ms, 500.0)

    def test_elapsed_zero_before_exit(self):
        t = LatencyTimer()
        t.__enter__()
        # elapsed_ms is only updated on __exit__
        self.assertEqual(t.elapsed_ms, 0.0)
        t.__exit__(None, None, None)


class TestGenerationBudgetMonitor(unittest.TestCase):
    def _monitor(self, **cfg) -> GenerationBudgetMonitor:
        return GenerationBudgetMonitor(BudgetConfig(**cfg))

    def test_no_stop_with_default_config(self):
        m = self._monitor()
        m.record(GenerationMetrics(generation=1, prompt_tokens=100))
        stop, _ = m.should_stop()
        self.assertFalse(stop)

    # Token budget ----------------------------------------------------------------

    def test_token_budget_triggers_stop(self):
        m = self._monitor(max_total_tokens=200)
        m.record(GenerationMetrics(generation=1, prompt_tokens=100, sampled_tokens=101))
        stop, reason = m.should_stop()
        self.assertTrue(stop)
        self.assertIn("token budget exhausted", reason)

    def test_token_budget_not_hit_below_cap(self):
        m = self._monitor(max_total_tokens=300)
        m.record(GenerationMetrics(generation=1, prompt_tokens=100, sampled_tokens=50))
        stop, _ = m.should_stop()
        self.assertFalse(stop)

    def test_token_budget_zero_means_disabled(self):
        m = self._monitor(max_total_tokens=0)
        m.record(GenerationMetrics(generation=1, prompt_tokens=10_000_000))
        stop, _ = m.should_stop()
        self.assertFalse(stop)

    # Generation cap --------------------------------------------------------------

    def test_generation_cap_triggers_stop(self):
        m = self._monitor(max_generations=2)
        m.record(GenerationMetrics(generation=1))
        m.record(GenerationMetrics(generation=2))
        stop, reason = m.should_stop()
        self.assertTrue(stop)
        self.assertIn("generation cap reached", reason)

    def test_generation_cap_below_limit(self):
        m = self._monitor(max_generations=5)
        m.record(GenerationMetrics(generation=1))
        stop, _ = m.should_stop()
        self.assertFalse(stop)

    def test_generation_cap_zero_means_disabled(self):
        m = self._monitor(max_generations=0)
        for i in range(100):
            m.record(GenerationMetrics(generation=i + 1))
        stop, _ = m.should_stop()
        self.assertFalse(stop)

    # Reward plateau --------------------------------------------------------------

    def test_reward_plateau_detected(self):
        m = self._monitor(reward_plateau_window=3, reward_plateau_min_delta=0.001)
        for i, r in enumerate([0.8, 0.8001, 0.8002, 0.8001], start=1):
            m.record(GenerationMetrics(generation=i, reward=r))
        stop, reason = m.should_stop()
        self.assertTrue(stop)
        self.assertIn("plateau", reason)

    def test_no_plateau_when_improving(self):
        m = self._monitor(reward_plateau_window=3, reward_plateau_min_delta=0.001)
        for i, r in enumerate([0.5, 0.6, 0.7, 0.8], start=1):
            m.record(GenerationMetrics(generation=i, reward=r))
        stop, _ = m.should_stop()
        self.assertFalse(stop)

    def test_plateau_requires_full_window(self):
        m = self._monitor(reward_plateau_window=5, reward_plateau_min_delta=0.001)
        for i in range(4):
            m.record(GenerationMetrics(generation=i + 1, reward=0.8))
        stop, _ = m.should_stop()
        self.assertFalse(stop)

    def test_plateau_ignored_when_rewards_missing(self):
        """Plateau check skipped when recent records lack reward values."""
        m = self._monitor(reward_plateau_window=3, reward_plateau_min_delta=0.001)
        for i in range(5):
            m.record(GenerationMetrics(generation=i + 1))  # no reward
        stop, _ = m.should_stop()
        self.assertFalse(stop)

    # Aggregates ------------------------------------------------------------------

    def test_total_tokens_accumulates(self):
        m = self._monitor()
        m.record(GenerationMetrics(generation=1, prompt_tokens=100, sampled_tokens=50))
        m.record(GenerationMetrics(generation=2, prompt_tokens=80, sampled_tokens=40))
        self.assertEqual(m.total_tokens, 270)

    def test_generation_count(self):
        m = self._monitor()
        for i in range(5):
            m.record(GenerationMetrics(generation=i + 1))
        self.assertEqual(m.generation_count, 5)

    # Summary ---------------------------------------------------------------------

    def test_summary_structure_and_values(self):
        m = self._monitor()
        m.record(GenerationMetrics(
            generation=1,
            prompt_tokens=100,
            sampled_tokens=50,
            proxy_latency_ms=10.0,
            sandbox_runtime_ms=20.0,
            merge_ops=3,
            reward=0.75,
        ))
        s = m.summary()
        self.assertEqual(s["generation_count"], 1)
        self.assertEqual(s["total_tokens"], 150)
        self.assertAlmostEqual(s["total_proxy_latency_ms"], 10.0)
        self.assertAlmostEqual(s["total_sandbox_runtime_ms"], 20.0)
        self.assertEqual(s["total_merge_ops"], 3)
        self.assertAlmostEqual(s["mean_reward"], 0.75)
        self.assertFalse(s["should_stop"])
        self.assertEqual(s["stop_reason"], "")

    def test_summary_mean_reward_none_when_no_rewards(self):
        m = self._monitor()
        m.record(GenerationMetrics(generation=1, prompt_tokens=100))
        s = m.summary()
        self.assertIsNone(s["mean_reward"])

    def test_summary_reports_stop_reason(self):
        m = self._monitor(max_generations=1)
        m.record(GenerationMetrics(generation=1))
        s = m.summary()
        self.assertTrue(s["should_stop"])
        self.assertIn("generation cap reached", s["stop_reason"])
