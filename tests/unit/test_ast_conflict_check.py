"""Unit tests for AST conflict pre-check module."""

import unittest
from unittest.mock import Mock, patch, MagicMock

from implementation.runtime.cwso.ast_conflict_check import (
    AstConflictChecker,
    ConflictSeverity,
    FileConflictAnalysis,
    PreCheckResult,
)
from implementation.runtime.cwso.client import (
    QueryType,
    MergeHeuristic,
    MergeLanguage,
)


class TestAstConflictCheckerLanguageDetection(unittest.TestCase):
    """Test language detection from file paths."""

    def setUp(self):
        self.mock_client = Mock()
        self.checker = AstConflictChecker(self.mock_client)

    def test_python_detection(self):
        """Detect Python files."""
        self.assertEqual(
            self.checker._detect_language("src/main.py"), MergeLanguage.PYTHON.value
        )

    def test_go_detection(self):
        """Detect Go files."""
        self.assertEqual(
            self.checker._detect_language("cmd/server/main.go"), MergeLanguage.GO.value
        )

    def test_typescript_detection(self):
        """Detect TypeScript files."""
        self.assertEqual(
            self.checker._detect_language("app/index.ts"), MergeLanguage.TYPESCRIPT.value
        )
        self.assertEqual(
            self.checker._detect_language("app/index.tsx"), MergeLanguage.TYPESCRIPT.value
        )

    def test_rust_detection(self):
        """Detect Rust files."""
        self.assertEqual(
            self.checker._detect_language("src/lib.rs"), MergeLanguage.RUST.value
        )

    def test_unsupported_language(self):
        """Return None for unsupported languages."""
        self.assertIsNone(self.checker._detect_language("README.md"))
        self.assertIsNone(self.checker._detect_language("config.yaml"))


class TestAstConflictCheckerSymbolQuerying(unittest.TestCase):
    """Test AST symbol and signature queries."""

    def setUp(self):
        self.mock_client = Mock()
        self.checker = AstConflictChecker(self.mock_client)

    def test_query_exports_success(self):
        """Query exports and return symbol set."""
        self.mock_client.query_ast.return_value = {
            "exports": ["function_a", "class_b", "const_c"]
        }

        result = self.checker._query_exports("workspace-123", "src/main.py")

        self.assertEqual(result, {"function_a", "class_b", "const_c"})
        self.mock_client.query_ast.assert_called_once_with(
            workspace_uuid="workspace-123",
            path="src/main.py",
            query_type=QueryType.LIST_EXPORTS,
            target_symbol=None,
        )

    def test_query_exports_empty(self):
        """Return empty set if no exports found."""
        self.mock_client.query_ast.return_value = {"exports": []}

        result = self.checker._query_exports("workspace-123", "src/main.py")

        self.assertEqual(result, set())

    def test_query_exports_graceful_failure(self):
        """Return empty set if query fails."""
        self.mock_client.query_ast.side_effect = Exception("Query failed")

        result = self.checker._query_exports("workspace-123", "src/main.py")

        self.assertEqual(result, set())

    def test_query_signatures_multiple_symbols(self):
        """Query signatures for multiple symbols."""
        _sigs = {
            "foo": {"signature": "def foo(x: int) -> str:"},
            "bar": {"signature": "def bar(a, b) -> None:"},
        }
        self.mock_client.query_ast.side_effect = (
            lambda **kw: _sigs[kw["target_symbol"]]
        )

        result = self.checker._query_signatures(
            "workspace-123", "src/main.py", {"foo", "bar"}
        )

        self.assertEqual(result["foo"], "def foo(x: int) -> str:")
        self.assertEqual(result["bar"], "def bar(a, b) -> None:")

    def test_query_signatures_partial_failure(self):
        """Handle partial signature query failures."""
        def _side_effect(**kw):
            if kw["target_symbol"] == "foo":
                return {"signature": "def foo(x) -> int:"}
            raise Exception("Query failed for bar")

        self.mock_client.query_ast.side_effect = _side_effect

        result = self.checker._query_signatures(
            "workspace-123", "src/main.py", {"foo", "bar"}
        )

        self.assertIn("foo", result)
        self.assertNotIn("bar", result)


