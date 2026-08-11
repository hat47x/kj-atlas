# Issue: DOMAIN-TITLE-01 文書タイトルのAI提案生成

- Type: Feature
- Status: Done
- Source Issue: N/A
- Priority: P2
- Owner: Maintainer
- Scope: `03_Implement/frontend/src/ui/SuggestionPanel.tsx`, `03_Implement/backend/src/kj_atlas_api/routes/ai.py`
- Related ADR/Spec: `ADR-0049-external-flat-rate-agent-collaboration.md` (Proposed), `02_Architecture/design/admin-surface-metadata-display-correction.html`
- Expected verification level: `e2e`

## 課題

- 現在の問題: 文書タイトルは利用者が手動で入力する以外に手段がなく、内容を反映したタイトルが付与されない文書が蓄積しやすい。特に新規作成直後や共有前の時点で、適切なタイトルがないと文書の識別性が低下する
- 利用者または開発への影響: 文書一覧や管理面での文書識別が困難になる。管理面のタイトル表示補正（2026-08-08）によりタイトルの重要性はさらに高まっている

## 対応方針

- 実施すること:
  1. AIによる文書タイトル候補の生成（既存SuggestionPanelパターンに準拠）
  2. 1〜3件の候補を並列提示（順位付け・スコア表示なし）
  3. per-proposalの明示Adopt/Reject（一括採用なし）
  4. SafeMode ON時は未レビューカード本文をAIへ送信しない
  5. トリガー: タイトル編集フィールドの「タイトルを提案」ボタン（明示要求時のみ。リアルタイム性不要）
  6. 推奨モデル: DeepSeek（低〜中の推論深度で十分。ローカルLLMもprovider abstractionの範囲内で理論上選択可能）
- 実施しないこと:
  1. タイトルの自動決定・自動適用（proposal-onlyを遵守）
  2. スコア・ランキング・「最適」表示
  3. タイトル変更のMergeDecisionLog記録（タイトルはmerge判断対象ではない）
  4. provider=none時のフォールバック代替
  5. 高品質なタイトル生成の追求（人間が書き換える前提。低品質許容）

## 予算申告

- 複雑性予算（ADR-0043 CB-1..4）: 初期表示への純増=なし（既存SuggestionPanelへの提案種別追加）。保留操作の距離=不変。取り消し導線=Rejectで即時取消
- 性能予算（ADR-0046 PB-1..5）: N/A（AI呼び出しは既存のai route経由、新規の重い同期処理なし）
- 触れるUQ次元（ADR-0044）: UQ-1（操作性 — タイトル入力の補助）、UQ-6（認知的抑制 — 候補を並列提示し誘導しない）

## 受入条件

- [ ] タイトル候補が1〜3件、順位付けなしで並列表示される
- [ ] Adoptした場合のみDocument.titleが更新される。Reject時は変更なし
- [ ] SafeMode ON時は未レビューカード本文がAIへの送信内容に含まれない
- [ ] provider=none時は「タイトル提案」操作自体が無効化または非表示になる（provider無効状態を劣化フォールバックとして扱わない）
- [ ] 低品質な提案でも表示され、人間が編集できる（品質によるフィルタリングを行わない）

## AIレーン宣言（GENAI-GOV-01）

- Lane: C（提案型生成 — AIが候補を生成し人間が審査）
- データ境界: タイトル提案のため、島ラベル・レビュー済みカード本文・関係構造をAIへ送信。SafeMode ON時は未レビューカード本文を除外。カードのka（声・価値）フィールドはレビュー状態に応じて送信制御
- SafeMode/監査/人間レビュー境界: 既定ON / proposal-only / human_reviewed人手昇格（タイトルはmerge判断対象外のためDecisionLog非記録だが、Adopt操作自体は人間の明示操作）
- Lane Dの場合: N/A

## 検証計画

- 実行する確認:
  1. タイトル候補生成のPlaywright e2e（provider mock使用）
  2. SafeMode ON/OFFでの送信内容差分の単体テスト
  3. provider=none時のUI非表示確認
  4. 日本語タイトル生成の品質確認（自動判定ではなく人間レビュー）
- 期待結果:
  1. 候補が並列表示され、順位・スコアがない
  2. Adopt/Rejectが正しく動作する
  3. SafeMode ON時に未レビュー本文が送信されない


## 完了記録（2026-08-12）

POST /ai/suggest-document-title + DocumentTitleEditor + e2e test実装済み。実機動作確認はKJ_ATLAS_DEEPSEEK_API_KEY投入後に実施
## 補足

- 依存: 既存SuggestionPanelの提案種別拡張が可能であること（構造確認要）
- 本issueは設計判断 `admin-surface-metadata-display-correction.html` の補正（管理面タイトル表示）と対になる。タイトルが識別メタデータとしての重要性を持つ以上、その品質を確保する手段が必要
- ADR-0049（外部エージェント連携）のAcceptを待たずに着手可能（内部AI提案パターンに完全準拠するため）
