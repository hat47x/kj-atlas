# Issue: AI-MERGE-PARTIAL-01 `partial` の部分採用契約を定める

> 個人OSS・プレリリース段階では `ADR-0039` を適用し、実行に必要な情報だけを記載する。

- Type: Feature / Domain Integrity
- Status: Done
- Source Issue: `AI-MERGE-SEMANTICS-01`
- Priority: P1
- Owner: Maintainer
- Scope: `03_Implement/frontend/src/ui/MergeSuggestionsPanel.tsx`, `03_Implement/frontend/src/domain/merge_suggestion_decisions.ts`, `03_Implement/frontend/src/domain/merge_suggestion_apply.ts`, `03_Implement/frontend/src/domain/merge/decision_audit_events.ts`, `03_Implement/frontend/e2e/merge_suggestion_partial_persistence.spec.ts`, `02_Architecture/api.md`
- Related ADR/Spec: `AI-MERGE-SEMANTICS-01`, `AI-MERGE-APPLY-01`, `ADR-0068`, `ADR-0069`
- Verification level: unit / UI / i18n / typecheck / E2E

## 課題

merge提案の判断には `accept` / `partial` / `reject` / `defer` があるが、従来の `partial` には「候補のうち、どのカードを採用するのか」を人間が指定する契約がなかった。

永続モデルには `selectedCardIds` が存在していたものの、既存互換の経路では候補全体の `cardIds` をそのまま複製する場合があった。この値を後から「人間が選んだ部分集合」と読み替えると、過去の判断の意味を変えてしまう。

このため、`partial` は**提案されたsourceカードの一部だけを、人間が明示的に採用する判断**として定義し直す。選択された集合は、判断ログ、監査、実merge、保存、再読込まで同じ集合として追跡できなければならない。

## 意味境界

A+B+C のmerge提案に対して A+B だけを統合し、C は独立したカードとして残す場合を `partial` とする。

次は `partial` には含めない。

- 統合本文だけを部分的に書き換えること。本文修正は `editedText` の責務とする。
- 全sourceカードを選択すること。この場合は `accept` を使う。
- 1枚以下しか選ばないこと。mergeそのものが成立しない。
- 採用カードを指定せず、理由欄だけで「一部採用」と記録すること。
- 一つの提案を、同時に複数の異なる部分集合へ適用すること。

## UI契約

`partial` の候補には「部分採用の対象を選ぶ」欄を表示し、利用者がsourceカードを自分で選択する。

- 初期状態ではAIが採用カードを自動選択しない。
- 2枚以上、かつ候補全件未満を選んだ場合だけ「一部採用」を有効にする。
- 全件を選ぶ場合は `accept` を使うよう案内する。
- 選ばなかったカードは実適用時にも変更しない。
- hold、既merge/canonicalization、`negate` / `contradicts`、異なる既知 `claimType` などの既存guardは、実適用直前にも再確認する。

日本語UIでは、次の文言で意味を明示する。

> 2枚以上、かつ候補の全件未満を選択してください。選ばなかったカードは変更しません。

## 永続・監査契約

新しく記録する `partial` では、`MergeSuggestionDecision.selectedCardIds` を必須とする。

- `2 <= len(selectedCardIds) < len(cardIds)` を満たす。
- `selectedCardIds` は `cardIds` の部分集合で、重複を含めない。
- 判断ログの `selectedCardIds` と監査イベントの `selectedCardIds` は同じ集合を記録する。
- 実適用後の `sourceCardIds` は、実際に適用した `selectedCardIds` と一致させる。

`accept` では、既存互換のため `selectedCardIds` に全候補が入る場合があっても、それを「部分採用集合」とは解釈しない。

旧データの `partial` で `selectedCardIds` が欠落している、または候補全件と同一である場合は、**採用した部分集合を確定できない旧判断**として扱う。推測で補完せず、実適用をfail-closedにする。

## 実適用契約

`applyRecordedMergeSuggestionDecision()` は、記録済み `partial` に対して次を行う。

