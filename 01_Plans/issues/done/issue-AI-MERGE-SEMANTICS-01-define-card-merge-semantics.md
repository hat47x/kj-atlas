# Issue: AI-MERGE-SEMANTICS-01 `suggest-merges` の意味境界と受入条件を定める

> 個人OSS・プレリリース段階では `ADR-0039` を適用し、Issue本文は現在の契約と完了根拠に絞る。詳細な実装履歴はGitとPRを正本とする。

- Type: Architecture / AI Integration
- Status: Done
- Source Issue: `AI-IR-STAGE5-SCOPE-01` Stage 5
- Priority: P2
- Owner: Maintainer
- Scope: `03_Implement/backend/src/kj_atlas_api/routes/ai.py`, `03_Implement/backend/src/kj_atlas_api/models.py`, `03_Implement/backend/src/kj_atlas_api/llm_input_ir.py`, `03_Implement/frontend/src/domain/representative_merge.ts`, `03_Implement/frontend/src/domain/merge_suggestion_decisions.ts`, `03_Implement/frontend/src/domain/merge_traceability.ts`, `03_Implement/frontend/src/App.tsx`, `00_Prompt/kj_technique.md`, `02_Architecture/api.md`
- Related ADR/Spec: `01_Plans/adr/ADR-0069-llm-input-ir-as-the-actual-ai-input-path.md`, `AI-IR-PROJECTION-01`, `AI-IR-STAGE5-SCOPE-01`, `AI-MERGE-APPLY-01`
- Expected verification level: integration → E2E

## 完了した意味境界

`suggest-merges` は、単なる類似カードの重複除去ではなく、元カードの意味と来歴を残したまま統合候補を提示するproposal-onlyの支援として扱う。

統合方法は次の二つを区別する。

- `near_duplicate`: 04ステップ型の近接整理。意味・主体・時点・条件・感触が十分に近く、別カードとして保持する増分が小さい場合に用いる。
- `kernel_fusion`: 核融合法型の意味核統合。完全な重複ではない複数カードから、それぞれを生かした共通の意味核を立てる場合に用いる。

単なる語彙類似や同一テーマは統合の十分条件にしない。方式は固定順位で選ばず、意味保存性、元カードへ戻したときの妥当性、こぼれる意味の大きさを見て判断する。

Islandへのグループ編成、Placardによる島全体の表現、カードのmergeは別の操作である。一匹狼、少数意見、対立、異なる感触を、束に入りにくいことや語彙の近さだけを理由にmergeしない。

## 決定論的に保護する条件

次の条件はLLMへの注意書きだけに任せず、提案時と適用時の双方でfail-closedにする。

- `holdState` がある。
- card-to-card `negate` または `type=contradicts` evidenceがある。
- 候補間で既知 `claimType` が異なる。
- すでに別のmerge/canonical系譜へ入っている。
- 同一応答で一枚のカードが複数候補へ重複する。

島所属、`equivalence` / `related`、出典差は判断文脈として使うが、それ単独を自動許可または自動禁止にはしない。

## 意味保存と人間判断の不変条件

- sourceカードを物理削除しない。
- sourceカード本文、`meta`、KA情報、元relation、元島所属を残す。
- 代表カードから `repOf` / `sources`、sourceカードから `mergedIntoCardId` / `canonicalId` を通じて元カードへ戻れるようにする。
- 構造投影が必要でも、元の島所属やrelationを上書きして原形を失わせない。
- AIが出典、残差、系譜を創作しない。
- `accept` は人間の採用判断の記録であり、それだけではDocumentを変更しない。
- 実適用は別の明示操作とし、適用直前のDocumentでhold・矛盾・既merge等を再検査する。
- merge採用だけで代表本文をhuman-reviewedへ昇格させない。
- 保存もさらに別の明示操作として維持する。

元sourceカード自体が残差の一次記録として保持されるため、AI生成の独立 `residuals` フィールドは追加していない。実使用で別の残差表現が必要だと確認された場合にだけ再検討する。

