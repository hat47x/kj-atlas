# Issue: QA-MONKEY-20 モンキーハーネスが常設menuitemと正常な操作遮断を不具合として報告する

- Type: Test / Quality
- Status: Done
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A（2026-08-16のアドホック・モンキーテストで発見）
- Priority: P2
- Owner: Maintainer
- Scope: `03_Implement/frontend/scripts/monkey_adversarial_probes.mjs`, `03_Implement/frontend/scripts/monkey_ui_sweep.mjs`
- Related Backlog: `QA-MONKEY-20`
- Related ADR/Spec: `01_Plans/issues/issue-MVP-EXIT-01-productization-readiness.md`, `03_Implement/frontend/docs/mvp_exit_monkey_test_log_2026-07-29.md`
- Expected verification level: `e2e`

## 課題

2026-08-16の実行で、製品挙動が正常でも次の誤検知が再現した。

1. `monkey_adversarial_probes.mjs` A3は、カードのコンテキストメニューをEscapeで閉じた後にページ全体の`menuitem`件数が0になることを期待する。しかし常設メニューバーが6件の`menuitem`を持つため、実際にはコンテキストメニューが閉じていても`SUSPECT`となる。2026-07-29の調査ログには既に誤検知と記録されていたが、ハーネスへ反映されていなかった。
2. `monkey_ui_sweep.mjs`は無効なUndo/Redo、モーダルやメニューの背後にあるカード、操作不能なチェックボックスも無作為クリック対象にする。Playwrightが正しくクリックを遮断した場合も`action-blocked` findingとなり、製品欠陥とテスト入力不備を区別できない。

この状態では、実際の例外、SafeMode表示消失、横方向overflow、accessible name欠落などの高価値findingがノイズへ埋もれる。

## 対応方針

- A3は操作前のページ全体`menuitem`件数をbaselineにし、右クリック後に増加し、Escape後にbaselineへ戻ることを検証する。
- ランダムスイープは`enabled`な要素だけを候補にし、Playwrightのtrial clickでその時点に操作可能な要素だけを実操作する。モーダル・メニュー等による正常な遮断はfindingにしない。
- page error、console error、SafeMode、ARIA、overflow、NaN等の不変条件検査は緩和しない。

三要素牽制: 業務上はQA結果の判別可能性を回復する。データ境界・保存形式は変更しない。機能上はテスト入力生成だけを修正し、製品UI・SafeMode・共有状態遷移は変更しない。横断的な製品設計判断を含まないためADRは不要。

## 受入条件

- [x] A3がコンテキストメニューの増減だけを判定し、常設メニューバーを誤検知しない。
- [x] ランダムスイープが無効要素やtop layer背後の要素を無理に操作しない。
- [x] 390pxと1440pxのseed実行で、正常な操作遮断だけを理由とするfindingが0件になる。
- [x] 例外、SafeMode、ARIA、overflow、NaNの不変条件検査が維持される。

## 検証計画

- `monkey_adversarial_probes.mjs` 全項目を再実行し、9/9 `ok` を確認する。
- `monkey_ui_sweep.mjs` を390pxと1440pxの固定seedで各200操作以上実行する。
- `python 01_Plans/issues/validate_active_issue_memos.py` と `python 01_Plans/docs_check.py` を実行する。

## 対応結果（2026-08-16）

- A3をページ全体の絶対件数ではなくbaseline差分で判定するよう変更した。実測は常設6件、コンテキストメニュー表示中10件、Escape後6件で、製品の閉じる挙動と常設メニューバーを区別できた。
- ランダムスイープは`enabled`候補とtrial clickを使い、その時点で操作不能な要素をskip traceとして扱う。trial後に実クリックが失敗した場合は従来どおり外側の`action-blocked`検出へ到達するため、操作可能と判定された後の異常は隠さない。
- 390px / seed 303 / 指定220反復: 実行action 193、finding 0。
- 1440px / seed 707 / 指定220反復: 実行action 197、finding 0。
- 明示プローブ: 9件すべて`ok`、`suspects: 0`。
- 製品コード、文書データ、SafeMode・共有・import境界は変更していない。
