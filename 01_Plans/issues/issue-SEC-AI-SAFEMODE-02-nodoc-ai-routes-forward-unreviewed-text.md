# Issue: SEC-AI-SAFEMODE-02 文書非依存AIルートが未レビュー本文をLLMへ送れる境界を持つ

> ドッグフーディング iteration 44（カスタマーサポート品質管理シナリオ）で実機検証により発見。

- Type: Security
- Status: In Progress
- Source Issue: `SEC-AI-SAFEMODE-01`（Done・6ルート配線の残余）
- Priority: P1
- Owner: Maintainer
- Scope: `03_Implement/backend/src/kj_atlas_api/routes/ai.py`, `03_Implement/backend/src/kj_atlas_api/models_ai.py`, `02_Architecture/api.md`, `03_Implement/backend/tests/test_ai_safemode.py`
- Related ADR/Spec: `01_Plans/adr/ADR-0068-ai-safemode-d2-b-422-reject.md`, `01_Plans/issues/issue-AI-IR-PROJECTION-01-llm-input-ir-as-ai-input-path.md`（AC-4 が将来のIR層で同一境界を塞ぐ・ADR-0069 採択待ち）
- Expected verification level: `integration`

## 三要素整合（ADR-0067）

- **業務設計（Business）**: `SEC-AI-SAFEMODE-01` は「未レビュー本文を外部LLMへ送出しない」を**API境界で fail-closed** と定めた（AC-1「全対象エンドポイントについて integration テストで固定」）。この約束は「文書コンテキストを持つルート」にしか実装されていない。品質管理シナリオ（証言カード）のように**未レビュー証言を AI で矛盾検出したい**利用者journeyでは、クライアントが未レビューカードの本文を渡すとそのまま外部LLMへ送られる。
- **データ設計（Data）**: `DetectContradictionRequest` / `SuggestCardGroupsRequest` / `RefineCardTextRequest` にレビュー状態フィールドが無い。未レビューかどうかをAPIが知る術がない。doc文脈ルートの `_reject_unreviewed_text` は文書の `cards[].textReviewed` を見るが、文書非依存ルートには当てはめられない。
- **機能設計（Function）**: `detect-contradiction` / `suggest-card-groups` / `refine-card-text` の3ルートは `_reject_unreviewed_text` を呼ばない（`routes/ai.py` で配線済みは suggest_layout / suggest_merges / suggest_island_summary / generate_narrative / check_narrative / propose_island_summary の6ルートのみ）。「API境界で強制」というSEC-AI-SAFEMODE-01の決定が3ルートに未適用のまま。

## 課題

- 現在の問題: 下記3ルートは、クライアントが渡すカード本文をレビュー状態の検査なしで LLM プロンプトへ埋め込む。frontend の SafeMode フィルタが唯一の防御だが、API境界での fail-closed ではない（SEC-AI-SAFEMODE-01 の決定との不整合）。

  | ルート | プロンプト構築 | レビュー検査 |
  |---|---|---|
  | `POST /ai/detect-contradiction` | `_build_detect_contradiction_prompt` が `cardA.text` / `cardB.text` を直接埋め込む（`routes/ai.py:1268-1274`） | 無し |
  | `POST /ai/suggest-card-groups` | `cards[].text` を埋め込む | 無し |
  | `POST /ai/refine-card-text` | `payload.cardText` を埋め込む（`routes/ai.py:1226`） | 無し |

- 利用者または開発への影響:
  - **実機検証（iteration 44）**: `detect-contradiction` に未レビュー本文のカード2枚を送ると **200** で構造化応答が返り、LLM（モック）へプロンプトが送信される。`suggest-island-summary` が未レビュー文で **422** を返すのと非対称。
  - 未レビュー証言（例: 確認前のクレーム発言・インタビュー逐語）が外部LLMベンダーへ送信され得る。`SEC-LLM-AUDIT-01` の監査は通過するため「監査があるから漏れない」とはならない。
  - `AI-IR-PROJECTION-01` AC-4 が IR 生成層で `constraints.safe_mode` を強制する予定だが、`ADR-0069` は Proposed のままであり現行出荷物の境界は開いている。

## 対応方針

