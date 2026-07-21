# T231 Implementation Guide: Model Fine-tuning & HAL Redeploy

**Task:** T231
**Owner:** backend-developer
**Priority:** P1 (critical path → T233)
**Estimated effort:** 3-5 days
**Depends on:** T230 ✅ (trainer bridge dataset)

## Overview

T231 fine-tunes the local open-weight model using the T230 trainer-bridge output (GRPO/SFT dataset) and redeploys behind HAL. This unblocks T233 (closed-loop eval) which measures improvement deltas.

**Current state (from T230):**
- ✅ Parquet trajectories in `/tmp/t226-parquet-store`
- ✅ Trainer bridge converts to GRPO/SFT dataset formats
- ✅ Saved as JSON manifests

**T231 goal:**
1. Load T230 dataset (GRPO or SFT format)
2. Fine-tune base model with reproducible hyperparameters
3. Save fine-tuned weights (LoRA or merged)
4. Redeploy behind HAL with new model version
5. Document rollback procedure

## Prerequisites Check

### 1. Verify T230 Dataset Output

**Location:** `implementation/adapters/sia-target/`

**Check trainer bridge functions:**
```python
# From trainer_bridge.py
def build_grpo_dataset(records):
  """Returns list of { "prompt": ..., "chosen": ..., "rejected": ... }"""

def build_sft_dataset(records):
  """Returns list of { "prompt": ..., "completion": ... }"""
```

**Verify dataset format:**
```bash
# Check if T230 test passed
pytest tests/functional/test_t230_trainer_bridge.py -v
# Expected: 34/34 passing

# Inspect dataset structure
python3 -c "
import sys
sys.path.insert(0, 'implementation/adapters/sia-target')
from trainer_bridge import read_trajectories, build_grpo_dataset
records = read_trajectories('/tmp/t226-parquet-store')
grpo = build_grpo_dataset(records[:5])
print('GRPO sample:', grpo[0] if grpo else 'empty')
"
```

### 2. Check HAL/vLLM Setup

**From T203 deployment (assumed running):**
```bash
# Verify HAL is accessible
curl http://localhost:8000/v1/models 2>/dev/null || echo "HAL not reachable"

# Get current model version
curl http://localhost:8000/v1/models | jq '.data[0]'
```

### 3. Fine-tuning Environment Setup

**Choose approach:**

#### Option A: LoRA Fine-tuning (Faster, Lower Resources)
- Use: `peft` (Parameter-Efficient Fine-Tuning)
- Output: LoRA adapter (small, mergeable)
- Time: 1-2 hours for PoC dataset
- Resources: Single GPU sufficient

#### Option B: Full Model Fine-tuning (Slower, Higher Quality)
- Use: HuggingFace Transformers + distributed training
- Output: Full merged weights
- Time: 4-8 hours depending on model size
- Resources: Multi-GPU recommended

**Recommendation:** Start with **Option A (LoRA)** for faster iteration.

## Implementation Steps

### Step 1: Load T230 Dataset (1 hour)

**Script: `implementation/scripts/fine-tune-setup.py`** (create)

