# diagnostics worker protocol

この文書は Frontend diagnostics worker の I/O 契約を定義する。
対象実装:
- `03_Implement/frontend/src/worker/diagnostics_protocol.ts`
- `03_Implement/frontend/src/worker/diagnostics_client.ts`
- `03_Implement/frontend/src/worker/diagnostics.worker.ts`

## diagnosticsData schemaVersion

- Current: `1`
- 対応方針: クライアントは `schemaVersion === 1` のみ受理する。
- pre-release 方針として、旧バージョン互換（schema欠損・旧versionマイグレーション）は提供しない。

## Worker message envelope

### Request
- `diagnostics.request`
- `diagnostics.cancel`

### Response
- `diagnostics.progress`
- `diagnostics.result`
- `diagnostics.error`
- `diagnostics.cancelled`

## Validation / fallback policy

`DiagnosticsWorkerClient` は次を検知した場合、worker結果を破棄し main-thread fallback 計算へ遷移する。

- invalid / unsupported `schemaVersion`
- malformed / array-shaped payload
- malformed result envelope（`result` がobjectでない、`diagnosticsMd` がstringでない）
- malformed progress（stage不正、percent不正）
- unknown message type
- malformed `diagnostics.error`（messageがstringでない）
- required fields 欠落（`recommendations`, `diagnosticsMd`, 各report object）

### requestId isolation

- 別requestIdのメッセージは無視する。
- 別requestIdで malformed なメッセージが来ても、対象requestの処理は継続する。

## Compatibility guarantee

- N（current）: 完全サポート
- N 以外: 互換なし（fallbackへ遷移し処理継続）
