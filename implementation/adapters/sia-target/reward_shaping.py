#!/usr/bin/env python3
"""
T225: Reward Shaping

This module blends two independent reward sources captured during a SIA
generation into a single, bounded, deterministic shaped reward used for
downstream training (GRPO / SFT):

1. merge_signal: The CWSO merge state-machine outcome (T224). Mapped to a
   binary ±1 signal: +1.0 when the trajectory merged cleanly, -1.0 when the
   merge failed or hit a conflict.
2. eval_component: The SIA task evaluation metric (T222) - the normalized
   ``overall_score`` in [0, 1] read from ``results.json``. Re-centered to
   [-1, +1] so it shares the same scale as merge_signal.

Shaped reward formula (deterministic, bounded to [-1, 1]):

    eval_component = 2 * clamp(eval_metric, 0, 1) - 1
    shaped = clamp(w_merge * merge_signal + w_eval * eval_component, -1, 1)

By default w_merge = w_eval = 0.5 and the weights are normalized so that
``w_merge + w_eval == 1.0``. Because both components live in [-1, 1] and the
normalized weights are convex, the blended value is already within [-1, 1];
the final clamp is a defensive guard.

Environment Variables:
- REWARD_SHAPING_W_MERGE (default: 0.5): weight applied to the merge signal
- REWARD_SHAPING_W_EVAL  (default: 0.5): weight applied to the eval component

Degenerate-case behavior:
- Missing / None eval metric  -> eval_component contributes 0 (neutral), warn
- Non-numeric eval metric      -> eval_component contributes 0 (neutral), warn
- eval metric outside [0, 1]   -> clamp to [0, 1], warn (mirrors T224)
- Failed / missing merge       -> merge_signal = -1.0
"""

import logging
import math
import os
from typing import Any, Dict, Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Default blend weights. Both components are pre-scaled to [-1, 1].
DEFAULT_W_MERGE = 0.5
DEFAULT_W_EVAL = 0.5

# Environment overrides for the blend weights.
ENV_W_MERGE = "REWARD_SHAPING_W_MERGE"
ENV_W_EVAL = "REWARD_SHAPING_W_EVAL"


def _clamp(value: float, low: float, high: float) -> float:
    """Clamp ``value`` into the inclusive range [low, high]."""
    return max(low, min(high, value))


def _resolve_weight(explicit: Optional[float], env_var: str, default: float) -> float:
    """
    Resolve a single weight from (in priority order): explicit arg, env var,
    default. The resolved value must be finite and non-negative.

    Args:
        explicit: Caller-provided weight (None to defer to env/default)
        env_var: Environment variable name to consult when explicit is None
        default: Fallback weight when neither explicit nor env is provided

    Returns:
        A finite, non-negative weight.

    Raises:
        ValueError: If the resolved weight is non-finite or negative.
    """
    if explicit is not None:
        weight = float(explicit)
    elif os.getenv(env_var) is not None:
        try:
            weight = float(os.environ[env_var])
        except ValueError as exc:
            raise ValueError(
                f"{env_var}={os.environ[env_var]!r} is not a valid float"
            ) from exc
    else:
        weight = float(default)

    if not math.isfinite(weight) or weight < 0.0:
        raise ValueError(
            f"Weight from {env_var} must be finite and non-negative, got {weight}"
        )
    return weight


def resolve_weights(
    w_merge: Optional[float] = None,
    w_eval: Optional[float] = None
) -> Dict[str, float]:
    """
    Resolve and normalize the blend weights.

    Resolution order per weight: explicit arg > env var > default. The two
    weights are then normalized so they sum to 1.0. If both resolve to 0.0
    (degenerate), the defaults are restored before normalization.

    Args:
        w_merge: Explicit merge weight (None -> env REWARD_SHAPING_W_MERGE -> 0.5)
        w_eval: Explicit eval weight (None -> env REWARD_SHAPING_W_EVAL -> 0.5)

    Returns:
        {"w_merge": float, "w_eval": float} with w_merge + w_eval == 1.0
    """
    merge = _resolve_weight(w_merge, ENV_W_MERGE, DEFAULT_W_MERGE)
    evaluation = _resolve_weight(w_eval, ENV_W_EVAL, DEFAULT_W_EVAL)

    total = merge + evaluation
    if total == 0.0:
        logger.warning(
            "Both shaping weights resolved to 0.0; restoring defaults "
            f"(w_merge={DEFAULT_W_MERGE}, w_eval={DEFAULT_W_EVAL})"
        )
        merge, evaluation = DEFAULT_W_MERGE, DEFAULT_W_EVAL
        total = merge + evaluation

    return {"w_merge": merge / total, "w_eval": evaluation / total}


