# Issue: DOGFOOD-06 検証経路の追加時は異常系をCIで固定する（結果分析からのプロセス改善）

- Type: Process
- Status: Draft
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

- [ ] 既存 `verify_api.sh` / `verify_mcp.ts` が異常系（503 / not_found / 契約外version）を正しく区別して報告する。
- [ ] 検証スクリプトの異常系を assert する unit テストが存在する。
- [ ] このルールが `01_Plans/dogfood/README.md` または検証経路の追加規約として記録される。

## 検証計画

- 実行コマンド:
  - `verify_api.sh` を503環境（local-devの`/session/context`）で実行し、503が pass 扱いされないこと。
  - `verify_mcp.ts` を存在しない docId で実行し、クラッシュせず not_found を報告すること。
  - 新規検証経路の追加時に本ルールが参照できること。

## 補足

- 本 issue は「検証インフラの品質」を対象とする。プロダクトの安全境界変更は含まない。
- 直近対応可能な範囲（DOGFOOD-03/04 のスクリプト修正＋unitテスト）と、将来の追加経路への規約化に分かれる。
