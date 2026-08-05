# Issue: HIL-RS-03 HIL-RS "add" カード適用がid/textを欠いたまま追加してしまう

- Type: Bug
- Status: Done
- Source Issue: N/A
- Priority: P1
- Owner: Maintainer
- Scope: `03_Implement/frontend/src/domain/hil_rs_apply.ts`, `03_Implement/frontend/src/domain/hil_rs_rediff_stub.ts`, `03_Implement/frontend/src/domain/hil_rs_apply.test.ts`, `03_Implement/frontend/src/domain/hil_rs_rediff_stub.test.ts`, `03_Implement/frontend/src/domain/hil_rs_client_apply.integration.test.ts`
- Related ADR/Spec: `issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`, `issue-HIL-RS-02-A2-frontend-reversible-synthesis-application.md`
- Expected verification level: `unit + integration`

## 課題

- 現在の問題:
  - `hil_rs_apply.ts` の `applyCardOp()` の `"add"` 分岐は、`op.after` をそのまま `Card` としてキャストして `document.cards` に push している（`document.cards.push(op.after as Document["cards"][number]);`）。
  - ところが、正規の生成元である `hil_rs_rediff_stub.ts:67-73`（`buildHilRsRediffStub()`）は、`"add"` 操作の `after` に **`x`/`y` しか含めていない**（`after: { x: suggestedCard.x, y: suggestedCard.y }`）。カードの `id` は `targetRef`（`card:${suggestedCard.id}`）経由でのみ渡され、`text` はどこにも渡されない。
  - `applyCardOp()` は `target.id`（`targetRef` から解析済み）を新しいカードにマージしていない。結果として、正規のHIL-RS再提案フロー経由で追加されたカードは常に `id: undefined, text: undefined` のまま `document.cards` に入ってしまう（`x`/`y` だけが正しい）。これは悪意ある入力や壊れた入力に限った話ではなく、**現状の正規経路でも毎回発生する**。
  - `hil_rs_contract.ts` の `HilRsDiffOp.after` 型は `Record<string, unknown> | null` であり、`validateHilRsRediffPayload()` も `after` の中身（`opType`ごとに必要なフィールド）までは検証していない。つまり契約レベルでも「`add` の `after` に何を含めるべきか」が明文化されていない。
- 利用者または開発への影響:
  - HIL-RS（Human-in-the-loop 再提案）フローで新しいカードが提案どおりに追加されると、そのカードは `id`/`text` を欠いた壊れた状態でドキュメントに入る。`id` 欠如はid参照ベースの以降の処理（検索・削除・他操作のtargetRef解決）を壊しうる。`text` 欠如は追加されたカードが空/表示不能になる可能性が高い。

## 対応方針

- (a)と(b)を組み合わせる。
  - 正規生成元はadd操作の`after`へ、suggested cardの`id`、`text`、`x`、`y`をすべて含める。
  - 適用側は`targetRef`から得たIDを正本としてカードを再構築し、`after.id`が存在して不一致の場合、`text`欠損、非数値・非有限座標の場合はその操作をskipする。
- `text`は空文字で補完せず、suggested cardの実テキストを使う。提案に本文がなければ、空カードを捏造せず適用しない。
- A1-REDIFF-IFの契約ID、schema version、汎用`before`/`after`形状は凍結互換のため変更しない。不完全な外部payloadが構造検証を通っても、Documentへcommitする適用境界で拒否する。
- `targetRef`は最初のコロンだけをnamespace区切りとして解析し、契約上許される後続コロンを含むIDでも`targetRef`全体と同じIDを生成する。
- 追加カードへは必須4フィールドだけをallowlistで構築し、提案payloadの未知フィールドやレビュー状態をDocumentへコピーしない。
- HIL-RS再提案フロー全体の再設計は行わない。

## 実施結果

- 正規preview-rediff-apply経路で`c3`が`{ id: "c3", text: "gamma", x: 230, y: 70 }`として追加される回帰テストを固定した。
- 不完全payload、ID矛盾、`NaN`座標、レビュー状態注入はskipされ、元Documentを変更しない。
- 既存のmove/remove、critique保持、proposal-only・人手適用境界は変更していない。

## 受入条件

- [x] HIL-RS再提案経由で追加されたカードが、`targetRef`と一致する`id`、suggested cardの実`text`、有限な`x`/`y`を持って`document.cards`に入る。
- [x] `hil_rs_client_apply.integration.test.ts` の既存フローを維持し、追加カードの全必須フィールドを新規アサーションで確認する。
- [x] 不完全・矛盾payload、レビュー状態注入をcommitせず、凍結済みA1契約とproposal-only・人手適用境界を維持する。
- [x] 宣言した検証とfrontend全体回帰を実行し、結果を記録する。

## 検証

- HIL-RS近接unit・integration・契約テスト:
  - `node node_modules/vitest/vitest.mjs run src/domain/hil_rs_apply.test.ts src/domain/hil_rs_client_apply.integration.test.ts src/domain/hil_rs_rediff_stub.test.ts src/domain/hil_rs_contract.test.ts`
  - `4 files / 29 tests passed`
- frontend全体回帰:
  - `node node_modules/vitest/vitest.mjs run`
  - `226 files / 1320 tests passed`
- 型検査:
  - `node node_modules/typescript/bin/tsc --noEmit`
  - passed
- production build:
  - `node node_modules/vite/bin/vite.js build`
  - passed（既存のchunk size warningのみ）
- issue/document contract:
  - `python 01_Plans/docs_check.py`
  - passed
- patch integrity:
  - `git diff --check -- <HIL-RS-03 changed files>`
  - passed

## 補足

- 依存・リスク・ロールバックがある場合だけ記載する。
  - この所見は当初「型安全性の抜け穴（`as any`相当のキャストが不正なペイロードを通す）」という round-24 の別角度の調査から見つかったが、実際に `applyCardOp()` の `"add"` 分岐へ `id`/`text`/`x`/`y` の型チェックを追加したところ、`hil_rs_client_apply.integration.test.ts` の既存テスト（正規の生成元 `hil_rs_rediff_stub.ts` が作る `after: {x, y}` のみのペイロード）が失敗することが判明し、機械的な修正では済まないことが分かった。そのため当該修正は取り下げ、本issueとして正しい対応方針の判断を依頼する。

---
