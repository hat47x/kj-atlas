from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from validate_cognitive_arm_packages import validate_package


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


class CognitiveArmPackageValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def package(self, arm: str) -> Path:
        return self.root / "cognitive-dogfood-case-001-arms" / arm

    def write_product(self, package: Path) -> None:
        product = package / "product"
        experiment = product / "_experiment"
        experiment.mkdir(parents=True)
        source = product / "README.md"
        payload = b"frozen product evidence\n"
        source.write_bytes(payload)
        manifest = {
            "schemaVersion": 1,
            "caseId": "case-001",
            "round": 1,
            "operatorOnlyMetadataCopied": False,
            "sources": [
                {
                    "path": "README.md",
                    "sha256": sha256_bytes(payload),
                }
            ],
        }
        (experiment / "bundle-manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def write_skill(self, package: Path, *, operator_manifest_copied: bool = False) -> None:
        skill = package / "skill"
        source = skill / "src" / "ja-JP" / "ROUTER.md"
        source.parent.mkdir(parents=True)
        payload = b"canonical skill source\n"
        source.write_bytes(payload)
        experiment = skill / "_experiment"
        experiment.mkdir(parents=True)
        manifest = {
            "schemaVersion": 1,
            "canonicalRoot": "src/ja-JP",
            "locale": "ja-JP",
            "caseScopedMetadataIncluded": False,
            "evaluationArtifactsCopied": False,
            "operatorManifestCopied": operator_manifest_copied,
            "repositoryDocsCopied": False,
            "sources": [
                {
                    "path": "src/ja-JP/ROUTER.md",
                    "sha256": sha256_bytes(payload),
                }
            ],
        }
        (experiment / "skill-bundle-manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def write_starter(self, package: Path, *, cards: list[dict] | None = None) -> None:
        starter = {
            "version": 1,
            "id": "doc_cognitive_case_001_starter",
            "cards": [] if cards is None else cards,
            "islands": [],
            "evidenceLinks": [],
            "readingOrder": [],
            "narratives": [],
            "transform": {"panX": 0, "panY": 0, "zoom": 1},
        }
        (package / "starter.json").write_text(
            json.dumps(starter, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def prepare(self, arm: str) -> Path:
        package = self.package(arm)
        package.mkdir(parents=True)
        (package / "launch.md").write_text("# frozen launch\n", encoding="utf-8")
        self.write_product(package)
        if arm in {"B", "D"}:
            self.write_skill(package)
        if arm in {"C", "D"}:
            self.write_starter(package)
        return package

    def test_valid_a_package_passes(self) -> None:
        self.prepare("A")
        self.assertEqual(validate_package(self.root, "001", "A"), [])

    def test_unexpected_product_file_is_rejected(self) -> None:
        package = self.prepare("A")
        (package / "product" / "operator-notes.md").write_text(
            "must not leak\n", encoding="utf-8"
        )
        issues = validate_package(self.root, "001", "A")
        self.assertTrue(
            any("unexpected bundle files leaked" in issue for issue in issues), issues
        )

    def test_skill_directory_in_arm_a_is_rejected(self) -> None:
        package = self.prepare("A")
        self.write_skill(package)
        issues = validate_package(self.root, "001", "A")
        self.assertTrue(any("top-level boundary mismatch" in issue for issue in issues), issues)

    def test_operator_skill_metadata_is_rejected(self) -> None:
        package = self.prepare("B")
        self.write_skill(package, operator_manifest_copied=True)
        issues = validate_package(self.root, "001", "B")
        self.assertTrue(
            any("operatorManifestCopied must be false" in issue for issue in issues), issues
        )

    def test_nonempty_starter_is_rejected(self) -> None:
        package = self.prepare("C")
        self.write_starter(package, cards=[{"id": "contaminated"}])
        issues = validate_package(self.root, "001", "C")
        self.assertTrue(any("starter cards must remain empty" in issue for issue in issues), issues)


if __name__ == "__main__":
    unittest.main()
