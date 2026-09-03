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
    "2026-09-03に `suggest-island-summary` をStage 5の第1経路として移行し、現在は**5経路がIR経由、未移行は6経路**である。",
    "2026-09-03に `suggest-island-summary` をStage 5の第1経路、`propose-opposing-viewpoint` を第2経路として移行し、現在は**6経路がIR経由、未移行は5経路**である。",
)
replace_once(
    stage5,
    "| `propose-opposing-viewpoint` | `DocumentV1`、対象カード | 対象カード、根拠・矛盾、人間が既に判断した矛盾状態、関連する反対所見 | **IR移行候補。優先度高**。現行promptはevidence linkの種別だけを渡し、`contradictionState` を渡していない |",
    "| `propose-opposing-viewpoint` | `DocumentV1`、対象カード | 対象カード、根拠・矛盾、人間が既に判断した矛盾状態、関連する反対所見 | **IR移行済み（2026-09-03）**。対象カードと直接接続するrelation/evidenceを必須意味として保護し、人間の `contradictionState` を新規AI発見と区別する。対象カード本文もIRから最終promptへ描画する |",
)
replace_once(
    stage5,
    "対象カードを `required_card_ids` で保護することは妥当だが、反対所見候補として全300カードを同じ優先度で保持するかは別問題である。対象カードに接続するevidence/relationと、文書全体からの反対候補探索を分けて設計する。",
    "対象カードを `required_card_ids` で保護することは妥当だが、反対所見候補として全300カードを同じ優先度で保持するかは別問題である。対象カードに接続するevidence/relationと、文書全体からの反対候補探索を分けて設計する。\n\n#### 実装結果（2026-09-03）\n\nStage 5の第2経路として `propose-opposing-viewpoint` をIRへ移行した。proposal-onlyの応答契約、UI側の人間判断、`Target card:` の行形式は変更していない。\n\n- 対象カードを必須カードとして保護し、対象カードへ直接接続するcard relation / evidenceの両端も必須文脈として保護する。\n- `confirmed` / `held` を含む `contradictionState` は、人間が既に行った判断としてprovider手前へ渡し、新しいAI発見として言い直さないようprompt上でも区別する。\n- 直接接続していないカードは、IRに残った範囲だけを反例探索の補助文脈として扱う。対象周辺の必須意味と文書全体からの探索を同じ重要度にしない。\n- providerへ送る `Target card:` の本文もIR正規化後の対象カード本文から描画し、Document側の生本文を中心入力へ迂回させない。merge前監査で同型の迂回を検出し、integration regressionを追加して解消した。\n- 必須relation / evidenceが共有IRの上限処理で欠けた場合は `required_relation_missing` / `required_evidence_missing`、必須カード集合が上限を超える場合は `required_card_budget_exceeded` でprovider呼出前にfail-closedにする。\n- SafeModeはroute側の一次検査とIR側の二次検査をともに維持し、座標は要求しない。\n\n専用IR回帰、既存 `test_ai_oppose.py`、AI経路被覆テストで、production routeがpromptと `LLMRequest.inputs` の双方へ同じIR本文・構造を渡すことまで固定した。",
)
replace_once(
    stage5,
    "### 次にIR移行を具体化してよい\n\n2. `propose-opposing-viewpoint`\n3. `check-narrative` — ただしscale方式決定後\n\n`propose-opposing-viewpoint` は対象カードという自然なfocusを持ち、`required_card_ids` とroute固有投影を利用しやすい。`check-narrative` は文書全体を扱うため、`AI-IR-SCALE-01` の結果を待つ。",
    "2. `propose-opposing-viewpoint` — 2026-09-03にIR移行を完了。対象カードと直接接続するrelation/evidenceを必須意味として保護し、既決 `contradictionState` と対象カード本文をIR実入力として保持した。\n\n### IR移行候補だがscale方式決定を待つ\n\n3. `check-narrative`\n\n`check-narrative` は文書全体を扱うため、`AI-IR-SCALE-01` の結果を待つ。",
)
replace_once(
    stage5,
    "2. **次: `propose-opposing-viewpoint` を状態付きevidenceへ移す。** 対象カードを保護し、`contradictionState` を新規発見と既決判断の区別に使う。\n3. `summarize-island-relation` / no-doc 2経路について、ADR-0069の適用範囲を短い追補で明確にする。",
    "2. **完了: `propose-opposing-viewpoint` を状態付きevidenceへ移した。** 対象カードと直接接続する意味を保護し、`contradictionState` を新規発見と既決判断の区別に使う。対象カード本文もIRからprovider promptへ描画する。\n3. **次: `summarize-island-relation` / no-doc 2経路について、ADR-0069の適用範囲を短い追補で明確にする。**",
)
replace_once(
    stage5,
    "- [ ] `propose-opposing-viewpoint` のroute-required meaningをintegration regressionとして固定する。",
    "- [x] `propose-opposing-viewpoint` のroute-required meaningをintegration regressionとして固定し、IRへ配線する。— 対象カードと直接接続するrelation/evidenceを保護し、人間の `contradictionState` を状態付きで保持した。対象カード本文もIRから最終promptへ描画し、生本文の迂回を回帰で禁止した。",
)

