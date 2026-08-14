# Issue: PGM-ITER-04-01 第4反復（成果物の複数化）のスコープ起票

- Type: Planning
- Status: Open
- Source Issue: `02_Architecture/post-mvp-business-scope-design-program.html`（3拡張軸の第2軸）, `01_Plans/direction-review-2026-08-13.md` 優先4
- Priority: P2
- Owner: Maintainer
- Scope: `01_Plans/issues/`, `02_Architecture/`
- Related ADR/Spec: `02_Architecture/post-mvp-business-scope-design-program.html`, `02_Architecture/inquiry_journey_model.html`
- Expected verification level: `docs-check`

## 課題

プログラムの3拡張軸の第2軸は「成果物の複数化」である。現行は単一文書（DocumentV1）が成果物の中心だが、第4反復では成果物の種類・関係（複数文書・レポート・共有パッケージ等）を拡張する。これに対応する issue は現状1件も存在しない（方向性レビュー優先4）。

## 対応方針

- 実施すること:
  1. 第4反復のスコープを三要素分析法（ADR-0067）で起票する:
     - **業務設計**: どの成果物種類・利用者journeyを対象にするか（単独実務者の成果物 → 複数成果物の関係）。
     - **データ設計**: 成果物間の関係（親子・参照・バージョン）を現行データ設計の上に載せるか、第2反復の補正（documents所有/lifecycle）と合わせるか。
     - **機能設計**: 成果物の生成・関係付け・共有のAPI契約。
  2. 第2反復（documents所有/lifecycle・DATA-DOC-LIFECYCLE-01）との依存関係を明記する。
- 実施しないこと:
  1. 成果物の複数化の実装（スコープ起票のみ）。

## 受入条件

- [ ] AC-1: 第4反復のスコープが三要素分析で起票される。
- [ ] AC-2: 第2反復（documents所有/lifecycle）との依存関係が明記される。

## 検証

- `python 01_Plans/docs_check.py`
