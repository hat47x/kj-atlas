# Issue Draft: EXT-AGENT-01 エージェント依頼パッケージの書き出し（AgentTaskPackage v1）

- Type: Feature request
- Status: Draft
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P2
- Owner: TBD
- Scope: `03_Implement/frontend/src/export/`, `03_Implement/frontend/src/ui/`, `03_Implement/frontend/src/i18n/locales/`, `03_Implement/frontend/e2e/`
- Related Backlog: `EXT-AGENT-01`
- Related ADR/Spec: `01_Plans/adr/ADR-0049-external-flat-rate-agent-collaboration.md`（D2）, `02_Architecture/external_agent_collaboration_spec.md`（§3 正本）, `01_Plans/issues/issue-CE1-context-query-bundle-foundation.md`
- Expected verification level: `integration`

## Requirement meta I/F（共通キー）

- RequirementID: EXT-AGENT-01
- RequirementStatement: 外部の定額課金 AI エージェントへ渡す依頼パッケージ（タスクシート Markdown＋随伴 task.json/context_bundle.json）を、Context Query Preview で人間が確認した文脈と応答契約・相関情報を束ねて生成し、共有・書き出し境界（SafeMode・共有前確認・監査）を通して書き出せるようにする。
- PriorityClass（Must / Should / Could）: Should
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=文書を開き範囲（島/カード）を選択 / 操作=「エージェントへ依頼」→ taskKind を選択 → Context Query Preview で範囲確認 → 書き出し / 期待結果=ガードレール・文脈・応答契約・相関ブロック（taskId/baseDocSignature/bundleHash）を含むタスクシートが生成され、未レビュー本文は既定除外、export-audit に exportKind=agent-task が記録される / 除外=外部への自動送信、Tier 1/2 транспорト、応答の取り込み（EXT-AGENT-02）。
- GoNoGoGate（Required / Optional / N/A）: Optional
- SecurityGateImpact: SafeMode / share-export（外部へ出る成果物の生成。既存境界を必ず通過し新しい抜け道を作らない）
- VerificationLevel: integration
- DecisionStatus（Fixed / Pending）: Fixed（ADR-0049 D2・spec §3）
- DecisionQueueRef: `ADR-0049`

## 1) 課題 / Problem statement

- 従量課金 API を使わずに定額エージェントへ思考を委ねる経路（ROADMAP 要件D）の出力側が未実装。文脈・指示・応答契約・相関情報を人手で組み立てるのは再現性がなく、SafeMode 境界も通らない。

## 2) 背景 / Context

- CE1（/context/query→/context/bundle、previewConfirmed、bundleHash）と SafeMode 書き出し境界・export-audit は実装済み。本Issueはそれらを束ねる**生成器と導線**のみを追加する。仕様正本は spec §3（構成順序・ガードレール固定文・メタスキーマ）。

## 3) 判断基準による優先度評価

- 価値: 定額エージェント活用の入口。P-07（自己ホスト）と両立する唯一の外部AI経路。
- 安全: 出力は共有・書き出し境界を必ず通過（未レビュー既定除外・出典既定OFF・SafeMode 表示・監査）。
- 規模拡大: 企業・自治体の Copilot 前提環境への導入障壁を解消。
- 後方互換: スキーマ変更なし（書き出しのみ）。

## 3.2 非目標 / Non-goals

- 外部エージェントへの自動送信・API 呼び出し（Tier 2 は別決裁）。応答取り込み（EXT-AGENT-02）。エージェント側テンプレの同梱（EXT-AGENT-03）。

## 4) 提案する解決策 / Proposed solution

- taskKind 選択（island_titles / merge_candidates / narrative_draft / opposing_viewpoints / critique_suggestions / free_analysis）→ 既存 ContextQueryPreviewPanel で範囲確認 → spec §3.3 の順序でタスクシート生成（.md ダウンロード＋クリップボードコピー）→ 随伴 JSON は任意ダウンロード。
- 相関: taskId（uuid）、baseDocSignature（CE3 と同一計算）、bundleHash/queryCanonicalHash（CE1 応答から）。書き出し済みタスクの一覧（awaiting 表示）をローカル保持。
- 監査: /export-audit（exportKind=agent-task）。i18n（ja/en）。

## 5) 受け入れ条件 / Acceptance criteria

- [ ] AC-1: 生成タスクシートが spec §3.3 の構成順序・ガードレール固定文・相関ブロックを含むことが golden fixture で固定される。
- [ ] AC-2: previewConfirmed を経ない書き出しができない（Context Query Preview 必須）。
- [ ] AC-3: 未レビュー本文が既定で除外され、includeUnreviewedDrafts 明示時のみ含まれる（SafeMode 文脈 share 適用）。
- [ ] AC-4: export-audit に exportKind=agent-task が記録される。
- [ ] AC-5: 書き出しは「詳細」（advanced）配下または作業面からの明示操作で、初期表示アンカー非回帰（CB-1）。

## 6) 実装タスク分解 / Task breakdown

- [ ] T1 タスクシート生成器（`export/agent_task_export.ts`・golden テスト）。
- [ ] T2 導線 UI（taskKind 選択＋Preview 接続＋書き出し・awaiting 一覧）。
- [ ] T3 SafeMode/preflight 統合＋export-audit。
- [ ] T4 i18n＋integration/e2e スモーク。

## 7) 検証計画 / Validation plan

- `cd 03_Implement/frontend && npm run typecheck && npm test`（golden・境界・監査）
- e2e: 依頼書き出し→ファイル内容検証（EXT-AGENT-02 のラウンドトリップ e2e と共通フィクスチャ）。

## 複雑性予算（ADR-0043 自己申告）

複雑性予算: 初期表示への純増=なし（明示操作の面のみ） / 保留操作の距離=不変 / 取り消し導線=あり（書き出しは非破壊・タスク一覧から破棄可能）

## Traceability

- Related: `01_Plans/adr/ADR-0049-external-flat-rate-agent-collaboration.md`, `02_Architecture/external_agent_collaboration_spec.md`（§3/§6）
- Related: `01_Plans/issues/issue-EXT-AGENT-02-agent-response-import.md`, `issue-EXT-AGENT-03-copilot-studio-reference-kit.md`
- Derived-from: `01_Plans/adr/ADR-0049-external-flat-rate-agent-collaboration.md`