replace_once(
    projection,
    "`suggest-island-summary` をStage 5の第1経路として移行し、現在は11件のLLMRequestのうち5経路がIR経由、残り6経路である。Stage 5では件数を機械的に減らさず、`AI-IR-STAGE5-SCOPE-01` で経路ごとの仕事と入力契約を確認してから移行する。次の実装対象は `propose-opposing-viewpoint`。",
    "`suggest-island-summary` をStage 5の第1経路、`propose-opposing-viewpoint` を第2経路として移行し、現在は11件のLLMRequestのうち6経路がIR経由、残り5経路である。Stage 5では件数を機械的に減らさず、`AI-IR-STAGE5-SCOPE-01` で経路ごとの仕事と入力契約を確認してから移行する。次は限定grounding経路とno-doc経路についてADR-0069の適用範囲を明確にする。",
)
replace_once(
    projection,
    "**2026-09-03更新**: `suggest-island-summary` をStage 5の第1経路としてIRへ移行し、IR経由は5件、未移行は6件になった。未移行経路の分類と次の順序は `AI-IR-STAGE5-SCOPE-01` を正本とする。",
    "**2026-09-03更新**: `suggest-island-summary` と `propose-opposing-viewpoint` をStage 5の第1・第2経路としてIRへ移行し、IR経由は6件、未移行は5件になった。未移行経路の分類と次の順序は `AI-IR-STAGE5-SCOPE-01` を正本とする。",
)
for ac in ("AC-4", "AC-9"):
    replace_once(
        projection,
        f"- [x] {ac}（detect-contradiction / suggest-card-groups / generate-narrative / suggest-layout / suggest-island-summary）:",
        f"- [x] {ac}（detect-contradiction / suggest-card-groups / generate-narrative / suggest-layout / suggest-island-summary / propose-opposing-viewpoint）:",
    )
marker = "## 受入条件\n"
text = projection.read_text(encoding="utf-8")
if text.count(marker) != 1:
    raise SystemExit("AI-IR-PROJECTION-01の受入条件見出しを一意に特定できませんでした")
stage5_result = """## 結果（Stage 5 第2経路: `propose-opposing-viewpoint`、2026-09-03）

対象カードを中心とした反対視点・根拠不足の提案を、文書全体の無差別なカード列挙からroute固有IRへ移した。

- 対象カードと、そこへ直接接続するrelation / evidenceの両端を必須カード集合として保護する。
- 必須relation / evidenceが共有IRの上限処理で欠けた場合はprovider呼出前にfail-closedにする。
- `confirmed` / `held` を含む `contradictionState` を人間の既決判断としてpromptへ明示し、新しいAI発見と区別する。
- 直接接続していないカードはIRに残った範囲だけを補助探索へ使い、対象周辺の必須意味を先に保護する。
- `Target card: {id,text}` の行形式は維持しつつ、本文はDocument生値ではなくIR正規化後本文から描画する。promptと `LLMRequest.inputs` の本文一致をintegration regressionで固定した。
- proposal-only、`status=proposed`、`reviewState=unreviewed`、SafeMode二層、人間の最終判断権は変更していない。

この変更でIR経由は6/11経路となった。残る5経路のうち `check-narrative` はscale方式決定待ち、`suggest-merges` は意味論の受入条件待ち、`summarize-island-relation` とno-doc 2経路はADR-0069の適用範囲確認を先に行う。

"""
projection.write_text(text.replace(marker, stage5_result + marker, 1), encoding="utf-8")

api_before = "- contradiction / evidence 構造をもとに、対象カードの**反対視点・根拠不足**を提案する（value_traceability V1/V3）。**proposal-only（自動適用なし・人間の判断を先取りしない）**。対象カードが存在しない場合は 422、対象Documentが永続化されていない場合は 404。判定（Adopt/Reject/Hold）は `/ai/proposals/audit` と同経路。\n"
api_after = api_before + (
    "- AI入力はLLM投入IRを経由する。対象カードと、そこへ直接接続するcard relation / evidenceの両端を必須文脈として保護し、`confirmed` / `held` を含む `contradictionState` を人間の既決判断としてprovider手前へ渡す。直接接続していないカードはIRに残った範囲だけを補助探索へ用いる。\n"
    "- `Target card:` の本文もIR正規化後の対象カード本文から描画し、Document側の生本文を中心入力へ迂回させない。promptと `LLMRequest.inputs` の対象本文は同じIR値を使う。\n"
    "- 必須意味が共有IRの上限で欠ける場合は422でfail-closedにする。主なコードは `required_card_budget_exceeded` / `required_card_context_mismatch` / `required_relation_missing` / `required_evidence_missing`。SafeModeはroute側とIR側の二層を維持し、座標は送らない。\n"
)
replace_once(api, api_before, api_after)

# 最低限の同期確認。自然な日本語の文脈を壊す機械的な全面書換えは行わない。
for path, needles in {
    stage5: ["6経路がIR経由、未移行は5経路", "対象カード本文もIRからprovider promptへ描画", "propose-opposing-viewpoint` のroute-required meaning"],
    projection: ["IR経由は6件、未移行は5件", "Stage 5 第2経路", "Target card: {id,text}"],
    api: ["Target card:` の本文もIR正規化後", "required_relation_missing", "contradictionState"],
}.items():
    body = path.read_text(encoding="utf-8")
    for needle in needles:
        if needle not in body:
            raise SystemExit(f"文書同期後の確認に失敗しました: {path}: {needle}")

print("opposing-viewpoint IR documentation synchronized")