- 実施すること（候補案。保守者判断を要する）:
  1. **案a（最小・API境界で強制）**: 上記3ルートのリクエストへ `allowUnreviewedText: bool | None`（doc文脈ルートと同じ `settings.allow_unreviewed_ai_text` ゲート付き）を追加し、未レビュー文を含む可能性を示すクライアント送信を `422`（`unreviewed_text_not_allowed`）で拒否する。既存の `test_ai_safemode.py` パターンを流用して integration テストを追加。
     - 課題: リクエストに「レビュー済みか」をどう運ぶか。カード本文のみで運ぶ場合、クライアントが嘘を付けない保証は無い（frontend が真値を送る前提は変わらない）。真に境界で強制するには doc 参照 or カードID→サーバ側解決が必要（→ AI-IR-PROJECTION-01 の IR 層と重なる）。
  2. **案b（適用範囲の明示・即時）**: 「文書非依存ルートは明示コンテンツ操作であり SafeMode の自動検査対象外」を api.md / SafeMode 文書へ明記し、frontend 側で未レビューカードを選択できないようにする（frontend は現状これらの操作を露出していないため実影響は小さい）。
  3. **案c（IR層へ委譲）**: `AI-IR-PROJECTION-01` AC-4 の適用を待つ。その間は案bの文書化を行う。
- 実施しないこと:
  - 既存の外部送出ガード（二段opt-in・ホストallowlist・trusted-HTTP検証）の変更 — 妥当であり対象外（`AI-IR-PROJECTION-01` と同見解）。
  - frontend の既存 SafeMode 実装の削除 — 二重防御として残す。

## 受入条件

- [x] 案a を採択: 3ルートが未レビュー文で 422（`unreviewed_text_not_allowed`）を返し、レビュー済み文で 200 を返すことを integration テストで固定した。— `models_ai.py` に `textReviewed`（既定 false = fail-closed）＋`allowUnreviewedText` を追加。`routes/ai.py` に `_reject_unreviewed_cards` を追加し3ルートへ配線。`test_ai_safemode.py` に5テスト追加（**9 pass**）。api.md にフィールドと fail-closed 既定を明記。呼出側（`verify_business_flow_e2e.sh` シナリオ1〜3・`verify_kj_multi_round.sh`・`run_ai_eval.py`・`test_ai_eval_pipeline.py`）へ `textReviewed: true` を追加し、E2E に未レビュー→422 の負例を固定（**15/15 pass**）。
- [x] **iteration 48 で更に2ルートの穴を発見・修正**（カバレッジカナリアで全量検査へ拡張）: ① `suggest-document-title`（文書非依存・`cardTexts` をLLMへ送るがレビュー検査なし）→ `textReviewed`＋`allowUnreviewedText` 追加・`_reject_unreviewed_cards` 配線。② `summarize-island-relation`（`ai_relations.py`・**doc 文脈なのに** `_reject_unreviewed_text` 未配線 — SEC-AI-SAFEMODE-01 の6ルート配線の盲点）→ `allowUnreviewedText` 追加・`_reject_unreviewed_text` 配線。**`test_ai_safemode.py` に「全コンテンツAIルートのカバレッジカナリア」を追加**（`_CONTENT_ROUTE_CASES` 10ルート×未レビュー→422。新ルート追加時の穴を構造的に検出）。E2E シナリオ7 で未レビュー→422 を固定（**29/29 pass**）。
- [ ] 案b（適用範囲外の文書化）は 案a 採択により不要。
- [ ] SEC-AI-SAFEMODE-01 の既存6ルートの回帰を壊さないことをフルスイートで確認する。

## 検証計画

- 実行する確認: モックLLM＋バックエンドで `detect-contradiction` に未レビュー文を送り、現状 200 であること（=穴の存在）と、案a適用後に 422 になることを実走行で確認。
- 期待結果: 未レビュー本文の外部送出が API 境界で拒否される（または適用範囲外として明示される）。

## 補足

- iteration 44 の E2E は本issueの**現状**（200）を固定しない。detect-contradiction の「正常系」は `verify_business_flow_e2e.sh` シナリオ3で固定し、SafeMode境界の扱いは本issueの判断後に確定させる。
- `refine-card-text` は文面変更を提案する操作であり、証言の原文保持の観点でも文脈上の注意を要する（iteration 44 シナリオ3の注意事項）。
