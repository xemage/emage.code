"""Tests for the Phase 6 kill-switch primitive (T502, `plan-035` nominal
T466) -- `implementation/runtime/kill_switch.py` and its CLI wrapper
`implementation/scripts/kill-switch.py`.

Exercises only this task's own deliverable via its exposed API and real CLI
invocation, with no dependency on `implementation/sia/`, T501's new module,
or any other Phase 6 code -- proving `docs/tasks/task-T502.md`'s "generic,
reusable primitive... built and proven correct in isolation" requirement.

Covers both required properties from the task's Objective section:
1. Halt is detectable, and the signal persists across a real process
   boundary (a fresh subprocess, not the one that set it, observes it).
2. A halted state cannot self-resume: repeated `is_halted()` / `status`
   calls never clear the signal, there is no automatic expiry, and the
   module/CLI expose no resume/clear/reset path at all (decision (a) in the
   task brief -- see `docs/artifacts/phase6-kill-switch-v1.md`).
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CLI_SCRIPT = REPO_ROOT / "implementation" / "scripts" / "kill-switch.py"

from implementation.runtime import kill_switch  # noqa: E402


class TestKillSwitchLibrary(unittest.TestCase):
    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmpdir.cleanup)
        self.halt_file = Path(self._tmpdir.name) / "HALT"

    def test_not_halted_when_signal_file_absent(self):
        self.assertFalse(kill_switch.is_halted(self.halt_file))

    def test_halt_sets_a_detectable_signal(self):
        kill_switch.halt(self.halt_file, reason="unit test")
        self.assertTrue(kill_switch.is_halted(self.halt_file))

    def test_halt_signal_is_a_real_file_on_disk(self):
        kill_switch.halt(self.halt_file)
        self.assertTrue(self.halt_file.exists())
        self.assertTrue(self.halt_file.is_file())
        contents = self.halt_file.read_text(encoding="utf-8")
        self.assertIn("halted_at=", contents)

    def test_repeated_is_halted_calls_never_clear_the_signal(self):
        kill_switch.halt(self.halt_file)
        for _ in range(10):
            self.assertTrue(kill_switch.is_halted(self.halt_file))
        self.assertTrue(self.halt_file.exists())

    def test_repeated_halt_calls_stay_halted(self):
        kill_switch.halt(self.halt_file)
        kill_switch.halt(self.halt_file)
        kill_switch.halt(self.halt_file, reason="second reason")
        self.assertTrue(kill_switch.is_halted(self.halt_file))

    def test_no_automatic_expiry_even_with_a_very_old_timestamp(self):
        kill_switch.halt(self.halt_file)
        very_old = time.time() - (365 * 24 * 60 * 60)
        os.utime(self.halt_file, (very_old, very_old))
        self.assertTrue(kill_switch.is_halted(self.halt_file))

    def test_module_exposes_no_resume_clear_or_reset_function(self):
        # Decision (a) from task-T502.md's Objective section 2: no
        # programmatic resume path exists anywhere in this deliverable.
        # Assert this at the module's actual public surface, not just prose.
        forbidden_names = {"resume", "clear", "reset", "unhalt", "clear_halt", "resume_halt", "delete_halt"}
        exported = {name for name in dir(kill_switch) if not name.startswith("_")}
        self.assertTrue(forbidden_names.isdisjoint(exported), f"found forbidden name(s): {forbidden_names & exported}")

    def test_env_var_override_resolves_path(self):
        custom = Path(self._tmpdir.name) / "custom-HALT"
        old = os.environ.get(kill_switch.ENV_VAR)
        os.environ[kill_switch.ENV_VAR] = str(custom)
        try:
            self.assertEqual(kill_switch.resolve_halt_file(), custom)
        finally:
            if old is None:
                del os.environ[kill_switch.ENV_VAR]
            else:
                os.environ[kill_switch.ENV_VAR] = old

    def test_explicit_path_wins_over_env_var(self):
        env_path = Path(self._tmpdir.name) / "env-HALT"
        explicit_path = Path(self._tmpdir.name) / "explicit-HALT"
        old = os.environ.get(kill_switch.ENV_VAR)
        os.environ[kill_switch.ENV_VAR] = str(env_path)
        try:
            self.assertEqual(kill_switch.resolve_halt_file(explicit_path), explicit_path)
        finally:
            if old is None:
                del os.environ[kill_switch.ENV_VAR]
            else:
                os.environ[kill_switch.ENV_VAR] = old

    def test_default_halt_file_lives_under_gitignored_tmp(self):
        # Confirms the documented default never risks landing in git status
        # without this task needing to touch .gitignore (outside its
        # file-ownership scope per task-T502.md's Constraints section).
        self.assertEqual(kill_switch.DEFAULT_HALT_FILE, kill_switch.REPO_ROOT / "tmp" / "kill-switch" / "HALT")


class TestKillSwitchCli(unittest.TestCase):
    """Exercises the real, documented command via subprocess -- proving the
    halt signal is process-independent: the CLI process that sets it exits
    completely before a separate, freshly-started process checks it."""

    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmpdir.cleanup)
        self.halt_file = Path(self._tmpdir.name) / "HALT"

    def _run_cli(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(CLI_SCRIPT), *args],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
            check=False,
        )

    def test_status_before_halt_reports_not_halted(self):
        result = self._run_cli("status", "--file", str(self.halt_file))
        self.assertEqual(result.returncode, 0)
        self.assertIn("NOT HALTED", result.stdout)

    def test_halt_command_sets_a_signal_a_fresh_process_can_detect(self):
        halt_result = self._run_cli("halt", "--file", str(self.halt_file), "--reason", "T502 CLI test")
        self.assertEqual(halt_result.returncode, 0)
        self.assertTrue(self.halt_file.exists())

        # A brand-new, unrelated process (never the one that set the halt)
        # checks the signal -- this is the process-boundary / durability proof.
        status_result = self._run_cli("status", "--file", str(self.halt_file))
        self.assertEqual(status_result.returncode, 1)
        self.assertIn("HALTED", status_result.stdout)

    def test_repeated_status_calls_after_halt_never_clear_it(self):
        self._run_cli("halt", "--file", str(self.halt_file))
        for _ in range(5):
            result = self._run_cli("status", "--file", str(self.halt_file))
            self.assertEqual(result.returncode, 1)
        self.assertTrue(self.halt_file.exists())

    def test_cli_exposes_exactly_halt_and_status_subcommands(self):
        # The help text deliberately documents the *absence* of a resume path
        # in prose (so it legitimately contains the word "resume"), so this
        # asserts against argparse's actual subcommand choices instead of a
        # raw substring search of the help text.
        result = self._run_cli("--help")
        self.assertIn("{halt,status}", result.stdout)

    def test_invoking_resume_as_a_subcommand_fails_with_nonzero_exit(self):
        # Confirms there is no hidden/undocumented resume subcommand either.
        result = self._run_cli("resume", "--file", str(self.halt_file))
        self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
