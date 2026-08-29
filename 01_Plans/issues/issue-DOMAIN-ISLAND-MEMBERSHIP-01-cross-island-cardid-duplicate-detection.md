# Issue: DOMAIN-ISLAND-MEMBERSHIP-01 カード→島の関数従属性（F-5）: 跨島マージで重複所属が生成されうるが、検知機構が無い

> 個人OSS・プレリリース段階では `ADR-0039` を適用し、実行に必要な情報だけを記載する。

- Type: Bug
- Status: Draft
- Source Issue: N/A
- Priority: P2
- Owner: Unassigned
- Scope: `03_Implement/frontend/src/domain/canonical_ops.ts`, `03_Implement/frontend/src/domain/validate_doc.ts`, `03_Implement/frontend/src/domain/island_edge_aggregate.ts`
- Related ADR/Spec: `02_Architecture/functional-dependency-integrity-2026-08-06.html`（F-5、R2(a)）, `01_Plans/adr/ADR-0069-llm-input-ir-as-the-actual-ai-input-path.md`（前提条件）, `01_Plans/adr/ADR-0078-integrity-consistency-budget-and-inspection-plan.md`（IC-10）
- Expected verification level: unit

## 課題

- 現在の問題:

`functional-dependency-integrity-2026-08-06.html` F-5（カード→島の関数従属性が強制されていない）のうち、**書込み側のドラッグ&ドロップ経路は既に修正済み**であることを確認した（`island_edge_aggregate.ts:50-76` `moveCardToIsland()` が対象カードを他の全島から除去してから追加先へ加える。`App.tsx:2882-2892` がこれを使用し、コード中のコメントが明示的に「R2(a)」を参照している）。**この点は本issueの対象ではない**（既に解決済みとして記録するのみ）。

一方、**同じ書込みクラスの別経路が未修正のまま残っている**ことを本issueの起票にあたり新たに確認した。`canonical_ops.ts:44-61` の `updateIslands()`（カード統合＝canonicalization時に呼ばれる）は、統合元カード（`sourceCardIds`）を含む島それぞれへ独立に統合先カード（`canonicalId`）を追加する。`islands.map()` の1パス内で各島の判定が元の `cardIds` に対して行われるため、**統合元カードが異なる複数の島に分散していた場合、統合先カードは複数の島へ同時に追加される**（`moveCardToIsland()` のような「他島から除去」ステップが無い）。

具体例: 島Aに `cardIds: ["a", ...]`、島Bに `cardIds: ["b", ...]` があり、`applyCanonicalization({ sourceCardIds: ["a", "b"], canonicalId: "canon-1" })` を実行すると、`canon-1` は島Aと島Bの両方の `cardIds` へ追加される。既存テスト（`canonical_ops.test.ts`）はこの跨島シナリオを検証しておらず（統合元の一方が無所属カードのケースのみをテスト）、コードレビューでの発見に依存していた。

さらに、`validate_doc.ts` の `validateIsland()`／文書全体検証には、**カードが複数の島の `cardIds` に同時出現することを検出する仕組みが一切無い**（確認済み。`shelf` には `seenCardIds` による重複検出があるが、`islands` 配列を横断した重複検出は存在しない）。そのため、上記のような重複所属が発生しても文書は妥当なまま保存・共有される。

- 利用者または開発への影響:

「カードは高々1つの島に属する」という前提（`getIslandsForCard()` のコメントが明言する規範）が、統合操作を経由すると静かに破られる。下流の多くの呼び出し箇所（表示・境界計算・エクスポート等）が単一所属を仮定しているため、跨島マージ後の表示・エクスポート結果が呼び出し箇所ごとに異なる島を採用する不整合を起こしうる。また、`ADR-0069`（LLM投入IR）の D3（`islands` をIRへ追加）は、この関数従属性が保証されていることを実装前提としており（ADR-0069「前提条件」節）、未解消のままでは `islands` の投影結果が一意にならない。

## 対応方針

