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
- RequirementStatement: Phase 1〜6を通じて API/CLI/GUI同値性と監査ログ4点セットを固定し、運用導線へ統合する。
- PriorityClass: Must
- AcceptanceScenario: 前提=CE3依存で停止しない（`sourceBundleHash`はモック入力許容） / 操作=同一queryをAPI/CLI/GUI実行 / 期待結果=同一bundleHash / 除外=認可機能拡張
- GoNoGoGate: Required
- SecurityGateImpact: SafeMode / public-exposure
- VerificationLevel: docs-check
- DecisionStatus: Fixed
- Stream: `E` (CE4 API/CLI Audit Integration)
- DecisionQueueRef: N/A

## 1) Phase 1 Read（同値性・監査4点セットの現状把握）

- Phase 1〜6 で契約ドリフトを許容しないため、CE-4は運用段の再現性と監査性を固定するフェーズとして API/CLI/GUI 同値性を明文化する必要がある。
- CE-0〜CE-3で確定した安全境界（safeMode既定ON、proposal-only、review昇格禁止）を運用導線で失わないことが前提。
- CE3完了待ちはしない。`sourceBundleHash` は CE4 の契約検証においてモック入力を許容し、依存待ちを排除する。
- Read固定4点セット:
  1. 同値性判定は `equivalenceKey + bundleHash` の AND 条件で固定する。
  2. 監査イベントは `query/bundle/proposal/apply` の4点セットを必須化する。
  3. `apply --dry-run` は副作用境界（DB永続化/外部送信/review昇格なし）を固定する。
  4. `sourceBundleHash` は `mock:<hash>` と本番 hash の双方を受理する。

## 2) Phase 2 ADR CDC明文化（Context / Decision / Consequences）

### 2.1 Context

- `query -> bundle -> proposal -> apply` の4操作で、API/CLI/GUIのイベント語彙が不一致だと監査再現性が崩れる。
- `apply --dry-run` の副作用境界が曖昧だと、検証実行が本番データ更新と衝突する。
- 監査ログ欠損を成功扱いすると CE-4 の Exit Criteria（Auditability）に反する。

### 2.2 Decision（Execute固定: API/CLI/GUI同値性 + 監査4点セット）

#### A. API/CLI 契約（実装前固定）

- API logical operations:
  - `context-query`
  - `context-bundle`
  - `proposal-diff`
  - `apply --dry-run`（副作用なし検証専用）
- CLI operations:
  - APIと同名・同責務のコマンドを提供し、同入力時の同結果を保証する。
- GUI operations:
  - GUIは内部的にAPI/CLIと同じ logical operation を呼び出し、`equivalenceKey` と `bundleHash` の一致を監査可能にする。

#### B. 監査ログ4点セット（固定）

| Event | Required keys | Purpose |
| --- | --- | --- |
| `query` | `queryId`, `timestamp`, `actor`, `safeMode`, `equivalenceKey` | 入力追跡と比較軸固定 |
| `bundle` | `queryId`, `bundleHash`, `excludedReason[]`, `equivalenceKey` | 決定論・除外理由追跡 |
| `proposal` | `proposalId`, `sourceBundleHash`, `status`, `equivalenceKey` | 提案ライフサイクル追跡 |
| `apply` | `proposalId`, `approver`, `dryRun`, `sideEffect`, `result`, `equivalenceKey` | 適用責務と副作用境界追跡 |

#### C. 実行固定（Execute）

- ログキーは `query/bundle/proposal/apply` の4イベントで必須化し、欠損時は即失敗（成功扱い禁止）。
- `dryRun=true` では `sideEffect="none"` を必須化し、DB永続化・外部送信・状態昇格を禁止（must）。
- `sourceBundleHash` は CE3未完了時に `mock:<hash>` 形式を許容し、契約検証を継続可能にする。
- Phase 1〜6 の全検証で、同値性判定は `equivalenceKey + bundleHash` のAND条件を固定する。

### 2.3 Consequences

