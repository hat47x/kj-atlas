# Issue: DX-CLEANUP-02 access_control_metadata.tsが完全に未参照

> 個人OSS・プレリリース段階では `ADR-0039` を適用し、実行に必要な情報だけを記載する。

- Type: Process
- Status: Draft
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P3
- Owner: Maintainer
- Scope: `03_Implement/frontend/src/domain/policy/access_control_metadata.ts`
- Related ADR/Spec: N/A
- Expected verification level: `unit`

## 課題

- 現在の問題: `03_Implement/frontend/src/domain/policy/access_control_metadata.ts`は、`normalizeAccessControlMetadata`・`validateAccessControlMetadata`・型`AccessControlMetadata`をexportしているが、リポジトリ全体をgrepしてもこのファイル自身以外に一切の参照（import）が無い。テストファイルからの参照も無い。
- 利用者または開発への影響: 実害はない（未参照のため実行パスに影響しない）が、認可/ポリシー関連の機能として意図的に作られたまま配線されずに残ったスキャフォールディングである可能性が高い。

## 対応方針

- 実施すること: このファイルが（a）将来の機能のために意図的に残されたものか、（b）廃止された旧設計の残骸かをMaintainerが確認し、(b)であれば削除する。
- 実施しないこと: このファイルの削除そのもの。ファイル単位の削除は影響範囲の見落としリスクがあるため、機械的には実施しない。

## 受入条件

- [ ] このモジュールの位置づけ（維持/削除）が決定される。
- [ ] 削除する場合、`02_Architecture/schemas.md`等の正本文書に本モジュールへの言及が無いことを確認する。

## 検証計画

- 実行する確認: 削除する場合、`npm run typecheck`および`npm run test`（frontend）。
- 期待結果: 既存のビルド・テストに影響がないことを確認する。

## 補足

- 発見経緯: 第8ラウンドの棚卸し（未使用export観点）で発見。ファイル単位で完全に孤立しているケースは、単一関数の未使用exportより見落としリスクが高いため、削除を実行せず起票のみとした。
