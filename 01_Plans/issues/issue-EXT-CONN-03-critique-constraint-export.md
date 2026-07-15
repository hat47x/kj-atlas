# Issue Draft: EXT-CONN-03 critique/constraint の機械可読エクスポート（訂正ループの輸出）

- Type: Feature request
- Status: Draft
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A（`ADR-0054` 段階3）
- Priority: P3
- Owner: TBD
- Scope: `03_Implement/frontend/src/export/`, `03_Implement/frontend/src/domain/types.ts`（加算フィールド）, `03_Implement/mcp/`（読み取りツール追加）, `02_Architecture/schemas.md` §18（契約正本・固定済み）, `02_Architecture/external_agent_collaboration_spec.md` §3.3a（埋め込みプロファイル・固定済み）
- Related Backlog: `EXT-CONN-03`
- Related ADR/Spec: `01_Plans/adr/ADR-0054-external-connection-layer-staged-introduction.md`, `02_Architecture/schemas.md` §18（agent-constraints.v1 正本）, `02_Architecture/external_agent_collaboration_spec.md` §3.3a, `01_Plans/issues/issue-EXT-AGENT-01-agent-task-package-export.md`
- Expected verification level: `unit` + `integration`

## Requirement meta I/F（共通キー）

- RequirementID: EXT-CONN-03
- RequirementStatement: 人間がカード・島・エージェント提案へ付けた違和感タグ（5種）・保留・却下を、次回以降のエージェント実行に渡る機械可読な制約（`agent-constraints.v1`）として輸出する。違和感は理由不要のまま輸出でき、輸出は既定で無効・明示 opt-in とする。
- PriorityClass（Must / Should / Could）: Could
- AcceptanceScenario: 前提=EXT-CONN-01/02 稼働・文書の constraintExportOptIn ON / 操作=外部エージェントが次回タスク取得時（タスクシート同梱 or MCP `get_agent_constraints`）に constraint を受け取る / 期待結果=過去の違和感・保留・却下が制約として明示され、同種の提案が繰り返されにくくなる / 除外=制約の自動学習・スコアリング・エージェント側の遵守検証。
- GoNoGoGate（Required / Optional / N/A）: Optional
- SecurityGateImpact: share-export / SafeMode
- VerificationLevel: unit + integration
- DecisionStatus（Fixed / Pending）: Pending
- DecisionQueueRef: `ADR-0054` は Accepted 済み（2026-07-12）。**constraint 契約の `schemas.md` 先行固定は 2026-07-15 に充足**（§18）。残るゲートは**段階1/2 の運用知見**（EXT-CONN-01 subslice C の稼働と EXT-CONN-02 の実装・運用開始。充足後に Open 化）。

## 背景

TRACE（arXiv:2606.13174）は「Mem0 記憶を使っても適用可能な選好チェックの57.5%が違反されたまま残る」ことを示した。記憶への保存では不十分で、**次回実行の制約として明示的に渡す**必要がある。kj-atlas には critique（違和感・理由不要・非ブロッキング）→ constraint（再配置条件）の内部設計が既にあり（`hil_rs_payload.ts` の `buildHilRsCritiqueInputs`: card/island の critiqueTags＋自由記述 → `CritiqueInput.constraintHints`）、これを外部エージェントへ輸出することで「同じ誤りを繰り返すAI」への訂正チャネルになる（リサーチ役割C）。ADR-0054 は本段階の効果を3段階中最大と位置づけている。

## 方式設計（2026-07-15 固定。正本: `schemas.md` §18）

要点のみ再掲する。詳細・契約不変条件は §18 を正とする。

