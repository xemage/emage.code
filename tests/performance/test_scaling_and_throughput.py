"""Scaling and throughput benchmark for verify/sync script envelopes."""
from __future__ import annotations

import json
import os
import shutil
import statistics
import subprocess
import tempfile
import time
import unittest
from pathlib import Path

from tests._helpers.repo import implementation_root, repo_root


FIXTURE_PATH = Path("tests/fixtures/benchmarks/scaling_cases.json")
THRESHOLD_PATH = Path("tests/_baselines/benchmark-thresholds-v1.json")


def _load_json(path: Path) -> dict:
    return json.loads((repo_root() / path).read_text(encoding="utf-8"))


def _percentile(values: list[float], percentile: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    index = (len(ordered) - 1) * percentile
    low = int(index)
    high = min(low + 1, len(ordered) - 1)
    weight = index - low
    return ordered[low] * (1.0 - weight) + ordered[high] * weight


def _coefficient_of_variation(values: list[float]) -> float:
    if not values:
        return 0.0
    mean_value = statistics.fmean(values)
    if mean_value == 0:
        return 0.0
    if len(values) < 2:
        return 0.0
    return statistics.stdev(values) / mean_value


class TestScalingAndThroughput(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not shutil.which("node"):
            raise unittest.SkipTest("node not available on PATH")
        cls.dataset = _load_json(FIXTURE_PATH)
        cls.thresholds = _load_json(THRESHOLD_PATH)["scaling_and_throughput"]
        cls.stress_mode = os.getenv("BENCH_STRESS", "0") == "1"

    def _run_case(self, case: dict) -> tuple[list[float], str, str]:
        warmups = int(case.get("warmup_runs", 0))
        iterations = int(case["stress_iterations"] if self.stress_mode else case["default_iterations"])
        script = case["script"]
        workdir_mode = case["workdir"]

        def run_once(cwd: Path) -> tuple[float, str, str, int]:
            t0 = time.monotonic()
            proc = subprocess.run(["node", script], cwd=cwd, capture_output=True, text=True)
            elapsed = time.monotonic() - t0
            return elapsed, proc.stdout, proc.stderr, proc.returncode

        samples: list[float] = []
        last_stdout = ""
        last_stderr = ""

        if workdir_mode == "temp_copy":
            with tempfile.TemporaryDirectory() as tmp:
                tmp_path = Path(tmp) / "impl"
                shutil.copytree(implementation_root(), tmp_path, symlinks=False)
                for _ in range(warmups):
                    _, last_stdout, last_stderr, code = run_once(tmp_path)
                    self.assertEqual(code, 0, f"{script} warmup failed:\n{last_stdout}\n{last_stderr}")
                for _ in range(iterations):
                    elapsed, last_stdout, last_stderr, code = run_once(tmp_path)
                    self.assertEqual(code, 0, f"{script} run failed:\n{last_stdout}\n{last_stderr}")
                    samples.append(elapsed)
        else:
            cwd = implementation_root()
            for _ in range(warmups):
                _, last_stdout, last_stderr, code = run_once(cwd)
                self.assertEqual(code, 0, f"{script} warmup failed:\n{last_stdout}\n{last_stderr}")
            for _ in range(iterations):
                elapsed, last_stdout, last_stderr, code = run_once(cwd)
                self.assertEqual(code, 0, f"{script} run failed:\n{last_stdout}\n{last_stderr}")
                samples.append(elapsed)

        return samples, last_stdout, last_stderr

    def test_scaling_and_throughput_envelope(self):
        cases = self.dataset["cases"]
        self.assertGreater(len(cases), 0, "scaling dataset has no cases")

        print(f"\n[scaling-and-throughput] stress_mode={self.stress_mode}")
        for case in cases:
            with self.subTest(case=case["id"]):
                samples, _, _ = self._run_case(case)
                self.assertGreater(len(samples), 0, f"{case['id']} produced no timing samples")

                p50 = _percentile(samples, 0.50)
                p95 = _percentile(samples, 0.95)
                cv = _coefficient_of_variation(samples)

                key = case["threshold_key"]
                baseline_case = self.thresholds[key]
                max_p95 = min(float(case["max_p95_seconds"]), float(baseline_case["max_p95_seconds"]))
                max_cv = min(
                    float(case["max_coefficient_of_variation"]),
                    float(baseline_case["max_coefficient_of_variation"]),
                )

                print(
                    "  "
                    f"{case['id']}: n={len(samples)} "
                    f"p50={p50:.3f}s p95={p95:.3f}s cv={cv:.3f} "
                    f"(max p95={max_p95:.3f}s, max cv={max_cv:.3f})"
                )

                self.assertLessEqual(
                    p95,
                    max_p95,
                    msg=f"{case['id']} p95 {p95:.3f}s exceeds {max_p95:.3f}s",
                )
                self.assertLessEqual(
                    cv,
                    max_cv,
                    msg=f"{case['id']} coefficient_of_variation {cv:.3f} exceeds {max_cv:.3f}",
                )


if __name__ == "__main__":
    unittest.main()
