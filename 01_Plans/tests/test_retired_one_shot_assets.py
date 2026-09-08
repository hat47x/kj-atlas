from pathlib import Path
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]

# DX-CI-STALE-ONESHOT-ASSETS-01 and later dogfood findings retired these exact
# files after they had already served their one-shot purpose. Keep the guard
# path-specific: temporary validation assets remain allowed elsewhere, while
# stale branch re-merges or later lifecycle drift must not be able to restore
# these already-completed execution tools silently.
RETIRED_ONE_SHOT_PATHS = (
    ".github/workflows/apply-ai-merge-ir-once.yml",
    ".github/workflows/fix-docs-check-optional-workflows-once.yml",
    ".github/workflows/merge-apply-e2e-once.yml",
    ".github/workflows/reconcile-partial-with-r18-once.yml",
    ".github/workflows/verify-ai-merge-apply-lineage-docs-once.yml",
    ".github/workflows/verify-ai-merge-apply-lineage-once.yml",
    ".github/workflows/lane-c-sync-qa-e2e-saas-child-status-once.yml",
    ".github/scripts/apply_ai_merge_ir_once.py",
    ".github/scripts/apply_merge_method_traceability_final_once.py",
    ".github/scripts/fix_docs_check_optional_workflows_once.py",
    ".github/scripts/reconcile_partial_with_r18_once.py",
)


class RetiredOneShotAssetsTest(unittest.TestCase):
    def test_retired_one_shot_assets_do_not_reappear(self) -> None:
        restored = [
            path
            for path in RETIRED_ONE_SHOT_PATHS
            if (REPOSITORY_ROOT / path).exists()
        ]

        self.assertEqual(
            restored,
            [],
            "retired one-shot assets reappeared in the repository: "
            + ", ".join(restored),
        )


if __name__ == "__main__":
    unittest.main()