- **D1 契約形態**: 独立文書 `agent-constraints.v1` を正とし、`agent-task.v1` タスクシートへの同梱は埋め込みプロファイル（`external_agent_collaboration_spec.md` §3.3a）とする。手動レーンと MCP 自動レーンで正本形状を共有し、二重定義を作らない。
- **D2 源泉**（すべて文書内・人間の判断のみ・決定論的に再導出可能）: card/island の critiqueTags＋自由記述、`Card.holdState==="held"`、`mergeSuggestionDecisions` の reject/defer、新設 `agentProposalDecisions` の rejected/held。`contradictionSignalDecisions`・`shelf` は v1 の源泉に含めない（§18.3 に理由記載）。
- **D3 持続化の補修**: エージェント提案への採否は現状セッション状態＋バックエンド監査のみで文書に残らない。`mergeSuggestionDecisions`/`contradictionSignalDecisions` と同じ「決定の文書内持続化」パターンで `DocumentV2.agentProposalDecisions?`（加算・optional）を新設する。副次効果として**却下が ⌘Z で取り消し可能・リロード後も保持**になる（保全思想の改善）。
- **D4 安全境界**（EXT-CONN-01 の原則を弱めない）: 未レビューカードの ID はいかなる形でも出さず件数のみ集計（`counts.withheldCardConstraints`）。proposal target は taskId/proposalId のエコーバックのみで文書内部 ID を含まない。自由記述は SafeMode ON で秘匿（`note: null`＋`noteRedacted: true`、`card.text` と同一判定チャネル）。契約はカード本文フィールドを持たない。
- **D5 配布**: 手動レーン=タスクシート任意節（opt-in ON のときのみ）。自動レーン=EXT-CONN-01 MCP サーバーへの読み取り専用ツール `get_agent_constraints` 追加（同一サーバー・同一 monorepo import パターン。**新しい輸送は作らない**）。opt-in OFF の文書へはエラー応答。
- **D6 opt-in**: `DocumentV2.constraintExportOptIn?`（加算・欠落=OFF）。ON への切替は人間の明示操作のみ。Claude Design P32 B-3 の方向（既定で含めない・明示 opt-in・受動態の帰結説明1行）に従う。
- **D7 決定論・監査**: entries は決定論ソート、`constraintsHash` = canonical JSON の sha256。タスクシート同梱時は相関ブロックに `constraintsHash`（optional）。MCP 読み取りは EXT-CONN-01 と同じ監査経路へ記録。
- **D8 用語衝突の回避**: `ContextProjectionConstraint`（投影の取得範囲セレクタ）と本件の constraint（訂正制約）は別概念。取得範囲セレクタへの `"constraints"` 値追加は採らず、独立ツールとした（§18.7）。

## 機能設計（実装ラウンドの設計。着手は段階ゲート充足後）

### F1 ドメイン型の加算（`03_Implement/frontend/src/domain/types.ts`）

- `AgentProposalDecision` / `AgentProposalDecisionEntry` / `DocumentV2.agentProposalDecisions?` / `DocumentV2.constraintExportOptIn?` を §18.4 のとおり追加。
- `validate_doc.ts`: 寛容/厳格の両モードで不正 entry を破棄し正しい要素を保全（`mergeSuggestionDecisions` の既存実装パターンを踏襲）。`id` 重複時は `decidedAt` が新しい方を採用。

### F2 輸出モジュール（`03_Implement/frontend/src/export/agent_constraints_export.ts`・新規）

- `buildAgentConstraints({ doc, safeMode }): Promise<AgentConstraintsV1>` — 純関数・決定論。`context_bundle_projection.ts` の設計規約（SafeModePolicy 共有・短縮ハッシュ不使用・canonicalizeJson＋sha256）をそのまま踏襲する。
- 収集は §18.3 の写像表に従う。card/island critique の収集条件（タグまたは自由記述が非空）は `buildHilRsCritiqueInputs` と同一セマンティクス（テストで同値性を固定）。
- 同一 target への複数源泉（critique と hold 等）は1 entry へ併合。ソートは §18.6。

### F3 App.tsx 配線

- エージェント提案の採用/却下ハンドラ（`handleAdoptAgentImportedProposal` / `handleRejectAgentImportedProposal`）が `agentProposalDecisions` へ entry を追記する（`applyDocumentChange` 1操作=1履歴ステップ。却下も undo 可能になる）。保留（held）は AgentResponseImportPanel の既存レビュー状態から同様に記録。
- `constraintExportOptIn` の切替 UI: SharePanel の Advanced（`isAdvancedUiEnabled`）セクション内トグル（公開範囲セレクトの近傍）。切替も `applyDocumentChange` 経由（履歴1ステップ・status message 表示）。常設 UI の純増はトグル1行のみ。
- B-3 受動態の帰結説明: opt-in ON のときに限り、SidePanel の違和感タグ入力近傍へ1行（`side_panel.critique.export_note`）。OFF では非表示（AC-5）。

### F4 タスクシート同梱（`agent_task_export.ts` 拡張）

- `doc.constraintExportOptIn === true` のとき §3.3a の「制約」節を生成順序どおり（ガードレールと文脈の間）に挿入し、相関ブロックへ `constraintsHash` を追加。OFF のとき生成物は現行と完全一致（golden fixture で固定）。

### F5 MCP ツール（`03_Implement/mcp/`）

- 読み取り専用ツール `get_agent_constraints`（入力: docId）。`agent_constraints_export.ts` を monorepo import。SafeMode パラメータの扱いは既存 `get_context_projection` と同一規約に揃える。opt-in OFF の文書にはエラー応答（契約 payload を返さない）。capability snapshot テスト（tools/list）を更新。

### F6 i18n（ja/en 両方）

- `share.panel.constraint_export.toggle` / `.hint`（トグルとその説明）、`side_panel.critique.export_note`（受動態の帰結説明）、`app.status.constraint_export.enabled` / `.disabled`（切替 status）、`app.history.agent_response.proposal_rejected` 等の決定持続化に伴う履歴ラベル。

### F7 テスト計画

