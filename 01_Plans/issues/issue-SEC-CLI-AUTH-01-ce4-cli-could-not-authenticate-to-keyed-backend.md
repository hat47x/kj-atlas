# Issue: SEC-CLI-AUTH-01 CE4 CLIがキー認証済みbackendへ接続できない

- Type: Security / Operability
- Status: Done
- Source Issue: 管理UI・CLI・API・MCP協調モンキーテスト（2026-08-16）
- Priority: P1
- Owner: Maintainer
- Scope: `03_Implement/backend/src/kj_atlas_api/cli.py`, CLI CE4 E2E, operator documentation
- Related Issue: `OPS-ADMIN-UX-01`, `CE4-api-cli-audit-integration`
- Related ADR/Spec: `ADR-0072`, `02_Architecture/api.md` §2.9
- Expected verification level: `e2e`

## 課題

MCP clientは`KJ_ATLAS_API_KEY`を`X-API-Key`としてbackendへ送る一方、正式な`kj_atlas_api.cli`はactor/trace headerしか送らず、既存E2EもAPI keyを無効にしたlocal-devだけを対象としていた。このため、キー認証を有効にしたenterprise相当のbackendでは`context-query`、`context-bundle`、`proposal-diff`、`apply --dry-run`、`ce4 resolve-bundle`がすべて401となり、GUI・MCP・CLIの監査経路が協調しなかった。

## 対応

- CLIが`KJ_ATLAS_API_KEY`を環境変数から読み、全business-plane requestへ`X-API-Key`として送信する。
- 秘密値をshell履歴・process一覧へ露出する`--api-key`引数は追加しない。
- unsetまたは空白値は送信せず、従来のopen local-dev互換を維持する。
- 自己完結CLI E2Eをキー有効backendへ変更し、CE4全操作と監査sink到達を確認する。

## 受入条件

- [x] キー有効backendでCE4 CLI全操作が成功する。
- [x] CLIとMCPが同じbusiness-plane key境界を通る。
- [x] キーはcommand line引数・標準出力・監査eventへ出ない。
- [x] キー未設定のlocal-dev互換を維持する。
