"""Test helper: generate a synthetic ~100K-LOC knowledge vault for T453's
latency benchmark (`tests/performance/test_hybrid_retrieval_latency.py`).

Real production vault content does not exist yet (T452's own scope explicitly
excluded populating one — see `implementation/runtime/memory/README.md`
"Vault content"), so acceptance criterion 5's "100K LOC (or larger) repo" is
built synthetically here, the same pattern T452 used for its own fixtures
(`tests/fixtures/memory/`). Documented in full in
`docs/artifacts/hybrid-retrieval-v1.md` "Latency benchmark methodology".
"""
from __future__ import annotations

import subprocess
from pathlib import Path

_LINES_PER_FUNCTION = 8


def _function_source(module_idx: int, fn_idx: int) -> str:
    name = f"module_{module_idx}_function_{fn_idx}"
    return (
        f"def {name}(value):\n"
        f'    """Helper {fn_idx} in module {module_idx}: transform and validate value."""\n'
        f"    processed = value * {fn_idx + 1}\n"
        f"    if processed < 0:\n"
        f"        raise ValueError('negative result in {name}')\n"
        f"    return processed\n"
        f"\n"
        f"\n"
    )


def _module_body(module_idx: int, functions_per_module: int) -> str:
    header = f"## Module {module_idx}\n\nSynthetic module {module_idx} for T453's latency benchmark.\n\n"
    code = "```python\nimport os\nimport json\n\n\n"
    code += "".join(_function_source(module_idx, i) for i in range(functions_per_module))
    code += "```\n"
    return header + code


def _entry_text(module_idx: int, project_id: str, functions_per_module: int) -> str:
    frontmatter = (
        "---\n"
        "scope: project\n"
        f"project_id: {project_id}\n"
        f'title: "Synthetic benchmark module {module_idx}"\n'
        "tags: [synthetic, t453-benchmark]\n"
        "---\n\n"
    )
    return frontmatter + _module_body(module_idx, functions_per_module)


def estimate_total_loc(num_modules: int, functions_per_module: int) -> int:
    return num_modules * functions_per_module * _LINES_PER_FUNCTION


def generate_synthetic_corpus(dest_dir: Path, project_id: str, num_modules: int,
                               functions_per_module: int) -> Path:
    """Write `num_modules` vault entries (each a fenced Python block of
    `functions_per_module` functions) under `dest_dir`, commit as a fresh
    git repo, and return `dest_dir`. Total generated LOC (in fenced code,
    not counting Markdown/frontmatter) is `estimate_total_loc(...)`.
    """
    vault_dir = dest_dir / "implementation" / "knowledge" / "memory" / "project"
    vault_dir.mkdir(parents=True, exist_ok=True)
    for module_idx in range(num_modules):
        text = _entry_text(module_idx, project_id, functions_per_module)
        (vault_dir / f"synthetic-module-{module_idx:04d}.md").write_text(text, encoding="utf-8")
    _commit_repo(dest_dir)
    return dest_dir


def _commit_repo(repo_dir: Path) -> None:
    _run_git(repo_dir, ["init", "-q"])
    _run_git(repo_dir, ["config", "user.email", "t453-benchmark@example.invalid"])
    _run_git(repo_dir, ["config", "user.name", "T453 Benchmark"])
    _run_git(repo_dir, ["add", "-A"])
    _run_git(repo_dir, ["commit", "-q", "-m", "fixture: synthetic 100K-LOC benchmark corpus"])


def _run_git(cwd: Path, args: list[str]) -> None:
    subprocess.run(["git", *args], cwd=str(cwd), check=True, capture_output=True, text=True)
