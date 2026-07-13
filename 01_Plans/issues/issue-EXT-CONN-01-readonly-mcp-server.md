# Issue Draft: EXT-CONN-01 read-only MCP サーバー（ContextBundle 制約付き投影の公開）

- Type: Feature request
- Status: Open

## Draft→Open 2026-07-12
`ADR-0054` が maintainer により Accepted（受理時条件: 用語「庭」→「縁側」置換、ADR側で対応済み）。本Issueの唯一のゲートが解消したため Open 化。
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
- DecisionStatus（Fixed / Pending）: Fixed（`ADR-0054` Accepted 2026-07-12）
- DecisionQueueRef: N/A（解消済み）

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

- [~] AC-1: MCPクライアントから reviewed-only 投影を取得でき、未レビュー本文・SafeMode対象が含まれない。→ **投影コアで担保・テスト済み**（reviewed-only は未レビューカードをノードごと除外、SafeMode ON は reviewed カード本文も redact）。MCP経由の取得はサブスライスBで結線。
- [ ] AC-2: サーバーは書き込み系ツールを一切公開しない（tools/list で検証）。→ サブスライスB（MCP結線）。
- [ ] AC-3: 読み取りごとに監査相関が記録され、CE-4 の監査導線から追跡できる。→ 投影は決定的 `bundleHash` を出力済み。監査ログ結線はサブスライスB。
- [ ] AC-4: `THREAT_MODEL.md` に公開面（認証・認可・レート・失敗時挙動）が追記され、PRODUCT-QA-01 ゲートで照合される。→ HTTP輸送を実装するサブスライスCで対応（stdioのサブスライスBは公開面なし）。
- [x] AC-5: 投影IRは輸送非依存で、MCPアダプタ層の差し替えが契約変更なしに可能な構造になっている。→ `context_bundle_projection.ts` として実装。純粋関数・輸送非依存・`ContextProjectionV1` IR固定。

## 実装記録（2026-07-12）: サブスライスA 完了 — 輸送非依存の投影コア

本Issueを輸送別に3サブスライスへ分割し、最も安全性が重くかつ今すぐ検証できる投影コアから着手した:

- **サブスライスA（本コミット・完了）**: `03_Implement/frontend/src/export/context_bundle_projection.ts`。`buildContextProjection(doc, constraint, safeMode)` が reviewed-only / evidence / contradiction / summary の4制約で read-only 投影を生成する純粋関数。安全境界は既存 `SafeModePolicy` を**そのまま**使用（`agent_task_export.ts` と同一の "share" 境界。2言語複製によるredactionドリフトを回避）。外部読み取り面は常に share 境界とみなし、SafeMode ON では reviewed カード本文も出さない。反スコアリング（score/rank/confidence/priority を出力・ハッシュとも一切含めない）と決定的 `bundleHash`（redact された本文は原文でなく null をハッシュ＝原文が相関ハッシュへ漏れない）を単体テストで固定（`context_bundle_projection.test.ts`、11 tests）。
- **サブスライスB（次）**: stdio MCP アダプタ。`resources`/`tools` として投影を公開（read-only、書き込みツールなし＝AC-2）、`GET /docs/{id}` から DocumentV2 を取得、bundleHash を ingest/query ログへ記録（AC-3）。配置は `03_Implement/mcp/`（新規 Node パッケージ）を第一候補とし、本モジュールを monorepo import で共有する（ドリフト回避）。共有の物理配置（frontend/src 直下のままか shared パッケージへ hoist するか）はサブスライスB着手時の構造判断。
- **サブスライスC（後）**: streamable HTTP + OAuth 2.1（MCP 2026-07-28 仕様）輸送を追加し ChatGPT / Copilot Studio へ到達。公開面の脅威追記（AC-4）と PRODUCT-QA-01 セキュリティ照合はここで実施。

## Traceability

- Derived-from: `01_Plans/adr/ADR-0054-external-connection-layer-staged-introduction.md`
- Related: `01_Plans/research-2026-07-12-trigger-ai-external-integration.md`
- Related: `03_Implement/frontend/src/export/agent_task_export.ts`（投影・redactionの前例実装）
