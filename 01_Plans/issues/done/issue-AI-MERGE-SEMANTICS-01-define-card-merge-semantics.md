# Issue: AI-MERGE-SEMANTICS-01 `suggest-merges` の意味境界と受入条件を定める

> 個人OSS・プレリリース段階では `ADR-0039` を適用し、Issue本文は現在の実行に必要な情報へ絞る。実装履歴はGitとPRを正本とする。

- Type: Architecture / AI Integration
- Status: Done
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

したがって、主要な利用経路を止めるP1課題は解消している。本IssueをP1のまま保持しない。残っているのは、**どの統合方法を使った提案なのかを判断・監査の来歴として残す**P2の追跡性である。

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

## R19 — 統合方法の追跡性を実装経路から再確認

R19では、方式フィールドを先に足すのではなく、provider出力、UI、判断記録、監査、ローカルfallbackを横断して「方式が実際にどこで失われるか」を確認した。

### 観察1 — promptは方法選択を要求するが、応答契約はその結果を捨てる

backendのmerge promptは、各候補について次の二方式を使い分けるよう明示している。

- 04ステップ型の近接整理。
- 核融合法型の意味核統合。

一方、providerへ要求するJSONは `groupId`、`cardIds`、`mergedTextDraft`、任意 `rationale` だけであり、どちらを選んだかを表す欄がない。つまり**内部推論では方法を選ばせながら、人間レビューへ渡す契約でその選択を落としている**。

このため、方式追跡性は単なる追加メタデータではなく、promptとreview契約の意味の切断として扱う。

### 観察2 — UIはAI理由と人間理由を区別して保持している

現行UIは `rationale` を提案理由として表示し、採否時には別の人間判断理由を必須にしている。Document上の `mergeSuggestionDecisions` にも、AI側 `rationale` と人間側 `note` が別々に保存される。

したがって `mergeMethod` を人間理由やrationale文字列へ埋め込む必要はない。文字列prefix等の隠れプロトコルを作らず、明示的な語彙として保持する方が現在の来歴設計と整合する。

### 観察3 — 決定論fallbackは核融合法ではない

frontendの `collectMergeCandidates()` は、正規化本文一致またはtoken signature一致だけで候補を生成する。これは近接候補の決定論的探索であり、複数カードから新たな意味核を立てる処理ではない。

したがってremote AI提案とfallbackを再び同じ内部契約へ畳まず、共通の意味語彙だけを共有する。

- remote AI: モデルが `near_duplicate` / `kernel_fusion` を明示して返す。
- deterministic fallback: 事実として `near_duplicate` を付けられる。

### 観察4 — 永続decisionと短期audit eventを同一視しない

Documentの `mergeSuggestionDecisions` は、提案本文、AI rationale、人間判断理由、source/representative snapshotを保存している。これを方式の永続来歴とする。

別に存在する `MergeDecisionAuditEvent` は件数上限を持つ軽量イベント列であり、人間判断理由の表示・監査を主眼としている。方式フィールドを機械的に二重保存することを完了条件にしない。まずDocument decision snapshotを正本とし、短期auditにも方式が必要だと実使用で確認された場合だけ追加する。

## R19実装契約

方式追跡性は**必要**と確定する。実装時は次の境界を守る。

1. 共通語彙は `near_duplicate` / `kernel_fusion` の2値とする。
2. 新しいremote provider応答では `mergeMethod` を必須にする。promptが要求した方法選択をreview契約へ出すためである。
3. 決定論fallbackは `mergeMethod: "near_duplicate"` を明示する。
4. frontendのremote/common `MergeSuggestion` でも `mergeMethod` を必須にし、未知値をfail-closedにする。
5. 新しく記録するDocument decision snapshotへ `mergeMethod` を渡す。
6. 過去Documentとの後方互換のため、永続済み `MergeSuggestionDecision.mergeMethod` はoptionalとして読む。旧記録へ方式を推測補完しない。
7. UIでは方式をAI理由と別に確認できるようにする。ただし方式ラベルだけを採否理由にしない。
8. `rationale`、人間の `note`、`mergeMethod` を一つの文字列へ符号化しない。
9. short-lived `MergeDecisionAuditEvent` への重複保存は本変更の必須条件にしない。
10. `residuals`、partial自動適用、merge自動確定へ範囲を広げない。

この変更は既存Documentの破壊的schema migrationではない。新しいproposal契約は厳格化するが、保存済みdecisionはoptional fieldで読むため、ADR-0047の破壊的変更ゲートには到達しない。

## 受入条件

- [x] `suggest-merges` とIsland / Placardの意味境界を定義した。
- [x] 04ステップ型と核融合法型をカード関係に応じて使い分ける契約を定義した。
- [x] hold、明示的対立・矛盾、異なる既知claimType、既存merge系譜、候補競合を決定論的に保護した。
- [x] provider実入力をroute固有structured inputへ移し、Document生本文の迂回送出を防いだ。
- [x] 元カード・source・merge/canonical系譜・元relationへ戻れる実mergeを実装した。
- [x] AI提案の採用から明示適用・保存・再読込までをE2Eで確認した（`AI-MERGE-APPLY-01` / PR #2849〜#2852）。
- [x] remote/common提案契約と決定論fallback固有契約を分離した（R18 / PR #2853）。
- [x] SafeMode二層、PII最小化、IR上限のfail-closedを維持した。
- [x] 統合方法をproposal → decisionへ機械可読に残す必要性と、remote/fallback/旧Documentの互換境界をR19で確定した。
- [x] `mergeMethod` をprovider出力、frontend共通契約、fallback、Document decision snapshotへ実装した。
- [x] 新規remote応答の欠落・未知方式を拒否し、旧decisionの方式欠落は読めることを回帰テストで固定した。

## R20実装結果（2026-09-04）

R19で確定した方式追跡性を実装した。remote providerは各提案に `mergeMethod` を必須で返し、backendとfrontendの双方で `near_duplicate` / `kernel_fusion` 以外をfail-closedにする。決定論的fallbackは処理実態に合わせて `near_duplicate` を付ける。UIでは方式をAI rationale・人間判断理由とは別に表示し、新しく記録するDocument decision snapshotへそのまま保存する。

保存済みの旧decisionは `mergeMethod` 欠落を許容し、方式を推測補完しない。`residuals` やpartial自動適用、短期audit eventへの重複保存には範囲を広げていない。decision → apply → save → reload の既存E2Eでも方式が保持されることを確認する。

## 完了境界

主要なmerge経路は実装済みである。本Issueの残作業は上記 `mergeMethod` の一本化だけに限定する。実装完了後は本Issueを `done/` へ移す。新しい実使用証拠なしに `residuals`、自動partial適用、追加のmerge自動化へ範囲を広げない。
