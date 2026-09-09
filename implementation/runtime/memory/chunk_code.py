"""Tree-sitter code chunking — ADR-005 Decision 1's "tree-sitter for code" path.

Applies to fenced code blocks found inside a vault entry's Markdown body
(see `chunker.py`), not to raw source files — the vault's canonical unit is a
Markdown/frontmatter knowledge entry (ADR-005 Decision 1), and code appears
inside it as fenced blocks. Each fenced block with a supported language gets
split into one chunk per top-level symbol (function/class); unsupported
languages fall back to one whole-block chunk (see `chunk_unsupported_code`).

Requires the optional `tree-sitter` + grammar packages
(`tree-sitter-python`, `tree-sitter-javascript`, `tree-sitter-bash`) — see
`implementation/runtime/memory/requirements.txt`. Callers must handle
ImportError for environments where these are not installed (mirrors this
repo's existing `unittest.SkipTest("... not available")` pattern).
"""
from __future__ import annotations

from dataclasses import dataclass

from implementation.runtime.memory.schema import RawChunk


@dataclass(frozen=True)
class _CodeContext:
    """Bundles the per-fenced-block invariants threaded through the
    tree-sitter walk, so functions in this module stay within this repo's
    max-4-parameters convention.
    """

    source: bytes
    definition_types: set[str]
    imports: tuple[str, ...]
    language: str
    base_line: int

# fence-language-tag -> (grammar module name, top-level definition node types)
_SUPPORTED_LANGUAGES = {
    "python": ("tree_sitter_python", {"function_definition", "class_definition"}),
    "javascript": ("tree_sitter_javascript", {"function_declaration", "class_declaration"}),
    "js": ("tree_sitter_javascript", {"function_declaration", "class_declaration"}),
    "typescript": ("tree_sitter_javascript", {"function_declaration", "class_declaration"}),
    "bash": ("tree_sitter_bash", {"function_definition"}),
    "sh": ("tree_sitter_bash", {"function_definition"}),
}

_IMPORT_NODE_TYPES = {"import_statement", "import_from_statement"}

_parser_cache: dict[str, object] = {}


def is_supported(language: str | None) -> bool:
    return language is not None and language.lower() in _SUPPORTED_LANGUAGES


def _get_parser(language: str):
    key = language.lower()
    if key in _parser_cache:
        return _parser_cache[key]
    from tree_sitter import Language, Parser  # local import: optional dependency

    module_name, _ = _SUPPORTED_LANGUAGES[key]
    grammar_module = __import__(module_name)
    ts_language = Language(grammar_module.language())
    parser = Parser(ts_language)
    _parser_cache[key] = parser
    return parser


def _extract_imports(root, source: bytes) -> tuple[str, ...]:
    imports = []
    for child in root.children:
        if child.type in _IMPORT_NODE_TYPES:
            imports.append(source[child.start_byte:child.end_byte].decode("utf-8").strip())
    return tuple(imports)


def _symbol_name(node, source: bytes) -> str | None:
    name_node = node.child_by_field_name("name")
    if name_node is None:
        return None
    return source[name_node.start_byte:name_node.end_byte].decode("utf-8")


def chunk_supported_code(code: str, language: str, base_line: int) -> list[RawChunk]:
    """Split one fenced code block into per-symbol chunks via tree-sitter.

    `base_line` is the 1-indexed line number of the code block's first line
    within the entry body, used to make `line_range` body-relative.
    """
    _, definition_types = _SUPPORTED_LANGUAGES[language.lower()]
    source = code.encode("utf-8")
    tree = _get_parser(language).parse(source)
    root = tree.root_node
    imports = _extract_imports(root, source)
    ctx = _CodeContext(source, definition_types, imports, language, base_line)
    chunks = _definition_chunks(root, ctx)
    if chunks:
        return chunks
    return [_whole_block_chunk(code, language, base_line, ast_type="module")]


def _definition_chunks(root, ctx: _CodeContext) -> list[RawChunk]:
    chunks = []
    for node in root.children:
        if node.type not in ctx.definition_types:
            continue
        chunks.append(_node_to_chunk(node, ctx, parents=()))
        chunks.extend(_nested_definition_chunks(node, ctx))
    return chunks


def _nested_definition_chunks(node, ctx: _CodeContext) -> list[RawChunk]:
    """Methods inside a class become their own chunk, `parents=(class_name,)`."""
    chunks = []
    outer_name = _symbol_name(node, ctx.source)
    body = node.child_by_field_name("body")
    if body is None:
        return chunks
    for child in body.children:
        if child.type not in ctx.definition_types:
            continue
        chunks.append(_node_to_chunk(child, ctx, parents=(outer_name,) if outer_name else ()))
    return chunks


def _node_to_chunk(node, ctx: _CodeContext, parents: tuple[str, ...]) -> RawChunk:
    text = ctx.source[node.start_byte:node.end_byte].decode("utf-8")
    start = ctx.base_line + node.start_point[0]
    end = ctx.base_line + node.end_point[0]
    return RawChunk(
        text=text,
        content_type="code",
        language=ctx.language,
        symbol=_symbol_name(node, ctx.source),
        ast_type=node.type,
        parents=parents,
        imports=ctx.imports,
        line_range=(start, end),
    )


def _whole_block_chunk(code: str, language: str | None, base_line: int, ast_type: str | None) -> RawChunk:
    line_count = code.count("\n") + (0 if code.endswith("\n") else 1)
    end = base_line + max(line_count - 1, 0)
    return RawChunk(
        text=code,
        content_type="code",
        language=language,
        symbol=None,
        ast_type=ast_type,
        parents=(),
        imports=(),
        line_range=(base_line, end),
    )


def chunk_unsupported_code(code: str, language: str | None, base_line: int) -> list[RawChunk]:
    """Fallback for a fenced block whose language has no installed tree-sitter
    grammar: index the whole block as one chunk, `ast_type=None` (documented,
    not silently approximated as some AST node type it isn't).
    """
    return [_whole_block_chunk(code, language, base_line, ast_type=None)]
