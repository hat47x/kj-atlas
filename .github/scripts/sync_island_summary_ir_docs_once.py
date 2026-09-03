from pathlib import Path


def replace_once(path: Path, before: str, after: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(before)
    if count != 1:
        raise SystemExit(
            f"安全のため文書更新を中止しました: {path} 想定一致数=1、実際={count}: {before[:120]!r}"
        )
    path.write_text(text.replace(before, after, 1), encoding="utf-8")


stage5 = Path("01_Plans/issues/issue-AI-IR-STAGE5-SCOPE-01-classify-remaining-ai-input-paths.md")
projection = Path("01_Plans/issues/issue-AI-IR-PROJECTION-01-llm-input-ir-as-ai-input-path.md")
api = Path("02_Architecture/api.md")

replace_once(
    stage5,
    "`AI-IR-PROJECTION-01` は、`detect-contradiction`、`suggest-card-groups`、`generate-narrative`、`suggest-layout` の4経路をLLM投入IRへ移行した後、Stage 5として「残りのエンドポイント」を残している。2026-08-31時点の棚卸しでは、prompt構築関数は11件、そのうちIR経由は4件、未移行は7件と整理されている。",
    "`AI-IR-PROJECTION-01` は、`detect-contradiction`、`suggest-card-groups`、`generate-narrative`、`suggest-layout` の4経路をLLM投入IRへ移行した後、Stage 5として「残りのエンドポイント」を残した。2026-08-31時点の棚卸しでは、prompt構築関数は11件、そのうちIR経由は4件、未移行は7件だった。2026-09-03に `suggest-island-summary` をStage 5の第1経路として移行し、現在は**5経路がIR経由、未移行は6経路**である。",
)
replace_once(stage5, "## 現在の7経路", "## Stage 5で棚卸しした7経路")
replace_once(
    stage5,
    "| `suggest-island-summary` | `DocumentV1`、対象島、利用者の違和感 | 対象島の全直接メンバー、表札への異議、島の論理的位置、矛盾・根拠の有無 | **IR移行候補。優先度高**。対象島に絞れるためroute固有投影と相性がよい |",
    "| `suggest-island-summary` | `DocumentV1`、対象島、利用者の違和感 | 対象島の全直接メンバー、表札への異議、島の論理的位置、矛盾・根拠の有無 | **IR移行済み（2026-09-03）**。対象島に必要な意味をroute固有投影で保護し、欠落時はfail-closedにした |",
)
replace_once(
    stage5,
    "対象島のメンバーはroute固有の必須集合として扱える可能性が高い。ただし1島だけで `MAX_CARDS` を超える場合に黙って一部を落とすことは表札の戻し検査と両立しない。必要ならfail-closedまたは島内分割を別途検討する。",
    "対象島のメンバーはroute固有の必須集合として扱える可能性が高い。ただし1島だけで `MAX_CARDS` を超える場合に黙って一部を落とすことは表札の戻し検査と両立しない。必要ならfail-closedまたは島内分割を別途検討する。\n\n#### 実装結果（2026-09-03）\n\nStage 5の第1経路として `suggest-island-summary` をIRへ移行した。request / response、既存の表札検査、`critiqueTags` / `critiqueText`、明示的なisland-to-island edge、proposal-only wrapperは変更していない。追加したのは、AIへ渡す意味の保全層である。\n\n- 対象島の全直接メンバーを必須カードとして保護する。\n- 直接メンバーに接続するカード間relationとevidenceの両端も文脈用カードとして保護する。\n- 外部の隣接カードは関係・根拠を理解するための文脈に限定し、`groundingIds` の許可範囲は対象島の直接メンバーから広げない。\n- 親島、表札カード、review state、card relation、`contradictionState` をIR由来の構造としてpromptへ渡す。\n- 必要なrelation / evidenceが共有IRの上限処理で欠けた場合は、存在しないものとして扱わず `required_relation_missing` / `required_evidence_missing` でfail-closedにする。必要カード集合そのものが上限を超える場合も、共有IRの `required_card_budget_exceeded` をそのまま利用する。\n- SafeModeは従来のroute側検査を一次防御として残し、IR側検査を第二層として維持する。\n\n専用回帰に加え、既存の表札prompt回帰とAI経路被覆テストを同時に実行し、`suggest_island_summary` をIR移行済みタスクへ移した状態で成功した。",
)
replace_once(
    stage5,
    "### IR移行を具体化してよい\n\n1. `suggest-island-summary`\n2. `propose-opposing-viewpoint`\n3. `check-narrative` — ただしscale方式決定後\n\n最初の2件は対象島・対象カードという自然なfocusを持ち、`required_card_ids` とroute固有投影を利用しやすい。`check-narrative` は文書全体を扱うため、`AI-IR-SCALE-01` の結果を待つ。",
    "### IR移行済み\n\n1. `suggest-island-summary` — 2026-09-03に移行。対象島の必要意味をroute固有投影で保護し、grounding境界を維持した。\n\n### 次にIR移行を具体化してよい\n\n2. `propose-opposing-viewpoint`\n3. `check-narrative` — ただしscale方式決定後\n\n`propose-opposing-viewpoint` は対象カードという自然なfocusを持ち、`required_card_ids` とroute固有投影を利用しやすい。`check-narrative` は文書全体を扱うため、`AI-IR-SCALE-01` の結果を待つ。",
)
replace_once(
    stage5,
    "1. **`suggest-island-summary` の必要意味をintegration testで先に固定する。** 対象島の全直接メンバー、島構造、関連するrelation/evidence、既存の戻し検査を同時に保持する。\n2. **`propose-opposing-viewpoint` を状態付きevidenceへ移す。** 対象カードを保護し、`contradictionState` を新規発見と既決判断の区別に使う。",
    "1. **完了: `suggest-island-summary` の必要意味をintegration regressionで固定し、同じ変更でIRへ配線した。** 対象島の全直接メンバー、島構造、関連するrelation/evidence、既存の戻し検査を同時に保持している。\n2. **次: `propose-opposing-viewpoint` を状態付きevidenceへ移す。** 対象カードを保護し、`contradictionState` を新規発見と既決判断の区別に使う。",
)
replace_once(
    stage5,
    "- [ ] `suggest-island-summary` のroute-required meaningをintegration regressionとして固定する。",
    "- [x] `suggest-island-summary` のroute-required meaningをintegration regressionとして固定し、IRへ配線する。— 対象島の直接メンバーと隣接するrelation/evidenceの意味を保護し、必要意味が投影上限で欠ける場合はfail-closedにした。",
)

replace_once(
    projection,
    "> **進捗（2026-08-31）: 段階適用の Stage 1〜4 / 5 完了（`detect-contradiction`・`suggest-card-groups`・`generate-narrative`・`suggest-layout`）。** 残り1段階（`ADR-0069` 実装順序5「残りのエンドポイント」）は未着手。AC-7 は Stage 4 で**着手・完了**（`getDerivedIslandEdges()` ↔ `derived_island_relations()` の1対に限定したスポットチェック）。AC-10 は依然未着手。詳細は末尾の「結果（Stage 1〜4）」各節を参照。`Status` メタデータの語彙は `Draft` / `Open` / `In Progress` / `Done` に固定されている（`01_Plans/issues/issue_memo_status.py`）ため、段階情報はここに書く。",
    "> **進捗（2026-09-03）: Stage 1〜4は完了し、Stage 5へ着手済み。** `suggest-island-summary` をStage 5の第1経路として移行し、現在は11件のLLMRequestのうち5経路がIR経由、残り6経路である。Stage 5では件数を機械的に減らさず、`AI-IR-STAGE5-SCOPE-01` で経路ごとの仕事と入力契約を確認してから移行する。次の実装対象は `propose-opposing-viewpoint`。AC-7 は Stage 4 で完了し、AC-10は `AI-IR-SCALE-01` へ切り出して継続している。詳細は末尾の各Stage結果を参照。`Status` メタデータの語彙は `Draft` / `Open` / `In Progress` / `Done` に固定されている（`01_Plans/issues/issue_memo_status.py`）ため、段階情報はここに書く。",
)
replace_once(
    projection,
    "**2026-08-31 の再実測**: プロンプト構築関数は `routes/ai.py` に10件・`routes/ai_relations.py` に1件の**計11件**（起票時の「9件」は 2026-08-09 時点の `routes/ai.py` のみの数であり、その後の増加分を含まない）。うち IR を受け取るのは4件（`_build_prompt` / `_build_generate_narrative_prompt` / `_build_suggest_card_groups_prompt` / `_build_detect_contradiction_prompt`、いずれも `ir` 引数を持つ）で、**残り7件については下記の記述が現在も有効である**。",
    "**2026-08-31 の再実測**: プロンプト構築関数は `routes/ai.py` に10件・`routes/ai_relations.py` に1件の**計11件**（起票時の「9件」は 2026-08-09 時点の `routes/ai.py` のみの数であり、その後の増加分を含まない）。この時点ではIRを受け取るのは4件だった。**2026-09-03更新**: `suggest-island-summary` をStage 5の第1経路としてIRへ移行し、IR経由は5件、未移行は6件になった。未移行経路の分類と次の順序は `AI-IR-STAGE5-SCOPE-01` を正本とする。",
)
replace_once(
    projection,
    "- [x] AC-4（detect-contradiction / suggest-card-groups / generate-narrative / suggest-layout）:",
    "- [x] AC-4（detect-contradiction / suggest-card-groups / generate-narrative / suggest-layout / suggest-island-summary）:",
)
replace_once(
    projection,
    "Stage 5 の対象エンドポイントでは未実施。",
    "Stage 5では `suggest-island-summary` に同じ二層SafeModeを適用済み。残るStage 5経路では、実際にIRへ移行する経路ごとに同じ境界を確認する。",
)
replace_once(
    projection,
    "- [x] AC-9（detect-contradiction / suggest-card-groups / generate-narrative / suggest-layout）:",
    "- [x] AC-9（detect-contradiction / suggest-card-groups / generate-narrative / suggest-layout / suggest-island-summary）:",
)
replace_once(
    projection,
    "他エンドポイントは未変更（未変更であることが正しい）。",
    "Stage 5第1経路として `/ai/suggest-island-summary` も同期した。request / responseの形は変えず、IR経由化、二層SafeMode、対象島の必要意味、文脈専用カードと `groundingIds` の境界、IR上限で必要relation/evidenceを保持できない場合の422を追記した。残る未移行6経路は、入力契約を確認するまで変更しない。",
)
marker = "## 受入条件\n"
text = projection.read_text(encoding="utf-8")
if text.count(marker) != 1:
    raise SystemExit("AI-IR-PROJECTION-01の受入条件見出しを一意に特定できませんでした")
stage5_result = """## 結果（Stage 5 第1経路: `suggest-island-summary`、2026-09-03）

Stage 5では、残る経路を一括してIR化せず、`AI-IR-STAGE5-SCOPE-01` で仕事上必要な意味を先に分類した。その第1経路として `suggest-island-summary` を移行した。

- 対象島の直接メンバーを必須カードとして保護する。
- 直接メンバーに接続するrelation / evidenceの両端も文脈用カードとして保護する。
- 外部の隣接カードは文脈専用とし、応答の `groundingIds` は従来どおり対象島メンバーだけに限定する。
- 親島、表札カード、review state、relation、`contradictionState` をIR由来の構造としてprovider手前まで渡す。
- task-requiredなrelation / evidenceが共有IRの上限で欠ける場合は、欠落を「関係なし」と誤認せずprovider呼出前にfail-closedにする。
- 既存promptの表札検査、戻し検査、`critiqueTags` / `critiqueText`、明示的なisland-to-island edge、proposal-only wrapperは変更していない。
- SafeModeはroute側の一次検査とIR側の二次検査をともに維持する。

この変更でIR経由は5/11経路となった。次は `propose-opposing-viewpoint` を対象カード中心の状態付きevidenceへ移す。`check-narrative` は文書全体を扱うため、`AI-IR-SCALE-01` の方式判断より先に移行しない。

"""
projection.write_text(text.replace(marker, stage5_result + marker, 1), encoding="utf-8")

replace_once(
    api,
    "- 島の表札（ラベル）を提案する。表札は分類名ではなく、カード群の訴えを代弁する文でなければならない（kj_technique.md §3 表札検査）。",
    "- 島の表札（ラベル）を提案する。表札は分類名ではなく、カード群の訴えを代弁する文でなければならない（kj_technique.md §3 表札検査）。\n- AI入力は `DocumentV1` を直接文字列化するだけでなく、LLM投入IRを経由する。対象島の全直接メンバーと、それらに接続するcard relation / evidenceの両端をroute固有の必須カードとして保護する。\n- 対象島の外側にある隣接カードは、relation / evidenceを理解するための**文脈専用**である。応答の `groundingIds` は従来どおり対象島の直接メンバーだけを許可し、外部カードへ広げない。\n- 親島、表札カード、review state、card relation、`contradictionState` はIR由来の構造としてAIへ渡す。`critiqueTags` / `critiqueText` と明示的なisland-to-island edgeはtask-local入力として従来の経路を維持する。\n- 対象島の仕事に必要なrelation / evidenceがIR上限で欠落する場合は、providerへ不完全な表札生成を依頼せず422でfail-closedにする。主なIRエラーコードは `required_card_budget_exceeded` / `required_relation_missing` / `required_evidence_missing`。request / responseの形は変更しない。",
)