- unit（`agent_constraints_export.test.ts`・golden fixture）: 空文書 / レビュー済み・未レビューカードの critique / 島 critique / hold / merge reject・defer / agentProposalDecisions / SafeMode ON の note 秘匿 / 決定論（同一入力→同一 constraintsHash）/ 併合とソート順。
- unit（不変条件・正規表現固定）: 直列化出力に `score|rank|confidence|priority|weight` が現れない（AC-2）／未レビューカード ID が現れない（AC-4）／カード本文フィールドが存在しない。
- unit（`validate_doc`）: 新フィールドの寛容/厳格検証・不正要素破棄・重複解決。
- integration: opt-in ON/OFF でのタスクシート生成差分（OFF は現行と完全一致）／`buildHilRsCritiqueInputs` との収集同値性。
- MCP: capability snapshot 更新・opt-in OFF エラー応答・正常応答の contract 形状。
- e2e（1本）: opt-in トグル ON → 違和感入力近傍に帰結説明表示 → タスクシート書き出しに「制約」節が含まれる → OFF へ戻すと両方消える。

## 非目標

- 制約の自動生成・自動学習（人間の付けた違和感・判断のみが源泉）。
- 制約への重み・スコア付け（反スコアリング維持）。
- エージェント側の遵守実装・遵守検証（受け手の責務。kj-atlas は明示的に渡すところまで）。agent-response.v1 への「制約に応答する」フィールドの追加もしない（§18.8）。
- `contradictionSignalDecisions`・`shelf` の輸出（§18.3。将来の版でも加算のみ）。
- 通知・プッシュ（縁側の原則維持）。

## 受け入れ条件（案）

- [x] AC-1: constraint 契約が `schemas.md` に先行固定され、往復互換の方針が明記される。→ **2026-07-15 充足**（§18。往復互換 = §18.8: 応答側フィールドを設けない一方向契約・全加算 optional・version 2 維持）。
- [ ] AC-2: 違和感タグ・保留・却下が理由なしでも輸出でき、score/rank/confidence/priority を含まない（正規表現によるテスト固定）。
- [ ] AC-3: EXT-CONN-01 の MCP サーバーから読み取り専用ツール `get_agent_constraints` として取得できる（新輸送なし）。
- [ ] AC-4: 輸出内容に未レビュー本文・SafeMode 対象が混入しない。未レビューカードの ID はいかなる形でも現れない（件数集計のみ）。
- [ ] AC-5: 輸出は既定で無効・明示 opt-in（Claude Design P32 方向）。有効時のみ、違和感入力の近傍に受動態の帰結説明（「この違和感は次回の依頼に制約として渡ります」）を表示し、常設UIの純増はしない。
- [ ] AC-6: エージェント提案への採否（adopted/rejected/held）が `agentProposalDecisions` として文書内へ持続化され、却下が ⌘Z で取り消し可能・リロード後も保持される。
- [ ] AC-7: 同一文書・同一 SafeMode 状態からの再輸出が同一 `constraintsHash` になる（決定論）。タスクシート同梱時は相関ブロックへ、MCP 読み取り時は既存監査経路へ `constraintsHash` が記録される。

## タスク分解（案）

- [ ] T1 ドメイン型加算＋validate（F1）。
- [ ] T2 `agent_constraints_export.ts` 本体＋golden fixture・不変条件テスト（F2, F7）。
- [ ] T3 提案採否の文書内持続化（F3 前半。AC-6）。
- [ ] T4 opt-in トグル＋B-3 帰結説明＋i18n（F3 後半, F6。AC-5）。
- [ ] T5 タスクシート同梱＋constraintsHash 相関（F4。AC-7 前半）。
- [ ] T6 MCP `get_agent_constraints`＋capability snapshot＋監査記録（F5。AC-3, AC-7 後半）。
- [ ] T7 e2e＋ドキュメント同期（`04_Documentation/` 利用手順への追記は EXT-AGENT-03 文書の改訂として実施）。

## Traceability

- Derived-from: `01_Plans/adr/ADR-0054-external-connection-layer-staged-introduction.md`
- Related: `02_Architecture/schemas.md` §18（契約正本・2026-07-15 固定）
- Related: `02_Architecture/external_agent_collaboration_spec.md` §3.3a（埋め込みプロファイル・2026-07-15 固定）
- Related: `01_Plans/research-2026-07-12-trigger-ai-external-integration.md`（追補A3: TRACE 定量根拠）
- Related: `01_Plans/issues/issue-EXT-CONN-01-readonly-mcp-server.md`, `issue-EXT-CONN-02-webhook-proposal-ingest.md`
- Related: `03_Implement/frontend/src/domain/hil_rs_payload.ts`（内部 critique→constraint 設計の前例）, `03_Implement/frontend/src/export/context_bundle_projection.ts`（外部読み取り面の安全境界前例）
