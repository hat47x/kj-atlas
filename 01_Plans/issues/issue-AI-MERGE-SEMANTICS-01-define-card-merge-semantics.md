# Issue: AI-MERGE-SEMANTICS-01 `suggest-merges` の意味境界と受入条件を定める

> 個人OSS・プレリリース段階では `ADR-0039` を適用し、Issue本文は現在の実行に必要な情報へ絞る。実装履歴はGitとPRを正本とする。

- Type: Architecture / AI Integration
- Status: In Progress
- Source Issue: `AI-IR-STAGE5-SCOPE-01` Stage 5
- Priority: P2
- Owner: Maintainer
- Scope: `03_Implement/backend/src/kj_atlas_api/routes/ai.py`, `03_Implement/backend/src/kj_atlas_api/models.py`, `03_Implement/backend/src/kj_atlas_api/llm_input_ir.py`, `03_Implement/frontend/src/domain/representative_merge.ts`, `03_Implement/frontend/src/domain/merge_suggestion_decisions.ts`, `03_Implement/frontend/src/domain/merge_traceability.ts`, `03_Implement/frontend/src/App.tsx`, `00_Prompt/kj_technique.md`, `02_Architecture/api.md`
- Related ADR/Spec: `01_Plans/adr/ADR-0069-llm-input-ir-as-the-actual-ai-input-path.md`, `AI-IR-PROJECTION-01`, `AI-IR-STAGE5-SCOPE-01`, `AI-MERGE-APPLY-01`
- Expected verification level: integration

## 現在地

起票時の `suggest-merges` は、ほぼカード本文の類似性だけを材料にしていた。現在のmainでは、その段階を越えている。

- 04ステップ型の近接整理と、核融合法型の意味核統合を使い分ける意味保存型promptへ移行済み。
- `holdState`、既merge、`negate`、`contradicts` evidence、異なる既知 `claimType`、同一応答内の候補競合を決定論的に保護済み。
- provider実入力は共有LLM入力IRを基底に、merge固有文脈を重ねるroute固有structured inputへ移行済み。
- 元カード、`sources`、`repOf`、`mergedIntoCardId`、`canonicalId`、元relation・島所属へ戻れる意味保存型の実mergeを実装済み。
- `accept` は判断記録、`apply` は明示的なDocument変更、保存はさらに別操作という境界を維持したまま接続済み。
- decision → apply → save → reload はE2Eで固定済み。
- R18で検出したremote AI提案と決定論ローカルfallbackの契約混線も解消済み。remote/common `MergeSuggestion` はbackend正本へ揃え、fallback固有metadataは派生表現へ分離した。

したがって、主要な利用経路を止めるP1課題は解消している。本IssueをP1のまま保持しない。残っているのは、**どの統合方法を使った提案なのかを判断・監査の来歴として残す必要があるか**というP2の追跡性である。

## 意味境界

### 04ステップ型の近接整理

意味・主体・時点・条件・感触が十分に近く、別カードとして保持する増分が小さい場合に使う。単なる語彙類似や同一テーマは十分条件ではない。

### 核融合法型の意味核統合

完全な重複ではない複数カードを一緒に見たとき、それぞれを生かした共通の意味核を新しい代表カードとして表現できる場合に使う。統合本文を元カードへ戻して比較できず、重要な条件・感触・異論が消えるなら統合しない。

04ステップを常に優先する、核融合法を常に優先するとは固定しない。意味保存性、残差の少なさ、元カードへの戻しやすさを見て選ぶ。

## グループ編成との境界

- Island / `suggest-card-groups`: 元カードを複数枚のまま近くに置き、束として読む。
- `suggest-merges`: 元カードを根拠に、新しい代表的一枚へ統合できる場合だけ提案する。
- Placard: 島全体の訴えを代弁する上位文であり、個々のカード統合とは別である。

