# Issue Draft: DX-CI-MCP-01 MCPテストスイートがCI未実行・ローカルも依存未インストール

- Type: Process / Tooling
- Status: Done
- Source Issue: N/A
- Priority: P3
- Owner: Maintainer
- Scope: `03_Implement/mcp/`, `.github/workflows/ci.yml`
- Related ADR/Spec: `01_Plans/issues/issue-EXT-CONN-01-readonly-mcp-server.md`
- Expected verification level: `docs-check`

## 課題

`03_Implement/mcp/` のテストスイート（6ファイル）がCIで実行されず、ローカルでも依存未インストールのため実行できない。

- `03_Implement/mcp/package.json` は `test: vitest run` と `vitest: 4.1.10`（devDependency）を宣言し、`src/audit_log.test.ts` 等6ファイルが存在する。
- `.github/workflows/ci.yml` には **MCPジョブが存在しない**（frontend / backend の2ジョブのみ）。`change-scope` も `frontend` / `backend` の2出力のみ。
- ローカルの `03_Implement/mcp/node_modules/` は **空**（0依存、expressもvitestも未インストール）。`npm test` は `ERR_MODULE_NOT_FOUND: Cannot find package 'vitest'` で失敗する。

つまりMCPのテストは「書かれているが、CIでもローカルでも実行されない」状態である。MCPは読み取り専用サーバー（`EXT-CONN-01`）として稼働が予定されており、`http_server.ts` / `oauth_verifier.ts` / `context_projection_tool.ts` / `document_client.ts` の契約を検証するテストが回らないのは、外部連携の回帰を検知できないリスクになる。

## 対応方針（案）

- (a) `ci.yml` へ MCPジョブを追加（`npm ci` + `npm test` + `npm run typecheck`）。`change-scope` に `mcp` 出力を追加し、`03_Implement/mcp/**` の変更時にのみ実行。
- (b) ローカルで `cd 03_Implement/mcp && npm install` を実行して依存を整える（環境メンテナンス）。
- (c) 少なくとも、MCPテストの実行コマンドと現状（未実行）を `03_Implement/mcp/README.md` か `CONTRIBUTING.md` に明記する。

## 受入条件

- [x] MCPテストがCIまたはローカルで実行可能になり、全テストが通る。→ `ci.yml` にMCPジョブ（`npm ci` + typecheck + test）を追加（2026-08-07）。ローカルで `npm install` 実行後、6ファイル/49テスト + typecheck pass。
- [x] 実行方法（コマンド）が文書化される。→ `03_Implement/mcp/package.json` の `test: vitest run` / `typecheck: tsc --noEmit` をCIジョブが直接利用。
- [x] `python 01_Plans/docs_check.py` が通る。→ pass（active_memos=65, tracked_markdown=488）。

## 検証計画

- `cd 03_Implement/mcp && npm test`
- `cd 03_Implement/mcp && npm run typecheck`
- `python 01_Plans/docs_check.py`
