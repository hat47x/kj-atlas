# Issue: UI-QUALITY-A11Y-07 StartPanelのfocus復帰導線が未定義

> 個人OSS・プレリリース段階では `ADR-0039` を適用し、実行に必要な情報だけを記載する。

- Type: Feature
- Status: Draft
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P3
- Owner: Maintainer
- Scope: `03_Implement/frontend/src/ui/StartPanel.tsx`, `03_Implement/frontend/src/App.tsx`
- Related ADR/Spec: `02_Architecture/design/ui_design_handoff.md`
- Expected verification level: `unit`

## 課題

- 現在の問題: `StartPanel.tsx`のEscape閉鎖は本ラウンドで対応したが、`App.tsx:onClose={() => setIsStartPanelVisible(false)}`は単純な状態更新のみで、`handleCloseCanvasLegend`/`closeCommandPalette`/`closeShortcutCheatsheet`（ADR-0030契約に基づき`data-focus-return-id`でトリガへfocusを戻す）のようなfocus復帰処理を持たない。
- 判断が必要な理由: `setIsStartPanelVisible(true)`は現在、初期`useState(true)`以外のどこからも呼ばれていない（grepで確認済み）。つまり現状StartPanelを閉じた後に再度開く導線が存在しないため、「どこへfocusを戻すべきか」という設計判断自体が成立しない。StartPanelを再度開く導線（例: メニューやツールバーからの再オープン）を新設するかどうかは製品判断であり、それが決まって初めてfocus復帰先が定まる。
- 利用者または開発への影響: 現状は実害なし（再オープン導線が無いため、閉鎖後にfocusを喪失するケース自体が発生しない）。将来的にStartPanelの再オープン導線を追加する際に、この設計を後回しにしないための記録。

## 対応方針

- 実施すること: StartPanelの再オープン導線を新設するか否かをMaintainerが決定する。新設する場合、`data-focus-return-id`パターンでの復帰実装を併せて設計する。
- 実施しないこと: focus復帰処理の実装そのもの。再オープン導線が存在しない現状では、復帰先を機械的に決められない。

## 受入条件

- [ ] StartPanelの再オープン導線の要否が決定される。
- [ ] 新設する場合、focus復帰の実装方針が決定される。

## 検証計画

- 実行する確認: 実装する場合、`npm run test`（frontend、StartPanel関連）。
- 期待結果: 再オープン導線とfocus復帰が既存の`data-focus-return-id`パターンと整合する。

## 補足

- 発見経緯: 第15ラウンドの棚卸し（ダイアログのfocus-trap/Escape観点）で発見。同じ観点で見つかったStartPanelのEscape閉鎖欠如は、既存の兄弟ダイアログ（`RecentDocumentsDialog.tsx`等）と同じ実装パターンをそのまま複製するだけの機械的な修正だったため、本ラウンドで直接対応済み。
