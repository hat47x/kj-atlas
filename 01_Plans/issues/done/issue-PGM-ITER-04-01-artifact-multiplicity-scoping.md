# Issue: PGM-ITER-04-01 第4反復（成果物の複数化）のスコープ起票

- Type: Planning
- Status: Done
- Source Issue: `02_Architecture/post-mvp-business-scope-design-program.html`（3拡張軸の第2軸）, `01_Plans/research/direction-review-2026-08-13.md` 優先4
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

- [x] AC-1: 第4反復のスコープが三要素分析で起票される。
- [x] AC-2: 第2反復（documents所有/lifecycle）との依存関係が明記される。

## 検証

- `python 01_Plans/docs_check.py`

## 対応記録（2026-08-20）

三要素分析を`post-mvp-business-scope-design-program.html` §13「第4反復: 成果物の複数化の三要素分析」に
起票した。着手前に実装状況を確認した結果、本issueが「現行は単一文書が成果物の中心」と課題設定していた
前提は起票時点で既に成立していなかった——`issue-DOMAIN-W-ITERATION-01`（W型累積KJ法支援）が
`ADR-0057`の採択済み設計目標に基づき、第2の成果物型`InquiryBundleV1`をtenant-scoped backend永続化まで
含めて先行実装していた（AC-4〜AC-10・AC-6a・AC-12・AC-13完了）。

- AC-1: §13.1で実装状況を三要素表として整理し、§13.2で新たな欠落（`InquiryBundleV1`に所有者・可視性境界が
  無い）を発見・記録した。
- AC-2: 第2反復への依存は当初想定（documents所有/lifecycleの上に成果物関係を載せる）ではなく、
  「`DocumentV1`用に確立した所有者・可視性モデルを、既に実装済みの第2の成果物型へ遡って適用するか」という
  順序が逆の依存であることが判明し、§13.3で明記した。
- §13.2で発見した欠落は`issue-SEC-INQUIRY-BOUND-01`として別途起票した（本issueは「実施しないこと:
  実装」の範囲を守り、判断・設計を要する実装を持ち出さない）。
- 検証: `python 01_Plans/docs_check.py`（既知の`DOC-NORM-02`偽陽性以外は失敗なし）、
  `03_Implement/backend/scripts/check_design_consistency.py`（0 errors, 0 warnings）。
