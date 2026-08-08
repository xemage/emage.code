"""AST-aware conflict pre-check for concurrent edits.

Detects semantic conflicts (diverging signatures, export changes) before
merge invocation to select appropriate merge heuristics and route to
conflict resolution early.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set
import json

from .client import CwsoClient, QueryType, MergeHeuristic, MergeLanguage


class ConflictSeverity(Enum):
    """Conflict severity levels."""
    NONE = "none"  # No conflicts detected
    LOW = "low"  # Independent edits, safe to merge
    MEDIUM = "medium"  # Signature changes, requires care
    HIGH = "high"  # Diverging signatures, will conflict


@dataclass
class SymbolChange:
    """Represents a change to a code symbol."""
    symbol_name: str
    change_type: str  # "added", "modified", "deleted"
    signature: Optional[str] = None
    source_workspace_uuid: Optional[str] = None


@dataclass
class FileConflictAnalysis:
    """Analysis of conflicts in a single file."""
    path: str
    language: str
    base_symbols: Set[str] = field(default_factory=set)
    ours_symbols: Set[str] = field(default_factory=set)
    theirs_symbols: Set[str] = field(default_factory=set)
    ours_signatures: Dict[str, str] = field(default_factory=dict)
    theirs_signatures: Dict[str, str] = field(default_factory=dict)
    severity: ConflictSeverity = ConflictSeverity.NONE
    recommended_heuristic: MergeHeuristic = MergeHeuristic.AST_SEMANTIC_ONLY
    diverging_symbols: List[str] = field(default_factory=list)
    conflicting_edits: List[str] = field(default_factory=list)


@dataclass
class PreCheckResult:
    """Result of AST conflict pre-check."""
    all_files: List[FileConflictAnalysis]
    overall_severity: ConflictSeverity
    file_heuristics: Dict[str, MergeHeuristic]  # path -> heuristic
    files_with_conflicts: List[str]  # paths with detected conflicts
    safe_to_merge: bool
    summary: str


class AstConflictChecker:
    """Pre-check orchestrator using AST queries to detect semantic conflicts."""

    def __init__(self, cwso_client: CwsoClient):
        """Initialize with CWSO client.

        Args:
            cwso_client: Authenticated CwsoClient for query_ast calls.
        """
        self.client = cwso_client
        self._language_map = {
            ".py": MergeLanguage.PYTHON,
            ".go": MergeLanguage.GO,
            ".rs": MergeLanguage.RUST,
            ".ts": MergeLanguage.TYPESCRIPT,
            ".tsx": MergeLanguage.TYPESCRIPT,
            ".js": MergeLanguage.TYPESCRIPT,  # Treat as TS for AST
        }

    def _detect_language(self, path: str) -> Optional[str]:
        """Detect language from file extension.

        Args:
            path: File path.

        Returns:
            Language string or None if unsupported.
        """
        for ext, lang in self._language_map.items():
            if path.endswith(ext):
                return lang.value
        return None

    def _query_exports(self, workspace_uuid: str, path: str) -> Set[str]:
        """Query top-level exports/symbols from a file.

        Args:
            workspace_uuid: Workspace UUID to query.
            path: File path within workspace.

        Returns:
            Set of exported symbol names.
        """
        try:
            lang = self._detect_language(path)
            if not lang:
                return set()

            result = self.client.query_ast(
                workspace_uuid=workspace_uuid,
                path=path,
                query_type=QueryType.LIST_EXPORTS,
                target_symbol=None,
            )

            if not isinstance(result, dict):
                return set()

            # Real server shape: {"hits": [{"kind": ..., "name": ...}, ...], ...}
            if "hits" in result:
                hits = result["hits"]
                if not isinstance(hits, list):
                    return set()
                return {
                    hit["name"]
                    for hit in hits
                    if isinstance(hit, dict) and "name" in hit
                }

            # Defensive fallback: old assumed top-level "exports" key shape.
            if "exports" in result:
                return set(result["exports"])

            return set()
        except Exception:
            # Graceful fallback: if AST query fails, assume no exports known
            return set()

    @staticmethod
    def _extract_signature(result: object) -> Optional[str]:
        """Extract a signature string from a query_ast EXTRACT_SIGNATURE response.

        Handles the real server shape (`{"hits": [{"signature": ...}, ...]}`)
        with a defensive fallback to the old assumed top-level `"signature"`
        key shape.

        Args:
            result: Raw response from `CwsoClient.query_ast`.

        Returns:
            The signature string if found, else None.
        """
        if not isinstance(result, dict):
            return None

        # Real server shape: {"hits": [{"kind": ..., "signature": ...}], ...}
        if "hits" in result:
            hits = result["hits"]
            if not isinstance(hits, list):
                return None
            for hit in hits:
                if isinstance(hit, dict) and "signature" in hit:
                    return hit["signature"]
            return None

        # Defensive fallback: old assumed top-level "signature" key shape.
        if "signature" in result:
            return result["signature"]

        return None

    def _query_signatures(
        self, workspace_uuid: str, path: str, symbols: Set[str]
    ) -> Dict[str, str]:
        """Query function/type signatures for given symbols.

        Args:
            workspace_uuid: Workspace UUID.
            path: File path.
            symbols: Symbol names to query.

        Returns:
            Dict mapping symbol name to signature string.
        """
        sigs = {}
        for symbol in symbols:
            try:
                result = self.client.query_ast(
                    workspace_uuid=workspace_uuid,
                    path=path,
                    query_type=QueryType.EXTRACT_SIGNATURE,
                    target_symbol=symbol,
                )

                signature = self._extract_signature(result)
                if signature is not None:
                    sigs[symbol] = signature
            except Exception:
                # If signature extraction fails, treat as unknown
                pass

        return sigs

    def analyze_file(
        self,
        path: str,
        base_workspace: str,
        ours_workspace: str,
        theirs_workspace: str,
    ) -> FileConflictAnalysis:
        """Analyze a single file across base/ours/theirs for conflicts.

        Args:
            path: File path.
            base_workspace: Base/parent workspace UUID.
            ours_workspace: Our edits workspace UUID.
            theirs_workspace: Their edits workspace UUID.

        Returns:
            FileConflictAnalysis with detected conflicts.
        """
        analysis = FileConflictAnalysis(
            path=path,
            language=self._detect_language(path) or "unknown",
        )

        # Query exports from each version
        analysis.base_symbols = self._query_exports(base_workspace, path)
        analysis.ours_symbols = self._query_exports(ours_workspace, path)
        analysis.theirs_symbols = self._query_exports(theirs_workspace, path)

        # Query signatures for all touched symbols
        all_symbols = (
            analysis.base_symbols
            | analysis.ours_symbols
            | analysis.theirs_symbols
        )
        analysis.ours_signatures = self._query_signatures(
            ours_workspace, path, all_symbols
        )
        analysis.theirs_signatures = self._query_signatures(
            theirs_workspace, path, all_symbols
        )

        # Detect conflicts
        self._detect_conflicts(analysis)

        return analysis

    def _detect_conflicts(self, analysis: FileConflictAnalysis) -> None:
        """Populate conflict info in analysis object (mutates).

        Args:
            analysis: FileConflictAnalysis to populate.
        """
        # Track symbols with diverging edits
        added_ours = analysis.ours_symbols - analysis.base_symbols
        added_theirs = analysis.theirs_symbols - analysis.base_symbols
        removed_ours = analysis.base_symbols - analysis.ours_symbols
        removed_theirs = analysis.base_symbols - analysis.theirs_symbols

        # Modified symbols: signature changed
        modified_ours = set()
        modified_theirs = set()

        for sym in analysis.base_symbols & analysis.ours_symbols:
            base_sig = None  # Would need to query base, omit for now
            if sym in analysis.ours_signatures and base_sig != analysis.ours_signatures.get(sym):
                modified_ours.add(sym)

        for sym in analysis.base_symbols & analysis.theirs_symbols:
            if sym in analysis.theirs_signatures and analysis.theirs_signatures.get(sym):
                modified_theirs.add(sym)

        # Detect diverging edits (same symbol edited in both)
        shared_symbols = analysis.ours_symbols & analysis.theirs_symbols
        diverging = []

        for sym in shared_symbols:
            ours_sig = analysis.ours_signatures.get(sym)
            theirs_sig = analysis.theirs_signatures.get(sym)

            # If signatures differ, they diverge
            if ours_sig and theirs_sig and ours_sig != theirs_sig:
                diverging.append(sym)
                analysis.conflicting_edits.append(
                    f"{sym}: ours={ours_sig[:50]}... vs theirs={theirs_sig[:50]}..."
                )

        analysis.diverging_symbols = diverging

        # Determine severity
        if diverging:
            # Diverging signatures: must fail early to avoid corruption
            analysis.severity = ConflictSeverity.HIGH
            analysis.recommended_heuristic = (
                MergeHeuristic.FAIL_RAPIDLY_ON_CONFLICT
            )
        elif added_ours & added_theirs:
            # Simultaneous add of same symbol: conflict
            analysis.severity = ConflictSeverity.MEDIUM
            analysis.conflicting_edits.extend(
                [f"added_both: {s}" for s in added_ours & added_theirs]
            )
            analysis.recommended_heuristic = (
                MergeHeuristic.FAIL_RAPIDLY_ON_CONFLICT
            )
        else:
            # Independent edits (including both removing same symbol): safe
            analysis.severity = ConflictSeverity.LOW
            analysis.recommended_heuristic = MergeHeuristic.AST_SEMANTIC_ONLY

    def run(
        self,
        file_paths: List[str],
        base_workspace: str,
        ours_workspace: str,
        theirs_workspace: str,
    ) -> PreCheckResult:
        """Run conflict pre-check across all files.

        Args:
            file_paths: List of file paths to analyze.
            base_workspace: Base workspace UUID.
            ours_workspace: Our workspace UUID.
            theirs_workspace: Their workspace UUID.

        Returns:
            PreCheckResult with heuristic assignments and conflict summary.
        """
        analyses = []
        file_heuristics = {}
        max_severity = ConflictSeverity.NONE
        files_with_conflicts = []

        for path in file_paths:
            analysis = self.analyze_file(
                path, base_workspace, ours_workspace, theirs_workspace
            )
            analyses.append(analysis)
            file_heuristics[path] = analysis.recommended_heuristic

            if analysis.severity in (ConflictSeverity.MEDIUM, ConflictSeverity.HIGH):
                files_with_conflicts.append(path)

            # Track max severity
            severity_order = {
                ConflictSeverity.NONE: 0,
                ConflictSeverity.LOW: 1,
                ConflictSeverity.MEDIUM: 2,
                ConflictSeverity.HIGH: 3,
            }
            if severity_order[analysis.severity] > severity_order[max_severity]:
                max_severity = analysis.severity

        # Determine if safe to merge
        safe_to_merge = max_severity not in (
            ConflictSeverity.MEDIUM,
            ConflictSeverity.HIGH,
        )

        # Build summary
        summary_parts = [
            f"Analyzed {len(analyses)} file(s)",
            f"Overall severity: {max_severity.value}",
        ]
        if files_with_conflicts:
            summary_parts.append(
                f"Conflicts in: {', '.join(files_with_conflicts)}"
            )
        else:
            summary_parts.append("No conflicts detected")

        return PreCheckResult(
            all_files=analyses,
            overall_severity=max_severity,
            file_heuristics=file_heuristics,
            files_with_conflicts=files_with_conflicts,
            safe_to_merge=safe_to_merge,
            summary="; ".join(summary_parts),
        )
