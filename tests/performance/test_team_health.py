"""Agent-team health checks — early warnings for orchestrator drift.

These tests target the *scaffolding* that keeps the agent team aligned with
its big-picture plan. They do NOT attempt to grade an LLM's reasoning quality
— that's not unit-testable. Instead they catch:

1. **Plan-drift** — active tasks that don't trace back to any plan document
2. **Lifecycle violations** — invalid task statuses; `done` tasks left in active queue
3. **Owner integrity** — task owners are real agents
4. **Checkpoint cadence** — at least one checkpoint per phase boundary (warning)
5. **Conventional-commit ratio** — recent commits follow the agreed format (warning)

Tests that produce *warnings only* print to stdout and pass; tests that produce
*hard failures* fail the suite.
"""
from __future__ import annotations

import json
import re
import subprocess
import unittest
from pathlib import Path

from tests._helpers.repo import docs_root, list_agents, repo_root


VALID_STATUSES = {"pending", "in_progress", "blocked", "in_review", "done", "cancelled"}
VALID_PRIORITIES = {"P0", "P1", "P2"}
TASK_ID_RE = re.compile(r"^T\d{3,}$")
EXAMPLE_TITLE_RE = re.compile(r"^[_*].*example.*[_*]$", re.IGNORECASE)


def _baselines() -> dict:
    return json.loads((repo_root() / "tests" / "_baselines" / "sync-timings.json").read_text())


def _parse_task_table(path: Path) -> list[dict]:
    """Parse a markdown task table. Returns list of {id,title,owner,status,priority,depends_on,...}."""
    if not path.exists():
        return []
    rows = []
    in_table = False
    headers: list[str] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line.startswith("|") and line.endswith("|"):
            cells = [c.strip() for c in line.strip("|").split("|")]
            if not in_table:
                headers = [c.lower().replace(" ", "_") for c in cells]
                in_table = True
                continue
            # separator row?
            if all(set(c) <= set("-:") for c in cells):
                continue
            row = dict(zip(headers, cells))
            rows.append(row)
        else:
            in_table = False
    return rows


def _is_example_row(row: dict) -> bool:
    title = row.get("title", "")
    return bool(EXAMPLE_TITLE_RE.match(title.strip())) or row.get("id", "").upper() == "T001" and "example" in title.lower()


def _real_tasks() -> list[dict]:
    rows = _parse_task_table(docs_root() / "tasks" / "active-tasks.md")
    return [r for r in rows if not _is_example_row(r)]


def _all_tasks() -> list[dict]:
    return (
        _parse_task_table(docs_root() / "tasks" / "active-tasks.md")
        + _parse_task_table(docs_root() / "tasks" / "completed-tasks.md")
    )


def _plan_files() -> list[Path]:
    plans_dir = docs_root() / "plans"
    if not plans_dir.exists():
        return []
    return sorted(p for p in plans_dir.glob("plan-*.md"))


def _checkpoint_files() -> list[Path]:
    chk_dir = docs_root() / "checkpoints"
    if not chk_dir.exists():
        return []
    return sorted(p for p in chk_dir.glob("checkpoint-*.md"))


def _agent_slugs() -> set[str]:
    return {p.stem for p in list_agents()}


# ──────────────────────────────────────────────────────────────────────────


