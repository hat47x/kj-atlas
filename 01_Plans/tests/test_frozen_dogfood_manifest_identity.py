import hashlib
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


def git_blob_oid(content: bytes) -> str:
    """Return Git's SHA-1 object id for file bytes without requiring Git history."""
    header = f"blob {len(content)}\0".encode("ascii")
    return hashlib.sha1(header + content).hexdigest()


class FrozenDogfoodManifestIdentityTest(unittest.TestCase):
    def test_round1_source_manifests_keep_preregistered_blob_identity(self):
        for filename, expected_oid in FROZEN_ROUND1_MANIFEST_BLOBS.items():
            with self.subTest(filename=filename):
                content = (DOGFOOD_DIR / filename).read_bytes()
                self.assertEqual(
                    git_blob_oid(content),
                    expected_oid,
                    msg=(
                        f"{filename} is a frozen Round 1 input. Do not follow "
                        "current lifecycle paths inside it; create a later-round "
                        "manifest for a genuinely new experiment input."
                    ),
                )

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
            git_blob_oid(rewritten),
            FROZEN_ROUND1_MANIFEST_BLOBS[path.name],
        )


if __name__ == "__main__":
    unittest.main()
