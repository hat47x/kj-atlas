from pathlib import Path


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{path}: expected exactly one match, found {count}: {old[:80]!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


api = Path("02_Architecture/api.md")
replace_once(
    api,
    "- AI入力は `DocumentV1` を直接文字列化するだけでなく、LLM投入IRを経由する。対象島の全直接メンバーと、それらに接続するcard relation / evidenceの両端をroute固有の必須カードとして保護する。",
    "- AI入力は `DocumentV1` をそのまま広げず、対象島の全直接メンバーと、それらへ直接つながるcard relation / evidenceの両端だけへsourceを縮約してからLLM投入IRを構築する。無関係な文書カードはIRにも追加prompt文脈にも送らない。",
)
replace_once(
    api,
    "- 親島、表札カード、review state、card relation、`contradictionState` はIR由来の構造としてAIへ渡す。`critiqueTags` / `critiqueText` と明示的なisland-to-island edgeはtask-local入力として従来の経路を維持する。",
    "- 親島、表札カード、review state、card relation、`contradictionState` はIR由来の構造としてAIへ渡す。親島は親子関係を保持する構造だけを残し、親島のカード集合まで入力へ広げない。`critiqueTags` / `critiqueText` と明示的なisland-to-island edgeはtask-local入力として従来の経路を維持する。",
)
replace_once(
    api,
    "- 対象島の仕事に必要なrelation / evidenceがIR上限で欠落する場合は、providerへ不完全な表札生成を依頼せず422でfail-closedにする。主なIRエラーコードは `required_card_budget_exceeded` / `required_relation_missing` / `required_evidence_missing`。request / responseの形は変更しない。",
    "- 対象島の仕事に必要な意味をIRで完全に保持できない場合は、providerへ不完全な表札生成を依頼せず422でfail-closedにする。主なIRエラーコードは、必須カード集合が上限を超える `required_card_budget_exceeded`、必須カード本文が文字数上限で短縮される `required_text_truncated`、投影後の必須カード集合が一致しない `required_card_context_mismatch`、必要なrelation / evidenceが欠ける `required_relation_missing` / `required_evidence_missing`。request / responseの形は変更しない。",
)

issue = Path("01_Plans/issues/issue-AI-IR-STAGE5-SCOPE-01-classify-remaining-ai-input-paths.md")
replace_once(
    issue,
    "1. `suggest-island-summary` — 2026-09-03に配線済み。対象島の必要意味をroute固有投影で保護し、grounding境界を維持した。実行回帰の確認を別ゲートとして残す。",
    "1. `suggest-island-summary` — 2026-09-03に配線済み。対象島の必要意味をroute固有投影で保護し、grounding境界を維持した。後続のmerge後監査で、mainでも再現する既知4件以外に新しいbackend回帰が無いことを確認した。",
)
replace_once(
    issue,
    "1. **`suggest-island-summary` の必要意味をintegration regressionでコードへ固定し、IRへ配線した。** 実行回帰の確認を残す。",
    "1. **完了: `suggest-island-summary` の必要意味をintegration regressionでコードへ固定し、IRへ配線した。** merge後監査で専用回帰と関連回帰を実行し、二層SafeModeを含めて確認した。backend全体ではmainでも同じ4件が失敗することを別環境で再現し、その4件を除く全テストが成功することを確認した。",
)
replace_once(
    issue,
    "- [ ] `suggest-island-summary` の追加・既存回帰を実行し、結果を確認する。",
    "- [x] `suggest-island-summary` の追加・既存回帰を実行し、結果を確認する。— 専用IR、既存prompt、経路被覆、関連SafeModeを実行して成功を確認した。backend全体はmainでも再現する既知4件を基準差分として切り分け、その4件を除く全回帰に新規失敗が無いことを確認した。",
)

# Final assertions: keep these intentionally literal so drift fails closed.
api_text = api.read_text(encoding="utf-8")
for needle in (
    "無関係な文書カードはIRにも追加prompt文脈にも送らない",
    "required_text_truncated",
    "required_card_context_mismatch",
):
    if needle not in api_text:
        raise SystemExit(f"api.md synchronization failed: {needle}")

issue_text = issue.read_text(encoding="utf-8")
if "backend全体はmainでも再現する既知4件を基準差分として切り分け" not in issue_text:
    raise SystemExit("Stage 5 issue synchronization failed")

print("PR #2839 documentation synchronized after baseline-aware regression.")
