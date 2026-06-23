---
title: "Trainer Bridge Design (T230)"
producer: "backend-developer"
date: 2026-06-23
Based on: task-T230.md, reward-shaping-v1.md, infra-deployment-t226-v1.md
---

# Trainer Bridge — Parquet Trajectories → GRPO/SFT Dataset

## Purpose

The Trainer Bridge is the offline data-pipeline component that converts raw
`CompletionRecord` trajectories captured by the CWSO `cwso-rollout` service
into labelled fine-tuning datasets.  It bridges the live inference loop (T224,
T225, T226) and the downstream training loop (GRPO / SFT) without requiring a
live CWSO connection.

---

## Data Flow

```
CWSO cwso-rollout service
         │  writes CompletionRecord rows
         ▼
  Polar Parquet Store
  $CWSO_ROLLOUT_TRAJECTORY_STORE_PATH / /tmp/t226-parquet-store
         │  read_trajectories(store_path)
         │  ── schema-adaptive glob ──► list[dict]
         ▼
  trainer_bridge.py
     ┌───────────────────┐       ┌─────────────────────┐
     │  build_grpo_dataset│       │  build_sft_dataset   │
     │  (all rewards)     │       │  (reward >= 0.0)     │
     └────────┬──────────┘       └──────────┬──────────┘
              │                             │
       grpo_dataset.jsonl           sft_dataset.jsonl
              │                             │
              └─────────────┬───────────────┘
                            ▼
                  dataset_manifest.json
                  (provenance + stats)
```

---

## CompletionRecord → Training Format Mapping

### Source Schema (Parquet)

| Field                | Type           | Notes                                     |
|----------------------|----------------|-------------------------------------------|
| `workspace_uuid`     | `str`          | SIA generation identifier                 |
| `rollout_session_id` | `str`          | CWSO session UUID (primary grouping key)  |
| `prompt_token_ids`   | `list[int]`    | Tokenised prompt                          |
| `sampled_token_ids`  | `list[int]`    | Tokenised model completion                |
| `logprobs`           | `list[float]`  | Per-token log-probabilities               |
| `finish_reason`      | `str`          | `"stop"`, `"max_tokens"`, `"error"`       |
| `timestamp_ns`       | `int`          | Nanosecond epoch timestamp                |
| `evaluation_reward`  | `float\|null`  | Shaped reward (older records)             |
| `shaped_reward`      | `float\|null`  | Shaped reward (newer records, preferred)  |

Missing columns default to `None`; the bridge never errors on schema drift.

### GRPO Output Format (`grpo_dataset.jsonl`)

One JSON object per line, one entry per `rollout_session_id`:

```json
{
  "prompt_token_ids":     [1, 2, 3, ...],
  "completion_token_ids": [4, 5, ...],
  "reward":               0.72,
  "session_id":           "3f8a-..."
}
```

Reward field priority: `shaped_reward` → `evaluation_reward` → excluded.

When multiple records share the same `rollout_session_id` (e.g. retries), only
the entry with the **highest reward** is retained.

### SFT Output Format (`sft_dataset.jsonl`)

One JSON object per line:

```json
{
  "input_token_ids":  [1, 2, 3, ...],
  "output_token_ids": [4, 5, ...],
  "session_id":       "3f8a-..."
}
```

---

## GRPO Format Rationale

GRPO (Group Relative Policy Optimisation) requires labelled `(prompt, completion, reward)`
triples for all sampled completions — including negative-reward ones.  The
**shaped reward** (T225 formula: `clamp(w_merge * merge_signal + w_eval * eval_component, -1, 1)`)
is preferred over raw `merge_signal` because:

1. It blends two independent signals (merge outcome + evaluation score),
   reducing variance from either signal alone.
2. It is bounded to `[-1, 1]`, providing numerically stable training targets.
3. It already incorporates partial-credit for near-passing generations.

Both positive and negative rewards are included so the policy can learn from
negative examples.

---

## SFT Filter Rationale

Supervised Fine-Tuning requires **positive demonstrations only** — incorrect
completions contaminate the signal.  The default `min_reward=0.0` maps
directly to the T225 definition: reward ≥ 0 means the generation at minimum
did not actively harm merge quality.  The threshold is configurable so
callers can raise the bar (e.g. `min_reward=0.5`) for higher-quality SFT data.

---

## Output Directory Structure

```
<output_path>/
├── grpo_dataset.jsonl       # GRPO tuples (all sessions with valid reward)
├── sft_dataset.jsonl        # SFT pairs  (reward >= min_reward only)
└── dataset_manifest.json    # Stats + provenance
```

### `dataset_manifest.json` shape

```json
{
  "grpo": {
    "count": 120,
    "path": "/path/to/grpo_dataset.jsonl",
    "reward_stats": {"min": -0.95, "max": 0.98, "mean": 0.31}
  },
  "sft": {
    "count": 87,
    "path": "/path/to/sft_dataset.jsonl",
    "reward_threshold": 0.0
  },
  "total_trajectories": 130,
  "provenance": {
    "store_path": "/tmp/t226-parquet-store",
    "output_path": "/tmp/trainer-output",
    "generated_at": "2026-06-23T10:15:00+00:00"
  }
}
```

---

## API Reference

### `read_trajectories(store_path: str) -> list[dict]`

Recursively globs `*.parquet` under `store_path`.  Returns `[]` if the path
does not exist or contains no Parquet files.  Never raises on missing columns.

### `build_grpo_dataset(trajectories, output_path) -> dict`

Groups by `rollout_session_id`, keeps best reward per session, writes
`grpo_dataset.jsonl`.

### `build_sft_dataset(trajectories, output_path, min_reward=0.0) -> dict`

Filters to `reward >= min_reward`, writes `sft_dataset.jsonl`.

### `build_dataset(store_path, output_path, **kwargs) -> dict`

Orchestrator: calls all three above, writes `dataset_manifest.json`.

**CLI smoke-test:**
```bash
python3 -c "
from implementation.adapters.sia_target.trainer_bridge import build_dataset
result = build_dataset('/tmp/t226-parquet-store', '/tmp/trainer-output')
import json; print(json.dumps(result, indent=2, default=str))
"
```

---

## Security Notes

- **Path traversal (OWASP A01):** `_assert_safe_path()` rejects any resolved
  path that escapes its root.  All output writes are within `output_path`.
- **No external requests:** the bridge is file-I/O only.
- **No secrets in logs:** rewards and token IDs are logged at DEBUG level only;
  no PII fields are present.

---

## Production Debt

| # | Tag | Description | Effort |
|---|-----|-------------|--------|
| 1 | POC-DEBT | Single-node glob — no distributed/S3 support | L |
| 2 | POC-DEBT | No deduplication across shard files (reprocessing safe) | M |
| 3 | POC-DEBT | No streaming — entire dataset loaded into memory | M |
| 4 | POC-DEBT | No schema validation against known CompletionRecord version | S |
| 5 | POC-DEBT | SFT does not deduplicate by session (all matching records included) | S |
| 6 | POC-DEBT | No data-quality metrics (token length distribution, null rates) | M |
