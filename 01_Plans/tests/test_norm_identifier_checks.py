"""Verify DC-NORM-001/002/003/004 actually detect what they claim to.

A rule that never fires is indistinguishable from no rule. Each check below is
run against a deliberately broken input and must produce a finding, then against
the real repository and must be clean.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from docs_contract_checks import (  # noqa: E402
    RETIRED_VOCAB_EXEMPT_CLOSE,
    RETIRED_VOCAB_EXEMPT_OPEN,
    check_norm_identifier_resolution,
    check_norm_identifier_uniqueness,
    check_norm_line_references,
    check_prompt_status_vocabulary,
    check_retired_vocabulary,
)

ROOT = Path(__file__).resolve().parents[2]
PROMPT = ROOT / "00_Prompt"


def _markdown_paths() -> list[Path]:
    return sorted(
        p.relative_to(ROOT)
        for p in ROOT.rglob("*.md")
        if not any(part in {".git", "node_modules", "build"} for part in p.parts)
    )


class NormIdentifierCheckTests(unittest.TestCase):
    """The baseline must be clean, and each mutation must be caught."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.md_paths = _markdown_paths()

    def _probe(self, path: Path, text: str):
        """Write a throwaway document and remove it however the test ends."""
        path.write_text(text, encoding="utf-8")
        self.addCleanup(lambda: path.unlink(missing_ok=True))
        return path

    # --- baseline ---------------------------------------------------------

    def test_baseline_uniqueness_is_clean(self) -> None:
        findings = check_norm_identifier_uniqueness(ROOT)
        self.assertEqual(findings, [], f"duplicate norm identifiers: {findings}")

    def test_baseline_resolution_is_clean(self) -> None:
        findings = check_norm_identifier_resolution(ROOT, self.md_paths)
        self.assertEqual(
            [f"{f.path}:{f.line} {f.target}" for f in findings],
            [],
        )

    def test_baseline_has_no_line_number_references(self) -> None:
        findings = check_norm_line_references(ROOT, self.md_paths)
        self.assertEqual(
            [f"{f.path}:{f.line} {f.target}" for f in findings],
            [],
        )

    def test_baseline_status_vocabulary_is_clean(self) -> None:
        findings = check_prompt_status_vocabulary(ROOT)
        self.assertEqual([f"{f.path} {f.target}" for f in findings], [])

    # --- mutations --------------------------------------------------------

    def test_unresolvable_reference_is_detected(self) -> None:
        probe = self._probe(
            ROOT / "01_Plans" / "_norm_probe.md",
            "参照テスト: DOM-CORE-99 は存在しない。\n",
        )
        findings = check_norm_identifier_resolution(
            ROOT, self.md_paths + [probe.relative_to(ROOT)]
        )
        self.assertIn("DOM-CORE-99", [f.target for f in findings])

    def test_line_number_citation_is_detected(self) -> None:
        probe = self._probe(
            ROOT / "01_Plans" / "_norm_probe.md",
            "行番号参照: `00_Prompt/domain.md:88` を見よ。\n",
        )
        findings = check_norm_line_references(
            ROOT, self.md_paths + [probe.relative_to(ROOT)]
        )
        self.assertIn("00_Prompt/domain.md:88", [f.target for f in findings])

    def test_duplicate_definition_is_detected(self) -> None:
        self._probe(PROMPT / "_dup_probe.md", "### DOM-CORE-01 重複定義\n")
        findings = check_norm_identifier_uniqueness(ROOT)
        self.assertIn("DOM-CORE-01", [f.target for f in findings])

    def test_uncontrolled_status_value_is_detected(self) -> None:
        self._probe(
            PROMPT / "_status_probe.md",
            "# probe\n\n- Status: Normative（追跡情報つき）\n",
        )
        findings = check_prompt_status_vocabulary(ROOT)
        self.assertTrue(any(f.path.endswith("_status_probe.md") for f in findings))

    def test_missing_status_is_detected(self) -> None:
        self._probe(PROMPT / "_status_probe.md", "# probe\n\n（Status なし）\n")
        findings = check_prompt_status_vocabulary(ROOT)
        self.assertTrue(any(f.path.endswith("_status_probe.md") for f in findings))

    def test_unknown_checklist_item_is_detected(self) -> None:
        probe = self._probe(
            ROOT / "01_Plans" / "_norm_probe.md",
            "存在する: CHK-X3 / 存在しない: CHK-X9\n",
        )
        findings = check_norm_identifier_resolution(
            ROOT, self.md_paths + [probe.relative_to(ROOT)]
        )
        flagged = [f.target for f in findings if f.path.endswith("_norm_probe.md")]
        self.assertIn("CHK-X9", flagged)
        self.assertNotIn("CHK-X3", flagged)

    # --- the rules must not fire on valid input ---------------------------

    def test_valid_reference_is_not_flagged(self) -> None:
        probe = self._probe(
            ROOT / "01_Plans" / "_norm_probe.md",
            "正当な参照: DOM-CORE-02 に従う。\n",
        )
        findings = check_norm_identifier_resolution(
            ROOT, self.md_paths + [probe.relative_to(ROOT)]
        )
        self.assertNotIn("DOM-CORE-02", [f.target for f in findings])


