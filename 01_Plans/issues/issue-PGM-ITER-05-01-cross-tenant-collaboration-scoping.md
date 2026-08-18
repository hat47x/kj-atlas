# Issue: PGM-ITER-05-01 第5反復（テナント間連携）のスコープ起票

- Type: Planning
- Status: Open
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

- [ ] AC-1: 第5反復のスコープが三要素分析で起票される。
- [ ] AC-2: `PGM-ITER-03-01`（外部比較調査）との依存関係が明記される。

## 検証

- `python 01_Plans/docs_check.py`
