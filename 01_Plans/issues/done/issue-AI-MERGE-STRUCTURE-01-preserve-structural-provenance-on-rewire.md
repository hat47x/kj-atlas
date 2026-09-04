# Issue: AI-MERGE-STRUCTURE-01 代表カードへの再配線で元の構造来歴を失わない

> 個人OSS・プレリリース段階では `ADR-0039` を適用し、実行に必要な情報だけを記載する。

- Type: Bug / Domain Integrity
- Status: Done
- Source Issue: `AI-MERGE-SEMANTICS-01`
- Priority: P1
- Owner: Maintainer
- Scope: `03_Implement/frontend/src/domain/representative_merge.ts`, `03_Implement/frontend/src/domain/representative_merge.test.ts`
- Related ADR/Spec: `AI-MERGE-SEMANTICS-01`, `02_Architecture/schemas.md`
- Expected verification level: unit

## 課題

`createRepresentativeMerge(..., { rewireMembershipAndEdges: true })` は、統合元カードそのものと `repOf` / `mergedIntoCardId` は残す一方、島の `cardIds` から元カードIDを取り除き、既存edgeの端点を代表カードIDへ置き換えている。

この状態を保存すると、代表カードから統合元カードへは戻れても、**どの元カードがどの島に属していたか、どの元カードにどのedgeが接続していたか**をDocument単体から完全には復元できない。kj-atlasが重視する「後から根拠と形成過程へ戻れること」に対し、表示上の再配線が永続構造の来歴を上書きしている。

## 対応方針

再配線を破壊的な置換ではなく、**代表カード側への構造投影の追加**として扱う。

- 統合元カードは従来どおり残し、`mergedIntoCardId` を付ける。
- 代表カードは `repOf` で直接の統合元カードIDを保持する。
- 再配線を選んだ場合も、元の島所属を削除しない。該当する島へ代表カードIDを追加する。
- 元edgeを変更・削除しない。統合元カードと非統合カードの間にあるedgeについて、代表カードへ接続した投影edgeを追加する。
- 統合元カード同士を結ぶedgeは元edgeだけを保持し、代表カードの自己ループは作らない。
- 複数の元edgeが同一の代表カード投影になる場合、投影edgeは同じ意味の組について一件にまとめる。元edgeは残るため、個別の来歴は失われない。
- 投影edgeのIDは既存edge IDと衝突しない決定的なIDを生成する。

この変更では新しい永続スキーマを追加しない。元データを残したまま代表カード側の閲覧構造を加えることで、既存 `DocumentV1` の範囲で可逆性を高める。

## 実施しないこと

- 統合元カードの物理削除。
- 元の島所属・edgeの上書き。
- `readingOrder` の自動変更。これは「membership and edges」の再配線とは別の意味判断を伴うため、本Issueでは変更しない。
- AI提案のacceptを実mergeの自動適用へ変更すること。

## 受入条件

- [x] 再配線なしでは、従来どおり元の島所属・edgeを変更しない。
- [x] 再配線ありでも、統合元カードの島所属がDocumentに残る。
- [x] 再配線ありでも、既存edgeのID・端点・typeがそのまま残る。
- [x] 代表カードが、統合元カードの属していた各島へ追加される。
- [x] 統合元カードと外部カードを結ぶ関係は、代表カード側の投影edgeとしても利用できる。
- [x] 統合元カード同士の関係から代表カード自己ループを生成しない。
- [x] 同一意味の投影edgeを重複生成しない。
- [x] `repOf` / `mergedIntoCardId` と元構造を組み合わせ、統合前の構造をDocument単体から追跡できる。
- [x] unit testで上記を固定する。
- [x] 内容確定後、意味を変えず自然な日本語として全文を読み直す。

## 検証計画

- `representative_merge.test.ts` で、再配線なし・再配線あり・内部edge・重複投影・複数島を確認する。
- frontendの型チェック／対象unit testを実行する。

### 検証状況(2026-09-04)

- `representative_merge.test.ts` に、上記受入条件の各項目に対応するunit testを追加・更新した(再配線なし固定、内部edge自己ループ回避、重複投影のdedup、複数島への代表カード追加を含む)。
- 実装コードのロジックを手動で追跡し、追加した全testケースの期待値と一致することを確認した。
- 別セッションが `~/kjnative-fe`(WSL nix devShell、Node 20)経由で実行を確認した。
  - `npx vitest run src/domain/representative_merge.test.ts`: 9 passed(9)
  - `npm run typecheck`(`tsc --noEmit`): exit code 0、エラーなし

## 補足

画面上で統合元カードを非表示にする機能は既に `mergedIntoCardId` を基準として存在するため、元構造を永続データから削除しなくても、表示上の簡略化とは両立できる。データの可逆性と表示上の整理を分離することを優先する。