class RetiredVocabularyCheckTests(unittest.TestCase):
    """DC-VOCAB-001: `domain.md` retires a term; nothing used to verify that."""

    #: The probe lives in 02_Architecture because that is the checked scope.
    PROBE = ROOT / "02_Architecture" / "_retired_vocab_probe.md"

    def _probe(self, body: str) -> None:
        self.PROBE.write_text(body, encoding="utf-8")
        self.addCleanup(lambda: self.PROBE.unlink(missing_ok=True))

    def test_baseline_is_clean(self) -> None:
        findings = check_retired_vocabulary(ROOT)
        self.assertEqual(
            [f"{f.path}:{f.line} {f.target}" for f in findings],
            [],
            "02_Architecture still uses retired vocabulary as contract prose",
        )

    def test_retired_term_in_contract_prose_is_detected(self) -> None:
        self._probe("Core Graph direct write は禁止する。\n")
        findings = check_retired_vocabulary(ROOT)
        self.assertTrue(
            any(f.path.endswith("_retired_vocab_probe.md") for f in findings),
            "a retired term used as contract prose was not detected",
        )

    def test_explicitly_marked_history_is_allowed(self) -> None:
        self._probe(
            f"<!-- {RETIRED_VOCAB_EXEMPT_OPEN} -->\n"
            "改名の記録: Core Graph を Consensus Graph へ改めた。\n"
            f"<!-- {RETIRED_VOCAB_EXEMPT_CLOSE} -->\n"
        )
        findings = check_retired_vocabulary(ROOT)
        self.assertFalse(
            any(f.path.endswith("_retired_vocab_probe.md") for f in findings),
            "an explicitly marked historical block was flagged",
        )

    def test_marker_does_not_leak_past_its_close(self) -> None:
        """An exemption must not silently cover the rest of the file."""
        self._probe(
            f"<!-- {RETIRED_VOCAB_EXEMPT_OPEN} -->\n"
            "改名の記録: Core Graph -> Consensus Graph\n"
            f"<!-- {RETIRED_VOCAB_EXEMPT_CLOSE} -->\n"
            "Core Graph direct write は禁止する。\n"
        )
        findings = [
            f for f in check_retired_vocabulary(ROOT)
            if f.path.endswith("_retired_vocab_probe.md")
        ]
        self.assertEqual([f.line for f in findings], [4])

    def test_inline_naming_as_retired_is_allowed(self) -> None:
        self._probe("Consensus Graph（旧称: Core Graph）を正本とする。\n")
        findings = check_retired_vocabulary(ROOT)
        self.assertFalse(
            any(f.path.endswith("_retired_vocab_probe.md") for f in findings)
        )


if __name__ == "__main__":
    unittest.main()
