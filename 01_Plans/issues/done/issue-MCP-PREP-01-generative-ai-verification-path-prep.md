# Issue: MCP-PREP-01 生成AIがMCPで検証する経路の準備（構造状態の投影とrunbook）

- Type: Process / Operations
- Status: Done
- Source Issue: ドッグフーディングループ（「生成AIがMCPを用いて検証する経路の準備」）
- Priority: P2
- Owner: Maintainer
- Scope: `03_Implement/mcp/scripts/verify_mcp.ts`, `README.md`, `03_Implement/frontend/src/export/context_bundle_projection.ts`
- Related ADR/Spec: `01_Plans/adr/ADR-0054-external-connection-service-scope.md`, `01_Plans/dogfood/README.md`（DOGFOOD-03/06/08）
- Expected verification level: `docs-check`

## 課題

生成AIが MCP でアプリを検証する経路の「準備」として、検証シナリオのrunbookと、新規の構造状態（voids・ナラティブA/B方向/件数）の投影が不足していた。

- `context_projection.v1` が `voids`（KJ-VOIDS-01・イテレーション6）と `narrativeChecks`（KJ-AB-CROSS-CHECK-01・イテレーション4）を含まないため、生成AIは MCP 経由で最新の構造状態を検証できなかった。
- MCP README に「何を・どう検証するか」のシナリオrunbookが無く、接続例のみだった。

## 対応方針

- 実施すること（D-a）:
  1. **投影の拡張**: `context-projection.v1` に `voids`（kind/refs/resolved・title/detail は SafeMode 上 redact のため含めない）と `narrativeChecks`（direction/counts・本文 message は含めない）を追加。MCP ツールは全投影を返すため自動反映。
  2. **verify_mcp.ts の拡張**: 検証出力に voids/narrative 状態を表示。
  3. **runbook**: MCP README に「Generative-AI verification runbook」節を追加（SafeMode fail-closed・holdState・反スコアリング・not_found・void状態・ナラティブA/B・bundle決定的）。
- 実施しないこと:
  1. 投影への本文（カード未レビュー内容・issue message）の露出 — SafeMode 境界は維持。
  2. 新規 MCP ツールの追加（`get_context_projection` のみ維持。DOGFOOD-05 の適用範囲を変えない）。

## 受入条件

- [x] AC-1: 投影が `voids` と `narrativeChecks`（構造値のみ）を含む。
- [x] AC-2: SafeMode が title/detail・issue message を露出しない（構造値のみ）。
- [x] AC-3: `verify_mcp.ts` が voids/narrative 状態を表示する。
- [x] AC-4: README に検証runbookがあり、`npm run verify` がそのシナリオを実行する。

## 検証

- `cd 03_Implement/mcp && npm run typecheck && npm test`
- `cd 03_Implement/frontend && npm run test -- src/export/context_bundle_projection.test.ts`
- `bash 03_Implement/backend/scripts/verify_api.sh`（/readyz・/version を含む5チェック）

## 対応記録（2026-08-14）

- `context_bundle_projection.ts`: `ProjectedVoid` / `ProjectedNarrativeCheck` を追加し、`ContextProjectionV1` に `voids` / `narrativeChecks` を追加（常に配列、空なら空配列）。bundleHash にも含める。
- `verify_mcp.ts`: 検証出力に `voids` / `narrative checks` の状態表示を追加。
- MCP README: 「Generative-AI verification runbook」節を追加（7シナリオ＋isError の解釈規則）。
- `verify_api.sh`: `/readyz`（200/503 を区別）・`/version`（200）を追加し5チェックへ。
- テスト: 投影テスト2件追加（voids/narrative・空配列）。frontend 1448 tests・MCP 56 tests・verify_api.sh 5 pass。
