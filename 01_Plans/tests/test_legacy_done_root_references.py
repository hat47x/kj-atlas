from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
ISSUES_ROOT = REPO_ROOT / "01_Plans" / "issues"
DONE_ROOT = ISSUES_ROOT / "done"
MANIFEST = ISSUES_ROOT / "legacy_done_at_root_r18.json"

# These references are frozen or dated provenance. Rewriting them to the memo's
# later done/ location would make historical evidence claim a path that was not
# used when the evidence was recorded. Keep the allow-list explicit so any new
# external retired-root reference still requires review.
EXTERNAL_HISTORICAL_EXCEPTIONS = {
    (
        "01_Plans/dogfood/doc_kj_atlas_dogfood_r15.json",
        "issue-AI-IR-PROMPT-EVIDENCE-01-render-ir-evidence-in-provider-prompts.md",
    ),
    (
        "01_Plans/dogfood/doc_kj_atlas_dogfood_r18.json",
        "issue-DOC-ISSUE-LIFECYCLE-01-done-memos-remain-at-active-root.md",
    ),
    (
        "01_Plans/dogfood/doc_kj_atlas_dogfood_r2.json",
        "issue-DX-CI-MCP-01-mcp-tests-not-run-in-ci.md",
    ),
    (
        "01_Plans/research/phase-exit-evaluation-ENV-ARCH-01-2026-03-11.md",
        "issue-ENV-ARCH-01-global-env-prefix-migration.md",
    ),
    (
        "01_Plans/research/core-value-realization-priorities-2026-07-18.md",
        "issue-MVP-EXIT-01-productization-readiness.md",
    ),
    (
        "01_Plans/research/mvp-exit-01-human-acceptance-handoff.md",
        "issue-MVP-EXIT-01-productization-readiness.md",
    ),
    (
        "01_Plans/dogfood/cognitive-dogfood-case-003-round1-source-manifest.json",
        "issue-OPS-SAAS-SCALE-01-in-process-state-blocks-horizontal-scaling.md",
    ),
}


class LegacyDoneRootReferenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        raw = json.loads(MANIFEST.read_text(encoding="utf-8"))
        cls.legacy_names = tuple(raw["paths"])
        cls.manifest_count = raw["count"]

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
        for name in self.legacy_names:
            stale.extend(self._grep_retired_root_path(name))

        self.assertEqual(
            stale,
            [],
            "retired legacy Done root paths are still referenced:\n" + "\n".join(stale),
        )

    def test_no_unreviewed_external_file_references_any_done_memo_at_retired_root(self) -> None:
        unexpected: list[str] = []
        observed_exceptions: set[tuple[str, str]] = set()
        done_names = sorted(path.name for path in DONE_ROOT.glob("issue-*.md"))

        for name in done_names:
            for line in self._grep_retired_root_path(name):
                source_path, _line_number, _body = line.split(":", 2)
                if source_path.startswith("01_Plans/issues/done/"):
                    # Done memos retain dated commands/scope guards as historical evidence.
                    continue
                key = (source_path, name)
                if key in EXTERNAL_HISTORICAL_EXCEPTIONS:
                    observed_exceptions.add(key)
                    continue
                unexpected.append(line)

        self.assertEqual(
            unexpected,
            [],
            "unreviewed external files reference canonical Done memos at retired active-root paths:\n"
            + "\n".join(unexpected),
        )
        self.assertEqual(
            observed_exceptions,
            EXTERNAL_HISTORICAL_EXCEPTIONS,
            "historical exception set changed; remove stale exceptions or review new provenance explicitly",
        )


if __name__ == "__main__":
    unittest.main()
