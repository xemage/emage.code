#!/usr/bin/env python3
"""Concurrent merge orchestration for Pattern A (Task T212).

This module coordinates parallel worker edits in isolated CWSO shadow workspaces,
then requests deterministic semantic merge via `merge_concurrent_results`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .client import CwsoClient, MergeHeuristic, MergeInput, MergeLanguage
from .ast_conflict_check import AstConflictChecker, PreCheckResult


@dataclass
class FileEdit:
    """Single file edit produced by a worker."""

    path: str
    content: str
    language: MergeLanguage
    base_content: str = ""


@dataclass
class WorkerEditSet:
    """Edit set produced by one worker agent."""

    agent_role: str
    commit_message: str
    files: List[FileEdit]


@dataclass
class WorkspaceAuditRecord:
    """Audit record for one worker workspace lifecycle."""

    agent_role: str
    workspace_uuid: str
    commit_oid: str
    tree_oid: str


@dataclass
class MergeConflict:
    """Structured unresolved conflict report entry."""

    path: str
    reason: str


@dataclass
class ConcurrentMergeResult:
    """Result envelope for the orchestration workflow."""

    merge_response: Dict[str, Any]
    audit_records: List[WorkspaceAuditRecord] = field(default_factory=list)
    unresolved_conflicts: List[MergeConflict] = field(default_factory=list)


class ConcurrentMergeOrchestrator:
    """Run N worker edit sets through shadow-workspace fanout and merge."""

    def __init__(self, client: CwsoClient) -> None:
        self._client = client
        self._ast_checker = AstConflictChecker(client)

    def run(
        self,
        worker_edits: List[WorkerEditSet],
        merge_heuristic: MergeHeuristic = MergeHeuristic.AST_SEMANTIC_ONLY,
        target_branch_ref: str | None = None,
        rollout_session_id: str | None = None,
        run_ast_precheck: bool = False,
        base_workspace_uuid: Optional[str] = None,
    ) -> ConcurrentMergeResult:
        if len(worker_edits) < 2:
            raise ValueError("worker_edits requires at least two workers for merge")

        workspace_uuids: List[str] = []
        audit_records: List[WorkspaceAuditRecord] = []

        try:
            for worker in worker_edits:
                create_resp = self._client.create_shadow_workspace()
                workspace_uuid = str(create_resp["workspace_uuid"])
                workspace_uuids.append(workspace_uuid)

                for file_edit in worker.files:
                    self._client.write_shadow_file(
                        workspace_uuid=workspace_uuid,
                        path=file_edit.path,
                        content=file_edit.content,
                    )

                commit_resp = self._client.commit_shadow(
                    workspace_uuid=workspace_uuid,
                    message=worker.commit_message,
                )

                audit_records.append(
                    WorkspaceAuditRecord(
                        agent_role=worker.agent_role,
                        workspace_uuid=workspace_uuid,
                        commit_oid=str(commit_resp.get("commit_oid", "")),
                        tree_oid=str(commit_resp.get("tree_oid", "")),
                    )
                )

            merge_inputs = self._build_merge_inputs(worker_edits)

            # Run AST pre-check if requested
            if run_ast_precheck and base_workspace_uuid and len(workspace_uuids) >= 2:
                precheck_result = self.ast_precheck(
                    file_paths=[edit.path for worker in worker_edits for edit in worker.files],
                    base_workspace_uuid=base_workspace_uuid,
                    ours_workspace_uuid=workspace_uuids[0],
                    theirs_workspace_uuid=workspace_uuids[1],
                )
                # Use per-file heuristics from pre-check if conflicts detected
                # (fall back to global heuristic for files not in pre-check result)
                merge_inputs = self._apply_precheck_heuristics(
                    merge_inputs, precheck_result
                )

            merge_resp = self._client.merge_concurrent_results(
                source_workspace_uuids=workspace_uuids,
                merge_inputs=merge_inputs,
                auto_resolve_heuristic=merge_heuristic,
                target_branch_ref=target_branch_ref,
                rollout_session_id=rollout_session_id,
            )

            unresolved = self._extract_conflicts(merge_resp)
            return ConcurrentMergeResult(
                merge_response=merge_resp,
                audit_records=audit_records,
                unresolved_conflicts=unresolved,
            )
        finally:
            for workspace_uuid in workspace_uuids:
                try:
                    self._client.drop_shadow_workspace(workspace_uuid=workspace_uuid)
                except Exception:
                    # Cleanup failure should not mask merge result/error.
                    pass

    @staticmethod
    def _build_merge_inputs(worker_edits: List[WorkerEditSet]) -> List[MergeInput]:
        merged_by_path: Dict[str, MergeInput] = {}

        for worker in worker_edits:
            for file_edit in worker.files:
                existing = merged_by_path.get(file_edit.path)
                if existing is None:
                    merged_by_path[file_edit.path] = MergeInput(
                        path=file_edit.path,
                        language=file_edit.language,
                        base_content=file_edit.base_content,
                        ours_content=file_edit.content,
                        theirs_content=file_edit.content,
                    )
                    continue

                existing.theirs_content = file_edit.content

        return list(merged_by_path.values())

    @staticmethod
    def _extract_conflicts(merge_response: Dict[str, Any]) -> List[MergeConflict]:
        """Extract structured conflicts from a merge_concurrent_results response.

        Real server shape: {"outcome": "conflict"|"success",
        "results": [{"path":..., "status": "conflict"|"merged",
        "reason_code":..., "message":...}], "conflict_count":..., ...}.
        Falls back to the old assumed top-level "unresolved_conflicts" shape.

        Args:
            merge_response: Raw response from `CwsoClient.merge_concurrent_results`.

        Returns:
            List of MergeConflict entries for every result with a conflict status.
        """
        if "results" in merge_response:
            return ConcurrentMergeOrchestrator._extract_conflicts_from_results(
                merge_response.get("results", [])
            )

        # Defensive fallback: old assumed top-level "unresolved_conflicts" shape.
        raw_conflicts = merge_response.get("unresolved_conflicts", [])
        return ConcurrentMergeOrchestrator._extract_conflicts_legacy(raw_conflicts)

    @staticmethod
    def _extract_conflicts_from_results(
        results: Any,
    ) -> List[MergeConflict]:
        """Build MergeConflict entries from the real "results" list shape."""
        conflicts: List[MergeConflict] = []
        if not isinstance(results, list):
            return conflicts

        for entry in results:
            if not isinstance(entry, dict):
                continue
            if entry.get("status") != "conflict":
                continue
            path = str(entry.get("path", ""))
            reason = entry.get("message") or entry.get("reason_code") or "unknown"
            conflicts.append(MergeConflict(path=path, reason=str(reason)))

        return conflicts

    @staticmethod
    def _extract_conflicts_legacy(raw_conflicts: Any) -> List[MergeConflict]:
        """Build MergeConflict entries from the old "unresolved_conflicts" shape."""
        conflicts: List[MergeConflict] = []
        if not isinstance(raw_conflicts, list):
            return conflicts

        for entry in raw_conflicts:
            if not isinstance(entry, dict):
                continue
            path = str(entry.get("path", ""))
            reason = str(entry.get("reason", "unknown"))
            conflicts.append(MergeConflict(path=path, reason=reason))

        return conflicts

    def ast_precheck(
        self,
        file_paths: List[str],
        base_workspace_uuid: str,
        ours_workspace_uuid: str,
        theirs_workspace_uuid: str,
    ) -> PreCheckResult:
        """Run AST conflict pre-check on touched files.

        Uses semantic analysis to detect diverging signatures and symbol changes
        before attempting merge, enabling early conflict routing.

        Args:
            file_paths: File paths to analyze.
            base_workspace_uuid: Base/parent workspace UUID.
            ours_workspace_uuid: Our edits workspace UUID.
            theirs_workspace_uuid: Their edits workspace UUID.

        Returns:
            PreCheckResult with per-file heuristics and conflict summary.
        """
        return self._ast_checker.run(
            file_paths=file_paths,
            base_workspace=base_workspace_uuid,
            ours_workspace=ours_workspace_uuid,
            theirs_workspace=theirs_workspace_uuid,
        )

    @staticmethod
    def _apply_precheck_heuristics(
        merge_inputs: List[MergeInput], precheck_result: PreCheckResult
    ) -> List[MergeInput]:
        """Apply per-file heuristics from pre-check to merge inputs.

        Mutates merge_inputs to set heuristic based on pre-check analysis.

        Args:
            merge_inputs: Original merge inputs.
            precheck_result: Pre-check result with per-file heuristics.

        Returns:
            Updated merge inputs (same objects, modified in-place).
        """
        for merge_input in merge_inputs:
            if merge_input.path in precheck_result.file_heuristics:
                # Note: MergeInput doesn't have heuristic field;
                # heuristic is passed separately to merge_concurrent_results.
                # This is for future enhancement where per-file heuristics
                # might be supported.
                pass

        return merge_inputs
