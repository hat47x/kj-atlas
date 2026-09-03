from pathlib import Path

VALIDATOR = Path("01_Plans/issues/validate_active_issue_memos.py")
TEST = Path("01_Plans/issues/tests/test_issue_lifecycle_contract.py")

text = VALIDATOR.read_text(encoding="utf-8")
old = '''def validate(root: Path) -> list[str]:
    return (
        validate_status_contract(root)
        + validate_done_memo_location(root)
        + validate_rows(root, discover_active_rows(root))
    )
'''
new = '''def validate(
    root: Path,
    *,
    enforce_done_baseline: bool | None = None,
    legacy_done_baseline: int = LEGACY_DONE_AT_ROOT_BASELINE,
) -> list[str]:
    """Validate issue memos without leaking repo-local debt into test fixtures.

    The Done-at-root baseline is a checked-in debt value for this repository's
    real ``01_Plans/issues`` directory. Synthetic roots used by contract tests
    have no relationship to that historical count, so the unified validator
    only applies the ratchet automatically to the real issues root. Callers
    that intentionally exercise the lifecycle contract on another root can
    opt in explicitly and supply a fixture-sized baseline.
    """
    real_issues_root = Path(__file__).resolve().parent
    should_enforce_done_baseline = (
        root.resolve() == real_issues_root
        if enforce_done_baseline is None
        else enforce_done_baseline
    )

    errors = validate_status_contract(root)
    if should_enforce_done_baseline:
        errors += validate_done_memo_location(
            root,
            legacy_baseline=legacy_done_baseline,
        )
    errors += validate_rows(root, discover_active_rows(root))
    return errors
'''
if text.count(old) != 1:
    raise SystemExit(f"validator replacement count={text.count(old)}")
VALIDATOR.write_text(text.replace(old, new, 1), encoding="utf-8")

test = TEST.read_text(encoding="utf-8")
needle = '''    def test_done_directory_does_not_consume_root_legacy_baseline(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_issue(root / "issue-a.md", "Done")
            write_issue(root / "issue-b.md", "Done")
            write_issue(root / "done" / "issue-c.md", "Done")

            self.assertEqual(
                MODULE.validate_done_memo_location(root, legacy_baseline=2),
                [],
            )
'''
addition = needle + '''
    def test_unified_validate_does_not_apply_repo_baseline_to_synthetic_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            self.assertEqual(MODULE.validate(root), [])

    def test_unified_validate_can_explicitly_enforce_fixture_baseline(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_issue(root / "issue-a.md", "Done")
            write_issue(root / "issue-b.md", "Done")
            write_issue(root / "issue-c.md", "Done")

            errors = MODULE.validate(
                root,
                enforce_done_baseline=True,
                legacy_done_baseline=2,
            )

            self.assertEqual(len(errors), 1)
            self.assertIn("3 > 2", errors[0])
'''
if test.count(needle) != 1:
    raise SystemExit(f"test insertion count={test.count(needle)}")
TEST.write_text(test.replace(needle, addition, 1), encoding="utf-8")

print("issue lifecycle fixture-scope patch applied")
