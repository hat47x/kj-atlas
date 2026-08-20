# Issue: KJ-PROMPT-ALIGN-01 実行時プロンプトが ai_kj_execution_procedures.md と乖離している

- Type: Product Invariant / AI Integration
- Status: Done
- Source Issue: `01_Plans/research/direction-review-2026-08-13.md` 優先3-4
- Priority: P2
- Owner: Maintainer
- Scope: `03_Implement/backend/src/kj_atlas_api/routes/ai.py`（prompt builder群）
- Related ADR/Spec: `00_Prompt/ai_kj_execution_procedures.md`, `00_Prompt/kj_technique.md`, `01_Plans/adr/ADR-0067-three-element-constraint-design-method.md`
- Expected verification level: `integration`

## 課題

`00_Prompt/ai_kj_execution_procedures.md` は KJ 各操作の判断基準・停止条件を normative に定めているが、実行時プロンプトがこれと乖離していた。方向性レビュー優先3-4 の指摘（「Normative文書が既にあるので設計は不要で、実装のみ」）。

| 操作 | normative 要求（ai_kj_execution_procedures.md） | 修正前の実行時プロンプト |
|---|---|---|
| `refine_card_text` | 名詞止め禁止・動詞で終わる文（§1） | 名詞止めへの言及なし |
| `suggest_card_groups` | 2〜3枚制約・孤立カードを無理に入れない・分類ではなく訴えの類似性で束ねる（§2） | 「**thematic** islands」と分類誘導。制約なし |
| `suggest_island_summary` | 表札検査（転置・戻し）・分類名ではなく代弁・名詞止め禁止（§3） | 表札検査なし・分類/名詞止めの禁止なし |
| `generate_narrative` | A/B照合を自己実行（§7） | A/B照合への言及なし |

## 対応方針

- 実施すること（実装のみ・prompt 文言の整合）:
  1. `refine_card_text`: 述語を伴う文・名詞止め禁止を明示。
  2. `suggest_card_groups`: 「thematic」を除去し、2〜3枚制約・孤立カードを無理に入れない・訴えの類似性を明示。
  3. `suggest_island_summary`: 表札検査（転置検査・戻し検査）と、分類名ではなく代弁・名詞止め禁止を明示。
  4. `generate_narrative`: A/B照合の自己実行と方向別の警告報告を明示（`warnings` スキーマは既存）。
- 実施しないこと:
  1. AI応答スキーマの変更（本issueは prompt 文言のみ。A/B照合の方向・件数フィールドは `KJ-AB-CROSS-CHECK-01` で別途対応済み）。
  2. 推論深度・推奨モデルの変更（AGENTS.md §1.2 が別途管理）。

## 受入条件

- [x] AC-1: `refine_card_text` prompt が名詞止め禁止を明示する。
- [x] AC-2: `suggest_card_groups` prompt が「thematic」を含まず、2〜3枚制約・孤立カード非強制・訴えの類似性を明示する。
- [x] AC-3: `suggest_island_summary` prompt が表札検査（転置・戻し）と代弁・名詞止め禁止を明示する。
- [x] AC-4: `generate_narrative` prompt が A/B照合の自己実行を明示する。

## 検証

- `python -m pytest tests/test_ai_prompt.py -q`
- `python 01_Plans/docs_check.py`

## 対応記録（2026-08-14）

実装のみで対応した。

- `_build_refine_card_text_prompt`: 「predicate-bearing sentence (動詞で終わる文)、never a noun-phrase stop (名詞止め)」を追加。
- `_build_suggest_card_groups_prompt`: 「thematic」を削除し、「Bundle cards by the similarity of what they are appealing for」「Each first-level bundle is 2-3 cards (rarely 4)」「Do not force a card into a bundle」を追加。
- `_build_island_summary_prompt`: 表札検査（Transposition / Return check）と「predicate-bearing advocacy sentence」「分類名」「名詞止め」の禁止を追加。
- `_build_generate_narrative_prompt`: A/B照合の自己実行と `b_missing_in_a` / `a_missing_in_b` の警告報告を追加。
- テスト: `test_ai_prompt.py` に4テスト追加（名詞止め禁止・束ね規約・表札検査・A/B照合）。全 AC 完了。
