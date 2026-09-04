# Issue: AI-MERGE-METHOD-TRACE-01 merge方式を判断まで追跡可能にする

> 実装履歴はGit/PRを正本とし、このメモは現在の契約と完了境界を残す。

- Type: Feature / Domain Integrity / AI Integration
- Status: Done
- Source Issue: `AI-MERGE-SEMANTICS-01`
- Priority: P2
- Owner: Maintainer
- Scope: `03_Implement/backend/src/kj_atlas_api/models.py`, `03_Implement/backend/src/kj_atlas_api/routes/ai.py`, `03_Implement/frontend/src/api/client.ts`, `03_Implement/frontend/src/domain/merge_suggestion_decisions.ts`, `03_Implement/frontend/src/ui/MergeSuggestionsPanel.tsx`, `02_Architecture/api.md`
- Related ADR/Spec: `ADR-0069`, `AI-MERGE-SEMANTICS-01`, `AI-MERGE-PARTIAL-01`, `AI-MERGE-APPLY-01`, 継続dogfood R19/R20
- Expected verification level: `integration`

## 完了した契約

merge提案がどの統合方式で作られたかを、提案から人間の判断記録まで同じ意味で追跡できるようにした。

- 機械可読な方式語彙を `near_duplicate` / `kernel_fusion` に固定し、フィールド名を `mergeMethod` とした。
- remote providerの新規提案では `mergeMethod` を必須とし、欠落値・未知値をbackend/frontend双方でfail-closedにする。
- 決定論fallbackとlocal mockは、実際の候補生成規則に合わせて `near_duplicate` だけを付与する。核融合法を実行したことにはしない。
- proposalの `mergeMethod` を新規Document decisionへそのまま保存し、UIでもAI理由や人間の判断理由とは分けて表示する。
- R20以前の旧decisionは方式欠落のまま読み込み可能とし、後から推測で方式を補完しない。
- Stream B、外部エージェント取込、SafeMode、Document再読込でも既知の方式語彙を保持する。
- 方式ラベルだけを理由に、accept / partial の実merge処理を自動分岐させない。
- 自由記述 `residuals` は追加せず、削除されず残るsourceカードを残差の一次記録とする。

## 検証実績

PR #2869と継続dogfood R20で、次の経路を横断して確認した。

- backend provider schemaと応答validation
- frontend decoder
- deterministic fallback / local mock
- proposalからdecisionへの保存
- UI表示
- Stream B / external-agent境界
- SafeModeとDocument validation
- 旧decisionの後方互換
- frontend / backendの関連回帰テストとtypecheck

R20の最終一回限り検証では、最新mainを取り込んだ状態で関連テスト、Active Issue memo validation、planning triage、dogfood文書検証、diff checkまで成功している。

## 完了境界

このIssueの目的は、方式の表示だけではなく、**新しい提案で方式を欠落させず、proposalから人間の判断記録まで意味を落とさず通すこと**だった。R20でその経路が実装・回帰固定され、親Issue `AI-MERGE-SEMANTICS-01` もPR #2873で完了正本へ整理されたため、本Issueも完了とする。

次は本Issueの未完条件には含めない。

- `AI-IR-SCALE-01` と `check-narrative` の大規模文書投影
- formal Case 001〜003の有効な生の実行記録
- `VALUE-REALNESS-01` の第三者価値実証
- 自動merge権限の拡張
- 方式によって実適用アルゴリズム自体を分岐させる将来設計

これらを残したままでも、merge方式のproposal → decision追跡という本Issueの完了境界は満たしている。