1. Document内に実在する判断だけを対象にする。
2. `selectedCardIds` が厳密な部分集合条件を満たすことを確認する。
3. 適用時点のDocumentで、選択されたsourceについてhold・既merge/canonicalization・矛盾・`claimType` を再検査する。
4. 選択されたsourceだけを `createRepresentativeMerge()` へ渡す。
5. 選択されなかったカードの本文、系譜、島所属、relation、review状態を変更しない。
6. 判断snapshotの `representativeCardId` / `sourceCardIds` を、実際に生成した代表カードと適用sourceへ同期する。
7. merge採用だけでは代表カードを `textReviewed=true` にしない。
8. 保存・再読込後も、代表カードから実際に採用したsource集合へ戻れるようにする。

## `mergeMethod` と残差の扱い

本Issueでは `mergeMethod` や自由記述の `residuals` を新たな必須フィールドにしない。

04ステップと核融合法は、現在の実適用ではどちらも「元カードを残したまま代表カードを生成する」という同じデータ変換を使う。方式名だけで適用規則が変わらない段階では、AIの自己申告を永続的な正本にしない。

また、統合本文へ入り切らなかった意味の一次記録は、削除されず残るsourceカードそのものとする。AIが別の `residuals` 文を生成して、元カードと二重の正本を作らない。

将来、方式によって適用規則・戻し検査・UIが実際に分岐する場合に限り、`mergeMethod` の機械可読契約を別Issueで追加する。

## 実装結果（2026-09-03）

- `appendMergeSuggestionDecision()` は、新規 `partial` に真部分集合の `selectedCardIds` を必須化した。
- `applyRecordedMergeSuggestionDecision()` は、`partial` の選択sourceだけを実mergeへ渡すようにした。
- `partial_selection_missing` / `partial_selection_invalid` を追加し、旧来の曖昧な `partial` を実適用しない。
- `MergeDecisionAuditEvent` に任意の `selectedCardIds` を追加し、候補全体と実採用集合を分けて追跡できるようにした。
- `MergeSuggestionsPanel` に部分採用対象の選択UIを追加した。初期状態では未選択で、2枚以上・全件未満の条件を満たした場合だけ「一部採用」を有効にする。
- `App.tsx` は、人間が選んだ `selectedCardIds` を判断ログと監査イベントの双方へ同じ値で渡す。
- E2Eでは3枚候補からc1+c2だけを選び、c3を変更しないまま、判断 → 明示適用 → Save → reload を通した。

## 検証結果

一回限りの検証workflowで次を実行し、すべて成功した。検証用workflow/scriptは最終差分から削除済みである。

- merge関連domain / UI: 6 test files、41 tests
- i18n: 4 test files、40 tests
- frontend typecheck
- Playwright: `merge_suggestion_partial_persistence.spec.ts`
- active Issue memo validation
- plan triage
- diff check

E2Eでは次を確認した。

- 3枚候補のうちc1+c2だけを人間が選べる。
- 1枚選択では `partial` を記録できず、2枚選択で有効になる。
- 実mergeの `repOf` / `sources` はc1+c2だけを指す。
- c3には `mergedIntoCardId` / `canonicalId` を付けず、本文も変更しない。
- 判断ログの `cardIds` は全候補、`selectedCardIds` / `sourceCardIds` は実採用したc1+c2を保持する。
- 保存後にページを再読込しても、代表カードと独立したc3を復元できる。

## 受入条件

- [x] `partial` の意味を「sourceカードの真部分集合を人間が明示採用する判断」としてUI・domain・永続契約で統一する。
- [x] `partial` の候補から2枚以上・全件未満を選べるUIを備える。
- [x] 全件選択や1枚以下を `partial` として記録できない。
- [x] 新規 `partial` decisionでは `selectedCardIds` を必須の真部分集合として保存する。
- [x] 旧来の曖昧な `partial` を実適用しない。
- [x] 実適用は選択されたsourceだけを統合し、非選択カードを変更しない。
- [x] 適用直前のhold・既merge・矛盾・`claimType` guardを選択集合に対して再実行する。
- [x] decision → partial apply → 保存 → 再読込のE2Eで、代表カードと選択sourceの系譜を確認する。
- [x] `mergeMethod` は実適用の意味が分岐するまで必須契約にしない。
- [x] 独立 `residuals` フィールドを追加せず、sourceカードを残差の一次記録とする。
- [x] 最終成果物を、意味を変えず自然な日本語として全文を読み直す。

## 完了境界

人間が明示した真部分集合が、判断ログ、監査、実merge、traceability、保存、再読込まで同じ集合として維持され、選ばなかったカードへ副作用を与えないことを確認したため、本Issueを完了とする。
