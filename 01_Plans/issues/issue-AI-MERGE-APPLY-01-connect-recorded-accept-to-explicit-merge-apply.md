# Issue: AI-MERGE-APPLY-01 記録済みacceptを明示的な実merge適用へ接続する

> 個人OSS・プレリリース段階では `ADR-0039` を適用し、実行に必要な情報だけを記載する。

- Type: Feature / Domain Integrity
- Status: In Progress
- Source Issue: `AI-MERGE-SEMANTICS-01`
- Priority: P1
- Owner: Maintainer
- Scope: `03_Implement/frontend/src/domain/merge_suggestion_apply.ts`, `03_Implement/frontend/src/domain/merge_suggestion_apply.test.ts`, 後続の最小UI接続
- Related ADR/Spec: `AI-MERGE-SEMANTICS-01`, `ADR-0068`, `ADR-0069`
- Expected verification level: unit → integration

## 課題

`MergeSuggestionsPanel` の `accept` は、人間の判断ログと監査イベントを記録するところまでであり、実際の代表カード生成とは接続されていない。一方、`createRepresentativeMerge()` はPR #2847で意味保存型へ改善され、元カード・島所属・relation・merge/canonical系譜を残した実mergeが可能になった。

現在不足しているのは、この二つの間にある**明示的な適用トランザクション**である。AI提案の出力を直接適用してはならず、人間が記録した判断を起点として、適用時点のDocumentを再検査したうえでのみ代表カードを生成する必要がある。

## 対応方針

第一段階としてdomain transactionを固定する。

- 対象はDocument内に実際に記録済みの `accept` 判断だけとする。
- `partial` は現UIに採用sourceの部分集合を指定する契約がないため適用しない。`selectedCardIds` が既存互換のため全候補を複製している状態を、部分採用の根拠として利用しない。
- `reject` / `defer` は適用しない。
- 適用直前のDocumentで、source欠落、hold、既merge/canonicalization、異なる既知claimType、候補間のnegate/contradictsを再検査する。
- 実mergeは `createRepresentativeMerge(..., rewireMembershipAndEdges=false)` を使い、まず最も可逆な形で適用する。
- 実merge後、判断時にはfallbackだったdecision snapshotの `representativeCardId` / source系譜を、実際に生成した代表カードへ同期する。
- merge採用を本文レビュー完了とはみなさず、代表カードの `textReviewed=false` を維持する。
- sourceカードの `Card.meta.source` は元カード上にそのまま残す。代表カードの `sources` は外部出典ではなくmerge provenanceのカードIDとして扱う。

第二段階でUIへ明示的な「適用」操作を接続する。acceptクリック自体へ暗黙適用は行わない。

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
- [x] UIから、記録済みacceptに対する明示的な実適用操作を呼び出せる。accept自体は判断記録のまま維持し、別の「採用した統合を適用」操作でdomain transactionを呼ぶ。
- [ ] decision → apply → Document保存 → 再読込を実際のUI/API経路でintegration regressionとして固定する。
- [ ] 最終成果物を自然な日本語として全文ドラフトし直す。

## 第二段階の実装結果（2026-09-03）

`MergeSuggestionsPanel` に、最新判断が `accept` の候補だけへ明示的な「採用した統合を適用」操作を追加した。`accept` ボタン自体の意味は変更せず、判断記録とDocument変更を別操作のまま保っている。

適用操作もtrusted human eventを要求し、AppはDocumentに記録された最新decisionを取得して `applyRecordedMergeSuggestionDecision()` へ渡す。成功時は既存の `applyDocumentChange()` を通してDocumentをdirtyにし、保存はアプリ既存の明示的な保存操作に委ねる。したがって、AI提案やacceptクリックだけで自動保存・自動mergeは発生しない。

実適用後は候補表示の代表カードID・解決方法・source件数を即時更新し、重複適用の操作を無効化する。

## 検証計画

第一段階:

- `merge_suggestion_apply.test.ts`
- `representative_merge.test.ts`
- `merge_traceability.test.ts`
- frontend typecheck
- docs check

第二段階:

- MergeSuggestionsPanel/Appの明示適用操作を含むintegration test
- 保存／再読込後のdecision snapshotと代表カード系譜の一致確認

## 補足

このIssueは「acceptを押したら自動mergeする」ことを目的にしない。AIはproposal-only、人間の採否判断とDocument変更は別段階、という既存の境界を保ったまま、二段階目の明示操作を安全に実装する。
