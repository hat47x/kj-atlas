# Issue: DX-CLEANUP-02 access_control_metadata.tsが完全に未参照

- Type: Process
- Status: Done
- Source Issue: N/A
- Priority: P3
- Owner: Maintainer
- Scope: `03_Implement/frontend/src/domain/policy/access_control_metadata.ts`
- Related ADR/Spec: N/A
- Expected verification level: `unit`

## 課題

- 現在の問題: `03_Implement/frontend/src/domain/policy/access_control_metadata.ts`は、`normalizeAccessControlMetadata`・`validateAccessControlMetadata`・型`AccessControlMetadata`をexportしているが、リポジトリ全体をgrepしてもこのファイル自身以外に一切の参照（import）が無い。テストファイルからの参照も無い。
- 利用者または開発への影響: 実害はない（未参照のため実行パスに影響しない）が、認可/ポリシー関連の機能として意図的に作られたまま配線されずに残ったスキャフォールディングである可能性が高い。
- 判断結果: 導入コミット`a3e5405b`以降、一度もimport・テスト・契約参照が追加されていない。現行の`ADR-0059`とAPI正本は、SaaS profileでclient由来のrole/group/policyRefを認可根拠にせず、server-owned metadataとtrusted resolverを使うことを要求する。raw policyRefを正規化してfrontendへ保持させる本モジュールは将来境界としても採用できないため、旧スキャフォールディングと判断した。

## 対応方針

- 実施したこと: 未参照かつ現行の信頼境界と一致しない`access_control_metadata.ts`を削除した。
- 実施しないこと: backendの`AccessControlAdapter`、server-owned access metadata、tenant resolver、認可判定の変更。

## 受入条件

- [x] このモジュールを旧スキャフォールディングと確定し、削除する。
- [x] `02_Architecture/schemas.md`、`api.md`、`02_Architecture/design/architecture.html`に本モジュールへの参照が無く、現行SaaS信頼境界と逆向きであることを確認する。

## 検証計画

- 実行する確認: 削除する場合、`npm run typecheck`および`npm run test`（frontend）。
- 期待結果: 既存のビルド・テストに影響がないことを確認する。

## Validation

- `node node_modules/vitest/vitest.mjs run`
- `node node_modules/typescript/bin/tsc --noEmit`
- `python 01_Plans/docs_check.py --root .`

## 補足

- 発見経緯: 第8ラウンドの棚卸し（未使用export観点）で発見。ファイル単位で完全に孤立しているケースは、単一関数の未使用exportより見落としリスクが高いため、削除を実行せず起票のみとした。
