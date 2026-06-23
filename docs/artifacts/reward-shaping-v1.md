# Artifact: reward-shaping-v1

**Design Document for SIA Reward Shaping (merge ±1 + `results.json` eval metric)**

## Metadata
- Producer: backend-developer (T225)
- Date: 2026-06-23
- Phase: Plan-009 Phase 2 (CWSO × SIA integration)
- Dependency: T222 (SIA `results.json` eval metric), T224 (reward attachment)
- Status: Implementation Complete
- Based on: docs/tasks/task-T225.md, implementation/adapters/sia-target/reward_attachment.py (T224), `results.json` evaluator (T222)

---

## Objective

Blend two independent reward sources captured during a SIA generation into a
single, bounded, deterministic **shaped reward** used for downstream training
(GRPO / SFT):

1. **merge_signal** — the CWSO merge state-machine outcome from T224. Mapped to
   a binary ±1 signal: `+1.0` when the trajectory merged cleanly
   (`merged == True`), `-1.0` when the merge failed or hit a conflict
   (`merged == False`).
2. **eval_component** — the SIA task evaluation metric from T222: the normalized
   `overall_score` in `[0, 1]` read from `results.json`, re-centered to
   `[-1, +1]` so it shares the same scale as `merge_signal`.

---

## Formula

```
eval_component = 2 * clamp(eval_metric, 0, 1) - 1
shaped         = clamp(w_merge * merge_signal + w_eval * eval_component, -1, 1)
```

The function is **pure and deterministic**: identical inputs always yield
identical output.

### `[0, 1] → [-1, 1]` Re-Centering Rationale

The SIA evaluator emits `overall_score` on a `[0, 1]` scale, whereas the merge
signal is a symmetric ±1 value. To combine them on a common axis, the eval
metric is affine-mapped with `2 * x - 1`:

- `0.0` (worst eval) → `-1.0` — penalizes the trajectory symmetrically with a
  failed merge.
- `0.5` (neutral eval) → `0.0` — contributes nothing to the blend, so the
  shaped reward is driven purely by the merge signal at the midpoint.
- `1.0` (best eval) → `+1.0` — rewards the trajectory symmetrically with a
  clean merge.

Without re-centering, a `[0, 1]` eval metric could never push the blend
negative, biasing the shaped reward upward. Re-centering keeps both components
zero-mean over their range, so equal weights produce an unbiased blend.

---

## Weights, Defaults & Normalization

| Weight | Default | Env override | Notes |
|--------|---------|--------------|-------|
| `w_merge` | `0.5` | `REWARD_SHAPING_W_MERGE` | weight on merge signal |
| `w_eval`  | `0.5` | `REWARD_SHAPING_W_EVAL`  | weight on eval component |

- Weights must be **finite and non-negative**; otherwise a `ValueError` is
  raised at the boundary.
- Weights are **normalized** so that `w_merge + w_eval == 1.0`. Because both
  components live in `[-1, 1]` and the normalized weights are convex, the blend
  is already inside `[-1, 1]`; the final `clamp` is a defensive guard against
  non-normalized direct calls to `shape_reward()`.
- If **both** weights resolve to `0.0` (degenerate), the defaults
  (`0.5 / 0.5`) are restored before normalization to avoid a divide-by-zero.

---

## Environment-Variable Overrides & Precedence

Resolution order **per weight**:

```
explicit function arg  >  environment variable  >  default
```

| Env var | Maps to | Default |
|---------|---------|---------|
| `REWARD_SHAPING_W_MERGE` | `w_merge` | `0.5` |
| `REWARD_SHAPING_W_EVAL`  | `w_eval`  | `0.5` |

A non-numeric env-var value (e.g. `REWARD_SHAPING_W_MERGE=abc`) raises a
`ValueError` rather than silently falling back, so misconfiguration fails fast.

---

## Worked Examples (default weights `w_merge = w_eval = 0.5`)

| merged | overall_score | merge_signal | eval_component | shaped_reward |
|--------|---------------|--------------|----------------|---------------|
| True   | 1.0           | +1.0         | +1.0           | **+1.0**      |
| True   | 0.5           | +1.0         | 0.0            | **+0.5**      |
| True   | 0.0           | +1.0         | -1.0           | **0.0**       |
| False  | 1.0           | -1.0         | +1.0           | **0.0**       |
| False  | 0.0           | -1.0         | -1.0           | **-1.0**      |

---

## Output Record Schema

`shape_reward_for_session(merge_result, evaluation, w_merge=None, w_eval=None)`
returns a record suitable for attaching to the trajectory:

```python
{
    "shaped_reward": 0.5,           # float in [-1, 1]
    "merge_signal": 1.0,            # +1.0 or -1.0
    "eval_component": 0.0,          # float in [-1, 1]
    "eval_metric": 0.5,             # raw normalized score, or None
    "weights": {"w_merge": 0.5, "w_eval": 0.5},
}
```

| Field | Type | Description |
|-------|------|-------------|
| `shaped_reward` | `float` | Blended reward, always within `[-1, 1]` |
| `merge_signal` | `float` | `+1.0` (merged) or `-1.0` (failed/missing) |
| `eval_component` | `float` | Re-centered eval metric in `[-1, 1]` |
| `eval_metric` | `float \| None` | Raw normalized `overall_score`, or `None` |
| `weights` | `dict` | Normalized `{"w_merge": float, "w_eval": float}` |

---

## Degenerate-Case Behavior

| Case | Behavior |
|------|----------|
| Missing / `None` eval metric | `eval_component = 0.0` (neutral), warning logged |
| Non-numeric eval metric (e.g. stray string) | `eval_component = 0.0` (neutral), warning logged — never raises (mirrors `build_merge_request` in T224) |
| Non-finite eval metric (NaN / inf) | `eval_component = 0.0` (neutral), warning logged |
| eval metric outside `[0, 1]` | clamped to `[0, 1]` with a warning (mirrors `build_merge_request`) |
| Failed / missing merge (`merged` falsy or `None`) | `merge_signal = -1.0` |
| Both weights resolve to `0.0` | defaults `0.5 / 0.5` restored before normalization |
| Negative or non-finite weight | `ValueError` raised at boundary |
| Non-numeric weight env var | `ValueError` raised at boundary |

---

## File Dependencies

- **Implementation**: `implementation/adapters/sia-target/reward_shaping.py` (T225)
- **Predecessor**: `implementation/adapters/sia-target/reward_attachment.py` (T224)
- **Tests**: `tests/functional/test_t225_reward_shaping.py`

---

## Acceptance Criteria (T225)

- [x] Reward is deterministic given the same merge outcome + metric.
- [x] Weighting and normalization are documented and configurable (args + env).
- [x] Degenerate cases (missing metric, non-numeric metric, out-of-range metric,
      failed merge) have defined, tested behavior.
- [x] Final shaped reward always within `[-1, 1]`.
- [x] Stdlib-only implementation (no new third-party dependencies).

---

## Consumed by

- T224 reward attachment flow (`reward_attachment.py`) — downstream trajectory
  reward record.
- Downstream training pipeline (GRPO / SFT) consuming the shaped reward.

---

**End of Design Document**
