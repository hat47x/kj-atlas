# Issue Draft: EXT-CONN-01 read-only MCP サーバー（ContextBundle 制約付き投影の公開）

- Type: Feature request
- Status: Draft
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A（`ADR-0054` 段階1）
- Priority: P2
- Owner: TBD
- Scope: `03_Implement/backend/`（または新規 `03_Implement/mcp/`）, `03_Implement/frontend/src/export/agent_task_export.ts`（投影ロジックの共有・抽出）, `THREAT_MODEL.md`, `02_Architecture/api.md`
- Related Backlog: `EXT-CONN-01`
- Related ADR/Spec: `01_Plans/adr/ADR-0054-external-connection-layer-staged-introduction.md`, `01_Plans/adr/ADR-0049-external-flat-rate-agent-collaboration.md`, `01_Plans/adr/ADR-0028-ai-cognitive-externalization-phase-plan.md`（CE-4）
- Expected verification level: `integration`（HTTP輸送を実装する場合は `e2e` へ引き上げ）

## Requirement meta I/F（共通キー）

- RequirementID: EXT-CONN-01
- RequirementStatement: 外部エージェント（Claude Code / ChatGPT / Copilot Studio）が、レビュー済み等の制約付き投影として kj-atlas の文脈を読み取れる read-only MCP サーバーを提供する。書き込みツールは持たない。
- PriorityClass（Must / Should / Could）: Should
- AcceptanceScenario: 前提=ADR-0054 Accepted / 操作=MCPクライアントから制約付き投影（reviewed-only 等）を読む / 期待結果=SafeMode境界どおりの内容だけが返り、監査相関（bundleHash等）が記録される / 除外=書き込み、トリガー実装、通知。
- GoNoGoGate（Required / Optional / N/A）: Required（公開面のためセキュリティ照合必須）
- SecurityGateImpact: SafeMode / share-export / public-exposure
- VerificationLevel: integration
- DecisionStatus（Fixed / Pending）: Pending
- DecisionQueueRef: `ADR-0054`（Accepted 後に Open 化）

## 背景

`ADR-0049` の手動レーン（copy/paste）で確立した安全境界（SafeMode本文redaction・未レビュー既定除外・反スコアリング・監査相関）を、MCP 輸送で自動化する第一段。読み取り専用のため最小リスクで、ChatGPT個人プランの「カスタムコネクタは読み取り専用」制約とも一致する。

## 提案する解決策

- MCP resources/tools として公開する投影: reviewed-only カード集合、根拠（evidence）サブセット、矛盾（contradiction）サブセット、島/関係の要約。ContextBundle IR（CE-0契約）の形を正とする。
- 投影ロジックは `agent_task_export.ts` の DocumentV2 直接走査＋SafeMode境界を再利用（バックエンドへ移植またはNode共有）。CE-1 実データ化を待たない。
- 輸送は stdio 先行（ローカル Claude Code）。streamable HTTP + OAuth 2.1（MCP 2026-07-28 仕様）は同一契約の追加アダプタとして分割可。
- すべての読み取りに `bundleHash` / `queryCanonicalHash` 相当の監査相関を残す（CE-4 整合）。

## 非目標

- 書き込み・提案受信（`EXT-CONN-02`）。
- トリガー/スケジューラ・通知プッシュ。
- MCP Apps（チャット内UI描画）。
- score/rank/confidence/priority を含む投影。

## 受け入れ条件（案）

- [ ] AC-1: MCPクライアントから reviewed-only 投影を取得でき、未レビュー本文・SafeMode対象が含まれない。
- [ ] AC-2: サーバーは書き込み系ツールを一切公開しない（tools/list で検証）。
- [ ] AC-3: 読み取りごとに監査相関が記録され、CE-4 の監査導線から追跡できる。
- [ ] AC-4: `THREAT_MODEL.md` に公開面（認証・認可・レート・失敗時挙動）が追記され、PRODUCT-QA-01 ゲートで照合される。
- [ ] AC-5: 投影IRは輸送非依存で、MCPアダプタ層の差し替えが契約変更なしに可能な構造になっている。

## Traceability

- Derived-from: `01_Plans/adr/ADR-0054-external-connection-layer-staged-introduction.md`
- Related: `01_Plans/research-2026-07-12-trigger-ai-external-integration.md`
- Related: `03_Implement/frontend/src/export/agent_task_export.ts`（投影・redactionの前例実装）
