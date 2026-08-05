# Issue: DX-CLEANUP-03 CARD_QUALITY_SCHEMA_VERSIONが未参照

> 個人OSS・プレリリース段階では `ADR-0039` を適用し、実行に必要な情報だけを記載する。

- Type: Process
- Status: Done
- Source Issue: N/A
- Priority: P3
- Owner: Maintainer
- Scope: `03_Implement/frontend/src/domain/card_quality.ts`
- Related ADR/Spec: N/A
- Expected verification level: `unit`

## 課題

- 現在の問題: `03_Implement/frontend/src/domain/card_quality.ts:3`の`CARD_QUALITY_SCHEMA_VERSION`定数は、リポジトリ全体で定義箇所以外に参照が無い。同じファイル内の`CARD_QUALITY_FIXTURE_KINDS`は使用されている。
- 利用者または開発への影響: 実害はない。ただし「スキーマバージョン」という命名は、将来のマイグレーション/互換性チェックのために予約された意図的なマーカーである可能性があったため、導入履歴と現在の契約を確認した。
- 判断結果: 導入コミット`3194dcdb`はカード品質支援を非永続の状態機械として追加し、コミット説明でも「No schema changes」と明記している。現行要件も品質上の指摘を導出提案とし、永続化には別issue/ADRを要求している。定数は型、fixture、import/export、validationのいずれにも使われず、予約済み契約ではない残骸と判断した。

## 対応方針

- 実施したこと: 未参照の`CARD_QUALITY_SCHEMA_VERSION`を削除した。
- 実施しないこと: カード品質支援の状態、fixture、UI、永続契約の変更。将来永続化する場合は正本要件どおり別issue/ADRで契約を定義する。

## 受入条件

- [x] この定数の位置づけを「永続スキーマを伴わない未使用残骸」と確定し、削除する。

## 検証計画

- 実行する確認: 削除する場合、`npm run typecheck`（frontend）。
- 期待結果: 既存のビルドに影響がないことを確認する。

## Validation

- `node node_modules/vitest/vitest.mjs run src/domain/card_quality.test.ts`（17 tests passed）
- `node node_modules/typescript/bin/tsc --noEmit`
- `python 01_Plans/docs_check.py --root .`

## 補足

- 発見経緯: 第8ラウンドの棚卸し（未使用export観点）で発見。
