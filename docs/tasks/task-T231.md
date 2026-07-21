# Task T231 - Fine-tune `<some-model>` (LoRA/GRPO) + redeploy behind HAL

## Objective
Fine-tune the local open-weight `<some-model>` from the trainer-bridge dataset and redeploy it behind
cwso-hal so the next SIA generations use the improved weights.

## Inputs
- Training dataset (T230)
- `<some-model>` base + serving stack (vLLM/HAL) from T203

## Expected outputs
- A fine-tuned model artifact (LoRA adapter or merged weights)
- Redeployment behind HAL with an OpenAI-compatible endpoint and a versioned model id

## Acceptance criteria
- Offline fine-tune completes with logged hyperparameters and seeds (reproducible).
- Redeployed model serves through HAL and is reachable via the rollout proxy.
- Rollback to the previous model version is documented and tested.

## Blocker protocol
If blocked, report blocker type and severity with one proposed mitigation.
