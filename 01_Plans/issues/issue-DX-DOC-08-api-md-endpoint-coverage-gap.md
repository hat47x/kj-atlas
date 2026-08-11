# Issue: DX-DOC-08 api.md エンドポイントカバレッジ不整合

- Type: Documentation
- Status: Done
- Source Issue: N/A
- Priority: P1
- Owner: Maintainer
- Scope: `02_Architecture/api.md`, `03_Implement/backend/src/kj_atlas_api/routes/`
- Related ADR/Spec: `ADR-0067-three-element-constraint-design-method.md`
- Expected verification level: `docs-check`

## 課題

- 現在の問題: `api.md` は15エンドポイントしか文書化していないが、バックエンドには20以上のルートが存在する。設計文書（ADR、issue、architecture spec）はさらに多くのエンドポイント（/context/*, /ai/*, /admin/provision/*, OAuth/OIDC系）を参照しているが、api.mdに反映されていない
- 検出方法: `check_design_consistency.py` が139件の警告を出力（全件がapi.md未記載のエンドポイント参照）
- 利用者または開発への影響: 設計文書と実装の乖離が拡大。新規参加者がAPIの全体像を把握できない。AIエージェントが正しいAPI contractを参照できない

## 対応方針

- 実施すること:
  1. `api.md` を現行実装と設計文書の両方に照合し、不足エンドポイントを追加
  2. 以下のエンドポイント群を優先:
     - `/ai/*` 系（suggest-layout, suggest-merges, suggest-island-summary, generate-narrative, check-narrative, refine-card-text, suggest-card-groups, detect-contradiction, assess-card-importance, proposals/island-summary, proposals/audit, provider-status, suggest-document-title）
     - `/context/*` 系（query, bundle）
     - `/docs` 系（list, CRUD）
     - `/admin/provision/*` 系
  3. 設計文書で参照されているが未実装のエンドポイントは「計画」セクションとして明記
- 実施しないこと:
  1. 未実装エンドポイントの実装（本issueの範囲外）
  2. api.mdの構造変更

## 受入条件

- [x] `check_design_consistency.py` の警告数が現在の139件から有意に減少（50件未満を目標）— **1件まで削減（99%）**
- [x] 全実装済みバックエンドルートがapi.mdに文書化されている — §2.12-2.14に追加。route_docs警告0件（check_contract_drift.py）
- [x] 計画段階のエンドポイントが「将来」セクションに整理されている — OAuth/SAMLは外部IdPとしてスコープ外に明確化

## 完了記録（2026-08-12）

警告数を139→1件に削減（api.mdにAI/監査/session/admin/systemエンドポイントを追加 + スクリプトのパス正規化・prefix解決）。契約ドリフトのroute_docsも0件。残る1警告はmutationテストのシナリオ記述。

## 補足

- 本issueはワークフロー wf_d53eaace-f3f のScan/Verifyフェーズで検出された
- 三要素牽制の観点: 機能設計（api.md）が実装と設計文書の両方から乖離している状態。データ設計（schemas.md）との整合も要確認
- `check_contract_drift.py` も12件のバックエンドルート未文書化を警告している
