# Issue: AI-MERGE-APPLY-01 記録済みの採用判断を明示的なmerge適用へ接続する

> 個人OSS・プレリリース段階では `ADR-0039` を適用し、実行に必要な情報だけを記載する。

- Type: Feature / Domain Integrity
- Status: Done
- Source Issue: `AI-MERGE-SEMANTICS-01`
- Priority: P1
- Owner: Maintainer
- Scope: `03_Implement/frontend/src/domain/merge_suggestion_apply.ts`, `03_Implement/frontend/src/domain/merge_suggestion_apply.test.ts`, `03_Implement/frontend/src/ui/MergeSuggestionsPanel.tsx`, `03_Implement/frontend/src/App.tsx`, `03_Implement/frontend/e2e/merge_suggestion_apply_persistence.spec.ts`
- Related ADR/Spec: `AI-MERGE-SEMANTICS-01`, `ADR-0068`, `ADR-0069`
- Expected verification level: unit → integration → E2E

## 課題

`MergeSuggestionsPanel` の `accept` は、人間の採用判断と監査記録を残すところまでを担い、実際の代表カード生成とは分離されている。一方、`createRepresentativeMerge()` はPR #2847で意味保存型へ改善され、元カード、島所属、relation、merge/canonical系譜を残したまま代表カードを生成できる。

必要だったのは、この二つを自動的に直結することではなく、**記録済みの人間判断を起点として、現在のDocumentを再検査してから実行する明示的な適用トランザクション**である。AI提案や `accept` のクリックだけでDocumentを書き換えたり保存したりせず、人間の判断、実適用、保存を別々の操作として保つ。

## 対応方針

第一段階ではdomain transactionを固定した。

- Documentに実際に記録済みの `accept` 判断だけを適用対象とする。
- `partial` は、現UIに採用sourceの部分集合を指定する契約がないため適用しない。既存互換の `selectedCardIds` を部分採用の根拠として読み替えない。
- `reject` / `defer` は適用しない。
- 適用直前のDocumentで、source欠落、hold、既merge/canonicalization、異なる既知claimType、候補間の `negate` / `contradicts` を再検査する。
- 実mergeは `createRepresentativeMerge(..., rewireMembershipAndEdges=false)` を使い、元カードと既存構造を残す可逆な適用を基本とする。
- 実merge後、判断時点ではfallbackだったdecision snapshotの `representativeCardId` とsource系譜を、実際に生成した代表カードへ同期する。
- merge採用を本文レビュー完了とはみなさず、代表カードの `textReviewed=false` を維持する。
- sourceカードの `Card.meta.source` は元カード上に残す。代表カードの `sources` は外部出典ではなく、merge元カードIDの系譜として扱う。

第二段階ではUIへ明示的な「採用した統合を適用」操作を接続した。`accept` 自体の意味は判断記録のまま変更せず、実適用を別操作として保った。

第三段階では、判断記録から保存・再読込までを実際のUI/API経路でE2E検証した。

## 受入条件

- [x] 記録済みacceptだけを実mergeへ変換するdomain transactionがある。
- [x] 未記録のdecision objectを適用できない。
- [x] partial/reject/deferは実適用されない。
- [x] 適用時に現在のhold・既merge・矛盾を再確認し、競合時はfail-closedになる。
- [x] sourceカードの本文・外部元記録参照・構造を失わない。
- [x] 代表カードは `repOf` / `sources` でmerge provenanceを保持する。
- [x] decision snapshotが適用後の実代表カードIDとsource系譜へ同期される。
- [x] merge採用だけでは `textReviewed=true` に昇格しない。
- [x] JSON save/reload相当のround-trip後も代表カードからsourceへ戻れることをunit testで確認する。
- [x] UIから、記録済みacceptに対する明示的な実適用操作を呼び出せる。accept自体は判断記録のまま維持する。
- [x] decision → apply → Document保存 → 再読込を、実際のUI/API経路でE2E regressionとして固定する。
- [x] 最終成果物を、意味を変えず自然な日本語として全文を読み直す。

## 第一・第二段階の実装結果（2026-09-03）

PR #2849で `applyRecordedMergeSuggestionDecision()` を追加し、記録済みacceptだけを現在のDocumentへ明示適用できるdomain境界を固定した。適用時にはDocumentを再検査し、判断後にholdや矛盾、既merge状態などが生じていれば停止する。

PR #2850では `MergeSuggestionsPanel` に、最新判断が `accept` の候補だけへ「採用した統合を適用」操作を追加した。適用操作もtrusted human eventを要求し、成功時は既存の `applyDocumentChange()` を通してDocumentをdirtyにする。保存は従来どおり別の明示操作であり、AI提案、accept、適用のいずれも勝手に永続化しない。

## 第三段階のE2E結果（2026-09-03）

`merge_suggestion_apply_persistence.spec.ts` で、外部LLMを使わず既存の決定論的ローカル候補生成を利用し、次の実経路を通した。

1. reviewed済みの近接カードからmerge候補を生成する。
2. 人間操作として判断理由を入力し、`accept` を記録する。
3. 別の「採用した統合を適用」操作を実行する。
4. 既存の保存操作で `PUT /docs/{id}` を行う。
5. 保存されたDocumentについて、代表カードの `repOf` / `sources`、元カードの `mergedIntoCardId` / `canonicalId`、decision snapshotの `representativeCardId` / `sourceCardIds` を確認する。
6. ページを再読込し、同じ `GET /docs/{id}` 経路から文書を読み直して、代表カードと元カードの本文がUIへ戻ることを確認する。

このE2Eの初回実走で、判断記録時の `applyDocumentChange()` がmerge候補stateを無条件に消していたため、accept直後に明示適用ボタンが表示できない残差を検出した。`applyDocumentChange()` に `preserveMergeSuggestions` を追加し、判断記録と実適用の二つの経路だけ候補stateを保持するよう修正した。その他のDocument変更では従来どおり候補を破棄するため、古い候補を一般的に保持するよう契約を緩めてはいない。

修正後は、E2E、merge関連unit test、frontend typecheck、active Issue memo検証、triage、差分検査がすべて成功した。

## 完了境界

このIssueは、`accept` を押しただけで自動mergeする仕組みを作るものではない。AIはproposal-only、人間の採否判断、Documentへの実適用、永続化は別段階という既存境界を保ったまま、記録済みacceptを安全に実適用し、その結果を保存・再読込しても系譜を追えるところまでを完了範囲とする。

`partial` の意味と部分集合指定UI、04ステップ／核融合法の方法表現や残差契約など、merge意味論全体の未完事項は `AI-MERGE-SEMANTICS-01` で継続する。