## `mergeMethod` の追跡契約

R19/R20で、promptが選ばせた統合方法を人間レビューへ渡す契約で失わないようにした。

- 共通語彙は `near_duplicate` / `kernel_fusion` の2値とする。
- 新しいremote provider応答では `mergeMethod` を必須とし、欠落・未知値はfail-closedにする。
- 決定論的ローカルfallbackは、実際に行っている近接探索に合わせて `near_duplicate` を明示する。
- frontendの共通 `MergeSuggestion` でも同じ語彙を保持する。
- UIでは統合方法をAIの `rationale` や人間の判断理由とは別に表示する。
- 新しく記録するDocument decision snapshotへ `mergeMethod` を保存する。
- 過去Documentとの後方互換のため、旧decisionは `mergeMethod` がなくても読める。旧記録へ方式を推測して補完しない。
- Stream B、external-agent入力、SafeModeの構造境界でも同じ方式語彙を保持する。
- 件数上限を持つ短期 `MergeDecisionAuditEvent` には方式を二重保存しない。永続来歴の正本はDocument decision snapshotとする。

この追加は既存Documentの破壊的schema migrationではない。新規proposalの契約は厳格化する一方、保存済みdecisionはoptional fieldとして読み続ける。

## 完了実績

主要な経路は次のPR群で段階的に固定した。

- PR #2845〜#2848: 意味保存型prompt、決定論的guard、IR入力、source/canonical系譜と構造来歴を整備。
- PR #2849〜#2852: 記録済みacceptから明示的なapply、保存、再読込までを接続し、E2Eで固定。
- PR #2853: remote/common提案契約と決定論fallback固有契約の混線を解消。
- PR #2861: R19で `mergeMethod` の語彙・後方互換・非スコープを確定。
- PR #2869: `mergeMethod` をprovider出力からfrontend、fallback、Document decision、Stream B / external-agent境界まで実装し、対象回帰と型検査を完了。

PR #2869 の最終一回限りrun `33840395373` では最新mainを取り込んだ状態で、frontend対象回帰、typecheck、backend merge回帰、旧decisionの後方互換、Issue memo検証、triage、dogfood文書検証、diff checkを通過した。検証用workflow/scriptは成功run内で削除しており、mainには残していない。

## 受入条件

- [x] `suggest-merges` とIsland / Placardの意味境界を定義した。
- [x] 04ステップ型と核融合法型をカード関係に応じて使い分ける契約を定義した。
- [x] hold、明示的対立・矛盾、異なる既知claimType、既存merge系譜、候補競合を決定論的に保護した。
- [x] provider実入力をroute固有structured inputへ移し、Document生本文の迂回送出を防いだ。
- [x] 元カード・source・merge/canonical系譜・元relationへ戻れる実mergeを実装した。
- [x] AI提案の採用から明示適用・保存・再読込までをE2Eで確認した。
- [x] remote/common提案契約と決定論fallback固有契約を分離した。
- [x] SafeMode二層、PII最小化、IR上限のfail-closedを維持した。
- [x] 統合方法をproposal → decisionへ機械可読に残す必要性と、remote/fallback/旧Documentの互換境界を確定した。
- [x] `mergeMethod` をprovider出力、frontend共通契約、fallback、Document decision snapshotへ実装した。
- [x] 新規remote応答の欠落・未知方式を拒否し、旧decisionの方式欠落を推測せず読み続けられることを回帰テストで固定した。
- [x] 最終成果物を意味を変えず自然な日本語として読み直した。

## 非スコープ

このIssueの完了を理由に、次を暗黙に追加しない。

- AI生成 `residuals` の新設。
- `partial` 判断の自動適用。
- mergeの自動確定・自動保存。
- formal Case 001〜003や第三者価値実証の完了扱い。
- `AI-IR-SCALE-01` や `check-narrative` のscale戦略の完了扱い。

これらは、実使用で必要性と契約が確認された場合に、それぞれ独立した課題として扱う。
