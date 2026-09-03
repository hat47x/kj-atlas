from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "validate_active_issue_memos.py"
sys.path.insert(0, str(MODULE_PATH.parent))
SPEC = importlib.util.spec_from_file_location("validate_active_issue_memos", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def write_issue(path: Path, status: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"# Issue\n\n- Status: {status}\n", encoding="utf-8")


class IssueLifecycleContractTests(unittest.TestCase):
    def test_checked_in_done_at_root_baseline_is_non_blocking(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_issue(root / "issue-a.md", "Done")
            write_issue(root / "issue-b.md", "Done")

            self.assertEqual(
                MODULE.validate_done_memo_location(root, legacy_baseline=2),
                [],
            )

    def test_done_at_root_growth_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_issue(root / "issue-a.md", "Done")
            write_issue(root / "issue-b.md", "Done")
            write_issue(root / "issue-c.md", "Done")

            errors = MODULE.validate_done_memo_location(root, legacy_baseline=2)

            self.assertEqual(len(errors), 1)
            self.assertIn("3 > 2", errors[0])
            self.assertIn("01_Plans/issues/done/", errors[0])

    def test_baseline_must_be_lowered_when_legacy_count_shrinks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_issue(root / "issue-a.md", "Done")

            errors = MODULE.validate_done_memo_location(root, legacy_baseline=2)

            self.assertEqual(len(errors), 1)
            self.assertIn("1 < 2", errors[0])
            self.assertIn("LEGACY_DONE_AT_ROOT_BASELINE to 1", errors[0])

    def test_done_directory_does_not_consume_root_legacy_baseline(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_issue(root / "issue-a.md", "Done")
            write_issue(root / "issue-b.md", "Done")
            write_issue(root / "done" / "issue-c.md", "Done")

            self.assertEqual(
                MODULE.validate_done_memo_location(root, legacy_baseline=2),
                [],
            )

    def test_unified_validate_does_not_apply_repo_baseline_to_synthetic_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            self.assertEqual(MODULE.validate(root), [])

    def test_unified_validate_can_explicitly_enforce_fixture_baseline(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_issue(root / "issue-a.md", "Done")
            write_issue(root / "issue-b.md", "Done")
            write_issue(root / "issue-c.md", "Done")

            errors = MODULE.validate(
                root,
                enforce_done_baseline=True,
                legacy_done_baseline=2,
            )

            self.assertEqual(len(errors), 1)
            self.assertIn("3 > 2", errors[0])


if __name__ == "__main__":
    unittest.main()