class TestConflictDetection(unittest.TestCase):
    """Test conflict detection logic."""

    def setUp(self):
        self.mock_client = Mock()
        self.checker = AstConflictChecker(self.mock_client)

    def test_no_conflicts_independent_edits(self):
        """Independent edits get LOW severity."""
        analysis = FileConflictAnalysis(path="main.py", language="python")
        analysis.base_symbols = {"foo", "bar"}
        analysis.ours_symbols = {"foo", "baz"}  # Added baz
        analysis.theirs_symbols = {"foo", "qux"}  # Added qux
        analysis.ours_signatures = {"foo": "def foo(): pass", "baz": "def baz(): pass"}
        analysis.theirs_signatures = {"foo": "def foo(): pass", "qux": "def qux(): pass"}

        self.checker._detect_conflicts(analysis)

        self.assertEqual(analysis.severity, ConflictSeverity.LOW)
        self.assertEqual(
            analysis.recommended_heuristic, MergeHeuristic.AST_SEMANTIC_ONLY
        )

    def test_diverging_signatures_high_severity(self):
        """Diverging function signatures get HIGH severity."""
        analysis = FileConflictAnalysis(path="main.py", language="python")
        analysis.base_symbols = {"foo"}
        analysis.ours_symbols = {"foo"}
        analysis.theirs_symbols = {"foo"}
        analysis.ours_signatures = {"foo": "def foo(x: int) -> str:"}
        analysis.theirs_signatures = {"foo": "def foo(x: str) -> int:"}

        self.checker._detect_conflicts(analysis)

        self.assertEqual(analysis.severity, ConflictSeverity.HIGH)
        self.assertEqual(
            analysis.recommended_heuristic, MergeHeuristic.FAIL_RAPIDLY_ON_CONFLICT
        )
        self.assertIn("foo", analysis.diverging_symbols)

    def test_both_added_same_symbol_medium_severity(self):
        """Both sides adding the same symbol gets MEDIUM severity."""
        analysis = FileConflictAnalysis(path="main.py", language="python")
        analysis.base_symbols = {"foo"}
        analysis.ours_symbols = {"foo", "new_func"}
        analysis.theirs_symbols = {"foo", "new_func"}
        analysis.ours_signatures = {
            "foo": "def foo(): pass",
            "new_func": "def new_func(): pass",
        }
        analysis.theirs_signatures = {
            "foo": "def foo(): pass",
            "new_func": "def new_func(): pass",
        }

        self.checker._detect_conflicts(analysis)

        self.assertEqual(analysis.severity, ConflictSeverity.MEDIUM)
        self.assertEqual(
            analysis.recommended_heuristic, MergeHeuristic.FAIL_RAPIDLY_ON_CONFLICT
        )


class TestFileAnalysis(unittest.TestCase):
    """Test single-file analysis."""

    def setUp(self):
        self.mock_client = Mock()
        self.checker = AstConflictChecker(self.mock_client)

    def test_analyze_file_queries_all_workspaces(self):
        """Analyze file queries exports from all three workspaces."""
        self.mock_client.query_ast.side_effect = [
            {"exports": ["base_func"]},  # base
            {"exports": ["base_func", "ours_func"]},  # ours
            {"exports": ["base_func", "theirs_func"]},  # theirs
        ]

        result = self.checker.analyze_file(
            "src/main.py", "base-ws", "ours-ws", "theirs-ws"
        )

        self.assertEqual(result.base_symbols, {"base_func"})
        self.assertEqual(result.ours_symbols, {"base_func", "ours_func"})
        self.assertEqual(result.theirs_symbols, {"base_func", "theirs_func"})

    def test_analyze_file_language_detection(self):
        """Analysis detects and stores language."""
        self.mock_client.query_ast.side_effect = [
            {"exports": []},
            {"exports": []},
            {"exports": []},
        ]

        result = self.checker.analyze_file(
            "src/lib.rs", "base-ws", "ours-ws", "theirs-ws"
        )

        self.assertEqual(result.language, MergeLanguage.RUST.value)


