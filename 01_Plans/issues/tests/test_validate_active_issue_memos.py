from __future__ import annotations

import importlib.util
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "validate_active_issue_memos.py"
sys.path.insert(0, str(MODULE_PATH.parent))
SPEC = importlib.util.spec_from_file_location("validate_active_issue_memos", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)

extract_verification_level = MODULE.extract_verification_level
discover_active_rows = MODULE.discover_active_rows
parse_active_rows = MODULE.parse_active_rows
validate = MODULE.validate


class ValidateActiveIssueMemosTest(unittest.TestCase):
    def test_parse_active_rows_extracts_table_entries(self) -> None:
        readme = textwrap.dedent(
            """
            ## Active issue memos
            | Backlog ID | Memo | Status | Source Issue |
            |---|---|---|---|
            | FB-1 | `issue-fb-1.md` | Draft | TBD |
            | DOC-1 | `issue-doc-1.md` | Open | https://example.com/1 |

            ## Completed locally (Source Issue pending)
            | Backlog ID | Memo | Status | Source Issue | Notes |
            |---|---|---|---|---|
            | FB-2 | `issue-fb-2.md` | Done (Local) | TBD | note |
            """
        )
        rows = parse_active_rows(readme)
        self.assertEqual(2, len(rows))
        self.assertEqual("issue-fb-1.md", rows[0].memo)
        self.assertEqual("Open", rows[1].status)

    def test_parse_active_rows_ignores_non_active_sections(self) -> None:
        readme = textwrap.dedent(
            """
            ## Active issue memos
            | Backlog ID | Memo | Status | Source Issue |
            |---|---|---|---|
            | DOC-1 | `issue-doc-1.md` | Draft | TBD |

            ## Completed locally (Source Issue pending)
            | Backlog ID | Memo | Status | Source Issue | Notes |
            |---|---|---|---|---|
            | DOC-2 | `issue-doc-2.md` | Done (Local) | TBD | note |
            """
        )
        rows = parse_active_rows(readme)
        self.assertEqual(["issue-doc-1.md"], [row.memo for row in rows])

    def test_extract_verification_level(self) -> None:
        memo = "- Expected verification level: `integration`\n"
        self.assertEqual("integration", extract_verification_level(memo))

    def test_validate_detects_status_source_inconsistency(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text(
                textwrap.dedent(
                    """
                    ## Active issue memos
                    | Backlog ID | Memo | Status | Source Issue |
                    |---|---|---|---|
                    | DOC-REL-01 | `issue-doc.md` | In Progress | TBD |
                    """
                ),
                encoding="utf-8",
            )
            (root / "issue-doc.md").write_text(
                textwrap.dedent(
                    """
                    - Type: Process / Documentation quality
                    - Status: In Progress
                    - Source Issue: TBD
                    - Priority: P1
                    - Scope: `01_Plans/issues/`
                    - Related ADR/Spec: `ADR-0000`
                    - Expected verification level: `docs-check`
                    """
                ),
                encoding="utf-8",
            )
            errors = validate(root)
            self.assertTrue(any("Source Issue is TBD" in err for err in errors))

    def test_validate_detects_invalid_verification_level(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text(
                textwrap.dedent(
                    """
                    ## Active issue memos
                    | Backlog ID | Memo | Status | Source Issue |
                    |---|---|---|---|
                    | DOC-REL-01 | `issue-doc.md` | Draft | TBD |
                    """
                ),
                encoding="utf-8",
            )
            (root / "issue-doc.md").write_text(
                textwrap.dedent(
                    """
                    - Type: Process / Documentation quality
                    - Status: Draft
                    - Source Issue: TBD
                    - Priority: P1
                    - Scope: `01_Plans/issues/`
                    - Related ADR/Spec: `ADR-0000`
                    - Expected verification level: `smoke`
                    """
                ),
                encoding="utf-8",
            )
            errors = validate(root)
            self.assertTrue(any("invalid Expected verification level" in err for err in errors))

    def test_validate_uses_memo_status_instead_of_readme_status(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text(
                textwrap.dedent(
                    """
                    ## Active issue memos
                    | Backlog ID | Memo | Status | Source Issue |
                    |---|---|---|---|
                    | DOC-REL-01 | `issue-doc.md` | In Progress | https://example.com/1 |
                    """
                ),
                encoding="utf-8",
            )
            (root / "issue-doc.md").write_text(
                textwrap.dedent(
                    """
                    - Type: Process / Documentation quality
                    - Status: Open
                    - Source Issue: https://example.com/1
                    - Priority: P1
                    - Scope: `01_Plans/issues/`
                    - Related ADR/Spec: `ADR-0000`
                    - Expected verification level: `docs-check`
                    """
                ),
                encoding="utf-8",
            )
            errors = validate(root)
            self.assertEqual([], errors)

    def test_validate_uses_memo_source_instead_of_readme_source(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text(
                textwrap.dedent(
                    """
                    ## Active issue memos
                    | Backlog ID | Memo | Status | Source Issue |
                    |---|---|---|---|
                    | DOC-REL-01 | `issue-doc.md` | Open | https://example.com/1 |
                    """
                ),
                encoding="utf-8",
            )
            (root / "issue-doc.md").write_text(
                textwrap.dedent(
                    """
                    - Type: Process / Documentation quality
                    - Status: Open
                    - Source Issue: https://example.com/2
                    - Priority: P1
                    - Scope: `01_Plans/issues/`
                    - Related ADR/Spec: `ADR-0000`
                    - Expected verification level: `docs-check`
                    """
                ),
                encoding="utf-8",
            )
            errors = validate(root)
            self.assertEqual([], errors)

    def test_validate_allows_empty_active_table(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text(
                textwrap.dedent(
                    """
                    ## Active issue memos
                    | Backlog ID | Memo | Status | Source Issue |
                    |---|---|---|---|

                    ## Completed locally (Source Issue pending)
                    | Backlog ID | Memo | Status | Source Issue | Notes |
                    |---|---|---|---|---|
                    | DOC-REL-01 | `issue-doc.md` | Done (Local) | TBD | note |
                    """
                ),
                encoding="utf-8",
            )
            errors = validate(root)
            self.assertEqual([], errors)

    def test_validate_rejects_noncanonical_status_enum(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text(
                textwrap.dedent(
                    """
                    ## Active issue memos
                    | Backlog ID | Memo | Status | Source Issue |
                    |---|---|---|---|
                    | DOC-REL-01 | `issue-doc.md` | Active | https://example.com/1 |
                    """
                ),
                encoding="utf-8",
            )
            (root / "issue-doc.md").write_text(
                textwrap.dedent(
                    """
                    - Type: Process / Documentation quality
                    - Status: Active
                    - Source Issue: https://example.com/1
                    - Priority: P1
                    - Scope: `01_Plans/issues/`
                    - Related ADR/Spec: `ADR-0000`
                    - Expected verification level: `docs-check`
                    """
                ),
                encoding="utf-8",
            )
            errors = validate(root)
            self.assertTrue(any("invalid Status `Active`" in err for err in errors))

    def test_validate_rejects_decorated_status_instead_of_normalizing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "issue-doc.md").write_text(
                "- Status: Draft (waiting)\n- Source Issue: TBD\n",
                encoding="utf-8",
            )

            errors = validate(root)

        self.assertTrue(any("invalid Status `Draft (waiting)`" in err for err in errors))

    def test_validate_detects_duplicate_active_requirement_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            memo = textwrap.dedent(
                """\
                - Type: Process
                - Status: Draft
                - Source Issue: TBD
                - Priority: P1
                - Scope: `01_Plans/`
                - Related ADR/Spec: `ADR-0001`
                - Expected verification level: `docs-check`
                - RequirementID: DUPLICATE-01
                """
            )
            (root / "issue-first.md").write_text(memo, encoding="utf-8")
            (root / "issue-second.md").write_text(memo, encoding="utf-8")

            errors = validate(root)

        self.assertTrue(any("duplicate active RequirementID `DUPLICATE-01`" in err for err in errors))

    def test_validate_rejects_duplicate_memo_basename_across_active_and_done(self) -> None:
        """DOC-ISSUE-IDENTITY-01: a completed memo must not coexist with an
        old active copy of the same physical memo after it was moved."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "done").mkdir()
            (root / "issue-duplicate.md").write_text(
                textwrap.dedent(
                    """
                    - Type: Process
                    - Status: Draft
                    - Source Issue: TBD
                    - Priority: P1
                    - Scope: `01_Plans/`
                    - Related ADR/Spec: `ADR-0001`
                    - Expected verification level: `docs-check`
                    """
                ),
                encoding="utf-8",
            )
            (root / "done" / "issue-duplicate.md").write_text(
                "- Status: Done\n",
                encoding="utf-8",
            )

            errors = validate(root)

        self.assertTrue(
            any("duplicate issue memo basename `issue-duplicate.md`" in err for err in errors),
            errors,
        )

    def test_validate_allows_one_done_memo_in_done(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "done").mkdir()
            (root / "done" / "issue-complete.md").write_text(
                "- Status: Done\n",
                encoding="utf-8",
            )

            errors = validate(root)

        self.assertEqual([], errors)

    def test_discover_active_rows_does_not_require_readme(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "issue-doc.md").write_text(
                "- Status: Draft\n- Source Issue: N/A\n",
                encoding="utf-8",
            )
            rows = discover_active_rows(root)
            self.assertEqual(["issue-doc.md"], [row.memo for row in rows])

    def test_discover_active_rows_records_the_done_subdirectory(self) -> None:
        """DOC-NORM-03 reproduction: an active-status memo misplaced under
        done/ (as happened once with issue-DX-DESIGN-CHECK-02) must be
        discovered with a path validate_rows() can actually re-resolve,
        not just a bare filename that only resolves directly under root."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "done").mkdir()
            (root / "done" / "issue-misplaced.md").write_text(
                "- Status: Draft\n- Source Issue: TBD\n",
                encoding="utf-8",
            )
            rows = discover_active_rows(root)
            self.assertEqual(["done/issue-misplaced.md"], [row.memo for row in rows])

    def test_validate_finds_and_rejects_an_active_memo_left_in_done(self) -> None:
        """DOC-NORM-03 keeps the real discovered path; DOC-ISSUE-IDENTITY-01
        adds the useful placement error instead of accepting the contradiction."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "done").mkdir()
            (root / "done" / "issue-misplaced.md").write_text(
                textwrap.dedent(
                    """
                    - Type: Process
                    - Status: Draft
                    - Source Issue: TBD
                    - Priority: P1
                    - Scope: `01_Plans/`
                    - Related ADR/Spec: `ADR-0001`
                    - Expected verification level: `docs-check`
                    """
                ),
                encoding="utf-8",
            )
            errors = validate(root)

        self.assertFalse(
            any("missing memo file" in err for err in errors),
            f"a memo discovered in done/ was misreported as missing: {errors}",
        )
        self.assertTrue(
            any("active Status `Draft` is not allowed under done/" in err for err in errors),
            errors,
        )

    def test_validate_detects_missing_dependency_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text(
                textwrap.dedent(
                    """
                    ## Active issue memos
                    | Backlog ID | Memo | Status | Source Issue |
                    |---|---|---|---|
                    | DOC-REL-01 | `issue-doc.md` | Open | https://example.com/1 |
                    """
                ),
                encoding="utf-8",
            )
            (root / "issue-doc.md").write_text(
                textwrap.dedent(
                    """
                    - Type: Process / Documentation quality
                    - Status: Open
                    - Source Issue: https://example.com/1
                    - Priority: P1
                    - Scope: `01_Plans/issues/`
                    - Related ADR/Spec: `ADR-0000`
                    - Expected verification level: `docs-check`

                    ## Dependencies
                    - requires `issue-does-not-exist.md`
                    """
                ),
                encoding="utf-8",
            )
            errors = validate(root)
            self.assertTrue(any("dependency path not found" in err for err in errors))


if __name__ == "__main__":
    unittest.main()
