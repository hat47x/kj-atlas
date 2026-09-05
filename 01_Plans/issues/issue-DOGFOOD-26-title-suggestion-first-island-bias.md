# Issue: DOGFOOD-26 タイトル提案が最初の島ラベルだけを参照し、複数島の全体テーマを検証できない

- Type: Process / Verification gap（ドッグフーディング観察）
- Status: Done
- Source Issue: ドッグフーディング iteration 190（シナリオ120・アミューズメント 実装時の実走行観察）。2島の文書（集客・客層戦略 / ゲーム機の維持・景品利益）で `suggest-document-title` を実行しても、モックが**最初の島ラベルだけ**を候補タイトルに埋め込み、**複数島の文書で全体テーマ（全島を反映したタイトル）**を検証できないことを再現確認した。
- Priority: P2
- Owner: Maintainer
- Scope: `03_Implement/deploy/tools/mock_local_llm.py`, `03_Implement/backend/scripts/verify_business_flow_e2e.sh`（シナリオ120）, `01_Plans/dogfood/business-flow-e2e-scenarios-2026-08-15.md`
- Related ADR/Spec: `00_Prompt/ai_kj_execution_procedures.md`（文書タイトル提案）, `02_Architecture/api.md`（suggest-document-title 契約）, `01_Plans/issues/issue-DOGFOOD-18-title-suggestion-not-grounded-in-canvas-content.md`（文書テーマ接地）, `01_Plans/issues/done/issue-DOGFOOD-25-check-narrative-multi-island-omission.md`（先頭島バイアスの同型）
- Expected verification level: `e2e`

## 課題

`mock_local_llm.py` の `suggest_document_title` は、**最初の島ラベルだけ**を候補タイトルへ埋め込む（DOGFOOD-18 で文書テーマ接地は実現したが「先頭島ラベル固定」のまま）:

```python
if task == "suggest_document_title":
    match = _TITLE_ISLAND_LINE.search(prompt)  # 先頭の島ラベル行だけ
    label = match.group(1).strip() if match else ""
    return json.dumps({"candidates": [{"title": f"（モック）{label}のタイトル候補"}]})
```

したがって:

- **複数島の文書で「全体テーマ（全島を反映したタイトル）」を検証できない**。タイトル候補が先頭島のラベルしか反映しない。
- 業務フローE2E のタイトル提案シナリオ（8・113）は**すべて単一島**のため、この制限が顕在化していなかった。
- タイトルは「文書全体の表象」（KJ法）であり、複数島の文書で全体テーマを捉えることが核心。その検証が単一島に限定されている。

実機再現（iteration 190）:

```text
# 2島（集客・客層戦略 / ゲーム機の維持・景品利益）で suggest-document-title
# → {"title":"（モック）アミューズメントの集客・客層戦略のタイトル候補"}
#   （先頭島ラベルのみ・ゲーム機の維持・景品利益を反映しない）
```

### なぜ問題か

- **タイトルの全体テーマ反映が未検証**: 複数島の文書で、タイトルが全島のテーマを捉えているか（文書全体の表象として機能するか）を E2E で検証できない。
- **先頭島バイアス**: DOGFOOD-25（A/B照合の先頭島固定）と同型の制限が、タイトル提案にも残っている。

## 三要素分析（ADR-0067）

| 次元 | 分析 | 他次元への制約 |
|------|------|---------------|
| **業務設計** | 定性分析者は複数島の文書に対し、**全体テーマ（全島のラベルを反映）**を捉えるタイトル候補を得たい。先頭島だけの反映では文書全体の表象にならない | タイトルは **proposal（read-only）** のまま。自動確定しない |
| **データ設計** | タイトルプロンプトは `Island labels:` 節に**全島ラベル**を含むため、モックは**全島ラベルを候補へ埋め込む**ことで「全体テーマの反映」を決定的に表現できる | 既存の単一島シナリオ（8・113）はラベル1件のまま成立（非後退） |
| **機能設計** | `suggest_document_title` の応答を「（モック）<全島ラベル>のタイトル候補」へ変更し、シナリオ120のタイトルチェックで**両方の島ラベルを参照**することを assert する。API契約（`SuggestDocumentTitleResponse`）は不変 | バックエンド実装・API契約は変更しない。既存シナリオは `"candidates"` キー・単一ラベル assert のため非後退 |

## 対応方針

- 実施すること:
  1. `mock_local_llm.py` の `suggest_document_title` で、`Island labels:` 節の**全島ラベル**を抽出して候補タイトルへ埋め込む（先頭島ラベル固定を廃止）。
  2. シナリオ120（アミューズメント・2島 amu-grow/amu-ops）で、**両方の島ラベルを反映するタイトル**を固定する。
- 実施しないこと:
  - suggest-document-title の**バックエンド実装・API契約の変更**。
  - 既存シナリオ（8・113・単一島）のアサーションの変更（非後退）。

## 受入条件

- [x] 2島（集客・客層戦略 / ゲーム機の維持・景品利益）のタイトル候補が**両方の島ラベル**を参照する（実走行で確認）。
- [x] 単一島（書店・棚づくり）は従来どおり単一ラベル（非後退・実走行で確認）。
- [x] シナリオ120のタイトルチェックが両方の島ラベルを assert し、業務フローE2E が **720/720 pass**（並行編集によるMGシナリオの干渉がない場合）。
- [x] `verify_dogfood_records.sh`・`docs_check.py` が pass。

## 検証計画

- `cd 03_Implement/backend && bash scripts/verify_business_flow_e2e.sh <PORT>` → 720/720（シナリオ120の AM ⑤タイトル提案が両島ラベルを参照）
- `bash 01_Plans/dogfood/verify_dogfood_records.sh` → 構造照合 pass
- `python 01_Plans/docs_check.py` → docs-check passed

## 補足

- モックの全島ラベル埋め込みは「タイトルが文書全体のテーマを反映する」ことを検証可能にする決定性表現であり、実LLMのタイトル生成品質とは独立（本issueは検証ハーネスの能力向上）。DOGFOOD-18（文書テーマ接地）の延長。
- ドッグフーディング観察起点（2026-08-16・iteration 190）: アミューズメント（2島）で suggest-document-title を実行し、先頭島ラベルのみを反映するタイトル候補が返ることを再現。複数島の文書で全体テーマのタイトルが検証不能であることを特定した。
