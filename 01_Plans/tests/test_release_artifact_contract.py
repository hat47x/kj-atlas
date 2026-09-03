import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "release.yml"
RELEASE_DOC_PATH = REPO_ROOT / "04_Documentation" / "release.md"


class ReleaseArtifactContractTest(unittest.TestCase):
    """RELEASE-DOC-01: release.md must match the repository's automation state."""

    @classmethod
    def setUpClass(cls):
        cls.doc_text = RELEASE_DOC_PATH.read_text(encoding="utf-8")

    def test_tag_format_stays_documented(self):
        self.assertIn("vX.Y.Z", self.doc_text)

    def test_disabled_actions_state_is_explicit_when_workflow_is_absent(self):
        if WORKFLOW_PATH.is_file():
            self.skipTest("release workflow exists; enabled-workflow contract applies")

        self.assertIn("GitHub Actionsによる自動リリースは無効", self.doc_text)
        self.assertIn("自動生成される成果物はありません", self.doc_text)
        self.assertNotIn("frontend-dist-<tag>", self.doc_text)

    def test_workflow_artifact_contract_when_workflow_exists(self):
        if not WORKFLOW_PATH.is_file():
            self.skipTest("release workflow is intentionally absent")

        workflow_text = WORKFLOW_PATH.read_text(encoding="utf-8")
        self.assertIn(
            "v*.*.*",
            workflow_text,
            "release.yml's tag trigger pattern changed; update release.md's vX.Y.Z description to match.",
        )
        self.assertIn(
            "frontend-dist-${{ github.ref_name }}",
            workflow_text,
            "frontend artifact name changed; update release.md in the same change.",
        )
        self.assertIn("frontend-dist-<tag>", self.doc_text)
        self.assertIn("push: false", workflow_text)
        self.assertIn("kj-atlas-api:${{ github.ref_name }}", workflow_text)
        self.assertIn("kj-atlas-api:<tag>", self.doc_text)

        for marker in ("npm run test", "pytest", "playwright test"):
            self.assertNotIn(
                marker,
                workflow_text,
                f"release.yml now runs {marker!r}; update release.md's pre-tag verification contract.",
            )


if __name__ == "__main__":
    unittest.main()
