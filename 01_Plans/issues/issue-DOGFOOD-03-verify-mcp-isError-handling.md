# Issue: DOGFOOD-03 verify_mcp.ts が not_found/error 応答を JSON.parse で破壊する

- Type: Bug
- Status: Done
- Source Issue: DOGFOOD-01（ドッグフーディング検証経路の拡張で発見）
- Priority: P2
- Owner: Maintainer
- Scope: `03_Implement/mcp/scripts/verify_mcp.ts`, `03_Implement/mcp/src/context_projection_tool.ts`
- Related ADR/Spec: `03_Implement/mcp/src/context_projection_tool.ts`（isError 契約）, `03_Implement/mcp/src/audit_log.ts`
- Expected verification level: `unit`

## 課題

MCP クライアント検証経路 `verify_mcp.ts` を実走行したところ、対象文書が存在しない（not_found）ときに
**"Unexpected token 'F', "Failed to "... is not valid JSON"** でクラッシュした。

### 三要素分析

- **機能設計**: MCP サーバー（`context_projection_tool.ts`）は not_found / error 時に `{ content: [{type:"text", text:<message>}], isError: true }` を返す正しい契約を持つ。一方 `verify_mcp.ts` は `result.isError` を確認せず、`JSON.parse(result.content[0].text)` を無条件実行するため、エラーメッセージ文字列を JSON として解析しようとして例外を投げる。**クライアント（検証スクリプト）がサーバーの isError 契約に従っていない**。
- **データ設計**: 成功時は `projection` の JSON、失敗時は平文メッセージという異なるデータ形が同じ `text` チャネルに流れる。検証スクリプトは成功形のみを仮定しており、失敗形の取り扱い（`outcome: "not_found" | "error"` の表示）が未実装。
- **業務設計**: 検証経路の目的は「MCP 経路が利用可能か」の確認であり、not_found は正常な結果の一種（文書が無いだけ）として扱えるべき。現状は not_found 自体が「検証失敗」に見えるため、MCP 検証の誤検知になる。

## 期待される改善

- `verify_mcp.ts` が `result.isError` を最初に確認し、エラー時は `outcome`（not_found / error）とメッセージを表示して、明確な成否判定を出す。
- not_found を「検証の成功（経路は稼働、対象文書が無いだけ）」として扱うか、意図的な期待失敗として文書化するかを明確化する。
- 実環境で文書が存在しない場合でもクラッシュせず、経路自体が生きていることを検証できるようにする。

## 受入条件

- [ ] 存在しない `docId` に対して `verify_mcp.ts` がクラッシュせず、`isError` 応答を表示して終了する。
- [ ] 成功時（文書存在・safeMode ON）の既存検証（ツール1つ・反スコアリング語彙なし）が引き続き通る。
- [ ] MCP 経路のヘルス確認が not_found と error を区別して報告する。

## 検証計画

- 実行コマンド:
  - `cd 03_Implement/mcp && KJ_ATLAS_MCP_API_BASE_URL=http://127.0.0.1:8000 npm run verify -- nonexistent_doc reviewed-only`
  - 成功系: `cd 03_Implement/mcp && ... npm run verify -- doc_phase1_canvas reviewed-only`（シード済み環境）
  - 注: `npm run verify` は `tsx scripts/verify_mcp.ts` を実行する。verify_mcp.ts は .ts モジュールを import し TS 構文（`as`）を含むため、Node 20 の素の `node` では起動しない（ERR_UNKNOWN_FILE_EXTENSION）。
- 期待結果: クラッシュなし。not_found の場合は経路稼働と対象不在を分けて報告。

## 補足

- MCP サーバー側の契約（isError）は正しく、サーバーの変更は不要。検証スクリプト側の仮定（常に JSON）が誤り。
- `verify_mcp.ts` は 2026-08-12 に追加されたばかりの経路であり、not_found 系のエッジが CI 未カバーだった。

## 対応記録（2026-08-12）

- `verify_mcp.ts` に `result.isError` の事前確認を追加。エラー時は outcome（not_found/error）とメッセージを表示して exit 0 とし、
  「MCP 経路は生きているが対象文書が取得できない」ことを報告する（クラッシュしない）。
- 検証: 実走行で not_found（`nonexistent_doc_xyz` → `outcome: "not_found"`、exit 0）と成功（`dogfood_orga_batch_20260812` → PASSED）の両方を通ることを確認。
- 回帰: `npx vitest run`（MCP）で 49 tests passed。
- DOGFOOD-06 の受入条件のうち「異常系を区別して報告する」を1件充足。
