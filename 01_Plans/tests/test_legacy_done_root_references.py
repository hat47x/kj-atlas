from __future__ import annotations

import json
import re
import subprocess
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
ISSUES_ROOT = REPO_ROOT / "01_Plans" / "issues"
DONE_ROOT = ISSUES_ROOT / "done"
MANIFEST = ISSUES_ROOT / "legacy_done_at_root_r18.json"
FROZEN_PRODUCT_REPOSITORY = "hat47x/kj-atlas"
FROZEN_PRODUCT_COMMIT = "2232b3bb26647e5c4a083f55bdbf83c161698649"
FROZEN_SOURCE_MANIFESTS = {
    "01_Plans/dogfood/cognitive-dogfood-case-001-round1-source-manifest.json": (
        "case-001",
        f"case-001-r1-product@{FROZEN_PRODUCT_COMMIT}",
    ),
    "01_Plans/dogfood/cognitive-dogfood-case-002-round1-source-manifest.json": (
        "case-002",
        f"case-002-r1-product@{FROZEN_PRODUCT_COMMIT}",
    ),
    "01_Plans/dogfood/cognitive-dogfood-case-003-round1-source-manifest.json": (
        "case-003",
        f"case-003-r1-product@{FROZEN_PRODUCT_COMMIT}",
    ),
}

# These references are frozen or dated provenance outside the structured cognitive
# source manifests. Rewriting them to the memo's later done/ location would make
# historical evidence claim a path that was not used when the evidence was
# recorded. Keep this allow-list explicit so any new unstructured exception still
# requires review.
EXTERNAL_HISTORICAL_EXCEPTIONS = {
    (
        "01_Plans/research/phase-exit-evaluation-ENV-ARCH-01-2026-03-11.md",
        "issue-ENV-ARCH-01-global-env-prefix-migration.md",
    ),
}


def _load_frozen_source_coordinate_exceptions() -> set[tuple[str, str]]:
    """Return retired-root paths that are coordinates inside the frozen product snapshot.

    A source-manifest path is not a live link into the current repository. It is
    interpreted together with productCommit/blobSha, so rewriting it after the
    memo moves to done/ would corrupt the frozen snapshot. Keep this exception
    structural and narrow: only the three preregistered Round 1 manifests at the
    exact frozen product identity can create it, and only when the current
    canonical memo is under done/ while the old active-root file is absent.

    The dogfood validator separately verifies each path/blob against the frozen
    Git commit. This guard deliberately does not duplicate that full-history
    dependency; it only recognizes the already-frozen coordinate shape.
    """

    exceptions: set[tuple[str, str]] = set()
    for relative_path, (expected_case_id, expected_manifest_id) in FROZEN_SOURCE_MANIFESTS.items():
        manifest_path = REPO_ROOT / relative_path
        raw = json.loads(manifest_path.read_text(encoding="utf-8"))
        if raw.get("schemaVersion") != 1:
            raise AssertionError(f"unexpected frozen manifest schema: {relative_path}")
        if raw.get("caseId") != expected_case_id:
            raise AssertionError(f"unexpected frozen manifest caseId: {relative_path}")
        if raw.get("manifestId") != expected_manifest_id:
            raise AssertionError(f"unexpected frozen manifest identity: {relative_path}")
        if raw.get("round") != 1:
            raise AssertionError(f"unexpected frozen manifest round: {relative_path}")
        if raw.get("productRepository") != FROZEN_PRODUCT_REPOSITORY:
            raise AssertionError(f"unexpected frozen product repository: {relative_path}")
        if raw.get("productCommit") != FROZEN_PRODUCT_COMMIT:
            raise AssertionError(f"unexpected frozen product commit: {relative_path}")

        common_sources = raw.get("commonSources")
        if not isinstance(common_sources, list):
            raise AssertionError(f"missing commonSources: {relative_path}")

        for source in common_sources:
            if not isinstance(source, dict):
                raise AssertionError(f"invalid commonSources entry: {relative_path}")
            source_path = source.get("path")
            blob_sha = source.get("blobSha")
            if not isinstance(source_path, str) or not isinstance(blob_sha, str):
                raise AssertionError(f"invalid frozen source identity: {relative_path}")
            if re.fullmatch(r"[0-9a-f]{40}", blob_sha) is None:
                raise AssertionError(f"invalid frozen source blob SHA: {relative_path}:{source_path}")

            prefix = "01_Plans/issues/"
            if not source_path.startswith(prefix) or source_path.startswith(
                "01_Plans/issues/done/"
            ):
                continue

            name = source_path.removeprefix(prefix)
            if "/" in name:
                continue
            if (DONE_ROOT / name).is_file() and not (ISSUES_ROOT / name).exists():
                exceptions.add((relative_path, name))

    return exceptions


class LegacyDoneRootReferenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        raw = json.loads(MANIFEST.read_text(encoding="utf-8"))
        cls.legacy_names = tuple(raw["paths"])
        cls.manifest_count = raw["count"]
        cls.frozen_source_coordinate_exceptions = _load_frozen_source_coordinate_exceptions()

    def _grep_retired_root_path(self, name: str) -> list[str]:
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
        if completed.returncode == 1:
            return []
        return completed.stdout.splitlines()

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
        observed_frozen_coordinates: set[tuple[str, str]] = set()
        for name in self.legacy_names:
            for line in self._grep_retired_root_path(name):
                source_path, _line_number, _body = line.split(":", 2)
                key = (source_path, name)
                if key in self.frozen_source_coordinate_exceptions:
                    observed_frozen_coordinates.add(key)
                    continue
                stale.append(line)

        expected_frozen_coordinates = {
            key
            for key in self.frozen_source_coordinate_exceptions
            if key[1] in self.legacy_names
        }
        self.assertEqual(
            observed_frozen_coordinates,
            expected_frozen_coordinates,
            "frozen R18 coordinate exceptions changed; verify the frozen manifests explicitly",
        )
        self.assertEqual(
            stale,
            [],
            "retired legacy Done root paths are still referenced:\n" + "\n".join(stale),
        )

    def test_no_unreviewed_external_file_references_any_done_memo_at_retired_root(self) -> None:
        unexpected: list[str] = []
        observed_exceptions: set[tuple[str, str]] = set()
        observed_frozen_coordinates: set[tuple[str, str]] = set()
        done_names = sorted(path.name for path in DONE_ROOT.glob("issue-*.md"))

        for name in done_names:
            for line in self._grep_retired_root_path(name):
                source_path, _line_number, _body = line.split(":", 2)
                if source_path.startswith("01_Plans/issues/done/"):
                    # Done memos retain dated commands/scope guards as historical evidence.
                    continue
                key = (source_path, name)
                if key in self.frozen_source_coordinate_exceptions:
                    observed_frozen_coordinates.add(key)
                    continue
                if key in EXTERNAL_HISTORICAL_EXCEPTIONS:
                    observed_exceptions.add(key)
                    continue
                unexpected.append(line)

        expected_frozen_coordinates = {
            key
            for key in self.frozen_source_coordinate_exceptions
            if key[1] in done_names
        }
        self.assertEqual(
            unexpected,
            [],
            "unreviewed external files reference canonical Done memos at retired active-root paths:\n"
            + "\n".join(unexpected),
        )
        self.assertEqual(
            observed_frozen_coordinates,
            expected_frozen_coordinates,
            "frozen source-coordinate exception set changed; review the snapshot identity explicitly",
        )
        self.assertEqual(
            observed_exceptions,
            EXTERNAL_HISTORICAL_EXCEPTIONS,
            "historical exception set changed; remove stale exceptions or review new provenance explicitly",
        )


if __name__ == "__main__":
    unittest.main()
