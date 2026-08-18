# Issue: PGM-ITER-03-01 第3反復（共同編集）の並行性モデル選定に必要な外部比較調査

- Type: Planning / Research
- Status: Done
- Source Issue: `02_Architecture/post-mvp-business-scope-design-program.html` §7-4, `01_Plans/research/direction-review-2026-08-13.md` 優先4
- Priority: P2
- Owner: Maintainer
- Scope: `01_Plans/issues/`（調査結果のissue・ADR起票）, `02_Architecture/`（比較結果の設計正本）
- Related ADR/Spec: `02_Architecture/post-mvp-business-scope-design-program.html`（3拡張軸・第3反復）, `01_Plans/adr/ADR-0067-three-element-constraint-design-method.md`
- Expected verification level: `docs-check`

## 課題

プログラムの3拡張軸（主体の複数化 → 成果物の複数化 → 境界の外部化）のうち、**第3反復（共同編集）の並行性モデル選定**は、類似製品の外部比較なしに判断すべきでないと明記されている。

> `post-mvp-business-scope-design-program.html:341`
> 未収集の外部知見: 類似製品（Miro / Notion / Figma / Slack / Atlassian）の組織モデル・bootstrap手順・共同編集の並行性モデルの比較調査は本版では未実施。第3反復（共同編集の並行性モデル選定）と第5反復（テナント間連携）では、この外部比較なしに判断すべきでない。

第3反復（および第5反復）に対応する issue は現状1件も存在しない（方向性レビュー優先4の指摘）。本issueは調査をスコープする。

## 対応方針

- 実施すること:
  1. 類似製品（Miro / Notion / Figma / Slack / Atlassian）の**共同編集の並行性モデル**を調査・比較する。
     - 楽観的並行制御（OT / CRDT）の採用状況
     - コンフリクト解決の利用者体験（自動merge / 手動 / last-write-wins）
     - 同時編集時のバージョン・リビジョン管理
  2. **組織モデル・bootstrap手順**の比較（誰がテナントを作るか・招待フロー）。
  3. 調査結果を設計正本（`02_Architecture/` のHTML＋Mermaid）として記録し、第3反復の並行性モデル選定の判断材料を供給する。
  4. 必要に応じて並行性モデル選定の ADR を起票する。
- 実施しないこと:
  1. 共同編集の実装（調査が先行）。
  2. 第5反復（テナント間連携）の設計（本issueは調査スコープ。結果は第5反復にも再利用）。

## 受入条件

- [x] AC-1: 類似製品の共同編集並行性モデルの比較調査が完了し、設計正本として記録される。
- [x] AC-2: 比較結果が第3反復の並行性モデル選定（ADR化）の判断材料を供給する。— **`ADR-0076`（第3反復の並行性モデル・Proposed）を起票**（D1=Aサーバ権威LWW＋既存CAS拡張を推奨）。採択は保守者の明示判断を待つ。

## 検証

- `python 01_Plans/docs_check.py`
- 調査結果の設計正本がリンク切れ検査を通る。

## 調査記録（2026-08-14、deep-research 105エージェント・3票反証検証）

設計正本: `02_Architecture/collaboration-concurrency-comparison-2026-08-14.html`

検証済みの主要事実:

- **Figma**: サーバ権威・property-level LWW（CRDT/OTではない・OTを明示的に却下）。ordered list は分数インデックス（base-95）。利用者に見えるマージUIなし。durability は S3 checkpoint（最大~60s喪失）→ DynamoDB journal（<1s喪失・2.2B changes/day）。
- **Miro**: ボード単一owner・譲渡可・5段階ロール（Owner/Co-owner/Editor/Commenter/Viewer）。ボード作成はチームMemberのみ。
- **Confluence**: 保存時コンフリクト検出（LWW）＋手動 Overwrite/Merge/Discard。文書化された履歴破損障害 CONFSERVER-32286。
- **OT vs CRDT**: Sun et al.（OTキャンプ・COI）の反論は陳腐化気味。Automerge（クライアント側merge・順序非依存）は P2P/E2EE に適合。
- **Notion / Slack / Jira**: 一次ソースが検証を通過せず未確認（open questions として記録）。

**第3反復への勧告（判断材料）**: サーバ権威 LWW＋既存CAS（ETag/If-Match 拡張）を推奨（選択肢A）。クライアントCRDTはオフライン/P2P/E2EE要件時のみ。Miro の単一owner・5段階ロールは第2反復（documents所有）の参照。選択肢は ADR として採否判断（本issueは材料供給・決定ではない）。
