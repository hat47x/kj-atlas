from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
ISSUES_ROOT = REPO_ROOT / "01_Plans" / "issues"
DONE_ROOT = ISSUES_ROOT / "done"
MANIFEST = ISSUES_ROOT / "legacy_done_at_root_r18.json"


class LegacyDoneRootReferenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        raw = json.loads(MANIFEST.read_text(encoding="utf-8"))
        cls.legacy_names = tuple(raw["paths"])
        cls.manifest_count = raw["count"]

    def test_r18_legacy_done_memos_are_all_canonical_under_done(self) -> None:
        self.assertEqual(self.manifest_count, len(self.legacy_names))
        self.assertEqual(len(set(self.legacy_names)), len(self.legacy_names))

        misplaced: list[str] = []
        missing: list[str] = []
        for name in self.legacy_names:
            if (ISSUES_ROOT / name).exists():
                misplaced.append(name)
            if not (DONE_ROOT / name).is_file():
                missing.append(name)

        self.assertEqual(misplaced, [], f"legacy Done memo returned to active root: {misplaced}")
        self.assertEqual(missing, [], f"legacy Done canonical memo missing under done/: {missing}")

    def test_no_tracked_file_references_retired_legacy_root_paths(self) -> None:
        stale: list[str] = []
        for name in self.legacy_names:
            retired = f"01_Plans/issues/{name}"
            completed = subprocess.run(
                ["git", "grep", "-n", "-F", retired, "--", "."],
                cwd=REPO_ROOT,
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
            )
            self.assertIn(
                completed.returncode,
                (0, 1),
                completed.stderr.strip() or f"git grep failed for {retired}",
            )
            if completed.returncode == 0:
                stale.extend(completed.stdout.splitlines())

        self.assertEqual(
            stale,
            [],
            "retired legacy Done root paths are still referenced:\n" + "\n".join(stale),
        )


if __name__ == "__main__":
    unittest.main()
