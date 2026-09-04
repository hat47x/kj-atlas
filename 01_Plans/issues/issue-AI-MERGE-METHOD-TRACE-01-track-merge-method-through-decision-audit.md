# Issue: AI-MERGE-METHOD-TRACE-01 merge方式を判断・監査まで追跡可能にする

> Issue本文は現在の実行に必要な情報へ絞り、実装履歴はGit/PRを正本とする。

- Type: Feature / Domain Integrity / AI Integration
- Status: Open
- Source Issue: `AI-MERGE-SEMANTICS-01`
- Priority: P2
- Owner: Maintainer
- Scope: `03_Implement/backend/src/kj_atlas_api/models.py`, `03_Implement/backend/src/kj_atlas_api/routes/ai.py`, `03_Implement/frontend/src/api/client.ts`, `03_Implement/frontend/src/domain/merge_suggestion_decisions.ts`, `03_Implement/frontend/src/domain/merge/decision_audit_events.ts`, `03_Implement/frontend/src/ui/MergeSuggestionsPanel.tsx`, `02_Architecture/api.md`
- Related ADR/Spec: `ADR-0069`, `AI-MERGE-SEMANTICS-01`, `AI-MERGE-PARTIAL-01`, `AI-MERGE-APPLY-01`, 継続dogfood R18/R19
- Expected verification level: `integration`

## 課題

merge promptは04ステップ型の近接整理と核融合法型の意味核統合を区別するが、共通 `MergeSuggestion` では方式が失われる。実mergeのデータ変換が同じでも、人間が後から「なぜこの統合を採ったか」を判断理由と一緒にたどるための監査文脈として方式には価値がある。

## 契約方針

- 候補語彙は `near_duplicate` / `kernel_fusion`。フィールド名は `mergeMethod` を第一候補とし、既存語彙と照合して確定する。
- remote/common提案はbackend正式schemaから方式を返す。新規provider応答の未知・欠落方式を黙って採用しない。
- 決定論ローカルfallbackは、その候補生成規則が近接整理に相当する場合だけ `near_duplicate` を付与する。Stream B固有metadataをremote/commonへ逆流させない。
- proposal → decision snapshot → decision auditへ同じ方式を通し、UIで判断前後に確認できるようにする。
- accept / partial の実mergeは、方式ラベルだけを理由に異なるデータ変換へ自動分岐しない。
- 旧Document・旧provider fixture・旧decision logは後方互換に読み込む。
- 自由記述 `residuals` は追加せず、元カードへのtraceabilityを残差の一次記録とする。

## 受入条件

- [ ] 機械可読な方式語彙とフィールド名を確定する。
- [ ] backendの新規provider提案で方式を欠落させない。
- [ ] remote/commonとlocal派生の契約分離を維持する。
- [ ] proposal → decision → auditで方式が一致する。
- [ ] UIで判断前後に方式を確認できる。
- [ ] 方式ラベルによる自動適用分岐を導入しない。
- [ ] 旧データ・fixtureとの後方互換を確認する。
- [ ] API文書と親Issueを実装結果へ同期する。
- [ ] 最終成果物を、意味を変えず自然な日本語として全文を読み直す。

## 完了境界

表示用ラベルを足すだけでは完了しない。新しい提案で方式を欠落させず、remote/commonとlocal派生の契約境界を壊さず、proposalから人間判断・監査まで同じ方式を追跡できることを回帰で固定した時点で完了とする。
