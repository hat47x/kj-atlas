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
    "| `propose-opposing-viewpoint` | `DocumentV1`、対象カード | 対象カード、根拠・矛盾、人間が既に判断した矛盾状態、関連する反対所見 | **IR移行済み（2026-09-03）**。対象カードと直接接続するrelation/evidenceを必須意味として保護し、人間の `contradictionState` を新規AI発見と区別する |",
)
replace_once(
    stage5,
    "対象カードを `required_card_ids` で保護することは妥当だが、反対所見候補として全300カードを同じ優先度で保持するかは別問題である。対象カードに接続するevidence/relationと、文書全体からの反対候補探索を分けて設計する。",
    "対象カードを `required_card_ids` で保護することは妥当だが、反対所見候補として全300カードを同じ優先度で保持するかは別問題である。対象カードに接続するevidence/relationと、文書全体からの反対候補探索を分けて設計する。\n\n#### 実装結果（2026-09-03）\n\nStage 5の第2経路として `propose-opposing-viewpoint` をIRへ移行した。proposal-onlyの応答契約、UI側の人間判断、`Target card:` の既存mock/E2E接地形式は変更していない。\n\n- 対象カードを必須カードとして保護する。\n- 対象カードへ直接接続するcard relation / evidenceの両端も、反対視点を理解するための必須文脈として保護する。\n- `confirmed` / `held` を含む `contradictionState` は、人間が既に行った判断としてprovider手前へ渡し、新しいAI発見として言い直さないようprompt上でも区別する。\n- 直接接続していないカードは、IRに残った範囲だけを探索用の補助文脈として渡す。対象周辺の必須意味と、文書全体から反例を探す補助探索を同じ重要度として扱わない。\n- 必須relationが `MAX_RELATIONS` で欠ける場合は `required_relation_missing`、必要カード集合が `MAX_CARDS` を超える場合は `required_card_budget_exceeded` でprovider呼出前にfail-closedにする。evidenceの欠落も `required_evidence_missing` として扱う。\n- SafeModeはroute側の一次検査とIR側の二次検査をともに維持する。座標は要求しない。\n\n専用IR回帰、既存 `test_ai_oppose.py`、AI経路被覆テストを同時に実行し、production routeがpromptと `LLMRequest.inputs` の双方へ同じIRを渡すことまで固定した。",
)
replace_once(
    stage5,
    "### IR移行済み\n\n1. `suggest-island-summary` — 2026-09-03に移行。対象島の必要意味をroute固有投影で保護し、grounding境界を維持した。\n\n### 次にIR移行を具体化してよい\n\n2. `propose-opposing-viewpoint`\n3. `check-narrative` — ただしscale方式決定後\n\n`propose-opposing-viewpoint` は対象カードという自然なfocusを持ち、`required_card_ids` とroute固有投影を利用しやすい。`check-narrative` は文書全体を扱うため、`AI-IR-SCALE-01` の結果を待つ。",
    "### IR移行済み\n\n1. `suggest-island-summary` — 2026-09-03に移行。対象島の必要意味をroute固有投影で保護し、grounding境界を維持した。\n2. `propose-opposing-viewpoint` — 2026-09-03に移行。対象カードと直接接続するrelation/evidenceを必須意味として保護し、人間の既決 `contradictionState` を状態付きで保持した。\n\n### IR移行候補だがscale方式決定を待つ\n\n3. `check-narrative`\n\n`check-narrative` は文書全体を扱うため、`AI-IR-SCALE-01` の結果を待つ。",
)
replace_once(
    stage5,
    "2. **次: `propose-opposing-viewpoint` を状態付きevidenceへ移す。** 対象カードを保護し、`contradictionState` を新規発見と既決判断の区別に使う。\n3. `summarize-island-relation` / no-doc 2経路について、ADR-0069の適用範囲を短い追補で明確にする。",
    "2. **完了: `propose-opposing-viewpoint` を状態付きevidenceへ移した。** 対象カードと直接接続する意味を保護し、`contradictionState` を新規発見と既決判断の区別に使う。\n3. **次: `summarize-island-relation` / no-doc 2経路について、ADR-0069の適用範囲を短い追補で明確にする。**",
)
replace_once(
    stage5,
    "- [ ] `propose-opposing-viewpoint` のroute-required meaningをintegration regressionとして固定する。",
    "- [x] `propose-opposing-viewpoint` のroute-required meaningをintegration regressionとして固定し、IRへ配線する。— 対象カードと直接接続するrelation/evidenceを保護し、人間の `contradictionState` を状態付きで保持した。",
)

