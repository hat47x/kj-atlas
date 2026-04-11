# Issue Draft: CE4 API/CLI/監査統合

- Type: Feature request
- Status: Open
- Source Issue: N/A
- Priority: P2
- Owner: Backend/Ops Team
- Scope: `01_Plans/issues/`, `02_Architecture/`, `04_Documentation/operations.md`, `04_Documentation/local_llm_ops_guide.md`
- Related Backlog: `CE-4`
- Related ADR/Spec: `ADR-0028`, `ADR-0008`
- Expected verification level: `docs-check`

## Requirement meta I/F（共通キー）
- RequirementID: `CE4-API-CLI-AUDIT`
- RequirementStatement: API/CLI/GUI同値性と監査ログ4点セットを運用導線へ統合する。
- PriorityClass: Must
- AcceptanceScenario: 前提=CE3完了 / 操作=同一queryをAPI/CLI/GUI実行 / 期待結果=同一bundleHash / 除外=認可機能拡張
- GoNoGoGate: Required
- SecurityGateImpact: SafeMode / public-exposure
- VerificationLevel: docs-check
- DecisionStatus: Fixed
- DecisionQueueRef: N/A

## 1) Context

- CE-4は運用段の再現性と監査性を固定するフェーズであり、API/CLI/GUIの同値性を契約として定義する必要がある。
- CE-0〜CE-3で確定した安全境界（safeMode既定ON、proposal-only、review昇格禁止）を運用導線で失わないことが前提。

## 2) Decision

### 2.1 API/CLI 契約（実装前固定）

- API logical operations:
  - `context-query`
  - `context-bundle`
  - `proposal-diff`
  - `apply --dry-run`（副作用なし検証専用）
- CLI operations:
  - APIと同名・同責務のコマンドを提供し、同入力時の同結果を保証する。

### 2.2 監査ログ4点セット（固定）

| Event | Required keys | Purpose |
| --- | --- | --- |
| `query` | `queryId`, `timestamp`, `actor`, `safeMode` | 入力追跡 |
| `bundle` | `queryId`, `bundleHash`, `excludedReason[]` | 決定論・除外理由追跡 |
| `proposal` | `proposalId`, `sourceBundleHash`, `status` | 提案ライフサイクル追跡 |
| `apply` | `proposalId`, `approver`, `dryRun`, `result` | 適用責務追跡 |

### 2.3 責務境界（Responsibility）

- API/CLI/GUI 同値性は「同一Query → 同一bundleHash」を最小保証とする。
- `--dry-run` は恒常的に副作用0（DB永続化なし）を保証する。
- ログ欠損時は成功扱いせず、運用上の失敗として扱う。

## 3) Consequences

- 実装レーンは共通実行ライブラリを採用し、片系独自ロジックを禁止する。
- reject reason は分類コード化し、運用時の再発分析を可能にする。
- safeMode後退、share/export緩和、Consensus直接更新が発生する設計変更は即No-Go。

## 4) 受入条件 / Acceptance criteria

- [ ] API/CLI/GUI で同一Query時に同一bundleHashを返す。
- [ ] 監査ログ4点セット欠損率0%（query/bundle/proposal/apply）。
- [ ] `--dry-run` で副作用0（DB永続化なし）を保証。
- [ ] 失敗時のreject reasonが分類コード付きで記録される。
- [ ] CIで同値性テストが自動実行される。

## 5) タスク分解（文書限定）

- [ ] T1: 監査ログイベントスキーマ（version付き）を architecture/docs に同期。
- [ ] T2: API/CLI同値性の判定基準（bundleHash一致）を明記。
- [ ] T3: `operations.md` / `local_llm_ops_guide.md` に運用runbookを整理。
- [ ] T4: dry-run副作用0の監査観点を手順化。

## 6) 検証計画 / Validation plan

- 実行コマンド:
  - `rg -n "API/CLI/GUI|bundleHash|dry-run|queryId|proposalId|excludedReason|reject reason" 01_Plans/adr 01_Plans/issues 02_Architecture 04_Documentation`
  - `python 01_Plans/issues/validate_active_issue_memos.py`
- 期待結果:
  - 同値性/監査ログ契約の語彙が一致し、validatorが成功する。

## 7) リスクとロールバック / Risks & rollback

- 失敗モード: CLI/API実装差で同値性が崩れる、または監査欠損が見逃される。
- ロールバック: 共通契約に反する文書差分をrevertし、同値性要件を再固定。
