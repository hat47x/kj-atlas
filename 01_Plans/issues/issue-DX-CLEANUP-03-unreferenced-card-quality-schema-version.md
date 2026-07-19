# Issue: DX-CLEANUP-03 CARD_QUALITY_SCHEMA_VERSIONが未参照

> 個人OSS・プレリリース段階では `ADR-0039` を適用し、実行に必要な情報だけを記載する。

- Type: Process
- Status: Draft
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P3
- Owner: Maintainer
- Scope: `03_Implement/frontend/src/domain/card_quality.ts`
- Related ADR/Spec: N/A
- Expected verification level: `unit`

## 課題

- 現在の問題: `03_Implement/frontend/src/domain/card_quality.ts:3`の`CARD_QUALITY_SCHEMA_VERSION`定数は、リポジトリ全体で定義箇所以外に参照が無い。同じファイル内の`CARD_QUALITY_FIXTURE_KINDS`は使用されている。
- 利用者または開発への影響: 実害はない。ただし「スキーマバージョン」という命名は、将来のマイグレーション/互換性チェックのために予約された意図的なマーカーである可能性があり、単純な削除対象と断定できない。

## 対応方針

- 実施すること: この定数が将来のスキーマバージョンチェックのために意図的に予約されたものか、単なる未使用の残骸かをMaintainerが判断する。
- 実施しないこと: この定数の削除。命名パターン（スキーマバージョン）が意図的な予約枠を示唆するため、削除是非の判断を待つ。

## 受入条件

- [ ] この定数の位置づけ（維持/削除）が決定される。

## 検証計画

- 実行する確認: 削除する場合、`npm run typecheck`（frontend）。
- 期待結果: 既存のビルドに影響がないことを確認する。

## 補足

- 発見経緯: 第8ラウンドの棚卸し（未使用export観点）で発見。
