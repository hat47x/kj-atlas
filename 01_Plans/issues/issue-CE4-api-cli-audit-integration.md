# Issue Draft: CE4 API/CLI/監査統合

- Type: Feature request
- Status: Open
- Source Issue: N/A
- Priority: P2
- Owner: Backend/Ops Team
- Scope: `01_Plans/issues/`, `02_Architecture/`, `04_Documentation/local_llm_ops_guide.md`
- Related Backlog: `CE-4`
- Related ADR/Spec: `ADR-0028`, `ADR-0008`
- Expected verification level: `docs-check`

## Requirement meta I/F（共通キー）
- RequirementID: `CE4-API-CLI-AUDIT`
- RequirementStatement: API/CLI/GUI同値性と監査ログ4点セットを運用導線へ統合する。
- PriorityClass: Must
- AcceptanceScenario: 前提=CE3依存で停止しない（`sourceBundleHash`はモック入力許容） / 操作=同一queryをAPI/CLI/GUI実行 / 期待結果=同一bundleHash / 除外=認可機能拡張
- GoNoGoGate: Required
- SecurityGateImpact: SafeMode / public-exposure
- VerificationLevel: docs-check
- DecisionStatus: Fixed
- DecisionQueueRef: N/A

## 1) Read（同値性・監査4点セットの現状把握）

- CE-4は運用段の再現性と監査性を固定するフェーズであり、API/CLI/GUIの同値性を契約として定義する必要がある。
- CE-0〜CE-3で確定した安全境界（safeMode既定ON、proposal-only、review昇格禁止）を運用導線で失わないことが前提。
- CE3完了待ちはしない。`sourceBundleHash` は CE4 の契約検証においてモック入力を許容し、依存待ちを排除する。

## 2) ADR明文化（Context / Decision / Consequences）

### 2.1 Context

- `query -> bundle -> proposal -> apply` の4操作で、API/CLI/GUIのイベント語彙が不一致だと監査再現性が崩れる。
- `apply --dry-run` の副作用境界が曖昧だと、検証実行が本番データ更新と衝突する。
- 監査ログ欠損を成功扱いすると CE-4 の Exit Criteria（Auditability）に反する。

### 2.2 Decision

#### A. API/CLI 契約（実装前固定）

- API logical operations:
  - `context-query`
  - `context-bundle`
  - `proposal-diff`
  - `apply --dry-run`（副作用なし検証専用）
- CLI operations:
  - APIと同名・同責務のコマンドを提供し、同入力時の同結果を保証する。

#### B. 監査ログ4点セット（固定）

| Event | Required keys | Purpose |
| --- | --- | --- |
| `query` | `queryId`, `timestamp`, `actor`, `safeMode`, `equivalenceKey` | 入力追跡と比較軸固定 |
| `bundle` | `queryId`, `bundleHash`, `excludedReason[]`, `equivalenceKey` | 決定論・除外理由追跡 |
| `proposal` | `proposalId`, `sourceBundleHash`, `status`, `equivalenceKey` | 提案ライフサイクル追跡 |
| `apply` | `proposalId`, `approver`, `dryRun`, `sideEffect`, `result`, `equivalenceKey` | 適用責務と副作用境界追跡 |

#### C. 実行固定（Execute）

- ログキーは `query/bundle/proposal/apply` の4イベントで必須化し、欠損時は即失敗。
- `dryRun=true` では `sideEffect="none"` を必須化し、DB永続化・外部送信・状態昇格を禁止。
- `sourceBundleHash` は CE3未完了時に `mock:<hash>` 形式を許容し、契約検証を継続可能にする。

### 2.3 Consequences

- 実装レーンは共通実行ライブラリを採用し、片系独自ロジックを禁止する。
- reject reason は分類コード化し、運用時の再発分析を可能にする。
- safeMode後退、share/export緩和、Consensus直接更新、ログ欠損成功扱いは即No-Go。

## 3) Plan（AC/DoD不足提案）

### 3.1 受入条件 / Acceptance criteria

- [ ] API/CLI/GUI で同一Query時に同一bundleHashを返す。
- [ ] 監査ログ4点セット欠損率0%（query/bundle/proposal/apply）。
- [ ] `--dry-run` で副作用0（`sideEffect=none`、DB永続化なし、外部送信なし）を保証。
- [ ] `sourceBundleHash` は本番値・`mock:<hash>` の両方を受理し、同値性判定を継続可能。
- [ ] 失敗時のreject reasonが分類コード付きで記録される。
- [ ] CIで同値性テストが自動実行される。

### 3.2 DoD不足提案（本Issueで補完）

- [ ] DoD-1: 同値性キー `equivalenceKey` の定義元（query canonical hash）をArchitectureに明記。
- [ ] DoD-2: `dry-run` の禁止副作用（DB/外送/review昇格）をRuntime/Opsに明記。
- [ ] DoD-3: ログ欠損を成功扱いしない判定（fail-closed）を運用手順へ反映。

## 4) Verify → Proceed（3回自己修復上限）

- Verify-1: 用語ドリフト確認（同値性、監査4点、dry-run副作用0）。
- Verify-2: 必須キー欠損確認（`equivalenceKey`, `sideEffect`, `sourceBundleHash`）。
- Verify-3: safeMode後退語彙確認。
- 自己修復は最大3回。3回で収束しない場合は Proceed 停止し、論点を保留化する。

## 5) フェイルセーフ（停止条件）

以下を検知した場合は CE4 作業を即停止する。

1. 同値性定義の多義化（`same query` 解釈が複数）
2. ログ欠損を成功扱いする記述
3. safeMode後退要求（share/export保護緩和、未レビュー保護緩和）

## 6) タスク分解（文書限定）

- [ ] T1: 監査ログイベントスキーマ（version付き）を architecture/docs に同期。
- [ ] T2: API/CLI同値性の判定基準（bundleHash一致 + equivalenceKey一致）を明記。
- [ ] T3: `local_llm_ops_guide.md` に監査runbookを同期。
- [ ] T4: dry-run副作用0の監査観点を手順化。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `rg -n "API/CLI/GUI|bundleHash|equivalenceKey|dry-run|sideEffect|queryId|proposalId|sourceBundleHash|excludedReason|rejectReasonCode|safeMode" 01_Plans/issues/issue-CE4-api-cli-audit-integration.md 02_Architecture/deployment.md 02_Architecture/runtime_parameter_registry.md 04_Documentation/local_llm_ops_guide.md`
- 期待結果:
  - 同値性/監査ログ契約の語彙が一致し、dry-run副作用0と停止条件が明示される。

## 8) リスクとロールバック / Risks & rollback

- 失敗モード: CLI/API実装差で同値性が崩れる、または監査欠損が見逃される。
- ロールバック: 共通契約に反する文書差分をrevertし、同値性要件とフェイルセーフを再固定。