replace_once(
    projection,
    "`suggest-island-summary` をStage 5の第1経路として移行し、現在は11件のLLMRequestのうち5経路がIR経由、残り6経路である。Stage 5では件数を機械的に減らさず、`AI-IR-STAGE5-SCOPE-01` で経路ごとの仕事と入力契約を確認してから移行する。次の実装対象は `propose-opposing-viewpoint`。",
    "`suggest-island-summary` をStage 5の第1経路、`propose-opposing-viewpoint` を第2経路として移行し、現在は11件のLLMRequestのうち6経路がIR経由、残り5経路である。Stage 5では件数を機械的に減らさず、`AI-IR-STAGE5-SCOPE-01` で経路ごとの仕事と入力契約を確認してから移行する。次は、限定grounding経路とno-doc経路についてADR-0069の適用範囲を明確にする。",
)
replace_once(
    projection,
    "**2026-09-03更新**: `suggest-island-summary` をStage 5の第1経路としてIRへ移行し、IR経由は5件、未移行は6件になった。未移行経路の分類と次の順序は `AI-IR-STAGE5-SCOPE-01` を正本とする。",
    "**2026-09-03更新**: `suggest-island-summary` と `propose-opposing-viewpoint` をStage 5の第1・第2経路としてIRへ移行し、IR経由は6件、未移行は5件になった。未移行経路の分類と次の順序は `AI-IR-STAGE5-SCOPE-01` を正本とする。",
)
replace_once(
    projection,
    "- [x] AC-4（detect-contradiction / suggest-card-groups / generate-narrative / suggest-layout / suggest-island-summary）:",
    "- [x] AC-4（detect-contradiction / suggest-card-groups / generate-narrative / suggest-layout / suggest-island-summary / propose-opposing-viewpoint）:",
)
replace_once(
    projection,
    "- [x] AC-9（detect-contradiction / suggest-card-groups / generate-narrative / suggest-layout / suggest-island-summary）:",
    "- [x] AC-9（detect-contradiction / suggest-card-groups / generate-narrative / suggest-layout / suggest-island-summary / propose-opposing-viewpoint）:",
)
marker = "## 受入条件\n"
text = projection.read_text(encoding="utf-8")
if text.count(marker) != 1:
    raise SystemExit("AI-IR-PROJECTION-01の受入条件見出しを一意に特定できませんでした")
stage5_result = """## 結果（Stage 5 第2経路: `propose-opposing-viewpoint`、2026-09-03）

対象カードを中心とした反対視点・根拠不足の提案を、文書全体の無差別なカード列挙からroute固有IRへ移した。

- 対象カードと、そこへ直接接続するrelation / evidenceの両端を `required_card_ids` で保護する。
- 必須relation / evidenceが共有IRの上限処理で欠けた場合はprovider呼出前にfail-closedにする。
- `confirmed` / `held` を含む `contradictionState` を、人間の既決判断としてpromptへ明示する。既決矛盾は反対視点の文脈として使えるが、新しいAI発見として再提示しない。
- 直接接続していないカードはIRに残った範囲だけを補助探索へ使う。対象周辺の必須意味は、より広い反例探索より先に保護する。
- DOGFOOD-17で固定した `Target card: {id,text}` の行形式を維持し、既存mock/E2Eが対象主張そのものへ接地する契約を壊さない。
- proposal-only、`status=proposed`、`reviewState=unreviewed`、SafeMode二層、人間の最終判断権は変更していない。

この変更でIR経由は6/11経路となった。残る5経路のうち `check-narrative` はscale方式決定待ち、`suggest-merges` は意味論の受入条件待ち、`summarize-island-relation` とno-doc 2経路はADR-0069の適用範囲確認を先に行う。

"""
projection.write_text(text.replace(marker, stage5_result + marker, 1), encoding="utf-8")

api_text = api.read_text(encoding="utf-8")
api_before = """- contradiction / evidence 構造をもとに、対象カードの**反対視点・根拠不足**を提案する（value_traceability V1/V3）。**proposal-only（自動適用なし・人間の判断を先取りしない）**。対象カードが存在しない場合は 422、対象Documentが永続化されていない場合は 404。判定（Adopt/Reject/Hold）は `/ai/proposals/audit` と同経路。
"""
api_after = """- contradiction / evidence 構造をもとに、対象カードの**反対視点・根拠不足**を提案する（value_traceability V1/V3）。**proposal-only（自動適用なし・人間の判断を先取りしない）**。対象カードが存在しない場合は 422、対象Documentが永続化されていない場合は 404。判定（Adopt/Reject/Hold）は `/ai/proposals/audit` と同経路。
- AI入力はLLM投入IRを経由する。`targetCardId` と、対象カードへ直接接続するcard relation / evidenceの両端をroute固有の必須カードとして保護する。座標は要求しない。
- `confirmed` / `held` を含む `contradictionState` は**人間が既に行った判断**としてAIへ渡し、新しいAI発見と区別する。既決矛盾を文脈として参照することはできるが、その存在だけで対象カードの真偽を決定しない。
- 直接接続していないカードは、IRに残った範囲で反例探索の補助文脈として利用できる。対象カードと直接関係する必須意味を、文書全体の探索候補より先に保持する。
- task-requiredなrelation / evidenceがIR上限で欠落する場合は不完全な入力でproviderを呼ばず422でfail-closedにする。主なIRエラーコードは `required_card_budget_exceeded` / `required_relation_missing` / `required_evidence_missing`。request / responseの形とproposal-only契約は変更しない。
"""
if api_text.count(api_before) != 1:
    raise SystemExit("api.mdのopposing-viewpoint契約を一意に特定できませんでした")
api.write_text(api_text.replace(api_before, api_after, 1), encoding="utf-8")
