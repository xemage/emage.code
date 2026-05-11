"""Rough character-based token estimator.

We deliberately avoid a real tokenizer dependency. The 1 token ≈ 4 chars
heuristic is good enough for budget *guardrails* — it errs on the conservative
side for English prose, which is what agent prompts mostly are.

Source: OpenAI tokenizer rule-of-thumb
https://platform.openai.com/tokenizer
"""
from __future__ import annotations


CHARS_PER_TOKEN = 4


def estimate_tokens(text: str) -> int:
    return max(1, len(text) // CHARS_PER_TOKEN)
