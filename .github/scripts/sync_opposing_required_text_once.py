from pathlib import Path


def replace_once(path: Path, before: str, after: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(before)
    if count != 1:
        raise SystemExit(
            f"安全のため文書更新を中止しました: {path} 想定一致数=1、実際={count}: {before[:140]!r}"
        )
    path.write_text(text.replace(before, after, 1), encoding="utf-8")


stage5 = Path("01_Plans/issues/issue-AI-IR-STAGE5-SCOPE-01-classify-remaining-ai-input-paths.md")
projection = Path("01_Plans/issues/issue-AI-IR-PROJECTION-01-llm-input-ir-as-ai-input-path.md")
api = Path("02_Architecture/api.md")

replace_once(
    stage5,
    "- 必須relation / evidenceが共有IRの上限処理で欠けた場合は `required_relation_missing` / `required_evidence_missing`、必須カード集合が上限を超える場合は `required_card_budget_exceeded` でprovider呼出前にfail-closedにする。",
    "- 必須relation / evidenceが共有IRの上限処理で欠けた場合は `required_relation_missing` / `required_evidence_missing`、必須カード集合が上限を超える場合は `required_card_budget_exceeded`、対象カードまたは直接文脈の本文が `MAX_TEXT_CHARS` により短縮される場合は `required_text_truncated`、必須カード集合が投影結果と一致しない場合は `required_card_context_mismatch` としてprovider呼出前にfail-closedにする。",
)
replace_once(
    stage5,
    "専用IR回帰、既存 `test_ai_oppose.py`、AI経路被覆テストで、production routeがpromptと `LLMRequest.inputs` の双方へ同じIR本文・構造を渡すことまで固定した。",
    "専用IR回帰、既存 `test_ai_oppose.py`、AI経路被覆テストで、production routeがpromptと `LLMRequest.inputs` の双方へ同じIR本文・構造を渡すことまで固定した。一回限り検証では専用IR 6件、route 5件、経路被覆3件、関連回帰73件が成功し、mainでも再現する既知4件を除くbackend全体も1470 passed / 39 skipped / 12 deselectedで新規失敗がないことを確認した。",
)
replace_once(
    projection,
    "- 必須relation / evidenceが共有IRの上限処理で欠けた場合はprovider呼出前にfail-closedにする。",
    "- 必須relation / evidenceが共有IRの上限処理で欠けた場合に加え、対象カードまたは直接文脈の本文が `MAX_TEXT_CHARS` により短縮される場合も `required_text_truncated` としてprovider呼出前にfail-closedにする。",
)
replace_once(
    api,
    "- 必須意味が共有IRの上限で欠ける場合は422でfail-closedにする。主なコードは `required_card_budget_exceeded` / `required_card_context_mismatch` / `required_relation_missing` / `required_evidence_missing`。SafeModeはroute側とIR側の二層を維持し、座標は送らない。",
    "- 必須意味が共有IRの上限で欠ける場合は422でfail-closedにする。主なコードは `required_card_budget_exceeded` / `required_text_truncated` / `required_card_context_mismatch` / `required_relation_missing` / `required_evidence_missing`。SafeModeはroute側とIR側の二層を維持し、座標は送らない。",
)

for path, needles in {
    stage5: ["required_text_truncated", "1470 passed / 39 skipped / 12 deselected"],
    projection: ["required_text_truncated", "Stage 5 第2経路"],
    api: ["required_text_truncated", "required_card_context_mismatch"],
}.items():
    body = path.read_text(encoding="utf-8")
    for needle in needles:
        if needle not in body:
            raise SystemExit(f"追加同期後の確認に失敗しました: {path}: {needle}")

print("opposing-viewpoint required-text boundary documentation synchronized")
