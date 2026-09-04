import importlib.util
import io
import json
import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock

MODULE_PATH = Path(__file__).resolve().parent / "validate_dogfood_docs.py"
SPEC = importlib.util.spec_from_file_location("validate_dogfood_docs", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class ValidateDogfoodDocsTest(unittest.TestCase):
    def test_missing_frozen_commit_has_one_actionable_history_diagnostic(self):
        failure = subprocess.CalledProcessError(
            128,
            ["git", "cat-file"],
            stderr="fatal: Not a valid object name",
        )
        with mock.patch.object(MODULE.subprocess, "run", side_effect=failure):
            available, issue = MODULE.git_commit_available(MODULE.PRODUCT_COMMIT)

        self.assertFalse(available)
        self.assertIsNotNone(issue)
        self.assertIn(MODULE.PRODUCT_COMMIT, issue)
        self.assertIn("unavailable in local Git history", issue)
        self.assertIn("fetch", issue)

    def test_manifest_structure_is_checked_without_blob_resolution(self):
        with mock.patch.object(MODULE, "git_blob_at") as blob_lookup:
            issues = MODULE.validate_product_source_manifest(
                "case-001",
                20,
                verify_frozen_blobs=False,
            )

        self.assertEqual(issues, [])
        blob_lookup.assert_not_called()

    def test_available_history_keeps_every_registered_blob_check(self):
        manifest_path = (
            MODULE.DOGFOOD_DIR
            / "cognitive-dogfood-case-001-round1-source-manifest.json"
        )
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        expected_blobs = {
            source["path"]: source["blobSha"]
            for source in manifest["commonSources"]
        }

        def lookup(commit, path):
            self.assertEqual(commit, MODULE.PRODUCT_COMMIT)
            return expected_blobs[path], None

        with mock.patch.object(MODULE, "git_blob_at", side_effect=lookup) as blob_lookup:
            issues = MODULE.validate_product_source_manifest(
                "case-001",
                20,
                verify_frozen_blobs=True,
            )

        self.assertEqual(issues, [])
        self.assertEqual(blob_lookup.call_count, 20)

    def test_main_fails_once_for_missing_history_without_path_noise(self):
        message = (
            f"frozen product commit {MODULE.PRODUCT_COMMIT} is unavailable "
            "in local Git history; fetch it"
        )
        stdout = io.StringIO()
        with mock.patch.object(
            MODULE,
            "git_commit_available",
            return_value=(False, message),
        ), mock.patch("sys.stdout", stdout):
            result = MODULE.main()

        output = stdout.getvalue()
        self.assertEqual(result, 1)
        self.assertIn("ISSUES FOUND (1)", output)
        self.assertIn(message, output)
        self.assertNotIn("source cannot resolve at frozen commit", output)


if __name__ == "__main__":
    unittest.main()