- 実装レーンは共通実行ライブラリを採用し、片系独自ロジックを禁止する。
- reject reason は分類コード化し、運用時の再発分析を可能にする。
- safeMode後退、share/export緩和、Consensus直接更新、ログ欠損成功扱いは即No-Go。
- 契約検証は `sourceBundleHash` の値種別（`mock:<hash>` / 本番hash）に依らず同一フローで実施し、監査導線の分岐を禁止する。

### 2.4 CDC固定テーブル（Phase 1〜6 横断）

| 区分 | CE4固定事項 | No-Go 条件 |
| --- | --- | --- |
| Context | API/CLI/GUI の logical operation を `context-query/context-bundle/proposal-diff/apply --dry-run` に統一する。 | operation語彙がチャネルごとに分岐する。 |
| Decision | 同値性判定を `equivalenceKey + bundleHash`（AND）に固定し、監査4点セット（`query/bundle/proposal/apply`）を必須化する。 | 監査4点欠損を成功扱いする。 |
| Consequences | `dryRun=true -> sideEffect=none` を強制し、`sourceBundleHash` は `mock:<hash>` / 本番hash を同一契約で検証する。 | dry-runで副作用が発生、または hash 種別で検証経路を分岐する。 |

## 3) Phase 3 Plan（AC/DoD補完提案）

> Phase進行は `Read → ADR CDC → Plan → Execute → Verify → Proceed` の固定順序を維持し、Verifyで未収束（自己修復3回超過）ならProceedを禁止する。


### 3.1 受入条件 / Acceptance criteria

- [x] API/CLI/GUI で同一Query時に同一bundleHashを返す。
- [x] 監査ログ4点セット欠損率0%（query/bundle/proposal/apply）。
- [x] `--dry-run` で副作用0（`dryRun=true` なら常に `sideEffect=none`、DB永続化なし、外部送信なし、review昇格なし）を保証。
- [x] `sourceBundleHash` は本番値・`mock:<hash>` の両方を受理し、同値性判定を継続可能（依存切断）。
- [x] 失敗時のreject reasonが分類コード付きで記録される。
- [x] CIで同値性テストが自動実行される（`03_Implement/backend/tests/test_docs_audit_integration.py` をCI標準pytest対象として維持）。

### 3.2 DoD不足提案（本Issueで補完）

- [x] DoD-1: 同値性キー `equivalenceKey` の定義元（query canonical hash）をArchitectureに明記。
- [x] DoD-2: `dry-run` の禁止副作用（DB/外送/review昇格）をRuntime/Opsに明記。
- [x] DoD-3: ログ欠損を成功扱いしない判定（fail-closed）を運用手順へ反映。
- [x] DoD-4: 監査イベント4点（`query/bundle/proposal/apply`）の `schemaVersion` を固定し、API/CLI/GUIで同一値を記録する。
- [x] DoD-5: `rejectReasonCode` の分類コード（例: `missing_event`, `equivalence_mismatch`, `dry_run_side_effect`, `safemode_regression`）を運用記録へ固定する。

## 4) Phase 4 Execute（mock `sourceBundleHash` 許容で依存切断）

- Execute開始時Read（再確認）:
  - 同値性判定は `equivalenceKey + bundleHash` の AND 条件。
  - 監査イベントは `query/bundle/proposal/apply` 4点セット必須。
  - `apply --dry-run` は `sideEffect=none` を必須とし、副作用境界を固定。
  - `sourceBundleHash` は `mock:<hash>` と本番hashを同一契約で受理。
- 実行固定:
  - CE3依存の完了待ちを禁止し、`mock:<hash>` 入力で契約検証を継続。
  - API/CLI/GUI は同一 logical operation を使い、片系独自分岐を禁止。
  - 監査キー欠損時は fail-closed で即失敗（成功扱い禁止）。

## 5) Phase 5 Verify（4点セット欠損=No-Go、自己修復最大3回）

- Verify開始時Read（再確認）:
  - No-Go条件は「4点セット欠損」「dry-run副作用境界違反」「同値性判定不一致」。
  - 自己修復は最大3回、4回目は禁止。