def compute_merge_signal(merge_result: Optional[Dict[str, Any]]) -> float:
    """
    Derive the ±1 merge signal from a CWSO MergeResult.

    Args:
        merge_result: MergeResult from attach_reward_via_merge(), expected to
            contain a boolean ``merged`` field. None or a missing/falsy
            ``merged`` is treated as a failed merge.

    Returns:
        +1.0 when merged is True, -1.0 otherwise.
    """
    if not merge_result or not merge_result.get("merged", False):
        logger.warning("Merge did not succeed (merged is falsy); signal = -1.0")
        return -1.0
    return 1.0


def compute_eval_component(eval_metric: Optional[float]) -> float:
    """
    Re-center the normalized eval metric from [0, 1] to [-1, 1].

    Args:
        eval_metric: Normalized ``overall_score`` in [0, 1], or None.

    Returns:
        2 * clamp(eval_metric, 0, 1) - 1, or 0.0 (neutral) when the metric is
        missing/None or non-numeric. Out-of-range metrics are clamped with a
        warning.
    """
    if eval_metric is None:
        logger.warning("eval_metric is None; eval component is neutral (0.0)")
        return 0.0

    try:
        metric = float(eval_metric)
    except (TypeError, ValueError):
        logger.warning(
            f"eval_metric {eval_metric!r} is not numeric; "
            "eval component is neutral (0.0)"
        )
        return 0.0

    if not math.isfinite(metric):
        logger.warning("eval_metric is non-finite; eval component is neutral (0.0)")
        return 0.0

    if not 0.0 <= metric <= 1.0:
        logger.warning(f"eval_metric {metric} outside [0, 1]; clamping")
        metric = _clamp(metric, 0.0, 1.0)

    return 2.0 * metric - 1.0


def shape_reward(
    merge_signal: float,
    eval_component: float,
    w_merge: float,
    w_eval: float
) -> float:
    """
    Blend the (already scaled) components into a bounded shaped reward.

    Pure and deterministic: identical inputs always yield identical output.

    Args:
        merge_signal: Merge signal in [-1, 1] (from compute_merge_signal)
        eval_component: Eval component in [-1, 1] (from compute_eval_component)
        w_merge: Normalized merge weight
        w_eval: Normalized eval weight

    Returns:
        Shaped reward clamped to [-1, 1].
    """
    blended = w_merge * merge_signal + w_eval * eval_component
    return _clamp(blended, -1.0, 1.0)


def shape_reward_for_session(
    merge_result: Optional[Dict[str, Any]],
    evaluation: Optional[Dict[str, Any]],
    w_merge: Optional[float] = None,
    w_eval: Optional[float] = None
) -> Dict[str, Any]:
    """
    Compute the shaped reward record for a completed SIA session.

    This is the main T225 entry point. It combines the CWSO MergeResult (T224)
    and the evaluation result (T222) into a single record suitable for
    attaching to the trajectory used in downstream training.

    Args:
        merge_result: MergeResult dict (``merged`` flag). None -> failed merge.
        evaluation: Evaluation dict with ``overall_score`` in [0, 1]. None or a
            missing score -> neutral eval component.
        w_merge: Optional merge weight override (env/default otherwise)
        w_eval: Optional eval weight override (env/default otherwise)

    Returns:
        {
            "shaped_reward": float in [-1, 1],
            "merge_signal": float (+1.0 or -1.0),
            "eval_component": float in [-1, 1],
            "eval_metric": Optional[float] (the raw normalized score, if any),
            "weights": {"w_merge": float, "w_eval": float},
        }
    """
    weights = resolve_weights(w_merge, w_eval)

    eval_metric = evaluation.get("overall_score") if evaluation else None
    merge_signal = compute_merge_signal(merge_result)
    eval_component = compute_eval_component(eval_metric)

    shaped = shape_reward(
        merge_signal, eval_component, weights["w_merge"], weights["w_eval"]
    )

    record = {
        "shaped_reward": shaped,
        "merge_signal": merge_signal,
        "eval_component": eval_component,
        "eval_metric": eval_metric,
        "weights": weights,
    }

    logger.info(
        f"Shaped reward computed: shaped={shaped:.4f}, "
        f"merge_signal={merge_signal:+.1f}, eval_component={eval_component:+.4f}, "
        f"weights=(merge={weights['w_merge']:.3f}, eval={weights['w_eval']:.3f})"
    )
    return record


if __name__ == "__main__":
    # Example usage (for testing/demonstration)
    demo_merge = {"merged": True, "trajectory_id": "traj-demo-001"}
    demo_eval = {"overall_score": 0.9, "passed": True}

    demo_record = shape_reward_for_session(demo_merge, demo_eval)
    print(demo_record)
