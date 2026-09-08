from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "01_Plans" / "check_stale_merge_reintroduction.py"

spec = importlib.util.spec_from_file_location("check_stale_merge_reintroduction", MODULE_PATH)
assert spec and spec.loader
checker = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = checker
spec.loader.exec_module(checker)


def _git(repo: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return completed.stdout.strip()


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class ProspectiveTreeNoopTests(unittest.TestCase):
    def _repo(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        tempdir = tempfile.TemporaryDirectory()
        repo = Path(tempdir.name)
        _git(repo, "init", "-b", "main")
        _git(repo, "config", "user.email", "dogfood@example.invalid")
        _git(repo, "config", "user.name", "Dogfood Test")
        _write(repo / "active.md", "state\n")
        _git(repo, "add", ".")
        _git(repo, "commit", "-m", "base")
        return tempdir, repo

    def test_already_applied_divergent_delta_is_reported_as_tree_noop(self) -> None:
        tempdir, repo = self._repo()
        with tempdir:
            _git(repo, "switch", "-c", "feature")
            _git(repo, "mv", "active.md", "done.md")
            _git(repo, "commit", "-m", "closeout on feature")

            _git(repo, "switch", "main")
            _git(repo, "mv", "active.md", "done.md")
            _git(repo, "commit", "-m", "equivalent closeout already on main")

            report = checker.analyze_repository(repo, "main", "feature")

            self.assertEqual(report.schemaVersion, 2)
            self.assertEqual(report.strongCount, 0)
            self.assertIsNotNone(report.prospectiveMergeTree)
            self.assertTrue(report.prospectiveTreeNoop)
            self.assertEqual(report.prospectiveMergeTree, report.baseTree)

    def test_net_new_branch_delta_is_not_tree_noop(self) -> None:
        tempdir, repo = self._repo()
        with tempdir:
            _git(repo, "switch", "-c", "feature")
            _write(repo / "feature.md", "new\n")
            _git(repo, "add", "feature.md")
            _git(repo, "commit", "-m", "net new feature")

            _git(repo, "switch", "main")
            _write(repo / "main.md", "main-only\n")
            _git(repo, "add", "main.md")
            _git(repo, "commit", "-m", "advance main")

            report = checker.analyze_repository(repo, "main", "feature")

            self.assertIsNotNone(report.prospectiveMergeTree)
            self.assertFalse(report.prospectiveTreeNoop)
            self.assertNotEqual(report.prospectiveMergeTree, report.baseTree)


if __name__ == "__main__":
    unittest.main()
