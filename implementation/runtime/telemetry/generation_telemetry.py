"""Per-generation cost and latency telemetry for the CWSO self-improvement loop.

T234: Cost/latency telemetry per generation.

Collects token counts, proxy-added latency, sandbox runtime, and merge ops per
generation and emits a structured GenerationMetrics record.
A GenerationBudgetMonitor derives convergence / stop signals from accumulated
metrics.

Security:
- Only token *counts* are captured; no raw prompt text is stored.
- No provider API keys or secrets appear in any emitted record.
"""
from __future__ import annotations

import time
from dataclasses import asdict, dataclass, field
from typing import List, Optional, Tuple


# ---------------------------------------------------------------------------
# Core data class
# ---------------------------------------------------------------------------

@dataclass
class GenerationMetrics:
    """Telemetry record for a single generation step.

    Args:
        generation:          1-based generation index.
        prompt_tokens:       Number of tokens in the prompt (count only).
        sampled_tokens:      Number of tokens produced by the model.
        proxy_latency_ms:    End-to-end latency added by the rollout proxy (ms).
        sandbox_runtime_ms:  Time spent inside the sandbox / evaluation (ms).
        merge_ops:           Number of merge operations performed this step.
        reward:              Optional shaped reward from the evaluator.
    """

    generation: int
    prompt_tokens: int = 0
    sampled_tokens: int = 0
    proxy_latency_ms: float = 0.0
    sandbox_runtime_ms: float = 0.0
    merge_ops: int = 0
    reward: Optional[float] = None

    @property
    def total_tokens(self) -> int:
        """Total token usage (prompt + sampled)."""
        return self.prompt_tokens + self.sampled_tokens

    @property
    def total_latency_ms(self) -> float:
        """Combined end-to-end latency (proxy + sandbox)."""
        return self.proxy_latency_ms + self.sandbox_runtime_ms

    def to_telemetry_payload(self) -> dict:
        """Return a safe telemetry payload dict.

        Contains only numeric metrics and the generation index.
        No raw prompts, completions, API keys, or secrets are included.
        """
        return asdict(self)


# ---------------------------------------------------------------------------
# Latency helper
# ---------------------------------------------------------------------------

class LatencyTimer:
    """Context manager that measures elapsed wall-clock time in milliseconds.

    Usage::

        with LatencyTimer() as t:
            do_work()
        print(t.elapsed_ms)
    """

    def __init__(self) -> None:
        self._start: float = 0.0
        self.elapsed_ms: float = 0.0

    def __enter__(self) -> "LatencyTimer":
        self._start = time.perf_counter()
        return self

    def __exit__(self, *_: object) -> None:
        self.elapsed_ms = (time.perf_counter() - self._start) * 1_000.0


# ---------------------------------------------------------------------------
# Budget / convergence configuration
# ---------------------------------------------------------------------------

@dataclass
class BudgetConfig:
    """Thresholds that govern when the generation loop should stop.

    Zero values disable the corresponding check:

    * ``max_total_tokens``:       Stop when cumulative token count reaches this.
    * ``max_generations``:        Stop after this many generations.
    * ``reward_plateau_window``:  Number of consecutive generations to compare.
    * ``reward_plateau_min_delta``: Stop when all reward deltas in the window
                                    are below this threshold.
    """

    max_total_tokens: int = 0
    max_generations: int = 0
    reward_plateau_window: int = 3
    reward_plateau_min_delta: float = 0.001


# ---------------------------------------------------------------------------
# Budget monitor
# ---------------------------------------------------------------------------

class GenerationBudgetMonitor:
    """Accumulates per-generation metrics and emits convergence / stop signals.

    Does not store raw prompt text or secrets — only numeric statistics.

    Example::

        monitor = GenerationBudgetMonitor(BudgetConfig(max_total_tokens=100_000))
        monitor.record(metrics)
        stop, reason = monitor.should_stop()
    """

    def __init__(self, config: Optional[BudgetConfig] = None) -> None:
        self._config: BudgetConfig = config or BudgetConfig()
        self._history: List[GenerationMetrics] = []

    # ------------------------------------------------------------------
    # Recording
    # ------------------------------------------------------------------

    def record(self, metrics: GenerationMetrics) -> None:
        """Append a completed generation's metrics to the history."""
        self._history.append(metrics)

    # ------------------------------------------------------------------
    # Aggregates
    # ------------------------------------------------------------------

    @property
    def total_tokens(self) -> int:
        """Cumulative token count across all recorded generations."""
        return sum(m.total_tokens for m in self._history)

    @property
    def generation_count(self) -> int:
        """Number of generations recorded so far."""
        return len(self._history)

    # ------------------------------------------------------------------
    # Stop signal
    # ------------------------------------------------------------------

    def should_stop(self) -> Tuple[bool, str]:
        """Return ``(stop, reason)`` based on configured thresholds.

        Checks (in order):
        1. Token budget cap.
        2. Generation cap.
        3. Reward plateau.
        """
        cfg = self._config

        if cfg.max_total_tokens > 0 and self.total_tokens >= cfg.max_total_tokens:
            return True, (
                f"token budget exhausted: {self.total_tokens} >= {cfg.max_total_tokens}"
            )

        if cfg.max_generations > 0 and self.generation_count >= cfg.max_generations:
            return True, (
                f"generation cap reached: {self.generation_count} >= {cfg.max_generations}"
            )

        if cfg.reward_plateau_window > 0 and len(self._history) >= cfg.reward_plateau_window:
            recent_rewards = [
                m.reward
                for m in self._history[-cfg.reward_plateau_window :]
                if m.reward is not None
            ]
            if len(recent_rewards) == cfg.reward_plateau_window:
                deltas = [
                    abs(recent_rewards[i] - recent_rewards[i - 1])
                    for i in range(1, len(recent_rewards))
                ]
                if all(d < cfg.reward_plateau_min_delta for d in deltas):
                    return True, (
                        f"reward plateau detected over last {cfg.reward_plateau_window} "
                        f"generations (max_delta={max(deltas):.4f} < "
                        f"{cfg.reward_plateau_min_delta})"
                    )

        return False, ""

    # ------------------------------------------------------------------
    # Summary / dashboard input
    # ------------------------------------------------------------------

    def summary(self) -> dict:
        """Return an aggregated summary dict suitable for dashboard / reporting.

        Contains no raw prompts or secrets.
        """
        stop, reason = self.should_stop()
        rewards = [m.reward for m in self._history if m.reward is not None]
        return {
            "generation_count": self.generation_count,
            "total_tokens": self.total_tokens,
            "total_proxy_latency_ms": sum(m.proxy_latency_ms for m in self._history),
            "total_sandbox_runtime_ms": sum(m.sandbox_runtime_ms for m in self._history),
            "total_merge_ops": sum(m.merge_ops for m in self._history),
            "mean_reward": sum(rewards) / len(rewards) if rewards else None,
            "should_stop": stop,
            "stop_reason": reason,
        }
