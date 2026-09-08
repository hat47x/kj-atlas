import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DOGFOOD_DIR = ROOT / "01_Plans" / "dogfood"

# These are the corrected Round 1 manifest blobs after frozen historical paths
# were restored at R24.  The manifests are preregistered experiment inputs: a
# later lifecycle move must update current references, not rewrite this past
# snapshot.  A future experiment round gets a new manifest instead.
FROZEN_ROUND1_MANIFEST_BLOBS = {
    "cognitive-dogfood-case-001-round1-source-manifest.json":
        "7e0284d69b9d3646b37a6fc1fb92481edbac0256",
    "cognitive-dogfood-case-002-round1-source-manifest.json":
        "e888443feafd67d848d42f3ac5c0b8dc48050e47",
    "cognitive-dogfood-case-003-round1-source-manifest.json":
        "4e819c3dfe1e2bae43eb644e4fbb94b89d5e45fc",
}


def git_filtered_blob_oid(content: bytes, path: Path) -> str:
    """Return the Git blob id after repository clean filters, without reading history."""
    relative_path = path.relative_to(ROOT).as_posix()
    completed = subprocess.run(
        [
            "git",
            "-C",
            str(ROOT),
            "hash-object",
            "--stdin",
            f"--path={relative_path}",
        ],
        input=content,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    return completed.stdout.decode("ascii").strip()


class FrozenDogfoodManifestIdentityTest(unittest.TestCase):
    def test_round1_source_manifests_keep_preregistered_blob_identity(self):
        for filename, expected_oid in FROZEN_ROUND1_MANIFEST_BLOBS.items():
            with self.subTest(filename=filename):
                path = DOGFOOD_DIR / filename
                content = path.read_bytes()
                self.assertEqual(
                    git_filtered_blob_oid(content, path),
                    expected_oid,
                    msg=(
                        f"{filename} is a frozen Round 1 input. Do not follow "
                        "current lifecycle paths inside it; create a later-round "
                        "manifest for a genuinely new experiment input."
                    ),
                )

    def test_worktree_crlf_representation_keeps_frozen_git_blob_identity(self):
        path = DOGFOOD_DIR / "cognitive-dogfood-case-001-round1-source-manifest.json"
        working_tree = path.read_bytes()
        lf_content = working_tree.replace(b"\r\n", b"\n")
        crlf_content = lf_content.replace(b"\n", b"\r\n")
        expected_oid = FROZEN_ROUND1_MANIFEST_BLOBS[path.name]

        self.assertEqual(git_filtered_blob_oid(lf_content, path), expected_oid)
        self.assertEqual(git_filtered_blob_oid(crlf_content, path), expected_oid)

    def test_case002_current_done_path_rewrite_is_not_the_frozen_blob(self):
        path = DOGFOOD_DIR / "cognitive-dogfood-case-002-round1-source-manifest.json"
        frozen = path.read_bytes()
        old = (
            b'"path": "01_Plans/issues/'
            b'issue-AI-ROUTE-01-multi-model-routing-and-final-judgment-boundary.md"'
        )
        current = (
            b'"path": "01_Plans/issues/done/'
            b'issue-AI-ROUTE-01-multi-model-routing-and-final-judgment-boundary.md"'
        )
        self.assertIn(old, frozen)
        rewritten = frozen.replace(old, current, 1)
        self.assertNotEqual(
            git_filtered_blob_oid(rewritten, path),
            FROZEN_ROUND1_MANIFEST_BLOBS[path.name],
        )


if __name__ == "__main__":
    unittest.main()