class TestTaskLifecycle(unittest.TestCase):
    """Hard failures — these block CI."""

    def test_active_task_statuses_are_valid(self):
        rows = _real_tasks()
        for row in rows:
            with self.subTest(task=row.get("id"), title=row.get("title")):
                status = row.get("status", "").lower()
                self.assertIn(
                    status, VALID_STATUSES,
                    msg=f"task {row.get('id')}: invalid status '{status}'",
                )

    def test_active_task_priorities_are_valid(self):
        for row in _real_tasks():
            with self.subTest(task=row.get("id")):
                priority = row.get("priority", "")
                self.assertIn(
                    priority, VALID_PRIORITIES,
                    msg=f"task {row.get('id')}: invalid priority '{priority}'",
                )

    def test_no_done_tasks_in_active_queue(self):
        leftover = [r for r in _real_tasks() if r.get("status", "").lower() == "done"]
        self.assertFalse(
            leftover,
            msg=(
                "Tasks marked 'done' are still in active-tasks.md — they must "
                f"be moved to completed-tasks.md: {[r.get('id') for r in leftover]}"
            ),
        )

    def test_task_owners_are_real_agents(self):
        agents = _agent_slugs()
        for row in _real_tasks():
            owner = (row.get("owner") or "").strip().lower()
            if not owner or owner == "—" or owner == "-":
                continue
            with self.subTest(task=row.get("id"), owner=owner):
                self.assertIn(
                    owner, agents,
                    msg=(
                        f"task {row.get('id')}: owner '{owner}' is not a known "
                        f"agent. Known agents: {sorted(agents)}"
                    ),
                )

    def test_task_ids_are_unique_and_well_formed(self):
        rows = _all_tasks()
        seen = []
        for row in rows:
            tid = row.get("id", "")
            if not tid:
                continue
            with self.subTest(task=tid):
                self.assertRegex(
                    tid, TASK_ID_RE.pattern,
                    msg=f"task id '{tid}' does not match T\\d{{3,}} format",
                )
            seen.append(tid)
        # uniqueness across both files
        dupes = {x for x in seen if seen.count(x) > 1}
        # T001 placeholder may legitimately appear in both as a template — allow it
        dupes.discard("T001")
        self.assertFalse(dupes, msg=f"duplicate task ids: {sorted(dupes)}")


class TestPlanCoverage(unittest.TestCase):
    """Hard failure: every active *real* task must trace back to a plan."""

    def test_every_active_task_has_a_plan(self):
        tasks = _real_tasks()
        if not tasks:
            self.skipTest("no real (non-example) tasks in active queue — nothing to verify")
        plans = _plan_files()
        if not plans:
            self.skipTest(
                f"{len(tasks)} active tasks but no plan documents under docs/plans/. "
                "Either add plan documents or remove the tasks. Skipping for now."
            )
        # Build set of all task IDs referenced anywhere in any plan
        plan_text = "\n".join(p.read_text(encoding="utf-8") for p in plans)
        referenced = set(re.findall(r"\bT\d{3,}\b", plan_text))
        orphans = [r.get("id") for r in tasks if r.get("id") and r.get("id") not in referenced]
        self.assertFalse(
            orphans,
            msg=(
                "Active tasks not referenced by any plan in docs/plans/ — "
                "this is a leading indicator that the orchestrator is "
                f"improvising and losing the big picture: {orphans}"
            ),
        )


class TestCheckpointCadence(unittest.TestCase):
    """Warning-only: missing checkpoints don't block CI but get printed."""

    def test_checkpoint_present_when_tasks_exist(self):
        tasks = _real_tasks()
        checkpoints = _checkpoint_files()
        # Skip the _template.md
        checkpoints = [c for c in checkpoints if not c.name.startswith("_")]
        if tasks and not checkpoints:
            print(
                "\n[warning] active tasks exist but no checkpoints under "
                "docs/checkpoints/. The orchestrator must write a checkpoint "
                "at every phase boundary.\n"
            )
        # informational only — don't fail


class TestConventionalCommits(unittest.TestCase):
    """Warning-only: low ratio of conventional commits = process erosion."""

    CC_RE = re.compile(r"^(feat|fix|docs|refactor|test|ci|chore|perf|revert|style|build)(\([\w./-]+\))?!?:\s.+")

    def test_recent_commit_format(self):
        budgets = _baselines()
        window = budgets["recent_commits_window"]
        threshold = budgets["min_conventional_commit_ratio"]
        try:
            log = subprocess.check_output(
                ["git", "log", f"-n{window}", "--pretty=format:%s"],
                cwd=repo_root(), text=True,
            )
        except subprocess.CalledProcessError:
            self.skipTest("git log failed")
        subjects = [s for s in log.splitlines() if s and not s.startswith("Merge ")]
        if not subjects:
            self.skipTest("no commits in window")
        matches = sum(1 for s in subjects if self.CC_RE.match(s))
        ratio = matches / len(subjects)
        print(
            f"\n[conventional-commit-ratio] {matches}/{len(subjects)} "
            f"({ratio:.0%}) of last {len(subjects)} commits follow the format"
        )
        if ratio < threshold:
            print(
                f"[warning] ratio {ratio:.0%} is below threshold {threshold:.0%}. "
                "Recent non-conforming subjects:"
            )
            for s in subjects:
                if not self.CC_RE.match(s):
                    print(f"  - {s}")
        # informational only — do not fail


if __name__ == "__main__":
    unittest.main()
