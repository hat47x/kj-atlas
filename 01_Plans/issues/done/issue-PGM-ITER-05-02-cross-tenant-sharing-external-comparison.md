# Issue: PGM-ITER-05-02 組織境界を越えた共有パターンの外部比較調査

- Type: Planning / Research
- Status: Done
- Source Issue: `02_Architecture/post-mvp-business-scope-design-program.html` §15.2（第5反復三要素分析で発見）, `01_Plans/issues/done/issue-PGM-ITER-05-01-cross-tenant-collaboration-scoping.md`
- Priority: P3
- Owner: Maintainer
- Scope: `01_Plans/issues/`（調査結果のissue起票）, `02_Architecture/`（比較結果の設計正本）
- Related ADR/Spec: `02_Architecture/post-mvp-business-scope-design-program.html`（3拡張軸・第5反復）, `02_Architecture/collaboration-concurrency-comparison-2026-08-14.html`（既存調査。本issueが補う対象外）, `01_Plans/adr/ADR-0059-saas-tenant-authorization-boundary.md`
- Expected verification level: `docs-check`

## 課題

`issue-PGM-ITER-05-01`（第5反復スコープ起票）の三要素分析（`post-mvp-business-scope-design-program.html`
§15）で、既存の外部比較調査（`issue-PGM-ITER-03-01`、`collaboration-concurrency-comparison-2026-08-14.html`）が
共同編集の並行性モデルと単一組織内の組織モデル・bootstrap手順のみを対象としており、**組織の境界を越えた
共有・連携の仕組み**（Slack Connect の共有チャンネル、Microsoft 365のB2Bゲストアクセス、Google Workspaceの
外部共有、Notionのcross-workspace共有等）を調査対象に含んでいなかったことが判明した。

第5反復（テナント間連携）が実際に必要とする判断材料は後者であり、前者だけでは不十分である。

## 対応方針

- 実施すること:
  1. 類似製品（Slack Connect / Microsoft 365 B2B / Google Workspace 外部共有 / Notion cross-workspace）の
     **組織境界を越えた共有・連携の仕組み**を調査・比較する。
     - ゲスト個人単位の信頼と、組織（IdP）単位の信頼をどう分離しているか。
     - 招待・承認フロー（誰が招待でき、相手組織側で何を承認するか）。
     - 境界を越えたアクセスの取り消し・失効の仕組み。
  2. `03_Implement/backend/src/kj_atlas_api/tenant_context.py`の`resolve_verified_claim_tenant_context()`が
     現状要求する「テナント単位のIdP全部信頼」という粒度と、調査結果を対比する。
  3. 調査結果を設計正本（`02_Architecture/`のHTML＋Mermaid）として記録し、第5反復の認可プリミティブ設計の
     判断材料を供給する。
- 実施しないこと:
  1. 新しい認可プリミティブの実装（調査が先行）。
  2. §15.1が指摘した「ライブ共同編集」の実需要確認（別途、既存bundle export/importでどこまで満たせるかの
     実運用フィードバックが前提）。

## 受入条件

- [x] AC-1: 類似製品の組織境界を越えた共有・連携パターンの比較調査が完了し、設計正本として記録される。
  - 2026-08-25: `02_Architecture/cross-tenant-sharing-external-comparison-2026-08-25.html` として記録。Slack Connect / Microsoft Entra ID B2B collaboration / Google Workspace 外部共有 / Notion cross-workspace共有の4製品を、ゲスト個人単位の信頼と組織（IdP）単位の信頼の分離・招待承認フロー・取り消し失効の3観点で比較した。
- [x] AC-2: 比較結果が第5反復の認可プリミティブ設計（ADR化）の判断材料を供給する。
  - 2026-08-25: 同文書 §3-4 で `tenant_context.py` の `resolve_verified_claim_tenant_context()` が要求する「テナント単位のIdP全部信頼」という粒度と、4製品が持つ個人単位の信頼プリミティブとのギャップを識別し、新規プリミティブの設計・実装は行わずに判断材料として供給した。

## 検証

- `python 01_Plans/docs_check.py`
- 調査結果の設計正本がリンク切れ検査を通る。
