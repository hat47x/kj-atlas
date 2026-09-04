from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "validate_active_issue_memos.py"
sys.path.insert(0, str(MODULE_PATH.parent))
SPEC = importlib.util.spec_from_file_location(
    "validate_active_issue_memos_required_values", MODULE_PATH
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)

extract_field_value = MODULE.extract_field_value
validate = MODULE.validate


class RequiredMetadataValuesTest(unittest.TestCase):
    REQUIRED_FIELDS = (
        "Type",
        "Status",
        "Source Issue",
        "Priority",
        "Scope",
        "Related ADR/Spec",
        "Expected verification level",
    )

    def memo(
        self,
        *,
        empty_field: str | None = None,
        verification: str = "`unit`",
    ) -> str:
        values = {
            "Type": "Process / Documentation quality",
            "Status": "Draft",
            "Source Issue": "N/A",
            "Priority": "P1",
            "Scope": "`01_Plans/issues/`",
            "Related ADR/Spec": "N/A",
            "Expected verification level": verification,
        }
        if empty_field is not None:
            values[empty_field] = ""
        return "\n".join(
            f"- {name}: {values[name]}" for name in self.REQUIRED_FIELDS
        ) + "\n"

    def test_extract_field_value_does_not_cross_metadata_line_boundary(self) -> None:
        text = "- Source Issue:\n- Priority: P1\n"
        self.assertIsNone(extract_field_value(text, "Source Issue"))
        self.assertEqual("P1", extract_field_value(text, "Priority"))

    def test_validate_rejects_empty_required_metadata_values(self) -> None:
        for field in self.REQUIRED_FIELDS:
            with self.subTest(field=field), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                (root / "issue-required-value.md").write_text(
                    self.memo(empty_field=field),
                    encoding="utf-8",
                )
                errors = validate(root)
                self.assertTrue(
                    errors,
                    f"empty {field} unexpectedly passed validation",
                )
                if field != "Status":
                    self.assertTrue(
                        any(
                            "missing or empty field" in error
                            and f"- {field}:" in error
                            for error in errors
                        ),
                        errors,
                    )

    def test_validate_rejects_invalid_unquoted_verification_level(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "issue-invalid-level.md").write_text(
                self.memo(verification="smoke"),
                encoding="utf-8",
            )
            errors = validate(root)
        self.assertTrue(
            any(
                "invalid Expected verification level `smoke`" in error
                for error in errors
            ),
            errors,
        )

    def test_validate_accepts_complete_required_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "issue-complete.md").write_text(
                self.memo(), encoding="utf-8"
            )
            errors = validate(root)
        self.assertEqual([], errors)


if __name__ == "__main__":
    unittest.main()