class TestPreCheckOrchestration(unittest.TestCase):
    """Test full pre-check orchestration across files."""

    def setUp(self):
        self.mock_client = Mock()
        self.checker = AstConflictChecker(self.mock_client)

    def test_run_multiple_files_mixed_severities(self):
        """Run across multiple files with mixed conflict severities."""
        # Mock file 1: no conflicts (LOW)
        # Mock file 2: diverging signatures (HIGH)
        call_sequence = [
            # File 1: main.py (LOW severity)
            {"exports": ["foo"]},
            {"exports": ["foo"]},
            {"exports": ["foo"]},
            # File 2: lib.py (HIGH severity)
            {"exports": ["bar"]},
            {"exports": ["bar"]},
            {"exports": ["bar"]},
            # Signatures for file 2
            {"signature": "def bar(x): pass"},
            {"signature": "def bar(x, y): pass"},
        ]
        self.mock_client.query_ast.side_effect = call_sequence

        with patch.object(
            self.checker, "analyze_file", wraps=self.checker.analyze_file
        ) as mock_analyze:
            # Manually set up return values for clarity
            def side_effect_analyze(path, base_ws, ours_ws, theirs_ws):
                analysis = self.checker.analyze_file(path, base_ws, ours_ws, theirs_ws)
                if "lib.py" in path:
                    # Simulate HIGH severity for lib.py
                    analysis.severity = ConflictSeverity.HIGH
                    analysis.recommended_heuristic = (
                        MergeHeuristic.FAIL_RAPIDLY_ON_CONFLICT
                    )
                    analysis.diverging_symbols = ["bar"]
                return analysis

            with patch.object(
                self.checker, "_detect_conflicts"
            ) as mock_detect:

                def detect_side_effect(analysis):
                    if "lib.py" in analysis.path:
                        analysis.severity = ConflictSeverity.HIGH
                        analysis.recommended_heuristic = (
                            MergeHeuristic.FAIL_RAPIDLY_ON_CONFLICT
                        )
                        analysis.diverging_symbols = ["bar"]

                mock_detect.side_effect = detect_side_effect

                result = self.checker.run(
                    ["main.py", "lib.py"], "base-ws", "ours-ws", "theirs-ws"
                )

        self.assertEqual(result.overall_severity, ConflictSeverity.HIGH)
        self.assertIn("lib.py", result.files_with_conflicts)
        self.assertFalse(result.safe_to_merge)

    def test_run_assigns_per_file_heuristics(self):
        """Each file gets assigned appropriate merge heuristic."""
        self.mock_client.query_ast.side_effect = [
            {"exports": []},
            {"exports": []},
            {"exports": []},
            {"exports": []},
            {"exports": []},
            {"exports": []},
        ]

        with patch.object(self.checker, "_detect_conflicts") as mock_detect:

            def assign_severity(analysis):
                if "safe" in analysis.path:
                    analysis.severity = ConflictSeverity.LOW
                    analysis.recommended_heuristic = (
                        MergeHeuristic.AST_SEMANTIC_ONLY
                    )
                else:
                    analysis.severity = ConflictSeverity.HIGH
                    analysis.recommended_heuristic = (
                        MergeHeuristic.FAIL_RAPIDLY_ON_CONFLICT
                    )

            mock_detect.side_effect = assign_severity

            result = self.checker.run(
                ["safe_file.py", "conflict_file.py"],
                "base-ws",
                "ours-ws",
                "theirs-ws",
            )

        self.assertEqual(
            result.file_heuristics["safe_file.py"], MergeHeuristic.AST_SEMANTIC_ONLY
        )
        self.assertEqual(
            result.file_heuristics["conflict_file.py"],
            MergeHeuristic.FAIL_RAPIDLY_ON_CONFLICT,
        )

    def test_run_returns_summary(self):
        """PreCheckResult includes human-readable summary."""
        self.mock_client.query_ast.side_effect = [
            {"exports": []},
            {"exports": []},
            {"exports": []},
        ]

        with patch.object(self.checker, "_detect_conflicts") as mock_detect:
            mock_detect.side_effect = lambda a: setattr(
                a, "severity", ConflictSeverity.NONE
            )

            result = self.checker.run(
                ["main.py"], "base-ws", "ours-ws", "theirs-ws"
            )

        self.assertIn("Analyzed", result.summary)
        self.assertIn("severity", result.summary)
        self.assertTrue(result.safe_to_merge)


if __name__ == "__main__":
    unittest.main()
