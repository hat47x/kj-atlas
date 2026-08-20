# Issue: PGM-ITER-05-01 第5反復（テナント間連携）のスコープ起票

- Type: Planning
- Status: Done
- Source Issue: `02_Architecture/post-mvp-business-scope-design-program.html`（3拡張軸の第3軸・§7-4）, `01_Plans/research/direction-review-2026-08-13.md` 優先4
- Priority: P3
- Owner: Maintainer
- Scope: `01_Plans/issues/`, `02_Architecture/`
- Related ADR/Spec: `02_Architecture/post-mvp-business-scope-design-program.html`, `01_Plans/adr/ADR-0059-saas-tenant-authorization-boundary.md`
- Expected verification level: `docs-check`

## 課題

プログラムの3拡張軸の第3軸は「境界の外部化」（テナント間連携）。第5反復はこの軸に対応するが、`post-mvp-business-scope-design-program.html:341` が「第3反復（共同編集の並行性モデル選定）と第5反復（テナント間連携）では、この外部比較なしに判断すべきでない」と明記している。第5反復に対応する issue は現状1件も存在しない（方向性レビュー優先4）。

## 対応方針

- 実施すること:
  1. 第5反復のスコープを三要素分析法（ADR-0067）で起票する:
     - **業務設計**: どのテナント間連携journeyを対象にするか（共有・公開・共同作業）。
     - **データ設計**: テナント境界を越えるデータの扱い（ADR-0059 の境界との整合）。
     - **機能設計**: 外部化のAPI契約（webhook・共有リンク・外部主体の認証）。
  2. `PGM-ITER-03-01`（外部比較調査）の結果が第5反復にも適用されることを明記する。
- 実施しないこと:
  1. テナント間連携の実装（スコープ起票のみ・外部比較調査の完了待ち）。

## 受入条件

- [x] AC-1: 第5反復のスコープが三要素分析で起票される。
- [x] AC-2: `PGM-ITER-03-01`（外部比較調査）との依存関係が明記される。

## 検証

- `python 01_Plans/docs_check.py`

## 対応記録（2026-08-20）

三要素分析を`post-mvp-business-scope-design-program.html` §15「第5反復: 組織間連携の三要素分析」に
起票した。

- AC-1: §15.1で「非同期の受け渡し（既存`InquiryBundleV1`のexport/import）」と「ライブ共同編集」を
  業務設計として切り分け、後者だけが§2で指摘した「別テナントのIdPに属する利用者」という構造的差異に
  直面することを整理した。`tenant_context.py`の`resolve_verified_claim_tenant_context()`を確認し、
  現状はテナント単位のIdP全部信頼という粗い粒度しか無いことをデータ・機能設計として記録した。
- AC-2: 当初想定どおりには成立しないことが判明した——`PGM-ITER-03-01`の完了済み調査は共同編集の並行性
  モデルと単一組織内の組織モデル・bootstrap手順のみを対象とし、組織境界を越えた共有・連携の仕組み
  （Slack Connect / B2Bゲスト等）は調査対象外だった。§15.2で依存関係を正確に明記し、不足分を
  `issue-PGM-ITER-05-02`として別途起票した。
- 実装（新しい認可プリミティブの設計）は本issueの範囲としない（§15.3）。
- 検証: `python 01_Plans/docs_check.py`（既知の`DOC-NORM-02`偽陽性以外は失敗なし）、
  `03_Implement/backend/scripts/check_design_consistency.py`（0 errors, 0 warnings）。