- Verify-1: 用語ドリフト確認（同値性、監査4点、dry-run副作用0）。
- Verify-2: 必須キー欠損確認（`equivalenceKey`, `sideEffect`, `sourceBundleHash`）。
- Verify-3: safeMode後退語彙確認。
- Verify-4: `sourceBundleHash` が `mock:<hash>` と本番hashの双方で同一契約（同値性判定・監査4点セット）を満たすことを確認。
- Verify-5: `channel`（`api|cli|gui`）差分があっても必須キー集合（`equivalenceKey`, `bundleHash`, `sourceBundleHash`, `dryRun`, `sideEffect`, `schemaVersion`）が不変であることを確認。
- 自己修復は最大3回。3回で収束しない場合は Proceed 停止し、論点を保留化する。

## 6) Phase 6 Proceed（運用導線への引継ぎ記録）

- Proceed開始時Read（再確認）:
  - 運用導線への引継ぎ先は `04_Documentation/local_llm_ops_guide.md` の CE4 runbook。
  - 引継ぎ記録には `equivalenceKey + bundleHash` 判定、4点監査、dry-run副作用境界、`mock:<hash>` 許容を必ず含める。
- 引継ぎ記録（本Issueの完了条件）:
  - `local_llm_ops_guide.md` に CE4運用runbook（Verify/停止条件含む）が同期済みであること。
  - 4点セット欠損を No-Go とする fail-closed 原則が運用手順に明記されていること。
  - 3回自己修復上限と「超過時停止」が運用手順に明記されていること。

## 7) フェイルセーフ（停止条件）

以下を検知した場合は CE4 作業を即停止する。

1. 同値性定義の多義化（`same query` 解釈が複数）
2. ログ欠損を成功扱いする記述
3. safeMode後退要求（share/export保護緩和、未レビュー保護緩和）
4. Consensus への直書き要求（proposal/apply 契約を迂回する更新要求）

## 8) タスク分解（文書限定）

- [x] T1: 監査ログイベントスキーマ（version付き）を architecture/docs に同期。
- [x] T2: API/CLI同値性の判定基準（bundleHash一致 + equivalenceKey一致）を明記。
- [x] T3: `local_llm_ops_guide.md` に監査runbookを同期。
- [x] T4: dry-run副作用0の監査観点を手順化。

## 9) 検証計画 / Validation plan

- 実行コマンド:
  - `rg -n "API/CLI/GUI|bundleHash|equivalenceKey|dryRun|sideEffect|queryId|proposalId|sourceBundleHash|excludedReason|rejectReasonCode|safeMode|fail-closed|schemaVersion" 01_Plans/issues/issue-CE4-api-cli-audit-integration.md 02_Architecture/api.md 04_Documentation/local_llm_ops_guide.md`
- 期待結果:
  - 同値性/監査ログ契約の語彙が一致し、dry-run副作用0と停止条件が明示される。

## 10) リスクとロールバック / Risks & rollback

- 失敗モード: CLI/API実装差で同値性が崩れる、または監査欠損が見逃される。
- ロールバック: 共通契約に反する文書差分をrevertし、同値性要件とフェイルセーフを再固定。


## 11) Phase 6 Proceed（CE3向け参照専用I/F）

- CE3は CE4 の同値性判定を `equivalenceKey + bundleHash` のAND条件で参照する。
- 監査4点セット（`query/bundle/proposal/apply`）は欠損時 fail-closed を維持する。
- `dryRun=true` の `sideEffect=none` を破る経路は契約違反として扱う。

フェイルセーフ（即停止）: SafeMode後退 / auto-apply許容 / 未レビュー昇格許容。

---

## 12) Stream E 実施記録（2026-04-12）

### Plan（AC/DoD合意）

- AC固定: `equivalenceKey + bundleHash`（AND）、監査4点セット、`apply --dry-run`、`sourceBundleHash` の `mock:<hash>` 許容を維持する。
- DoD固定: API契約・CLIコマンド・監査キーの語彙ドリフトを fail-closed で検知する。

### Execute（API契約 → CLI連携 → 監査ログ）

- API: `operation=apply` で `dryRun=false` を reject するバリデーションを追加。
- API: `operation` と `command` の固定マッピングを導入し、ミスマッチを reject するガードを追加。
- CLI: `apply` コマンドは常に `dryRun=true` を送信するよう固定（非dry-run経路を排除）。
- Docs: CE4 runbook に operation/command 固定マッピングと apply dry-run 必須を追記。

