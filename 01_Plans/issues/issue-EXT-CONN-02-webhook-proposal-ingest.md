# Issue Draft: EXT-CONN-02 webhook → 提案カード ingest（トリガー型出力の堆積場）

- Type: Feature request
- Status: Draft
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A（`ADR-0054` 段階2）
- Priority: P2
- Owner: TBD
- Scope: `03_Implement/backend/`（受信エンドポイント）, `03_Implement/frontend/src/import/agent_response_import.ts`（サニタイズの共有）, `THREAT_MODEL.md`
- Related Backlog: `EXT-CONN-02`
- Related ADR/Spec: `01_Plans/adr/ADR-0054-external-connection-layer-staged-introduction.md`, `01_Plans/issues/issue-EXT-AGENT-02-agent-response-import.md`（サニタイズ・提案着地の正本）, `01_Plans/issues/issue-DATA-MODEL-OPS-02-management-plane-data-boundary.md`（D3登録・認可境界）
- Expected verification level: `e2e`

## Requirement meta I/F（共通キー）

- RequirementID: EXT-CONN-02
- RequirementStatement: 外部エージェントの観察・ブリーフを `agent-response.v1` 互換 payload として HTTP で受信し、提案カード（未レビュー・自動確定なし・個別undo可）としてのみ着地させる。
- PriorityClass（Must / Should / Could）: Should
- AcceptanceScenario: 前提=EXT-CONN-01 稼働・ADR-0054 Accepted / 操作=外部エージェントが webhook へ観察を POST する / 期待結果=提案として未レビュー着地し、人間が採用するまで文書は変わらない / 除外=Consensus直接書き込み、自動採用、通知。
- GoNoGoGate（Required / Optional / N/A）: Required（悪性入力の一次面）
- SecurityGateImpact: import-sanitize / SafeMode / public-exposure
- VerificationLevel: e2e
- DecisionStatus（Fixed / Pending）: Pending
- DecisionQueueRef: `ADR-0054` はAccepted済み（2026-07-12）、`DATA-MODEL-OPS-02` D3はFixed済み（2026-07-13）。残るゲートは **EXT-CONN-01の運用実績 + D3の契約先行同期・admin認可実装/検証**。通常ownerが登録・失効できず、wrong/revoked/wrong-document tokenが拒否されるまでDraftを維持する。

## 背景

トリガー型AIの出力（会議前ブリーフ等）は ephemeral で流れて消える。これを「提案カード」として堆積させ、人間が後から KJ 法的に問題を立ち上げる素材にする（リサーチ役割D）。書き込み経路は EXT-AGENT-02 が確立した proposal-only 原則とサニタイズをそのまま強制する。

## 提案する解決策

- 受信エンドポイント（認証必須）で `agent-response.v1` 互換 payload を受け、EXT-AGENT-02 のパーサ・サニタイズを強制経路として通す: 禁止フィールド（score/rank/confidence/priority）除去または拒否、orphan 提案の保持、stale patch の適用拒否、解析だけでは文書を変えない。
- 着地は常に提案（未レビュー）。採用は既存の per-proposal Import（個別undo可）のみ。
- 由来（agent名・taskId 相関）を保持し、AI由来の視覚区別（ADR-0048 D1）に接続する。
- ingest ログを監査導線（CE-4）に残す。

## 非目標

- 自動採用・Consensus 直接書き込み。
- 通知プッシュ（着地はサイレント。人間は好きな時に見る）。
- トリガー側（何をいつ観察するか）の実装。

## 受け入れ条件（案）

- [ ] AC-1: 正常 payload が提案として着地し、人間が Import するまで文書本体が変わらない。
- [ ] AC-2: 禁止フィールド・不正 schema・stale patch が EXT-AGENT-02 と同一の規則で処理される（バイパス経路がない）。
- [ ] AC-3: 認証なしの POST は拒否される。受信面の脅威が `THREAT_MODEL.md` に追記される。
- [ ] AC-4: ingest ごとに監査ログ（由来・taskId相関・結果）が残る。
- [ ] AC-5: 着地した提案が外部由来と識別できる。視覚言語は Claude Design P32 回答で方向確定済み: メタ行の出所チップ（「⌂ agent名」、型バッジの後）＋「非人間由来」共通マーク（ADR-0048 D1拡張・色チャネル新設なし）、受け皿はキャンバス周縁の**縁側レーン**（正式用語は ADR-0054 用語定義。P32回答時の呼称は「庭」）、多数時は集約チップ「外部から n件」（通知バッジなし）。レッドラインは実装ラウンドで受領する。

## Traceability

- Derived-from: `01_Plans/adr/ADR-0054-external-connection-layer-staged-introduction.md`
- Related: `01_Plans/issues/issue-EXT-AGENT-02-agent-response-import.md`
- Related: `03_Implement/frontend/src/import/agent_response_import.ts`