一匹狼、少数意見、対立、異なる感触を「島に入りにくい」「似た語がある」という理由でmergeしない。`MergeSuggestion.groupId` はKJ法上のGroup/Clusterではなく、proposal-local IDである。

## hard veto

次はLLMの注意書きだけにせず、提案時と適用時の双方でfail-closedにする。

- `holdState` がある。
- card-to-card `negate` または `type=contradicts` evidenceがある。
- 両方に既知 `claimType` があり、その値が異なる。
- すでに別のmerge/canonical系譜へ入っている。
- 同一応答で一枚のカードが複数候補へ重複する。

島所属、`equivalence` / `related`、出典差は文脈として使うが、それ単独をhard vetoまたは自動許可にはしない。

## 意味保存の不変条件

- sourceカードを物理削除しない。
- sourceカード本文・meta・KA・元relation・元島所属を失わない。
- 代表カードから `repOf` / `sources`、sourceカードから `mergedIntoCardId` / `canonicalId` を通じて戻れる。
- rewireが必要でも原形を上書きせず、代表側への投影を追加する。
- AIが出典、残差、系譜を創作しない。
- `accept` だけでDocumentを変更しない。
- 実適用前に現在のDocumentでhold・矛盾・既merge等を再検査する。
- merge採用だけで代表本文をhuman-reviewedへ昇格させない。

元sourceカード自体を保持しているため、現時点ではAI生成 `residuals` フィールドを追加することを前提にしない。独立残差フィールドが本当に必要だと実使用で確認された場合にだけ再検討する。

## 残る論点 — 統合方法の追跡性

現在のpromptは04ステップ型と核融合法型を選び分けるよう要求する一方、remote/common `MergeSuggestion` には方法を機械可読に表すフィールドがない。

R19では、単にフィールドを増やすことを完了条件にしない。次を満たす場合に、後方互換な任意フィールドとして方式識別を追加する。

1. 人間が提案を読む際、近接整理なのか意味核統合なのかが採否判断に実際に影響する。
2. decision / auditへ残すことで、後から「なぜこの統合を採用したか」へ戻りやすくなる。
3. remote AI提案と決定論fallbackの責務差を再び混線させず、remote → frontend → decision → auditまで同じ意味で通せる。

追加する場合の候補語彙は `near_duplicate` / `kernel_fusion` とするが、API名は実装時に既存語彙と整合させる。方式が監査上使われないと確認できた場合は、フィールドを増やさず、その理由を記録して本Issueを閉じる。

`partial` は別問題である。採用するsource部分集合をUIで明示する契約がない現状では自動適用しない。必要になった時点で、曖昧な既存値を流用せず部分集合の操作契約を先に定める。

## 受入条件

- [x] `suggest-merges` とIsland / Placardの意味境界を定義した。
- [x] 04ステップ型と核融合法型をカード関係に応じて使い分ける契約を定義した。
- [x] hold、明示的対立・矛盾、異なる既知claimType、既存merge系譜、候補競合を決定論的に保護した。
- [x] provider実入力をroute固有structured inputへ移し、Document生本文の迂回送出を防いだ。
- [x] 元カード・source・merge/canonical系譜・元relationへ戻れる実mergeを実装した。
- [x] AI提案の採用から明示適用・保存・再読込までをE2Eで確認した（`AI-MERGE-APPLY-01` / PR #2849〜#2852）。
- [x] remote/common提案契約と決定論fallback固有契約を分離した（R18 / PR #2853）。
- [x] SafeMode二層、PII最小化、IR上限のfail-closedを維持した。
- [ ] 統合方法をproposal → decision → auditへ機械可読に残すことが実利用上必要かを確定し、必要なら後方互換に実装する。

## 完了境界

主要なmerge経路は実装済みである。本Issueの残作業は方式追跡性の要否判断だけに限定する。新しい実使用証拠なしに `residuals`、自動partial適用、追加のmerge自動化へ範囲を広げない。
