# Issue: DOGFOOD-01 kj-atlas によるプロジェクト自己管理の開始

- Type: Process
- Status: Draft
- Source Issue: N/A
- Priority: P1
- Owner: Maintainer
- Scope: `01_Plans/`, `02_Architecture/`, 新規 kj-atlas 文書
- Related ADR/Spec: `ADR-0042-product-value-realization-loop.md`, `ADR-0067-three-element-constraint-design-method.md`, `02_Architecture/dogfooding-ai-collaboration-plan.html`
- Expected verification level: `docs-check`

## 課題

- 現在の問題: 本プロジェクトの設計判断・issue・ADRの間の依存関係が文書間の相互参照としてしか表現されておらず、全体像の把握・矛盾の検出・判断の系譜追跡が困難
- 利用者または開発への影響: 設計判断の不整合（例: 管理面タイトル非表示問題）が早期に発見されない。新規参加者がプロジェクト構造を理解するコストが高い

## 対応方針

- 実施すること:
  1. 本プロジェクトのADR・issue・設計文書・制約をカード化し、kj-atlas文書として管理する
  2. 最初の題材: 現在の未解決設計課題とその相互関係（non-canvas-ui-flow-design.html §9の表を出発点とする）
  3. W型累積KJ法（R1〜R6）をプロジェクト改善に適用する
  4. ドッグフーディングで発見された kj-atlas 自体の改善点を issue 化する
- 実施しないこと:
  1. 既存のissue管理（01_Plans/issues/）の置き換え（補完であり、移行ではない）
  2. kj-atlas文書のGit管理自動化（現段階では手動export/import）

## W型ラウンド計画

| ラウンド | 題材 | 目的 |
|---------|------|------|
| R1: 問題提起 | 現行の設計プロセスの摩擦 | ドッグフード記録・issue・ADRから素材をカード化 |
| R2: 現状把握 | 設計判断の実態 | 三要素牽制の未適用箇所を特定 |
| R3: 本質追求 | 不整合の根本原因 | 方法論の欠如・文書間の不整合・レビュー不足の構造化 |
| R4: 構想 | 三要素牽制設計法の定着策 | プロセス・ツール・文書テンプレートの具体案 |
| R5: 具体策 | 各フェーズの実施手順 | 本計画の各項目の具体化 |
| R6: 手順 | 実行順序と依存関係 | 優先順位付けと実施計画 |

## 受入条件

- [ ] 最初の kj-atlas 文書（プロジェクト管理用）が作成され、R1のカード化が完了している
- [ ] ドッグフーディング中に発見された kj-atlas 自体の改善点が1件以上 issue 化されている
- [ ] 文書は `01_Plans/dogfood/` に配置し、export/import手順が文書化されている

## 補足

- 本issueはプロセス改善であり、コード変更を直接要求しない
- ドッグフーディングの副次的効果として、kj-atlasのUI/UX改善点が発見されることを期待する
- ADR-0042は「本番相当の負荷をかけるドッグフーディング」を要求しているが、本issueはその前段階としての軽量な適用である
