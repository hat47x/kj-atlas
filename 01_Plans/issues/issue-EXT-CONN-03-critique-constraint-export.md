# Issue Draft: EXT-CONN-03 critique/constraint の機械可読エクスポート（訂正ループの輸出）

- Type: Feature request
- Status: Draft
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A（`ADR-0054` 段階3）
- Priority: P3
- Owner: TBD
- Scope: `03_Implement/frontend/src/export/`, `02_Architecture/schemas.md`（constraint 契約の先行更新）, `03_Implement/backend/`（EXT-CONN-01 投影への合流）
- Related Backlog: `EXT-CONN-03`
- Related ADR/Spec: `01_Plans/adr/ADR-0054-external-connection-layer-staged-introduction.md`, `01_Plans/issues/issue-EXT-AGENT-01-agent-task-package-export.md`（agent-task.v1 ガードレール節）
- Expected verification level: `unit` + `integration`

## Requirement meta I/F（共通キー）

- RequirementID: EXT-CONN-03
- RequirementStatement: 人間がエージェント由来カードへ付けた違和感タグ・保留・却下を、次回以降のエージェント実行に渡る機械可読な制約として輸出する。違和感は理由不要のまま輸出できる。
- PriorityClass（Must / Should / Could）: Could
- AcceptanceScenario: 前提=EXT-CONN-01/02 稼働 / 操作=外部エージェントが次回タスク取得時に constraint を受け取る / 期待結果=過去の違和感・却下が制約として明示され、同種の提案が繰り返されにくくなる / 除外=制約の自動学習・スコアリング。
- GoNoGoGate（Required / Optional / N/A）: Optional
- SecurityGateImpact: share-export / SafeMode
- VerificationLevel: unit + integration
- DecisionStatus（Fixed / Pending）: Pending
- DecisionQueueRef: `ADR-0054`（Accepted 後、かつ段階1/2の運用知見を踏まえ、constraint 契約を `schemas.md` へ先行固定してから Open 化）

## 背景

TRACE（arXiv:2606.13174）は「Mem0 記憶を使っても適用可能な選好チェックの57.5%が違反されたまま残る」ことを示した。記憶への保存では不十分で、**次回実行の制約として明示的に渡す**必要がある。kj-atlas には critique（違和感・理由不要・非ブロッキング）→ constraint（再配置条件）の内部設計が既にあり、これを外部エージェントへ輸出することで「同じ誤りを繰り返すAI」への訂正チャネルになる（リサーチ役割C）。

## 提案する解決策

- 輸出形式の候補（実装時に決定・`schemas.md` 先行更新）: (a) `agent-task.v1` のガードレール節への constraint 追記、(b) 独立の `agent-constraints.v1` 文書。
- 内容: 対象（カード/島/提案kind）、違和感タグ（5種）、保留/却下の事実、人間の自由記述（あれば）。**理由の言語化を要求しない**（domain.md の違和感原則を輸出後も保持）。
- 配布: EXT-CONN-01 の投影に「constraints subset」として合流させる（新輸送を作らない）。

## 非目標

- 制約の自動生成・自動学習（人間の付けた違和感・判断のみが源泉）。
- 制約への重み・スコア付け（反スコアリング維持）。
- エージェント側の遵守実装（受け手の責務。kj-atlas は明示的に渡すところまで）。

## 受け入れ条件（案）

- [ ] AC-1: constraint 契約が `schemas.md` に先行固定され、往復互換の方針が明記される。
- [ ] AC-2: 違和感タグ・保留・却下が理由なしでも輸出でき、score/rank/confidence/priority を含まない。
- [ ] AC-3: EXT-CONN-01 投影から constraints subset として取得できる。
- [ ] AC-4: 輸出内容に未レビュー本文・SafeMode対象が混入しない。
- [ ] AC-5: 輸出は既定で無効・明示 opt-in（Claude Design P32 方向）。有効時のみ、違和感入力の近傍に受動態の帰結説明（「この違和感は次回の依頼に制約として渡ります」）を表示し、常設UIの純増はしない。

## Traceability

- Derived-from: `01_Plans/adr/ADR-0054-external-connection-layer-staged-introduction.md`
- Related: `01_Plans/research-2026-07-12-trigger-ai-external-integration.md`（追補A3: TRACE 定量根拠）
- Related: `01_Plans/issues/issue-EXT-CONN-01-readonly-mcp-server.md`, `issue-EXT-CONN-02-webhook-proposal-ingest.md`
