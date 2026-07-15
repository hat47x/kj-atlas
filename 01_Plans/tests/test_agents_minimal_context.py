import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
AGENTS = ROOT / "AGENTS.md"


class AgentsMinimalContextTest(unittest.TestCase):
    def test_keeps_ai_entrypoint_small_and_task_routed(self):
        text = AGENTS.read_text(encoding="utf-8")

        self.assertLessEqual(len(text.splitlines()), 180)
        self.assertIn("タスクに必要な正本とコードだけ", text)
        self.assertIn("ADR-0058-document-contract-v1-rebaseline.md", text)

    def test_does_not_restore_global_read_order_or_file_inventory(self):
        text = AGENTS.read_text(encoding="utf-8")
        prohibited = (
            "作業開始時は必ず後述の `Read Order` を上から順に読む",
            "ADR-0002`〜`ADR-",
            "ここがAGENTS.mdの中核です",
            "新しい主要ドキュメントやディレクトリが増えたら **必ず Project Map を更新**",
        )

        for phrase in prohibited:
            with self.subTest(phrase=phrase):
                self.assertNotIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
