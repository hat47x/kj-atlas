# Issue: MCP-DOGFOOD-12 MCP監査E2EがWSLのNode・一時領域差で起動不能になる

- Type: Test / Developer Experience
- Status: Done
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A（2026-08-16のMCPモンキーテストで発見）
- Priority: P2
- Owner: Maintainer
- Scope: `03_Implement/backend/scripts/verify_mcp_ce4_audit_e2e.py`, `01_Plans/agent_failure_log.md`
- Related Backlog: `MCP-DOGFOOD-12`
- Related ADR/Spec: `01_Plans/issues/done/issue-DOGFOOD-06-verification-paths-abnormal-case-coverage.md`
- Expected verification level: `e2e`

## 課題

MCP→CE-4監査E2EはMCP packageの`node_modules`だけを前提として記述されているが、実装はPATH上の`npm`を暗黙要求していた。またWSLがWindowsの`TEMP`を継承すると、tsxのIPC socketがdrvfs上に作られて`ENOTSUP`で停止した。MCPやbackendへ到達する前の環境差で生成AI連動検証が不能になる。

## 対応方針

- package-localの`tsx`を直接起動し、`npm`への不要な実行時依存を外す。
- 非WindowsではtsxのIPC一時領域を`/tmp`へ固定し、WSLのWindows TEMP継承を遮断する。
- MCP read→CE-4 `channel=mcp`→audit sinkの一気通貫を再実行する。

三要素牽制: 業務・データ・製品機能は変更しない。生成AI協働の監査検証経路だけを環境非依存にするためADR不要。

## 受入条件

- [x] PATHにnpmがなくてもpackage-local tsxから検証clientを起動できる。
- [x] WSLでWindows TEMP/TMPを継承してもIPC socket errorにならない。
- [x] MCP projectionが成功し、監査sinkへ`channel=mcp`が1件届く。
- [x] MCPのread-only・SafeMode・anti-scoring契約が回帰しない。

## 対応結果（2026-08-16）

- package-local tsx直接起動と非Windows`TMPDIR=/tmp`を実装した。
- MCP→CE-4監査E2E 8/8、MCP package 7 files / 61 tests、typecheckを通過した。

## 追加対応（2026-08-17）

PATH上のNode.js v12がpackage-local `tsx`のshebangから選択され、Node 20契約の構文を解釈できない再発を検出した。`KJ_ATLAS_NODE_BIN`で同一platformのruntimeを明示選択できるようにし、`.bin` shebangではなく選択済みNodeからtsxのJS entrypointを起動する。Node 20未満は構文エラーになる前に明示拒否し、stdio MCPとHTTP MCPを同じNode選択へ揃える。

子MCP serverも`npx`/`node`を再探索すると親だけruntimeを選んでも境界が破れるため、stdio verifierとHTTP harnessは`process.execPath`で親と同じruntimeを継承し、tsxのJS entrypointを直接起動する。

## 検証計画

- Node 20をPATHへ設定し、`verify_mcp_ce4_audit_e2e.py`をWindows TEMP継承状態で実行する。
- MCP typecheck/test、docs-check、active issue validatorを実行する。