```python
#!/usr/bin/env python3
"""Load T230 dataset and prepare for fine-tuning."""

import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "../adapters/sia-target"))

from trainer_bridge import read_trajectories, build_grpo_dataset, build_sft_dataset

def load_dataset(store_path="/tmp/t226-parquet-store", dataset_type="grpo"):
    """Load and validate trainer-bridge dataset."""
    print(f"Reading trajectories from {store_path}...")
    records = read_trajectories(store_path)

    if not records:
        print("ERROR: No trajectories found. Check parquet store path.")
        return None

    print(f"Loaded {len(records)} records")

    if dataset_type == "grpo":
        dataset = build_grpo_dataset(records)
        print(f"Built GRPO dataset: {len(dataset)} examples")
        validate_grpo(dataset)
    elif dataset_type == "sft":
        dataset = build_sft_dataset(records)
        print(f"Built SFT dataset: {len(dataset)} examples")
        validate_sft(dataset)

    return dataset

def validate_grpo(dataset):
    """Validate GRPO format."""
    required_keys = {"prompt", "chosen", "rejected"}
    for i, example in enumerate(dataset[:5]):
        if not all(k in example for k in required_keys):
            print(f"ERROR: Example {i} missing keys: {required_keys - set(example.keys())}")
            return False
    print(f"✓ GRPO validation passed (checked {min(5, len(dataset))} examples)")
    return True

def validate_sft(dataset):
    """Validate SFT format."""
    required_keys = {"prompt", "completion"}
    for i, example in enumerate(dataset[:5]):
        if not all(k in example for k in required_keys):
            print(f"ERROR: Example {i} missing keys: {required_keys - set(example.keys())}")
            return False
    print(f"✓ SFT validation passed (checked {min(5, len(dataset))} examples)")
    return True

if __name__ == "__main__":
    dataset = load_dataset(dataset_type="grpo")
    if dataset:
        print(f"\nDataset ready: {len(dataset)} examples")
        print(f"Sample: {json.dumps(dataset[0], indent=2)[:500]}...")
```

**Run:**
```bash
python3 implementation/scripts/fine-tune-setup.py
# Expected output:
# Reading trajectories from /tmp/t226-parquet-store...
# Loaded 50 records
# Built GRPO dataset: 50 examples
# ✓ GRPO validation passed (checked 5 examples)
# Dataset ready: 50 examples
```

### Step 2: LoRA Fine-tuning (2-3 hours)

**Install dependencies:**
```bash
pip install peft torch transformers datasets accelerate wandb
```

**Script: `implementation/scripts/fine-tune-lora.py`** (create)

```python
#!/usr/bin/env python3
"""Fine-tune model using LoRA adapter."""

import json
import torch
from pathlib import Path
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer
from datasets import Dataset
from peft import LoraConfig, get_peft_model, TaskType

# Configuration (reproducible)
MODEL_ID = "meta-llama/Llama-2-7b"  # Or whatever base model from T203
LORA_R = 8
LORA_ALPHA = 16
LORA_DROPOUT = 0.05
LEARNING_RATE = 5e-4
EPOCHS = 3
BATCH_SIZE = 4
OUTPUT_DIR = "./fine-tune-output"

def setup_model_and_tokenizer():
    """Load base model and tokenizer."""
    print(f"Loading model {MODEL_ID}...")
    model = AutoModelForCausalLM.from_pretrained(MODEL_ID, device_map="auto")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    tokenizer.pad_token = tokenizer.eos_token
    return model, tokenizer

def apply_lora(model):
    """Apply LoRA adapter to model."""
    config = LoraConfig(
        r=LORA_R,
        lora_alpha=LORA_ALPHA,
        lora_dropout=LORA_DROPOUT,
        bias="none",
        task_type=TaskType.CAUSAL_LM
    )
    return get_peft_model(model, config)

def prepare_dataset(dataset_path, tokenizer):
    """Load and tokenize dataset."""
    with open(dataset_path) as f:
        data = json.load(f)

    def tokenize_function(example):
        prompt_text = example["prompt"]
        completion_text = example.get("chosen", example.get("completion", ""))
        text = f"{prompt_text}\n{completion_text}"

        encodings = tokenizer(
            text,
            truncation=True,
            max_length=512,
            padding="max_length"
        )
        encodings["labels"] = encodings["input_ids"].copy()
        return encodings

    dataset = Dataset.from_dict(data)
    dataset = dataset.map(tokenize_function, remove_columns=data[0].keys())
    return dataset

def fine_tune():
    """Run fine-tuning loop."""
    # Setup
    model, tokenizer = setup_model_and_tokenizer()
    model = apply_lora(model)
    dataset = prepare_dataset("dataset.json", tokenizer)

    # Training arguments
    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        per_device_train_batch_size=BATCH_SIZE,
        learning_rate=LEARNING_RATE,
        num_train_epochs=EPOCHS,
        logging_steps=10,
        save_strategy="epoch",
        seed=42,  # Reproducible
    )

    # Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=dataset,
    )

    print("Starting training...")
    trainer.train()

    print(f"✓ Training complete. Output: {OUTPUT_DIR}")
    return model, OUTPUT_DIR

if __name__ == "__main__":
    model, output_dir = fine_tune()
    # Save adapter
    model.save_pretrained(f"{output_dir}/lora-adapter")
    print(f"LoRA adapter saved to: {output_dir}/lora-adapter")
```

