# Issue: AI-MERGE-PARTIAL-01 `partial` の部分採用契約を定める

> 個人OSS・プレリリース段階では `ADR-0039` を適用し、実行に必要な情報だけを記載する。

- Type: Feature / Domain Integrity
- Status: Open
- Source Issue: `AI-MERGE-SEMANTICS-01`
- Priority: P1
- Owner: Maintainer
- Scope: `03_Implement/frontend/src/ui/MergeSuggestionsPanel.tsx`, `03_Implement/frontend/src/domain/merge_suggestion_decisions.ts`, `03_Implement/frontend/src/domain/merge_suggestion_apply.ts`, `03_Implement/backend/src/kj_atlas_api/models.py`, `02_Architecture/api.md`
- Related ADR/Spec: `AI-MERGE-SEMANTICS-01`, `AI-MERGE-APPLY-01`, `ADR-0068`, `ADR-0069`
- Expected verification level: unit → integration → E2E

## 課題

merge提案の判断には `accept` / `partial` / `reject` / `defer` があるが、現在のUIには `partial` を選んだときに「候補のうち、どのカードを採用対象とするのか」を指定する操作がない。

永続モデルには `selectedCardIds` が存在するものの、既存互換の経路では候補全体の `cardIds` をそのまま複製して記録する場合がある。この値を「部分採用として人間が選んだカード集合」と読み替えると、過去データや現行UIの意味を変えてしまう。

したがって、`partial` は現状のまま実mergeへ適用しない。人間が明示的に部分集合を選び、その選択が判断ログ・実適用・保存・再読込まで一貫して追跡できる契約を先に固定する。

## 意味境界

`partial` は「merge提案の考え方には同意するが、提案された全カードを一つに統合することには同意しない」という判断とする。

例えば A+B+C の提案に対して A+B だけを統合し、C は独立カードとして残す場合に使う。

次は `partial` と扱わない。

- 統合本文の一部だけを書き換えること。
- すべてのsourceカードを選んだまま `partial` を記録すること。
- 採用カードを指定せず、理由欄だけで「一部」と書くこと。
- 一つの提案を複数の異なる部分集合へ同時に適用すること。

統合本文の修正は `editedText` の責務、部分集合の指定は `selectedCardIds` の責務として分ける。

## UI契約

`partial` を選ぶ場合だけ、候補カードごとに採用／除外を明示できる選択UIを表示する。

- 最低2枚を選ぶ必要がある。
- 元の `cardIds` 全件を選んだ場合は `partial` として保存せず、利用者へ `accept` を使うよう案内する。
- 1枚以下の場合はmergeそのものが成立しないため保存しない。
- hold、既merge/canonicalization、`negate` / `contradicts`、異なる既知 `claimType` など、実適用時の既存guardに反する組合せは選択時または適用時に停止する。
- 選択されなかったカードは元の状態を一切変更しない。

UIはAIが部分集合を自動選択した状態から始めない。初期状態では人間が自分で採用対象を選ぶ。

## 永続契約

`MergeSuggestionDecision.selectedCardIds` は、**`partial` のときに限り、人間が明示的に選択した実部分集合を表す**。

新しい判断ログについて次を固定する。

- `accept`: `selectedCardIds` は省略するか、互換目的で全件を入れる場合でも「部分集合」とは解釈しない。
- `partial`: `selectedCardIds` を必須とし、`2 <= len(selectedCardIds) < len(cardIds)` を満たす。
- `reject` / `defer`: `selectedCardIds` を部分採用集合として利用しない。
- `selectedCardIds` は `cardIds` の部分集合で、重複を許さない。
- 判断時点のsnapshotと監査ログにも同じ集合を残す。

過去データについては、`partial` で `selectedCardIds` が欠落している、または `cardIds` 全件と同一の場合、**部分採用集合が確定していないlegacy decision** とみなし、実適用しない。

## 実適用契約

`applyRecordedMergeSuggestionDecision()` は、`partial` を扱う場合に次を満たす。

1. Document内に記録済みのdecisionだけを対象とする。
2. `selectedCardIds` が上記の厳密な部分集合条件を満たさなければfail-closedする。
3. 適用直前のDocumentで、選択されたカード集合についてhold・既merge・矛盾・claimTypeを再検査する。
4. 選択されたカードだけを `createRepresentativeMerge()` へ渡す。
5. 選択されなかったカードの本文、系譜、島所属、relation、review状態を変更しない。
6. decision snapshotの `representativeCardId` / `sourceCardIds` は、実際に適用した部分集合へ同期する。
7. merge採用だけでは代表カードを `textReviewed=true` にしない。
8. 保存・再読込後も、代表カードから実際に採用したsource集合へ戻れる。

## `mergeMethod` / `residuals` との関係

本Issueでは `mergeMethod` や自由記述の `residuals` を新しい必須契約にしない。

- 04ステップと核融合法は、どちらも現在の実適用では「sourceカードを残した代表カード生成」という同じデータ変換を使う。方式ラベルだけで適用規則が変わらない段階では、AIの自己申告を永続的な正本にしない。
- 統合でこぼれた意味の一次記録は、削除されず残るsourceカードそのものとする。AIが別の `residuals` 文を生成して正本を二重化しない。
- 将来、方式ごとに適用規則・戻し検査・UIが実際に分岐する場合は、その時点で `mergeMethod` の機械可読契約を別Issueとして追加する。

`rationale` は提案時の説明として保持できるが、04ステップ／核融合法の認定や残差の正本にはしない。

## 受入条件

- [ ] `partial` の意味を「sourceカードの真部分集合を人間が明示採用する判断」としてUI・domain・APIで統一する。
- [ ] `partial` 選択時にのみ、候補カードから2枚以上の真部分集合を選べるUIを備える。
- [ ] 全件選択や1枚以下を `partial` として記録できない。
- [ ] 新規 `partial` decisionでは `selectedCardIds` を必須の真部分集合として保存する。
- [ ] legacy `partial` の曖昧な `selectedCardIds` を実適用しない。
- [ ] 実適用は選択されたsourceだけを統合し、非選択カードを変更しない。
- [ ] 適用直前のhold・既merge・矛盾・claimType guardを部分集合に対して再実行する。
- [ ] decision → partial apply → 保存 → 再読込のE2Eで、代表カードと選択sourceの系譜を確認する。
- [ ] `mergeMethod` は実適用の意味が分岐するまで必須契約にしないことを親Issue/API文書へ同期する。
- [ ] 独立 `residuals` フィールドを追加せず、sourceカードを残差の一次記録とすることを親Issue/API文書へ同期する。
- [ ] 最終成果物を、意味を変えず自然な日本語として全文を読み直す。

## 完了境界

このIssueは `partial` というラベルをUIに追加するだけでは完了しない。

人間が明示した真部分集合が、判断ログ、実merge、traceability、保存、再読込まで同じ集合として維持され、選ばなかったカードへ副作用を与えないことをE2Eで固定するところまでを完了条件とする。