- 実施すること:
  1. `validate_doc.ts` へ、**文書検証の合否（`errors`）には影響させない**、独立した助言的（advisory-only）診断関数を追加する（例: `checkIslandMembershipIntegrity(document): string[]`）。カードIDが複数の島の `cardIds` に同時出現する場合を検出して返す。**既存の `validateDocument()` の戻り値・`valid` 判定を変更しない**（`functional-dependency-integrity-2026-08-06.html` §8.1 が「fail-closedでの拒否には4観点とも反対」と結論した理由＝ローカルファーストには復旧UIが無く、文書が開けなくなるリスクが実害と釣り合わない、をそのまま踏襲する）。呼び出し箇所は、CI・保存・共有をブロックしない経路（例: 開発時コンソール警告、`docs_check.py`と同様の非ブロッキング診断スクリプト、または単体テストのみ）に限定する。
  2. `canonical_ops.ts` の `updateIslands()` に、跨島マージが実際に重複所属を生成することを示す回帰テストを追加する（**動作を今回変更する必要はない** — まず現状を可視化・固定することが目的。動作変更は下記「実施しないこと」を参照）。
  3. ADR-0069 の「前提条件」節が要求する「一意化規則の明示」を満たすため、**現状の暗黙の挙動（`getIslandsForCard()`/`islands.find()` は最初に一致した島を採用する＝先勝ち）を、単一所属を仮定する読み取り側の暫定規則として明文化する**（本issueの成果として `ADR-0069` へ反映）。跨島マージによる重複所属自体を禁止・自動解消する規則ではない（そこまでは本issueの対応方針としない）。
- 実施しないこと:
  - 重複所属を fail-closed で拒否する変更（`functional-dependency-integrity-2026-08-06.html` §8.1 の既存結論により、reject化は「計測してから判断」＝別途 `ADR-0047` 該当確認を要する。本issueは診断（warn相当）のみを範囲とする）。
  - 「統合先カードは統合元の島のうちどれに属すべきか」という業務設計判断（両方に残す／どちらか一方を選ぶ／ユーザーに確認する）の確定。これは本issueが追加する診断で実際の発生頻度を計測してから、必要なら別issueで決める。
  - `canonical_ops.ts` の跨島マージ挙動そのものの変更。

## 受入条件

- [ ] AC-1: `validate_doc.ts` に跨島カード重複所属を検出する助言的診断関数が追加され、既存の `validateDocument()` の合否判定・戻り値シグネチャを一切変更しないことがテストで示される（回帰テスト: 跨島重複を含む文書が引き続き `valid: true` を返す）。
- [ ] AC-2: `canonical_ops.test.ts` に、統合元カードが異なる2つの島に分散しているケースのテストが追加され、現状の挙動（両島へ統合先カードが追加される）が明示的に記録される。
- [ ] AC-3: `ADR-0069` の「前提条件」節が本issueを参照し、暫定の一意化規則（先勝ち、読み取り専用の規範であり書込み側の強制ではない）を明記する形へ更新される。
- [ ] AC-4: `ADR-0078` の IC-10 行が本issueを参照する形へ更新される。

## 検証計画

- 実行する確認: `npm test`（`canonical_ops.test.ts`, `validate_doc`関連テスト）を対象範囲で実行。
- 期待結果: 新規テストがグリーン、既存テスト（特に `validateDocument` の他の合否判定）に regression が無いこと。

## 補足

- 本issueは `functional-dependency-integrity-2026-08-06.html` の R2(a) のうち、書込み側バグ修正（drag&drop経路）は既に別セッションで解消済みと確認した上で、その修正が及んでいなかった別の書込み経路（統合/canonicalization経路）を新たに特定したものである。§8.1 の判定（「計測してから判断」＝warn-only診断を先行）は据え置き、reject化の要否は本issueの対象外とする。
- 本リポジトリは複数の生成AIセッションが同一ワークツリーを共有する運用がある（`01_Plans/agent_failure_lessons.md`参照）。実装前に `git status` で作業中ファイルの有無を確認する。
