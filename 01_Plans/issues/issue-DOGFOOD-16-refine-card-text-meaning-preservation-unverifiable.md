# Issue: DOGFOOD-16 文面整え（refine-card-text）の「元の意味を保持」をE2Eで検証できない

- Type: Process / Verification gap（ドッグフーディング観察）
- Status: Done
- Source Issue: ドッグフーディング iteration 181（シナリオ111・半導体製造 実装時の実走行観察）。rawな現場報告（「歩留まりが下がってロット廃棄が増えた」）を refine-card-text へ送っても、モックが入力に依らず同一の汎用文面を返し、「文面整えが**元の意味を保持**する」ことを E2E で固定できないことを再現確認した。
- Priority: P2
- Owner: Maintainer
- Scope: `03_Implement/deploy/tools/mock_local_llm.py`, `03_Implement/backend/scripts/verify_business_flow_e2e.sh`（シナリオ111）, `01_Plans/dogfood/business-flow-e2e-scenarios-2026-08-15.md`
- Related ADR/Spec: `00_Prompt/qualitative_card_quality_requirements.md`（文面整えは**元の意味を保持**し過剰言い換えしない）, `00_Prompt/ai_kj_execution_procedures.md` §1（名詞止め禁止・述語文）, `02_Architecture/api.md`（refine-card-text 契約）, `01_Plans/dogfood/business-flow-e2e-scenarios-2026-08-15.md`（シナリオ1のみが文面整えを固定）
- Expected verification level: `e2e`

## 課題

業務フローE2E で `refine-card-text`（文面整え）を固定しているのは **シナリオ1のみ**であり、そのアサーションは `"refinedText"` キーの存在だけを確認する。モックの `refine_card_text` は**入力に依らず同一の汎用文面**を返す:

```python
if task == "refine_card_text":
    return json.dumps({
        "refinedText": "（モック）カード文面の改善提案です。元の意味を保持しつつ明確化しています。",
        "reasoning": "同義語の選択と冗長表現の除去により可読性を向上。"})
```

したがって:

- **文面整えの核心要件「元の意味を保持（過剰言い換えをしない）」を E2E で一切検証できない**（qualitative_card_quality_requirements）。
- バックエンドが refine を無意味な/入力と無関係な文面に劣化させる（意味を落とす・幻覚を混入する）回帰が起きても、業務フローE2E は全部 pass する。
- 文面整えは rawな現場報告（半導体・介護・製造など）をカード化する際の中核操作であり、その品質が検証されないのは重大。

実機再現（iteration 181）:

```text
# cardText="歩留まりが下がってロット廃棄が増えた" を送る
# → refinedText="（モック）カード文面の改善提案です。元の意味を保持しつつ明確化しています。"
#   （入力と無関係な汎用文面。意味保持を検証できない）
```

### なぜ問題か

- **文面整えの品質（意味保持）が未固定**で、`refine` の「元の意味を保持」要件（qualitative_card_quality_requirements）を回帰から守れない。
- **操作カバーの偏り**: 業務フローE2E の11操作中、refine-card-text はシナリオ1のみで固定されており、カバーが最も薄い。

## 三要素分析（ADR-0067）

| 次元 | 分析 | 他次元への制約 |
|------|------|---------------|
| **業務設計** | 定性分析者は rawな現場報告を**意味を保持したまま**明確なカード文に整えたい。文面整えは「名詞止めを述語文へ」「冗長表現の除去」「元の意味の保持」を同時に満たす | 文面整えは **提案（read-only）** のまま。カード文面は人間の採否を経て確定（自動適用しない） |
| **データ設計** | refine-card-text のプロンプトは `Card text: <入力>` を含むため、モックは**入力を refinedText へ埋め込む**ことで「元の意味を保持」を決定的に表現できる | 既存シナリオ1の `"refinedText"` キー assert は、入力埋め込み後も成立（非後退） |
| **機能設計** | `refine_card_text` の応答を「元の意味（入力）を保持しつつ明確化」の形へ変更し、シナリオ111の refine チェックで**入力のキーフレーズ（例: 歩留まり）が保持される**ことを assert する。API契約（`RefineCardTextResponse`）は不変 | バックエンド実装・API契約は変更しない。既存シナリオ1は `"refinedText"` キーのみ assert のため非後退 |

## 対応方針

- 実施すること:
  1. `mock_local_llm.py` の `refine_card_text` で、プロンプトの `Card text:` から**入力テキストを抽出し refinedText へ埋め込む**（元の意味保持を決定的に表現）。
  2. シナリオ111（半導体製造）に **refine-card-text（文面整え）** を操作内容へ追加し、refine チェックで**入力のキーフレーズ（歩留まり）が保持される**ことを assert する（操作カバーをシナリオ1のみから拡大）。
- 実施しないこと:
  - refine-card-text の**バックエンド実装・API契約の変更**。
  - 既存シナリオ1の refine アサーションの変更（`"refinedText"` キーのみ assert・非後退）。

## 受入条件

- [x] 「歩留まりが下がってロット廃棄が増えた」の refine 応答に「歩留まり」が含まれる（実走行で確認）。
- [x] 既存シナリオ1相当（「待ち時間が長いと感じた」）も `"refinedText"` を返す（非後退・実走行で確認）。
- [x] シナリオ111の refine チェックが `"refinedText"` かつキーフレーズ「歩留まり」を assert し、業務フローE2E が **657/657 pass**。
- [x] `verify_dogfood_records.sh`・`docs_check.py` が pass。

## 検証計画

- `cd 03_Implement/backend && bash scripts/verify_business_flow_e2e.sh <PORT>` → 657/657（シナリオ111の SM ②文面整えが意味保持）
- `bash 01_Plans/dogfood/verify_dogfood_records.sh` → 構造照合 pass
- `python 01_Plans/docs_check.py` → docs-check passed

## 補足

- モックの入力埋め込みは「元の意味を保持する」ことを検証可能にするための決定性表現であり、実LLMの言い換え品質とは独立（本issueは検証ハーネスの能力向上）。
- ドッグフーディング観察起点（2026-08-16・iteration 181）: 半導体製造の raw現場報告（「歩留まりが下がってロット廃棄が増えた」）を refine へ送り、入力と無関係な汎用文面が返ることを再現。refine の「意味保持」がE2Eで検証不能であり、操作カバーもシナリオ1のみに偏っていることを特定した。
