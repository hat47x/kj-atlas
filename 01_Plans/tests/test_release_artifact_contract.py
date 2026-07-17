import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "release.yml"
RELEASE_DOC_PATH = REPO_ROOT / "04_Documentation" / "release.md"


class ReleaseArtifactContractTest(unittest.TestCase):
    """RELEASE-DOC-01: release.md must describe what release.yml actually does.

    A tag push is a hard-to-reverse external state change; if the docs drift
    from the workflow, a maintainer can believe a tag distributed something it
    didn't (a registry push, a GitHub Release, a signed artifact).
    """

    @classmethod
    def setUpClass(cls):
        cls.workflow_text = WORKFLOW_PATH.read_text(encoding="utf-8")
        cls.doc_text = RELEASE_DOC_PATH.read_text(encoding="utf-8")

    def test_tag_pattern_matches_documented_format(self):
        self.assertIn(
            "v*.*.*",
            self.workflow_text,
            "release.yml's tag trigger pattern changed; update release.md's vX.Y.Z description to match.",
        )
        self.assertIn("vX.Y.Z", self.doc_text)

    def test_frontend_artifact_name_matches_documented_name(self):
        self.assertIn(
            "frontend-dist-${{ github.ref_name }}",
            self.workflow_text,
            "frontend artifact name changed in release.yml; update release.md's frontend-dist-<tag> description.",
        )
        self.assertIn("frontend-dist-<tag>", self.doc_text)

    def test_backend_image_stays_unpublished_and_doc_says_so(self):
        self.assertIn(
            "push: false",
            self.workflow_text,
            "backend job now pushes an image; release.md's no-distribution claim is stale.",
        )
        self.assertIn("kj-atlas-api:${{ github.ref_name }}", self.workflow_text)
        self.assertIn("kj-atlas-api:<tag>", self.doc_text)
        self.assertIn("push: false", self.doc_text)

    def test_release_workflow_does_not_run_the_test_suites(self):
        # release.yml intentionally never re-runs frontend/backend tests --
        # release.md's "リリース判断の流れ" is the only place those run, against
        # the exact commit SHA before it gets tagged. If a future workflow
        # change adds test execution here, release.md's claim becomes stale.
        for marker in ("npm run test", "pytest", "playwright test"):
            self.assertNotIn(
                marker,
                self.workflow_text,
                f"release.yml now runs {marker!r}; release.md's 'release.yml が再実行しない' claim is stale.",
            )


if __name__ == "__main__":
    unittest.main()
