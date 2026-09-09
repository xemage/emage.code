"""Body chunker: dispatches fenced code blocks to `chunk_code.py` (tree-sitter)
and everything else to section-aware (heading-based) prose chunking.

ADR-005 Decision 1: "tree-sitter for code, section-aware chunking for prose."
A vault entry's body is Markdown; code appears inside it as fenced blocks
(``` lang ... ```). This module walks the body once, tracking the current
Markdown heading stack, and produces one ordered list of `RawChunk`s: a
prose chunk for each run of text between headings/fences, and one-or-more
code chunks (via `chunk_code.py`) for each fenced block.

Prose enrichment fields are the section-aware equivalent of the code fields
(acceptance criterion 1): `symbol` = nearest enclosing heading text, `parents`
= ancestor heading path, `line_range` = body-relative line span. `ast_type`
and `imports` have no prose equivalent — prose has no abstract syntax tree
and no import statements — so both are left `None`/`()` for prose chunks,
documented here rather than approximated.
"""
from __future__ import annotations

import re

from implementation.runtime.memory.chunk_code import (
    chunk_supported_code,
    chunk_unsupported_code,
    is_supported,
)
from implementation.runtime.memory.schema import RawChunk

_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*\S)\s*$")
_FENCE_START_RE = re.compile(r"^```(\S*)\s*$")
_FENCE_END_RE = re.compile(r"^```\s*$")


def chunk_body(body: str) -> list[RawChunk]:
    lines = body.splitlines()
    state = _ChunkState(lines)
    idx = 0
    while idx < len(lines):
        idx = state.consume_line(lines, idx)
    state.flush_prose(len(lines))
    return state.chunks


class _ChunkState:
    """Single-pass walker over a body's lines. Kept as a small state machine
    (rather than one long function) to respect the 50-line function budget.
    """

    def __init__(self, lines: list[str]) -> None:
        self.chunks: list[RawChunk] = []
        self.heading_stack: list[tuple[int, str]] = []
        self.prose_start: int | None = None  # 1-indexed line number
        self._all_lines = lines

    def consume_line(self, lines: list[str], idx: int) -> int:
        line = lines[idx]
        heading = _HEADING_RE.match(line)
        if heading:
            self.flush_prose(idx)
            self._push_heading(heading)
            return idx + 1
        fence = _FENCE_START_RE.match(line)
        if fence:
            self.flush_prose(idx)
            return self._consume_fence(lines, idx, fence.group(1) or None)
        if self.prose_start is None:
            self.prose_start = idx + 1
        return idx + 1

    def _push_heading(self, heading: re.Match) -> None:
        level = len(heading.group(1))
        text = heading.group(2)
        while self.heading_stack and self.heading_stack[-1][0] >= level:
            self.heading_stack.pop()
        self.heading_stack.append((level, text))

    def _consume_fence(self, lines: list[str], idx: int, language: str | None) -> int:
        body_lines: list[str] = []
        cursor = idx + 1
        while cursor < len(lines) and not _FENCE_END_RE.match(lines[cursor]):
            body_lines.append(lines[cursor])
            cursor += 1
        code = "\n".join(body_lines)
        base_line = idx + 2  # first line *inside* the fence, 1-indexed
        self.chunks.extend(self._chunk_fence(code, language, base_line))
        return cursor + 1  # skip past the closing ``` line

    def _chunk_fence(self, code: str, language: str | None, base_line: int) -> list[RawChunk]:
        if not code.strip():
            return []
        if is_supported(language):
            return chunk_supported_code(code, language, base_line)
        return chunk_unsupported_code(code, language, base_line)

    def flush_prose(self, end_idx_exclusive: int) -> None:
        if self.prose_start is None:
            return
        end_line = end_idx_exclusive  # 1-indexed inclusive end
        if end_line >= self.prose_start:
            self._emit_prose_chunk(end_line)
        self.prose_start = None

    def _emit_prose_chunk(self, end_line: int) -> None:
        symbol = self.heading_stack[-1][1] if self.heading_stack else None
        parents = tuple(text for _, text in self.heading_stack[:-1])
        text = "\n".join(self._prose_lines(end_line))
        if text.strip():
            self.chunks.append(RawChunk(
                text=text, content_type="prose", language=None,
                symbol=symbol, ast_type=None, parents=parents,
                imports=(), line_range=(self.prose_start, end_line),
            ))

    def _prose_lines(self, end_line: int) -> list[str]:
        return self._all_lines[self.prose_start - 1:end_line]
