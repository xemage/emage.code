# Task T213 - `query_ast` conflict pre-check + heuristic selection

## Objective
Use `query_ast` to pre-analyze concurrent edits and choose the appropriate merge heuristic per file/language,
reducing avoidable conflicts before invoking the merge engine.

## Inputs
- Orchestration module (T212)
- `query_ast` query types: `find_definition`, `find_references`, `extract_signature`, `list_exports`, `detect_entrypoints`
- Supported languages: Go, Python, Rust, TypeScript

## Expected outputs
- Pre-check that detects signature/export changes across `ours`/`theirs` and selects heuristic
  (`ast_semantic_only` default; `fail_rapidly_on_conflict` when signatures diverge)
- Language detection → merge_input `language` field population

## Acceptance criteria
- Diverging function signatures are detected via `extract_signature` and routed to a conflict path.
- Independent edits (different symbols) proceed with `ast_semantic_only`.
- Unsupported languages fall back gracefully (documented behavior).

## Blocker protocol
If blocked, report blocker type and severity with one proposed mitigation.
