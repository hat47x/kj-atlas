from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

import validate_cognitive_arm_packages as validator


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def git_blob_sha_bytes(value: bytes) -> str:
    header = f"blob {len(value)}\0".encode("ascii")
    return hashlib.sha1(header + value, usedforsecurity=False).hexdigest()


class CognitiveArmPackageValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        self.control = self.root / "control"
        self.control.mkdir()
        self.original_dogfood_dir = validator.DOGFOOD_DIR
        validator.DOGFOOD_DIR = self.control

        self.product_payload = b"frozen product evidence\n"
        self.skill_payload = b"canonical skill source\n"
        self.product_commit = "a" * 40
        self.skill_commit = "b" * 40
        self.product_repository = "hat47x/kj-atlas"
        self.skill_repository = "hat47x/cultural-substrate-weaving"
        self.write_operator_controls()

    def tearDown(self) -> None:
        validator.DOGFOOD_DIR = self.original_dogfood_dir
        self.tempdir.cleanup()

    def write_operator_controls(self) -> None:
        product_manifest = {
            "schemaVersion": 1,
            "manifestId": f"case-001-r1-product@{self.product_commit}",
            "caseId": "case-001",
            "round": 1,
            "productRepository": self.product_repository,
            "productCommit": self.product_commit,
            "commonSources": [
                {
                    "path": "README.md",
                    "blobSha": git_blob_sha_bytes(self.product_payload),
                }
            ],
        }
        (self.control / "cognitive-dogfood-case-001-round1-source-manifest.json").write_text(
            json.dumps(product_manifest, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        skill_manifest = {
            "schemaVersion": 1,
            "manifestId": f"case-001-skill-ja@{self.skill_commit}",
            "caseId": "case-001",
            "skillRepository": self.skill_repository,
            "skillCommit": self.skill_commit,
            "locale": "ja-JP",
            "canonicalRoot": "src/ja-JP",
            "canonicalSources": [
                {
                    "path": "src/ja-JP/ROUTER.md",
                    "blobSha": git_blob_sha_bytes(self.skill_payload),
                }
            ],
        }
        (self.control / "cognitive-dogfood-case-001-skill-manifest.json").write_text(
            json.dumps(skill_manifest, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        for mode in validator.ARM_LAUNCH_MODE.values():
            (self.control / f"cognitive-dogfood-case-001-launch-{mode}.md").write_text(
                f"# frozen launch {mode}\n",
                encoding="utf-8",
            )

    def package(self, arm: str) -> Path:
        return self.root / "cognitive-dogfood-case-001-arms" / arm

    def write_product(self, package: Path) -> None:
        product = package / "product"
        experiment = product / "_experiment"
        experiment.mkdir(parents=True)
        source = product / "README.md"
        source.write_bytes(self.product_payload)
        manifest = {
            "schemaVersion": 1,
            "bundleId": f"case-001-r1-product@{self.product_commit}",
            "caseId": "case-001",
            "round": 1,
            "productRepository": self.product_repository,
            "productCommit": self.product_commit,
            "sourceCount": 1,
            "operatorOnlyMetadataCopied": False,
            "sources": [
                {
                    "path": "README.md",
                    "gitBlobSha": git_blob_sha_bytes(self.product_payload),
                    "sha256": sha256_bytes(self.product_payload),
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
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_bytes(self.skill_payload)
        experiment = skill / "_experiment"
        experiment.mkdir(parents=True, exist_ok=True)
        manifest = {
            "schemaVersion": 1,
            "manifestId": f"cognitive-dogfood-skill-ja@{self.skill_commit}",
            "skillRepository": self.skill_repository,
            "skillCommit": self.skill_commit,
            "sourceCount": 1,
            "canonicalRoot": "src/ja-JP",
            "locale": "ja-JP",
            "caseScopedMetadataIncluded": False,
            "evaluationArtifactsCopied": False,
            "operatorManifestCopied": operator_manifest_copied,
            "repositoryDocsCopied": False,
            "sources": [
                {
                    "path": "src/ja-JP/ROUTER.md",
                    "gitBlobSha": git_blob_sha_bytes(self.skill_payload),
                    "sha256": sha256_bytes(self.skill_payload),
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
        mode = validator.ARM_LAUNCH_MODE[arm]
        frozen_launch = self.control / f"cognitive-dogfood-case-001-launch-{mode}.md"
        (package / "launch.md").write_bytes(frozen_launch.read_bytes())
        self.write_product(package)
        if arm in {"B", "D"}:
            self.write_skill(package)
        if arm in {"C", "D"}:
            self.write_starter(package)
        return package

    def test_valid_a_package_passes(self) -> None:
        self.prepare("A")
        self.assertEqual(validator.validate_package(self.root, "001", "A"), [])

    def test_wrong_frozen_launch_packet_is_rejected(self) -> None:
        package = self.prepare("A")
        wrong_launch = self.control / "cognitive-dogfood-case-001-launch-skill.md"
        (package / "launch.md").write_bytes(wrong_launch.read_bytes())
        issues = validator.validate_package(self.root, "001", "A")
        self.assertTrue(any("launch.md differs from frozen" in issue for issue in issues), issues)

    def test_product_commit_drift_is_rejected(self) -> None:
        package = self.prepare("A")
        manifest_path = package / "product" / "_experiment" / "bundle-manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["productCommit"] = "c" * 40
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        issues = validator.validate_package(self.root, "001", "A")
        self.assertTrue(
            any("product bundle productCommit differs from preregistration" in issue for issue in issues),
            issues,
        )

    def test_content_rewrite_with_matching_sha256_but_stale_git_blob_is_rejected(self) -> None:
        package = self.prepare("A")
        source = package / "product" / "README.md"
        changed = b"rewritten product evidence\n"
        source.write_bytes(changed)
        manifest_path = package / "product" / "_experiment" / "bundle-manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["sources"][0]["sha256"] = sha256_bytes(changed)
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        issues = validator.validate_package(self.root, "001", "A")
        self.assertTrue(any("git blob SHA mismatch" in issue for issue in issues), issues)

    def test_skill_commit_drift_is_rejected(self) -> None:
        package = self.prepare("B")
        manifest_path = package / "skill" / "_experiment" / "skill-bundle-manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["skillCommit"] = "d" * 40
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        issues = validator.validate_package(self.root, "001", "B")
        self.assertTrue(
            any("skill bundle skillCommit differs from preregistration" in issue for issue in issues),
            issues,
        )

    def test_unexpected_product_file_is_rejected(self) -> None:
        package = self.prepare("A")
        (package / "product" / "operator-notes.md").write_text(
            "must not leak\n", encoding="utf-8"
        )
        issues = validator.validate_package(self.root, "001", "A")
        self.assertTrue(
            any("unexpected bundle files leaked" in issue for issue in issues), issues
        )

    def test_skill_directory_in_arm_a_is_rejected(self) -> None:
        package = self.prepare("A")
        self.write_skill(package)
        issues = validator.validate_package(self.root, "001", "A")
        self.assertTrue(any("top-level boundary mismatch" in issue for issue in issues), issues)

    def test_operator_skill_metadata_is_rejected(self) -> None:
        package = self.prepare("B")
        self.write_skill(package, operator_manifest_copied=True)
        issues = validator.validate_package(self.root, "001", "B")
        self.assertTrue(
            any("operatorManifestCopied must be false" in issue for issue in issues), issues
        )

    def test_nonempty_starter_is_rejected(self) -> None:
        package = self.prepare("C")
        self.write_starter(package, cards=[{"id": "contaminated"}])
        issues = validator.validate_package(self.root, "001", "C")
        self.assertTrue(any("starter cards must remain empty" in issue for issue in issues), issues)


if __name__ == "__main__":
    unittest.main()
