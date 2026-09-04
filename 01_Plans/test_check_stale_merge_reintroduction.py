from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from check_stale_merge_reintroduction import analyze_repository, main


class GitRepo:
    def __init__(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.git("init", "-b", "main")
        self.git("config", "user.name", "R22 Test")
        self.git("config", "user.email", "r22@example.invalid")

    def close(self) -> None:
        self._tmp.cleanup()

    def git(self, *args: str) -> str:
        completed = subprocess.run(
            ["git", "-C", str(self.root), *args],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        return completed.stdout.strip()

    def write(self, path: str, text: str) -> None:
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")

    def remove(self, path: str) -> None:
        (self.root / path).unlink()

    def commit_all(self, message: str) -> None:
        self.git("add", "-A")
        self.git("commit", "-m", message)

    def seed(self, files: dict[str, str]) -> str:
        for path, text in files.items():
            self.write(path, text)
        self.commit_all("seed")
        return self.git("rev-parse", "HEAD")


class StaleMergeReintroductionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repo = GitRepo()

    def tearDown(self) -> None:
        self.repo.close()

    def _branch_from_seed(self, files: dict[str, str]) -> str:
        seed = self.repo.seed(files)
        self.repo.git("branch", "feature", seed)
        return seed

    def test_non_overlapping_changes_are_clean(self) -> None:
        self._branch_from_seed({"base.txt": "base\n"})

        self.repo.write("main.txt", "main\n")
        self.repo.commit_all("main change")

        self.repo.git("checkout", "feature")
        self.repo.write("feature.txt", "feature\n")
        self.repo.commit_all("feature change")

        report = analyze_repository(self.repo.root, "main", "feature")
        self.assertEqual(report.overlapCount, 0)
        self.assertEqual(report.strongCount, 0)
        self.assertGreater(report.baseCommitsSinceMergeBase, 0)
        self.assertGreater(report.headCommitsSinceMergeBase, 0)

    def test_main_deleted_branch_present_is_strong_resurrection_candidate(self) -> None:
        self._branch_from_seed({"retired.txt": "old\n"})

        self.repo.remove("retired.txt")
        self.repo.commit_all("retire file")

        self.repo.git("checkout", "feature")
        self.repo.write("retired.txt", "old branch revision\n")
        self.repo.commit_all("touch old file")

        report = analyze_repository(self.repo.root, "main", "feature")
        self.assertEqual(report.strongCount, 1)
        finding = report.findings[0]
        self.assertEqual(finding.path, "retired.txt")
        self.assertEqual(finding.classification, "main_deleted_branch_present")
        self.assertEqual(finding.severity, "strong")
        self.assertFalse(finding.base_exists)
        self.assertTrue(finding.head_exists)

        exit_code = main(
            [
                "--repo-root",
                str(self.repo.root),
                "--base-ref",
                "main",
                "--head-ref",
                "feature",
                "--fail-on-strong",
                "--json",
            ]
        )
        self.assertEqual(exit_code, 2)

    def test_main_deletion_without_feature_touch_is_not_reintroduction(self) -> None:
        self._branch_from_seed({"retired.txt": "old\n"})

        self.repo.remove("retired.txt")
        self.repo.commit_all("retire file on main")

        self.repo.git("checkout", "feature")
        self.repo.write("feature.txt", "independent\n")
        self.repo.commit_all("feature changes elsewhere")
        # The old tree still contains retired.txt, but the feature did not change
        # that path from the merge-base. A normal three-way merge preserves the
        # main-side deletion, so tree presence alone must not be called stale
        # reintroduction.
        self.repo.git("cat-file", "-e", "feature:retired.txt")

        report = analyze_repository(self.repo.root, "main", "feature")
        self.assertEqual(report.overlapCount, 0)
        self.assertEqual(report.strongCount, 0)

    def test_same_path_modified_on_both_sides_is_review_not_failure(self) -> None:
        self._branch_from_seed({"shared.txt": "line1\nline2\n"})

        self.repo.write("shared.txt", "main-line1\nline2\n")
        self.repo.commit_all("main edits first line")

        self.repo.git("checkout", "feature")
        self.repo.write("shared.txt", "line1\nfeature-line2\n")
        self.repo.commit_all("feature edits second line")

        report = analyze_repository(self.repo.root, "main", "feature")
        self.assertEqual(report.overlapCount, 1)
        self.assertEqual(report.strongCount, 0)
        self.assertEqual(report.findings[0].classification, "overlap_review")
        self.assertEqual(report.findings[0].severity, "review")

    def test_branch_deletes_main_changed_present_path_is_strong(self) -> None:
        self._branch_from_seed({"contract.txt": "v1\n"})

        self.repo.write("contract.txt", "v2-main\n")
        self.repo.commit_all("main advances contract")

        self.repo.git("checkout", "feature")
        self.repo.remove("contract.txt")
        self.repo.commit_all("feature deletes old contract")

        report = analyze_repository(self.repo.root, "main", "feature")
        self.assertEqual(report.strongCount, 1)
        finding = report.findings[0]
        self.assertEqual(finding.classification, "branch_deletes_main_present")
        self.assertTrue(finding.base_exists)
        self.assertFalse(finding.head_exists)

    def test_feature_only_deletion_is_not_stale_reversal(self) -> None:
        self._branch_from_seed({"contract.txt": "v1\n"})

        self.repo.write("main.txt", "main advances elsewhere\n")
        self.repo.commit_all("main changes elsewhere")

        self.repo.git("checkout", "feature")
        self.repo.remove("contract.txt")
        self.repo.commit_all("feature intentionally deletes contract")

        report = analyze_repository(self.repo.root, "main", "feature")
        self.assertEqual(report.overlapCount, 0)
        self.assertEqual(report.strongCount, 0)

    def test_commit_distance_without_overlap_does_not_fail(self) -> None:
        self._branch_from_seed({"seed.txt": "seed\n"})

        for index in range(5):
            self.repo.write(f"main-{index}.txt", f"{index}\n")
            self.repo.commit_all(f"main distance {index}")

        self.repo.git("checkout", "feature")
        self.repo.write("feature.txt", "feature\n")
        self.repo.commit_all("feature independent")

        report = analyze_repository(self.repo.root, "main", "feature")
        self.assertEqual(report.baseCommitsSinceMergeBase, 5)
        self.assertEqual(report.overlapCount, 0)
        self.assertEqual(report.strongCount, 0)
        self.assertEqual(
            main(
                [
                    "--repo-root",
                    str(self.repo.root),
                    "--base-ref",
                    "main",
                    "--head-ref",
                    "feature",
                    "--fail-on-strong",
                ]
            ),
            0,
        )


if __name__ == "__main__":
    unittest.main()
