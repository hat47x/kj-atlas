from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "validate_active_issue_memos.py"
sys.path.insert(0, str(MODULE_PATH.parent))
SPEC = importlib.util.spec_from_file_location("validate_active_issue_memos", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)

LEGACY_DONE_AT_ROOT_MAX = MODULE.LEGACY_DONE_AT_ROOT_MAX
validate_done_at_root_legacy = MODULE.validate_done_at_root_legacy


class DoneAtRootLegacyTest(unittest.TestCase):
    def _write_done(self, root: Path, count: int) -> None:
        for index in range(count):
            (root / f"issue-legacy-{index:03d}.md").write_text(
                "- Status: Done\n",
                encoding="utf-8",
            )

    def test_legacy_ceiling_is_allowed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_done(root, LEGACY_DONE_AT_ROOT_MAX)

            errors = validate_done_at_root_legacy(root)

        self.assertEqual([], errors)

    def test_one_more_done_at_root_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_done(root, LEGACY_DONE_AT_ROOT_MAX + 1)

            errors = validate_done_at_root_legacy(root)

        self.assertTrue(any("legacy ceiling" in error for error in errors))

    def test_moving_legacy_done_out_of_root_never_requires_baseline_update(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_done(root, LEGACY_DONE_AT_ROOT_MAX - 1)

            errors = validate_done_at_root_legacy(root)

        self.assertEqual([], errors)

    def test_done_directory_is_canonical_and_does_not_count_against_legacy_ceiling(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_done(root, LEGACY_DONE_AT_ROOT_MAX)
            done_root = root / "done"
            done_root.mkdir()
            (done_root / "issue-newly-completed.md").write_text(
                "- Status: Done\n",
                encoding="utf-8",
            )

            errors = validate_done_at_root_legacy(root)

        self.assertEqual([], errors)


if __name__ == "__main__":
    unittest.main()
