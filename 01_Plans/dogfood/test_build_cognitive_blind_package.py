#!/usr/bin/env python3
"""Contract tests for cognitive dogfood blind-package generation.

The fixtures are synthetic and contain no experiment result. They verify that
P2 packaging cannot bypass static intake and that method/test identities are
neutralized without dropping the preregistered result sections.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import build_cognitive_blind_package as blind
from test_validate_cognitive_run_records import build_case001_arm_c_record


class BlindPackageGateTests(unittest.TestCase):
    def record_path(self, directory: str, text: str) -> Path:
        path = Path(directory) / "cedar-17-record.md"
        path.write_text(text, encoding="utf-8")
        return path

    def test_valid_record_passes_intake_and_preserves_all_required_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = self.record_path(directory, build_case001_arm_c_record())
            self.assertEqual(blind.require_static_intake(path), [])

            package, warnings = blind.build_package(path.read_text(encoding="utf-8"))
            self.assertEqual(warnings, [])
            for number in range(1, 10):
                self.assertIn(f"### 6.{number} Required item {number}", package)

    def test_incomplete_record_cannot_enter_blind_packaging(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = self.record_path(
                directory,
                build_case001_arm_c_record(required_numbers=[1, 2, 3]),
            )
            with self.assertRaisesRegex(ValueError, "static intake failed"):
                blind.require_static_intake(path)

    def test_conflict_ids_are_neutralized_and_direct_method_markers_are_absent(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = self.record_path(directory, build_case001_arm_c_record())
            blind.require_static_intake(path)
            package, warnings = blind.build_package(path.read_text(encoding="utf-8"))

            self.assertIn("source-check-1 detected: yes", package)
            self.assertIn("source-check-2 detected: partial", package)
            self.assertIn("source-check-3 detected: no", package)
            self.assertNotIn("T1 detected", package)
            self.assertNotIn("T2 detected", package)
            self.assertNotIn("T3 detected", package)
            self.assertNotIn("Arm C", package)
            self.assertNotIn("cultural-substrate-weaving", package)
            self.assertNotIn("Activation verdict", package)
            self.assertEqual(warnings, [])


if __name__ == "__main__":
    unittest.main()
