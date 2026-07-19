# Issue: UI-QUALITY-A11Y-05 読み順バッジの並び替えにキーボード操作が無い

> 個人OSS・プレリリース段階では `ADR-0039` を適用し、実行に必要な情報だけを記載する。

- Type: Feature
- Status: Draft
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P3
- Owner: Maintainer
- Scope: `03_Implement/frontend/src/canvas/ReadingOrderLayer.tsx`
- Related ADR/Spec: `01_Plans/adr/ADR-0055-work-mode-navigation-semantics.md`, `issue-UI-QUALITY-A11Y-03-structural-aria-findings.md`
- Expected verification level: `unit`

## 課題

- 現在の問題: `ReadingOrderLayer.tsx`の読み順バッジ（`<button>`要素、L235-281）は、削除（Alt+Click）は`Delete`/`Backspace`キーで操作可能にした（本ラウンドで対応済み）が、並び替え自体は`onPointerDown`/`onPointerMove`/`onPointerUp`によるドラッグ操作のみ（L~150-227）で行われており、キーボードだけでは順序を変更できない。`ReadingOrderLayer`の唯一の利用元は`CanvasShell.tsx`で、代替の一覧編集パネルは存在しない（grep確認済み）。
- 利用者または開発への影響: キーボードのみで操作するユーザーは読み順を編集できない。バッジ自体はネイティブ`<button>`でフォーカス可能だが、実行できるアクションが「フォーカス」と「（対応済みの）削除」のみで、並び替えという主要な編集操作が欠落している。

## 対応方針

- 実施すること: 「上へ移動/下へ移動」のような離散的なキーボード操作（例: 矢印キー+モディファイア、または明示的なボタン）を設計し、`onRemoveEntry`と同様に既存の並び替えロジック（`onReorderEntry`相当のコールバック）へ配線する。
- 実施しないこと: ドラッグ操作自体の変更・削除。ドラッグ操作はマウス操作として現状のまま維持する。
- 判断が必要な理由: 離散的な移動インタラクション（何を1ステップの移動単位とするか、複数要素の並び替えをどう1ステップずつのキー操作に落とし込むか、操作結果をどうaria-liveなどでアナウンスするか）はUXデザイン判断であり、機械的に追加できるものではない。

## 受入条件

- [ ] キーボードのみで読み順を並び替えられる操作方式が決定される。
- [ ] 実装後、既存のドラッグ操作に回帰がないことを確認する。

## 検証計画

- 実行する確認: 実装後、`ReadingOrderLayer`関連のunit testおよび手動のキーボード操作確認。
- 期待結果: ドラッグ操作とキーボード操作の両方で同じ並び替え結果になる。

## 補足

- 発見経緯: 第8ラウンドの棚卸し（アクセシビリティ観点）で発見。同時に見つかった「Alt+Click削除にキーボード操作が無い」問題は`Delete`/`Backspace`キー対応として本ラウンドで直接修正済み（既存の`onRemoveEntry`コールバックを再利用するだけの機械的な変更のため）。