**Run:**
```bash
python3 implementation/scripts/fine-tune-lora.py 2>&1 | tee fine-tune.log
# Monitor progress: tail -f fine-tune.log
```

### Step 3: Merge Adapter & Save Full Weights (30 mins)

**Script: `implementation/scripts/merge-lora.py`** (create)

```python
#!/usr/bin/env python3
"""Merge LoRA adapter into base model for deployment."""

from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

MODEL_ID = "meta-llama/Llama-2-7b"
ADAPTER_PATH = "./fine-tune-output/lora-adapter"
OUTPUT_PATH = "./fine-tuned-merged"
MODEL_VERSION = "v1-ft"

def merge_and_save():
    """Load base model, apply adapter, merge, and save."""
    print(f"Loading base model {MODEL_ID}...")
    model = AutoModelForCausalLM.from_pretrained(MODEL_ID, device_map="auto")

    print(f"Loading LoRA adapter {ADAPTER_PATH}...")
    model = PeftModel.from_pretrained(model, ADAPTER_PATH)

    print("Merging adapter into base model...")
    model = model.merge_and_unload()

    print(f"Saving merged model to {OUTPUT_PATH}...")
    model.save_pretrained(OUTPUT_PATH)

    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    tokenizer.save_pretrained(OUTPUT_PATH)

    print(f"✓ Merged model ready for deployment: {OUTPUT_PATH}")
    return OUTPUT_PATH

if __name__ == "__main__":
    output_path = merge_and_save()
```

**Run:**
```bash
python3 implementation/scripts/merge-lora.py
# Output: ./fine-tuned-merged/
```

### Step 4: Redeploy Behind HAL (30 mins - 1 hour)

**Check HAL configuration:**
```bash
# Find HAL config/entrypoint
find /home/emage/Code/emage/CWSO -name "*hal*" -o -name "*vllm*" 2>/dev/null | head -10
```

**Option A: Update HAL config (simplest)**
```bash
# Stop current HAL/vLLM
docker-compose down cwso-vllm 2>/dev/null || pkill -f vllm

# Copy fine-tuned model
cp -r ./fine-tuned-merged /models/fine-tuned-v1

# Update environment
export VLLM_MODEL=/models/fine-tuned-v1

# Restart with new model
docker-compose up -d cwso-vllm
# Or: vllm serve /models/fine-tuned-v1 --port 8000
```

**Option B: Create versioned endpoint**
```bash
# Keep both models running on different ports
vllm serve ./fine-tuned-merged --port 8001 --model-name fine-tuned-v1 &

# Route traffic based on version header
# (Would need routing layer configuration)
```

**Verify new model:**
```bash
curl http://localhost:8000/v1/models | jq '.data[0].id'
# Expected: fine-tuned-v1
```

### Step 5: Document Rollback Procedure

**Create `docs/releases/model-v1-fine-tune-rollback.md`:**