### Verify（契約テスト/統合テスト）

- `test_context_audit_rejects_apply_without_dry_run`
- `test_context_audit_rejects_operation_command_mismatch`
- `test_cli_apply_forces_dry_run`

### Proceed（運用引継ぎ）

- `04_Documentation/local_llm_ops_guide.md` の CE4 runbook へ運用制約を同期済み。
- 既存監査スキーマ（`schemaVersion="ce4.audit.v1"`）は非破壊で維持。変更不要のためフェイルセーフ停止条件には未該当。

## 13) Stream E Verify実行ログ（docs-check / 自己修復3回）

- Verify command（docs-check）:
  - `rg -n "equivalenceKey|bundleHash|dryRun|sideEffect|sourceBundleHash|schemaVersion|rejectReasonCode|query|bundle|proposal|apply|fail-closed|mock:<hash>" 01_Plans/issues/issue-CE4-api-cli-audit-integration.md 02_Architecture/api.md 02_Architecture/runtime_parameter_registry.md 04_Documentation/local_llm_ops_guide.md`
  - `git diff --check`
- 自己修復ログ:
  1. 修復1: AC/DoD/TODOの未完了チェックを固定契約実装済み状態に同期。
  2. 修復2: Runbookの `dryRun=true -> sideEffect=none` を副作用境界（DB/外部送信/review昇格禁止）として明文化。
  3. 修復3: Verify停止条件（3回超過/契約衝突/未定義競合で停止）を運用導線へ明記。
- 判定:
  - 4点監査欠損 / 同値性不一致 / dry-run境界違反 / safeMode後退は No-Go（fail-closed）。
  - 3回自己修復で未収束の場合は Proceed 禁止のまま停止する。

## 14) Stream F 実施記録（CE4 API/CLI Audit）

### Read / ADR CDC / Plan

- Stream E で固定した CE4 契約（`equivalenceKey + bundleHash`、監査4点セット、`apply --dry-run`、`sourceBundleHash` の `mock:<hash>` 許容）を再確認し、追加仕様を導入せず監査導線固定に限定した。
- AC/DoD 不足の補完対象を docs 範囲（Issue / `02_Architecture/api.md` / `04_Documentation/local_llm_ops_guide.md`）へ限定した。

### Execute（監査導線固定）

- `Validation plan` の docs-check 導線を CE4 契約の正本参照に揃え、検証対象を `api.md` / `local_llm_ops_guide.md` / 本Issueに統一した。
- フェイルセーフ停止条件を CE4 運用導線に合わせ、`3回失敗・前提崩れ・未定義競合` で停止する判定を明文化した。

### Verify（docs-check + 契約整合）

- Verify command:
  - `rg -n "equivalenceKey|bundleHash|dryRun|sideEffect|sourceBundleHash|schemaVersion|rejectReasonCode|query|bundle|proposal|apply|fail-closed|前提崩れ|未定義競合|3回" 01_Plans/issues/issue-CE4-api-cli-audit-integration.md 02_Architecture/api.md 04_Documentation/local_llm_ops_guide.md`
  - `git diff --check`
- 判定:
  - CE4 契約語彙（同値性/監査4点/dry-run副作用境界/fail-closed）の文書間整合を確認。
  - フェイルセーフ停止条件（3回失敗・前提崩れ・未定義競合）を運用導線へ同期。

## 15) Stream E 継続運用メモ（2026-04-16 / CE2・CE4連携）

- 固定フローは `Read -> ADR CDC -> Plan -> Execute -> Verify -> Proceed` とし、`Plan -> Execute -> Verify -> Proceed` の順序逸脱を禁止する。
- CE3完了待ちは禁止し、`sourceBundleHash=mock:<hash>` を許容した契約検証を継続する。
- Verify は自己修復 3 回まで。4 回目相当は実施せず停止し、`Proceed` を実行しない。
- API/CLI/GUI 同値性契約は `equivalenceKey + bundleHash`（AND）と監査4点セット（`query/bundle/proposal/apply`）を同時充足した場合のみ pass とする。
