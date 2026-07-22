# Issue: HIL-RS-03 HIL-RS "add" カード適用がid/textを欠いたまま追加してしまう

> 個人OSS・プレリリース段階では `ADR-0039` を適用し、実行に必要な情報だけを記載する。

- Type: Bug
- Status: Draft
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: Maintainer
- Scope: `03_Implement/frontend/src/domain/hil_rs_apply.ts`, `03_Implement/frontend/src/domain/hil_rs_rediff_stub.ts`, `03_Implement/frontend/src/domain/hil_rs_contract.ts`
- Related ADR/Spec: `issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`, `issue-HIL-RS-02-A2-frontend-reversible-synthesis-application.md`
- Expected verification level: `unit`

## 課題

- 現在の問題:
  - `hil_rs_apply.ts` の `applyCardOp()` の `"add"` 分岐は、`op.after` をそのまま `Card` としてキャストして `document.cards` に push している（`document.cards.push(op.after as Document["cards"][number]);`）。
  - ところが、正規の生成元である `hil_rs_rediff_stub.ts:67-73`（`buildHilRsRediffStub()`）は、`"add"` 操作の `after` に **`x`/`y` しか含めていない**（`after: { x: suggestedCard.x, y: suggestedCard.y }`）。カードの `id` は `targetRef`（`card:${suggestedCard.id}`）経由でのみ渡され、`text` はどこにも渡されない。
  - `applyCardOp()` は `target.id`（`targetRef` から解析済み）を新しいカードにマージしていない。結果として、正規のHIL-RS再提案フロー経由で追加されたカードは常に `id: undefined, text: undefined` のまま `document.cards` に入ってしまう（`x`/`y` だけが正しい）。これは悪意ある入力や壊れた入力に限った話ではなく、**現状の正規経路でも毎回発生する**。
  - `hil_rs_contract.ts` の `HilRsDiffOp.after` 型は `Record<string, unknown> | null` であり、`validateHilRsRediffPayload()` も `after` の中身（`opType`ごとに必要なフィールド）までは検証していない。つまり契約レベルでも「`add` の `after` に何を含めるべきか」が明文化されていない。
- 利用者または開発への影響:
  - HIL-RS（Human-in-the-loop 再提案）フローで新しいカードが提案どおりに追加されると、そのカードは `id`/`text` を欠いた壊れた状態でドキュメントに入る。`id` 欠如はid参照ベースの以降の処理（検索・削除・他操作のtargetRef解決）を壊しうる。`text` 欠如は追加されたカードが空/表示不能になる可能性が高い。

## 対応方針

- 実施すること（人間の設計判断が必要。次のいずれかを選ぶ）:
  - (a) `hil_rs_rediff_stub.ts` の `"add"` 生成箇所を修正し、`after` に `id`（または少なくとも `text`）を含める。ただし、これは提案元（将来の実AI再提案プロバイダ）が同じ形式に従う保証がないため、根本解決にはならない可能性がある。
  - (b) `hil_rs_apply.ts` の `applyCardOp()` 側で、`"add"` 適用時に `target.id`（解析済み）を明示的にマージし、`text` については「追加時は空文字列を初期値とする」等の明確なデフォルト方針を定める。
  - (c) 上記の組み合わせ、または `HilRsDiffOp` の型自体を `opType` ごとに判別可能なユニオン型に強め、`add` の `after` が `Card` 全体（`id`/`text`/`x`/`y`）を含むことを型レベルで強制する。
  - いずれの方針でも、「追加されたカードの初期 `text` は何であるべきか」（空文字列か、それとも別の情報源から補完するか）という製品判断が必要。
- 実施しないこと:
  - HIL-RS再提案フロー全体の再設計（本issueはカード追加時のid/text欠落という一点に閉じる）。

## 受入条件

- [ ] HIL-RS再提案経由で追加されたカードが、`id`（`targetRef` と一致）と `text`（明確に定義されたデフォルトまたは実データ）を欠かずに `document.cards` に入る。
- [ ] `hil_rs_client_apply.integration.test.ts` の既存テストが継続して通過する。
- [ ] 関連する安全・互換性を損なわない。
- [ ] 宣言した検証を実行するか、未実施理由を記録する。

## 検証計画

- 実行する確認:
  - `npx vitest run src/domain/hil_rs_apply.test.ts src/domain/hil_rs_client_apply.integration.test.ts`
  - 追加されたカードの `id`/`text` が期待どおりであることを検証する新規アサーションを追加する。
- 期待結果:
  - 追加されたカードが `id`/`text`/`x`/`y` すべてを正しく持つ。

## 補足

- 依存・リスク・ロールバックがある場合だけ記載する。
  - この所見は当初「型安全性の抜け穴（`as any`相当のキャストが不正なペイロードを通す）」という round-24 の別角度の調査から見つかったが、実際に `applyCardOp()` の `"add"` 分岐へ `id`/`text`/`x`/`y` の型チェックを追加したところ、`hil_rs_client_apply.integration.test.ts` の既存テスト（正規の生成元 `hil_rs_rediff_stub.ts` が作る `after: {x, y}` のみのペイロード）が失敗することが判明し、機械的な修正では済まないことが分かった。そのため当該修正は取り下げ、本issueとして正しい対応方針の判断を依頼する。

---

## Authoring Checklist（人間/生成AI 共通）

- [x] `Source Issue` が運用状態と整合している。
- [x] `Related ADR/Spec` が最低1件ある。
- [x] 受入条件に「安全」「互換」「検証」が含まれる。
- [x] `Validation plan` に具体コマンドがある。
- [x] 非目標が明記されスコープ逸脱を防いでいる。