```markdown
# Model Fine-tuning Rollback (T231)

## Current State
- Base model: meta-llama/Llama-2-7b
- Fine-tuned model: /models/fine-tuned-v1
- HAL endpoint: http://localhost:8000

## Rollback Steps

### If fine-tuned model shows issues:

1. Stop HAL/vLLM
   docker-compose down cwso-vllm

2. Restore base model
   export VLLM_MODEL=/models/base-llama
   docker-compose up -d cwso-vllm

3. Verify rollback
   curl http://localhost:8000/v1/models | jq '.data[0].id'
   # Should show: meta-llama/Llama-2-7b

4. Run SIA harness test
   pytest tests/functional/test_t223_sia_harness_capture.py -v
   # Should show 14/15 passing (same as before)

## Quick Rollback Command

export VLLM_MODEL=/models/base-llama && docker-compose down cwso-vllm && docker-compose up -d cwso-vllm
```

## Testing & Validation

### Test 1: Model Loading
```bash
python3 -c "
from transformers import AutoModelForCausalLM, AutoTokenizer
model = AutoModelForCausalLM.from_pretrained('./fine-tuned-merged')
tokenizer = AutoTokenizer.from_pretrained('./fine-tuned-merged')
print('✓ Model loaded successfully')
"
```

### Test 2: Inference Quality
```bash
python3 -c "
from transformers import pipeline
gen = pipeline('text-generation', model='./fine-tuned-merged')
result = gen('def fibonacci', max_length=100)
print('Generated:', result[0]['generated_text'][:200])
"
```

### Test 3: HAL Integration
```bash
curl http://localhost:8000/v1/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "fine-tuned-v1", "prompt": "def fibonacci", "max_tokens": 50}' \
  | jq '.choices[0].text'
```

### Test 4: T233 Readiness
Once deployed, T233 (closed-loop eval) will measure improvement:
```bash
# (Run after T231 completes)
pytest tests/functional/test_t233_closed_loop_eval.py -v
```

## Acceptance Criteria

- [ ] Fine-tuning script runs to completion (all epochs)
- [ ] Loss curve shows convergence (check fine-tune.log)
- [ ] Model loads without errors
- [ ] HAL serves fine-tuned model on `/v1/models`
- [ ] Model generates valid code samples
- [ ] Rollback procedure tested and documented
- [ ] T233 can run and measure improvement delta

## Hyperparameters & Reproducibility

**Logged for future reference:**
- Base model: meta-llama/Llama-2-7b
- LoRA rank (r): 8
- LoRA alpha: 16
- Dropout: 0.05
- Learning rate: 5e-4
- Epochs: 3
- Batch size: 4
- Seed: 42
- Dataset size: ~50 examples from T230

**To reproduce:**
```bash
cd emage.code
python3 implementation/scripts/fine-tune-setup.py
python3 implementation/scripts/fine-tune-lora.py
python3 implementation/scripts/merge-lora.py
# Then follow redeploy steps
```

## Timeline

| Phase | Duration | Notes |
|-------|----------|-------|
| Step 1: Load dataset | 1 hour | Check T230 output validity |
| Step 2: LoRA fine-tune | 2-3 hours | Monitor training logs |
| Step 3: Merge adapter | 30 mins | CPU-bound, quick |
| Step 4: HAL redeploy | 30 mins - 1 hour | Restart service, verify |
| Step 5: Rollback doc | 15 mins | Write procedure |
| **Total** | **3-5 days** | Assuming T230 ✅ ready |

## Blockers & Mitigations

**Blocker: No GPU available**
- Mitigation: Use CPU (slower), reduce batch size, reduce epochs

**Blocker: LoRA training fails**
- Mitigation: Check dataset format with fine-tune-setup.py, reduce rank (r=4)

**Blocker: HAL won't start with new model**
- Mitigation: Check model format compatibility, verify tokenizer saved

## Next: T233 (Closed-Loop Eval)

Once T231 complete, T233 will:
- Run SIA harness with fine-tuned model
- Measure improvement delta vs baseline
- Compare reward scores from T225
- Unblock T234 (cost/latency telemetry)
