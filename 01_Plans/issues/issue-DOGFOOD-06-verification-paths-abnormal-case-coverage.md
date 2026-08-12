# Issue: DOGFOOD-06 検証経路の追加時は異常系をCIで固定する（結果分析からのプロセス改善）

- Type: Process
- Status: Done
- Source Issue: `01_Plans/dogfood/dogfood-analysis-synthesis-2026-08-12.md`（DOGFOOD-02〜05の横断分析）
- Priority: P2
- Owner: Maintainer
- Scope: `03_Implement/backend/scripts/verify_api.sh`, `03_Implement/mcp/scripts/verify_mcp.ts`, 新規検証経路の追加規約
- Related ADR/Spec: `01_Plans/dogfood/dogfood-analysis-synthesis-2026-08-12.md` §4, `issue-DOGFOOD-03`, `issue-DOGFOOD-04`, `01_Plans/dogfood/README.md`（W型サイクル）
- Expected verification level: `docs-check`

## 課題

2026-08-12 に追加された検証経路（`verify_api.sh`, `verify_mcp.ts`）が、いずれも**異常系のエッジを未検証**のまま
追加されたことが、DOGFOOD-03（isError を JSON.parse で破壊）と DOGFOOD-04（503 を reachable と誤判定）の
両方を生んだ。

横断分析（result-analysis-synthesis）の結論:
- 検証経路は「経路が存在し、正常系で動く」ことだけを見る。
- **経路が「実際に使える状態か」は見ない**（503・not_found・契約外version・未レビュー状態が対象外）。
- これは「検出対象の設定が正常系偏重」という、既存の「検出しても修正の主体がない」とは別の構造的問題。

## 期待される改善（新規追加ルール）

1. **新規検証経路を追加するときは、成功系だけでなく異常系もassertする**。
   最低限: not_found / 503相当 / 契約外version / 対象なし の各状態を検証入力として固定する。
2. **検証スクリプト自身に unit テストを付ける**（スクリプトの出力を assert するのではなく、スクリプトのロジックを直接）。
   DOGFOOD-03/04 は「スクリプト自身のテスト」があれば CI で早期検出できた。
3. **検証対象データを「理想状態」だけにしない**。旧version・未レビューのみ・空DB の状態も検証入力に含める。

## 受入条件

- [x] 既存 `verify_api.sh` / `verify_mcp.ts` が異常系（503 / not_found / 契約外version）を正しく区別して報告する。（verify_mcp.ts: DOGFOOD-03/06・verify_api.sh: DOGFOOD-04）
- [x] 検証スクリプトの異常系を assert する unit テストが存在する。（`03_Implement/mcp/src/mcp_verify_result.test.ts` 6件）
- [x] このルールが `01_Plans/dogfood/README.md` または検証経路の追加規約として記録される。（`01_Plans/dogfood/README.md`「検証経路の追加規約」節）

## 検証計画

- 実行コマンド:
  - `verify_api.sh` を503環境（local-devの`/session/context`）で実行し、503が pass 扱いされないこと。
  - `verify_mcp.ts` を存在しない docId で実行し、クラッシュせず not_found を報告すること。
  - 新規検証経路の追加時に本ルールが参照できること。

## 補足

- 本 issue は「検証インフラの品質」を対象とする。プロダクトの安全境界変更は含まない。
- 直近対応可能な範囲（DOGFOOD-03/04 のスクリプト修正＋unitテスト）と、将来の追加経路への規約化に分かれる。

## 対応記録（2026-08-12）

- **unit テスト**: `verify_mcp.ts` の isError/not_found 解釈を `src/mcp_verify_result.ts` へ抽出し、`mcp_verify_result.test.ts`（6件）で正常系・not_found・error・不正JSON・反スコアリング語彙なしを固定。
- **検証スクリプトの更新**: `verify_mcp.mjs` → `verify_mcp.ts` へリネームし、tsx 実行（`npm run verify`）へ統一（Node 20 の素 `node` では .ts import / `as` 構文が起動不能のため）。
- **規約化**: `01_Plans/dogfood/README.md` に「検証経路の追加規約」節を追加（異常系assert・スクリプト自身のunitテスト・実状態データの3点）。
- **検証**: MCP vitest 55 tests pass・typecheck OK・`npm run verify -- nonexistent_doc` 実走行で isError 経路（error分類）終了を確認。
